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
from synthtwin import canonical, contract, errors, profile, reading, taxonomy

Document = dict[str, typing.Any]
Change = typing.Callable[[Document], None]


# -- one conforming description, built by the real producer -----------


def table_text() -> str:
    """A neutral table with one column for every role in the taxonomy.

    The builder in `fixtures` covers nine of the ten; a column of
    numbers no binary64 can hold is added here so that the tenth is
    covered too, and so that the battery has a block of every shape to
    damage.

    A column of dates AND times in two offsets is added for the same
    reason. The builder's own column of dates carries no time of day,
    so a document made from it alone can break no rule about a seconds
    field or a shared clock, and D10 had no description to be broken by
    (review item P2-C3-F2).
    """
    lines = [line for line in fixtures.every_role_table().split("\n") if line]
    rows = [f"{lines[0]},huge,logged_at"]
    for index, line in enumerate(lines[1:]):
        huge = "1e999" if index % 2 else "-2e400"
        offset = "+02:00" if index % 2 else "-05:00"
        stamp = (
            f"2024-{(index % 12) + 1:02d}-{(index % 28) + 1:02d} "
            f"{index % 24:02d}:{(index * 11) % 60:02d}:"
            f"{(index * 7) % 59 + 1:02d}{offset}"
        )
        rows.append(f"{line},{huge},{stamp}")
    return "\n".join(rows) + "\n"


@pytest.fixture(scope="module")
def base(tmp_path_factory: pytest.TempPathFactory) -> Document:
    """The conforming description every mutation starts from."""
    folder = tmp_path_factory.mktemp("contract")
    path = fixtures.write(folder, "table.csv", table_text())
    table = reading.read_table(str(path))
    document = profile.build_document(
        table, taxonomy.Settings(), ["record_code"]
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

    The role's key set is the four shared label keys AND its own form
    census (P4-D18), so the relabelling supplies one -- otherwise the
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
        sizes = list(block["suppressed_level_counts"])
        sizes[0] = sizes[0] + given
        block["suppressed_level_counts"] = sorted(sizes)
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
        # be held back; the base is written at the default floor, where
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
                        },
                    ]
                }
            ),
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
            "B4", "a held-back label with no size beside it",
            edit("region", suppressed_level_counts=[]),
        ),
        Mutation(
            "B5", "a label held back that the floor would have published",
            edit("region", suppressed_level_counts=[20]),
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
            # the rule rather than a gap in the battery: at the default
            # floor of eleven every published level already covers the
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
            "W7", "a published label nobody wrote",
            edit_level("region", 0, variants={}, variants_withheld={}),
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
        Mutation(
            "SF1",
            "a written form named by fewer cells than the floor admits",
            edit("region", shape_forms={"AAAA": 117, "AAAAA": 3}),
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
                edit("region", shape_forms={"AAAA": 1, "(withheld)": 1}),
            ),
        ),
        Mutation(
            "SF3",
            "a census counting more cells than the column has present",
            edit("region", shape_forms={"AAAA": 117, "AAAAA": 9999}),
        ),
        Mutation(
            "P8",
            "two width censuses that are each possible and not both",
            edit(
                "visits",
                numeric_styles={
                    "plain": 174, "leading_plus": 20, "(withheld)": 35,
                },
                fraction_widths={"(withheld)": 10},
                pad_widths={},
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
            "a pool larger than the forms left to hold it",
            edit(
                "visits",
                numeric_styles={"plain": 100, "decimal": 60, "(withheld)": 69},
                fraction_widths={"2": 60},
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
    ]


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
    assert loaded.n_columns == 15
    assert len(loaded.columns) == 15


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
