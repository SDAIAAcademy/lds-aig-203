# /// script
# requires-python = ">=3.10"
# dependencies = ["model-signing==1.1.1", "pyopenssl>=24"]
# ///
"""Provenance helper for lab 1.2 of LDS-AIG-203.

Three commands, run from the folder labs/:

  uv run tools/provenance.py check
      proves the tool runs (prints the versions it uses)

  uv run tools/provenance.py bom files/sutur-ocr-small
      reads the model card (README.md) and every file of the package, and writes a
      CycloneDX machine-learning bill of materials (specVersion 1.6) next to the package:
      files/sutur-ocr-small.cdx.json. It prints what the card declares and what it leaves out.

  uv run tools/provenance.py verify files/sutur-ocr-small
      verifies the publisher's signature over the whole folder with the OpenSSF
      model_signing library (key-based, offline). The signature and the public key are in
      files/signatures/. Add --signature and --key to use other files.

Nothing is downloaded except the two Python packages above, and no model is loaded or run.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

CARD_FIELDS = ["license", "base_model", "datasets", "pipeline_tag", "model_version", "publisher"]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(65536), b""):
            h.update(block)
    return h.hexdigest()


def read_card(folder: Path) -> tuple[dict, str]:
    """Read the YAML front matter of README.md with a small parser (keys, scalars, lists)."""
    text = (folder / "README.md").read_text(encoding="utf-8")
    meta: dict = {}
    if not text.startswith("---"):
        return meta, text
    head, _, body = text[3:].partition("\n---")
    key = None
    for line in head.splitlines():
        if not line.strip():
            continue
        if line.lstrip().startswith("- ") and key:
            meta.setdefault(key, [])
            if isinstance(meta[key], list):
                meta[key].append(line.strip()[2:].strip())
            continue
        if ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip()
            meta[key] = value if value else []
    return meta, body


def cmd_check(_args) -> int:
    import importlib.metadata as md
    print("python", sys.version.split()[0])
    print("model-signing", md.version("model-signing"))
    print("ready: run 'bom' and 'verify' on files/sutur-ocr-small")
    return 0


def cmd_bom(args) -> int:
    folder = Path(args.folder)
    if not (folder / "README.md").exists():
        print(f"no README.md (model card) in {folder}")
        return 2
    meta, _body = read_card(folder)
    name = folder.name
    version = str(meta.get("model_version", "")) or "unknown"
    files = sorted(p for p in folder.rglob("*") if p.is_file())
    licence = meta.get("license")
    datasets = meta.get("datasets") or []
    base = meta.get("base_model")

    component = {
        "type": "machine-learning-model",
        "bom-ref": f"model:{name}@{version}",
        "name": name,
        "version": version,
        "publisher": meta.get("publisher", ""),
        "licenses": [{"license": {"id": "Apache-2.0"}}] if licence == "apache-2.0" else (
            [{"license": {"name": str(licence)}}] if licence else []),
        "hashes": [{"alg": "SHA-256", "content": sha256(folder / "model.safetensors")}]
        if (folder / "model.safetensors").exists() else [],
        "modelCard": {
            "modelParameters": {
                "task": meta.get("pipeline_tag", ""),
                "datasets": [{"ref": f"data:{d}"} for d in datasets],
            },
            "considerations": {"useCases": ["reading scanned invoices in loan applications"]},
        },
    }
    if base:
        component["pedigree"] = {"ancestors": [{"type": "machine-learning-model", "bom-ref": f"model:{base}", "name": str(base)}]}

    data_components = [
        {"type": "data", "bom-ref": f"data:{d}", "name": d, "data": [{"type": "dataset", "name": d}]}
        for d in datasets
    ]
    file_components = [
        {"type": "file", "bom-ref": f"file:{p.relative_to(folder).as_posix()}", "name": p.relative_to(folder).as_posix(),
         "hashes": [{"alg": "SHA-256", "content": sha256(p)}]}
        for p in files
    ]
    bom = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.6",
        "version": 1,
        "metadata": {
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "tools": {"components": [{"type": "application", "name": "provenance.py (LDS-AIG-203 lab 1.2)"}]},
            "component": component,
        },
        "components": data_components + file_components,
        "dependencies": [{"ref": component["bom-ref"], "dependsOn": [c["bom-ref"] for c in data_components + file_components]}],
    }
    out = Path(args.out) if args.out else folder.parent / f"{name}.cdx.json"
    out.write_text(json.dumps(bom, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"wrote {out.as_posix()}  ({len(files)} files, {len(data_components)} datasets)")
    print("\nwhat the card declares")
    for field in CARD_FIELDS:
        value = meta.get(field)
        shown = ", ".join(value) if isinstance(value, list) else value
        print(f"  {field:14} {shown if shown else '(not declared)'}")
    print("\nfiles and SHA-256")
    for p in files:
        print(f"  {sha256(p)}  {p.relative_to(folder).as_posix()}")
    print("\nwhat this bill of materials cannot tell you")
    print("  the licence of each dataset and of the base model (not in this card)")
    print("  whether these files are the ones the publisher released (that is what 'verify' checks)")
    return 0


def cmd_verify(args) -> int:
    folder = Path(args.folder)
    files_dir = Path(__file__).resolve().parent.parent / "files" / "signatures"
    sig = Path(args.signature) if args.signature else files_dir / "sutur-ocr-small.sig"
    key = Path(args.key) if args.key else files_dir / "sutur-lab.pub"
    print(f"folder     {folder.as_posix()}")
    print(f"signature  {sig.name}")
    print(f"public key {key.name}")
    run = subprocess.run(
        [sys.executable, "-m", "model_signing", "verify", "key", str(folder),
         "--signature", str(sig), "--public_key", str(key)],
        capture_output=True, text=True,
    )
    out = (run.stdout + run.stderr).strip()
    if run.returncode == 0:
        print("RESULT: signature valid. Every file matches what the key holder signed.")
        return 0
    print("RESULT: verification FAILED.")
    found = False
    for m in re.finditer(r"Extra files found in model '[^']*': ([^\"'\]]+)", out):
        print("  file not in the signed package:", m.group(1).strip())
        found = True
    for m in re.finditer(r"Missing files in the model: ([^\"'\]]+)", out):
        print("  signed file missing here:", m.group(1).strip())
        found = True
    for m in re.finditer(r"Hash mismatch for \\?'([^'\\]+)\\?'", out):
        print("  file changed after signing:", m.group(1))
        found = True
    if not found:
        print("  " + out[:400])
    return 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check").set_defaults(fn=cmd_check)
    b = sub.add_parser("bom")
    b.add_argument("folder")
    b.add_argument("--out")
    b.set_defaults(fn=cmd_bom)
    v = sub.add_parser("verify")
    v.add_argument("folder")
    v.add_argument("--signature")
    v.add_argument("--key")
    v.set_defaults(fn=cmd_verify)
    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
