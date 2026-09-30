#!/usr/bin/env python3
"""The commit-message scan: the decontamination manifest applied to messages.

WHY IT EXISTS. CLAUDE.md principle 4 names commit messages among the
places no denied vocabulary may appear, and nothing scanned one:
`tools/decontamination/check.py` reads the tracked tree, and a message
is not in the tree. The public history of `phase-5-relationships` held
104 matches in 87 of its 646 messages at d93fd43, and the 134 commits
pushed at 82b1f1a on 2026-09-30 brought 14 more in 13. By the owner's
decision of 2026-09-30 those stay as published and no NEW message may
carry one (plan P4-D362).

WHY HERE AND NOT BESIDE check.py. `tools/decontamination/` is the
attested tree: the signed attestation binds it, only the owner can
re-sign it, and a file added there changes it. This file decides
nothing of its own. The manifest parser, the decoder, the tokenizer and
the n-gram hash match are that tree's own functions, imported read-only,
so this scan and check.py cannot disagree about a line of text. What is
here is only where the text comes from, and it sits beside `install.sh`,
which installs the two hooks that run it.

MODES.

    check_messages.py --message-file FILE   (a) one message, as a commit-msg hook gets it
    check_messages.py --range REVISION...   (b) every commit the revisions reach
    check_messages.py [REVISION...]         (c) every commit the revisions reach (HEAD
                                                if none is given) that the grandfather
                                                commit does not
    check_messages.py --pre-push            (c) over the commits a push sends, named
                                                on the pre-push hook's input

A message is read by the attested decoder and matched line by line, as
check.py matches the lines of a file. In mode (a) git's scissors line
and everything below it are left out, because git drops them from the
message it stores; every other line is read, git's own comment lines
included, since git keeps a '#' line of a message given with -m.

Modes (b) and (c) refuse a shallow clone, whose history stops short
without saying where, and mode (c) refuses a history that lacks the
grandfather commit: neither is ever passed silently.

Output is value-silent, as check.py's is: the commit, the line of its
message, the n-gram length and a digest prefix, never the matched text.
Exit codes are check.py's: 0 clean, 1 matches, 2 violations -- a message
that is not scannable text, or a scan that could not be made -- 3 both.
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DECONTAMINATION = HERE.parent / "decontamination"
sys.path.insert(0, str(DECONTAMINATION))

# The attested tree's own functions, imported and never restated: one
# manifest parser, one decoder, one tokenizer and one match for both scans.
from check import ManifestFormatError, _match_hash, load_manifest
from surfaces import decode_bytes, load_magic
from tokenizer import tokenize

MANIFEST = DECONTAMINATION / "manifest.txt"
MAGIC = DECONTAMINATION / "magic.txt"

# THE GRANDFATHER LINE. The tip of `phase-5-relationships` as pushed on
# 2026-09-30 (committed 2026-09-29), before any commit message was scanned. The 118 matches in
# 100 of the 780 messages it reaches were published before this guard
# existed, and by the owner's decision of 2026-09-30 they are not
# rewritten; mode (c) reads every commit this one does not reach, and
# only those (plan P4-D362).
GRANDFATHER = "82b1f1a458ee694f9676dbfb370919a77fe977b3"

# git's scissors line, under any comment prefix. git drops it and every
# line below it -- the diff `git commit -v` shows is there.
_SCISSORS = re.compile(r"\S+ -{24} >8 -{24}")
_OBJECT = re.compile(r"[0-9a-f]{40}|[0-9a-f]{64}")
_LOG = [
    "log", "-z", "--format=%H%n%B", "--no-show-signature", "--no-notes",
    "--no-color", "--encoding=UTF-8",
]
_REWORD = (
    "reword that commit (git commit --amend for the last one, git rebase -i "
    "for an earlier one) before it is pushed"
)


class ScanRefused(Exception):
    """The history cannot be scanned as asked; the text says what to do."""


def message_matches(text, hashes, n_max):
    """Every match the manifest finds in one message: (line, n, digest), in order.

    Each line is tokenized and matched on its own, exactly as check.py
    matches a line of a file, and a blank line holds nothing to match.
    Pure: the same text, hashes and n_max give the same list.
    """
    found = []
    for lineno, line in enumerate(text.splitlines(), 1):
        if line.strip():
            for n, digest in _match_hash(list(tokenize(line)), hashes, n_max):
                found += [(lineno, n, digest)]
    return found


def above_the_scissors(text):
    """The part of a message file git keeps: every line above its scissors line.

    Line numbers are unchanged, since only the end of the text is cut.
    """
    kept = []
    for line in text.splitlines():
        if _SCISSORS.fullmatch(line):
            break
        kept += [line]
    return "\n".join(kept)


def _git(repo, arguments):
    """One git command in ``repo``: its exit status and its output bytes.

    Replacement objects are ignored, so what is read is what a push sends.
    """
    try:
        done = subprocess.run(
            ["git", "-C", str(repo), "--no-replace-objects", *arguments],
            capture_output=True, check=False,
        )
    except OSError as err:
        raise ScanRefused(
            f"git could not be run ({type(err).__name__}); install git or put "
            "it on PATH, then run the scan again."
        ) from err
    return done.returncode, done.stdout


def require_full_history(repo):
    """Raise ScanRefused unless ``repo`` is a git repository with its whole history."""
    status, out = _git(repo, ["rev-parse", "--is-shallow-repository"])
    if status != 0:
        raise ScanRefused(
            f"git cannot read a repository here (git rev-parse exit {status}); "
            "run the scan inside the repository or name it with --repo."
        )
    if out.strip() == b"true":
        raise ScanRefused(
            "this repository is a SHALLOW clone: its history stops short "
            "without saying where, so no scan of it can know it saw every "
            "commit. Fetch the whole history (git fetch --unshallow; in CI, "
            "fetch-depth: 0 on the checkout) and run the scan again."
        )


def holds_commit(repo, name):
    """Whether ``repo`` holds a commit named ``name``."""
    return _git(repo, ["cat-file", "-e", name + "^{commit}"])[0] == 0


def require_grandfather(repo):
    """Raise ScanRefused unless ``repo`` holds the grandfather commit."""
    if not holds_commit(repo, GRANDFATHER):
        raise ScanRefused(
            f"the grandfather commit {GRANDFATHER} is not in this repository, "
            "so the line between the messages published before this guard "
            "and the ones it holds cannot be drawn. Fetch the whole history "
            "(git fetch --unshallow; in CI, fetch-depth: 0 on the checkout) "
            "and run the scan again. If the published history no longer "
            "holds that commit, which commit ends it is the owner's decision "
            "(plan P4-D362), never a way to make a scan pass."
        )


def commit_messages(repo, revisions):
    """(commit, message bytes) for every commit the revisions reach, newest first.

    ``revisions`` are `git log` revision arguments: names, ``^name``
    exclusions and ``a..b`` ranges. Merge commits are included; each
    message is the whole of it, subject and body.
    """
    status, out = _git(repo, _LOG + list(revisions) + ["--"])
    if status != 0:
        raise ScanRefused(
            f"git could not list the commits asked for (git log exit {status}); "
            "check that each revision names a commit of this repository."
        )
    listed = []
    for record in out.split(b"\0"):
        if record:
            name, _, message = record.partition(b"\n")
            listed += [(name.decode("ascii"), message)]
    return listed


def pushed_revisions(lines, holds):
    """The revisions naming the commits a push sends, from the pre-push input.

    git writes one line per ref: local ref, local object, remote ref,
    remote object. A deleted ref (a local object of zeros) sends nothing.
    Any other sends what its local object reaches and its remote object
    does not -- where ``holds(remote object)`` says this repository has
    it; one it never fetched cannot be left out, so the scan then reads
    more, never less. A line of another shape raises ScanRefused.
    """
    revisions = []
    for line in lines:
        fields = line.split()
        if not fields:
            continue
        if len(fields) != 4 or not all(
            _OBJECT.fullmatch(fields[at]) for at in (1, 3)
        ):
            raise ScanRefused(
                "a line of the pre-push input is not the four fields git "
                "writes; run this mode only from the pre-push hook that "
                "tools/hooks/install.sh installs."
            )
        local, remote = fields[1], fields[3]
        if set(local) == {"0"}:
            continue
        revisions += [local]
        if set(remote) != {"0"} and holds(remote):
            revisions += ["^" + remote]
    return revisions


def _plural(count, word):
    return f"{count} {word}" + ("" if count == 1 else "es" if word.endswith("h") else "s")


def _scan_file(path, hashes, n_max, magic):
    """Mode (a): one message file. Returns the exit code."""
    try:
        raw = path.read_bytes()
    except OSError as err:
        print(
            f"commit message: NOT SCANNED - the message file could not be read "
            f"({type(err).__name__}); name the file git hands the commit-msg hook."
        )
        return 2
    kind, text = decode_bytes(raw, magic)
    if kind != "text" or text is None:
        print(
            f"VIOLATION message: {kind} - this commit message is not scannable "
            "text; write it as plain text."
        )
        return 2
    found = message_matches(above_the_scissors(text), hashes, n_max)
    for lineno, n, digest in found:
        print(
            f"MATCH message line:{lineno} n={n} {digest[:12]} - this commit "
            "message matches the denied-vocabulary manifest; rewrite the "
            "message (never edit the manifest)."
        )
    print("commit message: " + (_plural(len(found), "match") if found else "clean"))
    return 1 if found else 0


def _scan_commits(listed, hashes, n_max, magic, heading):
    """Modes (b) and (c): every listed commit's message. Returns the exit code."""
    matches = violations = 0
    touched = 0
    for commit, raw in listed:
        kind, text = decode_bytes(raw, magic)
        if kind != "text" or text is None:
            print(
                f"VIOLATION commit {commit}: {kind} - this commit message is not "
                f"scannable text; {_REWORD}."
            )
            violations += 1
            continue
        found = message_matches(text, hashes, n_max)
        for lineno, n, digest in found:
            print(
                f"MATCH commit {commit} line:{lineno} n={n} {digest[:12]} - this "
                f"commit message matches the denied-vocabulary manifest; {_REWORD}, "
                "and never edit the manifest."
            )
        matches += len(found)
        touched += 1 if found else 0
    scanned = _plural(len(listed), "commit") + " scanned"
    if matches or violations:
        told = [_plural(matches, "match") + f" in {touched} of {scanned}"]
        if violations:
            told += [_plural(violations, "violation")]
        print(f"{heading}: " + ", ".join(told))
    else:
        print(f"{heading}: clean, {scanned}")
    return (1 if matches else 0) | (2 if violations else 0)


