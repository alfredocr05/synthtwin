"""The commit-message scan and the hooks that run it (plan P4-D362).

CLAUDE.md principle 4 names commit messages, and nothing scanned one
until `tools/hooks/check_messages.py`. These hold it to its word: it
decides with the attested tree's own parser, decoder, tokenizer and
n-gram match, so it finds a canary exactly where check.py finds it in a
file and prints none of it; a message file, a range of commits and the
history past the grandfather line are each read on a throwaway
repository built here; a shallow clone and a missing grandfather are
refused aloud; and the installer puts both hooks in place without
overwriting a hook it did not write.

The canary is the decontamination battery's own invented token, and the
pair two more invented ones; no denied word is written here.
"""

import hashlib
import importlib.util
import inspect
import io
import os
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
HOOKS = REPO / "tools" / "hooks"
DECONTAMINATION = REPO / "tools" / "decontamination"
INSTALLER = HOOKS / "install.sh"

CANARY = "zqvortex"  # the invented token of tests/test_decontamination.py
PAIR = "plovarn zeticule"  # two invented tokens, denied only side by side
DIGEST = {entry: hashlib.sha256(entry.encode()).hexdigest() for entry in (CANARY, PAIR)}
HASHES = set(DIGEST.values())
N_MAX = 2


def _load(name: str, path: Path) -> "object":
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


scanner = _load("check_messages_under_test", HOOKS / "check_messages.py")
tree_scan = _load("decontam_check_for_messages", DECONTAMINATION / "check.py")


def _manifest(folder: Path) -> Path:
    """A manifest denying the canary and the pair, in the committed one's shape."""
    lines = [
        "# test manifest",
        f"# entry_count: {len(HASHES)}",
        f"# n_max: {N_MAX}",
    ]
    for name in (
        "snapshot_tree_sha256", "wordlist_sha256", "seed_sha256",
        "grammar_sha256", "magic_sha256", "tokenizer_sha256",
    ):
        lines += [f"# {name}: {hashlib.sha256(name.encode()).hexdigest()}"]
    lines += ["#"] + sorted(HASHES)
    path = folder / "manifest.txt"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return path


def _env() -> "dict[str, str]":
    """git with no user or system configuration, and a fixed identity."""
    env = dict(os.environ)
    env["GIT_CONFIG_GLOBAL"] = os.devnull
    env["GIT_CONFIG_SYSTEM"] = os.devnull
    for role in ("AUTHOR", "COMMITTER"):
        env[f"GIT_{role}_NAME"] = "synthtwin-test"
        env[f"GIT_{role}_EMAIL"] = "synthtwin-test@example.invalid"
    return env


def _run(where: Path, *arguments: str) -> "subprocess.CompletedProcess[str]":
    return subprocess.run(
        ["git", "-C", str(where), *arguments], capture_output=True, text=True,
        encoding="utf-8", errors="replace", check=False, timeout=120, env=_env(),
    )


def _git(where: Path, *arguments: str) -> str:
    done = _run(where, *arguments)
    assert done.returncode == 0, done.stdout + done.stderr
    return done.stdout.strip()


def _commit(repo: Path, message: str) -> str:
    _git(repo, "commit", "-q", "--allow-empty", "--no-verify", "-m", message)
    return _git(repo, "rev-parse", "HEAD")


@pytest.fixture()
def quiet_git(monkeypatch: pytest.MonkeyPatch) -> None:
    """The scanner's own git calls, isolated from the user's configuration."""
    for name, value in _env().items():
        monkeypatch.setenv(name, value)


_MATCH = re.compile(r"^MATCH commit ([0-9a-f]{40}) line:(\d+) n=(\d+) ([0-9a-f]{12}) ", re.M)


def _reported(printed: str) -> "set[tuple[str, int, int, str]]":
    return {(c, int(line), int(n), d) for c, line, n, d in _MATCH.findall(printed)}


# -- the pure matching ------------------------------------------------------

MESSAGE = (
    "a clean subject line\n"
    "\n"
    f"the canary plainly: {CANARY}\n"
    f"inside a name: some{CANARY.capitalize()}Thing\n"
    + "".join(chr(ord(c) + 0xFEE0) for c in CANARY) + " in fullwidth letters\n"
    "the pair joined: plovarn-Zeticule\n"
    "the pair apart: plovarn here, zeticule there\n"
)


