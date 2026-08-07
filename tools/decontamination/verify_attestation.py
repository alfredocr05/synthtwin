#!/usr/bin/env python3
"""Verify the decontamination attestation (plan D7; hardened per code-review
round-1 item F12 and round-2 item R2-B4).

Checks, in order:
  1. the SSH signature over attestation.json validates against the pinned
     key in allowed_signers (origin authentication against third parties;
     a compromised maintainer key is the recorded D14 residual);
  2. attestation.json has the exact v2 shape: every mandatory top-level
     key with the right type, every mandatory binding present (digest
     bindings as 64 lowercase hex characters), no unexpected key, and
     result equal to "pass";
  3. manifest.txt parses under the strict shared parser imported from
     check.py (exactly one occurrence of each mandatory header, every
     body line exactly 64 lowercase hex characters) - the scanner and
     this verifier can never read different values from the same file;
  4. every publicly recomputable binding matches the attestation:
     - the manifest.txt, magic.txt, tokenizer.py, and surfaces.py file
       digests, each recomputed directly from the bytes on disk;
     - the COMPLETE public scanner tree digest, covering check.py,
       tokenizer.py, surfaces.py, magic.txt, manifest.txt,
       allowed_signers, and this verifier itself;
     - the manifest header entry_count and n_max against the attestation
       AND against the actual counted hash lines in the manifest body;
     - every manifest digest header (wordlist, seed, grammar, magic,
       tokenizer, snapshot tree) against its attestation binding, so a
       header can never disagree with the signed graph.

Any drift means a bound artifact changed without a fresh signed
attestation; the maintainer must re-run the private coverage battery and
re-sign. Exit codes: 0 verified, 1 signature invalid/missing, 2 drift.
"""

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from check import ManifestFormatError, load_manifest  # the single shared parser

SCANNER_TREE = [
    "allowed_signers",
    "check.py",
    "magic.txt",
    "manifest.txt",
    "surfaces.py",
    "tokenizer.py",
    "verify_attestation.py",
]

_HEX64 = re.compile(r"[0-9a-f]{64}\Z")

# The exact attestation-v2 shape (round-2 item R2-B4): mandatory top-level
# keys with their required types, and the complete binding key set.
REQUIRED_TOP_LEVEL = {
    "artifact": str,
    "bindings": dict,
    "date": str,
    "entry_count": int,
    "n_max": int,
    "note": str,
    "refresh_triggers": str,
    "result": str,
}
REQUIRED_HEX_BINDINGS = (
    "all_objects_tool_sha256",
    "coverage_tool_sha256",
    "denial_seed_sha256",
    "extraction_script_sha256",
    "freeze_record_sha256",
    "inventory_review_round1_sha256",
    "inventory_review_round2_sha256",
    "magic_table_sha256",
    "pattern_grammar_sha256",
    "plaintext_inventory_sha256",
    "pre_first_push_note_sha256",
    "prototype_snapshot_tree_sha256",
    "public_manifest_sha256",
    "public_scanner_tree_sha256",
    "public_surfaces_sha256",
    "public_tokenizer_sha256",
    "wordlist_sha256",
    "wordlist_sources_sha256",
)
REQUIRED_TEXT_BINDINGS = ("snapshot_digest_algorithm",)

# Every manifest digest header maps to exactly one attestation binding;
# snapshot_tree_sha256 binds the header to the signed snapshot digest.
_HEADER_TO_BINDING = {
    "wordlist_sha256": "wordlist_sha256",
    "seed_sha256": "denial_seed_sha256",
    "grammar_sha256": "pattern_grammar_sha256",
    "magic_sha256": "magic_table_sha256",
    "tokenizer_sha256": "public_tokenizer_sha256",
    "snapshot_tree_sha256": "prototype_snapshot_tree_sha256",
}

# Public files whose digests are recomputed directly, byte for byte.
_RECOMPUTED_FILES = {
    "manifest.txt": "public_manifest_sha256",
    "magic.txt": "magic_table_sha256",
    "tokenizer.py": "public_tokenizer_sha256",
    "surfaces.py": "public_surfaces_sha256",
}


