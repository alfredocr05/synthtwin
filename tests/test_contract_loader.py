"""The strict loader, one refused document per rule (P2-D2).

The contract is `docs/spec/profile-contract-v5.md`, which carries
version 4 by reference. A loader that only
ever ACCEPTS good documents proves nothing: the whole of its value is
what it refuses, so this file is written the other way round. One
conforming description is built by the real producer, and every rule the
loader enforces gets at least one copy of that description with exactly
one thing wrong, which must be refused, with a message that names the
rule that was broken.

THE VACUITY FLOOR, which is the part that makes the battery mean
something. A mutation battery passes trivially in three ways, and each
of the three is closed here by a test of its own:

* the base could be refused already, so nothing the mutations do
  matters. `test_the_base_document_loads` and
  `test_every_mutation_starts_from_a_document_that_loads` refuse that.
* a mutation could change nothing, so the refusal is the base's own.
  `test_every_mutation_changes_the_document` refuses that.
* a mutation could be refused for a DIFFERENT reason than the rule it is
  filed under -- which is how a battery comes to say a rule is enforced
  when it is not. Every entry therefore states the words that must
  appear in the refusal, and for an invariant those words come from
  `contract.INVARIANTS`, which the loader itself raises with. A rule
  enforced by a message that names something else fails here.

`test_every_invariant_the_loader_names_has_a_mutation` closes the last
gap: the battery is compared against the loader's own list of rules, so
a rule added to the loader without a document that must be refused fails
this file.

WHAT THE BATTERY DOES NOT COVER, and why, is the comment above
`contract.INVARIANTS`: rules refused as a key, a range or a version
instead of as an invariant are covered here too, under their refusal
number from contract section 10.7, and rules that cannot be broken on
their own are named there with the rules that imply them.

The tables here are built by the seeded neutral builders in
`fixtures.py`; no data-format file is committed (plan D13).
"""

import copy
import dataclasses
import json
import pathlib
import typing

import pytest

import fixtures
from synthtwin import (
    canonical,
    contract,
    errors,
    profile,
    reading,
    taxonomy,
    workbook,
)

Document = dict[str, typing.Any]
Change = typing.Callable[[Document], None]


# -- one conforming description, built by the real producer -----------


def table_text() -> str:
    """A neutral table with one column for every role in the taxonomy.

    The builder in `fixtures` covers most of them; a column of numbers
    no binary64 can hold is added here so the unrepresentable role is
    covered too, and so that the battery has a block of every shape to
    damage.

    A JOINED column is added for the same reason and needs a
    declaration to be one. Without it this battery had no `JoinedFacts`
    block at all, so the loader's own rules about that role -- the
    range its rank agreements lie in, the length of its per-position
    widths -- could be deleted with every mutation here still green
    (review item P4-A2-R4-F3).

    A column of dates AND times in two offsets is added for the same
    reason. The builder's own column of dates carries no time of day,
    so a document made from it alone can break no rule about a seconds
    field or a shared clock, and D10 had no description to be broken by
    (review item P2-C3-F2).
    """
    lines = [line for line in fixtures.every_role_table().split("\n") if line]
    joined = fixtures.joined_column_text()
    rows = [f"{lines[0]},huge,logged_at,{fixtures.JOINED_COLUMN}"]
    for index, line in enumerate(lines[1:]):
        huge = "1e999" if index % 2 else "-2e400"
        offset = "+02:00" if index % 2 else "-05:00"
        stamp = (
            f"2024-{(index % 12) + 1:02d}-{(index % 28) + 1:02d} "
            f"{index % 24:02d}:{(index * 11) % 60:02d}:"
            f"{(index * 7) % 59 + 1:02d}{offset}"
        )
        rows.append(f"{line},{huge},{stamp},{joined[index]}")
    return "\n".join(rows) + "\n"


@pytest.fixture(scope="module")
def base(tmp_path_factory: pytest.TempPathFactory) -> Document:
    """The conforming description every mutation starts from.

    THE FLOOR IS DECLARED HERE RATHER THAN LEFT TO THE DEFAULT, which
    is now one (owner ruling, plan amendment A-P4-37). At a floor of one
    NOTHING is ever held back -- no pooled `(withheld)` key, no
    `suppressed_levels`, no `variants_withheld`, no unpublished
    tally -- and this battery is written against a description that
    HOLDS THINGS BACK: a whole family of rules here (B4, B5, C5-N3,
    C5-N4, W5, V1, D3, P2, P6, P6b, P8, SF1, LT1) can only be broken by
    damaging a pool or a held-back size, and those keys have to exist
    in the base before a mutation can damage one. Eleven is the floor
    the battery's arithmetic was sized for, and asking for it keeps
    every entry exercising the rule it is filed under. The two entries
    that are ABOUT the floor of one lower it themselves, from here.
    """
    folder = tmp_path_factory.mktemp("contract")
    path = fixtures.write(folder, "table.csv", table_text())
    table = reading.read_table(str(path))
    document = profile.build_document(
        table,
        taxonomy.Settings(small_cell_floor=11),
        ["record_code"],
        [],
        [fixtures.JOINED_COLUMN],
    )
    return json.loads(json.dumps(document))


def written(folder: pathlib.Path, document: Document) -> str:
    """Write a description in canonical bytes; return its path."""
    return str(fixtures.write_profile(folder, "table-profile.json", document))


def refusal(folder: pathlib.Path, document: Document) -> str:
    """Load a description that must be refused; return the message."""
    with pytest.raises(errors.ProfileError) as raised:
        contract.load_profile(written(folder, document))
    return f"{raised.value}"


def refusal_of_text(folder: pathlib.Path, text: str) -> str:
    """Load a file of exact text that must be refused; return the message.

    The bytes are the test's own and do NOT come through
    `fixtures.write_profile`: every caller here is proving that the
    loader refuses a file synthtwin would never have written, so the
    text has to reach the disk exactly as it was composed. ``newline``
    is passed for that reason -- with no newline argument the platform
    would rewrite the line endings and the file would carry bytes no
    caller asked for.
    """
    target = folder / "table-profile.json"
    target.write_text(text, encoding="utf-8", newline="")
    with pytest.raises(errors.ProfileError) as raised:
        contract.load_profile(str(target))
    return f"{raised.value}"


def at(document: Document, name: str) -> Document:
    """The block of the column called ``name``."""
    for block in document["columns"]:
        if block["name"] == name:
            return typing.cast(Document, block)
    raise AssertionError(f"the base description has no column {name}")


# -- the small mutators the battery is written from -------------------


def edit(_column: str, **changes: object) -> Change:
    """Replace keys of one column's block.

    The column's own name is spelled with a leading underscore so that a
    mutation may set the key called `name` without the two colliding.
    """
    def change(document: Document) -> None:
        at(document, _column).update(changes)
    return change


def whole_dates_carrying_offsets(_column: str) -> Change:
    """Read a column of stamps jointly, every value a whole date (D16).

    Its offsets stay the two real ones the stamps carried, so the whole
    dates would each have to wear one, which no whole date can.
    """
    def change(document: Document) -> None:
        block = at(document, _column)
        parsed = int(block["n_present"]) - int(block["n_unparsed"])
        block.update(
            format="iso-mixed",
            resolution_mix={"iso-date": parsed, "iso-datetime": 0},
            datetime_separators={},
        )
    return change


def wide_runs_on_a_pooled_form(_column: str) -> Change:
    """Claim wide runs where the forms map pools a single point-free cell.

    The column is written `decimal` on every cell, so one of them is
    moved into the withheld remainder: the room for a point-free cell is
    then exactly one, which passes WR1's room clause and is far below
    the floor of eleven this base is written at (plan P4-D91).
    """
    def change(document: Document) -> None:
        block = at(document, _column)
        styles = dict(block["numeric_styles"])
        styles["decimal"] = int(styles["decimal"]) - 1
        styles["(withheld)"] = 1
        block["numeric_styles"] = styles
        block["wide_runs"] = "canonical"
    return change


def counted_past_the_values(_column: str) -> Change:
    """Count more values at midnight than a column has (D15)."""
    def change(document: Document) -> None:
        block = at(document, _column)
        block["n_at_midnight"] = int(block["n_present"]) + 1
    return change


def one_value_at_midnight(_column: str) -> Change:
    """Publish a count of values at midnight of exactly one (D15, landing 2b.6).

    The reviewer's own shape said as a document: a count of one names the
    one person who holds the value, so the loader refuses it however low
    the run's smallest group size is.
    """
    def change(document: Document) -> None:
        block = at(document, _column)
        block["n_at_midnight"] = 1
    return change


def all_but_one_at_midnight(_column: str) -> Change:
    """Publish a count leaving exactly one value off midnight (D15)."""
    def change(document: Document) -> None:
        block = at(document, _column)
        parsed = int(block["n_present"]) - int(block["n_unparsed"])
        block["n_at_midnight"] = parsed - 1
        block["all_at_midnight"] = False
    return change


def nought_at_midnight(_column: str) -> Change:
    """Publish a nought, which stopped being a value of this field (D15)."""
    def change(document: Document) -> None:
        block = at(document, _column)
        block["n_at_midnight"] = 0
    return change


def lower_a_finer_rung(_column: str, _rung: str) -> Change:
    """Push one rung of the finer ladder below the one before it.

    The finer rungs are ninety, so a mutation that rewrote the whole
    map would be a hundred lines of fixture; this reaches into the
    block the producer wrote and moves ONE of them, which is what
    invariant Q19's joint walk is about.
    """
    def change(document: Document) -> None:
        block = at(document, _column)
        finer = dict(block["percentiles_between"])
        finer[_rung] = -1.0e9
        block["percentiles_between"] = finer
    return change


def drop(_column: str, _key: str) -> Change:
    """Take one key out of a column's block."""
    def change(document: Document) -> None:
        del at(document, _column)[_key]
    return change


def edit_top(**changes: object) -> Change:
    """Replace keys at the top of the description."""
    def change(document: Document) -> None:
        document.update(changes)
    return change


def edit_in(_place: str, **changes: object) -> Change:
    """Replace keys inside one top-level block."""
    def change(document: Document) -> None:
        document[_place].update(changes)
    return change


def edit_inside(_column: str, _key: str, **changes: object) -> Change:
    """Replace keys inside one block of one column."""
    def change(document: Document) -> None:
        at(document, _column)[_key].update(changes)
    return change


def edit_level(_column: str, _index: int, **changes: object) -> Change:
    """Replace keys of one published label."""
    def change(document: Document) -> None:
        at(document, _column)["levels"][_index].update(changes)
    return change


def _relabelled_as_a_long_tail(_column: str) -> Change:
    """Give a set of categories the long tail's role and key set.

    The role's key set is the four shared label keys, the form census
    among them (P4-D18), so the relabelling supplies one -- otherwise the
    document is refused for a missing key and never reaches LT2, which
    is the rule this mutation exists to break.
    """
    def change(document: Document) -> None:
        block = at(document, _column)
        block["role"] = "long_tail_labels"
        block["statistical_type"] = "long_tail_labels"
        del block["level_ceiling"]
        block["shape_forms"] = {"(withheld)": block["n_present"]}
    return change


def _long_tail_below_its_line(_column: str) -> Change:
    """Lower the floor, then put every published level under the line.

    The rows the two levels give up are counted among the withheld
    ones, so the sums the label invariants check still hold and G2 is
    the rule the document breaks rather than an arithmetic one.
    """
    def change(document: Document) -> None:
        document["settings"]["small_cell_floor"] = 10
        block = at(document, _column)
        given = 0
        # Both levels take the floor exactly -- ten, which is under the
        # line of eleven and is the smallest a published label may
        # take at this floor (B5) -- and are then put in the order B6
        # asks for, which at equal counts is by name.
        for level in block["levels"]:
            spare = level["count"] - 10
            level["count"] = 10
            level["variants"] = {key: 10 for key in level["variants"]}
            given = given + spare
        block["levels"] = sorted(
            block["levels"], key=lambda level: level["label"]
        )
        # The rows the two levels gave up join a level that was already
        # held back, rather than making a new one: the number of
        # DIFFERENT values did not change, and B2 counts the published
        # and the held-back levels against it.
        block["suppressed_rows"] = block["suppressed_rows"] + given
    return change


def edit_verdict(_column: str, _index: int, **changes: object) -> Change:
    """Replace keys of one decision about a stand-in number."""
    def change(document: Document) -> None:
        at(document, _column)["sentinel_verdicts"][_index].update(changes)
    return change


