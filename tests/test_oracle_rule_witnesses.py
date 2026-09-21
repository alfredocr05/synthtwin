"""The oracle's rules no frozen case reaches, witnessed one call at a time.

THE GAP, AS MEASURED (the skeptic of the oracle's independence repair of
2026-09-19, K-2B-42). The repair rewrote five oracle functions from the
method's statements -- `histogram_bin`, G6.5a's push refusals (`allowed`,
nested in `pushed_apart`), `anchor_units`, `absorbed_count` and
`alphabet_readings` -- and every committed vectors file rebuilt byte for
byte. The skeptic then made 23 mutants of those five functions and
rebuilt every file under each one: the shared edge moved to the lower
bin, a bin shifted up, and `return 0` all left the ten files unchanged,
and so did removing each push refusal alone, each of the three readings
of an anchor alone, the even split of an absorbed count, the census line
counted as below, and the filter keeping the figures at or under the code
alphabet. A rule whose every mutant leaves every committed byte where it
was is not witnessed by the frozen cases, however carefully it was
written.

**Why no frozen case was added.** The repair's brief keeps every vectors
file byte-identical, and plan P4-D295 routes the next case into an
existing file, so a new case moves committed bytes. More to the point,
two of these rules CANNOT be reached by a frozen case as the oracle
stands, and that was measured rather than assumed:

- `histogram_bin` has one caller in the oracle, G6.1's mode pass
  (`mode_held`), and there only past its other conditions, on a column
  publishing an empty bin, to ask whether the mode's bin is one of them.
  Rebuilding all ten files with the oracle instrumented, the pass reaches
  that clause once (`mode_held`, whose column publishes no empty bin)
  and `histogram_bin` is called NO times. One case (`saturated_band`)
  publishes twenty-five empty bins, and it publishes no mode. A
  description a producer writes can never put its mode in a bin it calls
  empty: the mode is one of the values the statistics used, and C6-122
  names as empty only the bins holding none of them. The loader does
  accept one that does (measured: a mode of 25.0 in bin 15, bin 15 named
  empty with its edges, loaded), so the clause is reachable only on a
  description that contradicts itself. The division is witnessed here,
  clause by clause; the empty-bin PASS (G6.7) stays unmirrored and is
  counted by ledger K-P4-23.
- Two of G6.5a's three push refusals can never decide a push the walk
  builds. On a column that writes some cells with no point, the walk
  visits only points of the mover's own kind, so a stratum it moves goes
  from a point of that kind to the next one, and the WHOLE refusal can
  fire only on a stratum whose value is not the number its text reads
  back as. The first and last strata stand on the published ends, which
  no walk passes, so the END refusal can fire only where they do not.
  `test_two_push_refusals_cannot_decide_a_push_the_walks_hand_on` holds
  both facts over seeded inputs of the shape the walks hand on, and
  holds the third refusal, POINT-FREE, to deciding some of them.

**A CLAUSE IS COVERED ONLY WHERE A CASE PARTS ITS TWO ROADS** (the
round-2 ledger pass, item 6). "Each clause, one call at a time" was too
strong a reading of this file until that pass: two clauses of
`anchor_units` had a case that TOUCHED them and no case that could tell
them from the fallback. Measured at 05e7d89, each mutant rebuilding all
nine generation reference files byte for byte and leaving every witness
here empty:

- with the leading-minus frame removed, `-0.05` still answers `(-5, 2)`
  -- it falls through to (c), whose shortest spelling writes the same
  two places -- while `anchor_units("-12.50", -12.5)` drops from
  `(-1250, 2)` to `(-125, 1)`;
- with the minus removed from (c)'s whitelist of characters a shortest
  spelling may hold, every positive case is unmoved while
  `anchor_units("-1.5e-3", -0.0015)` drops from `(-15, 4)` to `None`.

Both spellings and both mutants are in the tables below. A clause whose
mutant leaves EVERY case here answering as before is not witnessed,
however many cases reach it.

**THE SAME MEASUREMENT AGAIN, ON G7.9** (the skeptic of the independence
repair of 2026-09-21, K-2B-42). `marks_bought_for_the_shortfall` was
rewritten from a statement completed first, and its rule arrived here
with eight hand-worked rows and three mutants. Sixteen one-clause
mutants of it were then measured against all 103 oracle cases and those
eight rows: THIRTEEN were caught and FOUR were not, every one of the
four a real difference in the cells written --

- item 7's TIE stated the other way round (a census of
  `{"space": 6, "upper_t": 6}` wants `T` instead of ` `, and buys
  nothing instead of buying rank one a `t`) -- and nothing but the
  SHIPPED CODE had ever pinned that clause, which is the one source an
  oracle may not be written from;
- item 2's "wears the commonest NAMED mark" dropped (a census of
  `{"upper_t": 11}` over space-marked cells buys rank one);
- item 2's "its respelling is not a spelling the table declares absent"
  dropped (with the first day's respelling declared absent, rank one is
  bought instead of rank six -- the eight rows all passed no absent
  spelling at all, so the clause was asked of neither implementation);
- item 3's member skip dropped, which the slashed-stamp row could not
  part because contract D12 permits a slashed stamp the SPACE ALONE and
  its census therefore leaves no mark unnamed in any case.

Four rows and four mutants below close them, and the rows go to the
SHIPPED function too, so the gap covered the generator as much as the
oracle: had `_spellings_short_of_the_count` held any of the four wrong,
tests/test_generation_reference.py and this file would both have been
green. The mechanism was never in doubt -- dropping item 2's "worn by
another rank" turns `test_the_generator_says_how_many_numbers_it_proved`
red on two vectors files -- only its coverage.

**What this file holds.** Each rule's clauses, as a table of inputs and
the answers the method's statement gives, worked out by hand from the
statement (contract C6-31f with method G6.7.2; G6.5a; G8.3a step 3;
G9.5), asked of the oracle AND of the shipped function it is compared
with. The answers are not taken from either implementation. Every entry
of `WITNESS_MUTANTS` is a source edit of the oracle -- the skeptic's
mutants among them -- and each must turn its rule's witness red, so a
witness that stops witnessing is caught the same way a frozen case that
stops witnessing is (G14.3). The end refusal is witnessed on an input no
published column produces, a first stratum standing above the published
`min`, and that is the only way it can be.
"""

