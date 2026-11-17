# /// script
# requires-python = ">=3.10"
# dependencies = ["model-signing==1.1.1", "pyopenssl>=24"]
# ///
"""Runs the reference solution of every lab of LDS-AIG-203 against the files in labs/files/.

Each lab's reference answers (labs/solutions/D*.md) rest on facts in the case files. This script
recomputes every one of those facts from the files, runs the lab 1.2 tool for real (bill of
materials and both signature checks), and prints PASS or the first difference. For the trainer.

    cd labs
    uv run solutions/check.py
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

LABS = Path(__file__).resolve().parent.parent
F = LABS / "files"
FAILS: list[str] = []


def ok(label: str, got, want) -> None:
    if got == want:
        print(f"PASS  {label}: {got}")
    else:
        print(f"FAIL  {label}: got {got!r}, expected {want!r}")
        FAILS.append(label)


def rows(rel: str) -> list[dict]:
    with (F / rel).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def front_matter(text: str) -> dict:
    meta, key = {}, None
    head = text.split("---")[1] if text.startswith("---") else ""
    for line in head.splitlines():
        if line.lstrip().startswith("- ") and key:
            meta.setdefault(key, []).append(line.strip()[2:])
        elif ":" in line:
            key, _, v = line.partition(":")
            key = key.strip()
            meta[key] = v.strip() or []
    return meta


def lab_1_1() -> None:
    print("\nLab 1.1 · licence table")
    reg = rows("intake_register.csv")
    ok("six artefacts in the register", len(reg), 6)
    fawatir = (F / "cards/fawatir-scans.md").read_text(encoding="utf-8")
    ok("dataset metadata licence", front_matter(fawatir)["license"], "cc-by-4.0")
    ok("dataset text says NonCommercial", "NonCommercial 4.0" in fawatir, True)
    ok("dataset collected from public social media posts with names kept", "Names and phone numbers printed on invoices were not removed" in fawatir, True)
    sarid = (F / "cards/sarid-70b-instruct.md").read_text(encoding="utf-8")
    meta = front_matter(sarid)
    ok("Sarid base model is Llama 3.3", meta["base_model"], "meta-llama/Llama-3.3-70B-Instruct")
    title = re.search(r"^# (.+)$", sarid, re.M).group(1)
    ok("Sarid model name starts with 'Llama'", title.startswith("Llama"), False)
    ok("Sarid card shows 'Built with Llama'", "Built with Llama" in sarid, False)
    mcp = (F / "cards/mustanad-mcp.md").read_text(encoding="utf-8")
    ok("tool server under AGPL and the Fund writes a connector", ("AGPL-3.0" in mcp) and any("connector" in r["intended use at the Fund"] for r in reg), True)
    terms = (F / "terms/nuqta_cloud_terms.md").read_text(encoding="utf-8")
    ok("Nuqta trains on content unless Enterprise with Data Controls (5.2)", "may use Customer Content to improve and train" in terms, True)
    ok("Nuqta processes in any region (6.1)", "processed in any region" in terms, True)
    ok("Nuqta forbids resale (3.1)", "must not resell" in terms, True)


def run_tool(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(LABS / "tools/provenance.py"), *args], capture_output=True, text=True, cwd=LABS)


def lab_1_2() -> None:
    print("\nLab 1.2 · provenance (runs the tool for real)")
    pkg = F / "khatt-ocr-small"
    meta = front_matter((pkg / "README.md").read_text(encoding="utf-8"))
    ok("declared datasets", meta["datasets"], ["fawatir-scans", "khatt-internal-receipts"])
    ok("declared base model", meta["base_model"], "naqsh-ai/vision-encoder-base")
    rel = (pkg / "RELEASES.md").read_text(encoding="utf-8")
    v10 = re.search(r"`([0-9a-f]{64})`", rel).group(1)
    now = hashlib.sha256((pkg / "model.safetensors").read_bytes()).hexdigest()
    ok("weights changed between 1.0 and 1.1", v10 != now, True)
    ok("1.0 notes name one dataset, the card of 1.1 names two", ("Trained on fawatir-scans." in rel) and len(meta["datasets"]) == 2, True)
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "bom.json"
        r = run_tool("bom", "files/khatt-ocr-small", "--out", str(out))
        ok("bom command exit code", r.returncode, 0)
        bom = json.loads(out.read_text(encoding="utf-8"))
        comp = bom["metadata"]["component"]
        ok("BOM model component type", comp["type"], "machine-learning-model")
        ok("BOM lists six files", sum(1 for c in bom["components"] if c["type"] == "file"), 6)
        ok("BOM weights hash equals the file", comp["hashes"][0]["content"], now)
        ok("BOM base model in pedigree", comp["pedigree"]["ancestors"][0]["name"], "naqsh-ai/vision-encoder-base")
        ok("BOM datasets carry no licence", all("licenses" not in c for c in bom["components"] if c["type"] == "data"), True)
    r = run_tool("verify", "files/khatt-ocr-small")
    ok("official package signature", r.returncode, 0)
    r = run_tool("verify", "files/mirror/khatt-ocr-small")
    ok("mirror signature fails", r.returncode, 1)
    changed = sorted(re.findall(r"file changed after signing: (\S+)", r.stdout))
    extra = re.findall(r"file not in the signed package: (\S+)", r.stdout)
    ok("mirror files changed", changed, ["README.md", "model.safetensors"])
    ok("mirror extra file", extra, ["custom_loader.py"])


def lab_1_3() -> None:
    print("\nLab 1.3 · supplier assurance")
    q = rows("lamah_pack/questionnaire.csv")
    ok("questionnaire answers", len(q), 14)
    ok("answers with no evidence attached", sum(1 for r in q if not r["evidence attached"].strip()), 8)
    c42 = (F / "lamah_pack/cert_iso42001.md").read_text(encoding="utf-8")
    scope = re.search(r"\*\*Scope of certification:\*\* (.+)", c42).group(1)
    ok("ISO/IEC 42001 scope names DocSense", "DocSense" in scope, True)
    ok("ISO/IEC 42001 scope names the follow-up service", ("Mutabi" in scope) or ("مُتابِع" in scope), False)
    ok("ISO/IEC 42001 accreditation stated", "not stated" not in c42, False)
    c27 = (F / "lamah_pack/cert_iso27001.md").read_text(encoding="utf-8")
    ok("ISO/IEC 27001 covers all services from the Riyadh data centre", "all Lamah cloud services" in c27, True)
    pen = (F / "lamah_pack/pentest_letter.md").read_text(encoding="utf-8")
    ok("pentest scope excludes the service", "خارج النطاق: الواجهات البرمجية للخدمات، وخدمة «مُتابِع»" in pen, True)
    idx = (F / "lamah_pack/00_index.md").read_text(encoding="utf-8")
    ok("pack sent in February 2027", "فبراير 2027" in idx, True)
    ok("pentest ran in August 2025", "أغسطس 2025" in pen, True)
    ok("pentest age in months when the pack was sent", (2027 - 2025) * 12 + (2 - 8), 18)
    ev = (F / "lamah_pack/evaluation_summary.md").read_text(encoding="utf-8")
    ok("supplier evaluation run by its own product team", "فريق منتج" in ev, True)
    sub = rows("lamah_pack/subprocessors.csv")
    outside = [r["sub-processor"] for r in sub if "خارج المملكة" in r["location"]]
    ok("sub-processor processing outside the Kingdom", outside, ["Nuqta Cloud"])


def lab_2_1() -> None:
    print("\nLab 2.1 · change and exit")
    use = rows("nuqta/usage_inventory.csv")
    ok("workflows pinned to the retiring version", [r["id"] for r in use if r["model identifier"] == "nuqta-pro-2"], ["W1", "W4"])
    ok("workflows on the alias", [r["id"] for r in use if r["pinned or alias"] == "اسم مستعار"], ["W2"])
    ok("workflows the Fund cannot see", [r["id"] for r in use if r["model identifier"] == "غير معروف للصندوق"], ["W3"])
    terms = (F / "terms/nuqta_cloud_terms.md").read_text(encoding="utf-8")
    notice = int(re.search(r"at least (\d+) days' notice of a retirement", terms).group(1))
    proc = (F / "nuqta/athl_change_procedure.md").read_text(encoding="utf-8")
    needed = int(re.search(r"إلى الموافقة: (\d+) يومًا", proc).group(1))
    ok("provider notice in days", notice, 21)
    ok("days the Fund needs", needed, 30)
    ok("shortfall in days", needed - notice, 9)
    ev = rows("nuqta/eval_results.csv")
    by = defaultdict(lambda: [0, 0, 0])
    for r in ev:
        b = by[r["category"]]
        b[0] += 1
        b[1] += int(r["nuqta-pro-2 pass"])
        b[2] += int(r["nuqta-pro-3 pass"])
    ok("cases", len(ev), 40)
    ok("passes old / new", (sum(v[1] for v in by.values()), sum(v[2] for v in by.values())), (37, 34))
    ok("dialect passes old / new", tuple(by["dialect"][1:]), (9, 6))
    ok("sensitive passes old / new", tuple(by["sensitive"][1:]), (8, 7))
    ok("export window and deletion terms", ("14 days after termination" in terms) and ("No certificate of deletion" in terms), True)


def lab_2_2() -> None:
    print("\nLab 2.2 · retirement")
    log = rows("cdm/api_access_log.csv")
    calls, days = Counter(), Counter()
    for r in log:
        calls[r["client id"]] += int(r["calls"])
        days[r["client id"]] += 1
    declared = {r["client id"] for r in rows("cdm/dependency_register.csv")}
    ok("undeclared caller", sorted(set(calls) - declared), ["east-branch-sheet"])
    ok("undeclared caller: calls and active days in 90", (calls["east-branch-sheet"], days["east-branch-sheet"]), (286, 64))
    ok("declared consumer with no calls", sorted(declared - set(calls)), ["appeals-desk"])
    ok("quarterly caller seen once", calls["reg-extract"], 1)
    m = rows("cdm/decisions_by_month.csv")
    ok("months of decisions", len(m), 36)
    ok("decisions made by v3", sum(int(r["decisions"]) for r in m), 65166)
    ok("appeals still open", sum(int(r["appeals still open"]) for r in m), 38)
    par = rows("cdm/parallel_run.csv")
    gaps = {r["sector"]: round(float(r["v4 approval rate"]) - float(r["v3 approval rate"]), 2) for r in par}
    ok("largest drop in approval rate", min(gaps, key=gaps.get), "الزراعة")
    ok("agriculture drop in points", round(gaps["الزراعة"] * 100), -12)
    ok("agriculture applications in the parallel run", int(next(r for r in par if r["sector"] == "الزراعة")["applications in the parallel run"]), 410)


def main() -> int:
    for fn in (lab_1_1, lab_1_2, lab_1_3, lab_2_1, lab_2_2):
        fn()
    print()
    if FAILS:
        print(f"{len(FAILS)} check(s) failed")
        return 1
    print("all reference facts hold")
    return 0


if __name__ == "__main__":
    sys.exit(main())