def both(first: Change, second: Change) -> Change:
    """Two changes that make one broken rule reachable."""
    def change(document: Document) -> None:
        first(document)
        second(document)
    return change


def all_of(*changes: Change) -> Change:
    """Several changes that make one broken rule reachable."""
    def change(document: Document) -> None:
        for one in changes:
            one(document)
    return change


def length_of(_column: str, shortest: int) -> Change:
    """Set the shortest value of a column of text, by that key's name."""
    def change(document: Document) -> None:
        at(document, _column)["length"]["min"] = shortest
    return change


def sixtieth_second(name: str) -> Change:
    """Publish the last second of a leap minute as a column's last value.

    The ladder's own end is moved with it, so that the description
    breaks D10 and not D11: what is under test is the seconds field on
    the shared clock, not the tie between the two ends.
    """
    def change(document: Document) -> None:
        block = at(document, name)
        end = f"{block['latest'][0:17]}60"
        block["latest"] = end
        block["date_percentiles"]["max"] = end
    return change


def flat_ladder(name: str) -> Change:
    """Give a column of numbers the same value at every rung.

    That is how a description SAYS every value the statistics used is
    the same: the ends of the ladder are the smallest and the largest,
    so equal ends leave nothing in between. Three rules are settled by
    it, and each is checked from it.
    """
    def change(document: Document) -> None:
        block = at(document, name)
        block["percentiles"] = {rung: 5.0 for rung in contract.LADDER_KEYS}
        # THE FINER RUNGS GO FLAT WITH THEM (plan P4-D4.10). They are
        # part of the same ladder, so leaving them where they were says
        # a column whose named rungs are all 5 holds a value of 0 at
        # the second percentile -- which invariant Q19 refuses, and the
        # refusal a reader would then see is Q19's rather than the one
        # this mutation exists to reach.
        block["percentiles_between"] = {
            rung: 5.0 for rung in contract.FINER_LADDER_KEYS
        }
    return change


@dataclasses.dataclass(frozen=True)
class Mutation:
    """One document with exactly one thing wrong, and what must be said.

    ``rule`` is the contract's own identifier for an invariant, or the
    refusal number from section 10.7 where the rule is enforced as a
    key, a range or a version instead. ``names`` is the text the refusal
    must contain when the rule is not one the loader raises by name.
    """

    rule: str
    what: str
    change: Change
    names: str = ""

    def expected(self) -> str:
        """The words this mutation's refusal has to contain."""
        if self.rule in contract.INVARIANTS:
            return contract.INVARIANTS[self.rule]
        assert self.names, f"{self.rule} must say what its refusal names"
        return self.names