import collections
import pathlib
import random
import types
import typing

import pytest

from synthtwin import contract, generation, parsing

REPOSITORY = pathlib.Path(__file__).resolve().parent.parent
ORACLE = REPOSITORY / "tools" / "reference" / "make_generation_reference_vectors.py"
SOURCE = ORACLE.read_text(encoding="utf-8")


def _oracle(source: str = SOURCE) -> types.ModuleType:
    """The oracle, run from ``source`` as a module of its own."""
    module = types.ModuleType("oracle_under_witness")
    module.__dict__["__file__"] = str(ORACLE)
    exec(compile(source, str(ORACLE), "exec"), module.__dict__)
    return module


ORACLE_MODULE = _oracle()


def _asked(rule: typing.Callable[..., object], *arguments: object) -> object:
    """The rule's answer, or the name of what it raised."""
    try:
        return rule(*arguments)
    except Exception as stop:  # a raise is an answer here, and a wrong one
        return f"raised {type(stop).__name__}"


# --------------------------------------------------------------- the division
#
# Contract C6-31f: floor((v - min) / (max - min) * 32), clamped into 0..31,
# a shared edge in the UPPER bin, no division where the ends are equal or
# their difference cannot be held. Method G6.7.2: in binary64, the clamp
# before any arithmetic, and the result held to at most the last bin.

BINS = (
    # (value, min, max, bin)
    (0.0, 0.0, 32.0, 0),  # the published min is in the first bin
    (32.0, 0.0, 32.0, 31),  # the published max in the last, which is closed
    (1.0, 0.0, 32.0, 1),  # a shared edge belongs to the bin starting there
    (16.0, 0.0, 32.0, 16),
    (0.5, 0.0, 32.0, 0),
    (31.5, 0.0, 32.0, 31),
    (40.0, 0.0, 32.0, 31),  # above max: clamped to the last bin
    (-5.0, 0.0, 32.0, 0),  # below min: clamped to the first
    (5.0, 5.0, 5.0, 0),  # max equals min: no division, bin 0
    (0.0, -1e308, 1e308, 0),  # a width binary64 cannot hold: no scale
    # The clamp comes first: (1e308 + 1) / 2 * 32 overflows.
    (1e308, -1.0, 1.0, 31),
    # In binary64, 0.125 / 0.2 rounds to 0.625 and * 32 is exactly 20; exact
    # rationals over the two doubles give 19.99..., bin 19.
    (0.125, 0.0, 0.2, 20),
    # 2**-61 - (-1) and 2**-60 - (-1) both round to 1.0, so the product is
    # 32.0 on a value below max: held to the last bin.
    (2.0**-61, -1.0, 2.0**-60, 31),
)


def _bins_missed(rule: typing.Callable[..., object]) -> "list[str]":
    return [
        f"bin of {value!r} on {low!r}..{high!r}: {_asked(rule, value, low, high)!r},"
        f" the statement gives {want}"
        for value, low, high, want in BINS
        if _asked(rule, value, low, high) != want
    ]


