"""Decontamination machinery self-tests (plan D7; code-review round-1
items F13 and F20 folded in): neutral canaries in every surface form, the
full decoder battery, value-silent output, and attestation rejection. The
real inventory is never reproduced here; canaries are invented tokens.
"""

import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

TOOLS = Path(__file__).resolve().parent.parent / "tools" / "decontamination"

spec = importlib.util.spec_from_file_location("decontam_check", TOOLS / "check.py")
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)

CANARY = "zqvortex"  # invented; not in any dictionary or source tree


def make_manifest(tmp_path: Path, entries: list[str]) -> Path:
    hashes = sorted(hashlib.sha256(e.encode()).hexdigest() for e in entries)
    n_max = max(len(e.split(" ")) for e in entries)
    m = tmp_path / "manifest.txt"
    m.write_text(
        f"# test manifest\n# entry_count: {len(hashes)}\n# n_max: {n_max}\n#\n"
        + "\n".join(hashes) + "\n"
    )
    return m


def run_check(root: Path, manifest: Path) -> int:
    return check.main([str(root), "--manifest", str(manifest)])


@pytest.fixture()
def tree(tmp_path: Path) -> Path:
    root = tmp_path / "tree"
    root.mkdir()
    (root / "clean.md").write_text("an ordinary file with ordinary words\n")
    return root


# ---------- clean and green paths ----------------------------------------


def test_clean_tree_passes(tree: Path, tmp_path: Path) -> None:
    assert run_check(tree, make_manifest(tmp_path, [CANARY])) == 0


@pytest.mark.parametrize("codec,bom", [
    ("utf-16-be", b"\xfe\xff"), ("utf-16-le", b"\xff\xfe"),
    ("utf-32-be", b"\x00\x00\xfe\xff"), ("utf-32-le", b"\xff\xfe\x00\x00"),
    ("utf-8", b"\xef\xbb\xbf"),
])
def test_valid_bom_clean_text_is_green(
    tree: Path, tmp_path: Path, codec: str, bom: bytes
) -> None:
    (tree / "note.txt").write_bytes(bom + "ordinary words".encode(codec))
    assert run_check(tree, make_manifest(tmp_path, [CANARY])) == 0


# ---------- content-form detection ----------------------------------------


@pytest.mark.parametrize(
    "content",
    [
        f"prefix {CANARY} suffix\n",              # plain line
        "x = 'Zqvortex'\n",                        # capitalized, in a string
        f"def {CANARY}_helper():\n    pass\n",     # identifier position
        f"value = 1  # note: {CANARY}\n",          # comment
    ],
)
def test_canary_content_forms_fail(
    tree: Path, tmp_path: Path, content: str
) -> None:
    (tree / "placed_file.py").write_text(content)
    assert run_check(tree, make_manifest(tmp_path, [CANARY])) == 1


def test_canary_filename_fails(tree: Path, tmp_path: Path) -> None:
    (tree / f"{CANARY}_notes.md").write_text("nothing here\n")
    assert run_check(tree, make_manifest(tmp_path, [CANARY])) == 1