def battery() -> list[Mutation]:
    """Every rule, with a description that must be refused for it."""
    return [
        # -- the document and its structure ---------------------------
        Mutation("S1", "one column too few", edit_top(n_columns=11)),
        Mutation(
            "S2", "a column that claims another's place",
            edit("region", position=3),
        ),
        Mutation(
            "S4", "two columns of one name",
            edit("visits", name="region"),
        ),
        Mutation(
            "S5", "the fallback flag with the primary encoding",
            edit_in("source", used_fallback_encoding=True),
        ),
        Mutation(
            "S6", "names by convention that came from nowhere",
            edit_in(
                "source", header_source="generated", header_by_convention=True
            ),
        ),
        Mutation(
            "C5-S7", "a description claiming to hold the declared values",
            lambda document: document["settings"]["kept_values"].update(
                {"values_recorded": True}
            ),
        ),
        Mutation(
            "S8", "a declared name that is no column of the table",
            edit_in(
                "settings", forced_identifiers=["record_code", "zzz_missing"]
            ),
        ),
        Mutation(
            # ONE COLUMN, TWO READINGS THAT CANNOT BOTH BE ACTED ON.
            # `amount` is a real continuous column of this fixture, so
            # the name resolves and S8 is satisfied; what is wrong is
            # that a column read as codes is not read as numbers at
            # all, so the comma declaration could never be used and
            # would be recorded and silently ignored (plan P4-D26).
            "S8a", "one column named as codes and as writing commas",
            edit_in(
                "settings",
                forced_codes=["amount"],
                forced_decimal_commas=["amount"],
            ),
        ),
        Mutation(
            "S9", "more categories allowed at the floor than at the ceiling",
            edit_in("settings", categorical_floor=2000),
        ),
        Mutation(
            "S10", "a note about a column that is not there",
            lambda document: document["publication_notes"][0].update(
                {"column": "zzz_missing"}
            ),
        ),
        Mutation(
            "S11", "notes that run backwards through the table",
            edit_top(
                publication_notes=[
                    {"column": "batch", "note": "a note"},
                    {"column": "region", "note": "another note"},
                ]
            ),
        ),
        # THE FLOOR OF ONE, AND WHY THE MUTATION HAS TWO HALVES. At a
        # floor of one there is no group below the floor, so nothing may
        # be held back; the base is written at a floor of eleven, where
        # holding something back is ordinary. So the floor is lowered
        # AND something is left held back -- either half on its own is a
        # description the loader is right to accept. The tally is used
        # rather than a pooled `(withheld)` count because it needs no
        # arithmetic moved with it: it is a count of stand-in numbers
        # too rare to name, and at a floor of one none can be.
        Mutation(
            "C5-S13", "a floor of one that still holds something back",
            all_of(
                edit_in("settings", small_cell_floor=1),
                edit("record_code", n_sentinel_candidates_unpublished=1),
            ),
        ),
        # -- the axes -------------------------------------------------
        Mutation(
            "A1", "a column marked declared that nobody declared",
            edit("visits", structural_role="identifier"),
        ),
        Mutation(
            "A2", "codes in a column nobody declared",
            both(
                edit_in("settings", forced_identifiers=[]),
                edit("record_code", structural_role="data"),
            ),
        ),
        Mutation(
            "A3", "a declared column described as something else",
            both(
                edit_in(
                    "settings", forced_identifiers=["answer", "record_code"]
                ),
                edit("answer", structural_role="identifier"),
            ),
        ),
        Mutation(
            "A4", "a kind and a condition its type path never produces",
            edit("visits", quality_state="empty"),
        ),
        # -- the universal counts -------------------------------------
        Mutation("X1", "one value too many", edit("visits", n_present=230)),
        Mutation(
            "X2", "a value counted as nothing at all",
            edit("visits", n_not_numeric=1),
        ),
        Mutation(
            "X3", "more values ignoring case than there are",
            edit("visits", n_distinct_folded=11),
        ),
        Mutation(
            "X4", "values but nothing different among them",
            edit("visits", n_distinct=0, n_distinct_folded=0),
        ),
        Mutation(
            "N1", "reasons for an empty cell that do not add up",
            lambda document: at(document, "visits")["missing_by_class"].update(
                {"(blank)": 12}
            ),
        ),
        Mutation(
            "N2", "a reason used by too few rows to name",
            lambda document: at(document, "visits")["missing_by_class"].update(
                {"(blank)": 10, "(text-code)": 1}
            ),
        ),
        Mutation(
            "C5-N3", "spellings of an empty cell that do not add up",
            edit("visits", missing_by_source={"zz": 12}),
        ),
        Mutation(
            "C5-N3", "a spelling published by a column that publishes none",
            edit("comment", missing_by_source={"zz": 160}),
        ),
        # THE TWO COUNTS ARE THE SAME ACCOUNTING, so each of them
        # breaks the same rule on its own (contract 5 C5-N3). Version 4
        # kept both inside the map above and could not be damaged
        # separately.
        Mutation(
            "C5-N3", "a blank count larger than the empty cells there are",
            edit("visits", n_missing_blank=12),
        ),
        Mutation(
            "C5-N3", "cells held back on a column that accounts for none",
            edit("comment", n_missing_withheld=3),
        ),
        Mutation(
            "C5-N4", "a spelling written by too few rows to name",
            edit(
                "visits",
                missing_by_source={"zz": 1},
                n_missing_blank=0,
                n_missing_withheld=10,
            ),
        ),
        # AND THE BLANK COUNT IS UNDER THE SAME FLOOR (C5-N4). Version 4
        # exempted its `(blank)` key in the invariant although the
        # producer floored it anyway; version 5 has no exemption left.
        Mutation(
            "C5-N4", "a blank group too small for the floor to name",
            edit("visits", n_missing_blank=1, n_missing_withheld=10),
        ),
        # -- the two vocabulary lists ---------------------------------
        Mutation(
            "C5-K1", "a word in the settings that is nobody's but ours",
            lambda document: document["settings"]["kept_values"].update(
                {"built_in_texts": ["zz"], "n_declared": 1}
            ),
        ),
        Mutation(
            "C5-K3", "more of our own words named than values declared",
            lambda document: document["settings"]["kept_values"].update(
                {"built_in_texts": ["na"]}
            ),
        ),
        Mutation(
            "C5-K4", "one word both kept and read as 'no value'",
            all_of(
                lambda document: document["settings"]["kept_values"].update(
                    {"built_in_texts": ["na"], "n_declared": 1}
                ),
                lambda document: document["settings"][
                    "declared_missing_values"
                ].update({"built_in_texts": ["na"], "n_declared": 1}),
            ),
        ),
        # -- the decisions about stand-in numbers ---------------------
        Mutation(
            "V1", "a stand-in number held by too few rows to name",
            edit_verdict("reading", 0, n_occurrences=5),
        ),
        Mutation(
            "V2", "a withheld candidate on a column that publishes values",
            edit_verdict("reading", 0, candidate="(withheld)"),
        ),
        Mutation(
            "V3", "read as no value for a reason that does not allow it",
            edit_verdict("reading", 0, reason="too_rare"),
        ),
        Mutation(
            "V4", "two decisions in the wrong order",
            lambda document: at(document, "reading").update(
                {
                    "sentinel_verdicts": [
                        at(document, "reading")["sentinel_verdicts"][0],
                        {
                            "candidate": "-1000",
                            "verdict": "kept_as_a_number",
                            "reason": "not_an_outlier",
                            "n_occurrences": 13,
                            "spellings": [],
                        },
                    ]
                }
            ),
        ),
        # THE SPELLINGS A DECISION TOOK OUT (V5, repair pass of landing
        # 2b.6). Both directions of the rule are damaged: a decision
        # naming a spelling this column does not publish among its
        # absent cells, and a decision that KEPT its candidate as a
        # number naming one anyway. Neither is a document the producer
        # can write, and each would tell the generator and the
        # validator that a word the person declared was one column's
        # own judgement -- the mistake this key exists to end.
        Mutation(
            "V5", "a decision naming a spelling the column never published",
            edit_verdict("reading", 0, spellings=["zz"]),
        ),
        Mutation(
            "V5", "a kept candidate naming the spellings it did not take",
            edit_verdict(
                "reading", 0, verdict="kept_as_a_number", reason="too_rare"
            ),
        ),
        # ...and the two parts landing 2b.14 added, which are what make
        # the key CHECKABLE rather than merely published (P4-D95). Each
        # is a document the producer cannot write and the loader used to
        # accept, and each tells both consumers that a word the PERSON
        # DECLARED was one column's own judgement.
        Mutation(
            "V5", "two decisions of one column claiming one spelling's cells",
            lambda document: at(document, "reading").update(
                {
                    "sentinel_verdicts": [
                        at(document, "reading")["sentinel_verdicts"][0],
                        {
                            "candidate": "9999",
                            "verdict": "read_as_missing",
                            "reason": "outlier_and_frequent",
                            "n_occurrences": 13,
                            "spellings": ["-999"],
                        },
                    ]
                }
            ),
        ),
        Mutation(
            "V5", "spellings covering more cells than rows held the candidate",
            edit_verdict("reading", 0, n_occurrences=11),
        ),
        # ...and the OMISSION, which the two above left open (plan
        # P4-D135; review of 158c811, item 6). A judged decision edited to
        # name none of the spellings it took out, beside a pool too small
        # to hold those cells: the link is gone, the validator reads the
        # spelling as a declaration reaching the whole table, and a second
        # column's unchanged values are read as holes.
        Mutation(
            "V5", "a judged decision naming none of the spellings it took out",
            edit_verdict("reading", 0, spellings=[]),
        ),
        # -- the repetition patterns ----------------------------------
        Mutation(
            "M3", "a row count padded to a width nothing needs",
            edit("huge", n_distinct_by_occurrences={"0120": 2}),
        ),
        Mutation(
            "M4", "a size that covers nothing",
            edit("huge", n_distinct_by_occurrences={"120": 0}),
        ),
        Mutation(
            "U3", "a pattern that describes the wrong number of values",
            edit("huge", n_distinct_by_occurrences={"120": 1}),
        ),
        Mutation(
            "I2", "a pattern that covers the wrong number of rows",
            edit("record_code", n_distinct_by_occurrences={"2": 240}),
        ),
        Mutation(
            "F2", "a pattern that describes the wrong number of values",
            edit("comment", n_distinct_by_occurrences={"1": 79}),
        ),
        # -- the eleven rungs --------------------------------------
        Mutation(
            "L1", "a ladder that goes down",
            edit_inside("amount", "percentiles", p05=1000.0),
        ),
        Mutation(
            "L3", "a ladder of dates with nothing at one rung",
            edit_inside("recorded_on", "date_percentiles", p50=None),
        ),
        # -- the empty column -----------------------------------------
        Mutation(
            "E1", "a column called empty that holds every value",
            all_of(
                edit(
                    "unused",
                    n_present=240,
                    n_missing=0,
                    n_distinct=1,
                    n_distinct_folded=1,
                    n_not_numeric=240,
                    missing_by_source={},
                ),
                edit(
                    "unused",
                    missing_by_class={
                        "(blank)": 0,
                        "(declared-missing)": 0,
                        "(numeric-sentinel)": 0,
                        "(text-code)": 0,
                        "(withheld)": 0,
                    },
                ),
            ),
        ),
        # -- numbers this format cannot hold --------------------------
        Mutation("U1", "a whole number counted twice", edit("huge", n_whole=1)),
        Mutation(
            "U2", "a sign counted twice", edit("huge", n_positive=1)
        ),
        # -- the label roles ------------------------------------------
        Mutation(
            "B1", "a published label that was never folded",
            edit_level("region", 0, label="West"),
        ),
        Mutation(
            "B2", "labels that do not account for the different values",
            edit("region", n_distinct_folded=4),
        ),
        Mutation(
            "B3", "labels that do not account for the rows",
            both(
                edit_level("region", 3, count=57),
                lambda document: at(document, "region")["levels"][3].update(
                    {"variants": {"south": 57}}
                ),
            ),
        ),
        Mutation(
            "B4", "labels held back on fewer rows than their number",
            edit("region", suppressed_rows=0),
        ),
        Mutation(
            "B4", "a pool too large to be written below the floor",
            edit("region", suppressed_rows=11),
        ),
        Mutation(
            # B4b, A POOL THAT IS A COUNT OF ONE (the owner's ruling of
            # 2026-09-17, item 5; plan P4-D231). Every rule before it
            # holds: one label covers one row fewer, one label is said
            # to be held back over that one row, and the count of
            # different values rises with it -- so B2, B3, B4 and B5 are
            # all satisfied and what is left is one label on one row,
            # which `n_present` less the published counts reads off.
            # That is the description the producer stopped writing.
            "B4b", "a pool of one label on one row",
            both(
                edit_level("region", 0, count=65),
                both(
                    lambda document: at(document, "region")["levels"][0].update(
                        {"variants": {"west": 65}}
                    ),
                    edit("region", suppressed_rows=1),
                ),
            ),
        ),
        Mutation(
            "B5", "a label published below the floor",
            both(
                edit_level("region", 3, count=5),
                lambda document: at(document, "region")["levels"][3].update(
                    {"variants": {"south": 5}}
                ),
            ),
        ),
        Mutation(
            "B6", "labels out of order",
            lambda document: at(document, "region").update(
                {"levels": list(reversed(at(document, "region")["levels"]))}
            ),
        ),
        Mutation(
            "B7", "the same label twice",
            edit_level("region", 1, label="west"),
        ),
        Mutation(
            "C1", "one value in a column of two",
            edit("answer", role="constant", statistical_type="constant"),
        ),
        Mutation(
            "Y1", "two values in a column of one",
            edit("batch", role="binary", statistical_type="binary"),
        ),
        Mutation(
            "G1", "more categories than the line the column passed",
            edit("region", level_ceiling=2),
        ),
        Mutation(
            # G2 CAN ONLY BE REACHED UNDER A LOWERED FLOOR, and that is
            # the rule rather than a gap in the battery: at this
            # document's floor of eleven every published level covers the
            # long-tail line, because the line IS eleven there. At a
            # floor of ten a column may publish levels of ten, none of
            # which reaches the line -- a document claiming a role its
            # own numbers say the rule would not have given it.
            #
            # TEN AND NOT LESS, because a lowered floor is not simply
            # more permissive: a label the document HOLDS BACK must
            # cover fewer rows than the floor, so dropping the floor to
            # five makes another column's seven-row withheld label
            # illegal and B5 fires before G2 is reached.
            "LT1", "a long tail whose levels never reach its own line",
            _long_tail_below_its_line("note"),
        ),
        Mutation(
            # LT2, and it is the OTHER half of the rule: a document can
            # claim this role for a column that is not past the
            # categorical ceiling at all, whose four label keys are
            # perfectly good ones. Only recomputing the ceiling catches
            # it (review item P4-TAIL-F3).
            "LT2", "a set of categories relabelled as a long tail",
            _relabelled_as_a_long_tail("region"),
        ),
        # -- the spellings of a published label -----------------------
        Mutation(
            "W2", "a spelling filed under the wrong label",
            edit_level("region", 0, variants={"zzz": 59}),
        ),
        Mutation(
            "W3", "a spelling written by more rows than its label",
            edit_level("region", 0, variants={"west": 60}),
        ),
        Mutation(
            "W4", "spellings that do not account for the label's rows",
            edit_level("region", 0, variants={"west": 58}),
        ),
        Mutation(
            "W5", "a spelling named below the floor",
            edit_level(
                "region", 0, variants={"west": 5}, variants_withheld={"54": 1}
            ),
        ),
        Mutation(
            # W5b, A SPELLING ONE ROW WROTE (the owner's ruling of
            # 2026-09-17, item 5; plan P4-D240). Every rule around it
            # holds: the named spelling stays above the floor, the key
            # is inside `1 .. floor - 1` (W5), and the two together
            # still account for every row of the label (W4). What is
            # left is the census saying, in its own definition, that one
            # held-back spelling covered exactly one row -- and a twin
            # then writes that row's spelling in exactly one row.
            "W5b", "a spelling of a label that ONE row wrote",
            edit_level(
                "region", 0, variants={"west": 58}, variants_withheld={"1": 1}
            ),
        ),
        Mutation(
            "W7", "a published label nobody wrote",
            edit_level("region", 0, variants={}, variants_withheld={}),
        ),
        Mutation(
            # W8, on the clause this fixture can break: `west` is
            # letters alone, and a form carries two of the three kinds,
            # so the label has no written form and no spelling of it can
            # wear one (7.4.8, plan amendment A-P4-47). The other two
            # clauses -- the named spellings' own floor and the ceiling
            # the held-back rows set -- are pinned in
            # `tests/test_p4r34_form_census_per_level.py`, where the
            # column carrying a form-bearing label lives.
            "W8", "rows written in a form their label does not have",
            edit_level("region", 0, shape_form_cells=1),
        ),
        # -- the datetime column --------------------------------------
        Mutation(
            "D1", "dates published in a form the reading does not give",
            edit("recorded_on", resolution="quarter"),
        ),
        Mutation(
            "D2", "offsets that do not account for the values that parsed",
            edit("recorded_on", utc_offsets={"(none)": 241}),
        ),
        Mutation(
            "D3", "an offset carried by too few rows to name",
            edit("recorded_on", utc_offsets={"(none)": 239, "+02:00": 1}),
        ),
        # ...AND NO POOL STANDS BESIDE A NAMED OFFSET (plans P4-D220 and
        # P4-D222): three values held back beside 237 with no offset is the
        # count of the rows that wore some other one, and the producer
        # counts such rows into the commonest offset instead.
        Mutation(
            "D3", "a withheld pool of offsets beside a named one",
            edit(
                "recorded_on",
                utc_offsets={"(none)": 237, "(withheld)": 3},
                earliest_utc_offset="(none)",
                latest_utc_offset="(none)",
            ),
        ),
        Mutation(
            "D4", "an endpoint naming an offset the map holds back",
            edit("recorded_on", earliest_utc_offset="+02:00"),
        ),
        Mutation(
            "D5", "two offsets published on the local clock",
            edit("recorded_on", utc_offsets={"(none)": 200, "+02:00": 40}),
        ),
        Mutation(
            "D6", "a detail finer than the published form can hold",
            edit("recorded_on", time_precision="second"),
        ),
        Mutation(
            "D7", "fractions of a second nothing writes",
            edit("recorded_on", subsecond_digits=3),
        ),
        Mutation(
            # THE CENSUS MOVES WITH IT. Since the form census joined
            # the block it counts the values that parsed, so a
            # mutation that makes nothing parse has to empty the
            # census too -- otherwise RM2 refuses the document one
            # rule earlier and D8 is never reached, which would leave
            # D8 with no case at all while this file still looked
            # green.
            "D8", "a column of dates where nothing read as a date",
            edit("recorded_on", n_unparsed=240, resolution_mix={}),
        ),
        Mutation(
            "RM1", "a form census naming a form the column was not read in",
            edit("recorded_on", resolution_mix={"compact-date": 240}),
        ),
        Mutation(
            "RM1", "a form census naming two forms on a single-form column",
            edit(
                "recorded_on",
                resolution_mix={"iso-date": 200, "iso-datetime": 40},
            ),
        ),
        Mutation(
            "RM2", "a form census counting more values than parsed",
            edit("recorded_on", resolution_mix={"iso-date": 241}),
        ),
        Mutation(
            "D9", "an offset on a column that publishes no time of day",
            edit(
                "recorded_on",
                utc_offsets={"+02:00": 240},
                earliest_utc_offset="+02:00",
                latest_utc_offset="+02:00",
            ),
        ),
        Mutation(
            "D10", "a last value the shared clock cannot read back",
            sixtieth_second("logged_at"),
        ),
        Mutation(
            "D10", "ends carrying seconds a column of whole minutes cannot",
            edit("logged_at", time_precision="minute"),
        ),
        Mutation(
            "D11", "a ladder that begins before the column's first value",
            edit_inside(
                "recorded_on", "date_percentiles", min="2023-01-01"
            ),
        ),
        Mutation(
            "D12", "a mark between day and clock named for too few rows",
            edit("logged_at", datetime_separators={"space": 1}),
        ),
        # A POOL OF MARKS STANDS ALONE (plan P4-D220; stage 2 closed by
        # the owner rulings of 2026-09-17). Eleven values held back beside
        # a named mark cleared the bound this replaced -- (floor - 1)
        # times the two unnamed marks -- and told a reader that neither
        # of those marks was nought. `{"(withheld)": 240}`, the witness
        # this replaces, is the whole census and is admitted now.
        Mutation(
            "D12", "a withheld pool beside a named mark",
            edit("logged_at", datetime_separators={"upper_t": 229, "(withheld)": 11}),
        ),
        # A POOL OF EVERY MARK OVER MORE VALUES THAN TWO MARKS HOLD BELOW THE
        # LINE (plan P4-D222): it says each of the three was written, so the
        # producer names the commonest mark there, `{"(withheld)": 240}`
        # included.
        Mutation(
            "D12", "a pool of every mark that says each mark was written",
            edit("logged_at", datetime_separators={"(withheld)": 240}),
        ),
        Mutation(
            "D13", "marks counted on a column that writes no clock",
            edit("recorded_on", datetime_separators={"space": 240}),
        ),
        Mutation(
            "GS1", "a column not declared to write a decimal comma grouped with a point",
            edit("visits", group_separator="."),
        ),
        # The two spelling facts landing 2b.2 added beside the mark.
        Mutation(
            "NS1", "negatives said to wear brackets on a column that holds none",
            edit("visits", negative_form="brackets"),
        ),
        Mutation(
            "DP1", "signed decimals counted on a column with no decimal form",
            edit("visits", decimal_plus={"+": 5}),
        ),
        # ...AND AT THE FLOOR, so only the room clause can refuse it: the
        # case above is caught by the floor clause first, and withdrawing
        # the room check left this battery green (the verification of
        # landing 2b.2).
        Mutation(
            "DP1", "signed decimals counted past the cells the forms map can put in the decimal form",
            edit("visits", decimal_plus={"+": 11}),
        ),
        # The wide-run word landing 2b.13 added beside them (plan
        # P4-D90). Refused by its ROOM clause, which is the only clause
        # of WR1 a conforming word can break: `amount` is written
        # `decimal` on every one of its 240 cells, so the forms map
        # leaves room for no cell written `plain` and no run of figures
        # past 2**53 can be among them. A word outside the three is
        # refused as a range rather than as this invariant.
        Mutation(
            "WR1", "wide runs claimed on a column with no cell written plain",
            edit("amount", wide_runs="canonical"),
        ),
        # ...AND THE POOL OF ONE THAT USED TO WITNESS WR1's FLOOR CLAUSE
        # (landing 2b.13's repair pass, plan P4-D91) is refused before the
        # word is read: a pool below `parsing.census_floor` beside a named
        # form is invariant P6's since plan P4-D221 (stage 2 closed by the
        # owner rulings of 2026-09-17), so the room WR1's floor clause
        # measures is nought, a named form, a pool of the line or more, or
        # the whole numeric count of a column smaller than the floor.
        Mutation(
            "P6", "a pool of one cell beside a named form",
            wide_runs_on_a_pooled_form("amount"),
        ),
        # The two mixture censuses landing 2b.7 added beside them. Each
        # is refused by the clause the other cannot reach: the notations
        # by their POPULATION, which the column's own `n_negative`
        # bounds, and the marks by the CENSUS FLOOR, which is never one
        # however low the smallest group size is set.
        Mutation(
            "NS2", "notations counted on a column that holds no negative number",
            edit("visits", negative_notations={"brackets": 11}),
        ),
        Mutation(
            "TM1", "a mark counted for a single grouped number",
            edit("visits", thousands_marks={",": 1}),
        ),
        Mutation(
            "D14", "a column of whole dates said to stand at midnight",
            edit("recorded_on", all_at_midnight=True),
        ),
        Mutation(
            "D14", "stamps on the shared clock said to stand at midnight",
            edit("logged_at", all_at_midnight=True),
        ),
        Mutation(
            "D15", "more values counted at midnight than the column holds",
            counted_past_the_values("logged_at"),
        ),
        Mutation(
            "D15", "a count of values at midnight on a column that writes no clock",
            edit("recorded_on", n_at_midnight=12),
        ),
        # THE DISCLOSURE FLOOR, landing 2b.6. One is not a group: a count
        # of one names the person holding the value, and a count one short
        # of every value names the person who does not. Nought is refused
        # with them, because a nought a reader can tell from a suppressed
        # singleton IS that singleton.
        Mutation(
            "D15", "a count of values at midnight that names one person",
            one_value_at_midnight("logged_at"),
        ),
        Mutation(
            "D15", "a count leaving exactly one value off midnight",
            all_but_one_at_midnight("logged_at"),
        ),
        Mutation(
            "D15", "a nought where the count is simply not published",
            nought_at_midnight("logged_at"),
        ),
        Mutation(
            "D16", "whole dates counted beside offsets only moments carry",
            whole_dates_carrying_offsets("logged_at"),
        ),
        # HOW THE DATES WERE WRITTEN, landing 2b.6. `recorded_on` is read
        # as `iso-date`: its fields are of fixed width, it writes no
        # month NAME, it is no column of quarters and it names no zulu
        # offset -- so each of the four censuses is a census that column
        # can carry nothing in, and a document that fills one describes a
        # column no producer wrote.
        Mutation(
            "D17", "a width census on a member of fixed field width",
            edit("recorded_on", date_field_widths={"padded": 12}),
        ),
        Mutation(
            "D18", "a month-name census on a column writing no month name",
            edit(
                "recorded_on",
                month_name_styles={"title-abbreviated-space-no-comma": 12},
            ),
        ),
        Mutation(
            "D19", "a quarter-marker census on a column of whole dates",
            edit("recorded_on", quarter_marker_case={"upper": 12}),
        ),
        Mutation(
            "D20", "a zulu-case census where no zulu offset is named",
            edit("recorded_on", zulu_case={"upper": 12}),
        ),
        # -- the numeric roles ----------------------------------------
        Mutation("Q1", "a row count of its own", edit("visits", n_rows=5)),
        Mutation(
            "Q2", "statistics computed from the wrong values",
            edit("visits", n_used_in_statistics=230),
        ),
        Mutation(
            "Q3", "a column of numbers holding none",
            edit("visits", n_numeric=0, n_not_numeric=229),
        ),
        Mutation(
            "Q4", "no spread where there is one to have",
            edit("visits", std=None),
        ),
        Mutation(
            "Q5", "no shape where there is one to have",
            edit("visits", skew=None),
        ),
        Mutation(
            "Q6", "a spread on a column whose values are all the same",
            both(flat_ladder("visits"), edit("visits", skew=None)),
        ),
        Mutation(
            "Q7", "no average on a column whose values are all the same",
            all_of(
                flat_ladder("visits"),
                edit("visits", skew=None, std=0.0, mean=None),
            ),
        ),
        Mutation(
            "Q9", "a share that is not the share of the counts",
            edit("visits", numeric_share=0.5),
        ),
        Mutation(
            "Q10", "more negative values too large to hold than there are",
            edit("visits", n_negative_unrepresentable=5),
        ),
        Mutation(
            "Q11", "more zeroes than numbers", edit("visits", n_zero=230)
        ),
        Mutation(
            "Q15",
            "a shape whose bins do not account for the values",
            edit("visits", value_histogram={"0": 3}),
        ),
        Mutation(
            "Q20",
            "the first bin named as holding nothing",
            edit("visits", empty_bins=[0], value_histogram={}),
        ),
        Mutation(
            "Q21",
            "one pair of stretch edges more than there are stretches",
            edit("visits", empty_edges=[[0.0, 1.0]]),
        ),
        Mutation(
            "Q17",
            "more different numbers than cells that read as one",
            edit("visits", n_distinct_values=900),
        ),
        Mutation(
            "Q16",
            "tails no sample of that many values could have",
            edit("visits", kurtosis=900.0),
        ),
        Mutation(
            "Q19",
            "a finer rung below the rung before it",
            lower_a_finer_rung("visits", "p02"),
        ),
        Mutation(
            "Q18",
            "a commonest number held by more cells than the column has "
            "numbers",
            edit("visits", mode=1.0, mode_count=900),
        ),
        Mutation(
            "P1", "forms that do not account for the numbers",
            edit("visits", numeric_styles={"plain": 228}),
        ),
        Mutation(
            "P2", "a form used by too few cells to name",
            edit("visits", numeric_styles={"plain": 228, "decimal": 1}),
        ),
        Mutation(
            "P3", "a column of numbers saying nothing about their form",
            edit("visits", numeric_styles={}),
        ),
        Mutation(
            "P5",
            "figures after the point counted for cells that wrote none",
            edit("visits", fraction_widths={"2": 40}),
        ),
        # -- the census of padded field widths (P4-D14) --------------
        Mutation(
            "P5b",
            "field widths counted for cells that wrote no padding",
            edit("visits", pad_widths={"5": 40}),
        ),
        Mutation(
            "P6b",
            "a field width written by too few cells to name",
            edit(
                "visits",
                numeric_styles={"plain": 218, "leading_zero": 11},
                pad_widths={"5": 10, "6": 1},
            ),
        ),
        # -- the census of written forms (P4-D18) --------------------
        # Each of these is a document the loader must REFUSE, and each
        # is registered here because a rule the loader raises without
        # an entry in this battery reaches a person as a bare KeyError
        # (review round 1 finding 9).
        # THE KEYS HERE MUST BE FORMS THE PRODUCER COULD WRITE, or the
        # key grammar refuses them before SF1 is reached and the entry
        # names a rule it does not exercise. They were `AAAA` and
        # `AAAAA`, which the two-kinds rule forbids -- the review named
        # it before the alphabet change made it fail loudly (round 2,
        # test weakening 17).
        Mutation(
            "SF1",
            "a written form named by fewer cells than the floor admits",
            edit("region", shape_forms={"@@@-@": 117, "@@@-@@": 3}),
        ),
        # A pooled remainder at a floor of one is refused too, but by
        # C5-S13 at the top of the document rather than by a rule of
        # the census's own -- `shape_forms` is in C5-S13's list, so the
        # census never gets to see it.
        Mutation(
            "C5-S13",
            "a form census holding a pooled remainder at a floor of one",
            all_of(
                edit_in("settings", small_cell_floor=1),
                edit("region", shape_forms={"@@@-@": 1, "(withheld)": 1}),
            ),
        ),
        Mutation(
            "SF3",
            "a census counting more cells than the column has present",
            edit("region", shape_forms={"@@@-@": 117, "@@@-@@": 9999}),
        ),
        # THE CENSUS OF SPELLINGS OF A COUNT COLUMN (contract 7.13,
        # landing 2b.18 part 2, plan P4-D123), on `visits`, the base
        # description's count column: 229 number cells, 22 of them nought.
        Mutation(
            "SC1",
            "a spelling named for fewer cells than the floor admits",
            edit("visits", number_spellings={"07": 3, "7": 226}),
        ),
        Mutation(
            "SC2",
            "a census of spellings that leaves number cells unnamed",
            edit("visits", number_spellings={"07": 11, "7": 11}),
        ),
        Mutation(
            "SC3",
            "a census whose spellings of nought are not the published noughts",
            edit(
                "visits",
                number_spellings={"0": 11, "07": 11, "7": 207},
            ),
        ),
        # ...AND ONLY WHERE THE COLUMN'S VALUES DO NOT FOLD ONTO ONE
        # ANOTHER, which the two published distinct counts say.
        Mutation(
            "SF5",
            "a lower-case form key on a column whose values fold together",
            lambda document: at(document, "region").update(
                {
                    "shape_forms": {"&&&-&": 117},
                    "n_distinct": int(at(document, "region")["n_distinct_folded"])
                    + 1,
                }
            ),
        ),
        # THE LAYOUT CENSUS, on the one role that carries it (contract
        # 7.12, landing 2b.18, plan P4-D120). `record_code` is the base
        # description's declared identifier, so it is the only block
        # these two rules can be broken on.
        #
        # THE KEY HERE MUST BE A LAYOUT THE PRODUCER COULD WRITE, for
        # the reason the form census's own entries carry: a key the
        # grammar refuses is refused BEFORE LF1 is reached, and the
        # entry would then name a rule it does not exercise.
        Mutation(
            "LF1",
            "a layout named by fewer cells than the floor admits",
            edit("record_code", layout_forms={"@%%%%%": 3}),
        ),
        Mutation(
            "LF3",
            "a layout census counting more cells than the column holds",
            edit("record_code", layout_forms={"@%%%%%": 9999}),
        ),
        # THE DISCLOSURE RULE OVER THE WHOLE CENSUS (contract C6-131b,
        # landing 2b.18's repair pass, plan P4-D124). `record_code` holds
        # 240 present cells, all 240 in the code alphabet and none of them
        # figures alone, at a floor of eleven.
        Mutation(
            "LF2",
            "a layout census writing a pool of one cell",
            edit("record_code", layout_forms={"(withheld)": 1, "@%%%%%": 220}),
        ),
        Mutation(
            "LF4",
            "a layout census leaving exactly one present cell over",
            edit("record_code", layout_forms={"@%%%%%": 239}),
        ),
        Mutation(
            "LF5",
            "code-alphabet layouts one cell short of n_code_alphabet",
            edit(
                "record_code",
                layout_forms={"@%%%%%": 229, "@%%.%%": 11},
                n_code_alphabet=230,
            ),
        ),
        Mutation(
            "LF6",
            "a layout census whose keys say two conventions",
            edit("record_code", layout_forms={"@%%%%%": 120, "~~~~~~": 120}),
        ),
        # THE LITERAL PREFIX (contract 7.12a, owner ruling of 2026-09-17,
        # item 1, plan P4-D202). `record_code` is `R` and five figures on
        # 240 rows, so the base description publishes `{"(column)": "R"}`
        # beside `{"@%%%%%": 240}`.
        Mutation(
            "LP1",
            "a prefix for the whole column beside a prefix for a layout",
            edit(
                "record_code",
                layout_prefixes={"(column)": "R", "@%%%%%": "R"},
            ),
        ),
        Mutation(
            "LP1",
            "a prefix for a layout the census does not name",
            edit("record_code", layout_prefixes={"@@%%%%": "RE"}),
        ),
        Mutation(
            "LP2",
            "a prefix whose own layout does not open the census's layout",
            edit("record_code", layout_prefixes={"(column)": "RE"}),
        ),
        # LP3 (plan P4-D270). A prefix fixes characters of the layout it
        # stands on, so the room left has to carry the column's own
        # different values: `R` in front of `@%%` leaves a hundred cells
        # for 240 different record numbers, which spells the column out.
        Mutation(
            "LP3",
            "a prefix leaving its layout too little room for the column",
            edit(
                "record_code",
                layout_forms={"@%%": 240},
                layout_prefixes={"(column)": "R"},
            ),
        ),
        Mutation(
            "LP1",
            "a prefix beside a layout census that names no layout",
            edit(
                "record_code",
                layout_forms={},
                layout_prefixes={"(column)": "R"},
            ),
        ),
        Mutation(
            "R16",
            "a prefix holding a figure",
            edit("record_code", layout_prefixes={"(column)": "R0"}),
            names="layout_prefixes",
        ),
        # A WIDTH CENSUS SPEAKING FOR A HELD-BACK FORM (plans P4-D221 and
        # P4-D222). The pool of eleven stands alone and passes the census's
        # own line, so only P8 refuses it: the forms map holds every form
        # back, and a total of widths names how many of its cells carried
        # a point.
        Mutation(
            "P8",
            "a width census counting cells of a form the forms map holds back",
            edit(
                "visits",
                numeric_styles={"(withheld)": 229},
                fraction_widths={"(withheld)": 11},
                pad_widths={},
                field_widths={},
            ),
        ),
        Mutation(
            "P7b",
            "a field width no padded cell could ever wear",
            edit(
                "visits",
                numeric_styles={"plain": 218, "leading_zero": 11},
                pad_widths={"1": 11},
            ),
        ),
        # -- the census of whole-number field widths (P4-D30) --------
        # Each of these is a document the loader must REFUSE. The
        # census counts THREE of the six forms rather than one, so its
        # sum is bounded on both sides rather than pinned, and each end
        # is registered here.
        Mutation(
            "P9c",
            "a whole-number width census counting fewer cells than the "
            "forms map says were written without a point",
            edit("visits", field_widths={}),
        ),
        Mutation(
            "P9c",
            "a whole-number width census counting more cells than the "
            "column holds",
            edit("visits", field_widths={"5": 9999}),
        ),
        Mutation(
            "P6c",
            "a whole-number field width written by too few cells to name",
            edit("visits", field_widths={"5": 10}),
        ),
        Mutation(
            "P7c",
            "a whole-number field width of no figures at all",
            edit("visits", field_widths={"0": 228}),
        ),
        # -- clock times --------------------------------------------
        Mutation(
            "T1", "a clock rung written in the other form",
            edit_inside("seen_at", "clock_percentiles", p50="07:59:00"),
        ),
        Mutation(
            "T2", "a ladder that does not begin at the earliest time",
            edit("seen_at", earliest="07:01"),
        ),
        Mutation(
            "T3", "clock rungs that go backwards",
            edit_inside("seen_at", "clock_percentiles", p50="07:01"),
        ),
        Mutation(
            "T4", "a column of clock times holding none",
            edit("seen_at", n_unparsed=240),
        ),
        Mutation(
            "T5", "too few clock times for the column to be read that way",
            edit("seen_at", n_unparsed=100),
        ),
        Mutation(
            "P6",
            "a pool beside named forms",
            # No pool stands beside a named form (plan P4-D222): the
            # producer counts a form below the line into the commonest one.
            edit(
                "visits",
                numeric_styles={"plain": 98, "decimal": 60, "(withheld)": 71},
                fraction_widths={"2": 60},
            ),
        ),
        Mutation(
            "P6",
            "a pool of every form that says each form was written",
            # 229 numbers are more than five forms hold below the line, so
            # a pool of all six says every form was written (plan P4-D222).
            edit(
                "visits",
                numeric_styles={"(withheld)": 229},
                fraction_widths={},
                pad_widths={},
                field_widths={},
            ),
        ),
        # -- record numbers and text ----------------------------------
        Mutation(
            "I4", "the shortest value longer than the longest",
            edit("record_code", min_length=9),
        ),
        Mutation(
            "F1", "an average length outside the lengths it describes",
            edit_inside("comment", "length", mean=1000.0),
        ),
        # -- rules enforced as a key, a range or a version ------------
        Mutation(
            "R13", "an entry no version of synthtwin knows",
            edit_top(nobody_knows_this=1),
            names="nobody_knows_this",
        ),
        Mutation(
            "R13", "a key forbidden on the role that carries it",
            edit("unused", percentiles={}),
            names="percentiles",
        ),
        Mutation(
            "R13", "a ladder with a twelfth rung",
            edit_inside("amount", "percentiles", p60=1.0),
            names="p60",
        ),
        Mutation(
            "R13", "a ninth name for how the columns move together",
            edit_in("relationships", ninth=None),
            names="ninth",
        ),
        Mutation(
            "R14", "a column block with no name",
            drop("visits", "n_present"),
            names="n_present",
        ),
        Mutation(
            "R14", "a ladder with a rung missing",
            lambda document: at(document, "amount")["percentiles"].pop("p50"),
            names="p50",
        ),
        Mutation(
            "R15", "a count written as text",
            edit_top(n_columns="12"),
            names="a piece of text",
        ),
        Mutation(
            "R15", "a whole number written with a fractional part",
            edit("visits", n_present=229.0),
            names="a number with a fractional part",
        ),
        Mutation(
            "R15", "a yes or no value written as a number",
            edit("visits", integer_valued=1),
            names="a yes or no value",
        ),
        # THE SMALLEST FLOOR ALLOWED IS ONE, NOT ELEVEN (owner ruling
        # 2026-08-14, plan amendment A-P3-11). This mutation used to set
        # the floor to 3 and expect a refusal. Three is now a floor a
        # person can ask for with `--smallest-group`, and the whole
        # workflow runs on it, so a description carrying 3 is refused by
        # nothing here -- it trips B5 further down only because THIS
        # document's held-back labels were sized for a floor of eleven.
        # Zero is what R16 still has to refuse, and it is the honest
        # replacement: "below the floor" would then reach counts of
        # nothing at all, which no count is.
        Mutation(
            "R16", "a declared delimiter this format does not read",
            edit_in("settings", forced_delimiter=":"),
            names="forced_delimiter",
        ),
        Mutation(
            "R16", "a floor below the smallest one allowed",
            edit_in("settings", small_cell_floor=0),
            names="small_cell_floor",
        ),
        Mutation(
            "R16", "a type path nobody has",
            edit("visits", role="something_else"),
            names="role",
        ),
        Mutation(
            "R16", "a column with no name at all",
            edit("visits", name="   "),
            names="name",
        ),
        Mutation(
            "R16", "a value of a column of text with no characters in it",
            length_of("comment", 0),
            names="length -> min",
        ),
        Mutation(
            "R16", "a stand-in number decided on a column that holds none",
            edit(
                "unused",
                sentinel_verdicts=[
                    {
                        "candidate": "-999",
                        "verdict": "kept_as_a_number",
                        "reason": "too_rare",
                        "n_occurrences": 20,
                        "spellings": [],
                    }
                ],
            ),
            names="sentinel_verdicts",
        ),
        Mutation(
            "R16", "a date written in no canonical form",
            edit("recorded_on", earliest="15/03/2024"),
            names="earliest",
        ),
        Mutation(
            "R16", "an offset in no form an offset takes",
            edit("recorded_on", utc_offsets={"two hours": 240}),
            names="utc_offsets -> two hours",
        ),
        Mutation(
            "R16", "declared names out of order",
            both(
                edit_in(
                    "settings", forced_identifiers=["record_code", "answer"]
                ),
                edit("answer", structural_role="identifier"),
            ),
            names="forced_identifiers",
        ),
        Mutation(
            "R18", "a description that carries how the columns move together",
            edit_in("relationships", grain="one row per person"),
            names="update synthtwin",
        ),
        # -- how the table's file is written (plan P4-D86) -------------
        Mutation("FD1", "a written form one column short", _form_one_column_short),
        Mutation("FD2", "line endings for one line too many", _form_one_line_too_many),
        Mutation(
            "FD2", "line endings counted out of their listed order",
            _form_counted_out_of_order,
        ),
        Mutation(
            "FD4", "blank lines counted below the cap on places",
            _form_blank_lines_counted_below_the_cap,
        ),
        Mutation(
            "FD3", "a byte-order mark on Latin-1 text", _form_marked_latin1
        ),
        Mutation(
            "FD4", "blank lines after more records than the table has",
            _form_blank_past_the_end,
        ),
        Mutation(
            "FD5", "a record of nothing in a table with a column never absent",
            _form_an_empty_record,
        ),
        Mutation(
            "FD6", "a row sequence in a column with absent cells",
            _form_sequence_with_holes,
        ),
        Mutation(
            "FD7", "rows sorted by a column with absent cells",
            _form_sorted_by_holes,
        ),
        Mutation(
            "FD8", "a header cell written as another name",
            _form_written_as_another_name,
        ),
        Mutation(
            "FD9", "a quoting rule for rows of column descriptions that do not exist",
            _form_rule_for_no_rows,
        ),
        Mutation(
            "FD10", "rows with a trailing delimiter and left-out cells",
            _form_trailing_and_short,
        ),
        Mutation(
            "FD11", "a preamble recorded as withheld that holds nothing",
            _form_withheld_nothing,
        ),
        Mutation(
            "FD9", "rows of column descriptions nobody declared",
            _form_rows_nobody_declared,
        ),
        Mutation(
            "FD11", "a run of blank lines marked as a comment is",
            _form_blank_run_marked_as_a_comment,
        ),
        Mutation(
            "FD11", "a mark the twin could not write",
            _form_preamble_marked_with_a_quote,
        ),
        # The rule that keeps a declared identifier out of the written
        # form (plan P4-D76). `record_code` is declared in the base
        # description above, so a row sequence published of it is the
        # generator's instruction to write the very values the
        # declaration exists to withhold.
        Mutation(
            "FD12", "a row sequence in a column declared to hold record numbers",
            _form_sequence_on_a_declared_identifier,
        ),
        # The declared delimiter (plan P4-D110, review item CODEX-4). The
        # base description declares none and reads its file with the
        # comma, so a declaration of the semicolon says two things about
        # one file; and a workbook has no delimiter to declare at all.
        Mutation(
            "FD13", "a declared delimiter the written form does not publish",
            edit_in("settings", forced_delimiter=";"),
        ),
        Mutation(
            "FD13", "a delimiter declared on a workbook",
            _form_workbook_with_a_declared_delimiter,
        ),
        # The workbook block (plan P4-D77). The base is a delimited
        # file's description, so each of these installs a conforming
        # block first and then breaks one rule of it.
        Mutation(
            "WB1", "a workbook block describing the wrong number of columns",
            _form_workbook_of_the_wrong_width,
        ),
        Mutation(
            "WB2", "a sheet numbered past the last the workbook has",
            _form_workbook_sheet_past_the_last,
        ),
        Mutation(
            "WB3", "a cell census naming a single row",
            _form_workbook_census_names_one_row,
        ),
        Mutation(
            "WB4", "more records holding nothing than the table has rows",
            _form_workbook_more_empty_rows_than_rows,
        ),
        Mutation(
            "WB3", "a count of records holding nothing that names one row",
            _form_workbook_empty_records_name_one_row,
        ),
        # The two rules the twin's WRITER needs (plan P4-D79). Both are
        # rules a description can break, which is why they are
        # invariants at all: the first two drafted in part 1 could not
        # be broken by any document and were taken out again.
        Mutation(
            "WB5", "a workbook naming fewer sheets than it has",
            _form_workbook_names_too_few_sheets,
        ),
        Mutation(
            "WB6", "a format code of a kind the column's own census denies",
            _form_workbook_format_code_denied_by_its_census,
        ),
        # A code carrying words out of somebody's file (plan P4-D189).
        Mutation(
            "WB6", "a format code carrying a quoted word",
            _form_workbook_format_code_carrying_a_word,
        ),
        # What every sheet that is not the table's holds (plan P4-D82).
        Mutation(
            "WB7", "a block of cells on the sheet the table was read from",
            _form_workbook_describes_the_tables_own_sheet,
        ),
        Mutation(
            "WB7", "a second sheet holding a table this description does not carry",
            _form_workbook_other_sheet_holds_a_table,
        ),
        # The files review's reproductions, one per rule it broke (plan
        # P4-D164, P4-D170, P4-D171).
        Mutation(
            "WB3", "a census whose one withheld count the others rebuild",
            _form_workbook_census_rebuilds_its_withheld_count,
        ),
        Mutation(
            "WB3", "a census publishing a nought beside a withheld count",
            _form_workbook_census_nought_beside_a_withheld_count,
        ),
        # The repair pass after the files review (plan P4-D174): each of
        # WB3's two subtraction rules, on a census publishing no nought,
        # so that nothing but the rule named can refuse it.
        Mutation(
            "WB3", "a census whose one withheld count no nought gives away",
            _form_workbook_census_withholds_one_count,
        ),
        Mutation(
            "WB3", "a census whose withheld counts come to fewer than the line",
            _form_workbook_census_withholds_under_the_line,
        ),
        # The difference a column's count of numbers takes from its census
        # of number cells: the figures stored as text (plan P4-D197).
        Mutation(
            "WB3", "numbers stored as text fewer than the line",
            _form_workbook_numbers_stored_as_text_under_the_line,
        ),
        Mutation(
            "WB5", "two sheets of one name in different cases",
            _form_workbook_two_sheets_of_one_name,
        ),
        Mutation(
            "WB7", "a second sheet holding a table one column wide",
            _form_workbook_other_sheet_holds_a_narrow_table,
        ),
        Mutation(
            "WB8", "a commonest class the column's own census denies",
            _form_workbook_value_class_denied_by_its_census,
        ),
    ]


