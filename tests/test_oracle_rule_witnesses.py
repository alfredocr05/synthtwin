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
import datetime
import fractions
import math
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
        kept_stand_ins=(),
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

# TWELVE CELLS AND NOT ELEVEN since the dates pass of the stage-3
# review (item 6). Item 2's last clause stops the spend while the mark
# it is taken from would be left below `census_floor(floor)`, so a
# column of exactly eleven space-marked cells at a floor of eleven can
# buy nothing at all -- and every row below would have answered "()"
# for that one reason, parting none of the clauses each was written to
# part. One more cell puts the census one above the line, and the last
# row asks the new clause on its own.
SHORTFALL_CELLS = ["2025-01-01 00:00:00"] * 7 + ["2025-01-02 00:00:00"] * 5
SHORTFALL = (
    # (n_distinct_folded, n_unparsed, floor, census, member, holes, moved)
    # A shortfall of one, and one rank spent: the owner's own shape. It
    # is rank ONE and not rank nought, because the first rank is an end
    # the description publishes.
    (3, 0, 11, {"space": 12}, "iso-datetime", (), ((1, "T"),)),
    # THE SAME COLUMN WITH ONE STAND-IN. The stand-in is a folded
    # spelling of its own, so the cells in hand are one short of nothing
    # and the rule spends nothing.
    (3, 1, 11, {"space": 12}, "iso-datetime", (), ()),
    # A published four against two folded spellings and one stand-in:
    # a shortfall of one again, and one rank.
    (4, 1, 11, {"space": 12}, "iso-datetime", (), ((1, "T"),)),
    (4, 2, 11, {"space": 12}, "iso-datetime", (), ()),
    # THE BUDGET BINDING instead of the shortfall: a floor of three
    # gives two ranks, one per day, and the shortfall of ten is not
    # reached. A second rank of the first day would repeat a folded
    # spelling, and the last rank of the second is an end.
    (12, 0, 3, {"space": 12}, "iso-datetime", (), ((1, "T"), (7, "T"))),
    # A floor of one still publishes a census line of two, so one rank.
    (12, 0, 1, {"space": 12}, "iso-datetime", (), ((1, "T"),)),
    # A slashed stamp. Item 3 skips it BY MEMBER, and D12 permits it the
    # space alone, so the census leaves it no mark unnamed either way --
    # which is why this row parts no road on its own and the one below
    # it was added. (Until 2026-09-21 the comment here said 'character
    # eleven is a digit'; the frozen slashed_pool cell
    # '2024/06/20 13:37' holds the MARK at index ten.)
    (3, 0, 11, {"space": 12}, "month-first-datetime", (), ()),
    # A census holding a withheld pool: already split over every
    # permitted mark, so it leaves none unnamed.
    (3, 0, 11, {"(withheld)": 12}, "iso-datetime", (), ()),
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
    (3, 0, 11, {"space": 12}, "iso-date", (), ()),
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
    (3, 0, 11, {"upper_t": 12}, "iso-datetime", (), ()),
    # ITEM 2'S DECLARED-ABSENT SPELLING. The table declares the first
    # day's respelling absent, so the six ranks of that day are passed
    # over and the FIRST rank of the second day is bought instead.
    # Without that clause rank one is bought and the twin writes a
    # spelling its own description says the table does not hold.
    (3, 0, 11, {"space": 12}, "iso-datetime", ("2025-01-01T00:00:00",), ((7, "T"),)),
    # ITEM 2'S LAST CLAUSE (the dates pass of the stage-3 review,
    # item 6): at a floor of twelve the census stands ON the line,
    # so spending one of the twelve would leave eleven -- a count
    # no census may print -- and nothing is bought, though the
    # shortfall is one and two marks are spare. Without that clause
    # rank one is respelled and the twin's own description pools
    # the whole census.
    (3, 0, 12, {"space": 12}, "iso-datetime", (), ()),
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


# ------------------------------------------ G6.1's census that is only a pool
#
# Plan P4-D352, worked by hand from the method's sentence. With the line
# L = max(2, floor), G groupable cells and a pool P: T is G where G < P + L
# and P otherwise, never past the most seven marks let stand as a pool --
# 6(L - 1) where L is past seven, and at a line of three no odd count, a
# one being in every reading of it (plan P4-D356). The T cells picked go, one run of
# one value at a time, to the mark holding the fewest cells, the earlier on
# a tie, and none past L - 1; then while a mark holds none and another two
# or more, the one holding the most, the earlier on a tie, gives it the
# last cell it took. Each row: (pool, groupable, floor) and the answer
# (cells per mark in the method's order, groupable cells left with no
# mark). The groupable cells each hold their own value, so the marks take
# them in turn.
LONE_POOL_COUNTS = (
    ((60, 65, 11), ((9, 9, 9, 9, 8, 8, 8), 5)),  # six marks' worth: five bare
    ((50, 55, 11), ((8, 8, 8, 8, 8, 8, 7), 0)),  # a leftover of five joins
    ((50, 60, 11), ((9, 9, 9, 9, 8, 8, 8), 0)),  # ten join: one short of the line
    ((50, 61, 11), ((8, 7, 7, 7, 7, 7, 7), 11)),  # eleven are the column's bare cells
    ((60, 50, 11), ((8, 7, 7, 7, 7, 7, 7), 0)),  # short: every groupable cell
    ((4, 5, 3), ((1, 1, 1, 1, 0, 0, 0), 1)),  # the line of three: five would hold a one in every reading
)
# Each cell's mark, as its place in the method's order. Fourteen cells of
# fourteen values pooled at eleven: the marks take them in turn. Thirty
# cells of three values, ten each: each run gives nine to one mark -- two
# short of the line, so no value fills a mark alone (plan P4-D356) -- and
# its tenth to the next, and the one mark left empty is given the last
# cell of the fullest, the comma's.
# Thirty cells of thirty values pooled at fourteen: thirty is not fewer
# than fourteen and the floor together, so fourteen are marked, SPREAD
# over the thirty (plan P4-D149), and the sixteen bare cells (-1) lie
# among them from the lowest value to the highest. Packed onto the first
# fourteen, the sixteen largest would be the ones left bare.
LONE_POOL_CELLS = (
    ((14, 14, 11), tuple(range(14)),
     (0, 1, 2, 3, 4, 5, 6, 0, 1, 2, 3, 4, 5, 6)),
    ((30, 30, 11), (0,) * 10 + (1,) * 10 + (2,) * 10,
     (0,) * 8 + (6, 1) + (2,) * 9 + (3,) + (4,) * 9 + (5,)),
    ((14, 30, 11), tuple(range(30)),
     (-1, -1, 0, -1, 1, -1, 2, -1, 3, -1, 4, -1, 5, -1, 6,
      -1, -1, 0, -1, 1, -1, 2, -1, 3, -1, 4, -1, 5, -1, 6)),
)
LONE_POOL_ORDER = (",", " ", "'", "’", " ", " ", " ")


def _lone_pool_counts(rule, pool, groupable, floor):
    flags = [True] * groupable + [False] * 5
    worn = list(rule(pool, flags, floor, [float(i) for i in range(len(flags))]))
    counts = tuple(worn.count(mark) for mark in LONE_POOL_ORDER)
    return counts, sum(1 for mark in worn[:groupable] if not mark)


def _lone_pool_cells(rule, pool, groupable, floor, runs):
    flags = [True] * groupable + [False] * 5
    values = [1000.0 + run for run in runs] + [float(i) for i in range(5)]
    worn = list(rule(pool, flags, floor, values))
    return tuple(
        LONE_POOL_ORDER.index(mark) if mark else -1 for mark in worn[:groupable]
    )


def _lone_pool_missed(rule) -> "list[str]":
    missed = []
    for (pool, groupable, floor), want in LONE_POOL_COUNTS:
        got = _asked(_lone_pool_counts, rule, pool, groupable, floor)
        if got != want:
            missed += [
                f"pool {pool} of {groupable} groupable at floor {floor}:"
                f" {got!r}, the statement gives {want!r}"
            ]
    for (pool, groupable, floor), runs, want in LONE_POOL_CELLS:
        got = _asked(_lone_pool_cells, rule, pool, groupable, floor, runs)
        if got != want:
            missed += [
                f"cells of pool {pool} over runs {runs!r}:"
                f" {got!r}, the statement gives {want!r}"
            ]
    return missed


def _shipped_lone_pool(pool, flags, floor, values):
    worn, _notes = generation._pool_alone_places(
        types.SimpleNamespace(name="value"), flags, floor, values, pool
    )
    return worn


# ---------------------------- G6.1's lone pool, over how many marks it is spent
#
# The review of follow-up B, item 4, worked by hand from the method's
# sentence. K is seven unless the number cells written with seven hold
# more different folded spellings than the count G6.5 aims at; then the
# first of six, five and on down to k whose cells hold no more, and where
# none does, the count from k to seven whose cells hold the fewest, the
# most marks on a tie -- k the fewest marks, two or more, whose number as
# the room lets the pool stand: every reading of at most k marks under
# L = max(2, floor) leaves one of the seven out and none holds a count in
# every reading (plan P4-D356). Each row: (pool, floor, budget, the
# spellings at seven marks down to two) and K.
POOL_MARK_COUNTS = (
    ((14, 11, 4, (8, 7, 6, 5, 4, 3)), 3),  # the review's shape: 4 of 4 at three
    ((14, 11, 3, (8, 7, 6, 5, 4, 3)), 2),  # seven and seven: two hold 4..10 each
    ((14, 11, 16, (16, 16, 16, 16, 16, 16)), 7),  # room for all seven
    ((60, 11, 10, (99, 98, 97, 96, 95, 94)), 7),  # sixty: six marks read ten each
    ((25, 11, 2, (9, 8, 7, 6, 5, 4)), 3),  # three hold 10 10 5 and 9 9 7: the fewest
    ((40, 31, 6, (9, 8, 7, 6, 5, 4)), 4),  # at thirty-one: six at four marks
    ((4, 3, 1, (9, 8, 7, 6, 5, 4)), 4),  # the line of three: 2 2, 2 1 1, 1 1 1 1
    ((11, 11, 5, (7, 6, 6, 6, 5, 5)), 3),  # eleven: two hold it; five at three
    ((50, 11, 55, (56, 56, 56, 56, 55, 55)), 7),  # fifty: five read ten each; none fits
    ((40, 11, 3, (9, 8, 6, 7, 5, 4)), 5),  # forty: four read ten each; five the fewest
)


def _pool_mark_counts_missed(rule) -> "list[str]":
    missed = []
    for (pool, floor, budget, down), want in POOL_MARK_COUNTS:
        spelled = {7 - place: down[place] for place in range(6)}
        got = _asked(rule, pool, floor, budget, spelled)
        if got != want:
            missed += [
                f"pool {pool} at floor {floor} beside {budget} spellings:"
                f" {got!r}, the statement gives {want!r}"
            ]
    return missed


def _oracle_pool_mark_count(module):
    def rule(pool, floor, budget, spelled):
        return module.lone_pool_count(
            {"(withheld)": pool}, floor, budget,
            lambda count: [str(text) for text in range(spelled[count])],
        )
    return rule


# ------------------------------- G6.1's trailing minus, and the points it needs
#
# The second skeptic of plan P4-D352, worked by hand from the method's
# sentences. THE EXCHANGE: while fewer cells allocated `decimal` hold a
# negative value than R -- the named `trailing_minus`, no larger than the
# negative cells -- each `plain` cell on a negative value, first upward,
# takes `decimal` from the `decimal` cell on a value not below zero that has
# a point-free spelling, last downward, which takes `plain`; and the
# `decimal` cells not below zero stay at least the named `decimal_plus`.
# THE ORDER: the trailing minus takes its count before the notations the
# contract orders ahead of it. The frozen case `trailing_minus_points`
# reaches the values step and the order and never the exchange: no
# negative there is whole before the step. Each row: (R, decimal_plus,
# styles, values) and the styles the statement gives.
TRAILING_EXCHANGES = (
    # two pairs: every donor spent
    ((2, 0, ("plain", "plain", "decimal", "decimal", "plain"),
      (-3.0, -2.0, 1.0, 5.0, 7.0)),
     ("decimal", "decimal", "plain", "plain", "plain")),
    # one decimal cell kept for the plus: one pair, the last donor
    ((2, 1, ("plain", "plain", "decimal", "decimal", "plain"),
      (-3.0, -2.0, 1.0, 5.0, 7.0)),
     ("decimal", "plain", "decimal", "plain", "plain")),
    # 5.5 has no point-free spelling, so it gives nothing
    ((2, 0, ("plain", "plain", "decimal", "decimal", "plain"),
      (-3.0, -2.0, 1.0, 5.5, 7.0)),
     ("decimal", "plain", "plain", "decimal", "plain")),
    # a negative already carries the point the count asks for
    ((1, 0, ("decimal", "plain", "decimal", "decimal"),
      (-3.0, -2.0, 1.0, 5.0)),
     ("decimal", "plain", "decimal", "decimal")),
    # R past the two negatives; nought is not below zero and gives first
    ((5, 0, ("plain", "plain", "decimal", "decimal", "decimal"),
      (-3.0, -2.0, 1.0, 5.0, 0.0)),
     ("decimal", "decimal", "decimal", "plain", "plain")),
    # only a `plain` cell takes: the padded negative keeps its form
    ((2, 0, ("leading_zero", "plain", "decimal", "decimal"),
      (-3.0, -2.0, 1.0, 5.0)),
     ("leading_zero", "decimal", "decimal", "plain")),
)
# (census, styles, values) and each cell's notation: the trailing minus
# takes the one cell with a point before the brackets can.
TRAILING_ORDERS = (
    (({"brackets": 1, "trailing_minus": 1}, ("plain", "decimal"), (-2.0, -1.5)),
     ("brackets", "trailing_minus")),
    (({"minus": 1, "trailing_minus": 2}, ("decimal", "plain", "decimal"),
      (-4.5, -3.0, -1.5)),
     ("trailing_minus", "minus", "trailing_minus")),
)


def _trailing_missed(exchange, order) -> "list[str]":
    missed = []
    for (count, plus, styles, values), want in TRAILING_EXCHANGES:
        got = _asked(exchange, count, plus, list(styles), list(values))
        if got is None or isinstance(got, str) or tuple(got) != want:
            missed += [
                f"exchange of {count} over {styles!r} at {values!r}: {got!r},"
                f" the statement gives {want!r}"
            ]
    for (census, styles, values), want in TRAILING_ORDERS:
        got = _asked(order, census, list(styles), list(values))
        if got is None or isinstance(got, str) or tuple(got) != want:
            missed += [
                f"notations of {census!r} over {styles!r}: {got!r},"
                f" the statement gives {want!r}"
            ]
    return missed


def _oracle_trailing(module):
    return (
        lambda count, plus, styles, values: module.trailing_style_exchange(
            count, plus, styles, values, False
        ),
        lambda census, styles, values: module.notation_places(
            census, "minus", styles, values
        ),
    )


def _shipped_exchange(count, plus, styles, values):
    facts = types.SimpleNamespace(
        negative_notations={"trailing_minus": count},
        decimal_plus={"+": plus} if plus else {},
    )
    return generation._trailing_style_swaps(facts, styles, values, False)


def _shipped_order(census, styles, values):
    worn, _notes = generation._notation_places(
        types.SimpleNamespace(name="value"),
        types.SimpleNamespace(negative_form="minus", negative_notations=census),
        styles,
        values,
    )
    return worn


# ----------------------------- G6.4's values step beside a trailing minus
#
# W point-free cells, N negative, F not negative, R the named
# `trailing_minus` no larger than N. Where R is above nought a walk over
# the strata that are not negative comes before the walk over every
# stratum, until they carry the lesser of W - max(0, N - R) and F, and the
# last walk then takes the strata that are not negative first, ascending,
# and the negative ones nearest zero first, and so does the walk over the
# negative strata alone that a D above nought asks for; where R is nought
# both walk them in stratum order. No frozen case reaches the first walk,
# nor a D beside an R: withdrawn, every committed vectors file and every
# row above stood (the second skeptic of plan P4-D352 (6), and its round
# 3). One cell per stratum and no ladder, so each stratum
# takes its nearest whole number, ties toward positive infinity (G5.4),
# and the ends stay. Each row: (styles, values, R, D), D the named
# `decimal_plus`, and the values the statement gives.
TRAILING_VALUES = (
    # -9 and -6 are whole already, so the last walk is met at three; R = N
    # leaves no negative point-free, so 1.5 and 2.5 are taken first.
    (({"plain": 3, "decimal": 5}, (-9.0, -6.0, -4.3, -3.2, 1.5, 2.5, 3.5, 8.0), 4, 0),
     (-9.0, -6.0, -4.3, -3.2, 2.0, 3.0, 3.5, 8.0)),
    # W - (N - R) = 1: 1.5 first; then 2.5, and -2.2, the negative nearest zero
    (({"plain": 3, "decimal": 4}, (-9.5, -6.5, -4.3, -2.2, 1.5, 2.5, 8.5), 2, 0),
     (-9.5, -6.5, -4.3, -2.0, 2.0, 3.0, 8.5)),
    # no trailing minus: the lowest strata first
    (({"plain": 2, "decimal": 4}, (-9.5, -6.5, -4.3, 1.5, 2.5, 8.5), 0, 0),
     (-9.5, -6.0, -4.0, 1.5, 2.5, 8.5)),
    # N - R = 2 and -9 and -6 are whole already, so W - (N - R) = 1, which
    # 8 carries: the walk beside moves nothing, and -9, -6 and 8 meet the
    # last walk. Asked for W, the walk beside would make 1.5 and 2.5 whole.
    (({"plain": 3, "decimal": 4}, (-9.0, -6.0, -4.3, 1.5, 2.5, 3.5, 8.0), 1, 0),
     (-9.0, -6.0, -4.3, 1.5, 2.5, 3.5, 8.0)),
    # one cell asked, two strata that are not negative before any negative:
    # the lower, 1.5, and not 2.4
    (({"plain": 1, "decimal": 4}, (-9.5, -4.3, 1.5, 2.4, 9.5), 1, 0),
     (-9.5, -4.3, 2.0, 2.4, 9.5)),
    # D = 2 of F = 3 keep a point, so W - (F - D) = 2 negatives are made
    # whole, nearest zero first: -2.5 and -4.5; then the last walk, 1.5
    (({"plain": 3, "decimal": 4}, (-9.5, -6.5, -4.5, -2.5, 1.5, 3.5, 9.5), 1, 2),
     (-9.5, -6.5, -4.0, -2.0, 2.0, 3.5, 9.5)),
    # the same with no trailing minus: the lowest negatives, -6.5 and -4.5,
    # and then -2.5, the next in stratum order
    (({"plain": 3, "decimal": 4}, (-9.5, -6.5, -4.5, -2.5, 1.5, 3.5, 9.5), 0, 2),
     (-9.5, -6.0, -4.0, -2.0, 1.5, 3.5, 9.5)),
)


def _bands(values):
    return tuple(
        "negative" if value < 0 else "zero" if value == 0 else "positive"
        for value in values
    )


def _trailing_values_missed(rule) -> "list[str]":
    missed = []
    for (styles, values, count, signed), want in TRAILING_VALUES:
        got = _asked(rule, styles, values, count, signed)
        if got is None or isinstance(got, str) or tuple(got) != want:
            missed += [
                f"values step of {styles!r} over {values!r} beside {count}"
                f" trailing and {signed} signed: {got!r}, the statement gives {want!r}"
            ]
    return missed


def _oracle_trailing_values(module):
    return lambda styles, values, count, signed: module.whole_number_values(
        styles, list(values), [1] * len(values), list(range(len(values))),
        list(_bands(values)), None, len(values), False, signed, count,
    )


def _shipped_trailing_values(styles, values, count, signed):
    facts = types.SimpleNamespace(
        integer_valued=False,
        numeric_styles=styles,
        decimal_plus={"+": signed} if signed else {},
        negative_notations={"trailing_minus": count} if count else {},
        kept_stand_ins=(),
    )
    layout = types.SimpleNamespace(
        sizes=(1,) * len(values),
        starts=tuple(range(len(values))),
        bands=_bands(values),
    )
    return generation._whole_enough(
        types.SimpleNamespace(n_numeric=len(values)),
        typing.cast(contract.NumericFacts, facts),
        typing.cast(typing.Any, layout),
        None,
        list(values),
    )


# ------------------------------------- G7.3b step 9's choice and placement
#
# THE STEP'S ORDER AND ITS KEEP-ONE CAP WERE PARTED BY NO FROZEN CASE (the
# second skeptic of landing 3b.0, 2026-09-26). The one case that reaches
# the step, `every_day_group`, takes every offer it has, so with the
# oracle's order turned outer-first, or its cap lifted so a group gives
# its last rank, every vectors file rebuilt byte for byte. The rule is
# asked here one call at a time: each tail as its group's distance `g`,
# its group's ranks `G` and the distances it offers, and the answer the
# method's sentence gives -- each tail's group distances from its
# outermost group rank inward -- worked out by hand. The offers go in
# this order while the count is short: the smaller |d - g| first; at one
# |d - g|, the smaller d; at one |d - g| and one d, the low tail. A group
# keeps one rank. Units outside g go to the outermost ranks, the largest
# outermost; units inside g to the innermost, the smallest innermost.
GROUP_OFFERS = (
    # (low (g, G, offered) or None, high the same, owed, low answer, high answer)
    #
    # THE FROZEN CASE'S TWO GROUPS, owed four, three, two, one and nought.
    # The offers sort (1, 1, high), (1, 2, low), (1, 4, low), (2, 1, low).
    ((3, 21, (1, 2, 4)), (2, 11, (1,)), 4,
     (4,) + (3,) * 18 + (2, 1), (2,) * 10 + (1,)),
    ((3, 21, (1, 2, 4)), (2, 11, (1,)), 3,
     (4,) + (3,) * 19 + (2,), (2,) * 10 + (1,)),
    ((3, 21, (1, 2, 4)), (2, 11, (1,)), 2,
     (3,) * 20 + (2,), (2,) * 10 + (1,)),
    # Owed one: the high tail's unit one out, at a remove of one, before
    # the low tail's two out (the smaller d); taken outer-first, the low
    # tail's four out would go instead.
    ((3, 21, (1, 2, 4)), (2, 11, (1,)), 1,
     (3,) * 21, (2,) * 10 + (1,)),
    ((3, 21, (1, 2, 4)), (2, 11, (1,)), 0,
     (3,) * 21, (2,) * 11),
    # At one remove and one distance, the low tail first.
    ((3, 5, (2,)), (3, 5, (2,)), 1, (3, 3, 3, 3, 2), (3,) * 5),
    # At one remove, the smaller distance across the two tails.
    ((5, 5, (4,)), (2, 5, (1,)), 1, (5,) * 5, (2, 2, 2, 2, 1)),
    # A GROUP KEEPS ONE RANK: two ranks give one, however much is owed.
    ((3, 2, (2, 4, 1)), None, 3, (3, 2), None),
    # ...and the other tail takes what the full one cannot.
    ((3, 2, (2, 4)), (2, 4, (1, 3, 4)), 3, (3, 2), (3, 2, 2, 1)),
    # Several units outside g: the largest on the outermost rank.
    ((2, 5, (3, 4, 5)), None, 3, (5, 4, 3, 2, 2), None),
    # Several units inside g: the smallest on the innermost rank.
    ((5, 5, (1, 2, 3)), None, 3, (5, 5, 3, 2, 1), None),
    # One tail alone.
    (None, (2, 3, (1, 3)), 1, None, (2, 2, 1)),
)


def _group_missed(rule: typing.Callable[..., object]) -> "list[str]":
    missed = []
    for low, high, owed, want_low, want_high in GROUP_OFFERS:
        got = _asked(rule, low, high, owed)
        if got != (want_low, want_high):
            missed += [
                f"{low!r} and {high!r} owed {owed}: {got!r}, the statement gives"
                f" {(want_low, want_high)!r}"
            ]
    return missed


def _oracle_group(module: types.ModuleType) -> typing.Callable[..., object]:
    def placed(low, high, owed):
        tails = {
            name: (spec[0], spec[1], list(spec[2]))
            for name, spec in (("low", low), ("high", high))
            if spec is not None
        }
        found = module.group_offers_taken(tails, owed)
        return tuple(
            tuple(found[name]) if name in found else None for name in ("low", "high")
        )
    return placed


def _generator_group(low, high, owed):
    offered = [
        None if spec is None else (spec[0], spec[1], list(spec[2])) for spec in (low, high)
    ]
    found = generation._group_offers_taken(offered, owed)
    return tuple(
        None if offered[side] is None else tuple(found[side]) for side in range(2)
    )


# ------------------------------------------- G7.3's merges move a run whole
#
# A RUN MOVES WHOLE, SO IT MOVES ONLY WHERE EVERY RANK OF IT MAY GO (the
# fix pass of landing 3b.0, plan P4-D354). The count pass merges a run of
# ranks on one unit onto an instant ranks already hold, and asked the
# run's FIRST rank alone whether the instant lay inside its gap. A body
# run shares one gap; a tail run does not, each rank's gap being its own
# stratum (G7.3b step 8), so the rest of the run went past theirs. Asked
# here on hand-built ranks: an unpinned run between pinned ends, each
# rank's gap given, and the answer the statement gives -- the instant must
# lie inside the gap of EVERY rank of the run -- worked out by hand. Days
# are whole numbers; the rows in seconds (a day of 86400) put the run's
# rank neighbours at midnight, so only the nearest held unit of its own
# standing is offered, and the trade moves a run onto the other standing.
DAY = 86400


def _day(month: int, day: int) -> int:
    """A day of 2020 as the day number both implementations read (days since 1970-01-01)."""
    return (datetime.date(2020, month, day) - datetime.date(1970, 1, 1)).days


RUN_MERGES = (
    # (ordinals, pinned, lows, highs, day, distinct, width word, ordinals after)
    #
    # THE NEIGHBOUR. The run of ranks 2 and 3 on day 3 may go to day 2
    # (its first rank's gap) or to day 4 (both ranks' gaps). Asked of its
    # first rank, day 2 is taken, nearer the start, and rank 3 stands a
    # day below its gap; asked of every rank, day 4.
    ((0, 2, 3, 3, 4, 6), (True, False, False, False, False, True),
     (0, 1, 2, 3, 4, 6), (0, 2, 4, 4, 5, 6), 1, 4, "",
     (0, 2, 4, 4, 4, 6)),
    # THE HELD UNIT NO RANK NEIGHBOUR IS. The run's neighbours stand at
    # midnight and it does not, so they are not offered; the one held unit
    # of its own standing, second 50, lies in its first rank's gap and not
    # in its last's. Rank 1 at midnight has no other midnight in its gap,
    # and its trade finds no payer. Nothing moves; the count stays one over.
    ((50, DAY, DAY + 500, DAY + 500, 2 * DAY, 3 * DAY),
     (True, False, False, False, False, True),
     (50, 50, 50, DAY + 100, 100000, 3 * DAY),
     (50, DAY + 1000, DAY + 1000, DAY + 1000, 200000, 3 * DAY), DAY, 4, "",
     (50, DAY, DAY + 500, DAY + 500, 2 * DAY, 3 * DAY)),
    # THE NEIGHBOUR READ AGAIN. Rank 1 merges onto day 1 first; the run of
    # ranks 2 and 3, offered rank 1's day 3, then finds day 1 there, which
    # its first rank's gap holds and its last's does not. It stays.
    ((1, 3, 5, 5, 9), (True, False, False, False, True),
     (1, 1, 1, 3, 9), (1, 3, 6, 6, 9), 1, 2, "",
     (1, 1, 5, 5, 9)),
    # THE NEAREST HELD UNIT IS LOOKED FOR INSIDE THE ROOM. Month-first
    # dates of 2020 under the census word `first-field-padded`: the ninth
    # of April and the first of May show the other width kind, so the
    # run's neighbours are not offered. The nearest held unit of its own
    # kind in its first rank's gap is the 31st of March, twelve days off,
    # outside its last rank's gap; inside the gap of both is the 20th of
    # May, thirty-eight off, and the run moves there. Looked for in the
    # first rank's gap, the 31st is found, refused, and nothing moves.
    ((_day(3, 31), _day(4, 9), _day(4, 12), _day(4, 12), _day(5, 1), _day(5, 20)),
     (True, False, False, False, False, True),
     (_day(3, 31), _day(3, 31), _day(3, 31), _day(4, 5), _day(4, 20), _day(5, 20)),
     (_day(3, 31), _day(4, 9), _day(5, 20), _day(5, 20), _day(5, 20), _day(5, 20)),
     1, 4, "first-field-padded",
     (_day(3, 31), _day(4, 9), _day(5, 20), _day(5, 20), _day(5, 1), _day(5, 20))),
    #
    # A RUN NO MERGE CAN TAKE IS SPLIT (the third skeptic of landing 3b.0).
    # THE SPLIT. Ranks 2 and 3 on day 3 have gaps meeting on day 3 alone,
    # so their room is their own day and no rank neighbour lies in it.
    # Rank 2 goes onto rank 1's day 2, inside its gap; rank 3 cannot, and
    # goes onto rank 4's day 5, inside its own. Day 3 is freed.
    ((0, 2, 3, 3, 5, 7), (True, False, False, False, False, True),
     (0, 1, 2, 3, 4, 7), (0, 2, 3, 5, 6, 7), 1, 4, "",
     (0, 2, 2, 5, 5, 7)),
    # IN ORDER. Rank 2 reaches only the day above the run and rank 3 only
    # the day below it; the ranks keep their order, so once one rank has
    # gone up none goes down, and rank 3 has nowhere. Nothing moves. (Taken
    # rank by rank, rank 2 goes up and rank 3 down, past each other.)
    ((0, 2, 3, 3, 5, 7), (True, False, False, False, False, True),
     (0, 1, 3, 2, 4, 7), (0, 2, 5, 4, 6, 7), 1, 4, "",
     (0, 2, 3, 3, 5, 7)),
    # OF ITS OWN STANDING. In seconds, the run stands off midnight and its
    # neighbours at midnight: rank 2's gap holds the day below and rank 3's
    # the day above, and neither may take a unit of the other standing.
    # No midnight lies inside the room, so there is no trade. Nothing moves.
    ((0, DAY, DAY + 500, DAY + 500, 2 * DAY, 3 * DAY),
     (True, True, False, False, True, True),
     (0, DAY, DAY, DAY + 400, 2 * DAY, 3 * DAY),
     (0, DAY, DAY + 600, 2 * DAY, 2 * DAY, 3 * DAY), DAY, 4, "",
     (0, DAY, DAY + 500, DAY + 500, 2 * DAY, 3 * DAY)),
    # ONLY WHERE THE ROOM HOLDS NO OTHER HELD UNIT. The run on day 5 is
    # offered day 6, the nearest held unit in its room 3 to 6; rank 5 merges
    # off day 6 first, onto day 7, so that merge is not made. Day 3, held by
    # a pinned rank out of order, still lies in the room, so the run is
    # left for the next round's merge rather than split across days 2 and 9.
    ((0, 2, 5, 5, 9, 6, 7, 3, 10),
     (True, True, False, False, True, False, True, True, True),
     (0, 2, 2, 3, 9, 6, 7, 3, 10), (0, 2, 6, 9, 9, 7, 7, 3, 10), 1, 6, "",
     (0, 2, 5, 5, 9, 7, 7, 3, 10)),
    # ALONE ON ITS UNIT (the fourth skeptic). The run of ranks 2 and 3 on
    # day 5 shares that day with the pinned rank 7, out of order; its room
    # 3 to 6 holds no other held unit, and rank 2 could go to day 2 and
    # rank 3 to day 9. The run is not alone on its unit, so it is not
    # split, and day 5 stays held. Nothing moves.
    ((0, 2, 5, 5, 9, 8, 8, 5, 10),
     (True, True, False, False, True, False, True, True, True),
     (0, 2, 2, 3, 9, 8, 8, 5, 10), (0, 2, 6, 9, 9, 8, 8, 5, 10), 1, 5, "",
     (0, 2, 5, 5, 9, 8, 8, 5, 10)),
    # AT MOST OWED. Two runs could be split, on day 3 and on day 8, and
    # one unit is owed: the first in rank order is split, the second is
    # left where it stands.
    ((0, 2, 3, 3, 5, 7, 8, 8, 10, 12),
     (True, False, False, False, False, False, False, False, False, True),
     (0, 1, 2, 3, 4, 6, 7, 8, 9, 12), (0, 2, 3, 5, 6, 7, 8, 10, 11, 12), 1, 7, "",
     (0, 2, 2, 5, 5, 7, 8, 8, 10, 12)),
    # OF ITS OWN STANDING ON THE WAY DOWN. Rank 2 could go down onto the
    # pinned midnight of day 1, which is inside its gap, and rank 3 up
    # onto the pinned second 300 of day 2, inside its own and of its
    # standing; the way down changes the standing, so the run is not
    # split (asked of the way up alone, it would be). Nothing moves.
    ((0, DAY, DAY + 500, DAY + 500, 2 * DAY + 300, 3 * DAY),
     (True, True, False, False, True, True),
     (0, DAY, DAY, DAY + 400, 2 * DAY + 300, 3 * DAY),
     (0, DAY, DAY + 600, 2 * DAY + 300, 2 * DAY + 300, 3 * DAY), DAY, 4, "",
     (0, DAY, DAY + 500, DAY + 500, 2 * DAY + 300, 3 * DAY)),
    # OF ITS OWN STANDING ON THE WAY UP, the mirror: rank 2 could go down
    # onto the pinned second 300 of day 1, of its standing, and rank 3 up
    # onto the pinned midnight of day 3, which is not. Nothing moves.
    ((0, DAY + 300, 2 * DAY + 500, 2 * DAY + 500, 3 * DAY, 4 * DAY),
     (True, True, False, False, True, True),
     (0, DAY + 300, DAY + 300, 2 * DAY + 400, 3 * DAY, 4 * DAY),
     (0, DAY + 300, 2 * DAY + 600, 3 * DAY, 3 * DAY, 4 * DAY), DAY, 4, "",
     (0, DAY + 300, 2 * DAY + 500, 2 * DAY + 500, 3 * DAY, 4 * DAY)),
    #
    # WHERE NO ONE RUN CAN GIVE A UNIT UP, THE RANKS ARE STACKED AFRESH
    # (the fourth skeptic of landing 3b.0).
    # THE STACK. Rank 1 alone on day 1, the pairs on days 3 and 5 with
    # two-day strata shifted by one rank each, rank 6 alone on day 6: each
    # pair's room is its own day and its neighbours stand two days off, so
    # no merge and no split takes any of them, while every rank moving one
    # day onto the next frees day 1. Taken by upper ends, rank 1 stacks day
    # 2 and rank 2 joins it, rank 3 stacks day 4 and rank 4 joins, rank 5
    # stacks day 6 and rank 6 joins: five units, the count, and taken.
    ((0, 1, 3, 3, 5, 5, 6, 8), (True, False, False, False, False, False, False, True),
     (0, 1, 2, 3, 4, 5, 6, 8), (0, 2, 3, 4, 5, 6, 7, 8), 1, 5, "",
     (0, 2, 2, 4, 4, 6, 6, 8)),
    # THE RAISE. The same chain twice over, ranks 1 to 10 over days 1 to
    # 10, stacks seven units where eight are wanted; in rank order, rank 1,
    # sharing day 2, moves onto day 1, the nearest free unit inside its gap,
    # and the count is met.
    ((0, 1, 3, 3, 4, 6, 6, 7, 9, 9, 10, 12),
     (True, False, False, False, False, False, False, False, False, False, False, True),
     (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12), (0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12), 1, 8, "",
     (0, 1, 2, 4, 4, 6, 6, 8, 8, 10, 10, 12)),
    # ONLY WHERE THE COUNT IS MET. The stack of these ranks holds four
    # units, days 0, 2, 4 and 6, and three are wanted: it is not taken, and
    # nothing moves.
    ((0, 1, 3, 3, 4, 6), (True, False, False, False, False, True),
     (0, 1, 2, 3, 4, 6), (0, 2, 3, 4, 5, 6), 1, 3, "",
     (0, 1, 3, 3, 4, 6)),
    # BY THE UPPER ENDS. Rank 2's gap reaches day 5, past rank 3's day 4:
    # taken by upper ends, rank 3 stacks day 4 before rank 2's turn and
    # rank 2 joins it, as rank 4 does. Taken in rank order, rank 2 would
    # join rank 1's day 2 and rank 3 stack day 4: the count met on other
    # days.
    ((0, 1, 3, 3, 5, 6), (True, False, False, False, False, True),
     (0, 1, 2, 3, 4, 6), (0, 2, 5, 4, 5, 6), 1, 4, "",
     (0, 2, 4, 4, 4, 6)),
    # THE PINNED RANK STANDS. The pinned rank 1 stands on day 2 with a gap
    # of days 1 to 3 (which the layout never gives a pin); taken by that
    # gap it would stack day 3 and ranks 2 and 3 join it, three units, the
    # count. Taken where it stands, the stack holds four: nothing moves.
    ((0, 2, 3, 3, 5), (True, True, False, False, True),
     (0, 1, 2, 3, 5), (0, 3, 3, 4, 5), 1, 3, "",
     (0, 2, 3, 3, 5)),
    #
    # THE RAISE, clause by clause (the fifth skeptic of landing 3b.0).
    # A PINNED RANK IS NOT RAISED, AND THE RAISE STAYS INSIDE THE GAP. The
    # stack holds days 6 (the pin and rank 1), 8, 11 and 13, four of five.
    # The pin, gap 5 to 6 (which the layout never gives a pin), is passed
    # by; rank 1's nearest free day inside its gap 6 to 7 is day 7, and
    # the count is met. (Raising the pin puts it on day 5; searched past
    # the gap, rank 1 goes to day 5, earlier first.)
    ((6, 7, 7, 9, 10, 10, 12, 13), (True, False, False, False, False, False, False, True),
     (5, 6, 7, 8, 8, 10, 11, 12), (6, 7, 8, 9, 10, 11, 12, 13), 1, 5, "",
     (6, 7, 8, 8, 8, 11, 11, 13)),
    # The same below the gap's lower end: the stack holds days 0 (the pin
    # and rank 1), 3, 6 and 8, and rank 1 goes to day 1 inside its gap 0
    # to 2; day -1, as near and earlier, lies outside it.
    ((0, 2, 2, 4, 5, 5, 7, 8, 8), (True, False, False, False, False, False, False, False, True),
     (0, 0, 2, 3, 3, 5, 6, 7, 8), (0, 2, 3, 4, 5, 6, 7, 8, 10), 1, 5, "",
     (0, 1, 3, 3, 3, 6, 6, 8, 8)),
    # ONLY A RANK SHARING ITS UNIT IS RAISED. The stack holds days 0, 2,
    # 3 (the pin and rank 3), 5, 8 and 11, six of seven. Rank 1 stands
    # alone on day 2 and is passed by (raised, it would leave day 2 empty
    # and count day 1 as a seventh unit); rank 3 goes to day 4.
    ((0, 1, 3, 4, 4, 6, 7, 7, 10, 11),
     (True, False, True, False, False, False, False, False, False, True),
     (0, 1, 3, 3, 4, 5, 5, 7, 8, 9), (1, 2, 3, 4, 5, 6, 7, 8, 10, 11), 1, 7, "unpadded",
     (0, 2, 3, 4, 5, 5, 5, 8, 8, 11)),
    # OF ITS STANDING. Month-first dates under `first-field-padded`: a day
    # below the 10th counts outside the word. The stack holds the 9th of
    # January (the pin and rank 1), the 11th, 14th and 16th, four of five.
    # Rank 1's one free day inside its gap is the 10th, of the other kind,
    # so it is passed by; rank 2 goes from the 11th to the 10th, of its own.
    ((_day(1, 9), _day(1, 9), _day(1, 10), _day(1, 12), _day(1, 13), _day(1, 13),
      _day(1, 15), _day(1, 16)),
     (True, False, False, False, False, False, False, True),
     (_day(1, 9), _day(1, 9), _day(1, 10), _day(1, 11), _day(1, 11), _day(1, 13),
      _day(1, 14), _day(1, 16)),
     (_day(1, 9), _day(1, 10), _day(1, 11), _day(1, 12), _day(1, 13), _day(1, 14),
      _day(1, 15), _day(1, 16)), 1, 5, "first-field-padded",
     (_day(1, 9), _day(1, 9), _day(1, 10), _day(1, 11), _day(1, 11), _day(1, 14),
      _day(1, 14), _day(1, 16))),
    # THE NEAREST FREE UNIT IS ONE NO RANK HOLDS, A UNIT RAISED ONTO
    # INCLUDED (the landing's sixth skeptic). Nothing merges, trades or
    # splits, and the stack holds ten days: 0, 2 (ranks 1 to 3), 4 (4 and
    # 5), 6, 8, 10, 12, 14, 16 and 18, each later pair on its upper day.
    # Raised in rank order to twelve: rank 1 onto day 1, the one free day
    # in its gap of 1 to 2; ranks 2 and 3 then find none, day 1 being held;
    # rank 4 onto day 3. (With a day raised onto read as free again, rank
    # 2 goes to day 1 too and the stack is taken holding eleven.)
    ((0, 2, 2, 2, 3, 5, 5, 6, 8, 8, 9, 11, 11, 12, 14, 14, 15, 17, 18),
     (True,) + (False,) * 17 + (True,),
     (0, 1, 1, 1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18),
     (0, 2, 2, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18), 1, 12, "",
     (0, 1, 2, 2, 3, 4, 6, 6, 8, 8, 10, 10, 12, 12, 14, 14, 16, 16, 18)),
)
RUN_TRADES = (
    # (ordinals, pinned, lows, highs, owed, ordinals after, trades made)
    #
    # THE TRADE. The run of ranks 1 and 2 stands off midnight; the only
    # midnight in its first rank's gap is second 0, outside its second
    # rank's, so it is offered nothing. The run of three at midnight on
    # day 3 is offered 3D + 300, and its payment needs three ranks off
    # midnight to move onto one: rank 1 can, and rank 2 then stands alone.
    # Nothing trades. (Asked of the first rank alone, ranks 1 and 2 move
    # onto second 0, rank 2 below its gap, paid for by ranks 4 and 5.)
    ((0, DAY + 100, DAY + 100, 2 * DAY, 3 * DAY, 3 * DAY, 3 * DAY, 3 * DAY + 300, 4 * DAY),
     (True, False, False, True, False, False, False, False, True),
     (0, 0, DAY + 50, 2 * DAY) + (3 * DAY - 1000,) * 4 + (4 * DAY,),
     (0, DAY + 200, DAY + 200, 2 * DAY) + (3 * DAY + 1000,) * 4 + (4 * DAY,), 1,
     (0, DAY + 100, DAY + 100, 2 * DAY, 3 * DAY, 3 * DAY, 3 * DAY, 3 * DAY + 300, 4 * DAY), 0),
)
# The member the width rows are read under, month-first, so its first
# field is the month.
RUN_MEMBER = "month-first-date"


def _run_missed(merge: typing.Callable[..., object], trade: typing.Callable[..., object]) -> "list[str]":
    missed = []
    for ordinals, pinned, lows, highs, day, distinct, word, want in RUN_MERGES:
        got = _asked(
            merge, list(ordinals), list(pinned), list(lows), list(highs), day, distinct, word
        )
        if got != want:
            missed += [f"merge of {ordinals!r}: {got!r}, the statement gives {want!r}"]
    for ordinals, pinned, lows, highs, owed, want, made in RUN_TRADES:
        got = _asked(trade, list(ordinals), list(pinned), list(lows), list(highs), owed)
        if got != (want, made):
            missed += [f"trade of {ordinals!r}: {got!r}, the statement gives {(want, made)!r}"]
    return missed


def _held(ordinals: "list[int]") -> "dict[int, int]":
    return dict(collections.Counter(ordinals))


def _oracle_run(module: types.ModuleType) -> "tuple[typing.Callable[..., object], typing.Callable[..., object]]":
    def merge(ordinals, pinned, lows, highs, day, distinct, word):
        module.distinct_pass(
            {"format": RUN_MEMBER}, ordinals, pinned, lows, highs, day, 1, distinct,
            bool(word), word,
        )
        return tuple(ordinals)

    def trade(ordinals, pinned, lows, highs, owed):
        made = module.traded_merges(
            {"format": RUN_MEMBER}, ordinals, pinned, lows, highs, DAY, 1, 1,
            _held(ordinals), False, "", owed, True,
        )
        return (tuple(ordinals), made)

    return merge, trade


_RUN_FACTS = types.SimpleNamespace(parser_family=RUN_MEMBER)


def _generator_merge(ordinals, pinned, lows, highs, day, distinct, word):
    generation._distinct_reached(
        typing.cast(contract.DatetimeFacts, _RUN_FACTS), ordinals, pinned, lows, highs,
        day, 1, distinct, bool(word), word,
    )
    return tuple(ordinals)


def _generator_trade(ordinals, pinned, lows, highs, owed):
    made = generation._traded_merges(
        typing.cast(contract.DatetimeFacts, _RUN_FACTS), ordinals, pinned, lows, highs,
        DAY, 1, 1, _held(ordinals), False, "", owed, True,
    )
    return (tuple(ordinals), made)



# --------------------------------------- G7.3's count met past the strata
#
# WHERE NO PLACEMENT INSIDE THE GAPS REACHES THE COUNT (the orchestrator's
# call of 2026-09-28, not an owner ruling; the owner may reverse it; plan
# P4-D354). Where even the stack holds more units than the count, the
# ranks take the stack and give units up one at a time: a run of the
# stack's ranks, none pinned, alone on its unit and between two ranks,
# splits -- its lower ranks onto the instant of the rank just below it,
# the rest onto the instant of the rank just above it, each of its own
# standing -- where each lands inside its gap or, being an unpinned rank of
# a shape-drawn tail, strictly beyond its tail's boundary; the split whose
# farthest rank stands least far outside its gap first, then the fewest
# ranks outside, then the lower run, then more ranks down; taken only where
# the count is met and each tail's summed distance and summed square lie
# inside G12.14's window. Asked on hand-built ranks, days as whole
# numbers: each tail given as its ranks from the outermost in, its
# anchor, its unit, its half unit, its side, and the nearest and furthest
# distance each rank is summed over (given here, and where a row needs
# room, wider than a real tail's). The answer is worked out by hand.
STRATA = (
    # (ordinals, pinned, lows, highs, tails, day, distinct, width word, ordinals after)
    #
    # THE COUNT MET, BY THE LEAST AMOUNT. The stack holds days 10, 13, 15,
    # 18 and 20, five of four. Rank 1 onto day 10 or 15 stands two days
    # outside its gap; rank 2 onto day 13 one day, onto 18 three; rank 3
    # onto 15 two, and onto day 20, the boundary's, not at all. Rank 2 goes
    # down: distances 10, 7, 7 and 2 sum to 26 inside 24 to 27, squares to
    # 202 inside 178 to 209.
    ((10, 12, 14, 17, 20), (True, False, False, False, True), (10, 12, 14, 17, 20),
     (10, 13, 15, 18, 20), (((0, 1, 2, 3), 20, 1, 0, True, (10, 7, 5, 2), (10, 8, 6, 3)),),
     1, 4, "", (10, 13, 13, 18, 20)),
    # ONLY WHERE THE STACK HOLDS MORE UNITS THAN THE COUNT. The same ranks
    # asked for five: the stack holds five, a placement inside every gap
    # reaches the count, and nothing moves.
    ((10, 12, 14, 17, 20), (True, False, False, False, True), (10, 12, 14, 17, 20),
     (10, 13, 15, 18, 20), (((0, 1, 2, 3), 20, 1, 0, True, (10, 7, 5, 2), (10, 8, 6, 3)),),
     1, 5, "", (10, 12, 14, 17, 20)),
    # NEVER ONTO THE BOUNDARY'S UNIT. The stack holds days 8, 12 and 13,
    # three of two. Rank 1's day 13 is the boundary's, one day past its gap
    # and not offered; it goes down to day 8, three days past its gap:
    # distances 5 and 5, sum 10 inside 6 to 10, squares 50 inside 26 to 68.
    ((8, 12, 13, 13), (True, False, True, True), (8, 11, 13, 13), (8, 12, 13, 13),
     (((0, 1), 13, 1, 0, True, (5, 1), (8, 2)),), 1, 2, "", (8, 8, 13, 13)),
    # EVERY TAIL'S SUMMED DISTANCE INSIDE ITS WINDOW. The stack holds days
    # 7, 11 (rank 1), 12 (the boundary and the body rank 3) and 15. Rank 1
    # can only go down to day 7, and its tail's distances then sum to 10
    # against a window of 6 to 9: nothing moves.
    ((7, 10, 12, 14, 15), (True, False, True, False, True), (7, 10, 12, 12, 15),
     (7, 11, 12, 15, 15), (((0, 1), 12, 1, 0, True, (5, 1), (7, 2)),), 1, 3, "",
     (7, 10, 12, 14, 15)),
    # ...AND ITS SUMMED SQUARE. The stack holds days 2, 4, 9, 11 and 14.
    # Rank 1 onto day 2 stands one day outside its gap and is taken first;
    # the tail's distances 9, 9 and 2 sum to 20 inside 18 to 21, but their
    # squares to 166 against 134 to 161: nothing moves.
    ((2, 4, 8, 11, 14, 14), (True, False, False, True, False, True), (2, 3, 7, 11, 11, 14),
     (2, 4, 9, 11, 14, 14), (((0, 1, 2), 11, 1, 0, True, (9, 7, 2), (9, 8, 4)),), 1, 4, "",
     (2, 4, 8, 11, 14, 14)),
    # THE LEAST FAR BEFORE THE FEWEST. The stack holds days 6, 11, 13
    # (ranks 2 and 3), 15 and 17. Ranks 2 and 3 both onto day 11 stand one
    # day outside their gaps; rank 1 onto day 13 alone stands two. The two
    # go down: distances 9, 4, 4 and 4 inside the window.
    ((6, 10, 12, 13, 15, 15, 17), (True, False, False, False, True, False, True),
     (6, 10, 12, 12, 15, 15, 17), (6, 11, 13, 13, 15, 17, 17),
     (((0, 1, 2, 3), 15, 1, 0, True, (9, 4, 2, 2), (12, 5, 3, 3)),), 1, 4, "",
     (6, 11, 11, 11, 15, 15, 17)),
    # ...AND THE FEWEST OUTSIDE BEFORE THE LOWER RUN. The stack holds days 7,
    # 10 (ranks 1 and 2), 12, 13 and 14. The run of ranks 1 and 2 splits
    # onto days 7 and 12, each one day outside its gap; rank 3 onto day 10
    # stands one day outside too, alone. Rank 3 goes.
    ((7, 9, 10, 11, 13, 14), (True, False, False, False, True, True), (7, 8, 10, 11, 13, 14),
     (7, 10, 11, 12, 13, 14), (((0, 1, 2, 3), 13, 1, 0, True, (6, 3, 2, 1), (6, 5, 3, 2)),),
     1, 4, "", (7, 10, 10, 10, 13, 14)),
    # MORE RANKS DOWN ON A TIE. The stack holds days 2, 4, 5 and 10. Rank 1
    # stands one day outside its gap on day 2 and on day 5; it goes down,
    # and its tail's distances 8, 8 and 5 lie inside the window, where
    # 8, 5 and 5 would not.
    ((2, 4, 5, 10, 10), (True, False, True, True, True), (2, 3, 5, 10, 10), (2, 4, 5, 10, 10),
     (((0, 1, 2), 10, 1, 0, True, (8, 6, 5), (10, 7, 5)),), 1, 3, "", (2, 2, 5, 10, 10)),
    # OF ITS OWN STANDING. Month-first dates under `first-field-padded`: the
    # 8th of January counts outside the word and the 11th inside it. Rank
    # 1's only offer is the 8th, of the other kind: nothing moves.
    ((_day(1, 8), _day(1, 11), _day(1, 12), _day(1, 12)), (True, False, True, True),
     (_day(1, 8), _day(1, 10), _day(1, 12), _day(1, 12)),
     (_day(1, 8), _day(1, 11), _day(1, 12), _day(1, 12)),
     (((0, 1), _day(1, 12), 1, 0, True, (4, 1), (7, 2)),), 1, 2, "first-field-padded",
     (_day(1, 8), _day(1, 11), _day(1, 12), _day(1, 12))),
    # A BODY RANK NEVER LEAVES ITS GAP. Rank 2's gap of 9 to 10 reaches
    # neither neighbour, days 7 and 12 (a body gap runs from pin to pin, so
    # only a row can give it this one), and it is no tail's: nothing moves.
    ((4, 7, 10, 12), (True, True, False, True), (4, 7, 9, 12), (4, 7, 10, 12),
     (((0,), 7, 1, 0, True, (3,), (3,)),), 1, 3, "", (4, 7, 10, 12)),
    # THE LOWER RUN ON A TIE. The stack holds days 10, 13, 16 and 20. Rank
    # 1 onto day 10 and rank 2 onto day 13 each stand two days outside
    # their gaps; rank 1 goes.
    ((10, 12, 15, 20), (True, False, False, True), (10, 12, 15, 20), (10, 13, 16, 20),
     (((0, 1, 2), 20, 1, 0, True, (10, 7, 4), (12, 8, 5)),), 1, 3, "", (10, 10, 16, 20)),
    # NONE PINNED. Rank 2 is pinned on day 7 though its gap is 6 to 10,
    # which the layout never gives a pin, and the stack puts rank 1 on day
    # 7 beside it. Split, rank 1 would go down to day 4 and rank 2 up to day
    # 10 inside its gap, the count met and the window held; the run holds a
    # pinned rank, so nothing moves.
    ((4, 7, 7, 10), (True, False, True, True), (4, 6, 6, 10), (4, 7, 10, 10),
     (((0, 1), 10, 1, 0, True, (6, 3), (6, 6)),), 1, 2, "", (4, 7, 7, 10)),
    # A PINNED RANK IS STACKED ON ITS OWN INSTANT. Rank 2 is pinned on day
    # 13, its gap 13 to 14. The stack holds 6, 8 and 13; rank 1 goes down
    # one day outside its gap onto day 6.
    ((6, 7, 13), (False, False, True), (5, 7, 13), (6, 8, 14),
     (((0, 1), 13, 1, 0, True, (7, 5), (9, 6)),), 1, 2, "", (6, 6, 13)),
    # STACKED BY THE UPPER ENDS. Rank 2 is pinned on day 12 below rank 1's
    # day 16. Taken by the upper ends, rank 1 joins day 12 and the stack
    # holds two days, as many as the count: nothing moves.
    ((11, 16, 12), (True, False, True), (11, 12, 12), (11, 16, 12),
     (((0,), 12, 1, 0, True, (1,), (3,)),), 1, 2, "", (11, 16, 12)),
    # THE STACK SORTED, EVERY RANK THEN INSIDE ITS GAP. Rank 1's gap of 8 to
    # 9 lies below rank 0's of 10 to 11. Sorted, rank 0 takes day 9, outside
    # its gap: there is no stack, and nothing moves.
    ((10, 8, 12), (False, False, True), (10, 8, 12), (11, 9, 12),
     (((0, 1), 12, 1, 0, True, (1, 1), (4, 4)),), 1, 2, "", (10, 8, 12)),
    # BETWEEN TWO RANKS. The last two ranks share day 18 and nothing stands
    # above them: nothing moves.
    ((15, 16, 20), (True, False, False), (15, 16, 16), (15, 18, 20),
     (((0,), 16, 1, 0, True, (1,), (1,)),), 1, 1, "", (15, 16, 20)),
    # ALONE ON ITS UNIT. The stack puts rank 0 on day 11 with rank 2, the
    # pinned rank 1 between them; rank 2 going up frees no day: nothing moves.
    ((14, 14, 11, 16), (False, True, False, True), (11, 14, 9, 15), (14, 14, 11, 17),
     (((0, 1, 2), 15, 1, 0, True, (1, 1, 4), (4, 1, 6)),), 1, 2, "", (14, 14, 11, 16)),
)


def _strata_missed(settle: typing.Callable[..., object]) -> "list[str]":
    missed = []
    for ordinals, pinned, lows, highs, tails, day, distinct, word, want in STRATA:
        got = _asked(
            settle, list(ordinals), list(pinned), list(lows), list(highs), tails, day,
            distinct, word,
        )
        if got != want:
            missed += [f"strata of {ordinals!r}: {got!r}, the statement gives {want!r}"]
    return missed


def _oracle_strata(module: types.ModuleType) -> typing.Callable[..., object]:
    def settle(ordinals, pinned, lows, highs, tails, day, distinct, word):
        module.count_met_past_the_strata(
            {"format": RUN_MEMBER}, ordinals, pinned, lows, highs, day, 1, 1,
            bool(word), word, distinct, list(tails),
        )
        return tuple(ordinals)

    return settle


def _generator_strata(ordinals, pinned, lows, highs, tails, day, distinct, word):
    generation._count_met_past_the_strata(
        typing.cast(contract.DatetimeFacts, _RUN_FACTS), ordinals, pinned, lows, highs,
        day, 1, 1, bool(word), word, distinct, list(tails),
    )
    return tuple(ordinals)


# ------------------------------------------ G7.3's passes offer no hole
#
# A DAY AN ABSENT SPELLING NAMES IS OFFERED TO NO RANK (the review of
# landing 3b.0, items 2 and 4; plan P4-D358). Every pass of G7.3 and step
# 9 of G7.3b skips such a day wherever it would put a rank on one, a rank
# drawn onto one moves off it before the passes count, and a tail rank no
# pass may move that stands on one adds its day to the count they reach.
# Asked on hand-built ranks, days as whole numbers, each row once with its
# holes; the answer is worked out by hand from that statement, and each
# row's answer with the holes ignored is another, so every row parts the
# rule from its absence.
HOLE_ROWS = (
    # (pass, ordinals, pinned, lows, highs, distinct, holes, ordinals after)
    #
    # A MERGE. Units 10, 12, 14 and 20, one over three: rank 1 is offered
    # day 10 and day 14, both two away, and takes the lower -- unless day 10
    # is a hole, when it takes day 14.
    ("merge", (10, 12, 14, 20), (True, False, False, True), (10, 10, 10, 20),
     (10, 19, 19, 20), 3, (10,), (10, 14, 14, 20)),
    # A FREE UNIT. Units 10, 12 and 20, one short of four: rank 1 shares
    # day 12 and takes the nearest free day, 11 -- or 13 where 11 is a hole.
    ("merge", (10, 12, 12, 20), (True, False, False, True), (10, 10, 10, 20),
     (10, 19, 19, 20), 4, (11,), (10, 13, 12, 20)),
    # AN OFFER IS MADE ONLY WHERE THE NEIGHBOUR STANDS OFF A HOLE. Rank 1
    # stands on the hole at day 12 and merges down onto day 10 first; rank
    # 2 was offered no merge onto rank 1, which stood on the hole when the
    # offers were made, so it merges up onto day 16 rather than onto
    # rank 1's new day 10.
    ("merge", (10, 12, 14, 16, 20), (True, False, False, False, True), (10, 10, 10, 11, 20),
     (10, 13, 19, 19, 20), 3, (12,), (10, 10, 16, 16, 20)),
    # A SPLIT. Ranks 1 and 2 share day 11, their room that day alone: no
    # merge takes them, and the split would send rank 1 down onto day 10
    # and rank 2 up onto day 12 -- but day 10 is a hole, rank 1 has no
    # other way, and the split is not made; the stack then holds three
    # units against the count of two, and nothing moves.
    ("merge", (10, 11, 11, 12), (True, False, False, True), (10, 10, 11, 12),
     (10, 11, 12, 12), 2, (10,), (10, 11, 11, 12)),
    # ...and the same split with day 12, above, the hole: rank 2 has no
    # other way.
    ("merge", (10, 11, 11, 12), (True, False, False, True), (10, 10, 11, 12),
     (10, 11, 12, 12), 2, (12,), (10, 11, 11, 12)),
    # A PAID MERGE, month-first under `first-field-padded`. Rank 4 on 12
    # October has no held day of its own kind in its room and would move
    # onto 8 October, the pinned rank 3's, paid for by rank 1 moving from
    # 5 October onto 18 October -- but 8 October is a hole. No other merge,
    # trade, split or stack meets the count of four, and nothing moves.
    ("merge-widths",
     (_day(10, 3), _day(10, 5), _day(10, 5), _day(10, 8), _day(10, 12), _day(10, 18)),
     (True, False, False, True, False, True),
     (_day(10, 3), _day(10, 4), _day(10, 4), _day(10, 8), _day(10, 8), _day(10, 18)),
     (_day(10, 3), _day(10, 20), _day(10, 20), _day(10, 8), _day(10, 13), _day(10, 18)), 4,
     (_day(10, 8),),
     (_day(10, 3), _day(10, 5), _day(10, 5), _day(10, 8), _day(10, 12), _day(10, 18))),
    # A TRADE OF STANDINGS, month-first under `first-field-padded` (a day
    # of 1 to 9 October is of one width kind, every other day here of the
    # other). Ranks 1 and 2 share 9 October, and their gap's one free day,
    # 10 October, is of the other kind; rank 3, alone on 12 October, could
    # take 7 October, of theirs, so the two would move together -- but
    # 10 October is a hole, and nothing moves.
    ("merge-widths", (_day(10, 8), _day(10, 9), _day(10, 9), _day(10, 12), _day(10, 14)),
     (True, False, False, False, True),
     (_day(10, 8), _day(10, 9), _day(10, 9), _day(10, 7), _day(10, 14)),
     (_day(10, 8), _day(10, 10), _day(10, 10), _day(10, 14), _day(10, 14)), 5, (_day(10, 10),),
     (_day(10, 8), _day(10, 9), _day(10, 9), _day(10, 12), _day(10, 14))),
    # THE STACK. Taken by upper ends, rank 1 stacks the top of its gap,
    # day 14, and rank 2 joins it; with day 14 a hole rank 1 walks down to
    # day 13 and rank 2 joins that. Three units: the count.
    ("stack", (10, 13, 15, 20), (True, False, False, True), (10, 11, 13, 20),
     (10, 14, 16, 20), 3, (14,), (10, 13, 13, 20)),
    # ...NOR JOINS ONE. The pinned rank 0 stands on day 10, a hole, and is
    # stacked first; rank 1, whose gap reaches day 10, stacks its own day
    # 12 rather than join it, so the stack holds three units against the
    # count of two, and nothing moves.
    ("stack", (10, 12, 20), (True, False, True), (10, 10, 20), (10, 12, 20), 2, (10,),
     (10, 12, 20)),
    # ...AND ITS RAISE. Asked for four, the stack holds three and rank 1,
    # sharing day 13, is raised to the nearest free day of its gap: 12,
    # 14 and 12 being holes, day 11.
    ("stack", (10, 13, 15, 20), (True, False, False, True), (10, 11, 13, 20),
     (10, 14, 16, 20), 4, (12, 14), (10, 11, 13, 20)),
    # PAST THE STRATA. The stack puts rank 1 on day 12, below the hole at
    # 13, and holds days 10, 12, 15, 18 and 20; every split on offer leaves
    # a rank two days outside its gap, and rank 1's down onto day 10 is
    # the lower run. With day 13 no hole the stack holds it, and rank 2
    # goes down onto it, one day outside.
    ("strata", (10, 12, 14, 17, 20), (True, False, False, False, True),
     (10, 12, 14, 17, 20), (10, 13, 15, 18, 20), 4, (13,), (10, 10, 15, 18, 20)),
    # ...THE STACK PASSING A HOLE THERE TOO. Rank 3's gap tops at day 18, a
    # hole, so the stack puts it on day 17; the least split is rank 2 down
    # onto day 13, one day outside, and rank 3 stays on day 17.
    ("strata", (10, 12, 14, 17, 20), (True, False, False, False, True),
     (10, 12, 14, 17, 20), (10, 13, 15, 18, 20), 4, (18,), (10, 13, 13, 17, 20)),
    # ...AND NO SPLIT LANDS ON ONE. The stack holds days 10, 13, 17, 19
    # and 20, the pinned rank 0 standing on day 10, a hole. The least
    # splits are rank 1 down onto day 10 and rank 3 down onto day 17,
    # each one day outside its gap; rank 1's is the lower run, but its
    # day is a hole, so rank 3 goes down, and the window holds.
    ("strata", (10, 12, 16, 18, 20), (True, False, False, False, True),
     (10, 11, 16, 18, 20), (10, 13, 17, 19, 20), 4, (10,), (10, 13, 17, 17, 20)),
    # A WIDTH MOVE, month-first under `first-field-padded`: a day of
    # September or from 10 October counts into the word, 1 to 9 October
    # does not. Two of four count and three are owed: rank 2 on 6 October
    # is four days from 10 October and rank 1 on 5 October five from 30
    # September, so rank 2 moves -- unless 10 October is a hole, when its
    # nearest is 11 October, five days off, and rank 1, the lower, moves.
    ("widths", (_day(9, 30), _day(10, 5), _day(10, 6), _day(10, 20)),
     (True, False, False, True), (_day(9, 30), _day(9, 30), _day(9, 30), _day(10, 20)),
     (_day(9, 30), _day(10, 20), _day(10, 20), _day(10, 20)), 3, (_day(10, 10),),
     (_day(9, 30), _day(9, 30), _day(10, 6), _day(10, 20))),
    # THE STEP OFF A HOLE BEFORE THE COUNT. Rank 1 on day 12 moves to day
    # 11, the earlier of two free days; rank 2 on day 13 finds day 12 a
    # hole and moves to day 14. A rank whose gap holds holes alone stays.
    ("off", (10, 12, 13, 20), (True, False, False, True), (10, 11, 11, 20),
     (10, 15, 15, 20), 0, (12, 13), (10, 11, 14, 20)),
    ("off", (10, 12, 20), (True, False, True), (10, 12, 20), (10, 13, 20), 0,
     (12, 13), (10, 12, 20)),
)

# THE STUCK TAIL RANK. Two low-tail ranks and one high-tail rank; ranks 0,
# 2 and 4 are pinned. Days 5, 9 and 15 are holes: rank 0 and rank 4 are
# pinned tail ranks on holes and count, rank 2 is a body rank and rank 3
# is not pinned. Two days.
STUCK_ROWS = (
    # (ordinals, pinned, low rows, high rows, holes, days counted)
    ((5, 7, 9, 12, 15), (True, False, True, False, True), 2, 1, (5, 9, 12, 15), 2),
    ((5, 7, 9, 12, 15), (False, False, True, False, True), 2, 1, (5, 9, 12, 15), 1),
)

# The tail every `strata` row above is summed over: wide enough for both
# rows' answers and for the answers the holes ignored would give.
HOLE_TAILS = (((0, 1, 2, 3), 20, 1, 0, True, (10, 6, 2, 1), (10, 10, 6, 3)),)


def _iso(day: int) -> str:
    return (datetime.date(1970, 1, 1) + datetime.timedelta(days=day)).isoformat()


def _month_first(day: int) -> str:
    date = datetime.date(1970, 1, 1) + datetime.timedelta(days=day)
    return f"{date.month}/{date.day}/{date.year}"


def _hole_missed(asked: typing.Callable[..., object], stuck: typing.Callable[..., object]) -> "list[str]":
    missed = []
    for kind, ordinals, pinned, lows, highs, distinct, holes, want in HOLE_ROWS:
        got = _asked(asked, kind, list(ordinals), list(pinned), list(lows), list(highs), distinct, holes)
        if got != want:
            missed += [f"{kind} of {ordinals!r} beside {holes!r}: {got!r}, the statement gives {want!r}"]
    for ordinals, pinned, low_rows, high_rows, holes, want in STUCK_ROWS:
        got = _asked(stuck, list(ordinals), list(pinned), low_rows, high_rows, holes)
        if got != want:
            missed += [f"stuck of {ordinals!r} beside {holes!r}: {got!r}, the statement gives {want!r}"]
    return missed


def _oracle_hole(module: types.ModuleType) -> "tuple[typing.Callable[..., object], typing.Callable[..., object]]":
    def column(holes, low_rows=0, high_rows=0, member="iso-date"):
        found = {
            "format": member, "resolution": "date", "datetimes_read_at": "local",
            "missing_by_source": {
                _iso(day) if member == "iso-date" else _month_first(day): 1 for day in holes
            },
        }
        if low_rows:
            found["low_tail"], found["high_tail"] = {"rows": low_rows}, {"rows": high_rows}
        return found

    def asked(kind, ordinals, pinned, lows, highs, distinct, holes):
        if kind == "merge":
            module.distinct_pass(column(holes), ordinals, pinned, lows, highs, 1, 1, distinct, False, "")
        elif kind == "merge-widths":
            module.distinct_pass(
                column(holes, member=RUN_MEMBER), ordinals, pinned, lows, highs, 1, 1, distinct,
                True, "first-field-padded",
            )
        elif kind == "stack":
            module.ranks_restacked(
                column(holes), ordinals, pinned, lows, highs, 1, 1, 1, _held(ordinals), False, "", distinct,
            )
        elif kind == "strata":
            module.count_met_past_the_strata(
                column(holes), ordinals, pinned, lows, highs, 1, 1, 1, False, "", distinct, list(HOLE_TAILS),
            )
        elif kind == "widths":
            module.widths_pass(
                column(holes, member=RUN_MEMBER), ordinals, pinned, lows, highs, 1, distinct, 1,
                False, "first-field-padded",
            )
        else:
            module.stepped_off_absent_days(column(holes), ordinals, pinned, lows, highs, 1, 1, 1, False, "")
        return tuple(ordinals)

    def stuck(ordinals, pinned, low_rows, high_rows, holes):
        return len(module.absent_days_stuck(column(holes, low_rows, high_rows), ordinals, pinned, 1, len(ordinals)))

    return asked, stuck


def _generator_hole(kind, ordinals, pinned, lows, highs, distinct, holes):
    facts = typing.cast(contract.DatetimeFacts, _RUN_FACTS)
    gone = frozenset(holes)
    if kind == "merge":
        generation._distinct_reached(facts, ordinals, pinned, lows, highs, 1, 1, distinct, False, "", gone)
    elif kind == "merge-widths":
        generation._distinct_reached(
            facts, ordinals, pinned, lows, highs, 1, 1, distinct, True, "first-field-padded", gone,
        )
    elif kind == "stack":
        generation._ranks_restacked(
            facts, ordinals, pinned, lows, highs, 1, 1, 1, _held(ordinals), False, "", distinct, gone,
        )
    elif kind == "strata":
        generation._count_met_past_the_strata(
            facts, ordinals, pinned, lows, highs, 1, 1, 1, False, "", distinct, list(HOLE_TAILS), gone,
        )
    elif kind == "widths":
        generation._widths_reached(
            facts, ordinals, pinned, lows, highs, 1, 1, distinct, False, "first-field-padded", gone,
        )
    else:
        generation._stepped_off_the_holes(
            facts, ordinals, pinned, lows, highs, 1, 1, 1, False, "", gone, (0, -1),
        )
    return tuple(ordinals)


def _generator_stuck(ordinals, pinned, low_rows, high_rows, holes):
    layout = types.SimpleNamespace(low=types.SimpleNamespace(rows=low_rows), high=types.SimpleNamespace(rows=high_rows))
    return generation._held_by_stuck_tail_ranks(
        ordinals, pinned, frozenset(holes), 1, typing.cast("generation._DateLayout", layout)
    )


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
    "lone_pool": (
        lambda module: _lone_pool_missed(module.marks_of_a_lone_pool),
        lambda: _lone_pool_missed(_shipped_lone_pool),
    ),
    "pool_mark_count": (
        lambda module: _pool_mark_counts_missed(_oracle_pool_mark_count(module)),
        lambda: _pool_mark_counts_missed(generation._pool_mark_count),
    ),
    "trailing": (
        lambda module: _trailing_missed(*_oracle_trailing(module)),
        lambda: _trailing_missed(_shipped_exchange, _shipped_order),
    ),
    "trailing_values": (
        lambda module: _trailing_values_missed(_oracle_trailing_values(module)),
        lambda: _trailing_values_missed(_shipped_trailing_values),
    ),
    "group": (
        lambda module: _group_missed(_oracle_group(module)),
        lambda: _group_missed(_generator_group),
    ),
    "run": (
        lambda module: _run_missed(*_oracle_run(module)),
        lambda: _run_missed(_generator_merge, _generator_trade),
    ),
    "strata": (
        lambda module: _strata_missed(_oracle_strata(module)),
        lambda: _strata_missed(_generator_strata),
    ),
    "hole": (
        lambda module: _hole_missed(*_oracle_hole(module)),
        lambda: _hole_missed(_generator_hole, _generator_stuck),
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
    "lone_pool_uncapped": (
        "lone_pool",
        "    while target >= line and not lone_pool_stands(target, floor, len(spent)):\n"
        "        target -= 1\n",
        "",
    ),
    "lone_pool_capped_by_the_room_less_one": (
        "lone_pool",
        "    while target >= line and not lone_pool_stands(target, floor, len(spent)):\n"
        "        target -= 1\n",
        "    target = min(target, (len(spent) - 1) * room)\n",
    ),
    "lone_pool_no_join": (
        "lone_pool",
        "target = len(grouped) if len(grouped) < pool + line else pool",
        "target = min(len(grouped), pool)",
    ),
    "lone_pool_every_leftover_joins": (
        "lone_pool",
        "target = len(grouped) if len(grouped) < pool + line else pool",
        "target = len(grouped)",
    ),
    "lone_pool_packed_into_the_first_mark_with_room": (
        "lone_pool",
        "key=lambda m: (len(held[m]), spent.index(m))",
        "key=lambda m: (len(held[m]) >= room, spent.index(m))",
    ),
    "lone_pool_a_run_fills_a_mark": (
        "lone_pool", "    most = max(1, line - 2)\n", "    most = room\n",
    ),
    "lone_pool_runs_ignored": (
        "lone_pool",
        "        if runs and values[runs[-1][-1]] == values[i]:\n",
        "        if False:\n",
    ),
    "lone_pool_an_empty_mark_left_empty": (
        "lone_pool", "        if len(held[most]) < 2:\n", "        if True:\n",
    ),
    "pool_mark_count_always_seven": (
        "pool_mark_count",
        "    if list(census) != [\"(withheld)\"]:\n",
        "    if True:\n",
    ),
    "pool_mark_count_fewest_by_the_room_less_one": (
        "pool_mark_count",
        "if lone_pool_stands(pool, floor, k) or k == 7)",
        "if pool <= (k - 1) * (max(2, floor) - 1) or k == 7)",
    ),
    "pool_mark_count_fewest_taken_first": (
        "pool_mark_count",
        "    for count in range(7, least - 1, -1):\n",
        "    for count in range(least, 8):\n",
    ),
    "pool_mark_count_the_fewest_marks_where_none_fits": (
        "pool_mark_count",
        "    return max(held, key=lambda count: (-held[count], count))\n",
        "    return least\n",
    ),
    "pool_mark_count_budget_strict": (
        "pool_mark_count",
        "for text in spelled_with(count)}) <= folded_budget:",
        "for text in spelled_with(count)}) < folded_budget:",
    ),
    "lone_pool_cells_packed": (
        "lone_pool",
        "    picked = plus_cells_by_value(grouped, values, target, True)\n",
        "    picked = grouped[:target]\n",
    ),
    "trailing_exchange_withdrawn": (
        "trailing",
        '        exchanged[taker], exchanged[giver] = "decimal", "plain"\n',
        "        pass\n",
    ),
    "trailing_exchange_spends_the_plus": (
        "trailing",
        '    room = kinds.count(("decimal", False)) - signed\n',
        '    room = kinds.count(("decimal", False))\n',
    ),
    "trailing_exchange_counts_none_held": (
        "trailing",
        '    short = min(count, below.count(True)) - kinds.count(("decimal", True))\n',
        "    short = min(count, below.count(True))\n",
    ),
    "trailing_exchange_donors_first_upward": (
        "trailing",
        '        for i in range(len(values) - 1, -1, -1)\n'
        '        if kinds[i] == ("decimal", False)\n',
        '        for i in range(len(values))\n'
        '        if kinds[i] == ("decimal", False)\n',
    ),
    "trailing_exchange_any_donor": (
        "trailing",
        '        if kinds[i] == ("decimal", False)\n'
        "        and point_free_spelling(values[i], integer_valued) is not None\n",
        '        if kinds[i] == ("decimal", False)\n',
    ),
    "trailing_exchange_nought_below_zero": (
        "trailing",
        "    below = [value < 0 for value in values]\n",
        "    below = [value <= 0 for value in values]\n",
    ),
    "trailing_exchange_any_negative_takes": (
        "trailing",
        '    needing = [i for i, kind in enumerate(kinds) if kind == ("plain", True)]\n',
        '    needing = [i for i, kind in enumerate(kinds) if kind[1] and kind[0] != "decimal"]\n',
    ),
    "trailing_taken_in_the_contract_order": (
        "trailing",
        '        key=lambda pair: pair[0] != "trailing_minus",\n',
        "        key=lambda pair: 0,\n",
    ),
    "trailing_values_no_walk_beside": (
        "trailing_values", "        (beside, REACHABLE[0]),\n", "",
    ),
    "trailing_values_walk_order_with_no_trailing_minus": (
        "trailing_values",
        "        if kept_pointed > 0 and reachable != REACHABLE[0]:\n",
        "        if reachable != REACHABLE[0]:\n",
    ),
    "trailing_values_last_walk_in_stratum_order": (
        "trailing_values",
        "        if kept_pointed > 0 and reachable != REACHABLE[0]:\n",
        "        if False:\n",
    ),
    "trailing_values_negative_walk_in_stratum_order": (
        "trailing_values",
        "        if kept_pointed > 0 and reachable != REACHABLE[0]:\n",
        "        if kept_pointed > 0 and reachable == REACHABLE[1]:\n",
    ),
    "trailing_values_most_negative_first": (
        "trailing_values",
        "            walk += negative[::-1]\n",
        "            walk += negative\n",
    ),
    "trailing_values_beside_asks_for_every_point_free_cell": (
        "trailing_values",
        "        min(wanted - max(0, negative_cells - kept_pointed), free)\n",
        "        min(wanted, free)\n",
    ),
    "trailing_values_non_negative_descending": (
        "trailing_values",
        "            walk = [index for index in walk if index not in negative]\n",
        "            walk = [index for index in walk if index not in negative][::-1]\n",
    ),
    "readings_by_code_first": (
        "readings",
        "return [published] + sorted(candidates, key=moved_then_counts)",
        "return [published] + sorted(candidates, key=lambda pair: (pair[1], pair[0]))",
    ),
    # G7.3b step 9 (the second skeptic of landing 3b.0): O1 and O2 are the
    # two it measured leaving every vectors file byte-identical.
    "group_outer_unit_first": (
        "group",
        "for _gap, d, _order, name in sorted(offered):",
        "for _gap, d, _order, name in sorted(offered, key=lambda o: (o[0], -o[1], o[2])):",
    ),
    "group_gives_its_last_rank": (
        "group",
        "        if len(chosen[name]) + 2 > tails[name][1]:\n",
        "        if len(chosen[name]) + 1 > tails[name][1]:\n",
    ),
    "group_smallest_distance_first": (
        "group",
        "for _gap, d, _order, name in sorted(offered):",
        "for _gap, d, _order, name in sorted(offered, key=lambda o: (o[1], o[0], o[2])):",
    ),
    "group_high_tail_first_on_a_tie": (
        "group",
        "for _gap, d, _order, name in sorted(offered):",
        "for _gap, d, _order, name in sorted(offered, key=lambda o: (o[0], o[1], -o[2])):",
    ),
    "group_outer_units_smallest_outermost": (
        "group",
        "outer = sorted((d for d in chosen[name] if d > group), reverse=True)",
        "outer = sorted(d for d in chosen[name] if d > group)",
    ),
    "group_inner_units_largest_innermost": (
        "group",
        "inner = sorted(d for d in chosen[name] if d < group)",
        "inner = sorted((d for d in chosen[name] if d < group), reverse=True)",
    ),
    # G7.3's merges (the fix pass of landing 3b.0). The room asked of the
    # run's first rank alone, everywhere; then each place on its own. The
    # neighbour offered at the start of a round needs no mutant of its own:
    # it is asked again when its turn comes, and a neighbour cannot move
    # INTO the room between -- it moves onto a held unit, and every held
    # unit between it and the run is the run's own.
    "run_room_of_the_first_rank": (
        "run",
        "    return max(lows[first:last + 1]), min(highs[first:last + 1])\n",
        "    return lows[first], highs[first]\n",
    ),
    "run_held_unit_looked_for_past_the_room": (
        "run",
        "ordinals[first], low, high, unit, held, spot, standing,",
        "ordinals[first], lows[first], highs[first], unit, held, spot, standing,",
    ),
    "run_neighbour_read_again_past_the_room": (
        "run",
        "            low, high = run_room(lows, highs, first, first + size - 1)\n",
        "            low, high = lows[first], highs[first]\n",
    ),
    "run_trade_looked_for_past_the_room": (
        "run",
        "                room = run_room(lows, highs, first, last)\n",
        "                room = (lows[first], highs[first])\n",
    ),
    # The split of a run no merge can take (the third skeptic of landing
    # 3b.0): withdrawn, made where the room holds a held unit, made out of
    # rank order, made onto a unit of the other standing, made in part.
    "run_split_withdrawn": (
        "run", "            split = runs_split(\n", "            split = 0 and runs_split(\n",
    ),
    "run_split_past_a_held_unit_in_the_room": (
        "run",
        "            and nearest_held_unit(\n"
        "                ordinals[first], *run_room(lows, highs, first, last), unit, held, spot, standing,\n"
        "            ) is None\n",
        "",
    ),
    "run_split_out_of_order": (
        "run",
        "if above not in goes and fits(rank, below):",
        "if fits(rank, below):",
    ),
    "run_split_of_any_standing": (
        "run",
        "return lows[rank] <= target <= highs[rank] and standing(ordinals[rank], target)",
        "return lows[rank] <= target <= highs[rank]",
    ),
    "run_split_in_part": (
        "run",
        "            if len(goes) == size:\n",
        "            if goes:\n",
    ),
    # The fourth skeptic's two unwitnessed clauses of the split: made of a
    # run that shares its unit with a rank elsewhere, and made past the
    # count owed.
    "run_split_of_a_shared_unit": (
        "run", " and held[own] == size\n", "\n",
    ),
    "run_split_past_the_count": (
        "run", "    while first < parsed and made < owed:\n", "    while first < parsed:\n",
    ),
    # The stack of the ranks where no one run can give a unit up (the
    # fourth skeptic): withdrawn, taken short of the count, stacked at the
    # lower ends, stacked in rank order, of any standing, and of a pinned
    # rank by its gap.
    "restack_withdrawn": (
        "run",
        "        if count > distinct and not changed and ranks_restacked(\n",
        "        if count > distinct and False and ranks_restacked(\n",
    ),
    "restack_out_of_order": (
        "run", "    sort_unpinned_runs(placed, pinned)\n", "",
    ),
    "restack_past_a_gap": (
        "run",
        "    if any(not low <= placed[r] <= high for r, (low, high) in enumerate(bounds)):\n"
        "        return False\n",
        "",
    ),
    "restack_taken_short_of_the_count": (
        "run",
        "    if len(now) != distinct:\n        return False\n    ordinals[:] = placed\n",
        "    ordinals[:] = placed\n",
    ),
    "restack_at_the_lower_ends": (
        "run",
        "        candidate = ordinals[rank] + (high - ordinals[rank]) // by * by\n"
        "        while candidate >= low and (stands(candidate) != own or not may_hold(rank, candidate)):\n"
        "            candidate -= by\n"
        "        if candidate < low:\n",
        "        candidate = ordinals[rank] - (ordinals[rank] - low) // by * by\n"
        "        while candidate <= high and (stands(candidate) != own or not may_hold(rank, candidate)):\n"
        "            candidate += by\n"
        "        if candidate > high:\n",
    ),
    "restack_in_rank_order": (
        "run",
        "    order = sorted((bounds[r][1], bounds[r][0], r) for r in range(len(ordinals)))\n",
        "    order = sorted((r, bounds[r][0], r) for r in range(len(ordinals)))\n",
    ),
    "restack_of_any_standing": (
        "run",
        "    def stands(value):\n        return standing_of(column, value, day, step, widths, word)\n",
        "    def stands(value):\n        return (False, False)\n",
    ),
    "restack_of_a_pinned_rank_by_its_gap": (
        "run",
        "    bounds = [(ordinals[r], ordinals[r]) if pinned[r] else (lows[r], highs[r]) for r in range(len(ordinals))]\n",
        "    bounds = [(lows[r], highs[r]) for r in range(len(ordinals))]\n",
    ),
    "restack_raised_from_the_top": (
        "run",
        "    for rank in range(len(ordinals)):\n        if len(now) >= distinct:\n",
        "    for rank in reversed(range(len(ordinals))):\n        if len(now) >= distinct:\n",
    ),
    # The raise's own clauses (the fifth skeptic): raised past the gap,
    # onto a day of either width kind, a pinned rank raised, and a rank
    # alone on its unit raised.
    "restack_raised_past_the_gap": (
        "run",
        "            column, placed[rank], lows[rank], highs[rank], day, step, unit, now, widths,\n",
        "            column, placed[rank], lows[rank] - 2 * unit, highs[rank] + 2 * unit, day, step, unit, now, widths,\n",
    ),
    "restack_raised_of_any_width": (
        "run",
        "            column, placed[rank], lows[rank], highs[rank], day, step, unit, now, widths,\n"
        "            stands(placed[rank]), True, word,\n",
        "            column, placed[rank], lows[rank], highs[rank], day, step, unit, now, False,\n"
        "            (False, stands(placed[rank])[1]), True, word,\n",
    ),
    "restack_raised_a_pinned_rank": (
        "run",
        "        if pinned[rank] or now[placed[rank] // unit] < 2:\n            continue\n        found = nearest_free_where(",
        "        if now[placed[rank] // unit] < 2:\n            continue\n        found = nearest_free_where(",
    ),
    "restack_raised_a_rank_alone": (
        "run",
        "        if pinned[rank] or now[placed[rank] // unit] < 2:\n            continue\n        found = nearest_free_where(",
        "        if pinned[rank] or now[placed[rank] // unit] < 1:\n            continue\n        found = nearest_free_where(",
    ),
    # The raise onto the nearest FREE unit: a unit an earlier raise took is
    # no longer free (the landing's sixth skeptic).
    "restack_raised_onto_a_taken_unit": (
        "run", "        now[found // unit] = 1\n", "        now[found // unit] = 0\n",
    ),
    # The count met past the strata, clause by clause (the orchestrator's
    # call of 2026-09-28, plan P4-D354).
    "strata_withdrawn": (
        "strata",
        '    kind = [standing_of(column, value, day, step, widths, word) for value in ordinals]\n',
        '    return False\n    kind = [standing_of(column, value, day, step, widths, word) for value in ordinals]\n',
    ),
    "strata_where_the_stack_reaches_the_count": (
        "strata",
        '    if len(held) <= distinct:\n        return False\n',
        '',
    ),
    "strata_from_the_ranks_as_they_stand": (
        "strata",
        '    held = {}\n    for value in laid:\n',
        '    laid = list(ordinals)\n    held = {}\n    for value in laid:\n',
    ),
    "strata_a_body_rank_leaves": (
        "strata",
        '        beyond = rank in tail_of and ',
        '        beyond = rank not in tail_of or ',
    ),
    "strata_onto_the_boundary": (
        "strata",
        '*tail_of[rank][1:5]) > 0\n',
        '*tail_of[rank][1:5]) >= 0\n',
    ),
    "strata_farthest_first": (
        "strata",
        'offers.append(((max(costs), sum(1 for c in costs if c > 0), start, -down), start, goes))',
        'offers.append(((-max(costs), sum(1 for c in costs if c > 0), start, -down), start, goes))',
    ),
    "strata_fewest_outside_first": (
        "strata",
        'offers.append(((max(costs), sum(1 for c in costs if c > 0), start, -down), start, goes))',
        'offers.append(((sum(1 for c in costs if c > 0), max(costs), start, -down), start, goes))',
    ),
    "strata_any_number_outside": (
        "strata",
        'offers.append(((max(costs), sum(1 for c in costs if c > 0), start, -down), start, goes))',
        'offers.append(((max(costs), 0, start, -down), start, goes))',
    ),
    "strata_the_higher_run_first": (
        "strata",
        'offers.append(((max(costs), sum(1 for c in costs if c > 0), start, -down), start, goes))',
        'offers.append(((max(costs), sum(1 for c in costs if c > 0), -start, -down), start, goes))',
    ),
    "strata_more_ranks_up": (
        "strata",
        'offers.append(((max(costs), sum(1 for c in costs if c > 0), start, -down), start, goes))',
        'offers.append(((max(costs), sum(1 for c in costs if c > 0), start, down), start, goes))',
    ),
    "strata_of_any_standing": (
        "strata",
        '        same = standing_of(column, target, day, step, widths, word) == standing_of(column, laid[rank], day, step, widths, word)\n',
        '        same = True\n',
    ),
    "strata_a_shared_unit": (
        "strata",
        '\n                and held[laid[start] // unit] == len(run)\n',
        '\n',
    ),
    "strata_a_pinned_rank_split": (
        "strata",
        '                not any(pinned[rank] for rank in run)\n',
        '                True\n',
    ),
    "strata_the_sum_unwindowed": (
        "strata",
        '        if not sum(near) <= sum(away) <= sum(far):\n            return False\n',
        '',
    ),
    "strata_the_square_unwindowed": (
        "strata",
        '        if not sum(d * d for d in near) <= sum(d * d for d in away) <= sum(d * d for d in far):\n            return False\n',
        '',
    ),
    "strata_stacked_in_rank_order": (
        "strata",
        'key=lambda r: (room[r][1], room[r][0], r)',
        'key=lambda r: r',
    ),
    "strata_stacked_at_the_lower_ends": (
        "strata",
        'for c in range(top, low - 1, -by)',
        'for c in range(low, top + 1, by)',
    ),
    "strata_stack_unsorted": (
        "strata",
        '    sort_unpinned_runs(laid, pinned)\n    if not all(',
        '    if not all(',
    ),
    "strata_a_pinned_rank_stacked_by_its_gap": (
        "strata",
        '    room = [(value, value) if fixed else (low, high) for value, fixed, low, high in zip(ordinals, pinned, lows, highs)]\n',
        '    room = [(low, high) for value, fixed, low, high in zip(ordinals, pinned, lows, highs)]\n',
    ),
    "strata_stack_past_a_gap": (
        "strata",
        '    if not all(low <= value <= high for value, (low, high) in zip(laid, room)):\n        return False\n',
        '',
    ),
    "strata_between_two_ranks": (
        "strata",
        '                and start > 0 and stop + 1 < size_of\n',
        '                and start > 0\n',
    ),
    "group_takes_past_the_count": (
        "group",
        "        if owed == 0:\n            break\n        if len(chosen[name]) + 2",
        "        if len(chosen[name]) + 2",
    ),
}

# The hole clauses (plan P4-D358): each withdrawn alone turns `hole` red.
WITNESS_MUTANTS.update({
    "hole_a_merge_onto_a_hole": (
        "hole", "        if target // unit in absent:\n            return False\n", "",
    ),
    "hole_a_free_unit_on_a_hole": (
        "hole", "            if candidate // unit in absent:\n                continue\n", "",
    ),
    "hole_stacked_on_a_hole": (
        "hole",
        "    def may_hold(rank, value):\n        return pinned[rank] or value // unit not in absent\n",
        "    def may_hold(rank, value):\n        return True\n",
    ),
    "hole_split_past_the_strata_onto_a_hole": (
        "hole", "        same = same and target // unit not in absent\n", "",
    ),
    "hole_stacked_past_the_strata_on_a_hole": (
        "hole",
        "    def lands(rank, value):\n        return pinned[rank] or value // unit not in absent\n",
        "    def lands(rank, value):\n        return True\n",
    ),
    "hole_a_width_move_onto_a_hole": (
        "hole",
        "                counts_into_width(column, candidate // day, word) != fewer\n"
        "                and candidate // unit not in absent\n",
        "                counts_into_width(column, candidate // day, word) != fewer\n",
    ),
    "hole_a_paid_merge_onto_a_hole": (
        "hole",
        "                            candidate // unit not in seen\n"
        "                            and candidate // unit not in absent\n",
        "                            candidate // unit not in seen\n",
    ),
    "hole_no_step_off_before_the_count": (
        "hole", "        if found is not None:\n            ordinals[rank] = found\n", "",
    ),
    "hole_stuck_counted_unpinned": (
        "hole",
        "if pinned[rank] and ordinals[rank] // unit in absent and not first <= rank <= last",
        "if ordinals[rank] // unit in absent and not first <= rank <= last",
    ),
    "hole_stuck_counted_in_the_body": (
        "hole",
        "if pinned[rank] and ordinals[rank] // unit in absent and not first <= rank <= last",
        "if pinned[rank] and ordinals[rank] // unit in absent",
    ),
})


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


# ------------------------------------------ the tail bound at both ends of the range
#
# Method G5.3b step 4 bounds the derived end by `d1 + sqrt((m - 1) *
# max(0, rms**2 - d1**2))`, TAKEN AS `rms` TIMES A FRACTION,
# `d1 + rms * sqrt((m - 1) * max(0, 1 - (d1 / rms)**2))`. The two are the
# same number in exact arithmetic and NOT the same number in binary64:
# `rms * rms` underflows to nought below about 1e-162 and overflows above
# about 1e154, and the squared form then returns `d1` itself or an
# infinity. No frozen case reaches either end of that range -- every
# committed tail stands at an ordinary scale -- so the clause could be
# written either way with all eleven vectors files unchanged, which is
# the gap the governance pass of stage 3's review named (item 2).
#
# THE EXPECTATION IS DERIVED AND NOT COPIED. `_exact_bound` works the
# clause in exact rationals with a whole-number square root, which is a
# different arithmetic from the oracle's binary64 one, and the witness
# asks that the two agree to within four units in the last place. The
# scale defect is a factor of six, not a last place.

TAIL_BOUNDS = (
    # (rows, mean distance, root-mean-square, why this row is here)
    (12, 1.0, 2.0, "an ordinary scale, where either form works"),
    (12, 1e-200, 2e-200, "below where `rms * rms` underflows to nought"),
    (12, 1e200, 2e200, "above where `rms * rms` overflows to infinity"),
    (12, 5e-324, 1e-323, "the smallest numbers this format holds at all"),
    (2, 3.0, 3.0, "a JUMP tail: every row at one distance, so the bound is `d1`"),
    (12, 0.0, 0.0, "a FLAT tail, whose bound is nought"),
    (1, 7.0, 9.0, "one row, where the square root is over nought rows"),
)


def _exact_bound(rows: int, mean: float, root: float) -> float:
    """G5.3b step 4's bound in exact rationals, rounded once at the end."""
    spread = fractions.Fraction(root) ** 2 - fractions.Fraction(mean) ** 2
    if spread < 0:
        spread = fractions.Fraction(0)
    under = fractions.Fraction(rows - 1) * spread
    guard = 2 * (200 + max(0, under.denominator.bit_length()))
    scaled = (under.numerator << guard) // under.denominator
    whole = math.isqrt(scaled)
    return float(
        fractions.Fraction(mean)
        + fractions.Fraction(whole, 1) / fractions.Fraction(2) ** (guard // 2)
    )


def _bounds_missed(rule: typing.Callable[..., object]) -> "list[str]":
    missed = []
    for rows, mean, root, why in TAIL_BOUNDS:
        found = _asked(rule, rows, mean, root)
        wanted = _exact_bound(rows, mean, root)
        if not isinstance(found, float) or not math.isfinite(found):
            missed += [f"bound of ({rows}, {mean!r}, {root!r}): {found!r} ({why})"]
            continue
        gap = abs(found - wanted)
        if gap > abs(wanted) * 2.0**-50:
            missed += [
                f"bound of ({rows}, {mean!r}, {root!r}): {found!r}, and the "
                f"clause worked in exact rationals gives {wanted!r} ({why})"
            ]
    return missed


def test_the_oracle_s_tail_bound_holds_at_every_supported_scale() -> None:
    """Every row of `TAIL_BOUNDS`, asked of the oracle as committed."""
    assert _bounds_missed(ORACLE_MODULE.tail_bound) == []


# The squared form, which is the arithmetic the clause replaced. It is
# the whole of the defect: at 1e-200 it returns the mean distance itself.
_SQUARED_BOUND = (
    """    share = 0.0
    if root > 0.0:
        ratio = mean / root
        if ratio < 1.0:
            share = 1.0 - ratio * ratio
    bound = mean + root * math.sqrt((rows - 1) * share)
""",
    """    spread = root * root - mean * mean
    if not spread > 0.0:
        spread = 0.0
    bound = mean + math.sqrt((rows - 1) * spread)
""",
)


def test_the_tail_bound_witness_fails_on_the_squared_form() -> None:
    """And the witness can fail: the squared form put back, one edit.

    A guard nobody has watched fail is a guard nobody knows the reach
    of. The edit is the text the clause used to carry, and it stands in
    the oracle exactly once.
    """
    before, after = _SQUARED_BOUND
    assert SOURCE.count(before) == 1
    mutated = _oracle(SOURCE.replace(before, after))
    missed = _bounds_missed(mutated.tail_bound)
    assert missed != []
    assert any("1e-200" in line for line in missed), missed
