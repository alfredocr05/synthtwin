"""A-P4-52: the proposal gate's turn, measured arm against arm.

Review round 3 of landing L7 gave the pairing walk two changes that
pull opposite ways: the acceptance rule's per-pair refusals, which on
their own leave MORE above-counts missed, and method G6B.4a's
above-count proposal, which is what was to make up for them. The
proposal was gated on the walk's own try counter -- and the walk takes
its positions in turn from that same counter, so on every column whose
mover count is EVEN the two clocks locked, one parity of positions was
aimed at on every turn it got and the other on none.

This driver re-derives that, two ways.

**ARITHMETIC**, needing no column at all: for each mover count it
prints how many of a position's own turns each gate opens on. The
round-3 gate answers 0 or every one of them wherever the mover count
is even; the shipped gate answers half, for every position, at every
mover count.

**MEASURED**, through the real reader, producer, loader and generator:
forty described columns of two to five positions, and eight more at
the five-position shape where the starved parity lives, at forty
generation seeds each, counting the pairs whose above-count the twin
missed and the pairs whose agreement lands outside method G12.9's
window. Every arm is one exact edit to a COPY of the shipped
generation module in a temporary folder. This driver never writes
inside the repository and never runs a program.

The parent arm -- the tree before review round 3, which had neither
the refusals nor the proposal -- is not one of the variants below,
because it is a different commit rather than a different gate. Put
`git show df12e69:src/synthtwin/generation.py` in place of the shipped
file to re-derive it.

Usage:

    .venv/bin/python tools/measurements/a_p4_52_l7_parity.py
    .venv/bin/python tools/measurements/a_p4_52_l7_parity.py --arms shipped,round-3

No network, no program started, no import of anything but the standard
library and the package under measurement.
"""
import argparse
import collections
import pathlib
import random
import shutil
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tests"))

# The gate on `_proposed`'s above-count branch, arm by arm. The key is
# the source line the shipped tree carries; the value replaces it.
SHIPPED_GATE = "            if not _aims_at_above(turn, place):\n"
ARMS = {
    # The shipped arm's replacement IS the gate line, so the
    # arm that measures the tree as it stands really is the tree as
    # it stands.
    "shipped": SHIPPED_GATE,
    # Review round 3 as it landed: the walk's own counter, read after
    # the walk has stepped it.
    "round-3": "            if tries % 2:\n",
    # The other parity starved instead, which is what shows that the
    # starving is the mechanism and not the direction.
    "flipped": "            if (turn + place + 1) % 2:\n",
    # Alternation without the stagger: every position aims on the same
    # turns of the turn rather than on opposite ones.
    "no-stagger": "            if turn % 2:\n",
    # ITS OTHER PHASE, so the stagger is compared against BOTH phases
    # of dropping it and not just one. Review round 4 of L7: three
    # phases of the stagger against one of the plain turn is not a
    # comparison, and the four arms differ by fewer pairs than the
    # phases differ among themselves.
    "no-stagger-flipped": "            if (turn + 1) % 2:\n",
    # The branch open on every turn, and shut on every turn.
    "always-aim": "            if False:\n",
    "never-aim": "            if True:\n",
}

SEEDS = 40
WINDOW = 0.02


def gate_opens(movers: int, place: int, turns: int, gate: str) -> int:
    """How many of one position's first `turns` turns a gate opens on.

    The walk reaches position `place` at tries `place - 1`,
    `place - 1 + movers`, ... and `tries` is stepped before the gate
    reads it, so the round-3 gate sees `turn * movers + place`.
    """
    opened = 0
    for turn in range(turns):
        tries = turn * movers + place
        if gate == "round-3":
            shut = tries % 2
        elif gate == "shipped":
            shut = (turn + place) % 2
        elif gate == "no-stagger":
            shut = turn % 2
        elif gate == "no-stagger-flipped":
            shut = (turn + 1) % 2
        else:
            shut = (turn + place + 1) % 2
        if not shut:
            opened = opened + 1
    return opened


def schedule() -> None:
    """The arithmetic, which needs no column and no seed."""
    print("\n===== how many of a position's first 40 turns aim at an "
          "above-count =====")
    print("  movers  position   round-3 gate   shipped gate")
    for movers in range(1, 7):
        for place in range(1, movers + 1):
            print(f"  {movers:6d}  {place:8d}   {gate_opens(movers, place, 40, 'round-3'):12d}"
                  f"   {gate_opens(movers, place, 40, 'shipped'):12d}")
    print("  A position starved at 0 of 40, or fed at all 40, is a "
          "position whose alternation is gone.")