def _form(document: Document) -> Document:
    """The written form of the base description (`source.dialect`)."""
    return typing.cast(Document, document["source"]["dialect"])


def _position_of(document: Document, name: str) -> int:
    return typing.cast(int, at(document, name)["position"])


def _form_one_column_short(document: Document) -> None:
    _form(document)["columns"] = _form(document)["columns"][:-1]


def _form_one_line_too_many(document: Document) -> None:
    _form(document)["line_endings"][0]["lines"] += 1


def _form_counted_out_of_order(document: Document) -> None:
    """Counts that account for every line, with CRLF listed before LF."""
    lines = typing.cast(int, _form(document)["line_endings"][0]["lines"])
    _form(document)["line_endings"] = []
    _form(document)["line_endings_spread"] = [
        {"ending": "crlf", "lines": 1},
        {"ending": "lf", "lines": lines - 1},
    ]


def _form_blank_lines_counted_below_the_cap(document: Document) -> None:
    _form(document)["blank_lines_spread"] = {
        "first": 0, "last": 1, "lines": 2, "text": "",
    }
    _form(document)["line_endings"][0]["lines"] += 2


def _form_marked_latin1(document: Document) -> None:
    document["source"]["encoding"] = "latin-1"
    document["source"]["used_fallback_encoding"] = True
    _form(document)["byte_order_mark"] = True