# ------------------------------------------------------ G6.5a's push refusals
#
# Hand-built strata, all in the positive band. A column's grid texts are
# the oracle's and the generator's own writing of each value, so the only
# thing an entry fixes is the values, the ladder's ends and the flags.

PUSHES = (
    # (values, figures, ladder, point_free, keep_whole, integer_valued,
    #  pushed)
    #
    # POINT-FREE decides: the styles ask for point-free cells (a pooled
    # share, which G6.4 writes plain) while every cell has a point, so the
    # walk takes points of either kind. Both ways move 1.0, which has a
    # point-free spelling, to 0.9 or 1.1, which have none: refused, and the
    # collision is immovable.
    ((0.5, 1.0, 1.0, 2.0), 1, (0.5, 2.0), True, False, False,
     (0.5, 1.0, 1.0, 2.0)),
    # The same strata where nothing asks for a point-free cell: the
    # downward way moves one stratum, which is fewer or a tie, so it wins.
    ((0.5, 1.0, 1.0, 2.0), 1, (0.5, 2.0), False, False, False,
     (0.5, 0.9, 1.0, 2.0)),
    # A move keeping the point-free spelling absent is allowed.
    ((0.5, 1.5, 1.5, 3.0), 1, (0.5, 3.0), True, False, False,
     (0.5, 1.4, 1.5, 3.0)),
    # END decides: the downward walk from 3 passes 2, which the FIRST
    # stratum holds, to the free 1 -- refused, because the first stratum
    # may not move. Upward, 4 is held and 5 is past max. Immovable. (The
    # first stratum above the published min is the input no published
    # column produces.)
    ((2.0, 3.0, 3.0, 4.0), 0, (1.0, 4.0), False, False, True,
     (2.0, 3.0, 3.0, 4.0)),
    # With the first stratum on min, 2 is free and the mover takes it.
    ((1.0, 3.0, 3.0, 4.0), 0, (1.0, 4.0), False, False, True,
     (1.0, 2.0, 3.0, 4.0)),
)


def _oracle_push(module: types.ModuleType) -> typing.Callable[..., object]:
    def pushed(values, figures, ladder, point_free, keep_whole, integer_valued):
        texts = [module.grid_text(value, figures) for value in values]
        held = dict(collections.Counter(texts))
        return tuple(module.pushed_apart(
            len(values), figures, list(values), texts, held,
            ["positive"] * len(values), list(ladder), (), point_free,
            integer_valued, keep_whole,
        ))
    return pushed


def _generator_push(values, figures, ladder, point_free, keep_whole, integer_valued):
    texts = [generation._grid_text(value, figures) for value in values]
    held = dict(collections.Counter(texts))
    styles = {"decimal": len(values)}
    if point_free:
        styles = {"decimal": len(values) - 1, contract.WITHHELD: 1}
    facts = types.SimpleNamespace(
        n_distinct_values=len(values),
        empty_edges=(),
        integer_valued=integer_valued,
        numeric_styles=styles,
    )
    layout = types.SimpleNamespace(bands=[generation._BAND_POSITIVE] * len(values))
    return tuple(generation._pushed_apart(
        typing.cast(contract.NumericFacts, facts),
        typing.cast(typing.Any, layout),
        tuple(ladder), list(values), texts, held, figures, keep_whole,
    )[0])


def _pushes_missed(rule: typing.Callable[..., object]) -> "list[str]":
    missed = []
    for values, figures, ladder, point_free, keep_whole, whole, want in PUSHES:
        got = _asked(rule, values, figures, ladder, point_free, keep_whole, whole)
        if got != want:
            missed += [f"push of {values!r}: {got!r}, the statement gives {want!r}"]
    return missed


# ----------------------------------------------- G8.3a step 3's three readings

