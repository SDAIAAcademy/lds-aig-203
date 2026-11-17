# /// script
# requires-python = ">=3.10"
# dependencies = ["model-signing==1.1.1", "pyopenssl>=24", "cryptography>=42"]
# ///
"""Signs the official Khatt-OCR-small package for lab 1.2, as its fictional publisher would.

Makes a new elliptic-curve key pair in a temporary folder, signs files/khatt-ocr-small with the
OpenSSF model_signing library (key method), writes files/signatures/khatt-ocr-small.sig and the
public key files/signatures/khatt-lab.pub, then deletes the private key. Run it after
prepare_files.py. Each run makes a new key, so the signature and key change together.

    cd labs
    uv run _tools/sign_package.py
"""
import subprocess
import sys
import tempfile
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

ROOT = Path(__file__).resolve().parent.parent
PKG = ROOT / "files" / "khatt-ocr-small"
OUT = ROOT / "files" / "signatures"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        priv = Path(tmp) / "khatt-lab.priv"
        key = ec.generate_private_key(ec.SECP256R1())
        priv.write_bytes(key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
        (OUT / "khatt-lab.pub").write_bytes(key.public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo))
        run = subprocess.run([sys.executable, "-m", "model_signing", "sign", "key", str(PKG),
                              "--private_key", str(priv), "--signature", str(OUT / "khatt-ocr-small.sig")],
                             capture_output=True, text=True)
        print((run.stdout + run.stderr).strip())
        return run.returncode


if __name__ == "__main__":
    sys.exit(main())