def _form_blank_past_the_end(document: Document) -> None:
    rows = typing.cast(int, document["n_rows"])
    _form(document)["blank_lines"] = [{"after": rows + 1, "lines": 1, "text": ""}]
    _form(document)["line_endings"][0]["lines"] += 1


def _form_an_empty_record(document: Document) -> None:
    _form(document)["empty_rows"]["interior"] = 1


def _form_sequence_with_holes(document: Document) -> None:
    place = _position_of(document, "visits") - 1
    _form(document)["columns"][place]["sequence_start"] = 0


def _form_sorted_by_holes(document: Document) -> None:
    _form(document)["row_order"] = {
        "collation": "number",
        "column": _position_of(document, "visits"),
        "direction": "ascending",
    }


def _form_written_as_another_name(document: Document) -> None:
    _form(document)["written_names"] = [{"position": 1, "text": "renamed"}]


def _form_rule_for_no_rows(document: Document) -> None:
    _form(document)["header_rows_quoting"] = "always"


def _form_trailing_and_short(document: Document) -> None:
    _form(document)["short_rows"] = True
    _form(document)["trailing_delimiter"]["rows"] = True


def _form_withheld_nothing(document: Document) -> None:
    _form(document)["preamble_withheld"] = True


def _form_rows_nobody_declared(document: Document) -> None:
    # TWO ROWS OF COLUMN DESCRIPTIONS AND NOBODY DECLARED THEM (FD9,
    # plan P4-D81). `settings.forced_metadata_rows` is nought in the
    # base, so this IS the description the producer wrote from a guess
    # before landing 2b.11: two rows taken out of the table and
    # published as schema text, held to no smallest group and written
    # into the twin as they stand. That is how a person's own record
    # became schema (review item CODEX-2), and the clause that refuses
    # it -- the published rows are the DECLARED rows -- could be taken
    # out with the whole required gate still green until this entry
    # existed.
    width = len(_form(document)["columns"])
    _form(document)["header_rows"] = [
        [f"what column {place + 1} holds" for place in range(width)],
        [f"marker {place + 1}" for place in range(width)],
    ]
    # Two rows of column descriptions are two more LINES of the file, so
    # the line endings account for them: FD2 is about the file's shape
    # and would otherwise refuse this description before FD9 read it,
    # leaving the clause under test unexercised.
    _form(document)["line_endings"][0]["lines"] += 2