ANCHORS = (
    # (spelling, value, (units, places) or None)
    ("12.50", 12.5, (1250, 2)),  # (a) a plain decimal
    ("-0.05", -0.05, (-5, 2)),
    # THE NEGATIVE CLAUSES, WORKED OUT BY HAND (round-2 ledger item 6).
    # `-0.05` above does not witness the leading-minus frame: with the
    # frame gone the spelling falls through to (c), whose shortest
    # spelling is `-0.05` at two places, and the answer is the same
    # (-5, 2) by another road. `-12.50` is where the two roads part: (b)
    # reads the minus and the two written places and gives (-1250, 2),
    # while (c) reads repr(-12.5) == '-12.5' and gives (-125, 1). And
    # (c)'s own whitelist must hold the minus: `-1.5e-3` reaches no
    # rewriting, so it is read from its value, whose shortest spelling
    # `-0.0015` carries a sign character that a whitelist of digits and
    # a point alone would refuse, turning the anchor into None.
    ("-12.50", -12.5, (-1250, 2)),  # (b) the leading-minus frame, trailing noughts kept
    ("-1.5e-3", -0.0015, (-15, 4)),  # (c) the sign is part of the shortest spelling
    ("7", 7.0, (7, 0)),
    ("+1.50", 1.5, (150, 2)),  # (b) a leading plus dropped
    ("(12.50)", -12.5, (-1250, 2)),  # (b) brackets are negative
    ("12.50-", -12.5, (-1250, 2)),  # (b) a trailing minus is negative
    ("1,234.50", 1234.5, (123450, 2)),  # (b) GS1 marks taken out
    ("(1 234.5)", -1234.5, (-12345, 1)),
    ("+1'000", 1000.0, (1000, 0)),
    ("1e3", 1000.0, (1000, 0)),  # (c) whole, below 2**53: no places
    ("2.5E1", 25.0, (25, 0)),
    ("1.5e-3", 0.0015, (15, 4)),  # (c) the shortest spelling, positional
    ("9.007199254740992e15", 2.0**53, (90071992547409920, 1)),  # one nought
    # (c) printed with an exponent: READ THROUGH IT since item 3 of the
    # numbers pass of the second Codex round (2026-09-19). The part
    # before the mark is read plainly and the exponent moves the places
    # it was read at, downward where it is positive and upward where it
    # is negative; where that leaves fewer than no places the units carry
    # the difference. Before this both rows answered None, a column
    # published at 1.1e-7 had no anchor at all, and its made-up cells
    # came back near a thousandth.
    ("1e20", 1e20, (10 ** 20, 0)),
    ("1e-5", 1e-5, (1, 5)),
    ("1.1e-7", 1.1e-07, (11, 8)),
    ("-2.5e18", -2.5e18, (-2500000000000000000, 0)),
    ("x", None, None),
)


def _anchors_missed(rule: typing.Callable[..., object]) -> "list[str]":
    return [
        f"anchor of {text!r}: {_asked(rule, text, value)!r}, the statement gives {want!r}"
        for text, value, want in ANCHORS
        if _asked(rule, text, value) != want
    ]


# ---------------------------------------------- G9.5's absorbed alphabet count

ABSORBED = (
    # (count, population, floor, published). The line is max(2, floor).
    (5, 10, 11, 10),  # an even split, both sides below: goes INSIDE
    (4, 10, 11, 0),
    (6, 10, 11, 10),
    (1, 2, 0, 2),  # an even split at the line of two
    (11, 30, 11, 11),  # a side ON the line is not below it: printed as is
    (19, 30, 11, 19),
    (10, 30, 11, 0),
    (20, 30, 11, 30),
    (0, 30, 11, 0),  # one group only, not below: printed as is
    (30, 30, 11, 30),
    (1, 5, 0, 0),
    (2, 4, 1, 2),
    (3, 7, 11, 0),
    (4, 7, 11, 7),
    (0, 0, 11, 0),
)


def _absorbed_missed(rule: typing.Callable[..., object]) -> "list[str]":
    return [
        f"{count} of {population} at floor {floor}:"
        f" {_asked(rule, count, population, floor)!r}, the statement gives {want}"
        for count, population, floor, want in ABSORBED
        if _asked(rule, count, population, floor) != want
    ]


# ------------------------------------------------ G9.5's order of the readings
#
# Twelve present cells publishing nought figures and nought code-alphabet
# cells, at the floor of eleven: a count c meets nought where c is nought
# or c holds less than half and a side is below eleven -- 0 to 5. The pairs
# with the figures never more than the code alphabet, in ascending summed
# difference, then figures, then code, the published pair first.
READINGS = (
    ((0, 0, 12), (
        (0, 0), (0, 1), (0, 2), (1, 1), (0, 3), (1, 2), (0, 4), (1, 3),
        (2, 2), (0, 5), (1, 4), (2, 3), (1, 5), (2, 4), (3, 3), (2, 5),
        (3, 4), (3, 5), (4, 4), (4, 5), (5, 5),
    )),
    # Twelve and twenty of forty: both sides of each reach the line, so
    # each count is met by itself alone.
    ((12, 20, 40), ((12, 20),)),
)


def _oracle_readings(module: types.ModuleType) -> typing.Callable[..., object]:
    def readings(figures, code, present):
        column = {
            "n_all_digits": figures, "n_code_alphabet": code, "n_present": present,
        }
        return tuple(tuple(pair) for pair in module.alphabet_readings(column))
    return readings


