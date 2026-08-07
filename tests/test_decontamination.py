"""Decontamination machinery self-tests (plan D7): neutral canaries in
every surface form, encoding battery, attestation rejection. The real
inventory is never reproduced here; canaries are invented neutral tokens.
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
    hashes = sorted(
        hashlib.sha256(e.encode()).hexdigest() for e in entries
    )
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


def test_clean_tree_passes(tree: Path, tmp_path: Path) -> None:
    assert run_check(tree, make_manifest(tmp_path, [CANARY])) == 0


@pytest.mark.parametrize(
    "content",
    [
        f"prefix {CANARY} suffix\n",              # plain line
        "x = 'Zqvortex'\n",                       # capitalized, in a string
        f"def {CANARY}_helper():\n    pass\n",     # identifier position
        f"value = 1  # note: {CANARY}\n",          # comment
    ],
)
def test_canary_content_forms_fail(tree: Path, tmp_path: Path, content: str) -> None:
    (tree / "placed_file.py").write_text(content)
    assert run_check(tree, make_manifest(tmp_path, [CANARY])) == 1


def test_canary_filename_fails(tree: Path, tmp_path: Path) -> None:
    (tree / f"{CANARY}_notes.md").write_text("nothing here\n")
    assert run_check(tree, make_manifest(tmp_path, [CANARY])) == 1


def test_canary_csv_cell_fails(tree: Path, tmp_path: Path) -> None:
    # written at runtime into tmp only; data files never enter the repo
    (tree / "table.csv").write_text(f"col_a,col_b\n1,{CANARY}\n")
    assert run_check(tree, make_manifest(tmp_path, [CANARY])) == 1


def test_canary_multiline_ast_constant_fails(tree: Path, tmp_path: Path) -> None:
    phrase = f"{CANARY} alpha beta"
    (tree / "mod.py").write_text(
        'DOC = (\n    "Zqvortex alpha "\n    "beta tail"\n)\n'
    )
    assert run_check(tree, make_manifest(tmp_path, [phrase])) == 1


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


def test_fullwidth_compatibility_spelling_fails(tree: Path, tmp_path: Path) -> None:
    fw = "".join(chr(ord(c) + 0xFEE0) for c in CANARY)
    (tree / "wide.md").write_text(f"token {fw} end\n")
    assert run_check(tree, make_manifest(tmp_path, [CANARY])) == 1


def test_control_byte_binary_is_violation(tree: Path, tmp_path: Path) -> None:
    (tree / "blob.txt").write_bytes(b"looks text \x01\x02 but is not")
    assert run_check(tree, make_manifest(tmp_path, [CANARY])) == 2


def test_magic_signature_is_violation(tree: Path, tmp_path: Path) -> None:
    (tree / "archive.txt").write_bytes(bytes.fromhex("504b0304") + b"rest")
    assert run_check(tree, make_manifest(tmp_path, [CANARY])) == 2


def test_repo_tree_is_clean_under_real_manifest() -> None:
    repo = TOOLS.parent.parent
    assert check.main([str(repo)]) == 0


def _verify(tmp_dir: Path) -> int:
    proc = subprocess.run(
        [sys.executable, str(tmp_dir / "verify_attestation.py")],
        capture_output=True, text=True, check=False,
    )
    return proc.returncode


@pytest.fixture()
def att_copy(tmp_path: Path) -> Path:
    d = tmp_path / "decontam"
    shutil.copytree(TOOLS, d)
    return d


def test_attestation_verifies_as_committed(att_copy: Path) -> None:
    assert _verify(att_copy) == 0


def test_tampered_attestation_rejected(att_copy: Path) -> None:
    att = att_copy / "attestation.json"
    data = json.loads(att.read_text())
    data["entry_count"] = 1  # structurally consistent, content changed
    att.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    assert _verify(att_copy) == 1  # signature no longer covers the bytes


def test_manifest_drift_without_resign_rejected(att_copy: Path) -> None:
    m = att_copy / "manifest.txt"
    m.write_text(m.read_text() + hashlib.sha256(b"new").hexdigest() + "\n")
    assert _verify(att_copy) == 2  # signature ok, digest drift caught