def _form_blank_run_marked_as_a_comment(document: Document) -> None:
    # A RUN PUBLISHED AS BLANK WHOSE MARK IS A COMMENT'S (FD11, plan
    # P4-D80). The twin writes `# ` for such a run, the survey reads
    # that line back as a COMMENT, and the description said blank: the
    # twin's own form is then not the form published. FD11's shape
    # clause is the only rule that refuses this, and nothing in the
    # required tests noticed its removal until this entry.
    _form(document)["preamble"] = [{"kind": "blank", "lines": 1, "mark": "# "}]
    _form(document)["line_endings"][0]["lines"] += 1


def _form_preamble_marked_with_a_quote(document: Document) -> None:
    # A MARK THE TWIN CANNOT WRITE (FD11, plan P4-D83). The twin writes
    # `"withheld line` for this run -- a quoted field nothing closes --
    # and such a twin missed about 120 obligations of its own
    # description while `synthtwin profile` refused to read it at all.
    # The shape clause CANNOT catch it: `"withheld line` is read back
    # as a comment marked `"`, which is exactly what is published here.
    _form(document)["preamble"] = [{"kind": "comment", "lines": 1, "mark": '"'}]
    _form(document)["preamble_withheld"] = True
    _form(document)["line_endings"][0]["lines"] += 1


def _form_sequence_on_a_declared_identifier(document: Document) -> None:
    place = _position_of(document, "record_code") - 1
    _form(document)["columns"][place]["sequence_start"] = 0


def _workbook_block(document: Document, columns: int, rows: int) -> Document:
    """Install a conforming workbook block on the base description.

    The base is a description of a DELIMITED file, so it carries no
    workbook block at all and no mutation of one could be built from it.
    This writes the block the producer writes for a workbook of the same
    shape -- every census holding to the base's floor of eleven -- so
    that each entry below damages exactly one rule and nothing else.
    """
    # THE CENSUSES COUNT THE DESCRIPTION'S OWN ROWS, whatever `rows` says:
    # a census is held to the table's row count now (plan P4-D164), and
    # the base description has 240 of them.
    rows = typing.cast(int, document["n_rows"])
    classes: "dict[str, object]" = {}
    for kind in workbook.CELL_CLASSES:
        classes[kind] = 0
    classes["number"] = rows
    kinds: "dict[str, object]" = {}
    for kind in workbook.FORMAT_KINDS:
        kinds[kind] = 0
    kinds["plain"] = rows
    every: "list[object]" = []
    for _place in range(columns):
        every += [
            {
                "cell_classes": dict(classes),
                "format_code": "General",
                "format_kinds": dict(kinds),
                # A nought of formulas is WITHHELD like any count that
                # is not the whole or at the line on both sides, so that
                # a withheld count is never told from a real nought (plan
                # P4-D164).
                "formulas": None,
                "value_class": "number",
            }
        ]
    block: Document = {
        "autofilter": False,
        "columns": every,
        "date_system": "1900",
        "defined_names": 0,
        "defined_table": False,
        "empty_rows_inside": None,
        "frozen_rows": 0,
        "macro_project": False,
        "rows_above_header": 0,
        "sheet_count": 2,
        "sheet_hidden": False,
        "sheet_names": ["Data", "Notes"],
        # The table's own sheet describes no block of cells and every
        # other sheet describes one (WB7, plan P4-D82). The second sheet
        # here holds a single cell, which is the shape a notes page
        # takes and the one the twin writes back with a word of
        # synthtwin's own.
        "sheet_extents": [None, {"columns": 1, "rows": 1}],
        "sheet_position": 1,
        "trailing_blank_columns": 0,
        "trailing_blank_rows": 0,
    }
    document["source"]["workbook"] = block
    return block


def _form_workbook_with_a_declared_delimiter(document: Document) -> None:
    _workbook_block(document, 16, 120)
    document["settings"]["forced_delimiter"] = ","


def _form_workbook_of_the_wrong_width(document: Document) -> None:
    block = _workbook_block(document, 16, 120)
    del block["columns"][-1]


def _form_workbook_sheet_past_the_last(document: Document) -> None:
    block = _workbook_block(document, 16, 120)
    block["sheet_position"] = 3


def _form_workbook_census_names_one_row(document: Document) -> None:
    block = _workbook_block(document, 16, 120)
    # One cell of one class, at a floor of eleven: the row holding that
    # cell is named by the count, and so is every other row by its
    # complement.
    block["columns"][0]["cell_classes"]["error"] = 1


def _form_workbook_more_empty_rows_than_rows(document: Document) -> None:
    block = _workbook_block(document, 16, 120)
    block["empty_rows_inside"] = 1000


def _form_workbook_empty_records_name_one_row(document: Document) -> None:
    block = _workbook_block(document, 16, 120)
    # ONE record of 120 holding nothing, at a floor of eleven. The count
    # names the row that holds nothing as surely as a census of one cell
    # names the row that holds it, and its complement names every other
    # row. Published raw at every floor until the repair of landing
    # 2b.10, and the twin then wrote that one empty record back.
    block["empty_rows_inside"] = 1


def _form_workbook_names_too_few_sheets(document: Document) -> None:
    block = _workbook_block(document, 16, 120)
    # Two sheets, one name. A twin built from this would have no name to
    # write the second sheet under.
    block["sheet_names"] = ["Data"]


def _form_workbook_describes_the_tables_own_sheet(document: Document) -> None:
    block = _workbook_block(document, 16, 120)
    # The sheet the table was read from is described by the table's own
    # facts. A block of cells here as well says two things about one
    # sheet, and the writer would put a page of withheld cells over the
    # table it just wrote.
    block["sheet_extents"] = [{"columns": 4, "rows": 12}, {"columns": 1, "rows": 1}]


def _form_workbook_other_sheet_holds_a_table(document: Document) -> None:
    block = _workbook_block(document, 16, 120)
    # A second sheet holding twelve rows by four columns is a TABLE this
    # description does not carry. synthtwin refuses such a workbook when
    # it reads one (plan P4-D82); a description asking for one would
    # have the twin write a frame of withheld cells where a table stood,
    # so code developed on it would read a table that is not there.
    block["sheet_extents"] = [None, {"columns": 4, "rows": 12}]


def _form_workbook_census_rebuilds_its_withheld_count(
    document: Document,
) -> None:
    block = _workbook_block(document, 16, 120)
    # THE REPRODUCTION (files review, item 4). Sixty numbers, fifty-nine
    # texts and one boolean, the boolean withheld and every other class
    # published: 120 - 60 - 59 rebuilds the withheld count of one.
    census = block["columns"][0]["cell_classes"]
    census["number"] = 120
    census["text"] = 119
    census["boolean"] = None


def _form_workbook_census_nought_beside_a_withheld_count(
    document: Document,
) -> None:
    block = _workbook_block(document, 16, 120)
    # Two counts withheld, the rest published -- and the published
    # noughts tell a reader the withheld ones are not nought, so each is
    # "some, but few" (plan P4-D164).
    census = block["columns"][0]["cell_classes"]
    census["number"] = 200
    census["text"] = None
    census["boolean"] = None