def recipe() -> "list[tuple[str, int, list[str]]]":
    """FORTY described columns, randomised in every dimension that matters.

    The position count, the row count, the span of the numbers and how
    far position 1 sits from position 0 are all drawn, so no arm is
    read off one shape. Two to five positions: six is past the role's
    own ceiling and is declined as free text.
    """
    random.seed(4242)
    out = []
    for case in range(40):
        parts = random.choice((3, 3, 5, 5, 4, 2))
        rows = random.choice((80, 120, 150, 200))
        span = random.choice((4, 8, 15, 30, 60))
        noise = random.choice((1, 2, 4, 8))
        base = random.randint(10, 40)
        made = []
        for _row in range(rows):
            one = random.randint(base, base + span)
            held = [
                one,
                max(1, one + random.randint(-noise, noise)),
                random.randint(base, base + span),
                2 * base + span - one,
                max(1, one + random.randint(-2 * noise, 2 * noise)),
            ][:parts]
            made.append("/".join(str(each) for each in held))
        out.append((f"c{case:02d}p{parts}r{rows}", parts, made))
    return out


def tight() -> "list[tuple[str, int, list[str]]]":
    """EIGHT columns at the shape where the starved parity lives.

    Five positions, so four movers, so an EVEN mover count -- and the
    span and spread at which a search over sixty random shapes found
    the arms parting company. It is here as a family of its own so the
    recipe's rate is never read as a rate for this shape.
    """
    random.seed(20260903)
    out = []
    for case in range(8):
        made = []
        for _row in range(150):
            one = random.randint(20, 35)
            made.append("/".join(str(each) for each in (
                one,
                max(1, one + random.randint(-2, 2)),
                random.randint(20, 35),
                55 - one,
                max(1, one + random.randint(-4, 4)),
            )))
        out.append((f"tight{case}", 5, made))
    return out


def spread() -> "list[tuple[str, int, list[str]]]":
    """TWELVE columns built a DIFFERENT WAY from the recipe's.

    The recipe draws every part from one anchor value, so its pairs
    are correlated the same way in every one of its forty columns; a
    schedule read off it alone is read off one construction. Review
    round 4 of L7 asked for the choice to be made across families.

    Here the centres are chosen apart, ties are set at three rates,
    and -- on columns of more than two positions -- the last part runs
    in REVERSE of the first, so above-counts sit near the ends of
    their range rather than in the middle, which is where a schedule
    that starves a position shows up soonest.

    **THIS IS A COUPLED STRESS FAMILY AND NOT A SAMPLE.** Review round
    5 of L7 corrected an earlier wording here that called the parts
    independently drawn. They are not: the tie branch copies part 0
    outright, the last part is a deterministic function of part 0, the
    two-position column never reaches the reversing branch, and the
    drawn centres are not always unequal -- case 11's are
    [44, 58, 44], two of the three the same.
    What this family is good for is stressing a schedule against a
    construction unlike the recipe's. Its miss rate is ITS OWN and
    generalises to nothing without a family built to represent
    something.
    """
    random.seed(70707)
    out = []
    for case in range(12):
        parts = (3, 4, 5, 4, 5, 3, 4, 5, 2, 4, 5, 3)[case]
        rows = (90, 140, 160, 200)[case % 4]
        centres = [random.randint(10, 90) for _each in range(parts)]
        ties = (0.0, 0.15, 0.35)[case % 3]
        made = []
        for _row in range(rows):
            held: "list[int]" = []
            for which in range(parts):
                if held and random.random() < ties:
                    held.append(held[0])
                elif which == parts - 1 and parts > 2:
                    held.append(max(1, centres[0] + centres[which] - held[0]))
                else:
                    held.append(max(
                        1, centres[which] + random.randint(-12, 12)
                    ))
            made.append("/".join(str(each) for each in held))
        out.append((f"s{case:02d}p{parts}r{rows}", parts, made))
    return out


def arm_tree(home: "pathlib.Path", name: str) -> str:
    """A COPY of the shipped package with this arm's one line in it."""
    where = home / name
    where.mkdir(parents=True)
    shutil.copytree(
        ROOT / "src" / "synthtwin", where / "synthtwin",
        ignore=shutil.ignore_patterns("__pycache__"),
    )
    source = where / "synthtwin" / "generation.py"
    text = source.read_text(encoding="utf-8")
    if text.count(SHIPPED_GATE) != 1:
        raise SystemExit(
            "the shipped gate is not where this driver expects it; the "
            "arms below would all be the same tree"
        )
    source.write_text(text.replace(SHIPPED_GATE, ARMS[name]), encoding="utf-8")
    return str(where)


