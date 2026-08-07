"""Decontamination machinery self-tests (plan D7; code-review round-1
items F13/F20 and round-2 items R2-B4, R2-B6, and R2-M1 folded in):
neutral canaries in every surface form, the decoder battery driven by
every signature in the committed magic table, value-silent output, the
strict shared manifest parser, and attestation rejection with each inner
check isolated under a temporary pinned key. The real inventory is never
reproduced here; canaries are invented tokens.
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


# Digest headers the strict shared parser requires (round-2 item R2-B4);
# test manifests carry syntactically valid filler values for them.
FILLER_DIGEST_HEADERS = (
    "snapshot_tree_sha256",
    "wordlist_sha256",
    "seed_sha256",
    "grammar_sha256",
    "magic_sha256",
    "tokenizer_sha256",
)


def make_manifest(tmp_path: Path, entries: list[str]) -> Path:
    hashes = sorted(hashlib.sha256(e.encode()).hexdigest() for e in entries)
    n_max = max(len(e.split(" ")) for e in entries)
    header = [
        "# test manifest",
        f"# entry_count: {len(hashes)}",
        f"# n_max: {n_max}",
    ]
    for name in FILLER_DIGEST_HEADERS:
        header.append(f"# {name}: {hashlib.sha256(name.encode()).hexdigest()}")
    header.append("#")
    m = tmp_path / "manifest.txt"
    m.write_text("\n".join(header) + "\n" + "\n".join(hashes) + "\n")
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
    (tree / "wide.md").write_text(f"token {fw} end\n", encoding="utf-8")
    assert run_check(tree, make_manifest(tmp_path, [CANARY])) == 1


def test_enclosed_compatibility_spelling_fails(
    tree: Path, tmp_path: Path
) -> None:
    # Circled letters NFKC-normalize to plain letters (ratified R2-C1).
    enclosed = "".join(chr(0x24D0 + (ord(c) - ord("a"))) for c in CANARY)
    (tree / "circled.md").write_text(f"token {enclosed} end\n", encoding="utf-8")
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


class _StrictAsciiStdout:
    """Stand-in for a console whose encoding cannot represent non-ASCII
    text (a cp1252 or POSIX-C stream): any non-ASCII character written
    to it raises UnicodeEncodeError, exactly like the real stream."""

    def __init__(self) -> None:
        self.chunks: list[str] = []

    def write(self, text: str) -> int:
        text.encode("ascii", "strict")
        self.chunks.append(text)
        return len(text)

    def flush(self) -> None:
        pass


def test_non_ascii_violation_path_reports_on_ascii_stdout(
    tree: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Round-4 item R4-m1: a control-byte file whose NAME contains a
    # non-ASCII character (the name matches nothing in the manifest, so
    # it is printed unredacted) must still produce the value-silent
    # violation report and the violation exit code when stdout cannot
    # encode the name. The pre-repair scanner raised UnicodeEncodeError
    # from print, replacing exit code 2 with a traceback.
    name = "caf\u00e9-blob.txt"  # e-acute as an escape: ASCII source
    (tree / name).write_bytes(b"looks text \x01\x02 but is not")
    writer = _StrictAsciiStdout()
    monkeypatch.setattr(sys, "stdout", writer)
    code = run_check(tree, make_manifest(tmp_path, [CANARY]))
    out = "".join(writer.chunks)
    assert code == 2, out
    assert "VIOLATION" in out
    # The untrusted name is escaped, never dropped and never raised on.
    assert "\\xe9" in out


# Round-2 item R2-B6: the mutation battery is parameterized over EVERY
# signature read from the committed magic table at test time, so a table
# refresh can never leave a signature untested.
MAGIC_TABLE = check.load_magic(TOOLS / "magic.txt")


def test_committed_magic_table_is_nonempty() -> None:
    # Guards the parametrized battery below: an emptied table must fail
    # loudly here instead of silently collecting zero cases.
    assert len(MAGIC_TABLE) >= 4


@pytest.mark.parametrize(
    "offset,sig", MAGIC_TABLE, ids=[sig.hex() for _off, sig in MAGIC_TABLE]
)
def test_every_committed_magic_signature_is_a_violation(
    tree: Path, tmp_path: Path, offset: int, sig: bytes
) -> None:
    (tree / "payload.txt").write_bytes(b"A" * offset + sig + b"rest")
    assert run_check(tree, make_manifest(tmp_path, [CANARY])) == 2


# ---------- strict shared manifest parser ----------------------------------


def test_scanner_rejects_duplicate_manifest_header(
    tree: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # Round-2 item R2-B4: a second n_max header is a hard error in the
    # single shared parser, never a silent precedence choice.
    m = make_manifest(tmp_path, [CANARY])
    m.write_text(m.read_text() + "# n_max: 1\n")
    assert run_check(tree, m) == 2
    out = capsys.readouterr().out
    assert "n_max" in out and "more than once" in out


def test_scanner_rejects_non_hex_manifest_body_line(
    tree: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    m = make_manifest(tmp_path, [CANARY])
    m.write_text(m.read_text() + "Z" * 64 + "\n")
    assert run_check(tree, m) == 2
    assert "64 lowercase hex" in capsys.readouterr().out


def test_scanner_rejects_missing_mandatory_header(
    tree: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    m = make_manifest(tmp_path, [CANARY])
    kept = [
        ln for ln in m.read_text().splitlines()
        if not ln.startswith("# wordlist_sha256:")
    ]
    m.write_text("\n".join(kept) + "\n")
    assert run_check(tree, m) == 2
    assert "wordlist_sha256" in capsys.readouterr().out


# ---------- the real repository -------------------------------------------


def test_repo_tree_is_clean_under_real_manifest() -> None:
    repo = TOOLS.parent.parent
    assert check.main([str(repo)]) == 0


# ---------- attestation ----------------------------------------------------

SCANNER_TREE_NAMES = [
    "allowed_signers",
    "check.py",
    "magic.txt",
    "manifest.txt",
    "surfaces.py",
    "tokenizer.py",
    "verify_attestation.py",
]


def _verify(tmp_dir: Path) -> int:
    return _verify_out(tmp_dir)[0]


def _verify_out(tmp_dir: Path) -> tuple[int, str]:
    proc = subprocess.run(
        [sys.executable, str(tmp_dir / "verify_attestation.py")],
        capture_output=True, text=True, check=False,
    )
    return proc.returncode, proc.stdout


def _sha256_path(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _scanner_tree_digest(d: Path) -> str:
    h = hashlib.sha256()
    for name in sorted(SCANNER_TREE_NAMES):
        h.update(name.encode() + b"\0" + (d / name).read_bytes())
    return h.hexdigest()


def _temp_signer(att_copy: Path, tmp_path: Path) -> Path:
    """Create a fresh signing key and pin it in the temp tree's
    allowed_signers, so mutation tests can re-sign consistent outer
    bindings and isolate one inner check each (round-2 item R2-B4)."""
    key = tmp_path / "temp_signing_key"
    subprocess.run(
        ["ssh-keygen", "-t", "ed25519", "-f", str(key), "-N", "", "-q"],
        check=True,
    )
    key_type, key_body = key.with_suffix(".pub").read_text().split()[:2]
    (att_copy / "allowed_signers").write_text(
        f"synthtwin-maintainer {key_type} {key_body}\n"
    )
    return key


def _sign_attestation(att_copy: Path, key: Path) -> None:
    """Sign the temp tree's attestation.json bytes exactly as they sit
    on disk, so a test can hand-shape the raw JSON text (for example a
    duplicate member name) and still carry a VALID signature."""
    sig = att_copy / "attestation.json.sig"
    if sig.exists():
        sig.unlink()
    subprocess.run(
        ["ssh-keygen", "-Y", "sign", "-f", str(key),
         "-n", "synthtwin-attestation", str(att_copy / "attestation.json")],
        check=True, capture_output=True,
    )


def _rewrite_manifest_headers(att_copy: Path, values: dict[str, str]) -> None:
    """Set named manifest digest header lines to the given values while
    leaving every other manifest byte alone, so intentional manifest
    mutations made by a test survive the header refresh."""
    m = att_copy / "manifest.txt"
    lines = m.read_text().splitlines()
    for i, ln in enumerate(lines):
        for name, value in values.items():
            if ln.startswith(f"# {name}:"):
                lines[i] = f"# {name}: {value}"
    m.write_text("\n".join(lines) + "\n")


def _refresh_outer_and_sign(
    att_copy: Path, key: Path, *, skip: set[str] = frozenset(), edit=None
) -> None:
    """Recompute every public outer binding over the CURRENT temp-tree
    bytes, apply the single inner break via ``edit``, and re-sign with
    the temp key, so a red verifier result can only come from the one
    broken inner property (round-2 items R2-B4 and R2-M1). ``skip``
    leaves named bindings stale on purpose. The manifest digest headers
    that mirror per-file bindings are rewritten to the post-``skip``
    binding values, exactly as a maintainer refresh keeps them, so the
    temp tree stays self-consistent even while the live tree awaits its
    maintainer re-sign."""
    att_path = att_copy / "attestation.json"
    att = json.loads(att_path.read_text())
    b = att["bindings"]
    fresh = {
        "magic_table_sha256": _sha256_path(att_copy / "magic.txt"),
        "public_tokenizer_sha256": _sha256_path(att_copy / "tokenizer.py"),
        "public_surfaces_sha256": _sha256_path(att_copy / "surfaces.py"),
    }
    for name, value in fresh.items():
        if name not in skip:
            b[name] = value
    _rewrite_manifest_headers(att_copy, {
        "magic_sha256": b["magic_table_sha256"],
        "tokenizer_sha256": b["public_tokenizer_sha256"],
    })
    if "public_manifest_sha256" not in skip:
        b["public_manifest_sha256"] = _sha256_path(att_copy / "manifest.txt")
    if "public_scanner_tree_sha256" not in skip:
        b["public_scanner_tree_sha256"] = _scanner_tree_digest(att_copy)
    if edit is not None:
        edit(att)
    att_path.write_text(json.dumps(att, indent=2, sort_keys=True) + "\n")
    _sign_attestation(att_copy, key)


@pytest.fixture()
def att_copy(tmp_path: Path) -> Path:
    d = tmp_path / "decontam"
    shutil.copytree(TOOLS, d, ignore=shutil.ignore_patterns("__pycache__"))
    return d


def test_committed_signature_is_valid(att_copy: Path) -> None:
    # The committed signature bytes must validate against the committed
    # pinned key. (End-to-end exit 0 over the committed bytes also needs
    # the maintainer refresh-and-re-sign step that the round-2 review
    # orders after any change to a scanner-tree file; the temp-key
    # control below proves the full green path of the verifier itself.)
    proc = subprocess.run(
        [
            "ssh-keygen", "-Y", "verify",
            "-f", str(att_copy / "allowed_signers"),
            "-I", "synthtwin-maintainer", "-n", "synthtwin-attestation",
            "-s", str(att_copy / "attestation.json.sig"),
        ],
        stdin=(att_copy / "attestation.json").open("rb"),
        capture_output=True, check=False,
    )
    assert proc.returncode == 0


def test_temp_resigned_consistent_tree_verifies(
    att_copy: Path, tmp_path: Path
) -> None:
    # Harness control (round-2 item R2-B4): with a temp pinned key and
    # every outer binding recomputed over the temp tree, the verifier is
    # green - so each mutation below is red for exactly its one broken
    # inner property, never for outer digest or signature drift.
    key = _temp_signer(att_copy, tmp_path)
    _refresh_outer_and_sign(att_copy, key)
    code, out = _verify_out(att_copy)
    assert code == 0, out


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


# Each test below breaks exactly ONE inner property, then recomputes all
# consistent outer bindings and re-signs with a temp pinned key (round-2
# items R2-B4 and R2-M1), so the red result names the inner check itself.


def test_missing_binding_key_rejected(att_copy: Path, tmp_path: Path) -> None:
    key = _temp_signer(att_copy, tmp_path)

    def drop(att: dict) -> None:
        del att["bindings"]["plaintext_inventory_sha256"]

    _refresh_outer_and_sign(att_copy, key, edit=drop)
    code, out = _verify_out(att_copy)
    assert code == 2
    assert "missing binding 'plaintext_inventory_sha256'" in out


def test_wrong_entry_count_type_rejected(
    att_copy: Path, tmp_path: Path
) -> None:
    key = _temp_signer(att_copy, tmp_path)

    def stringly(att: dict) -> None:
        att["entry_count"] = str(att["entry_count"])

    _refresh_outer_and_sign(att_copy, key, edit=stringly)
    code, out = _verify_out(att_copy)
    assert code == 2
    assert "'entry_count'" in out and "wrong type" in out


def test_wrong_tokenizer_digest_rejected(
    att_copy: Path, tmp_path: Path
) -> None:
    # The tokenizer file changes but its individual binding stays stale;
    # the scanner-tree digest IS refreshed, so only the direct per-file
    # recomputation can catch it.
    tok = att_copy / "tokenizer.py"
    tok.write_text(tok.read_text() + "\n# drifted line\n")
    key = _temp_signer(att_copy, tmp_path)
    _refresh_outer_and_sign(att_copy, key, skip={"public_tokenizer_sha256"})
    code, out = _verify_out(att_copy)
    assert code == 2
    assert "tokenizer.py digest vs binding public_tokenizer_sha256" in out
    assert "scanner tree" not in out  # tree was refreshed: check isolated


def test_wrong_surfaces_digest_rejected(
    att_copy: Path, tmp_path: Path
) -> None:
    surf = att_copy / "surfaces.py"
    surf.write_text(surf.read_text() + "\n# drifted line\n")
    key = _temp_signer(att_copy, tmp_path)
    _refresh_outer_and_sign(att_copy, key, skip={"public_surfaces_sha256"})
    code, out = _verify_out(att_copy)
    assert code == 2
    assert "surfaces.py digest vs binding public_surfaces_sha256" in out
    assert "scanner tree" not in out


def test_snapshot_header_binding_mismatch_rejected(
    att_copy: Path, tmp_path: Path
) -> None:
    # The manifest header snapshot_tree_sha256 and the signed snapshot
    # binding disagree; nothing else in the graph is inconsistent.
    key = _temp_signer(att_copy, tmp_path)
    other = hashlib.sha256(b"a different snapshot value").hexdigest()

    def bend(att: dict) -> None:
        att["bindings"]["prototype_snapshot_tree_sha256"] = other

    _refresh_outer_and_sign(att_copy, key, edit=bend)
    code, out = _verify_out(att_copy)
    assert code == 2
    assert (
        "manifest header snapshot_tree_sha256 vs binding "
        "prototype_snapshot_tree_sha256"
    ) in out


def test_duplicate_n_max_header_rejected(
    att_copy: Path, tmp_path: Path
) -> None:
    # A second n_max line, with the manifest digest binding refreshed to
    # the mutated bytes: only the strict shared parser can reject it.
    m = att_copy / "manifest.txt"
    m.write_text(m.read_text() + "# n_max: 1\n")
    key = _temp_signer(att_copy, tmp_path)
    _refresh_outer_and_sign(att_copy, key)
    code, out = _verify_out(att_copy)
    assert code == 2
    assert "n_max" in out and "more than once" in out


def test_non_hex_body_line_rejected(att_copy: Path, tmp_path: Path) -> None:
    m = att_copy / "manifest.txt"
    bad = hashlib.sha256(b"upper").hexdigest().upper()  # uppercase: invalid
    m.write_text(m.read_text() + bad + "\n")
    key = _temp_signer(att_copy, tmp_path)
    _refresh_outer_and_sign(att_copy, key)
    code, out = _verify_out(att_copy)
    assert code == 2
    assert "64 lowercase hex" in out


def test_duplicate_body_line_rejected(att_copy: Path, tmp_path: Path) -> None:
    # Replace the last body line with a copy of the first: the count is
    # unchanged, so only the duplicate check can go red.
    m = att_copy / "manifest.txt"
    lines = m.read_text().splitlines()
    body = [ln for ln in lines if ln and not ln.startswith("#")]
    lines[lines.index(body[-1])] = body[0]
    m.write_text("\n".join(lines) + "\n")
    key = _temp_signer(att_copy, tmp_path)
    _refresh_outer_and_sign(att_copy, key)
    code, out = _verify_out(att_copy)
    assert code == 2
    assert "duplicate manifest hash lines" in out
    assert "hash-line count" not in out


def test_duplicate_top_level_member_rejected(
    att_copy: Path, tmp_path: Path
) -> None:
    # Round-3 item R2-B4: a freshly signed attestation carrying the same
    # top-level member twice with contradictory values must be refused
    # as schema-invalid, never parsed with the last value winning
    # silently. The temp key makes the signature VALID, so only the
    # duplicate-member check can fire.
    key = _temp_signer(att_copy, tmp_path)
    _refresh_outer_and_sign(att_copy, key)
    att_path = att_copy / "attestation.json"
    text = att_path.read_text()
    assert '  "result": "pass"' in text
    att_path.write_text(
        text.replace(
            '  "result": "pass"',
            '  "result": "fail",\n  "result": "pass"',
            1,
        )
    )
    _sign_attestation(att_copy, key)
    code, out = _verify_out(att_copy)
    assert code == 2
    assert "SCHEMA INVALID" in out
    assert "'result'" in out and "more than once" in out


def test_duplicate_binding_member_rejected(
    att_copy: Path, tmp_path: Path
) -> None:
    # Round-3 item R2-B4, nested depth: a stale binding value followed
    # by the current one under the SAME member name inside "bindings".
    # A last-value-wins parse would see only the fresh digest and pass;
    # the verifier must instead refuse the ambiguous signed graph and
    # name the duplicated member.
    key = _temp_signer(att_copy, tmp_path)
    _refresh_outer_and_sign(att_copy, key)
    att_path = att_copy / "attestation.json"
    lines = att_path.read_text().splitlines()
    idx = next(
        i for i, ln in enumerate(lines)
        if '"public_manifest_sha256":' in ln
    )
    stale = '    "public_manifest_sha256": "' + "0" * 64 + '",'
    lines.insert(idx, stale)
    att_path.write_text("\n".join(lines) + "\n")
    _sign_attestation(att_copy, key)
    code, out = _verify_out(att_copy)
    assert code == 2
    assert "SCHEMA INVALID" in out
    assert "'public_manifest_sha256'" in out and "more than once" in out


def test_count_check_isolated_from_digest_drift(
    att_copy: Path, tmp_path: Path
) -> None:
    # Round-2 item R2-M1: remove one body line, keep the header count,
    # and REFRESH the outer manifest digest before re-signing, so the
    # only possible red reason is the actual line-count comparison. If a
    # refactor deletes that comparison, this test goes green and fails.
    m = att_copy / "manifest.txt"
    lines = m.read_text().splitlines()
    body = [ln for ln in lines if ln and not ln.startswith("#")]
    lines.remove(body[-1])
    m.write_text("\n".join(lines) + "\n")
    key = _temp_signer(att_copy, tmp_path)
    _refresh_outer_and_sign(att_copy, key)
    code, out = _verify_out(att_copy)
    assert code == 2
    assert "actual manifest hash-line count vs header entry_count" in out
    assert "manifest.txt digest" not in out  # isolated from digest drift