def _form_workbook_census_withholds_one_count(document: Document) -> None:
    block = _workbook_block(document, 16, 120)
    rows = typing.cast(int, document["n_rows"])
    # Every class holds cells and every count but one is published, so
    # the one withheld is the row count less the others (plan P4-D174).
    census = block["columns"][0]["cell_classes"]
    for kind in workbook.CELL_CLASSES:
        census[kind] = 30
    census["number"] = rows - 30 * 7
    census["date"] = None


def _form_workbook_census_withholds_under_the_line(document: Document) -> None:
    block = _workbook_block(document, 16, 120)
    rows = typing.cast(int, document["n_rows"])
    # Two counts withheld, no nought beside them, and together they come
    # to five cells at a floor of eleven (plan P4-D174).
    census = block["columns"][0]["cell_classes"]
    for kind in workbook.CELL_CLASSES:
        census[kind] = 30
    census["number"] = rows - 30 * 5 - 5
    census["date"] = None
    census["error"] = None


def _form_workbook_numbers_stored_as_text_under_the_line(
    document: Document,
) -> None:
    block = _workbook_block(document, 16, 120)
    rows = typing.cast(int, document["n_rows"])
    # `visits` publishes 229 numbers; a census of 224 number cells and 16
    # text cells holds every count and complement to the line, and leaves
    # five figures stored as text -- one subtraction away (plan P4-D197).
    census = block["columns"][2]["cell_classes"]
    census["number"] = 224
    census["text"] = rows - 224


def _form_workbook_two_sheets_of_one_name(document: Document) -> None:
    block = _workbook_block(document, 16, 120)
    # A spreadsheet renames the second of two sheets whose names differ
    # only in case, so the twin could not carry both (plan P4-D171).
    block["sheet_names"] = ["Data", "DATA"]


def _form_workbook_other_sheet_holds_a_narrow_table(document: Document) -> None:
    block = _workbook_block(document, 16, 120)
    # A header and thirty values in one column: records, however narrow
    # (files review, item 8; plan P4-D170).
    block["sheet_extents"] = [None, {"columns": 1, "rows": 31}]


def _form_workbook_value_class_denied_by_its_census(document: Document) -> None:
    block = _workbook_block(document, 16, 120)
    # The census says no cell holds text, and the column names text as
    # its commonest class.
    block["columns"][0]["value_class"] = "text"


def _form_workbook_format_code_denied_by_its_census(document: Document) -> None:
    block = _workbook_block(document, 16, 120)
    # The column's census says not one of its cells wears a date format,
    # and its twin is told to wear one. A twin written from this would
    # come back from every reader as a column of dates where the
    # description publishes none.
    block["columns"][0]["format_code"] = "mm-dd-yy"


def _form_workbook_format_code_carrying_a_word(document: Document) -> None:
    block = _workbook_block(document, 16, 120)
    # A code of the format language's own tokens alone is published as
    # written; one carrying a quoted word is not, and a twin written from
    # this would wear the word in every cell of the column.
    block["columns"][0]["format_code"] = '"Record "0'


BATTERY = battery()


@pytest.mark.parametrize(
    "mutation", BATTERY, ids=[f"{one.rule}-{one.what}" for one in BATTERY]
)
def test_every_rule_has_a_description_that_must_be_refused(
    tmp_path: pathlib.Path, base: Document, mutation: Mutation
) -> None:
    """One thing wrong, one refusal, and it names the rule that broke.

    The message check is the whole point: a refusal that names some
    other rule would leave this one unenforced while the battery still
    passed.
    """
    document = copy.deepcopy(base)
    mutation.change(document)
    message = refusal(tmp_path, document)
    assert mutation.expected() in message, message


# -- the vacuity floor ------------------------------------------------


def test_the_base_document_loads(
    tmp_path: pathlib.Path, base: Document
) -> None:
    """The description every mutation starts from is accepted as it is."""
    loaded = contract.load_profile(written(tmp_path, base))
    assert loaded.n_columns == 16
    assert len(loaded.columns) == 16


def test_every_mutation_starts_from_a_document_that_loads(
    tmp_path: pathlib.Path, base: Document
) -> None:
    """No entry of the battery is refused before it changes anything.

    The base is loaded once per entry rather than once in all, so that
    an entry that quietly damaged the shared copy could not hide behind
    one that did not.
    """
    for mutation in BATTERY:
        document = copy.deepcopy(base)
        contract.load_profile(written(tmp_path, document))
        mutation.change(document)


def test_every_mutation_changes_the_document(base: Document) -> None:
    """A mutation that changes nothing refuses the base, not the rule."""
    for mutation in BATTERY:
        document = copy.deepcopy(base)
        before = canonical.serialize(document)
        mutation.change(document)
        assert canonical.serialize(document) != before, mutation.what


def test_every_invariant_the_loader_names_has_a_mutation() -> None:
    """Every rule the loader raises by name is broken by some entry.

    This is the completeness half of the floor: a rule added to
    `contract.INVARIANTS` without a description that must be refused for
    it fails here, so the battery cannot fall behind the loader.
    """
    covered = {mutation.rule for mutation in BATTERY}
    missing = sorted(set(contract.INVARIANTS) - covered)
    assert not missing, f"rules with no refused description: {missing}"


def test_every_mutation_names_a_rule_the_loader_knows() -> None:
    """No entry is filed under a rule that does not exist.

    A battery entry naming a rule the loader never raises would pass by
    accident, on whatever message the document happened to produce.
    """
    catalogue = {f"R{number}" for number in range(1, 20)}
    for mutation in BATTERY:
        assert (
            mutation.rule in contract.INVARIANTS
            or mutation.rule in catalogue
        ), mutation.rule


def test_the_battery_would_notice_a_loader_that_checked_nothing(
    tmp_path: pathlib.Path, base: Document
) -> None:
    """Every entry is refused, and one bad document is not enough.

    The count is asserted so that a battery quietly reduced to a handful
    of entries fails: the floor is not only that each entry is refused,
    but that there are as many of them as there are rules.
    """
    assert len(BATTERY) >= len(contract.INVARIANTS)
    refused = 0
    for mutation in BATTERY[:5]:
        document = copy.deepcopy(base)
        mutation.change(document)
        refusal(tmp_path, document)
        refused += 1
    assert refused == 5


# -- the refusal catalogue, R1 to R19 (contract 10.7) -----------------


def test_r1_a_path_that_names_nothing(tmp_path: pathlib.Path) -> None:
    """R1 names the path, says nothing is there, and says to check it."""
    place = tmp_path / "not-there-profile.json"
    with pytest.raises(errors.ProfileError) as raised:
        contract.load_profile(str(place))
    message = f"{raised.value}"
    assert f"{place}" in message
    assert "There is no file at" in message
    assert "-profile.json" in message