def test_a_canary_is_found_on_its_own_line_in_every_form_the_tokenizer_reads() -> None:
    """Line, n-gram length and digest, in order; the pair only side by side."""
    assert scanner.message_matches(MESSAGE, HASHES, N_MAX) == [
        (3, 1, DIGEST[CANARY]),
        (4, 1, DIGEST[CANARY]),
        (5, 1, DIGEST[CANARY]),
        (6, 2, DIGEST[PAIR]),
    ]
    assert scanner.message_matches("nothing to find\n\nhere\n", HASHES, N_MAX) == []


def test_the_message_scan_and_the_tree_scan_agree_line_for_line(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The same text as a file: check.py reports the same lines, lengths, digests."""
    tree = tmp_path / "tree"
    tree.mkdir()
    (tree / "message.txt").write_text(MESSAGE, encoding="utf-8", newline="\n")
    assert tree_scan.main([str(tree), "--manifest", str(_manifest(tmp_path))]) == 1
    from_the_tree = sorted(
        (int(line), int(n), digest)
        for line, n, digest in re.findall(
            r"^MATCH message\.txt L line:(\d+) n=(\d+) ([0-9a-f]{12}) ",
            capsys.readouterr().out, re.M,
        )
    )
    from_the_scan = sorted(
        (line, n, digest[:12])
        for line, n, digest in scanner.message_matches(MESSAGE, HASHES, N_MAX)
    )
    assert from_the_tree and from_the_scan == from_the_tree


def test_every_deciding_function_is_the_attested_trees_own() -> None:
    """Nothing is restated here, so the two scans cannot drift apart."""
    for used in (
        scanner.load_manifest, scanner._match_hash, scanner.tokenize,
        scanner.decode_bytes, scanner.load_magic,
    ):
        source = inspect.getsourcefile(used)
        assert source is not None
        assert Path(source).resolve().parent == DECONTAMINATION.resolve(), used


# -- mode (a): one message file ----------------------------------------------


def _scan_message(tmp_path: Path, text: "str | bytes") -> int:
    message = tmp_path / "COMMIT_EDITMSG"
    if isinstance(text, bytes):
        message.write_bytes(text)
    else:
        message.write_text(text, encoding="utf-8", newline="\n")
    return scanner.main(
        ["--message-file", str(message), "--manifest", str(_manifest(tmp_path))]
    )


def test_a_message_file_is_reported_by_line_and_digest_and_never_quoted(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert _scan_message(tmp_path, f"subject {CANARY}\n\nplovarn zeticule\n") == 1
    printed = capsys.readouterr().out
    assert f"MATCH message line:1 n=1 {DIGEST[CANARY][:12]} " in printed
    assert f"MATCH message line:3 n=2 {DIGEST[PAIR][:12]} " in printed
    assert "commit message: 2 matches" in printed
    for token in (CANARY, "plovarn", "zeticule", "subject"):
        assert token not in printed.casefold(), token
    assert _scan_message(tmp_path, "a clean message\n") == 0
    assert "commit message: clean" in capsys.readouterr().out


def test_below_the_scissors_is_what_git_drops_and_a_comment_line_is_read(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """`git commit -v` puts the diff under the scissors; `-m` keeps a '#' line."""
    scissors = "# " + "-" * 24 + " >8 " + "-" * 24
    below = f"a clean subject\n{scissors}\n# Do not modify the line above.\n-removed {CANARY}\n"
    assert _scan_message(tmp_path, below) == 0
    assert _scan_message(tmp_path, f"a clean subject\n# a note on {CANARY}\n") == 1
    assert f"MATCH message line:2 n=1 {DIGEST[CANARY][:12]}" in capsys.readouterr().out


def test_a_message_that_is_not_text_or_not_there_is_refused(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert _scan_message(tmp_path, b"subject\x1b[31m red\n") == 2
    assert "VIOLATION message: binary-control" in capsys.readouterr().out
    code = scanner.main(
        ["--message-file", str(tmp_path / "absent"), "--manifest", str(_manifest(tmp_path))]
    )
    assert code == 2
    assert "NOT SCANNED" in capsys.readouterr().out


def test_arguments_that_would_narrow_the_scan_are_refused(tmp_path: Path) -> None:
    for argv in (
        ["--range"],
        ["--range", "--", "--max-count=1"],
        ["--", "--all"],
        ["--message-file", "x", "HEAD"],
        ["--pre-push", "HEAD"],
    ):
        with pytest.raises(SystemExit) as stop:
            scanner.main(argv + ["--manifest", str(_manifest(tmp_path))])
        assert stop.value.code == 2, argv


# -- modes (b) and (c): a throwaway history ----------------------------------


@pytest.fixture(scope="module")
def history(tmp_path_factory: pytest.TempPathFactory) -> "tuple[Path, dict[str, str]]":
    """Seven commits across their own grandfather line.

    The first commit, a canary published before the line, the
    grandfather (whose own message holds one); past it a clean commit,
    a canary in a message BODY, a side commit holding the pair, and the
    merge that joins it, holding the canary.
    """
    repo = tmp_path_factory.mktemp("history")
    _git(repo, "init", "-q")
    named = {"root": _commit(repo, "the first commit")}
    named["old"] = _commit(repo, f"published before the guard {CANARY}")
    named["grandfather"] = _commit(repo, f"the grandfather itself {CANARY}")
    named["clean"] = _commit(repo, "a clean commit past the line")
    named["body"] = _commit(repo, f"a clean subject\n\nand a body that says {CANARY}")
    _git(repo, "checkout", "-q", "-b", "side", named["clean"])
    named["side"] = _commit(repo, "a side commit: plovarn-zeticule")
    _git(repo, "checkout", "-q", "-")
    _git(repo, "merge", "-q", "--no-ff", "-m", f"the merge {CANARY}", "side")
    named["merge"] = _git(repo, "rev-parse", "HEAD")
    return repo, named


def _scan(repo: Path, tmp_path: Path, *argv: str) -> int:
    return scanner.main(
        [*argv, "--repo", str(repo), "--manifest", str(_manifest(tmp_path))]
    )


def test_a_range_reads_every_message_it_reaches_whole_and_merges_too(
    history: "tuple[Path, dict[str, str]]", tmp_path: Path,
    capsys: pytest.CaptureFixture[str], quiet_git: None,
) -> None:
    repo, named = history
    assert _scan(repo, tmp_path, "--range", "HEAD") == 1
    printed = capsys.readouterr().out
    assert _reported(printed) == {
        (named["old"], 1, 1, DIGEST[CANARY][:12]),
        (named["grandfather"], 1, 1, DIGEST[CANARY][:12]),
        (named["body"], 3, 1, DIGEST[CANARY][:12]),
        (named["side"], 1, 2, DIGEST[PAIR][:12]),
        (named["merge"], 1, 1, DIGEST[CANARY][:12]),
    }
    assert "commit messages: 5 matches in 5 of 7 commits scanned" in printed
    assert CANARY not in printed and "plovarn" not in printed
    assert _scan(repo, tmp_path, "--range", f"{named['body']}..{named['merge']}") == 1
    assert {c for c, *_ in _reported(capsys.readouterr().out)} == {
        named["side"], named["merge"]
    }


def test_past_the_grandfather_line_only_new_messages_are_read(
    history: "tuple[Path, dict[str, str]]", tmp_path: Path,
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch,
    quiet_git: None,
) -> None:
    """The canary before the line and the grandfather's own are not reported."""
    repo, named = history
    monkeypatch.setattr(scanner, "GRANDFATHER", named["grandfather"])
    assert _scan(repo, tmp_path) == 1
    printed = capsys.readouterr().out
    assert {c for c, *_ in _reported(printed)} == {
        named["body"], named["side"], named["merge"]
    }
    assert "3 matches in 3 of 4 commits scanned" in printed
    # A pull request's own commits: what its head reaches and its base does not.
    assert _scan(repo, tmp_path, named["merge"], "^" + named["body"]) == 1
    assert {c for c, *_ in _reported(capsys.readouterr().out)} == {
        named["side"], named["merge"]
    }
    assert _scan(repo, tmp_path, named["clean"]) == 0
    assert "clean, 1 commit scanned" in capsys.readouterr().out
    assert _scan(repo, tmp_path, named["grandfather"]) == 0
    assert "clean, 0 commits scanned" in capsys.readouterr().out


def test_a_history_without_the_grandfather_is_refused_aloud(
    history: "tuple[Path, dict[str, str]]", tmp_path: Path,
    capsys: pytest.CaptureFixture[str], quiet_git: None,
) -> None:
    """The committed constant names a commit this throwaway history lacks."""
    repo, _named = history
    assert _scan(repo, tmp_path) == 2
    printed = capsys.readouterr().out
    assert "NOT SCANNED" in printed and scanner.GRANDFATHER in printed


def test_a_shallow_clone_is_refused_even_when_it_holds_the_grandfather(
    tmp_path: Path, capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch, quiet_git: None,
) -> None:
    """Its cut hides a canary past the line, and nothing else would say so.

    The canary sits on a branch merged after the grandfather, two parents
    down from the merge; a clone two deep holds the merge, the
    grandfather and the canary's child, and not the canary.
    """
    origin = tmp_path / "origin"
    origin.mkdir()
    _git(origin, "init", "-q")
    root = _commit(origin, "the first commit")
    _git(origin, "checkout", "-q", "-b", "topic")
    _commit(origin, f"hidden below the cut {CANARY}")
    _commit(origin, "a clean child")
    _git(origin, "checkout", "-q", "-b", "trunk", root)
    grandfather = _commit(origin, "the grandfather")
    _git(origin, "merge", "-q", "--no-ff", "-m", "the merge", "topic")
    monkeypatch.setattr(scanner, "GRANDFATHER", grandfather)
    assert _scan(origin, tmp_path) == 1
    capsys.readouterr()

    shallow = tmp_path / "shallow"
    _git(tmp_path, "clone", "-q", "--depth", "2", origin.as_uri(), str(shallow))
    assert _git(shallow, "rev-parse", "--is-shallow-repository") == "true"
    assert _run(shallow, "cat-file", "-e", grandfather + "^{commit}").returncode == 0
    assert _scan(shallow, tmp_path) == 2
    printed = capsys.readouterr().out
    assert "NOT SCANNED" in printed and "SHALLOW" in printed
    assert _scan(shallow, tmp_path, "--range", "HEAD") == 2


def test_a_message_that_is_not_text_is_a_violation_beside_the_matches(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], quiet_git: None
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _commit(repo, f"a canary {CANARY}")
    coloured = _commit(repo, "coloured \x1b[31m text")
    assert _scan(repo, tmp_path, "--range", "HEAD") == 3
    printed = capsys.readouterr().out
    assert f"VIOLATION commit {coloured}: binary-control" in printed
    assert "1 match in 1 of 2 commits scanned, 1 violation" in printed


# -- the pre-push input --------------------------------------------------------

ZERO = "0" * 40


def test_the_pushed_commits_are_named_from_the_pre_push_input() -> None:
    local, remote, unfetched = "a" * 40, "b" * 40, "c" * 40
    held = {remote}.__contains__
    assert scanner.pushed_revisions([], held) == []
    assert scanner.pushed_revisions(
        [f"(delete) {ZERO} refs/heads/gone {remote}", ""], held
    ) == []
    assert scanner.pushed_revisions(
        [f"refs/heads/new {local} refs/heads/new {ZERO}"], held
    ) == [local]
    assert scanner.pushed_revisions(
        [f"refs/heads/x {local} refs/heads/x {remote}"], held
    ) == [local, "^" + remote]
    assert scanner.pushed_revisions(
        [f"refs/heads/x {local} refs/heads/x {unfetched}"], held
    ) == [local]
    for bad in (f"refs/heads/x {local} refs/heads/x", f"refs/heads/x --all refs/heads/x {remote}"):
        with pytest.raises(scanner.ScanRefused):
            scanner.pushed_revisions([bad], held)


def test_a_push_is_scanned_past_its_remote_and_past_the_grandfather(
    history: "tuple[Path, dict[str, str]]", tmp_path: Path,
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch,
    quiet_git: None,
) -> None:
    repo, named = history
    monkeypatch.setattr(scanner, "GRANDFATHER", named["grandfather"])
    pushes = {
        f"refs/heads/main {named['merge']} refs/heads/main {named['body']}\n": {
            named["side"], named["merge"]
        },
        f"refs/heads/main {named['merge']} refs/heads/main {ZERO}\n": {
            named["body"], named["side"], named["merge"]
        },
    }
    for pushed, expected in pushes.items():
        monkeypatch.setattr(sys, "stdin", io.StringIO(pushed))
        assert _scan(repo, tmp_path, "--pre-push") == 1
        assert {c for c, *_ in _reported(capsys.readouterr().out)} == expected
    monkeypatch.setattr(sys, "stdin", io.StringIO(f"(delete) {ZERO} refs/heads/x {named['old']}\n"))
    assert _scan(repo, tmp_path, "--pre-push") == 0
    assert "this push sends no commit" in capsys.readouterr().out


# -- the installer ---------------------------------------------------------------


def _install(repo: Path) -> "subprocess.CompletedProcess[str]":
    return subprocess.run(
        ["sh", str(INSTALLER)], cwd=str(repo), capture_output=True, text=True,
        check=False, timeout=120, env=_env(),
    )


def test_the_installer_puts_both_hooks_in_place_and_a_rerun_stays_quiet(
    tmp_path: Path,
) -> None:
    _git(tmp_path, "init", "-q")
    first = _install(tmp_path)
    assert first.returncode == 0, first.stdout + first.stderr
    hooks = tmp_path / ".git" / "hooks"
    for name, runs in (
        ("pre-push", "tools/hooks/check_messages.py --pre-push"),
        ("commit-msg", 'tools/hooks/check_messages.py" --message-file "$1"'),
    ):
        hook = hooks / name
        assert hook.is_file() and os.access(hook, os.X_OK), name
        assert runs in hook.read_text(encoding="utf-8"), name
        assert f"Installed the advisory {name} hook" in first.stdout
    installed = {name: (hooks / name).read_bytes() for name in ("pre-push", "commit-msg")}
    second = _install(tmp_path)
    assert (second.returncode, second.stdout, second.stderr) == (0, "", "")
    assert {name: (hooks / name).read_bytes() for name in installed} == installed


def test_a_different_hook_is_never_overwritten_and_the_other_still_goes_in(
    tmp_path: Path,
) -> None:
    runs = {"pre-push": b"--pre-push", "commit-msg": b"--message-file"}
    for foreign_name, other in (("commit-msg", "pre-push"), ("pre-push", "commit-msg")):
        repo = tmp_path / foreign_name
        repo.mkdir()
        _git(repo, "init", "-q")
        hooks = repo / ".git" / "hooks"
        hooks.mkdir(parents=True, exist_ok=True)
        foreign = "#!/bin/sh\necho an organizational policy\n"
        (hooks / foreign_name).write_text(foreign, encoding="utf-8", newline="\n")
        result = _install(repo)
        assert result.returncode == 1, result.stdout + result.stderr
        assert (hooks / foreign_name).read_text(encoding="utf-8") == foreign
        assert f"a different {foreign_name} hook already exists" in result.stderr
        assert "Refusing to overwrite" in result.stderr
        assert not (hooks / f"{foreign_name}.synthtwin.tmp").exists()
        # The refusal is of that one hook: the other goes in all the same.
        assert f"Installed the advisory {other} hook" in result.stdout
        assert runs[other] in (hooks / other).read_bytes()


# The pre-push hook this installer wrote from 2bf3907 to 82b1f1a, byte for
# byte: the one an owner who installed it before this landing holds.
EARLIER_PRE_PUSH = """#!/bin/sh
# synthtwin advisory pre-push hook: runs the three guards on the tree
# about to be pushed. Advisory by design (plan D13): it can be bypassed
# with --no-verify. CI remains the authoritative check; from Phase 3's
# visibility flip the branch ruleset makes the CI gate a mechanically
# enforced merge requirement (see SECURITY.md's activation record).
set -e
cd "$(git rev-parse --show-toplevel)"
PY=".venv/bin/python"; [ -x "$PY" ] || PY="python3"
echo "pre-push: decontamination scan..."
"$PY" tools/decontamination/check.py
echo "pre-push: attestation verification..."
"$PY" tools/decontamination/verify_attestation.py
echo "pre-push: offline static scan..."
"$PY" tools/offline_scan/scan_imports.py src
echo "pre-push: provenance check..."
"$PY" tools/provenance/check_provenance.py
echo "pre-push: all guards passed."
"""


def test_the_earlier_pre_push_hook_is_replaced_and_an_edited_one_is_not(
    tmp_path: Path,
) -> None:
    """Replacing a hook this installer wrote loses nothing; an edit is not ours."""
    for label, text, replaced in (
        ("earlier", EARLIER_PRE_PUSH, True),
        ("edited", EARLIER_PRE_PUSH + "echo one more organizational check\n", False),
    ):
        repo = tmp_path / label
        repo.mkdir()
        _git(repo, "init", "-q")
        hook = repo / ".git" / "hooks" / "pre-push"
        hook.parent.mkdir(parents=True, exist_ok=True)
        hook.write_text(text, encoding="utf-8", newline="\n")
        result = _install(repo)
        now = hook.read_text(encoding="utf-8")
        if replaced:
            assert result.returncode == 0, result.stdout + result.stderr
            assert "Replaced the earlier synthtwin pre-push hook" in result.stdout
            assert "check_messages.py --pre-push" in now
            for guard in re.findall(r'^"\$PY" (.*)$', text, re.M):
                assert f'"$PY" {guard}\n' in now, guard
        else:
            assert result.returncode == 1, result.stdout + result.stderr
            assert now == text
            assert "a different pre-push hook already exists" in result.stderr


@pytest.mark.skipif(
    sys.platform == "win32",
    reason="the hooks run under sh here through a POSIX wrapper for this interpreter",
)
def test_the_installed_hooks_stop_a_canary_at_the_commit_and_at_the_push(
    tmp_path: Path,
) -> None:
    """End to end, through git itself, on a repository carrying the scanners.

    The tree holds the real scanners, a manifest denying the canary and
    stand-ins for the three guards that read nothing of it; its copy of
    the message scanner names this history's own grandfather.
    """
    work = tmp_path / "work"
    tools = work / "tools"
    for folder in ("hooks", "decontamination", "offline_scan", "provenance"):
        (tools / folder).mkdir(parents=True)
    _git(work, "init", "-q")
    for name in ("check.py", "surfaces.py", "tokenizer.py", "magic.txt"):
        shutil.copyfile(DECONTAMINATION / name, tools / "decontamination" / name)
    _manifest(tools / "decontamination")
    for stand_in in (
        "decontamination/verify_attestation.py",
        "offline_scan/scan_imports.py",
        "provenance/check_provenance.py",
    ):
        (tools / stand_in).write_text("raise SystemExit(0)\n", encoding="utf-8")
    copy = tools / "hooks" / "check_messages.py"
    shutil.copyfile(HOOKS / "check_messages.py", copy)
    python = work / ".venv" / "bin" / "python"
    python.parent.mkdir(parents=True)
    python.write_text(f'#!/bin/sh\nexec {shlex.quote(sys.executable)} "$@"\n', encoding="utf-8")
    python.chmod(0o755)
    (work / ".gitignore").write_text(".venv/\n", encoding="utf-8")
    _git(work, "add", "-A")
    _commit(work, "the tools the hooks run")
    _commit(work, f"published before the guard {CANARY}")
    grandfather = _commit(work, "the grandfather")
    stated = f'GRANDFATHER = "{scanner.GRANDFATHER}"'
    text = copy.read_text(encoding="utf-8")
    assert text.count(stated) == 1
    copy.write_text(text.replace(stated, f'GRANDFATHER = "{grandfather}"'), encoding="utf-8")
    _git(work, "add", "-A")
    _commit(work, "the scanner names this history's grandfather")
    remote = tmp_path / "remote.git"
    _git(tmp_path, "init", "-q", "--bare", str(remote))
    _git(work, "remote", "add", "origin", str(remote))
    installed = _install(work)
    assert installed.returncode == 0, installed.stdout + installed.stderr

    # Every commit is new to the remote; the canary stands before the line.
    first = _run(work, "push", "origin", "HEAD:refs/heads/main")
    assert first.returncode == 0, first.stdout + first.stderr
    assert "past the grandfather line" in first.stdout + first.stderr

    head = _git(work, "rev-parse", "HEAD")
    refused = _run(work, "commit", "--allow-empty", "-m", f"a new message {CANARY}")
    told = refused.stdout + refused.stderr
    assert refused.returncode != 0, told
    assert f"MATCH message line:1 n=1 {DIGEST[CANARY][:12]}" in told
    assert CANARY not in told
    assert _git(work, "rev-parse", "HEAD") == head

    _commit(work, f"made past the hook {CANARY}")
    stopped = _run(work, "push", "origin", "HEAD:refs/heads/main")
    told = stopped.stdout + stopped.stderr
    assert stopped.returncode != 0, told
    assert "MATCH commit" in told and CANARY not in told
    assert _git(remote, "rev-parse", "main") == head

    reworded = _run(work, "commit", "--amend", "--allow-empty", "-m", "reworded")
    assert reworded.returncode == 0, reworded.stdout + reworded.stderr
    pushed = _run(work, "push", "origin", "HEAD:refs/heads/main")
    assert pushed.returncode == 0, pushed.stdout + pushed.stderr
    assert _git(remote, "rev-parse", "main") == _git(work, "rev-parse", "HEAD")