def test_canary_filename_is_never_printed(
    tree: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # Value-silent output (review item F20): the protected token appears
    # only in a filename; the scanner must go red WITHOUT repeating the
    # token anywhere in its output.
    (tree / f"{CANARY}_notes.md").write_text("nothing here\n")
    assert run_check(tree, make_manifest(tmp_path, [CANARY])) == 1
    out = capsys.readouterr().out
    assert CANARY not in out.casefold(), "matched path text leaked into output"
    assert "<redacted:" in out


def test_canary_shell_line_fails(tree: Path, tmp_path: Path) -> None:
    (tree / "run.sh").write_text(f"#!/bin/sh\n# step: {CANARY}\necho ok\n")
    assert run_check(tree, make_manifest(tmp_path, [CANARY])) == 1


def test_canary_csv_cell_fails(tree: Path, tmp_path: Path) -> None:
    # written at runtime into tmp only; data files never enter the repo
    (tree / "table.csv").write_text(f"col_a,col_b\n1,{CANARY}\n")
    assert run_check(tree, make_manifest(tmp_path, [CANARY])) == 1


def test_canary_multiline_ast_constant_fails(
    tree: Path, tmp_path: Path
) -> None:
    phrase = f"{CANARY} alpha beta"
    (tree / "mod.py").write_text(
        'DOC = (\n    "Zqvortex alpha "\n    "beta tail"\n)\n'
    )
    assert run_check(tree, make_manifest(tmp_path, [phrase])) == 1


def test_canary_utf8_bom_python_ast_fails(tree: Path, tmp_path: Path) -> None:
    # Ratification battery: a UTF-8 BOM must not disable AST extraction.
    phrase = f"{CANARY} alpha beta"
    src = 'DOC = "Zqvortex alpha " "beta"\n'
    (tree / "mod.py").write_bytes(b"\xef\xbb\xbf" + src.encode())
    assert run_check(tree, make_manifest(tmp_path, [phrase])) == 1


# ---------- encoding battery ----------------------------------------------


@pytest.mark.parametrize("codec,bom", [
    ("utf-16-be", b"\xfe\xff"), ("utf-16-le", b"\xff\xfe"),
    ("utf-32-be", b"\x00\x00\xfe\xff"), ("utf-32-le", b"\xff\xfe\x00\x00"),
    ("utf-8", b"\xef\xbb\xbf"),
])
def test_canary_bom_encodings_fail(
    tree: Path, tmp_path: Path, codec: str, bom: bytes
) -> None:
    (tree / "enc.txt").write_bytes(bom + f"see {CANARY} here".encode(codec))
    assert run_check(tree, make_manifest(tmp_path, [CANARY])) == 1


def test_fullwidth_compatibility_spelling_fails(
    tree: Path, tmp_path: Path
) -> None:
    fw = "".join(chr(ord(c) + 0xFEE0) for c in CANARY)
    (tree / "wide.md").write_text(f"token {fw} end\n")
    assert run_check(tree, make_manifest(tmp_path, [CANARY])) == 1


def test_enclosed_compatibility_spelling_fails(
    tree: Path, tmp_path: Path
) -> None:
    # Circled letters NFKC-normalize to plain letters (ratified R2-C1).
    enclosed = "".join(chr(0x24D0 + (ord(c) - ord("a"))) for c in CANARY)
    (tree / "circled.md").write_text(f"token {enclosed} end\n")
    assert run_check(tree, make_manifest(tmp_path, [CANARY])) == 1


def test_malformed_bom_text_is_violation(tree: Path, tmp_path: Path) -> None:
    (tree / "bad.txt").write_bytes(b"\xef\xbb\xbf\xff\xff\xfe")
    assert run_check(tree, make_manifest(tmp_path, [CANARY])) == 2


def test_bomless_wide_encoding_is_violation(
    tree: Path, tmp_path: Path
) -> None:
    # BOM-less UTF-16 text carries NUL bytes -> fail-closed control route.
    (tree / "wide.txt").write_bytes(f"see {CANARY}".encode("utf-16-be"))
    assert run_check(tree, make_manifest(tmp_path, [CANARY])) == 2


def test_unknown_magic_printable_survivor_is_scanned(
    tree: Path, tmp_path: Path
) -> None:
    # A printable stream with an unknown leading tag survives to the text
    # path (the named residual) and its content is still token-scanned.
    (tree / "tagged.bin.txt").write_bytes(b"XTAG" + f" {CANARY} ".encode())
    assert run_check(tree, make_manifest(tmp_path, [CANARY])) == 1


def test_control_byte_binary_is_violation(tree: Path, tmp_path: Path) -> None:
    (tree / "blob.txt").write_bytes(b"looks text \x01\x02 but is not")
    assert run_check(tree, make_manifest(tmp_path, [CANARY])) == 2


@pytest.mark.parametrize("sig", ["504b0304", "1f8b", "7f454c46",
                                 "53514c69746520666f726d6174203300"])
def test_magic_signatures_are_violations(
    tree: Path, tmp_path: Path, sig: str
) -> None:
    (tree / "payload.txt").write_bytes(bytes.fromhex(sig) + b"rest")
    assert run_check(tree, make_manifest(tmp_path, [CANARY])) == 2


# ---------- the real repository -------------------------------------------


def test_repo_tree_is_clean_under_real_manifest() -> None:
    repo = TOOLS.parent.parent
    assert check.main([str(repo)]) == 0


# ---------- attestation ----------------------------------------------------


def _verify(tmp_dir: Path) -> int:
    proc = subprocess.run(
        [sys.executable, str(tmp_dir / "verify_attestation.py")],
        capture_output=True, text=True, check=False,
    )
    return proc.returncode


@pytest.fixture()
def att_copy(tmp_path: Path) -> Path:
    d = tmp_path / "decontam"
    shutil.copytree(TOOLS, d, ignore=shutil.ignore_patterns("__pycache__"))
    return d


def test_attestation_verifies_as_committed(att_copy: Path) -> None:
    assert _verify(att_copy) == 0


def test_tampered_attestation_rejected(att_copy: Path) -> None:
    att = att_copy / "attestation.json"
    data = json.loads(att.read_text())
    data["entry_count"] = 1  # structurally consistent, content changed
    att.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    assert _verify(att_copy) == 1  # signature no longer covers the bytes


def test_missing_signature_rejected(att_copy: Path) -> None:
    (att_copy / "attestation.json.sig").unlink()
    assert _verify(att_copy) == 1


def test_wrong_key_signature_rejected(att_copy: Path, tmp_path: Path) -> None:
    # Re-sign with a fresh key NOT in allowed_signers: origin check fails.
    key = tmp_path / "rogue_key"
    subprocess.run(
        ["ssh-keygen", "-t", "ed25519", "-f", str(key), "-N", "", "-q"],
        check=True,
    )
    (att_copy / "attestation.json.sig").unlink()
    subprocess.run(
        ["ssh-keygen", "-Y", "sign", "-f", str(key),
         "-n", "synthtwin-attestation", str(att_copy / "attestation.json")],
        check=True, capture_output=True,
    )
    assert _verify(att_copy) == 1


def test_manifest_drift_without_resign_rejected(att_copy: Path) -> None:
    m = att_copy / "manifest.txt"
    m.write_text(m.read_text() + hashlib.sha256(b"new").hexdigest() + "\n")
    assert _verify(att_copy) == 2  # signature ok, digest drift caught


def test_verifier_counts_actual_manifest_entries(att_copy: Path) -> None:
    # Header says N but the body holds N-1 hashes: the verifier must count
    # the real lines, not trust two declared numbers (review item F12).
    m = att_copy / "manifest.txt"
    lines = m.read_text().splitlines()
    body = [ln for ln in lines if ln and not ln.startswith("#")]
    lines.remove(body[-1])
    m.write_text("\n".join(lines) + "\n")
    assert _verify(att_copy) == 2