def test_r2_a_file_that_cannot_be_read(
    tmp_path: pathlib.Path, base: Document,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """R2 names the path and points at permission or the drive.

    The failure is arranged rather than provoked: a file nobody may read
    cannot be made portably, and the run may be a user who may read
    everything anyway.
    """
    path = written(tmp_path, base)

    def refuse(_place: pathlib.Path) -> str:
        raise PermissionError("permission denied")

    monkeypatch.setattr(contract, "_read_text", refuse)
    with pytest.raises(errors.ProfileError) as raised:
        contract.load_profile(path)
    message = f"{raised.value}"
    assert path in message
    assert "permission" in message


def test_r3_a_folder_where_a_description_belongs(
    tmp_path: pathlib.Path
) -> None:
    """R3 names the folder and says which file to give instead."""
    with pytest.raises(errors.ProfileError) as raised:
        contract.load_profile(str(tmp_path))
    message = f"{raised.value}"
    assert f"{tmp_path}" in message
    assert "is a folder" in message
    assert "-profile.json" in message


def test_r4_bytes_that_are_not_text(tmp_path: pathlib.Path) -> None:
    """R4 says the file is not text synthtwin can read."""
    target = tmp_path / "table-profile.json"
    target.write_bytes(b"\xff\xfe{\x00")
    with pytest.raises(errors.ProfileError) as raised:
        contract.load_profile(str(target))
    message = f"{raised.value}"
    assert "not readable as text" in message
    assert "synthtwin profile" in message


def test_r5_text_that_is_not_the_written_form(
    tmp_path: pathlib.Path
) -> None:
    """R5 says where the reading stopped and what usually causes it."""
    message = refusal_of_text(tmp_path, '{\n  "profile_version": 6,\n')
    assert "line 3" in message
    assert "character" in message
    assert "edited" in message or "copied" in message


def test_r6_a_character_that_cannot_be_written(
    tmp_path: pathlib.Path
) -> None:
    """R6 says the file holds a character that is not writable text."""
    message = refusal_of_text(
        tmp_path, '{\n  "note": "\\ud800",\n  "profile_version": 6\n}\n'
    )
    assert "cannot be written as text" in message


def test_r7_a_number_that_is_not_one(tmp_path: pathlib.Path) -> None:
    """R7 says the file holds a number that is not a number."""
    message = refusal_of_text(
        tmp_path, '{\n  "note": NaN,\n  "profile_version": 6\n}\n'
    )
    assert "is not a number" in message


def test_r8_nesting_deeper_than_the_bound(tmp_path: pathlib.Path) -> None:
    """R8 gives the limit and says no description comes near it."""
    depth = contract.MAXIMUM_DEPTH + 1
    message = refusal_of_text(tmp_path, "[" * depth + "]" * depth)
    assert f"{contract.MAXIMUM_DEPTH} deep" in message
    assert "six deep" in message


def test_the_depth_bound_accepts_the_document_at_the_limit() -> None:
    """The near-limit case passes the scan, and one more does not."""
    depth = contract.MAXIMUM_DEPTH
    contract._scanned("[" * depth + "]" * depth, "somewhere")
    with pytest.raises(errors.ProfileError):
        contract._scanned("[" * (depth + 1) + "]" * (depth + 1), "somewhere")


def test_r9_a_number_written_longer_than_the_bound(
    tmp_path: pathlib.Path
) -> None:
    """R9 gives the limit and draws the same conclusion as R8."""
    token = "1" * (contract.MAXIMUM_NUMBER_CHARACTERS + 1)
    message = refusal_of_text(tmp_path, f"[{token}]")
    assert f"{contract.MAXIMUM_NUMBER_CHARACTERS} characters" in message


def test_the_number_bound_accepts_the_token_at_the_limit() -> None:
    """The near-limit case passes the scan, and one more does not."""
    limit = contract.MAXIMUM_NUMBER_CHARACTERS
    contract._scanned("[" + "1" * limit + "]", "somewhere")
    with pytest.raises(errors.ProfileError):
        contract._scanned("[" + "1" * (limit + 1) + "]", "somewhere")


def test_the_pre_scan_counts_nothing_inside_a_string() -> None:
    """A brace or a long figure inside a value is a character of it."""
    braces = '{"note": "' + "{" * 100 + '", "profile_version": 6}'
    contract._scanned(braces, "somewhere")
    figures = '{"note": "' + "1" * 500 + '", "profile_version": 6}'
    contract._scanned(figures, "somewhere")
    escaped = '{"note": "a quotation mark \\" and ' + "{" * 100 + '"}'
    contract._scanned(escaped, "somewhere")


NOT_CANONICAL = (
    ("a repeated entry", '{\n  "a": 1,\n  "a": 2,\n  "profile_version": 6\n}\n'),
    ("entries out of order", '{\n  "b": 1,\n  "a": 2,\n  "profile_version": 6\n}\n'),
    ("a number written the long way", '{\n  "a": 1.0e2,\n  "profile_version": 6\n}\n'),
    ("no final newline", '{\n  "a": 1,\n  "profile_version": 6\n}'),
    ("two final newlines", '{\n  "a": 1,\n  "profile_version": 6\n}\n\n'),
    ("an indent of its own", '{\n    "a": 1,\n    "profile_version": 6\n}\n'),
    (
        "line endings from another system",
        '{\r\n  "a": 1,\r\n  "profile_version": 6\r\n}\r\n',
    ),
)


@pytest.mark.parametrize(
    "what,text", NOT_CANONICAL, ids=[name for name, _text in NOT_CANONICAL]
)
def test_r10_a_file_that_is_not_the_bytes_synthtwin_writes(
    tmp_path: pathlib.Path, what: str, text: str
) -> None:
    """R10 catches every non-canonical form, the repeated key included.

    Every one of these parses. What refuses them is writing the parsed
    value out again and comparing it with the file, which is one check
    and no callback of any kind.
    """
    message = refusal_of_text(tmp_path, text)
    assert "not in the exact form synthtwin writes" in message, what


def test_r11_an_older_description_is_made_again(
    tmp_path: pathlib.Path, base: Document
) -> None:
    """R11 gives both versions and says to run 'synthtwin profile'."""
    document = copy.deepcopy(base)
    document["profile_version"] = 4
    message = refusal(tmp_path, document)
    assert "version 4" in message
    assert "version 6" in message
    assert "synthtwin profile" in message
    # THE THINGS CONTRACT 5 SECTION 10.2 FIXES WORD FOR WORD: why the
    # older file cannot be read, and every option that has to come back
    # with the person if the new description is to read their table the
    # same way -- five of them since 2026-08-17, because two of the
    # three that were missing change what the description PUBLISHES
    # (review item P3-V9-F6, plan amendment A-P3-36). The set is held to
    # the shipped parser's own in
    # `tests/test_p3v9f6_migration_names_every_option.py`; what is
    # asserted here is that the loader's own refusal carries them.
    assert "cannot be read back exactly" in message
    for option in (
        "--keep-value",
        "--missing-value",
        "--identifier",
        "--smallest-group",
        "--first-row",
    ):
        assert option in message, option


def test_r12_a_newer_description_never_sends_anybody_to_a_profiler(
    tmp_path: pathlib.Path, base: Document
) -> None:
    """R12 gives both versions, says to update, and says nothing else.

    The advice not given is the point: somebody holding a newer
    description may not hold the table at all, so telling them to make
    the description again is advice that cannot be followed and may be
    acted on anyway.
    """
    document = copy.deepcopy(base)
    document["profile_version"] = 7
    message = refusal(tmp_path, document)
    assert "version 7" in message
    assert "version 6" in message
    assert "update synthtwin" in message
    assert "synthtwin profile" not in message


def test_the_version_is_read_before_the_canonical_form(
    tmp_path: pathlib.Path, base: Document
) -> None:
    """A newer description that is also not canonical is still told so.

    Direction-correct version advice is more use to a person than a
    complaint about the exact bytes, and a description written by
    another version is very likely canonical under its own rules.
    """
    document = copy.deepcopy(base)
    document["profile_version"] = 7
    target = tmp_path / "table-profile.json"
    target.write_text(
        canonical.serialize(document) + "\n", encoding="utf-8", newline="\n"
    )
    with pytest.raises(errors.ProfileError) as raised:
        contract.load_profile(str(target))
    assert "update synthtwin" in f"{raised.value}"


def test_r19_memory_exhausted_while_reading(
    tmp_path: pathlib.Path, base: Document,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """R19 says what happened and what to try, and quotes no row count.

    Running the machine out of memory for real is not a test anybody can
    run, so the failure is arranged at the one place it happens.
    """
    path = written(tmp_path, base)

    def exhaust(_place: pathlib.Path) -> str:
        raise MemoryError()

    monkeypatch.setattr(contract, "_read_text", exhaust)
    with pytest.raises(errors.ProfileError) as raised:
        contract.load_profile(path)
    message = f"{raised.value}"
    assert path in message
    assert "not enough memory" in message
    assert "more memory" in message
    assert "fewer columns" in message


def test_no_refusal_on_this_path_quotes_a_row_count(
    tmp_path: pathlib.Path, base: Document
) -> None:
    """The row count never reaches a message, whatever is wrong.

    Reading a description can run out of memory before a single field
    has been checked, so a message naming a row count could be naming a
    number nobody read. The rule is checked on the row count itself
    being wrong, which is the case a message would most want to quote.
    """
    document = copy.deepcopy(base)
    document["n_rows"] = -1
    message = refusal(tmp_path, document)
    assert "n_rows" in message
    assert "-1" not in message
    other = copy.deepcopy(base)
    other["n_rows"] = 999
    quoted = refusal(tmp_path, other)
    assert "999" not in quoted


# -- what the loader is, beyond the rules it enforces ------------------


def test_the_loader_returns_typed_objects_not_the_document(
    tmp_path: pathlib.Path, base: Document
) -> None:
    """A consumer cannot read a key the contract does not define."""
    loaded = contract.load_profile(written(tmp_path, base))
    assert isinstance(loaded, contract.Profile)
    assert isinstance(loaded.source, contract.SourceBlock)
    assert isinstance(loaded.settings, contract.SettingsBlock)
    assert isinstance(loaded.relationships, contract.RelationshipManifest)
    assert loaded.relationships.slots == contract.RELATIONSHIP_KEYS
    facts = {block.name: type(block.facts) for block in loaded.columns}
    assert facts["unused"] is contract.EmptyFacts
    assert facts["region"] is contract.CategoricalFacts
    assert facts["answer"] is contract.LabelFacts
    assert facts["visits"] is contract.NumericFacts
    assert facts["recorded_on"] is contract.DatetimeFacts
    assert facts["comment"] is contract.TextFacts
    assert facts["record_code"] is contract.IdentifierFacts
    assert facts["huge"] is contract.UnrepresentableFacts
    with pytest.raises(AttributeError):
        assert loaded.columns[0].facts.percentiles  # type: ignore[union-attr]
    with pytest.raises(dataclasses.FrozenInstanceError):
        loaded.columns[0].name = "something else"  # type: ignore[misc]


def test_the_columns_come_back_in_the_order_the_document_holds_them(
    tmp_path: pathlib.Path, base: Document
) -> None:
    """S3: list order is schema order, and this loader keeps it.

    It is the one contract rule a loader does not check but UPHOLDS, and
    everything downstream -- the twin's column order and the order the
    one random stream is consumed in -- rests on it.
    """
    loaded = contract.load_profile(written(tmp_path, base))
    assert [block.name for block in loaded.columns] == [
        block["name"] for block in base["columns"]
    ]
    assert [block.position for block in loaded.columns] == list(
        range(1, len(loaded.columns) + 1)
    )


def test_the_axes_carry_what_the_generator_dispatches_on(
    tmp_path: pathlib.Path, base: Document
) -> None:
    """Every column carries the three axes, and they agree with the role."""
    loaded = contract.load_profile(written(tmp_path, base))
    for block in loaded.columns:
        assert (
            block.role,
            block.statistical_type,
            block.quality_state,
        ) in contract.AXIS_ROWS
    declared = [
        block.name
        for block in loaded.columns
        if block.structural_role == "identifier"
    ]
    assert declared == ["record_code"]


def test_a_wide_table_description_loads(tmp_path: pathlib.Path) -> None:
    """The producer-to-loader boundary holds on a genuinely wide table.

    There is no document-size limit and no limit on how many entries a
    block may hold, on purpose: every column contributes one entry to
    the list of columns, so a limit there would be a limit on how many
    columns a table may have, which Phase 1 never promised to stop at.
    """
    names = [f"column_{index}" for index in range(150)]
    rows = [[f"{index + place}" for place in range(150)] for index in range(14)]
    path = fixtures.write(
        tmp_path, "wide.csv", fixtures.rows_to_csv(names, rows)
    )
    table = reading.read_table(str(path))
    document = profile.build_document(table, taxonomy.Settings(), [])
    loaded = contract.load_profile(written(tmp_path, document))
    assert loaded.n_columns == 150
    assert len(loaded.columns) == 150


def test_the_loader_reaches_neither_the_reader_nor_pandas() -> None:
    """The generation path never reads the real table (plan P2-D1).

    The check is on the SOURCE rather than on what happens to be
    imported while the suite runs, because the suite imports the reader
    for its own tests. Everything `contract` imports, and everything
    those modules import in turn, is walked, and the two forbidden
    targets must not appear anywhere in that closure.
    """
    folder = pathlib.Path(__file__).resolve().parent.parent / "src"
    seen: set[str] = set()
    waiting = ["contract"]
    while waiting:
        name = waiting.pop()
        if name in seen:
            continue
        seen.add(name)
        text = (folder / "synthtwin" / f"{name}.py").read_text(
            encoding="utf-8"
        )
        for line in text.split("\n"):
            stripped = line.strip()
            if stripped.startswith(("import ", "from ")):
                assert "pandas" not in stripped, (name, stripped)
                for module in (
                    "canonical", "errors", "parsing", "paths", "taxonomy",
                    "profile", "reading", "writing", "summary", "cli",
                ):
                    if f" {module}" in stripped and "synthtwin" in stripped:
                        waiting.append(module)
    assert "reading" not in seen
    assert "profile" not in seen


# -- the raised floor of the midnight count, which the battery above
# cannot witness (landing 2b.14) --------------------------------------


def _stamps_partly_at_midnight() -> str:
    """Four hundred moments, five of them standing at midnight."""
    rows: "list[str]" = []
    for index in range(400):
        if index < 5:
            rows += [f"2024-03-{index + 1:02d} 00:00:00"]
        else:
            rows += [
                f"2024-{(index % 12) + 1:02d}-{(index % 28) + 1:02d} "
                f"{(index % 23) + 1:02d}:{index % 60:02d}:"
                f"{(index * 7) % 59:02d}"
            ]
    return fixtures.single_column_table("when", rows)


@pytest.fixture(scope="module")
def at_a_floor_of_one(tmp_path_factory: pytest.TempPathFactory) -> Document:
    """An honest description of that column, asked for at a floor of ONE.

    THE BATTERY ABOVE CANNOT BE THIS DOCUMENT, and that is the point.
    Its base declares a floor of eleven, because a whole family of rules
    there can only be broken by damaging something held back, and at a
    floor of one nothing is. But D15 carries a floor OF ITS OWN -- never
    below two, whatever the run asked for -- and at a floor of eleven
    that raise decides nothing: the ordinary floor refuses a count of one
    long before the raise is consulted. So the raise sits underneath
    every one of the battery's five D15 entries without being exercised
    by any of them. Measured, not assumed: with the raise withdrawn from
    the loader, `tests/test_contract_loader.py` passes entire.

    This column is where the raise is the only rule standing. A floor of
    one holds nothing back, so S13 is silent and the description loads;
    five of the four hundred moments stand at midnight, which a floor of
    one publishes as an ordinary count.
    """
    folder = tmp_path_factory.mktemp("midnight-floor-one")
    path = fixtures.write(folder, "stamps.csv", _stamps_partly_at_midnight())
    table = reading.read_table(str(path))
    document = profile.build_document(
        table, taxonomy.Settings(small_cell_floor=1), [], [], []
    )
    return json.loads(json.dumps(document))


def test_the_witness_starts_from_a_description_that_loads(
    tmp_path: pathlib.Path, at_a_floor_of_one: Document
) -> None:
    """A witness refused for some other reason would witness nothing."""
    contract.load_profile(written(tmp_path, at_a_floor_of_one))
    settings = typing.cast(Document, at_a_floor_of_one["settings"])
    assert settings["small_cell_floor"] == 1, settings["small_cell_floor"]
    block = at_a_floor_of_one["columns"][0]
    assert block["n_at_midnight"] == 5, block["n_at_midnight"]
    assert block["all_at_midnight"] is False, block["all_at_midnight"]


@pytest.mark.parametrize(
    "counted,names",
    [
        (1, "the one person who holds the value"),
        (399, "the one person who does not hold it"),
    ],
)
def test_the_count_at_midnight_names_nobody_even_at_a_floor_of_one(
    tmp_path: pathlib.Path,
    at_a_floor_of_one: Document,
    counted: int,
    names: str,
) -> None:
    """D15's own floor of two, at the one floor where it is the rule deciding.

    Both directions, because the disclosure rule has two halves and the
    raise is what enforces each: a count of one names the person holding
    the value, and a count one short of every value names the person who
    does not. At a floor of one the run's own floor admits both, so a
    refusal here is the raise and nothing else -- which is exactly what
    the battery above, written at a floor of eleven, cannot show.
    """
    document = copy.deepcopy(at_a_floor_of_one)
    block = at_a_floor_of_one["columns"][0]
    parsed = int(block["n_present"]) - int(block["n_unparsed"])
    assert counted < parsed, "the count must leave the column short"
    document["columns"][0]["n_at_midnight"] = counted
    document["columns"][0]["all_at_midnight"] = False
    message = refusal(tmp_path, document)
    assert contract.INVARIANTS["D15"] in message, (names, message)