def _generator_readings(figures, code, present):
    others = generation._alphabet_readings(figures, code, present, 11)
    return ((figures, code),) + tuple((entry[0], entry[1]) for entry in others)


def _readings_missed(rule: typing.Callable[..., object]) -> "list[str]":
    return [
        f"readings of {published!r}: {_asked(rule, *published)!r}, the statement"
        f" gives {want!r}"
        for published, want in READINGS
        if _asked(rule, *published) != want
    ]


# ------------------------------- G7.9's shortfall, and the stand-ins it counts
#
# Eleven moments at midnight on two days, every one written with a space,
# at a census of `{"space": 11}` that leaves `upper_t` and `lower_t`
# unnamed. The rule spends `n_distinct_folded` less the folded spellings
# the cells hold LESS the `n_unparsed` stand-ins still to be written, and
# at most `census_floor(floor) - 1` ranks, on the spare marks in the order
# upper_t, space, lower_t, never on the first rank or the last, and never
# twice on one folded spelling. No frozen case parts the stand-in road
# from the fallback: the one case that reaches this rule publishes
# `n_unparsed` of nought, and adding a second would move committed bytes
# (plan P4-D295). So the term is witnessed here, one call at a time.

SHORTFALL_CELLS = ["2025-01-01 00:00:00"] * 6 + ["2025-01-02 00:00:00"] * 5
SHORTFALL = (
    # (n_distinct_folded, n_unparsed, floor, census, member, holes, moved)
    # A shortfall of one, and one rank spent: the owner's own shape. It
    # is rank ONE and not rank nought, because the first rank is an end
    # the description publishes.
    (3, 0, 11, {"space": 11}, "iso-datetime", (), ((1, "T"),)),
    # THE SAME COLUMN WITH ONE STAND-IN. The stand-in is a folded
    # spelling of its own, so the cells in hand are one short of nothing
    # and the rule spends nothing.
    (3, 1, 11, {"space": 11}, "iso-datetime", (), ()),
    # A published four against two folded spellings and one stand-in:
    # a shortfall of one again, and one rank.
    (4, 1, 11, {"space": 11}, "iso-datetime", (), ((1, "T"),)),
    (4, 2, 11, {"space": 11}, "iso-datetime", (), ()),
    # THE BUDGET BINDING instead of the shortfall: a floor of three
    # gives two ranks, one per day, and the shortfall of ten is not
    # reached. A second rank of the first day would repeat a folded
    # spelling, and the last rank of the second is an end.
    (12, 0, 3, {"space": 11}, "iso-datetime", (), ((1, "T"), (6, "T"))),
    # A floor of one still publishes a census line of two, so one rank.
    (12, 0, 1, {"space": 11}, "iso-datetime", (), ((1, "T"),)),
    # A slashed stamp. Item 3 skips it BY MEMBER, and D12 permits it the
    # space alone, so the census leaves it no mark unnamed either way --
    # which is why this row parts no road on its own and the one below
    # it was added. (Until 2026-09-21 the comment here said 'character
    # eleven is a digit'; the frozen slashed_pool cell
    # '2024/06/20 13:37' holds the MARK at index ten.)
    (3, 0, 11, {"space": 11}, "month-first-datetime", (), ()),
    # A census holding a withheld pool: already split over every
    # permitted mark, so it leaves none unnamed.
    (3, 0, 11, {"(withheld)": 11}, "iso-datetime", (), ()),
    # ---- THE FOUR ROWS OF THE ROUND-3 SKEPTIC (2026-09-21) ----
    # Each of the four moved cells under a one-clause mutant while
    # moving no committed byte and none of the eight rows above.
    #
    # ITEM 3'S MEMBER SKIP, PARTED. A DATE member is not a slashed
    # stamp, so D12 permits it all three marks and the row above cannot
    # tell the skip from the fallback; these cells are eleven characters
    # and longer, so only the member itself refuses the spend. Both
    # implementations answer nothing; a member test that admitted
    # anything but the two ISO datetime members would buy rank one.
    (3, 0, 11, {"space": 11}, "iso-date", (), ()),
    # ITEM 7'S TIE. Two names of one count: the commonest is the FIRST
    # IN SORTED ORDER, so 'space' and not 'upper_t', the cells wear the
    # mark wanted, and the one spare mark 'lower_t' is bought. Stated
    # the other way round the column is left exactly as it was -- and
    # before this row nothing but the shipped code had ever pinned it.
    (3, 0, 11, {"space": 6, "upper_t": 6}, "iso-datetime", (), ((1, "t"),)),
    # ITEM 2'S COMMONEST **NAMED** MARK. The census names `upper_t`
    # alone while every cell wears a space, so no rank wears the
    # commonest named mark and nothing is bought, though the shortfall
    # is one and two marks are spare. Without that clause rank one is
    # respelled with the lower `t`.
    (3, 0, 11, {"upper_t": 11}, "iso-datetime", (), ()),
    # ITEM 2'S DECLARED-ABSENT SPELLING. The table declares the first
    # day's respelling absent, so the six ranks of that day are passed
    # over and the FIRST rank of the second day is bought instead.
    # Without that clause rank one is bought and the twin writes a
    # spelling its own description says the table does not hold.
    (3, 0, 11, {"space": 11}, "iso-datetime", ("2025-01-01T00:00:00",), ((6, "T"),)),
)