def main(argv=None):
    """Run one mode; the exit code of check.py's scheme.

    With ``argv`` None the command line is read; a list is read instead,
    so a caller in the same process passes its own arguments.
    """
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "revisions", nargs="*", metavar="REVISION",
        help="modes (b) and (c): the git revisions to read, for example HEAD ^BASE",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--message-file", metavar="FILE",
        help="mode (a): scan this one message file",
    )
    mode.add_argument(
        "--range", action="store_true",
        help="mode (b): scan every commit the revisions reach, drawing no line",
    )
    mode.add_argument(
        "--pre-push", action="store_true",
        help="mode (c) over the refs git names on standard input to a pre-push hook",
    )
    parser.add_argument(
        "--manifest", default=str(MANIFEST),
        help="hashed manifest (default: the committed one)",
    )
    parser.add_argument(
        "--repo", default=".", help="the repository (default: the current directory)"
    )
    args = parser.parse_args(argv)

    if (args.message_file is not None or args.pre_push) and args.revisions:
        parser.error("--message-file and --pre-push take no revisions")
    if args.range and not args.revisions:
        parser.error("--range needs a revision, such as origin/main..HEAD")
    if any(revision.startswith("-") for revision in args.revisions):
        parser.error("a revision may not begin with '-'; name commits, not options")

    try:
        headers, body_lines = load_manifest(Path(args.manifest))
    except ManifestFormatError as err:
        print(f"manifest format error: {err}")
        return 2
    except OSError as err:
        print(
            f"commit messages: NOT SCANNED - the manifest could not be read "
            f"({type(err).__name__}); restore tools/decontamination/manifest.txt "
            "from version control."
        )
        return 2
    hashes = set(body_lines)
    n_max = int(headers["n_max"])
    magic = load_magic(MAGIC)

    if args.message_file is not None:
        return _scan_file(Path(args.message_file), hashes, n_max, magic)

    repo = Path(args.repo)
    try:
        require_full_history(repo)
        if args.range:
            revisions = list(args.revisions)
            heading = "commit messages"
        else:
            require_grandfather(repo)
            if args.pre_push:
                revisions = pushed_revisions(
                    sys.stdin.read().splitlines(),
                    lambda name: holds_commit(repo, name),
                )
                if not revisions:
                    print("commit messages: this push sends no commit")
                    return 0
            else:
                revisions = list(args.revisions) or ["HEAD"]
            # First, so no revision after it can turn the exclusion around.
            revisions = ["^" + GRANDFATHER] + revisions
            heading = f"commit messages past the grandfather line {GRANDFATHER[:12]}"
        listed = commit_messages(repo, revisions)
    except ScanRefused as err:
        print(f"commit messages: NOT SCANNED - {err}")
        return 2
    return _scan_commits(listed, hashes, n_max, magic, heading)


if __name__ == "__main__":
    sys.exit(main())