def _file_digest(name: str) -> str:
    return hashlib.sha256((HERE / name).read_bytes()).hexdigest()


def scanner_tree_digest() -> str:
    h = hashlib.sha256()
    for name in sorted(SCANNER_TREE):
        h.update(name.encode() + b"\0" + (HERE / name).read_bytes())
    return h.hexdigest()


def schema_problems(att) -> list:
    """Return every departure from the exact attestation-v2 shape."""
    problems = []
    if not isinstance(att, dict):
        return ["attestation is not a JSON object"]
    for key, kind in REQUIRED_TOP_LEVEL.items():
        if key not in att:
            problems.append(f"missing attestation key '{key}'")
        elif not isinstance(att[key], kind) or isinstance(att[key], bool):
            problems.append(f"attestation key '{key}' has the wrong type")
    for key in sorted(set(att) - set(REQUIRED_TOP_LEVEL)):
        problems.append(f"unexpected attestation key '{key}'")
    bindings = att.get("bindings")
    if not isinstance(bindings, dict):
        return problems
    for key in REQUIRED_HEX_BINDINGS:
        value = bindings.get(key)
        if value is None:
            problems.append(f"missing binding '{key}'")
        elif not isinstance(value, str) or not _HEX64.fullmatch(value):
            problems.append(
                f"binding '{key}' is not 64 lowercase hex characters"
            )
    for key in REQUIRED_TEXT_BINDINGS:
        value = bindings.get(key)
        if not isinstance(value, str) or not value:
            problems.append(f"missing or empty binding '{key}'")
    known = set(REQUIRED_HEX_BINDINGS) | set(REQUIRED_TEXT_BINDINGS)
    for key in sorted(set(bindings) - known):
        problems.append(f"unexpected binding '{key}'")
    if att.get("result") != "pass":
        problems.append("result is not 'pass'")
    return problems


def main() -> int:
    att_path = HERE / "attestation.json"
    sig_path = HERE / "attestation.json.sig"
    signers = HERE / "allowed_signers"
    needed = [att_path, sig_path] + [HERE / name for name in SCANNER_TREE]
    for p in needed:
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
    problems = schema_problems(att)
    if problems:
        print(
            "attestation: SCHEMA INVALID in: " + ", ".join(problems)
            + " - attestation.json does not have the exact v2 shape; the "
            "maintainer must rebuild it from the private pipeline and "
            "re-sign."
        )
        return 2

    try:
        headers, body_hashes = load_manifest(HERE / "manifest.txt")
    except ManifestFormatError as err:
        print(
            f"attestation: MANIFEST FORMAT INVALID - {err} (bindings "
            "cannot be checked until the manifest is restored)."
        )
        return 2

    b = att["bindings"]
    drift = []

    for name, key in _RECOMPUTED_FILES.items():
        if _file_digest(name) != b[key]:
            drift.append(f"{name} digest vs binding {key}")
    if scanner_tree_digest() != b["public_scanner_tree_sha256"]:
        drift.append("public scanner tree digest")

    count = int(headers["entry_count"])
    n_max = int(headers["n_max"])
    if count != att["entry_count"]:
        drift.append("header entry_count vs attestation")
    if len(body_hashes) != count:
        drift.append("actual manifest hash-line count vs header entry_count")
    if len(set(body_hashes)) != len(body_hashes):
        drift.append("duplicate manifest hash lines")
    if n_max != att["n_max"]:
        drift.append("header n_max vs attestation")
    for header_name, key in _HEADER_TO_BINDING.items():
        if headers[header_name] != b[key]:
            drift.append(f"manifest header {header_name} vs binding {key}")

    if drift:
        print(
            "attestation: DIGEST DRIFT in: " + ", ".join(drift)
            + " - a bound artifact changed without a fresh signed "
            "attestation. The maintainer must re-run the private coverage "
            "battery and re-sign."
        )
        return 2
    print(
        "attestation: verified (signature valid, exact v2 shape, scanner "
        "tree, manifest, header bindings, and counts all match)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