def _moved_ranks(cells: "list[str]") -> "tuple[tuple[int, str], ...]":
    """Which ranks came back wearing a mark they did not go in with."""
    return tuple(
        (rank, cells[rank][10])
        for rank in range(len(cells))
        if cells[rank] != SHORTFALL_CELLS[rank]
    )


def _oracle_shortfall(module: types.ModuleType) -> typing.Callable[..., object]:
    def spent(folded, unparsed, floor, census, member, holes):
        column = {
            "n_distinct_folded": folded,
            "n_unparsed": unparsed,
            "format": member,
            "datetime_separators": dict(census),
        }
        return _moved_ranks(
            module.marks_bought_for_the_shortfall(
                column, list(SHORTFALL_CELLS), holes, floor
            )
        )
    return spent


def _generator_shortfall(folded, unparsed, floor, census, member, holes):
    column = types.SimpleNamespace(n_distinct_folded=folded)
    facts = types.SimpleNamespace(
        parser_family=member,
        datetime_separators=dict(census),
        n_unparsed=unparsed,
    )
    return _moved_ranks(
        generation._spellings_short_of_the_count(
            column, facts, list(SHORTFALL_CELLS), holes, floor
        )
    )


def _shortfall_missed(rule: typing.Callable[..., object]) -> "list[str]":
    return [
        f"{folded} folded, {unparsed} unparsed, floor {floor}, {census} on"
        f" {member}, absent {holes}:"
        f" {_asked(rule, folded, unparsed, floor, census, member, holes)!r},"
        f" the statement gives {want!r}"
        for folded, unparsed, floor, census, member, holes, want in SHORTFALL
        if _asked(rule, folded, unparsed, floor, census, member, holes) != want
    ]


# ------------------------------------------------------------ the two readers

WITNESSES = {
    "shortfall": (
        lambda module: _shortfall_missed(_oracle_shortfall(module)),
        lambda: _shortfall_missed(_generator_shortfall),
    ),
    "division": (
        lambda module: _bins_missed(module.histogram_bin),
        lambda: _bins_missed(parsing.histogram_bin),
    ),
    "push": (
        lambda module: _pushes_missed(_oracle_push(module)),
        lambda: _pushes_missed(_generator_push),
    ),
    "anchor": (
        lambda module: _anchors_missed(module.anchor_units),
        lambda: _anchors_missed(generation._anchor_units),
    ),
    "absorbed": (
        lambda module: _absorbed_missed(module.absorbed_count),
        lambda: _absorbed_missed(parsing.absorbed_total),
    ),
    "readings": (
        lambda module: _readings_missed(_oracle_readings(module)),
        lambda: _readings_missed(_generator_readings),
    ),
}


