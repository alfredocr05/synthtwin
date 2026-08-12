"""Write the disposition seal: what the guard has already been shown.

Review item P2-C5-F1. The three governing documents -- the ratified plan
and both specifications -- and the registry's own judgment are sealed
passage by passage in `tests/disposition_seal.py`. The guard reads that
file and refuses any passage it does not hold, so a sentence nobody has
reviewed turns the suite red whatever the sentence says. That is the
protection the round-5 attacks went through: six of eight defeated a
guard that read prose for known wording, and none of the six changes a
document without moving a digest here.

USAGE, and read the next paragraph before running it:

    .venv/bin/python tools/dispositions/seal.py            # show
    .venv/bin/python tools/dispositions/seal.py --write    # re-seal

`--write` writes the seal again from the tree as it stands. Running it
asserts something: that every passage it newly seals states no less than
the ratified plan states, and that every registry entry it newly seals is
the plan's own ruling. If a passage you are sealing lowers a bar, the
answer is not to seal it -- it is to amend `docs/plans/phase-2-generator.md`
in the open, or to leave the obligation standing and name the deviation
in the report. The diff this writes is deliberately countable: one line
per passage, so a reviewer reads "three passages changed" off the diff
without opening a document.

No network, no subprocess, no dynamic import; it reads three text files
and writes one Python file.
"""

import argparse
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tests"))

import dispositions

TARGET = ROOT / "tests" / "disposition_seal.py"

HEADER = '''"""The disposition seal -- GENERATED, and signed by whoever writes it.

Written by `tools/dispositions/seal.py`. Do not edit by hand.

WHAT A LINE IN `SEALED` MEANS. One passage of one governing document was
present when somebody last re-sealed, and re-sealing asserts that the
passage states no less than the ratified plan states. The guard in
`tests/test_p2c4f1_disposition_registry.py` refuses any passage of those
three documents whose digest is not here -- so writing a new sentence,
or rewording an old one, turns the suite red BEFORE anybody argues about
what the sentence means. That is the whole point: round 5 defeated a
guard that argued about meaning, six attacks out of eight, and every one
of the six had to write or change a passage.

WHAT `JUDGMENT` MEANS. Four digests over the registry's own decisions:
the class each fact carries, the plan text each fact is bound by, every
authorized lesser outcome, and the two report lines that are notes
rather than misses. Round 5 walked through two of those surfaces by
editing `tests/dispositions.py` alone. An edit there now has to be
countersigned here, in a file whose only reason to change is that
somebody decided to change what a published fact owes.

WHITESPACE IS COLLAPSED before digesting, so re-wrapping a paragraph
moves nothing. Only a change of words moves a digest.

RE-SEALING IS THE VISIBLE ACT, not a formality. The diff is one line per
passage. If it is long, say why in the commit message; if it is short,
the reviewer can read exactly which sentences moved.
"""

# The passages of each governing document, by the digest
# `dispositions.digest` gives them, sorted.
SEALED: "dict[str, tuple[str, ...]]" = {
'''

MIDDLE = '''}

# The registry's own judgment, in the surfaces
# `dispositions.judgment` separates.
JUDGMENT: "dict[str, str]" = {
'''


def _render() -> str:
    """The whole seal file, as text, from the tree as it stands."""
    body = [HEADER]
    for relative in dispositions.GOVERNING:
        marks = sorted(
            {
                dispositions.digest(passage)
                for passage in dispositions.passages(
                    dispositions.REPO_ROOT / relative
                )
            }
        )
        body.append(f'    "{relative}": (\n')
        body.extend(f'        "{mark}",\n' for mark in marks)
        body.append("    ),\n")
    body.append(MIDDLE)
    for surface, mark in sorted(
        dispositions.judgment(dispositions.REGISTRY).items()
    ):
        body.append(f'    "{surface}": "{mark}",\n')
    body.append("}\n")
    return "".join(body)


def main(argv: "list[str] | None" = None) -> int:
    """Show or write the seal. Returns 0 when the seal is current."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--write",
        action="store_true",
        help="rewrite tests/disposition_seal.py from the tree as it stands",
    )
    options = parser.parse_args(argv)
    rendered = _render()
    current = TARGET.read_text(encoding="utf-8") if TARGET.exists() else ""
    if options.write:
        TARGET.write_text(rendered, encoding="utf-8")
        print(f"disposition seal written to {TARGET.relative_to(ROOT)}")
        return 0
    if rendered == current:
        print("disposition seal: current")
        return 0
    print(
        "disposition seal: OUT OF DATE. Some passage of a governing "
        "document, or some registry decision, is not the one that was "
        "sealed. Read the difference before running --write: sealing a "
        "passage asserts it states no less than the ratified plan does."
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