def imported(where: str):
    """The package under `where`, replacing whatever was imported before."""
    for name in [
        module for module in sys.modules
        if module == "synthtwin" or module.startswith("synthtwin.")
    ]:
        del sys.modules[name]
    sys.path.insert(0, where)
    import synthtwin
    if not synthtwin.__file__.startswith(where + "/"):
        raise SystemExit(
            f"this arm resolved to {synthtwin.__file__}, which is not the "
            "copy it was told to measure"
        )
    return synthtwin


def walk(shapes, seeds: int, modules) -> dict:
    contract, generation, profile, reading, taxonomy = modules
    import fixtures
    misses: "collections.Counter" = collections.Counter()
    parity: "collections.Counter" = collections.Counter()
    outside = 0
    pairs = 0
    built = 0
    refused = 0
    with tempfile.TemporaryDirectory() as folder:
        home = pathlib.Path(folder)
        for stem, parts, rows in shapes:
            fixtures.write(
                home, f"{stem}.csv", "reading\n" + "\n".join(rows) + "\n"
            )
            table = reading.read_table(
                str(home / f"{stem}.csv"),
                first_row=reading.FIRST_ROW_AUTOMATIC,
            )
            document = profile.build_document(
                table, taxonomy.Settings(), [], None, ["reading"]
            )
            loaded = contract.load_profile(str(fixtures.write_profile(
                home, f"{stem}-p.json", document
            )))
            column = loaded.columns[0]
            facts = column.facts
            if not isinstance(facts, contract.JoinedFacts):
                refused = refused + 1
                continue
            built = built + 1
            firsts, seconds = generation._pair_seats(facts.n_parts)
            for seed in range(seeds):
                twin = generation.generate(loaded, seed)
                cells = [one for one in twin.columns[0] if one != ""]
                held = [
                    [
                        float(one.split(facts.separator)[place])
                        for one in cells
                    ]
                    for place in range(facts.n_parts)
                ]
                for seat in range(len(facts.part_above)):
                    one, two = firsts[seat], seconds[seat]
                    pairs = pairs + 1
                    above = sum(
                        1 for row in range(len(cells))
                        if held[one][row] > held[two][row]
                    )
                    got = generation._rank_agreement(held[one], held[two])
                    if abs(round(got, 4) - facts.part_agreements[seat]) > (
                        WINDOW
                    ):
                        outside = outside + 1
                    if above != facts.part_above[seat]:
                        misses[stem] += 1
                        movers = [one, two] if one else [two]
                        if all(each % 2 for each in movers):
                            parity["only odd movers"] += 1
                        elif all(each % 2 == 0 for each in movers):
                            parity["only even movers"] += 1
                        else:
                            parity["one of each"] += 1
    return {
        "built": built,
        "refused": refused,
        "misses": sum(misses.values()),
        "by column": dict(sorted(misses.items())),
        "outside": outside,
        "pairs": pairs,
        "parity": dict(parity),
    }


def measure(names: "list[str]", seeds: int) -> None:
    with tempfile.TemporaryDirectory() as folder:
        home = pathlib.Path(folder)
        for name in names:
            where = arm_tree(home, name)
            imported(where)
            from synthtwin import (
                contract, generation, profile, reading, taxonomy,
            )
            modules = (contract, generation, profile, reading, taxonomy)
            print(f"\n===== arm {name}: {ARMS[name].strip()} =====")
            print(f"  measuring {generation.__file__}")
            for label, shapes in (
                ("the forty-column recipe", recipe()),
                ("the eight five-position columns", tight()),
                ("the twelve columns drawn apart", spread()),
            ):
                found = walk(shapes, seeds, modules)
                print(f"  {label}: built {found['built']}, refused "
                      f"{found['refused']}")
                print(f"    above-counts missed: {found['misses']} of "
                      f"{found['pairs']} pairs")
                print(f"    agreements outside the {WINDOW} window: "
                      f"{found['outside']} of {found['pairs']}")
                print(f"    where the misses landed: {found['parity']}")
                if found["by column"]:
                    print(f"    by column: {found['by column']}")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="a_p4_52_l7_parity",
        description="the proposal gate's turn, arm against arm",
    )
    parser.add_argument("--arms", default="shipped,round-3")
    parser.add_argument("--seeds", type=int, default=SEEDS)
    parser.add_argument("--schedule-only", action="store_true")
    known = parser.parse_args()
    schedule()
    if known.schedule_only:
        return
    names = [one.strip() for one in known.arms.split(",") if one.strip()]
    for name in names:
        if name not in ARMS:
            raise SystemExit(
                f"no arm named {name}; the arms are "
                + ", ".join(sorted(ARMS))
            )
    measure(names, known.seeds)


if __name__ == "__main__":
    main()