# Each: (the witness it must turn red, the oracle's text, the text put in
# its place). The text must stand in the oracle exactly once.
WITNESS_MUTANTS = {
    "division_shared_edge_to_the_lower_bin": (
        "division",
        "step = math.floor((value - lowest) / width * HISTOGRAM_BINS)",
        "step = max(math.ceil((value - lowest) / width * HISTOGRAM_BINS) - 1, 0)",
    ),
    "division_one_bin_up": (
        "division", "    return min(step, last)\n", "    return min(step + 1, last)\n",
    ),
    "division_no_cap_at_the_last_bin": (
        "division", "    return min(step, last)\n", "    return step\n",
    ),
    "division_top_clamped_to_the_first_bin": (
        "division",
        "    if value >= highest:\n        return last\n",
        "    if value >= highest:\n        return 0\n",
    ),
    "division_clamp_after_the_arithmetic": (
        "division",
        "    if value >= highest:\n        return last\n"
        "    if value <= lowest:\n        return 0\n    step",
        "    step",
    ),
    "division_in_exact_rationals": (
        "division",
        "step = math.floor((value - lowest) / width * HISTOGRAM_BINS)",
        "step = math.floor((F(value) - F(lowest)) / (F(highest) - F(lowest))"
        " * HISTOGRAM_BINS)",
    ),
    "division_always_the_first_bin": (
        "division",
        "    width = highest - lowest\n    last = HISTOGRAM_BINS - 1\n",
        "    return 0\n",
    ),
    "push_point_free_refusal_removed": (
        "push",
        "        if point_free:\n            checks += [",
        "        if False:\n            checks += [",
    ),
    "push_end_refusal_removed": (
        "push",
        "        checks += [place not in (0, total - 1)]",
        "        checks += [True]",
    ),
    "push_every_move_allowed": (
        "push", "        return all(checks)\n", "        return True\n",
    ),
    "push_every_move_refused": (
        "push", "        return all(checks)\n", "        return False\n",
    ),
    "anchor_no_leading_plus": (
        "anchor", 'frames = (("+", "", False), ', "frames = (",
    ),
    "anchor_no_leading_minus": (
        "anchor", '("-", "", True), ', "",
    ),
    "anchor_value_read_without_its_minus": (
        "anchor",
        'set(shortest) <= set("-.0123456789")',
        'set(shortest) <= set(".0123456789")',
    ),
    "anchor_brackets_read_as_positive": (
        "anchor",
        "return int(-size if bracketed or minus else size), len(after)",
        "return int(-size if minus else size), len(after)",
    ),
    "anchor_no_trailing_minus": (
        "anchor", '("", "-", True), ', "",
    ),
    "anchor_marks_kept": (
        "anchor",
        "digits = core.translate({ord(mark): None for mark in GROUP_MARKS})",
        "digits = core",
    ),
    "anchor_no_reading_of_the_value": (
        "anchor",
        "    # (c): the value, where no rewriting reaches the spelling.\n",
        "    return None\n",
    ),
    "anchor_whole_value_at_one_place": (
        "anchor",
        "        return int(value), 0\n    shortest",
        "        return int(value) * 10, 1\n    shortest",
    ),
    "anchor_exponent_spelling_unread": (
        "anchor",
        '    head, mark, tail = shortest.partition("e")\n',
        '    return None\n    head, mark, tail = shortest.partition("e")\n',
    ),
    "absorbed_even_split_outside": (
        "absorbed",
        "return population if count >= half else 0",
        "return population if count > half else 0",
    ),
    "absorbed_side_on_the_line_below": (
        "absorbed",
        "below = [side for side in groups if side < line]",
        "below = [side for side in groups if side <= line]",
    ),
    "absorbed_into_the_smaller": (
        "absorbed",
        "return population if count >= half else 0",
        "return 0 if count >= half else population",
    ),
    "absorbed_never": (
        "absorbed", "    if not below:\n        return count\n", "    return count\n",
    ),
    "readings_figures_above_the_code_alphabet": (
        "readings", "        if figures <= code\n", "        if True\n",
    ),
    "readings_published_last": (
        "readings",
        "return [published] + sorted(candidates, key=moved_then_counts)",
        "return sorted(candidates, key=moved_then_counts) + [published]",
    ),
    "shortfall_stand_ins_uncounted": (
        "shortfall",
        'shortfall = column["n_distinct_folded"] - len(wearers)'
        ' - column["n_unparsed"]',
        'shortfall = column["n_distinct_folded"] - len(wearers)',
    ),
    "shortfall_budget_at_the_census_line": (
        "shortfall", "    budget = census_line(floor) - 1\n",
        "    budget = census_line(floor)\n",
    ),
    "shortfall_both_ends_open": (
        "shortfall",
        "        for rank in range(1, len(written) - 1)\n",
        "        for rank in range(len(written))\n",
    ),
    # The four the round-3 skeptic found witnessed by nothing. Each was
    # measured to move cells and to leave every committed vectors file
    # and all eight rows above it unmoved.
    "shortfall_tie_the_other_way": (
        "shortfall",
        "wanted = MARK_OF[max(sorted(census), key=census.get)]",
        "wanted = MARK_OF[max(reversed(sorted(census)), key=census.get)]",
    ),
    "shortfall_any_mark_not_only_the_commonest_named": (
        "shortfall", "            or cell[10] != wanted\n", "",
    ),
    "shortfall_absent_spellings_bought": (
        "shortfall", "            or changed.strip().lower() in absent\n", "",
    ),
    "shortfall_every_member_bought": (
        "shortfall",
        '        column["format"] in ("iso-datetime", "iso-mixed")\n',
        "        True\n",
    ),
    "readings_by_code_first": (
        "readings",
        "return [published] + sorted(candidates, key=moved_then_counts)",
        "return [published] + sorted(candidates, key=lambda pair: (pair[1], pair[0]))",
    ),
}


