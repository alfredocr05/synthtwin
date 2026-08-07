#!/usr/bin/env python3
"""Verify the decontamination attestation (plan D7).

Checks, in order:
  1. the SSH signature over attestation.json validates against the pinned
     key in allowed_signers (origin authentication against third parties;
     a compromised maintainer key is the recorded D14 residual);
  2. every publicly recomputable digest matches the attestation: the
     manifest, the scanner tree (check.py, magic.txt, manifest.txt), and
     the manifest header's entry count and n_max.
Any drift means the manifest or scanner changed without a fresh signed
attestation - the CI decontam job fails until the maintainer re-runs the
private coverage battery and re-signs.

Exit codes: 0 verified, 1 signature invalid/missing, 2 digest drift.
"""

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCANNER_TREE = ["check.py", "magic.txt", "manifest.txt"]


def scanner_tree_digest() -> str:
    h = hashlib.sha256()
    for name in sorted(SCANNER_TREE):
        h.update(name.encode() + b"\0" + (HERE / name).read_bytes())
    return h.hexdigest()


def main() -> int:
    att_path = HERE / "attestation.json"
    sig_path = HERE / "attestation.json.sig"
    signers = HERE / "allowed_signers"
    for p in (att_path, sig_path, signers):
        if not p.exists():
            print(f"attestation: missing {p.name} - the decontamination "
                  "system is unverified; restore it or re-sign.")
            return 1

    with tempfile.NamedTemporaryFile() as _:
        proc = subprocess.run(
            ["ssh-keygen", "-Y", "verify", "-f", str(signers),
             "-I", "synthtwin-maintainer", "-n", "synthtwin-attestation",
             "-s", str(sig_path)],
            stdin=att_path.open("rb"), capture_output=True, check=False,
        )
    if proc.returncode != 0:
        print("attestation: SIGNATURE INVALID - attestation.json does not "
              "carry a valid signature from the pinned key. Do not trust "
              "the manifest until the maintainer re-signs.")
        return 1

    att = json.loads(att_path.read_text())
    b = att["bindings"]
    drift = []
    manifest_d = hashlib.sha256((HERE / "manifest.txt").read_bytes()).hexdigest()
    if manifest_d != b["public_manifest_sha256"]:
        drift.append("manifest.txt")
    if scanner_tree_digest() != b["public_scanner_tree_sha256"]:
        drift.append("scanner tree (check.py/magic.txt/manifest.txt)")
    header = (HERE / "manifest.txt").read_text().splitlines()
    count = next(int(l.split(":")[1]) for l in header if l.startswith("# entry_count:"))
    n_max = next(int(l.split(":")[1]) for l in header if l.startswith("# n_max:"))
    if count != att["entry_count"]:
        drift.append("entry_count")
    if n_max != att["n_max"]:
        drift.append("n_max")
    if att.get("result") != "pass":
        drift.append("result is not 'pass'")

    if drift:
        print("attestation: DIGEST DRIFT in: " + ", ".join(drift) +
              " - the bound artifacts changed without a fresh signed "
              "attestation. The maintainer must re-run the private "
              "coverage battery and re-sign.")
        return 2
    print("attestation: verified (signature valid, all public digests match)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
