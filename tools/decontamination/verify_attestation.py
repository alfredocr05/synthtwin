#!/usr/bin/env python3
"""Verify the decontamination attestation (plan D7; hardened per code-review
round-1 item F12).

Checks, in order:
  1. the SSH signature over attestation.json validates against the pinned
     key in allowed_signers (origin authentication against third parties;
     a compromised maintainer key is the recorded D14 residual);
  2. every publicly recomputable binding matches the attestation:
     - the manifest digest;
     - the COMPLETE public scanner tree digest, covering check.py,
       tokenizer.py, surfaces.py, magic.txt, manifest.txt, allowed_signers,
       and this verifier itself;
     - the public magic-table digest against its own binding;
     - the manifest header's entry_count and n_max against the attestation
       AND against the actual counted hash lines in the manifest body;
     - the manifest header's wordlist/seed/grammar/tokenizer digest lines
       against the attestation's bindings.
Any drift means a bound artifact changed without a fresh signed
attestation; the maintainer must re-run the private coverage battery and
re-sign. Exit codes: 0 verified, 1 signature invalid/missing, 2 drift.
"""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCANNER_TREE = [
    "allowed_signers",
    "check.py",
    "magic.txt",
    "manifest.txt",
    "surfaces.py",
    "tokenizer.py",
    "verify_attestation.py",
]

_HEADER_TO_BINDING = {
    "# wordlist_sha256:": "wordlist_sha256",
    "# seed_sha256:": "denial_seed_sha256",
    "# grammar_sha256:": "pattern_grammar_sha256",
    "# magic_sha256:": "magic_table_sha256",
    "# tokenizer_sha256:": "public_tokenizer_sha256",
}


def _file_digest(name: str) -> str:
    return hashlib.sha256((HERE / name).read_bytes()).hexdigest()


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
            print(
                f"attestation: missing {p.name} - the decontamination "
                "system is unverified; restore it or re-sign."
            )
            return 1

    proc = subprocess.run(
        [
            "ssh-keygen", "-Y", "verify", "-f", str(signers),
            "-I", "synthtwin-maintainer", "-n", "synthtwin-attestation",
            "-s", str(sig_path),
        ],
        stdin=att_path.open("rb"), capture_output=True, check=False,
    )
    if proc.returncode != 0:
        print(
            "attestation: SIGNATURE INVALID - attestation.json does not "
            "carry a valid signature from the pinned key. Do not trust "
            "the manifest until the maintainer re-signs."
        )
        return 1

    att = json.loads(att_path.read_text())
    b = att["bindings"]
    drift: list[str] = []

    if _file_digest("manifest.txt") != b.get("public_manifest_sha256"):
        drift.append("manifest.txt digest")
    if scanner_tree_digest() != b.get("public_scanner_tree_sha256"):
        drift.append("public scanner tree digest")
    if _file_digest("magic.txt") != b.get("magic_table_sha256"):
        drift.append("magic.txt vs bound magic-table digest")

    header_lines = (HERE / "manifest.txt").read_text().splitlines()
    body_hashes = [
        line for line in header_lines if line and not line.startswith("#")
    ]
    count = next(
        int(line.split(":")[1])
        for line in header_lines
        if line.startswith("# entry_count:")
    )
    n_max = next(
        int(line.split(":")[1])
        for line in header_lines
        if line.startswith("# n_max:")
    )
    if count != att.get("entry_count"):
        drift.append("header entry_count vs attestation")
    if len(body_hashes) != count:
        drift.append("actual manifest hash-line count vs header entry_count")
    if len(set(body_hashes)) != len(body_hashes):
        drift.append("duplicate manifest hash lines")
    if n_max != att.get("n_max"):
        drift.append("header n_max vs attestation")
    for prefix, key in _HEADER_TO_BINDING.items():
        header_value = next(
            (
                line.split(":", 1)[1].strip()
                for line in header_lines
                if line.startswith(prefix)
            ),
            None,
        )
        if header_value is None or header_value != b.get(key):
            drift.append(f"header {prefix.strip('# :')} vs attestation")
    if att.get("result") != "pass":
        drift.append("result is not 'pass'")

    if drift:
        print(
            "attestation: DIGEST DRIFT in: " + ", ".join(drift)
            + " - a bound artifact changed without a fresh signed "
            "attestation. The maintainer must re-run the private coverage "
            "battery and re-sign."
        )
        return 2
    print(
        "attestation: verified (signature valid, scanner tree, manifest, "
        "header bindings, and counts all match)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