@pytest.mark.parametrize("rule", sorted(WITNESSES))
def test_the_oracle_gives_the_statement_s_answers(rule: str) -> None:
    """Every hand-worked answer, asked of the oracle as committed."""
    assert WITNESSES[rule][0](ORACLE_MODULE) == []


@pytest.mark.parametrize("rule", sorted(WITNESSES))
def test_the_shipped_rule_gives_the_statement_s_answers(rule: str) -> None:
    """The same answers, asked of the function the oracle is compared with."""
    assert WITNESSES[rule][1]() == []


def test_every_rule_has_a_mutant_and_every_mutant_a_rule() -> None:
    """No witness stands without a mutant, and no mutant names no witness."""
    named = {entry[0] for entry in WITNESS_MUTANTS.values()}
    assert named == set(WITNESSES)


@pytest.mark.parametrize("name", sorted(WITNESS_MUTANTS))
def test_each_witness_fails_when_its_rule_is_broken(name: str) -> None:
    """Each mutant is one edit the oracle's text holds once, and turns red."""
    rule, before, after = WITNESS_MUTANTS[name]
    assert SOURCE.count(before) == 1, name
    mutated = _oracle(SOURCE.replace(before, after))
    assert WITNESSES[rule][0](mutated) != [], name


# The two refusals no push the walks build can reach, and the one that can.
REFUSALS = {
    "whole": (
        "        if keep_whole:\n            checks +=",
        "        if False:\n            checks +=",
    ),
    "end": (
        "        checks += [place not in (0, total - 1)]",
        "        checks += [True]",
    ),
    "point_free": (
        "        if point_free:\n            checks += [",
        "        if False:\n            checks += [",
    ),
}


def _walked_strata(draw: random.Random, module: types.ModuleType):
    """Strata of the shape the walks hand the push, or None.

    In order; the first and last on the published ends; every value the
    number its grid text reads back as; fewer texts than strata.
    """
    figures = draw.choice((0, 1, 2))
    span = draw.randint(3, 25)
    start = draw.choice((draw.randint(-span, 0), draw.randint(1, 5)))
    points = [round((start + step) * 10.0**-figures, figures) for step in range(span + 1)]
    total = draw.randint(3, min(12, len(points) + 2))
    inside = sorted(draw.choice(points) for _each in range(total - 2))
    values = [
        float(module.grid_text(value, figures))
        for value in [points[0]] + inside + [points[-1]]
    ]
    texts = [module.grid_text(value, figures) for value in values]
    if len(set(texts)) >= total:
        return None
    bands = [
        "zero" if value == 0 else "negative" if value < 0 else "positive"
        for value in values
    ]
    keep_whole = draw.random() < 0.5
    point_free = draw.random() < 0.5
    integer_valued = figures == 0 and draw.random() < 0.5
    return (figures, values, texts, bands, keep_whole, point_free, integer_valued)


def _push_once(module: types.ModuleType, strata) -> "tuple[float, ...]":
    figures, values, texts, bands, keep_whole, point_free, integer_valued = strata
    return tuple(module.pushed_apart(
        len(values), figures, list(values), list(texts),
        dict(collections.Counter(texts)), list(bands), [values[0], values[-1]],
        (), point_free, integer_valued, keep_whole,
    ))


def test_two_push_refusals_cannot_decide_a_push_the_walks_hand_on() -> None:
    """Removing the whole or the end refusal moves nothing; point-free does.

    Method G6.5a says which of its three refusals can decide a push: over
    strata of the shape the walks hand on, only the point-free one, and
    only on a column asking for point-free cells while writing none of
    its cells without a point. Measured at the repair over 40,000 draws
    (28,723 inputs of this shape): 482 moved without it, every one of that
    shape, and none moved without either of the other two.
    """
    without = {
        name: _oracle(SOURCE.replace(before, after))
        for name, (before, after) in REFUSALS.items()
    }
    draw = random.Random(20260919)
    moved: "collections.Counter[str]" = collections.Counter()
    shapes: "collections.Counter[tuple[bool, bool]]" = collections.Counter()
    for _each in range(3000):
        strata = _walked_strata(draw, ORACLE_MODULE)
        if strata is None:
            continue
        want = _push_once(ORACLE_MODULE, strata)
        for name, module in without.items():
            if _push_once(module, strata) != want:
                moved[name] += 1
                if name == "point_free":
                    shapes[(strata[4], strata[5])] += 1
    assert moved["whole"] == 0
    assert moved["end"] == 0
    assert moved["point_free"] > 0
    assert set(shapes) == {(False, True)}
