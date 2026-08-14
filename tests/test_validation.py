"""The validator: the green direction, the red battery, and disclosure.

Plan P3-D4 and specification section V8. Three things are proved here
and each one fails in its own way:

* THE GREEN DIRECTION -- producer to generator to validator over the
  every-role fixture: zero MISSED and zero WITHHELD. A twin validated
  against its own description must not trip the disclosure gate,
  because type read-back agreement is itself a Phase 2 promise;
* THE RED BATTERY -- every perturbation NAMES the subcheck it must
  fail, and the assertion is that THAT subcheck reports MISSED. Other
  subchecks failing alongside is fine; a perturbation caught only by a
  neighbour is a red battery, because the named subcheck did not do its
  job;
* DISCLOSURE -- no string read from the measured file appears in any
  field of any result, proved by walking every character of every
  check against the file's own cells.

Every table is built at test time by the seeded neutral builders in
`fixtures.py`; no data-format file enters the repository (plan D13).
"""

import csv
import dataclasses
import io
import json
import pathlib

import pytest

import fixtures
from synthtwin import (
    contract,
    errors,
    generation,
    parsing,
    profile,
    reading,
    rendering,
    taxonomy,
    validation,
)

# The seed the battery's twins are built at. Nothing depends on the
# number; it is written out so a reader can reproduce a run by hand.
SEED = 20260813
OTHER_SEED = 20260814


# -- building one whole run -------------------------------------------


def _describe(
    folder: pathlib.Path,
    text: str,
    declared: "list[str] | None" = None,
    stem: str = "table",
    first_row: str = reading.FIRST_ROW_AUTOMATIC,
) -> contract.Profile:
    """Profile one table's text through the real producer and loader."""
    return _described(folder, text, declared, stem, first_row)[0]


def _described(
    folder: pathlib.Path,
    text: str,
    declared: "list[str] | None" = None,
    stem: str = "table",
    first_row: str = reading.FIRST_ROW_AUTOMATIC,
) -> "tuple[contract.Profile, str]":
    """The same, with the description's own bytes beside it.

    The bytes are what tells a PUBLISHED string from a MEASURED one:
    every label a result may name is one the description itself
    carries, so a string that is in neither the description nor this
    module's own fixed words is a string read out of the measured file.

    ``first_row`` chooses which reading the description is built from,
    so that a HEADERLESS description -- one whose names were generated,
    and whose twin therefore carries no header line -- can be built
    here as the profiler really builds one.
    """
    table_path = fixtures.write(folder, f"{stem}.csv", text)
    table = reading.read_table(str(table_path), first_row=first_row)
    document = profile.build_document(
        table, taxonomy.Settings(), declared if declared else []
    )
    written = fixtures.write_profile(folder, f"{stem}-profile.json", document)
    return (
        contract.load_profile(str(written)),
        written.read_text(encoding="utf-8"),
    )


def _twin_text(described: contract.Profile, seed: int = SEED) -> str:
    """The twin's exact bytes, as `synthtwin generate` would write them."""
    return rendering.twin_csv(generation.generate(described, seed))


def _measure(
    folder: pathlib.Path,
    described: contract.Profile,
    text: str,
    name: str = "twin.csv",
) -> validation.Outcome:
    """Write a measured file and measure it against a description."""
    target = fixtures.write(folder, name, text)
    return validation.measure(described, str(target))


def _verdicts(outcome: validation.Outcome, subcheck: str) -> "list[str]":
    """Every verdict filed under one subcheck identity."""
    return [
        check.verdict
        for check in outcome.checks
        if check.subcheck == subcheck
    ]


def _missed(outcome: validation.Outcome) -> "list[str]":
    """The subcheck identity of every MISSED verdict."""
    return [
        check.subcheck
        for check in outcome.checks
        if check.verdict == validation.MISSED
    ]


@pytest.fixture(scope="module")
def every_role(
    tmp_path_factory: pytest.TempPathFactory,
) -> "tuple[contract.Profile, str]":
    """The every-role description and its twin, built once."""
    folder = tmp_path_factory.mktemp("every-role")
    described = _describe(
        folder, fixtures.every_role_table(), ["record_code"]
    )
    return described, _twin_text(described)


@pytest.fixture(scope="module")
def every_role_bytes(
    tmp_path_factory: pytest.TempPathFactory,
) -> "tuple[contract.Profile, str, str]":
    """The same run, with the description's own bytes beside it."""
    folder = tmp_path_factory.mktemp("every-role-bytes")
    described, written = _described(
        folder, fixtures.every_role_table(), ["record_code"]
    )
    return described, _twin_text(described), written


# -- V8.4: the green direction ----------------------------------------


def test_a_twin_of_its_own_description_misses_nothing(
    tmp_path: pathlib.Path,
    every_role: "tuple[contract.Profile, str]",
) -> None:
    """Producer to generator to validator: zero MISSED, zero WITHHELD.

    The whole product in one line. If this fails, either the generator
    stopped meeting a published fact or the validator started asking
    for one the contract does not set -- and the named subchecks below
    say which.
    """
    described, twin = every_role
    outcome = _measure(tmp_path, described, twin)
    assert _missed(outcome) == []
    assert outcome.census.missed == 0
    assert outcome.census.withheld == 0
    assert outcome.census.held > 0


def test_the_census_counts_exactly_the_verdicts_filed(
    tmp_path: pathlib.Path,
    every_role: "tuple[contract.Profile, str]",
) -> None:
    """The summary is generated from the census and the census alone."""
    described, twin = every_role
    outcome = _measure(tmp_path, described, twin)
    counted = (
        outcome.census.held
        + outcome.census.within_bound
        + outcome.census.authorized_deviation
        + outcome.census.withheld
        + outcome.census.missed
    )
    assert counted == len(outcome.checks)
    assert outcome.census.not_checkable == len(outcome.listings)
    for check in outcome.checks:
        assert check.verdict in validation.VERDICTS


def test_a_twin_at_another_seed_still_passes(
    tmp_path: pathlib.Path,
    every_role: "tuple[contract.Profile, str]",
) -> None:
    """Seed invariance: the description is the obligation, not the seed.

    A twin regenerated at a different seed is a different file, cell for
    cell, and it owes exactly the same published facts.
    """
    described, twin = every_role
    other = _twin_text(described, OTHER_SEED)
    assert other != twin
    outcome = _measure(tmp_path, described, other)
    assert _missed(outcome) == []
    assert outcome.census.withheld == 0


def test_every_check_carries_a_known_verdict_and_a_named_subcheck(
    tmp_path: pathlib.Path,
    every_role: "tuple[contract.Profile, str]",
) -> None:
    """No check may be nameless: a red case has to be able to name it."""
    described, twin = every_role
    outcome = _measure(tmp_path, described, twin)
    for check in outcome.checks:
        assert check.subcheck
        assert check.fact
    for listing in outcome.listings:
        assert listing.fact
        assert listing.reason


# -- V8.1 and V8.2: the red battery, each case naming its subcheck ----


def _moved_cell(text: str, row: int, column: int, value: str) -> str:
    """One cell of a written table replaced, and nothing else."""
    lines = text.split("\n")
    cells = lines[row].split(",")
    cells[column] = value
    lines[row] = ",".join(cells)
    return "\n".join(lines)


def _column_of(described: contract.Profile, role: str) -> int:
    """The position of the first column of one role, or -1."""
    for column in described.columns:
        if column.role == role:
            return column.position
    return -1


def test_red_a_moved_cell_misses_the_count_it_moves(
    tmp_path: pathlib.Path,
    every_role: "tuple[contract.Profile, str]",
) -> None:
    """NAMED SUBCHECK: presence.n_present on the column that lost a cell.

    Blanking one present cell is the smallest perturbation there is,
    and it must be caught by the presence count itself rather than by
    some statistic downstream of it.
    """
    described, twin = every_role
    position = _column_of(described, taxonomy.ROLE_CATEGORICAL)
    assert position > 0
    name = described.columns[position - 1].name
    broken = _moved_cell(twin, 1, position - 1, "")
    outcome = _measure(tmp_path, described, broken)
    found = [
        check
        for check in outcome.checks
        if check.column == name and check.subcheck == "presence.n_present"
    ]
    assert len(found) == 1
    assert found[0].verdict == validation.MISSED


def test_red_a_wrong_row_count_misses_the_row_count(
    tmp_path: pathlib.Path,
    every_role: "tuple[contract.Profile, str]",
) -> None:
    """NAMED SUBCHECK: rows.n_rows."""
    described, twin = every_role
    lines = twin.split("\n")
    shorter = "\n".join(lines[: len(lines) - 2]) + "\n"
    outcome = _measure(tmp_path, described, shorter)
    assert _verdicts(outcome, "rows.n_rows") == [validation.MISSED]


def test_red_a_truncated_file_misses_the_row_count(
    tmp_path: pathlib.Path,
    every_role: "tuple[contract.Profile, str]",
) -> None:
    """NAMED SUBCHECK: rows.n_rows, on a file cut off half way."""
    described, twin = every_role
    lines = twin.split("\n")
    half = "\n".join(lines[: len(lines) // 2]) + "\n"
    outcome = _measure(tmp_path, described, half)
    assert _verdicts(outcome, "rows.n_rows") == [validation.MISSED]


def test_red_a_recased_label_misses_that_level(
    tmp_path: pathlib.Path,
    every_role: "tuple[contract.Profile, str]",
) -> None:
    """NAMED SUBCHECK: levels.<label>.variants on the re-cased level.

    The fold pools a re-cased spelling onto its own label, so the level
    COUNT still holds -- which is exactly why the variant map has to be
    the thing that catches this. A battery where only the count moved
    would be a battery that never checked the map.
    """
    described, twin = every_role
    position = _column_of(described, taxonomy.ROLE_CATEGORICAL)
    column = described.columns[position - 1]
    facts = column.facts
    assert isinstance(facts, contract.LabelFacts)
    spelling = ""
    label = ""
    for level in facts.levels:
        for written in level.variants:
            if written != written.upper():
                spelling = written
                label = level.label
                break
        if spelling:
            break
    assert spelling
    lines = twin.split("\n")
    changed = 0
    for index in range(1, len(lines)):
        cells = lines[index].split(",")
        if len(cells) > position - 1 and cells[position - 1] == spelling:
            cells[position - 1] = spelling.upper()
            lines[index] = ",".join(cells)
            changed = changed + 1
            break
    assert changed == 1
    outcome = _measure(tmp_path, described, "\n".join(lines))
    assert (
        _verdicts(outcome, f"levels.{label}.variants")
        == [validation.MISSED]
    )


def test_red_a_respelled_number_misses_its_style(
    tmp_path: pathlib.Path,
    every_role: "tuple[contract.Profile, str]",
) -> None:
    """NAMED SUBCHECK: styles.at-least.plain on the numeric column.

    Rewriting one plain cell with a decimal point leaves its VALUE
    alone, so every statistic of the column still holds. The style map
    is the only thing that can see it, which is what owner decision 10
    exists for.
    """
    described, twin = every_role
    position = _column_of(described, taxonomy.ROLE_COUNT)
    assert position > 0
    name = described.columns[position - 1].name
    lines = twin.split("\n")
    changed = False
    for index in range(1, len(lines)):
        cells = lines[index].split(",")
        if len(cells) <= position - 1:
            continue
        body = cells[position - 1]
        if body and parsing.numeric_style(body) == parsing.STYLE_PLAIN:
            cells[position - 1] = f"{body}.0"
            lines[index] = ",".join(cells)
            changed = True
            break
    assert changed
    outcome = _measure(tmp_path, described, "\n".join(lines))
    found = [
        check
        for check in outcome.checks
        if check.column == name
        and check.subcheck == "styles.at-least.plain"
    ]
    assert len(found) == 1
    assert found[0].verdict == validation.MISSED


def test_a_respelled_pooled_cell_is_withheld_because_nothing_can_see_it(
    tmp_path: pathlib.Path,
) -> None:
    """REVIEW ITEM P3-V2-D-F2, and what it costs P3-V1-F7's clause.

    This test used to assert MISSED here, and the assertion was outside
    what the report may say. Ten `1`s beside `1.5` and `2.5` publish
    `numeric_styles` as the single withheld key: every cell of the
    column is POOLED. Re-spelling one pooled cell `1.50` where its
    value's canonical text is `1.5` leaves the cell in the same form and
    the same value, so `synthtwin profile` writes the SAME description
    for the two files, byte for byte -- which this test now proves
    rather than assumes. V5.1 says the report may state about a measured
    file only what describing that file would publish about it, so a
    verdict that told those two files apart would be stating what no
    description of either carries -- which is what ONE report may not
    say, to a reader who may hold no file, and is the whole ground this
    stands on. The sentence that used to follow it here, about repeated
    candidate descriptions reading the count off the verdicts, is out of
    scope from 2026-08-14 (V5-A1; plan amendment A-P3-13).

    THE CLAUSE IS NOT GONE, AND THE SECOND HALF OF THIS TEST IS THE
    PROOF. The same description still makes the subcheck MISS on a file
    whose own description NAMES the form -- eleven decimal cells reach
    the publication floor, so that file's own description carries a
    `decimal` count and the ceiling is settled against it. What is lost
    is the verdict on a file that keeps the form under the floor, and
    plan amendment A-P3-3 records that in those words.
    """
    folder = tmp_path / "pooled"
    folder.mkdir()
    values = ["1" for _index in range(10)] + ["1.5", "2.5"]
    described = _describe(
        folder,
        fixtures.single_column_table("reading", values),
        stem="pooled",
    )
    facts = described.columns[0].facts
    assert isinstance(facts, contract.NumericFacts)
    assert facts.numeric_styles == {taxonomy.SUPPRESSED_LABEL: 12}
    twin = _twin_text(described)
    good = _measure(folder, described, twin, "pooled-twin.csv")
    assert _missed(good) == []
    # One pooled cell re-spelled into a non-canonical text of the SAME
    # style and the SAME value.
    lines = twin.split("\n")
    changed = 0
    for index in range(1, len(lines)):
        body = lines[index]
        if not body:
            continue
        if parsing.numeric_style(body) != parsing.STYLE_DECIMAL:
            continue
        lines[index] = f"{body}0"
        changed = changed + 1
        break
    assert changed == 1
    respelled = "\n".join(lines)
    # THE TWO FILES DESCRIBE IDENTICALLY. This is the whole reason the
    # verdict may not be shown, so it is measured here and not asserted
    # from memory.
    assert _own_description(folder, respelled, "pooled-odd") == (
        _own_description(folder, twin, "pooled-same")
    )
    bad = _measure(folder, described, respelled, "pooled-odd.csv")
    assert _verdicts(bad, "styles.canonical.decimal") == [
        validation.WITHHELD
    ]
    for check in bad.checks:
        if check.subcheck != "styles.canonical.decimal":
            continue
        assert check.citation == validation._GATE_POOLED
    # ...and the same description still has a file this subcheck misses
    # on: eleven cells in the form reach the publication floor, so the
    # file's own description names it and the ceiling is settled.
    named = ["1" for _index in range(1)] + [
        f"{index + 1}.50" for index in range(11)
    ]
    over = _measure(
        folder,
        described,
        fixtures.single_column_table("reading", named),
        "pooled-named.csv",
    )
    assert _verdicts(over, "styles.canonical.decimal") == [validation.MISSED]


def _own_description(
    folder: pathlib.Path, text: str, stem: str
) -> str:
    """What `synthtwin profile` writes about one file, as its bytes.

    The disclosure envelope of V5.1 is exactly this string: a report may
    state about a measured file only what describing that file would
    publish. Two files this returns the same bytes for are two files
    whose reports may not differ.
    """
    return _described(folder, text, None, stem, reading.FIRST_ROW_NAMES)[1]


def test_two_files_one_description_get_one_report(
    tmp_path: pathlib.Path,
) -> None:
    """REVIEW ITEM P3-V2-D-F2, as the property it violates (V5.1).

    The witness the reviewer ran: forty numbers, thirty-nine of them
    plain, differing only in whether the fortieth was written `1E5` or
    `1e5`. Both spellings are pooled -- one cell is under any
    publication floor -- so `synthtwin profile` writes the same
    description for the two files, byte for byte. The version this
    tests against gave them different verdicts on five style subchecks,
    different censuses and different screen output, which states about
    each file which form its pooled cell wore. Nine of the ten style
    subchecks recounted the written cells and compared the recount with
    a number the SUBMITTED description chose, so ONE report was enough
    to separate two files the producer describes byte for byte alike.

    The property is the general one and not the witness: where the two
    files describe identically, the two reports are identical.
    """
    folder = tmp_path / "twinned"
    folder.mkdir()
    plain = [f"{100 + index}" for index in range(39)]
    upper = fixtures.single_column_table("amount", plain + ["1E5"])
    lower = fixtures.single_column_table("amount", plain + ["1e5"])
    assert _own_description(folder, upper, "upper") == _own_description(
        folder, lower, "lower"
    )
    submitted = _describe(
        folder,
        fixtures.single_column_table(
            "amount", [f"{100 + index}" for index in range(40)]
        ),
        stem="submitted",
    )
    first = _measure(folder, submitted, upper, "upper.csv")
    second = _measure(folder, submitted, lower, "lower.csv")
    assert first.checks == second.checks
    assert first.listings == second.listings
    assert first.census == second.census


def test_no_candidate_description_can_pin_a_pooled_style_count(
    tmp_path: pathlib.Path,
) -> None:
    """REVIEW ITEM P3-V2-D-F2, witness B, kept as a CONSEQUENCE.

    Two plain cells, one leading-zero cell and thirty-seven decimal ones
    publish `{(withheld): 3, decimal: 37}`: the two-and-one split is
    pooled and no description of that file names it. The reviewer walked
    six candidate descriptions differing only in their style map and
    found exactly one that held -- which pins the plain count at two and
    the leading-zero count at one, both under a floor of eleven and both
    withheld by the producer.

    WHY THIS IS STILL HERE AFTER V5-A1 (owner ruling 2026-08-14, plan
    amendment A-P3-13). The ruling stops promising anything about a
    person who submits descriptions of their own; it is not this test's
    ground and never was the ground of the gate this exercises. The gate
    withholds these subchecks in EVERY SINGLE REPORT, because the count
    they compare is one the file's own description pools -- and a
    sequence of reports that each say nothing says nothing in sequence
    either. So the property below is a consequence of the rule that
    still binds, and it is asserted rather than argued because the
    consequence is the readable form of it.

    The assertion is not that the search fails on these six candidates:
    it is that no candidate settles a style subcheck of that column at
    all, so there is nothing for a search to be run over.
    """
    folder = tmp_path / "search"
    folder.mkdir()
    values = ["100", "101", "007"] + [
        f"{200 + index}.5" for index in range(37)
    ]
    text = fixtures.single_column_table("amount", values)
    described, _ = _described(folder, text, None, "search")
    facts = described.columns[0].facts
    assert isinstance(facts, contract.NumericFacts)
    assert facts.numeric_styles == {
        taxonomy.SUPPRESSED_LABEL: 3,
        parsing.STYLE_DECIMAL: 37,
    }
    settled: list[str] = []
    for decimal in range(35, 40):
        candidate = _with_styles(
            folder,
            _described(folder, text, None, "search")[1],
            f"cand-{decimal}",
            {
                taxonomy.SUPPRESSED_LABEL: 40 - decimal,
                parsing.STYLE_DECIMAL: decimal,
            },
        )
        outcome = _measure(folder, candidate, text, f"cand-{decimal}.csv")
        for check in outcome.checks:
            pooled = check.subcheck in ("styles.spill", "styles.remainder")
            if pooled and check.verdict != validation.WITHHELD:
                settled = settled + [
                    (
                        f"decimal={decimal}: {check.subcheck} "
                        f"{check.verdict}"
                    )
                ]
    assert not settled, (
        "a candidate description settled a subcheck whose count the "
        "file's own description pools, so one report states a count "
        f"that description withholds (V5.1): {settled}"
    )


def _with_styles(
    folder: pathlib.Path,
    written: str,
    stem: str,
    styles: "dict[str, int]",
) -> contract.Profile:
    """One written description with its first column's style map replaced.

    The candidate is built as a FILE and reloaded through the strict
    loader, because a description an attacker submits is a file and has
    to survive every invariant that loader enforces -- which is what
    keeps this search honest about what can actually be asked.
    """
    document = json.loads(written)
    document["columns"][0]["numeric_styles"] = styles
    target = fixtures.write_profile(folder, f"{stem}.json", document)
    return contract.load_profile(str(target))


def _mixed_numeric_column(
    folder: pathlib.Path, stem: str
) -> contract.Profile:
    """A numeric column publishing BOTH point-free and decimal counts.

    Forty whole values and twenty halves, so `numeric_styles` names
    `plain` and `decimal` and neither count is the column's own cell
    count. That is the shape the canonical ceiling can be exceeded on,
    and the shape `test_the_canonical_split_still_licenses_the_published_counts`
    needs to say anything at all.
    """
    values = [f"{index % 40 + 1}" for index in range(40)]
    values = values + [f"{index % 20 + 1}.5" for index in range(20)]
    return _describe(
        folder, fixtures.single_column_table("amount", values), stem=stem
    )


def test_the_canonical_split_still_licenses_the_published_counts(
    tmp_path: pathlib.Path,
) -> None:
    """...and the ceiling is the PUBLISHED count, not zero.

    The clause is a ceiling on non-canonical cells, and the published
    count is what raises it: a column that publishes `decimal` cells has
    bought exactly that many spellings of its own choosing, and a check
    that refused them would accuse the generator of doing what the
    description asked for. The pair matters as much as the red case
    does.

    THE LICENSE IS SPENT IN FULL HERE, which is what makes this the
    ceiling's own test rather than a second green run: every decimal
    cell of the twin is re-spelled with a leading zero -- owner decision
    8's invention family, which the contract's ladder still counts as
    `decimal` and which reads back as the same number -- so the count of
    non-canonical cells lands exactly ON the published count and the
    check holds.
    """
    folder = tmp_path / "licensed"
    folder.mkdir()
    described = _mixed_numeric_column(folder, "licensed")
    facts = described.columns[0].facts
    assert isinstance(facts, contract.NumericFacts)
    published = facts.numeric_styles.get(parsing.STYLE_DECIMAL, 0)
    assert 0 < published < described.n_rows
    twin = _twin_text(described)
    outcome = _measure(folder, described, twin, "licensed-twin.csv")
    assert _verdicts(outcome, "styles.canonical.decimal") == [validation.HELD]
    assert _missed(outcome) == []
    lines = twin.split("\n")
    spent = 0
    for index in range(1, len(lines)):
        body = lines[index]
        if not body:
            continue
        if parsing.numeric_style(body) != parsing.STYLE_DECIMAL:
            continue
        lines[index] = f"0{body}"
        spent = spent + 1
    assert spent == published
    licensed = _measure(folder, described, "\n".join(lines), "licensed-odd.csv")
    assert _verdicts(licensed, "styles.canonical.decimal") == [validation.HELD]
    assert _verdicts(licensed, "styles.spelled") == [validation.HELD]


def _over_the_licence(
    described: contract.Profile, twin: str, extra: int
) -> str:
    """The twin with every decimal cell padded and ``extra`` more made one.

    The licence is spent in full first -- every published `decimal` cell
    written with a leading zero, which the contract's ladder still counts
    as `decimal` and which reads back as the same number -- and then
    ``extra`` point-free cells are re-written as non-canonical decimals.
    So the file's non-canonical count in that form is the published count
    plus ``extra``, exactly.
    """
    lines = twin.split("\n")
    added = 0
    for index in range(1, len(lines)):
        body = lines[index]
        if not body:
            continue
        style = parsing.numeric_style(body)
        if style == parsing.STYLE_DECIMAL:
            lines[index] = f"0{body}"
            continue
        if style == parsing.STYLE_PLAIN and added < extra:
            lines[index] = f"0{body}.0"
            added = added + 1
    assert added == extra, (added, extra)
    return "\n".join(lines)


def test_red_one_cell_over_the_licence_breaks_the_ceiling(
    tmp_path: pathlib.Path,
) -> None:
    """NAMED SUBCHECK: styles.canonical.decimal, one cell over its licence.

    The other side of the pair above, AND THE BAR IT IS BACK AT (owner
    ruling 2026-08-14; plan amendment A-P3-13 clause 2, which withdraws
    A-P3-10 clause 1). Between two rounds this subcheck read its recount
    at the publication floor's own resolution, so that a person trying
    one candidate description after another could locate the count no
    closer than a floor-wide block -- and the price, recorded in those
    words, was that a file between ONE cell and one floor over its
    licence stopped being missed here. The owner ruled that person out of
    scope, so the recount is compared exactly again and the teeth are
    back at one cell.

    Both halves are pinned, because the direction matters as much as the
    teeth:

    * ONE cell over the licence MISSES;
    * a whole floor over misses too, so nothing turns on where inside a
      block the count sits;
    * and the file that spends its licence exactly is still HELD, which
      is the test above -- a stricter comparison may not reach a
      conforming twin.
    """
    folder = tmp_path / "over"
    folder.mkdir()
    described = _mixed_numeric_column(folder, "over")
    facts = described.columns[0].facts
    assert isinstance(facts, contract.NumericFacts)
    assert 0 < facts.numeric_styles.get(parsing.STYLE_DECIMAL, 0), (
        "the description licenses no decimal cell at all, so this file "
        "is over its licence at the first one and the pair proves nothing"
    )
    floor = described.settings.small_cell_floor
    assert floor > 1, "a floor of one is the identity and pins nothing"
    twin = _twin_text(described)
    one = _measure(
        folder, described, _over_the_licence(described, twin, 1), "one.csv"
    )
    assert _verdicts(one, "styles.canonical.decimal") == [
        validation.MISSED
    ], (
        "one cell over the licence is not missed, so the teeth amendment "
        "A-P3-13 clause 2 buys back are not there"
    )
    outcome = _measure(
        folder,
        described,
        _over_the_licence(described, twin, floor),
        "over-twin.csv",
    )
    assert _verdicts(outcome, "styles.canonical.decimal") == [
        validation.MISSED
    ]


def test_the_canonical_ceiling_is_a_listing_where_it_licenses_every_cell(
    tmp_path: pathlib.Path,
) -> None:
    """REVIEW ITEM P3-V2-C-F1: the ceiling that admitted every file.

    Where the description publishes as many cells of a form as the file
    has rows, the ceiling is every cell there is: no file of the
    published length can be over it, and the shipped validator counted
    the line HELD on every run. The pooled fixture's red case passed
    because its published count is zero, so the repair of P3-V1-F7 was
    green on a description shaped like the one it was written for and
    vacuous on the ordinary one.

    So the entry is a listing on such a description -- carried in the
    NOT-CHECKABLE census with the sentence that says why -- and never a
    verdict. The per-cell obligation it used to be confused with is
    `styles.spelled`, which is checked here and on every numeric column.
    """
    folder = tmp_path / "ceiling"
    folder.mkdir()
    values = [f"{index % 20}.5" for index in range(60)]
    described = _describe(
        folder,
        fixtures.single_column_table("amount", values),
        stem="ceiling",
    )
    facts = described.columns[0].facts
    assert isinstance(facts, contract.NumericFacts)
    assert (
        facts.numeric_styles.get(parsing.STYLE_DECIMAL, 0) == described.n_rows
    )
    outcome = _measure(
        folder, described, _twin_text(described), "ceiling-twin.csv"
    )
    assert _verdicts(outcome, "styles.canonical.decimal") == []
    listed = [
        listing
        for listing in outcome.listings
        if listing.subcheck == "styles.canonical.decimal"
    ]
    assert len(listed) == 1
    assert listed[0].fact == "numeric.numeric_styles"
    assert listed[0].reason
    assert _verdicts(outcome, "styles.spelled") == [validation.HELD]
    assert _missed(outcome) == []


def test_the_spelling_family_accepts_every_spelling_the_generator_writes(
) -> None:
    """The other half of `styles.spelled`: it may not accuse a twin.

    A check counting cells "in no permitted spelling" is only honest if
    the set of permitted spellings is the method's whole family, and the
    validator writes that family out from method G6.1 and G6.3 rather
    than importing the generator's copy (V1.4, V4.2). Two texts written
    from one document drift, and the direction this one would drift in
    is a MISSED verdict against a conforming twin.

    So the two are compared HERE, where both may be imported: every one
    of the six styles, at leading-zero orders zero to three, over values
    that pin G6.2's own boundaries -- the fixed-point window at both
    ends, a whole value far outside it, zero, a negative, and a value
    whose shortest round trip is sixteen figures long. Every text the
    generator writes must be a text the validator's family holds.
    """
    values = (
        0.0,
        -0.0,
        5.0,
        -2.5,
        0.0001,
        1e-05,
        1e16,
        1e20,
        1000000000000000.0,
        66.6013870196064,
        -1.7976931348623157e308,
    )
    styles = (
        parsing.STYLE_PLAIN,
        parsing.STYLE_LEADING_ZERO,
        parsing.STYLE_LEADING_PLUS,
        parsing.STYLE_DECIMAL,
        parsing.STYLE_EXPONENT_LOWER,
        parsing.STYLE_EXPONENT_UPPER,
    )
    seen = 0
    for whole_column in (False, True):
        for value in values:
            if whole_column and value != int(value):
                continue
            family = validation._permitted_spellings(value, whole_column)
            for style in styles:
                for order in range(4):
                    written = generation._styled_number(
                        value, style, order, whole_column
                    )
                    assert parsing.parse_number(written) == value, written
                    assert any(
                        validation._wears(written, spelling)
                        for spelling in family
                    ), (
                        f"the generator writes {written!r} for {value!r} in "
                        f"the {style} style at order {order}, and the "
                        f"validator's spelling family does not hold it -- so "
                        f"a conforming twin would be reported as carrying a "
                        f"cell in no published form"
                    )
                    seen = seen + 1
    assert seen > 200


def test_red_a_trailing_zero_on_every_cell_is_in_no_published_form(
    tmp_path: pathlib.Path,
) -> None:
    """NAMED SUBCHECK: styles.spelled. The witness of P3-V2-C-F1.

    Two hundred and forty decimal cells, each given one trailing zero:
    the same numbers, the same forms, the same counts, and a text that
    is not the shortest round trip of its own value. Method G6.1 says a
    numeric cell is written in exactly one of six styles "and in no
    other form", and G6.3 fixes what each of the six writes. Until this
    subcheck existed the file validated with exit 0 under "NO CHECKABLE
    OBLIGATION WAS MISSED", because every check in the validator was
    arithmetic over counts and the ceiling above licensed every cell.
    """
    folder = tmp_path / "padded"
    folder.mkdir()
    values = [f"{index % 20}.5" for index in range(60)]
    described = _describe(
        folder,
        fixtures.single_column_table("amount", values),
        stem="padded",
    )
    twin = _twin_text(described)
    lines = twin.split("\n")
    changed = 0
    for index in range(1, len(lines)):
        if not lines[index]:
            continue
        lines[index] = f"{lines[index]}0"
        changed = changed + 1
    assert changed == described.n_rows
    outcome = _measure(folder, described, "\n".join(lines), "padded-twin.csv")
    assert _verdicts(outcome, "styles.spelled") == [validation.MISSED]
    # ...and the cells still read back as exactly the same numbers, so
    # nothing about the column's shape moved: this is a spelling fault
    # and the report says so rather than blaming the ladder.
    assert _verdicts(outcome, "ladder.min") == [validation.HELD]
    assert _verdicts(outcome, "ladder.max") == [validation.HELD]
    assert _verdicts(outcome, "counts.n_numeric") == [validation.HELD]


def test_red_a_shifted_date_misses_a_ladder_end(
    tmp_path: pathlib.Path,
    every_role: "tuple[contract.Profile, str]",
) -> None:
    """NAMED SUBCHECK: ends.latest on the datetime column.

    Every cell of the column moved forward by a decade: the two ends of
    a column of dates carry no authorization at all, so this cannot
    land anywhere but MISSED.
    """
    described, twin = every_role
    position = _column_of(described, taxonomy.ROLE_DATETIME)
    assert position > 0
    name = described.columns[position - 1].name
    lines = twin.split("\n")
    for index in range(1, len(lines)):
        cells = lines[index].split(",")
        if len(cells) <= position - 1:
            continue
        body = cells[position - 1]
        if len(body) >= 4 and body[:2] == "20":
            cells[position - 1] = f"20{int(body[2:4]) + 10:02d}{body[4:]}"
            lines[index] = ",".join(cells)
    outcome = _measure(tmp_path, described, "\n".join(lines))
    found = [
        check
        for check in outcome.checks
        if check.column == name and check.subcheck == "ends.latest"
    ]
    assert len(found) == 1
    assert found[0].verdict == validation.MISSED


def test_red_reordered_columns_miss_the_column_order(
    tmp_path: pathlib.Path,
    every_role: "tuple[contract.Profile, str]",
) -> None:
    """NAMED SUBCHECK: columns.order."""
    described, twin = every_role
    lines = twin.split("\n")
    swapped = []
    for line in lines:
        if not line:
            swapped.append(line)
            continue
        cells = line.split(",")
        cells[0], cells[1] = cells[1], cells[0]
        swapped.append(",".join(cells))
    outcome = _measure(tmp_path, described, "\n".join(swapped))
    assert _verdicts(outcome, "columns.order") == [validation.MISSED]


def test_red_an_injected_byte_order_mark_misses_the_byte_rule(
    tmp_path: pathlib.Path,
    every_role: "tuple[contract.Profile, str]",
) -> None:
    """NAMED SUBCHECK: bytes.byte-order-mark.

    The reader strips a UTF-8 mark transparently, so every other check
    still passes; this one is the only thing between a twin and a file
    no second tool will read the same way.
    """
    described, twin = every_role
    target = tmp_path / "marked.csv"
    target.write_bytes(b"\xef\xbb\xbf" + twin.encode("utf-8"))
    outcome = validation.measure(described, str(target))
    assert _verdicts(outcome, "bytes.byte-order-mark") == [validation.MISSED]


def test_red_carriage_returns_miss_the_line_ending_rule(
    tmp_path: pathlib.Path,
    every_role: "tuple[contract.Profile, str]",
) -> None:
    """NAMED SUBCHECK: bytes.line-endings."""
    described, twin = every_role
    target = tmp_path / "crlf.csv"
    target.write_bytes(twin.replace("\n", "\r\n").encode("utf-8"))
    outcome = validation.measure(described, str(target))
    assert _verdicts(outcome, "bytes.line-endings") == [validation.MISSED]


def test_red_a_missing_terminal_newline_misses_that_rule(
    tmp_path: pathlib.Path,
    every_role: "tuple[contract.Profile, str]",
) -> None:
    """NAMED SUBCHECK: bytes.terminal-newline."""
    described, twin = every_role
    outcome = _measure(
        tmp_path, described, twin[: len(twin) - 1], "no-newline.csv"
    )
    assert _verdicts(outcome, "bytes.terminal-newline") == [validation.MISSED]


def test_red_an_edited_header_misses_the_header_names(
    tmp_path: pathlib.Path,
    every_role: "tuple[contract.Profile, str]",
) -> None:
    """NAMED SUBCHECK: header.names."""
    described, twin = every_role
    lines = twin.split("\n")
    cells = lines[0].split(",")
    cells[0] = f"{cells[0]}_x"
    lines[0] = ",".join(cells)
    outcome = _measure(tmp_path, described, "\n".join(lines))
    assert _verdicts(outcome, "header.names") == [validation.MISSED]


def test_red_a_removed_header_misses_the_header_presence(
    tmp_path: pathlib.Path,
) -> None:
    """NAMED SUBCHECK: header.presence, on a headered twin with no header.

    Review item P3-V1-F8. The check this replaces compared the file's
    first line with the names the reader had just DERIVED from that
    line, so the two agreed whatever the file held and this
    perturbation -- the plainest one there is -- reported HELD.
    Neighbouring checks caught the file; the named one slept, which V8.2
    calls a red battery.

    The column here holds a value in every row, so the file with its
    header taken off still reads as a table and the reader returns it.
    That is deliberate: it puts the perturbation through
    `_header_presence` itself rather than through the structural path
    that catches a first row which cannot name columns at all.
    """
    folder = tmp_path / "header"
    folder.mkdir()
    described = _describe(
        folder,
        fixtures.single_column_table(
            "reading", fixtures.numbers(71, 60, 1, 400)
        ),
        stem="headed",
    )
    twin = _twin_text(described)
    good = _measure(folder, described, twin, "headed-twin.csv")
    assert _verdicts(good, "header.presence") == [validation.HELD]
    lines = twin.split("\n")
    bad = _measure(
        folder, described, "\n".join(lines[1:]), "no-header.csv"
    )
    assert _verdicts(bad, "header.presence") == [validation.MISSED]


def test_red_a_header_written_into_a_headerless_file_misses_presence(
    tmp_path: pathlib.Path,
) -> None:
    """NAMED SUBCHECK: header.presence, in the other direction.

    A description whose names were GENERATED asks for a file with no
    header line at all, and the check has to be able to fail that way
    too: the version this replaces returned the expected words
    unconditionally in this mode, so nothing whatever could move it.
    """
    folder = tmp_path / "headerless"
    folder.mkdir()
    values = fixtures.numbers(61, 40, 1, 9)
    described = _describe(
        folder,
        "\n".join(values) + "\n",
        stem="bare",
        first_row=reading.FIRST_ROW_DATA,
    )
    assert described.source.header_source == reading.HEADER_GENERATED
    twin = _twin_text(described)
    good = _measure(folder, described, twin, "bare-twin.csv")
    assert _verdicts(good, "header.presence") == [validation.HELD]
    written = [column.name for column in described.columns]
    injected = ",".join(written) + "\n" + twin
    bad = _measure(folder, described, injected, "bare-headed.csv")
    assert _verdicts(bad, "header.presence") == [validation.MISSED]


def _headerless_pair(
    folder: pathlib.Path,
) -> "tuple[contract.Profile, str]":
    """A description whose names were generated, and its twin."""
    values = fixtures.numbers(61, 40, 1, 9)
    described = _describe(
        folder,
        "\n".join(values) + "\n",
        stem="bare",
        first_row=reading.FIRST_ROW_DATA,
    )
    assert described.source.header_source == reading.HEADER_GENERATED
    return described, _twin_text(described)


def test_red_a_header_written_in_and_a_row_taken_out_misses_presence(
    tmp_path: pathlib.Path,
) -> None:
    """NAMED SUBCHECK: header.presence. REVIEW ITEM P3-V2-C-F8.

    The headerless half of this check used to ask for TWO things at
    once: a first line reading back as the published names, AND a file
    holding more rows than the description publishes. A conjunction is
    only as strong as the conjunct an editor can pay off separately, and
    this is the payment -- the header line goes in, one record comes
    out, the row count lands exactly where the description puts it, and
    the check reported "no header line, the first row is a record" about
    a file whose first line was the published names. It stated the
    opposite of the truth about the bytes it governs, defeated by the
    exact perturbation class it exists for.

    The row count is not a conjunct now; it is `rows.n_rows`, which
    misses on its own terms and holds here, which is the point.
    """
    folder = tmp_path / "compensated"
    folder.mkdir()
    described, twin = _headerless_pair(folder)
    written = [column.name for column in described.columns]
    lines = [line for line in twin.split("\n") if line]
    swapped = ",".join(written) + "\n" + "\n".join(lines[: len(lines) - 1])
    outcome = _measure(folder, described, swapped + "\n", "compensated.csv")
    assert _verdicts(outcome, "rows.n_rows") == [validation.HELD]
    assert _verdicts(outcome, "columns.n_columns") == [validation.HELD]
    assert _verdicts(outcome, "header.presence") == [validation.MISSED]


def test_the_first_column_of_a_headerless_description_is_listed(
    tmp_path: pathlib.Path,
) -> None:
    """REVIEW ITEM P3-V2-C-F7: a position no file could be wrong about.

    `position.at` has two failure branches, and where the names were
    generated only one is live -- the file stops before this column
    number. Nothing stops before the FIRST column: a file carrying no
    columns at all is refused by the reader before any verdict exists,
    so on the first column of a headerless description the check had an
    empty failure set and reported HELD on every file that reached it.

    It is a listing entry there, and nowhere else: the second and later
    columns of the same description are still checked, and a file that
    stops short still misses them (`test_a_missing_column_...` and the
    entry table's own registered case). Plan amendment A-P3-2 records
    the lowering in those words.
    """
    folder = tmp_path / "first"
    folder.mkdir()
    described, twin = _headerless_pair(folder)
    assert described.n_columns == 1
    outcome = _measure(folder, described, twin, "bare-first.csv")
    assert _verdicts(outcome, "position.at") == []
    listed = [
        listing
        for listing in outcome.listings
        if listing.subcheck == "position.at"
    ]
    assert len(listed) == 1
    assert listed[0].column == described.columns[0].name
    assert listed[0].fact == "universal.position"
    assert listed[0].reason


def test_a_later_headerless_column_still_carries_its_position(
    tmp_path: pathlib.Path,
) -> None:
    """...and the narrowing is the first column and nothing else.

    A two-column headerless description keeps `position.at` on its
    second column, and a file that stops before it misses.
    """
    folder = tmp_path / "second"
    folder.mkdir()
    rows = [
        f"{value},{fixtures.REGIONS[index % 4]}"
        for index, value in enumerate(fixtures.numbers(41, 60, 1, 400))
    ]
    described = _describe(
        folder,
        "\n".join(rows) + "\n",
        stem="two",
        first_row=reading.FIRST_ROW_DATA,
    )
    assert described.n_columns == 2
    second = described.columns[1].name
    twin = _twin_text(described)
    good = _measure(folder, described, twin, "two-twin.csv")
    assert [
        check.column
        for check in good.checks
        if check.subcheck == "position.at"
    ] == [second]
    narrowed = []
    for line in twin.split("\n"):
        if not line:
            narrowed.append(line)
            continue
        narrowed.append(line.split(",")[0])
    bad = _measure(folder, described, "\n".join(narrowed), "two-narrow.csv")
    missed = [
        check.column
        for check in bad.checks
        if check.subcheck == "position.at"
        and check.verdict == validation.MISSED
    ]
    assert missed == [second]


def test_a_skew_window_that_admits_every_value_is_listed(
    tmp_path: pathlib.Path,
    every_role: "tuple[contract.Profile, str]",
) -> None:
    """REVIEW ITEM P3-V2-C-F2: a window equal to the attainable range.

    Method G12.3 ends with a finite fallback: where the published
    ladder's own spread does not exceed the displacement the
    construction can produce, the skew bound becomes the range EVERY
    sample of that many values lies in whatever they are. G12.3 is right
    to PRINT that -- a wide bound tells a reader the ladder is too
    coarse to say anything about the shape -- but a CHECK against it
    admits every file there is, and the shipped validator counted it
    WITHIN-BOUND on every run. Measured by the review: a column rewritten
    to two hundred and twenty-seven ones, one nine and one hundred
    thousand achieved the endpoint itself and was still called inside.

    The validator may not draw a narrower window of its own -- V1 says
    every APPROXIMATED bound lives in G12 and is cited, never restated,
    so a tighter envelope is a change to the generation method and not
    an invention in the thing that checks it. So the entry is a listing
    with the sentence that says why, and the two moments whose windows
    do bite are checked exactly as before.
    """
    described, twin = every_role
    outcome = _measure(tmp_path, described, twin, "skew-twin.csv")
    # THE COLUMN THE REVIEW MEASURED IT ON. `visits` publishes a ladder
    # of whole counts whose own spread the displacement reaches, so the
    # quotient of G12.3 has no finite end and its finite fallback
    # stands; `amount` publishes a ladder that describes it, so its
    # window bites and its check is made exactly as before.
    listed = {
        listing.column
        for listing in outcome.listings
        if listing.subcheck == "moments.skew"
    }
    checked = {
        check.column
        for check in outcome.checks
        if check.subcheck == "moments.skew"
    }
    assert "visits" in listed
    assert "visits" not in checked
    assert "amount" in checked
    assert "amount" not in listed
    for listing in outcome.listings:
        if listing.subcheck != "moments.skew":
            continue
        assert listing.fact == "numeric.skew"
        assert listing.reason
    # ...and the two moments whose windows bite are checked on the very
    # column whose skew is listed, so this narrows one bound and not the
    # column's whole shape.
    assert [
        check.verdict
        for check in outcome.checks
        if check.subcheck == "moments.mean" and check.column == "visits"
    ] == [validation.WITHIN_BOUND]
    assert [
        check.verdict
        for check in outcome.checks
        if check.subcheck == "moments.std" and check.column == "visits"
    ] == [validation.WITHIN_BOUND]


def test_a_skew_window_narrower_than_the_range_is_still_checked(
    tmp_path: pathlib.Path,
) -> None:
    """...and the listing is the coarse ladder, never the fact.

    A column whose ladder describes it keeps its skew check, and a file
    whose shape leaves the window misses it. That pair is what says the
    line above narrows one description rather than retiring an
    obligation.
    """
    folder = tmp_path / "shaped"
    folder.mkdir()
    described = _describe(
        folder,
        fixtures.single_column_table(
            "reading", fixtures.numbers(83, 200, 1, 4000)
        ),
        stem="shaped",
    )
    twin = _twin_text(described)
    good = _measure(folder, described, twin, "shaped-twin.csv")
    assert _verdicts(good, "moments.skew") == [validation.WITHIN_BOUND]
    lines = twin.split("\n")
    numbers = [
        float(line) for line in lines[1:] if line
    ]
    low = min(numbers)
    high = max(numbers)
    crowded = [lines[0]]
    step = 0
    for line in lines[1:]:
        if not line:
            crowded.append(line)
            continue
        share = step / (len(numbers) - 1)
        crowded.append(f"{low + (high - low) * share * share * share}")
        step = step + 1
    bad = _measure(folder, described, "\n".join(crowded), "shaped-bad.csv")
    assert _verdicts(bad, "moments.skew") == [validation.MISSED]


def test_red_a_dropped_column_misses_the_column_count(
    tmp_path: pathlib.Path,
    every_role: "tuple[contract.Profile, str]",
) -> None:
    """NAMED SUBCHECK: columns.n_columns."""
    described, twin = every_role
    lines = []
    for line in twin.split("\n"):
        if not line:
            lines.append(line)
            continue
        cells = line.split(",")
        lines.append(",".join(cells[: len(cells) - 1]))
    outcome = _measure(tmp_path, described, "\n".join(lines))
    assert _verdicts(outcome, "columns.n_columns") == [validation.MISSED]


def test_the_red_battery_covers_several_classes_of_perturbation(
    tmp_path: pathlib.Path,
    every_role: "tuple[contract.Profile, str]",
) -> None:
    """V8.5's vacuity floor: the battery cannot rot into one mutation.

    A counted floor of distinct perturbation CLASSES, so that a battery
    which quietly collapsed into eleven copies of one edit is red here
    rather than green everywhere.
    """
    described, twin = every_role
    classes = {
        "cell": _moved_cell(twin, 1, 1, ""),
        "rows": "\n".join(twin.split("\n")[:-2]) + "\n",
        "header": twin.replace(
            twin.split("\n")[0], twin.split("\n")[0].upper(), 1
        ),
        "newline": twin[: len(twin) - 1],
    }
    seen = set()
    for name in sorted(classes):
        outcome = _measure(tmp_path, described, classes[name], f"{name}.csv")
        for subcheck in _missed(outcome):
            seen.add(subcheck)
    assert len(seen) >= 4


# -- V8.4 and P3-D4: the pairing battery ------------------------------


def test_a_twin_of_one_description_against_another_misses(
    tmp_path: pathlib.Path,
) -> None:
    """Twin of A against B: at least one MISSED, and never a clean pass.

    A and B are a deliberately mismatching pair -- different widths,
    different roles -- so at least one checkable obligation cannot hold.
    This is not a claim about arbitrary pairs; it is a claim about this
    one, which is why the pair is built here rather than assumed.
    """
    folder = tmp_path / "pair"
    folder.mkdir()
    first = _describe(
        folder,
        fixtures.single_column_table(
            "reading", fixtures.numbers(11, 60, 1, 400)
        ),
        stem="a",
    )
    second = _describe(
        folder,
        fixtures.rows_to_csv(
            ["reading", "region"],
            [
                [value, fixtures.REGIONS[index % 4]]
                for index, value in enumerate(
                    fixtures.numbers(12, 60, 1, 400)
                )
            ],
        ),
        stem="b",
    )
    outcome = _measure(folder, second, _twin_text(first), "crossed.csv")
    assert outcome.census.missed >= 1
    assert _missed(outcome) != []


def test_a_real_table_against_its_own_description_is_measured(
    tmp_path: pathlib.Path,
) -> None:
    """The table a description was built from, validated against it.

    The battery records the outcome rather than asserting a verdict:
    nothing in a CSV proves provenance, and the validator cannot tell a
    synthetic file from a real one. What IS asserted is that the run
    completes and produces verdicts, because a command that refused
    here would be refusing the ordinary mistake it exists to survive.
    """
    text = fixtures.every_role_table(n_rows=60)
    described = _describe(tmp_path, text, ["record_code"])
    outcome = _measure(tmp_path, described, text, "same.csv")
    assert len(outcome.checks) > 0
    assert outcome.census.held > 0


# -- V5: the disclosure gate ------------------------------------------


def test_no_string_from_the_measured_file_reaches_any_check(
    tmp_path: pathlib.Path,
    every_role_bytes: "tuple[contract.Profile, str, str]",
) -> None:
    """V5.4, proved rather than promised.

    Every cell of the measured file is looked for in every text field
    of every check and every listing, and a hit is allowed only where
    the DESCRIPTION carries that same string -- because then what the
    result named is the description's own published text, which is the
    one thing V5.4 permits. A spelling that exists only in the measured
    file may appear nowhere.
    """
    described, twin, written = every_role_bytes
    outcome = _measure(tmp_path, described, twin)
    spoken = []
    for check in outcome.checks:
        spoken = spoken + [check.published, check.achieved, check.citation]
    for listing in outcome.listings:
        spoken = spoken + [listing.reason]
    whole = " ".join(spoken)
    leaked = []
    for line in twin.split("\n")[1:]:
        for cell in line.split(","):
            body = cell.strip()
            if len(body) < 4 or body in written:
                continue
            if body in whole:
                leaked.append(body)
    assert leaked == []


def test_no_measured_value_reaches_the_achieved_side_as_text(
    tmp_path: pathlib.Path,
    every_role_bytes: "tuple[contract.Profile, str, str]",
) -> None:
    """The narrower promise this module makes about the achieved side.

    Where an achieved value would be a SPELLING taken from the measured
    file, the comparison is made in full and only the VERDICT is
    reported. What may still print is a MEASUREMENT -- a count, a
    summary, a rung -- which V5.4 allows exactly where the file's own
    description publishes it, and which can coincide with some cell's
    text without having been read out of it. So the rule asserted here
    is the one that matters: an achieved field that matches a measured
    cell has to be a number.
    """
    described, twin, _written = every_role_bytes
    outcome = _measure(tmp_path, described, twin)
    cells = set()
    for line in twin.split("\n")[1:]:
        for cell in line.split(","):
            body = cell.strip()
            if body:
                cells.add(body)
    vocabulary = set(taxonomy.STATISTICAL_TYPES) | set(taxonomy.RESOLUTIONS)
    vocabulary = vocabulary | set(parsing.PRECISION_ORDER)
    vocabulary = vocabulary | set(taxonomy.DATETIMES_READ_AT)
    vocabulary = vocabulary | {"yes", "no", ""}
    for check in outcome.checks:
        if check.achieved in cells and check.achieved not in vocabulary:
            assert parsing.parse_number(check.achieved) is not None


def test_the_gate_withholds_where_the_file_describes_differently(
    tmp_path: pathlib.Path,
) -> None:
    """V5.3: the gate closes over the VERDICT, not only the value.

    A description of a column of numbers, measured against a file whose
    own description sends that column down a label path, must not print
    the numeric summary -- and must not print a within-bound or missed
    line against it either, because a verdict stated against a published
    value is itself something one report says about the measured file,
    and one report is read by people who hold no file. (The second
    ground V5.3 used to give, about repeated candidate profiles
    binary-searching the number, is withdrawn by V5-A1 and this stands
    on the first.)
    """
    folder = tmp_path / "gate"
    folder.mkdir()
    described = _describe(
        folder,
        fixtures.single_column_table(
            "reading", fixtures.numbers(21, 80, 1, 400)
        ),
        stem="numbers",
    )
    labelled = fixtures.single_column_table(
        "reading", ["one" for _index in range(80)]
    )
    outcome = _measure(folder, described, labelled, "labelled.csv")
    ladder = [
        check
        for check in outcome.checks
        if check.subcheck == "ladder.p50"
    ]
    assert len(ladder) == 1
    assert ladder[0].verdict == validation.WITHHELD
    assert ladder[0].achieved == ""
    assert outcome.census.withheld > 0


def test_a_sub_floor_count_prints_as_fewer_than_the_floor(
    tmp_path: pathlib.Path,
) -> None:
    """V5.4: the exact sub-floor number never appears beside a name.

    A published label the measured file holds only a handful of times
    is omitted from that file's own description, and the omission
    already publishes exactly one thing: fewer rows than the floor,
    possibly none. The line says that and no more.
    """
    folder = tmp_path / "floor"
    folder.mkdir()
    values = ["north" for _index in range(40)] + [
        "south" for _index in range(40)
    ]
    described = _describe(
        folder, fixtures.single_column_table("region", values), stem="two"
    )
    thinned = ["north" for _index in range(77)] + [
        "south" for _index in range(3)
    ]
    outcome = _measure(
        folder,
        described,
        fixtures.single_column_table("region", thinned),
        "thin.csv",
    )
    found = [
        check
        for check in outcome.checks
        if check.subcheck == "levels.south.count"
    ]
    assert len(found) == 1
    assert found[0].verdict == validation.MISSED
    assert found[0].achieved == "fewer than 11"
    assert "3" not in found[0].achieved


# -- V2: the measurement, the settings, and the kept set --------------


def test_the_settings_are_rebuilt_from_the_description(
    tmp_path: pathlib.Path,
    every_role: "tuple[contract.Profile, str]",
) -> None:
    """P3-D3's table, field by field: fifteen keys, used fifteen ways."""
    described, _twin = every_role
    settings = validation.settings_for(described)
    block = described.settings
    assert settings.small_cell_floor == block.small_cell_floor
    assert settings.identifier_uniqueness == block.identifier_uniqueness
    assert settings.identifier_minimum_rows == block.identifier_minimum_rows
    assert settings.minimum_parse_rate == block.minimum_parse_rate
    assert settings.categorical_share == block.categorical_share
    assert settings.categorical_ceiling == block.categorical_ceiling
    assert settings.categorical_floor == block.categorical_floor
    assert (
        settings.sentinel_outlier_iqr_multiple
        == block.sentinel_outlier_iqr_multiple
    )
    assert settings.sentinel_minimum_share == block.sentinel_minimum_share
    assert settings.near_threshold_slack == block.near_threshold_slack
    assert settings.declaration_matching == block.declaration_matching
    # The two declaration tuples: one derived from the description, one
    # empty exactly, because the contract records neither spelling.
    assert settings.declared_missing_values == ()
    assert settings.kept_values == validation.kept_spellings(described)
    # ...and the read mode is NOT a settings key.
    assert described.source.header_source in (
        reading.HEADER_FROM_FILE,
        reading.HEADER_GENERATED,
    )


def test_the_kept_set_reaches_all_three_published_routes(
    tmp_path: pathlib.Path,
    every_role: "tuple[contract.Profile, str]",
) -> None:
    """V2.3: variants keys, kept sentinel candidates, and folded labels."""
    described, _twin = every_role
    kept = validation.kept_spellings(described)
    assert kept == tuple(sorted(kept))
    labels = []
    for column in described.columns:
        facts = column.facts
        if isinstance(facts, contract.LabelFacts):
            for level in facts.levels:
                labels.append(level.label)
                for spelling in level.variants:
                    assert spelling in kept
    assert labels
    for label in labels:
        assert label in kept


def test_presence_is_blankness_and_never_the_redescription(
    tmp_path: pathlib.Path,
) -> None:
    """V2.4, proved by the one file where the two answers differ.

    The column below holds thirty cells spelling a built-in marker for
    "no value". The profiler counts those absent, so a validator that
    took presence from the re-description would report the file HELD
    its published count. Presence is BLANKNESS, so the sixty non-blank
    cells are what is counted, the published thirty is not met, and the
    verdict says so.

    This is the rule doing exactly what it exists to do: a twin writes
    every absent cell empty, so on a twin the two answers agree, and
    the one file where they part is a file that is not a twin.
    """
    folder = tmp_path / "blankness"
    folder.mkdir()
    values = ["north" for _index in range(30)] + [
        "n/a" for _index in range(30)
    ]
    described = _describe(
        folder,
        fixtures.single_column_table("region", values),
        stem="kept",
    )
    column = described.columns[0]
    assert column.n_present == 30
    outcome = _measure(
        folder,
        described,
        fixtures.single_column_table("region", values),
        "again.csv",
    )
    found = [
        check
        for check in outcome.checks
        if check.subcheck == "presence.n_present"
    ]
    assert len(found) == 1
    assert found[0].published == "30"
    assert found[0].achieved == "60"
    assert found[0].verdict == validation.MISSED


def test_a_presence_gap_is_measured_over_the_split_not_withheld(
    tmp_path: pathlib.Path,
) -> None:
    """V2.4, and review item P3-V2-A1: the gap MEASURES, it does not hide.

    The same file as the test above: sixty non-blank cells, thirty of
    which the profiler reads as absences, against a description
    publishing thirty present and one level. Presence is blankness, so
    the two readings disagree.

    TWO VERSIONS FAILED HERE BEFORE THIS ONE. The first returned one
    synthetic `presence.agreement` check, built so that it could only
    ever be WITHHELD, and dropped every level, variant, distinctness and
    ladder obligation the column carries, so an extra bad variant in
    such a file drew no line at all. The second kept the lines and made
    every one of them WITHHELD -- which read as complete and let the
    measured file decide which of its own checks ran: one cell spelling
    a built-in marker turned every dependent obligation of a column from
    a potential MISS into a withholding, and files carrying none of
    their published labels then passed.

    So three things are asserted. Every obligation still HAS a line,
    compared against the description's own twin rather than a list
    written here. The two counts the blank split owns still verdict. And
    the dependent obligations carry VERDICTS taken over the blank split
    -- not one of them is withheld, because nothing here is a fact the
    file's own description would refuse to publish.
    """
    folder = tmp_path / "gap"
    folder.mkdir()
    values = ["north" for _index in range(30)] + [
        "n/a" for _index in range(30)
    ]
    described = _describe(
        folder,
        fixtures.single_column_table("region", values),
        stem="gap",
    )
    assert described.columns[0].n_present == 30
    clean = _measure(
        folder, described, _twin_text(described), "gap-twin.csv"
    )
    gapped = _measure(
        folder,
        described,
        fixtures.single_column_table("region", values),
        "gap-again.csv",
    )
    named = [check.subcheck for check in gapped.checks]
    assert "presence.agreement" not in named
    assert sorted(named) == sorted(
        check.subcheck for check in clean.checks
    )
    # The blank split still verdicts the two counts it owns...
    assert _verdicts(gapped, "presence.n_present") == [validation.MISSED]
    assert _verdicts(gapped, "presence.n_missing") == [validation.MISSED]
    # ...and the sixty non-blank cells are what every dependent
    # measurement is taken over. The file holds two levels where the
    # description publishes one, and the census says so.
    assert _verdicts(gapped, "levels.set") == [validation.MISSED]
    assert _verdicts(gapped, "distinct.n_distinct") == [validation.MISSED]
    assert gapped.census.missed > 0
    for check in gapped.checks:
        assert check.verdict != validation.WITHHELD, check
    assert gapped.census.withheld == 0


# -- V4: the corners, and V4.3's refusals -----------------------------


def test_the_corner_classifier_is_a_function_of_the_profile_alone(
    tmp_path: pathlib.Path,
    every_role: "tuple[contract.Profile, str]",
) -> None:
    """V4.2: no file is read, and the answer never varies."""
    described, _twin = every_role
    once = validation.corners_of(described)
    again = validation.corners_of(described)
    assert once == again
    for name in once:
        for corner in once[name]:
            assert corner in validation.CORNERS
            assert validation.CORNER_CITATIONS[corner]


def test_the_offsets_corner_is_listed_and_carries_no_verdict(
    tmp_path: pathlib.Path,
) -> None:
    """A datetime column whose offsets are the single withheld key.

    REVIEW ITEM P3-V1-F4. In this corner the four offset facts are
    REPORT-ONLY -- the registry's own class for them, and V4.1's -- and
    a REPORT-ONLY fact is a listing entry: it produces no verdict and is
    counted where a not-checkable obligation is counted. The version
    this test was first written against returned four
    AUTHORIZED-DEVIATION checks, which put four facts nothing had been
    measured against into the count of obligations the file WAS checked
    against, and a pass census then said more than it could support.

    Two things are asserted: no verdict of any kind is filed under any
    of the four identities, and each appears in the census with the
    passage that authorizes the lesser outcome, because a lowering shown
    without its authority is one nobody can check.
    """
    folder = tmp_path / "offsets"
    folder.mkdir()
    # Six offsets over sixty rows: every one of them covers ten rows,
    # which is under the small-cell floor, so the description pools the
    # whole map into the single withheld key -- which IS the corner.
    zones = ("+00:00", "+01:00", "+02:00", "-03:00", "-04:00", "+05:30")
    stamps = []
    for index in range(60):
        offset = zones[index // 10]
        stamps.append(f"2024-01-{(index % 28) + 1:02d}T00:00:00{offset}")
    described = _describe(
        folder,
        fixtures.single_column_table("recorded_on", stamps),
        stem="offsets",
    )
    corners = validation.corners_of(described)
    column = described.columns[0]
    facts = column.facts
    assert isinstance(facts, contract.DatetimeFacts)
    if column.name not in corners:
        pytest.skip("this fixture did not reach the withheld-offset corner")
    assert (
        validation.CORNER_DATETIME_OFFSETS_WITHHELD
        in corners[column.name]
    )
    outcome = _measure(
        folder, described, _twin_text(described), "offset-twin.csv"
    )
    offsets = (
        "offsets.map",
        "offsets.earliest",
        "offsets.latest",
        "offsets.read-at",
    )
    for subcheck in offsets:
        assert _verdicts(outcome, subcheck) == []
    listed = [
        listing
        for listing in outcome.listings
        if listing.subcheck in offsets
    ]
    assert len(listed) == len(offsets)
    for listing in listed:
        assert listing.column == column.name
        assert (
            validation.CORNER_CITATIONS[
                validation.CORNER_DATETIME_OFFSETS_WITHHELD
            ]
            in listing.reason
        )
    assert outcome.census.not_checkable >= len(offsets)


def test_a_generation_refusal_is_a_refusal_and_never_a_verdict(
    tmp_path: pathlib.Path,
) -> None:
    """V4.3: a G12-infeasible description cannot produce a pass.

    The description is hand-built to meet one refusal exactly, then
    validated against an ordinary file. Treating the refusal as an
    authorized corner would launder an impossible obligation into a
    passing report, so the run must stop instead.
    """
    folder = tmp_path / "refusal"
    folder.mkdir()
    described = _describe(
        folder,
        fixtures.single_column_table(
            "reading", fixtures.numbers(31, 60, 1, 400)
        ),
        stem="plain",
    )
    column = described.columns[0]
    facts = column.facts
    assert isinstance(facts, contract.NumericFacts)
    broken = dataclasses.replace(
        described,
        columns=(
            dataclasses.replace(
                column,
                facts=dataclasses.replace(
                    facts, n_zero=column.n_numeric + 1, n_negative=0
                ),
            ),
        ),
    )
    assert validation.refusal_of(broken) == (
        validation.REFUSAL_COUNTS_CONTRADICT
    )
    target = fixtures.write(folder, "any.csv", "reading\n1\n")
    with pytest.raises(errors.ProfileError) as raised:
        validation.measure(broken, str(target))
    said = f"{raised.value}"
    # The refusal mirrors the generation refusal and adds the sentence
    # this path needs: whatever the file is, it cannot be that
    # description's twin.
    assert "cannot be this description's twin" in said


def _single_character_description(
    folder: pathlib.Path, count: int
) -> contract.Profile:
    """A description of one column of ``count`` one-character values.

    Every value is outside the code alphabet and every one is written
    once, so the description publishes `count` different values, both
    length ends at one, and both alphabet counts at zero. It is the
    fixture the generator's own boundary test uses, built here from the
    same real producer so that nothing about the capacity is written
    into this file.
    """
    values = [chr(0x100 + 2 * index) for index in range(count)]
    return _describe(
        folder,
        fixtures.single_column_table("note", values),
        stem=f"tiny-{count}",
    )


def test_a_description_the_domain_cannot_hold_refuses_rather_than_verdicts(
    tmp_path: pathlib.Path,
) -> None:
    """REVIEW ITEM P3-V1-F5: the fourth G12 refusal, reached from validate.

    Twenty-six different one-character values outside the code alphabet,
    where twenty-five such values exist to be written. Generation
    refuses this description by name and no conforming twin of it can
    exist, so validation may not return an outcome for it -- a verdict
    on a file measured against an impossible obligation is a report
    saying the file failed to be something nothing could be, and where
    the file happens to hold nothing the description publishes it could
    even pass.

    THE BOUNDARY IS ASSERTED FROM BOTH SIDES, because a refusal that
    fires one value early is a description a person cannot get a twin of
    for no reason: twenty-five validates, twenty-six refuses, and both
    descriptions come from the shipped producer.
    """
    folder = tmp_path / "domain"
    folder.mkdir()
    inside = _single_character_description(folder, 25)
    assert validation.refusal_of(inside) == ""
    outcome = _measure(
        folder, inside, _twin_text(inside), "inside-twin.csv"
    )
    assert outcome.census.missed == 0
    beyond = _single_character_description(folder, 26)
    assert validation.refusal_of(beyond) == (
        validation.REFUSAL_DOMAIN_TOO_SMALL
    )
    target = fixtures.write(folder, "any.csv", "note\nx\n")
    with pytest.raises(errors.ProfileError) as raised:
        validation.measure(beyond, str(target))
    said = f"{raised.value}"
    assert "cannot be this description's twin" in said
    assert "is valid" in said
    # ...and the two sides agree about which descriptions are impossible.
    # A shared design error would now need the same mistake written
    # twice, from two documents (V4.2's reasoning, applied to G9.4).
    with pytest.raises(errors.ProfileError):
        generation.plan_generation(beyond)
    generation.plan_generation(inside)


def test_the_domain_rule_never_refuses_an_ordinary_column_of_text(
    tmp_path: pathlib.Path,
    every_role: "tuple[contract.Profile, str]",
) -> None:
    """The direction that makes the rule safe to have at all.

    Every bound the capacity arithmetic compares against is an UPPER
    bound on what the construction can write, so a description a twin
    exists for can never meet this refusal. The every-role fixture
    carries a column of free text with eighty different values, and the
    battery's other free-text fixtures carry more; none of them may be
    refused.
    """
    described, _twin = every_role
    assert validation.refusal_of(described) == ""
    folder = tmp_path / "wide-text"
    folder.mkdir()
    for count in (2, 10, 25):
        assert validation.refusal_of(
            _single_character_description(folder, count)
        ) == ""


# -- V9: refusals that name positions, never values -------------------


def test_a_missing_measured_file_refuses(
    tmp_path: pathlib.Path,
    every_role: "tuple[contract.Profile, str]",
) -> None:
    """Validation that could not run at all is a refusal, not a verdict."""
    described, _twin = every_role
    with pytest.raises(errors.ProfileError):
        validation.measure(described, str(tmp_path / "not-there.csv"))


def test_a_folder_instead_of_a_file_refuses(
    tmp_path: pathlib.Path,
    every_role: "tuple[contract.Profile, str]",
) -> None:
    """A folder given where a table was meant."""
    described, _twin = every_role
    folder = tmp_path / "a-folder"
    folder.mkdir()
    with pytest.raises(errors.ProfileError):
        validation.measure(described, str(folder))


def _two_column_description(folder: pathlib.Path) -> contract.Profile:
    """An ordinary two-column description to point a hostile file at."""
    return _describe(
        folder,
        fixtures.rows_to_csv(
            ["c0", "c1"],
            [
                [value, fixtures.REGIONS[index % 4]]
                for index, value in enumerate(fixtures.numbers(91, 60, 1, 9))
            ],
        ),
        stem="two",
    )


def test_a_value_the_two_readers_read_differently_names_positions(
    tmp_path: pathlib.Path,
) -> None:
    """REACHABILITY: the value-disagreement refusal, from validate.

    The file is the one the reading battery uses for this: the standard
    reader yields ["", "B"] for that row and pandas' C reader yields
    ["B", ""], with equal row and column counts and no zero byte
    anywhere. The profiler's form of the refusal names the column by the
    NAME it read out of the file. Here the file may be anybody's, so the
    refusal names the column NUMBER, and this asserts it names nothing
    else (V9).
    """
    folder = tmp_path / "disagree-value"
    folder.mkdir()
    described = _two_column_description(folder)
    target = folder / "crooked.csv"
    target.write_bytes(b"c0,c1\n\r,B\nz,w\n")
    with pytest.raises(errors.ProfileError) as raised:
        validation.measure(described, str(target))
    said = f"{raised.value}"
    assert "row 1, column number 1" in said, said
    assert "may not be your own table" in said, said
    assert "'c0'" not in said and "'c1'" not in said, said


def test_a_name_the_two_readers_read_differently_names_positions(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """REACHABILITY: the name-disagreement refusal, from validate.

    The file is rewritten between the two reading passes, which is how
    the reading battery reaches this one. The profiler's form quotes
    both names it read; on this path the file may be somebody else's
    table, so the refusal names the column number and neither spelling.
    """
    folder = tmp_path / "disagree-name"
    folder.mkdir()
    described = _two_column_description(folder)
    target = folder / "rewritten.csv"
    target.write_bytes(b"c0,c1\n1,north\n2,south\n")
    real = reading._read_authoritatively

    def rewrite_after_reading(
        table_path: object, shown: str, first_row: str, refusals: str
    ) -> object:
        found = real(table_path, shown, first_row, refusals)
        pathlib.Path(f"{table_path}").write_bytes(
            b"zzmarkerzz,c1\n1,north\n2,south\n"
        )
        return found

    monkeypatch.setattr(
        reading, "_read_authoritatively", rewrite_after_reading
    )
    with pytest.raises(errors.ProfileError) as raised:
        validation.measure(described, str(target))
    said = f"{raised.value}"
    assert "name of column number 1" in said, said
    assert "zzmarkerzz" not in said, said
    assert "may not be your own table" in said, said


def test_a_file_the_checking_pass_cannot_read_names_no_detail(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """REACHABILITY: the not-readable-as-CSV refusal, from validate.

    The checking pass's own account of what went wrong can carry a
    piece of the file with it -- a byte it stopped at, a fragment of a
    line -- and the profiler's form of this refusal prints that account.
    The library is made to fail with an account that holds a marker, and
    the marker may not reach the refusal.
    """
    folder = tmp_path / "unreadable"
    folder.mkdir()
    described = _two_column_description(folder)
    target = fixtures.write(folder, "ordinary.csv", "c0,c1\n1,north\n2,south\n")

    def refuse_to_read(*_args: object, **_keywords: object) -> object:
        raise ValueError("stopped at zzmarkerzz on line 2")

    monkeypatch.setattr(reading.pandas, "read_csv", refuse_to_read)
    with pytest.raises(errors.ProfileError) as raised:
        validation.measure(described, str(target))
    said = f"{raised.value}"
    assert "zzmarkerzz" not in said, said
    assert "could not be read as a CSV table" in said, said
    assert "may not be your own table" in said, said


def test_a_structural_mismatch_is_a_verdict_and_not_a_refusal(
    tmp_path: pathlib.Path,
    every_role: "tuple[contract.Profile, str]",
) -> None:
    """The report is the product even when the news is bad."""
    described, twin = every_role
    lines = []
    for line in twin.split("\n"):
        lines.append(line if not line else f"{line},extra")
    outcome = _measure(tmp_path, described, "\n".join(lines), "wide.csv")
    assert _verdicts(outcome, "columns.n_columns") == [validation.MISSED]


def test_a_repeated_header_name_is_a_verdict_and_names_no_value(
    tmp_path: pathlib.Path,
) -> None:
    """V9's last paragraph, and review item P3-V1-F10.

    A file whose first row uses one name twice cannot name a table's
    columns, and the profiler's reader refuses it -- in a sentence that
    QUOTES the repeated name. Reached from validate, that refusal both
    printed a string out of a file nobody promised was the reader's and
    turned a wrong name into a run that never happened. A wrong name is
    a MISSED verdict with a report; the columns nothing could be matched
    to MISS rather than being dropped; and the spelling appears nowhere.

    THEY MISS RATHER THAN BEING LISTED (review item P3-V2-E-F2). This
    test asserted the listing, and the listing said something false: a
    not-checkable line means no written CSV can evidence the obligation
    either way, and the twin of this same description evidences every
    one of them. What is true is that this file does not carry them.
    """
    folder = tmp_path / "repeated"
    folder.mkdir()
    described = _describe(
        folder,
        fixtures.rows_to_csv(
            ["reading", "region"],
            [
                [value, fixtures.REGIONS[index % 4]]
                for index, value in enumerate(fixtures.numbers(81, 60, 1, 9))
            ],
        ),
        stem="two",
    )
    marker = "zzmarkerzz"
    rows = [f"{index},{index}" for index in range(60)]
    hostile = f"{marker},{marker}\n" + "\n".join(rows) + "\n"
    outcome = _measure(folder, described, hostile, "repeated.csv")
    assert _verdicts(outcome, "header.names") == [validation.MISSED]
    assert _verdicts(outcome, "header.presence") == [validation.MISSED]
    assert _verdicts(outcome, "columns.order") == [validation.MISSED]
    # ...and no column's obligations vanish: each carries a MISSED
    # verdict with the reason instead of leaving the census without a
    # line, or being called an obligation no CSV can evidence.
    missed = {
        check.column
        for check in outcome.checks
        if check.fact == "universal.position"
        and check.verdict == validation.MISSED
    }
    for column in described.columns:
        assert column.name in missed
        assert column.name not in {
            listing.column for listing in outcome.listings
            if listing.fact == "universal.position"
        }
    spoken = []
    for check in outcome.checks:
        spoken = spoken + [check.published, check.achieved, check.citation]
    for listing in outcome.listings:
        spoken = spoken + [listing.reason, listing.column, listing.fact]
    assert marker not in " ".join(spoken)


def test_a_blank_header_name_is_a_verdict_and_names_the_position(
    tmp_path: pathlib.Path,
) -> None:
    """The other unusable first row, and it names WHICH column."""
    folder = tmp_path / "blank"
    folder.mkdir()
    described = _describe(
        folder,
        fixtures.rows_to_csv(
            ["reading", "region"],
            [
                [value, fixtures.REGIONS[index % 4]]
                for index, value in enumerate(fixtures.numbers(83, 60, 1, 9))
            ],
        ),
        stem="two",
    )
    rows = [f"{index},{index}" for index in range(60)]
    hostile = "reading,\n" + "\n".join(rows) + "\n"
    outcome = _measure(folder, described, hostile, "blank.csv")
    found = [
        check for check in outcome.checks if check.subcheck == "header.names"
    ]
    assert len(found) == 1
    assert found[0].verdict == validation.MISSED
    assert found[0].achieved == "no name at column number 2"


def test_the_header_question_is_settled_on_the_first_RECORD(
    tmp_path: pathlib.Path,
) -> None:
    """REVIEW ITEM P3-V2-D-F1: what the reader calls the first row.

    Round 1 settled the two header faults before the reader is called,
    and settled them on the first PHYSICAL LINE. The reader does not
    read a file that way: it drops blank lines and it honours a newline
    inside a quoted value. So a repeated name behind a leading blank
    line, and a repeated name with a newline written into it, both got
    past the pre-check into the reader's own refusal -- which quotes the
    repeated name, on a file nobody promised was the reader's.

    Both are structural mismatches and V9 says a structural mismatch is
    a MISSED verdict with a report. The assertion is that both files
    reach a report at all, and that no string of either file is in it.

    THE REPORT NAMES NO POSITION FOR A REPEATED NAME (review item
    P3-V4-F3; plan amendment A-P3-10 clause 2). It used to name the two
    column numbers, and the profiler's own refusal for such a file names
    neither -- it quotes the repeated NAME -- so two files with the
    repeat in different columns are one file to the producer and were
    two to this report. What it says now is what that refusal says.
    """
    folder = tmp_path / "records"
    folder.mkdir()
    described = _describe(
        folder,
        fixtures.rows_to_csv(
            ["reading", "region"],
            [
                [value, fixtures.REGIONS[index % 4]]
                for index, value in enumerate(fixtures.numbers(85, 60, 1, 9))
            ],
        ),
        stem="two",
    )
    marker = "zzmarkerzz"
    rows = "\n".join(f"{index},{index}" for index in range(60)) + "\n"
    for label, hostile in (
        ("blank-first-line", f"\n{marker},{marker}\n" + rows),
        ("quoted-newline", f'"{marker}\nx","{marker}\nx"\n' + rows),
    ):
        outcome = _measure(folder, described, hostile, f"{label}.csv")
        found = [
            check
            for check in outcome.checks
            if check.subcheck == "header.names"
        ]
        assert len(found) == 1, label
        assert found[0].verdict == validation.MISSED, label
        assert "column number" not in found[0].achieved, label
        spoken = []
        for check in outcome.checks:
            spoken = spoken + [
                check.published, check.achieved, check.citation
            ]
        for listing in outcome.listings:
            spoken = spoken + [listing.reason, listing.column, listing.fact]
        assert marker not in " ".join(spoken), label


def test_the_record_walk_agrees_with_the_reader_it_stands_in_for(
    tmp_path: pathlib.Path,
) -> None:
    """The anti-drift assertion for `_records_of` (P3-V2-D-F1, E-F4).

    Two questions are settled before the reader is called -- which row
    is the first one, and whether the file holds any rows -- and both
    have to reach the answer the reader would reach, because where they
    do not, a file this module called reportable is one the reader
    refuses, and its refusals quote what they found. The last
    disagreement was a leading blank line and a newline inside a quoted
    name. So this is not a test of a rule written twice: it drives both
    readings of the same files and asserts they agree, which is the only
    form that catches the NEXT disagreement.

    AND IT IS DRIVEN OVER THE FILE, NOT OVER THE STRING (review item
    P3-V3-F6). This used to hand the walk the characters the test had
    written and ask the reader for the file, so everything the module
    does BETWEEN the bytes and the walk was outside the comparison --
    and two of the three ways the two readings could differ were in
    exactly that gap. The
    measured file is now read exactly as `measure` reads it, so the
    comparison covers the whole path from bytes to records.

    THE BOUNDARIES ARE HERE FOR THE SAME REASON. A field one character
    longer than the interpreter's default limit parsed here as a header
    and nothing else while the reader read every row of it, and the
    catalogue's own long-field file was two hundred characters, so
    nothing crossed the line. Three lengths straddle it, quoted and
    plain, in a value and in a name. The other two boundaries the two
    readings meet are the encodings -- the reader tries its own two in
    its own order, and so does the caller here -- and the byte-order
    mark, which the reader's own codec takes off and this module takes
    off by name.
    """
    folder = tmp_path / "agree"
    folder.mkdir()
    default_limit = 131_072
    long = "x" * (default_limit + 1)
    files = {
        "byte-order-mark": "﻿a,b\n1,2\n",
        "not-utf8": "a,b\n1,\xff\n",
        "plain": "a,b\n1,2\n3,4\n",
        "no-terminal-newline": "a,b\n1,2\n3,4",
        "leading-blank": "\na,b\n1,2\n",
        "inner-blanks": "a,b\n\n1,2\n\n\n3,4\n",
        "quoted-newline": 'a,"b\nc"\n1,2\n3,4\n',
        "quoted-comma": 'a,b\n"1,5",2\n3,4\n',
        "carriage-returns": "a,b\r\n1,2\r\n",
        "carriage-only": "a,b\r1,2\r3,4\r",
        "quoted-carriage": 'a,"b\rc"\n1,2\n3,4\n',
        "one-line": "a,b\n",
        "doubled-quotes": 'a,b\n"1""5",2\n3,4\n',
        "trailing-blanks": "a,b\n1,2\n\n\n",
        "under-the-default": "a,b\n" + "x" * (default_limit - 1) + ",2\n",
        "at-the-default": "a,b\n" + "x" * default_limit + ",2\n",
        "over-the-default": f"a,b\n{long},2\n",
        "over-the-default-quoted": f'a,b\n"{long}",2\n',
        "over-the-default-in-a-name": f"{long},b\n1,2\n",
        "over-the-default-with-a-break": f'a,b\n"{long}\ny",2\n',
        "over-the-default-twice": f"a,b\n{long},{long}\n",
    }
    for label in sorted(files):
        target = folder / f"{label}.csv"
        encoding = "latin-1" if label == "not-utf8" else "utf-8"
        target.write_text(files[label], encoding=encoding, newline="")
        table = reading.read_table(
            str(target), first_row=reading.FIRST_ROW_DATA
        )
        rows = [
            [column[at] for column in table.columns]
            for at in range(table.n_rows)
        ]
        # Exactly the choice `measure` makes, and the byte-order mark
        # taken off exactly where its callers take it off.
        text = validation._read_utf8(target)
        as_read = (
            text if text is not None else validation._read_fallback(target)
        )
        walked, whole = validation._walked(
            validation._without_a_mark(as_read)
        )
        assert whole, (
            f"{label}: the walk stopped part way on a file the reader "
            f"read to its end"
        )
        assert walked == rows, label


def test_a_blank_line_after_the_header_is_still_a_report(
    tmp_path: pathlib.Path,
) -> None:
    """REVIEW ITEM P3-V2-E-F4: one empty line, and the report vanished.

    `header\\n` gave a full census with the row count MISSED at exit 3.
    `header\\n\\n` gave a refusal at exit 1, no report at all, carrying
    the profiler's advice to go and find a file that has the rows in it
    -- when the true answer is that this file misses the published row
    count and every obligation its cells would have carried. Two files
    two empty bytes apart, and only one of them was told the truth.
    Headerless, the same step stood between a file of no bytes and a
    file holding one newline.

    The two sides of each step now produce the same verdict on every
    obligation that is not a rule about the file's BYTES, which is the
    property: an empty line carries no record, so a file that holds one
    holds the records the file without it holds. The byte rules are
    where the two files really do differ and are excluded by name --
    a file of no bytes has no terminal newline and a file of two
    newlines has one, and both statements are true.
    """
    folder = tmp_path / "blanks"
    folder.mkdir()
    made = [
        [value, fixtures.REGIONS[index % 4]]
        for index, value in enumerate(fixtures.numbers(87, 60, 1, 9))
    ]
    headed = _describe(
        folder,
        fixtures.rows_to_csv(["reading", "region"], made),
        stem="headed",
    )
    bare = _describe(
        folder,
        fixtures.rows_to_csv(["1", "north"], made),
        stem="bare",
        first_row=reading.FIRST_ROW_DATA,
    )
    for described, first, second in (
        (headed, "reading,region\n", "reading,region\n\n\n"),
        (bare, "", "\n\n"),
    ):
        one = _measure(folder, described, first, "one.csv")
        two = _measure(folder, described, second, "two.csv")
        assert one.census.missed > 50
        assert _apart_from_bytes(two) == _apart_from_bytes(one)
        assert two.listings == one.listings
        assert _verdicts(two, "rows.n_rows") == [validation.MISSED]


def _apart_from_bytes(
    outcome: validation.Outcome,
) -> "list[validation.Check]":
    """Every verdict a run filed that is not a rule about its bytes."""
    return [
        check
        for check in outcome.checks
        if not check.subcheck.startswith("bytes.")
    ]


def test_red_a_reshaped_text_column_misses_the_length_average(
    tmp_path: pathlib.Path,
    every_role: "tuple[contract.Profile, str]",
) -> None:
    """NAMED SUBCHECK: length.mean, at method G12.6's own reach.

    REVIEW ITEM P3-V1-F9, reproduced as the reviewer wrote it. The
    every-role `comment` column publishes eighty singleton groups,
    lengths from 48 to 50, and an average of 49.525. G12.6 bounds what
    the walk can achieve to 49.5125-49.5375; the window this replaces
    was the two published ends, 48 to 50, and it accepted a file whose
    cells were half at 48 and half at 50 -- an average of 49.0, with
    every extreme, every word count and the whole repetition pattern
    preserved. Nothing else in the report would have said a word about
    it.

    Both directions are asserted, because a window that catches this
    file by being narrow would accuse the conforming twin: the twin
    lands inside, the reshaped file does not.
    """
    described, twin = every_role
    column = None
    for entry in described.columns:
        if isinstance(entry.facts, contract.TextFacts):
            column = entry
    assert column is not None
    facts = column.facts
    assert isinstance(facts, contract.TextFacts)
    assert facts.length.minimum == 48
    assert facts.length.maximum == 50
    green = _measure(tmp_path, described, twin, "text-green.csv")
    assert _verdicts(green, "length.mean") == [validation.WITHIN_BOUND]
    index = column.position - 1
    # Read and rewritten as CSV rather than split on commas: a free-text
    # cell can hold a comma and is then quoted, and splitting such a
    # line takes the row apart.
    rows = [row for row in csv.reader(io.StringIO(twin))]
    step = 0
    for row in range(1, len(rows)):
        if not rows[row][index]:
            continue
        wanted = 48 if step % 2 == 0 else 50
        body = f"aa bb cc dd ee ff gg h{step:04d}"
        body = body + "z" * (wanted - len(body))
        assert len(body) == wanted
        rows[row][index] = body
        step = step + 1
    out = io.StringIO()
    csv.writer(out, lineterminator="\n").writerows(rows)
    outcome = _measure(tmp_path, described, out.getvalue(), "text-red.csv")
    # The perturbation leaves every neighbouring obligation held, which
    # is what makes it a test of THIS subcheck.
    # ...counting the identifier column, which carries the same two
    # length identities and is untouched by this edit.
    assert validation.MISSED not in _verdicts(outcome, "length.min")
    assert validation.MISSED not in _verdicts(outcome, "length.max")
    assert validation.MISSED not in _verdicts(outcome, "words.max")
    assert _verdicts(outcome, "length.mean") == [validation.MISSED]


# -- V3.3 and P3-D2: the obligation set belongs to the DESCRIPTION ----
#    (review items P3-V1-F3 and P3-V1-F11)


def _checked(outcome: validation.Outcome) -> "set[tuple[str, str, str]]":
    """Every obligation one run filed a VERDICT on, as its bare identity."""
    return {
        (check.column, check.fact, check.subcheck)
        for check in outcome.checks
    }


def _listed(outcome: validation.Outcome) -> "set[tuple[str, str, str]]":
    """Every obligation one run called NOT CHECKABLE, as its identity."""
    return {
        (listing.column, listing.fact, listing.subcheck)
        for listing in outcome.listings
    }


def _identities(outcome: validation.Outcome) -> "set[tuple[str, str, str]]":
    """Every obligation one run accounted for, as its bare identity.

    Checks and listings together, because the two are the same
    obligation reported two ways: an obligation a file could be measured
    against carries a verdict, and one it could not carries a line in
    the not-checkable census. What may never happen is for it to be in
    neither.
    """
    return _checked(outcome) | _listed(outcome)


def test_the_obligation_set_is_a_function_of_the_description(
    tmp_path: pathlib.Path,
    every_role: "tuple[contract.Profile, str]",
) -> None:
    """REVIEW ITEM P3-V1-F11, stated as the property it violates.

    What a description obliges a file to carry is fixed by the
    DESCRIPTION. A file that is missing a column, or holds no rows, or
    whose first row cannot name a table's columns, does not thereby owe
    less: what it cannot carry it MISSES, or is listed as unmeasurable
    with the reason -- never dropped. The version this test was written
    against collapsed a 249-check census to five against a header-only
    file and to one invented line for a dropped column, and the report
    then called those five every measurable obligation.

    AND THE PARTITION IS COMPARED, BUCKET BY BUCKET (review item
    P3-V2-E-F2). The version of this test that shipped with the round-1
    repair unioned the checks and the listings into ONE set and compared
    that, so an obligation MOVING from the checkable bucket to the
    not-checkable one was invisible to it -- and one file did move three
    hundred and seven of them. The report then told its reader that this
    description sets eight obligations a written file can be checked
    against and that three hundred and seventy-two of its obligations
    are beyond any CSV, about a description whose own twin had answered
    three hundred and fifteen of them three commands earlier. Both
    sentences are claims about the DESCRIPTION (V7.2) and both were
    false. So the two buckets are asserted separately, and the union is
    asserted as well, because a repair that moved an obligation OUT of
    both would satisfy either half alone.
    """
    described, twin = every_role
    lines = twin.split("\n")
    narrowed = []
    for line in lines:
        if not line:
            narrowed.append(line)
            continue
        cells = line.split(",")
        narrowed.append(",".join(cells[: len(cells) - 1]))
    files = {
        "twin": twin,
        "header-only": lines[0] + "\n",
        "dropped-column": "\n".join(narrowed),
        "one-row": lines[0] + "\n" + lines[1] + "\n",
        "unusable-header": (
            ",".join(["same" for _cell in lines[0].split(",")])
            + "\n"
            + "\n".join(lines[1:])
        ),
    }
    base = _measure(tmp_path, described, twin, "base.csv")
    expected = _identities(base)
    assert len(expected) > 200
    assert len(_checked(base)) > 200
    assert _listed(base)
    for name in sorted(files):
        outcome = _measure(tmp_path, described, files[name], f"{name}.csv")
        assert _identities(outcome) == expected, name
        assert _checked(outcome) == _checked(base), name
        assert _listed(outcome) == _listed(base), name
        assert outcome.census.not_checkable == base.census.not_checkable, name
        assert len(outcome.checks) == len(base.checks), name


def test_a_missing_column_misses_its_obligations_rather_than_dropping_them(
    tmp_path: pathlib.Path,
    every_role: "tuple[contract.Profile, str]",
) -> None:
    """NAMED SUBCHECK: position.at, and every obligation beside it.

    A file one column short used to draw one invented `column.present`
    miss, and every other obligation that column carried left the census
    without a line -- so a reader was told the file had been measured
    against every obligation the description sets while dozens of them
    had been quietly removed by the file's own shape.
    """
    described, twin = every_role
    last = described.columns[len(described.columns) - 1]
    narrowed = []
    for line in twin.split("\n"):
        if not line:
            narrowed.append(line)
            continue
        cells = line.split(",")
        narrowed.append(",".join(cells[: len(cells) - 1]))
    outcome = _measure(tmp_path, described, "\n".join(narrowed), "short.csv")
    mine = [
        check for check in outcome.checks if check.column == last.name
    ]
    assert len(mine) > 5
    for check in mine:
        assert check.verdict == validation.MISSED, check
    assert validation.MISSED in _verdicts(outcome, "position.at")


def test_a_file_holding_no_rows_misses_every_obligation_it_cannot_carry(
    tmp_path: pathlib.Path,
    every_role: "tuple[contract.Profile, str]",
) -> None:
    """The header-only file of review item P3-V1-F11.

    Five checks and ten listings, against a description that sets nearly
    three hundred obligations, was the census this file used to produce
    -- and the summary above it said those five were every obligation a
    file can be measured against.

    WHAT THE HEADER LINE EVIDENCES HERE IS NOTHING, AND THIS TEST SAID
    THE OPPOSITE (review item P3-V3-F3; plan amendment A-P3-7 clause 1).
    It asserted that the names and the width read back HELD off the
    first line of a file `synthtwin profile` refuses to describe at all,
    which is what let two header-only files named alike be told apart by
    their reports. The obligations the row count settles are what this
    file misses, and they are what this test is about.
    """
    described, twin = every_role
    outcome = _measure(
        tmp_path, described, twin.split("\n")[0] + "\n", "head.csv"
    )
    assert outcome.census.missed > 200
    assert _verdicts(outcome, "rows.n_rows") == [validation.MISSED]
    # ...and what the header line would have to answer for is withheld,
    # because describing this file publishes no header at all.
    assert _verdicts(outcome, "header.names") == [validation.WITHHELD]
    assert _verdicts(outcome, "columns.n_columns") == [validation.WITHHELD]
    assert _verdicts(outcome, "header.presence") == [validation.WITHHELD]
    for column in described.columns:
        mine = [
            check for check in outcome.checks if check.column == column.name
        ]
        assert len(mine) > 5


def test_every_column_carries_its_four_axes_and_its_position(
    tmp_path: pathlib.Path,
    every_role: "tuple[contract.Profile, str]",
) -> None:
    """REVIEW ITEM P3-V1-F3: four registry facts were in no entry at all.

    `universal.position`, `universal.role`, `universal.quality_state`
    and `universal.structural_role` appeared in no check, no listing and
    no input-side binding, while the report said its counts covered
    every obligation. Each is bound here, per column, and the green
    direction holds: the twin re-reads as the same kind of column, which
    is what Phase 2's decisions 5, 8 and 10 bought.

    AND ONE OF THE FIVE IS BOUND AS A LISTING (review item P3-V2-C-F3;
    plan amendment A-P3-2, which records the lowering in those words).
    `structural_role` says whether the person who owns the table
    declared this column with `--identifier`. The taxonomy computes it
    from that declaration and nothing else -- its own docstring says no
    value of the column is consulted -- and the validator re-describes
    the file under the same declaration list, so both sides read the
    same word for every column of every description that declares no
    identifier, which is the zero-code default. It was a HELD line on
    every column of every ordinary report that no file could miss. What
    this test still asserts is P3-V1-F3's own point: the fact is BOUND,
    once per column, to an entry of one of the three kinds.
    """
    described, twin = every_role
    outcome = _measure(tmp_path, described, twin)
    for subcheck, fact in (
        ("position.at", "universal.position"),
        ("axes.role", "universal.role"),
        ("axes.statistical_type", "universal.statistical_type"),
        ("axes.quality_state", "universal.quality_state"),
    ):
        mine = [
            check for check in outcome.checks if check.subcheck == subcheck
        ]
        assert len(mine) == len(described.columns), subcheck
        for check in mine:
            assert check.fact == fact
            assert check.verdict == validation.HELD
    assert not [
        check
        for check in outcome.checks
        if check.subcheck == "axes.structural_role"
    ], (
        "the declared-identifier axis is carrying a verdict again, and "
        "no file can make it miss on a description that declares no "
        "identifier -- which is every description a person who never "
        "used --identifier writes"
    )
    listed = [
        listing
        for listing in outcome.listings
        if listing.subcheck == "axes.structural_role"
    ]
    assert len(listed) == len(described.columns)
    for listing in listed:
        assert listing.fact == "universal.structural_role"
        assert listing.reason


def test_red_swapped_columns_miss_the_position_of_each(
    tmp_path: pathlib.Path,
    every_role: "tuple[contract.Profile, str]",
) -> None:
    """NAMED SUBCHECK: position.at.

    Two whole columns exchanged, header and cells together. The file
    still holds every value the description publishes and still reads as
    a table of the same width, so nothing about its content is wrong --
    what is wrong is that two columns are not where the description puts
    them, which is the obligation `universal.position` states.
    """
    described, twin = every_role
    first = described.columns[0].position - 1
    second = described.columns[1].position - 1
    swapped = []
    for line in twin.split("\n"):
        if not line:
            swapped.append(line)
            continue
        cells = line.split(",")
        cells[first], cells[second] = cells[second], cells[first]
        swapped.append(",".join(cells))
    outcome = _measure(tmp_path, described, "\n".join(swapped), "swapped.csv")
    missed = [
        check.column
        for check in outcome.checks
        if check.subcheck == "position.at"
        and check.verdict == validation.MISSED
    ]
    assert described.columns[0].name in missed
    assert described.columns[1].name in missed


def test_a_renamed_declared_identifier_is_caught_by_the_name_and_not_the_axis(
    tmp_path: pathlib.Path,
    every_role: "tuple[contract.Profile, str]",
) -> None:
    """WHAT THE STRUCTURAL-ROLE LOWERING COST, measured (P3-V2-C-F3).

    The version this replaces registered this file as the red case for
    `axes.structural_role` and reasoned that "the axis is the one fact
    that says so". It was not. The declaration is matched by NAME, so
    the only thing this file changed that the axis could see is the name
    at that position -- which `header.names` states outright and
    `position.at` states for that column. The axis was a third copy of
    one piece of evidence on the one description in the suite that
    declares an identifier, and a HELD line no file could move on every
    description that does not.

    So the axis is a listing entry now, and this test is what says the
    file is still caught, by the two checks that can actually see it.
    """
    described, twin = every_role
    declared = described.settings.forced_identifiers[0]
    lines = twin.split("\n")
    names = lines[0].split(",")
    for index, name in enumerate(names):
        if name == declared:
            names[index] = "another_name"
    lines[0] = ",".join(names)
    outcome = _measure(tmp_path, described, "\n".join(lines), "renamed.csv")
    assert not [
        check
        for check in outcome.checks
        if check.subcheck == "axes.structural_role"
    ]
    assert _verdicts(outcome, "header.names") == [validation.MISSED]
    position = [
        check
        for check in outcome.checks
        if check.subcheck == "position.at" and check.column == declared
    ]
    assert len(position) == 1
    assert position[0].verdict == validation.MISSED


# -- V6.4: the two degenerate zero-row forms --------------------------


def _zero_row_profile(described: contract.Profile) -> contract.Profile:
    """The same description with its row count taken down to zero."""
    return dataclasses.replace(described, n_rows=0)


def test_the_headered_zero_row_form_is_the_check(
    tmp_path: pathlib.Path,
) -> None:
    """Owner decision 7: the byte form IS the executable subcheck."""
    folder = tmp_path / "zero"
    folder.mkdir()
    described = _describe(
        folder,
        fixtures.single_column_table(
            "reading", fixtures.numbers(41, 40, 1, 9)
        ),
        stem="rows",
    )
    zero = _zero_row_profile(described)
    good = _measure(folder, zero, "reading\n", "empty-twin.csv")
    assert _verdicts(good, "bytes.zero-row-form") == [validation.HELD]
    bad = _measure(folder, zero, "reading\n1\n", "nonempty-twin.csv")
    assert _verdicts(bad, "bytes.zero-row-form") == [validation.MISSED]


def test_the_zero_row_form_lists_what_no_bytes_can_evidence(
    tmp_path: pathlib.Path,
) -> None:
    """The structural facts an empty file cannot show are listed, not passed."""
    folder = tmp_path / "zero-listings"
    folder.mkdir()
    described = _describe(
        folder,
        fixtures.single_column_table(
            "reading", fixtures.numbers(51, 40, 1, 9)
        ),
        stem="rows",
    )
    zero = _zero_row_profile(described)
    outcome = _measure(folder, zero, "reading\n", "empty.csv")
    assert outcome.census.not_checkable == len(outcome.listings)
    assert outcome.listings


# -- V1.4: what the validate path may not reach -----------------------


def test_the_module_never_imports_the_generator() -> None:
    """V1.4, read off the source rather than trusted.

    A validator that called `plan_generation` would share every planner
    defect with the generator it is a second opinion on, and no test of
    an end-to-end run could see it.
    """
    source = pathlib.Path(validation.__file__).read_text(encoding="utf-8")
    for line in source.split("\n"):
        if line.startswith(("import ", "from ")):
            assert "generation" not in line
            assert "random" not in line
    assert not hasattr(validation, "generation")
    assert "default_rng" not in source
    assert "Random(" not in source


def test_input_side_entries_carry_no_verdict_and_no_listing(
    tmp_path: pathlib.Path,
    every_role: "tuple[contract.Profile, str]",
) -> None:
    """V3.3: an input-side fact may be neither checked nor listed.

    The contract says a LOADER-ONLY fact imposes no obligation on the
    written CSV, so dressing one as a check would invent an obligation
    the matrix refuses to state, and listing it as an unverified twin
    fact would do the same in quieter words.
    """
    described, twin = every_role
    outcome = _measure(tmp_path, described, twin)
    named = set()
    for group, field in validation.INPUT_SIDE_ENTRIES:
        named.add(f"{group}.{field}")
    # `columns` is the one fact that is BOTH, and the split is the
    # contract's own: its profile-side membership rule is input-side,
    # while its twin-side rule -- that the list order IS the CSV's
    # column order -- is an executable subcheck. Totality is over
    # obligations, not over facts, so one fact contributing two kinds is
    # the rule rather than an exception to it.
    both = "document.columns"
    for check in outcome.checks:
        assert check.fact not in named or check.fact == both
    for listing in outcome.listings:
        assert listing.fact not in named or listing.fact == both


def test_red_a_collapsed_ladder_misses_the_middle_rung(
    tmp_path: pathlib.Path,
) -> None:
    """NAMED SUBCHECK: ladder.p50, on a ladder far from a straight line.

    The mutant this window exists to reject: a file that ignores the
    nine interior rungs and spreads its values evenly between the two
    ends. On a column whose own ladder is nearly straight such a file
    is indistinguishable from a conforming one, so the fixture is built
    deliberately lopsided -- most of its values in a narrow band low
    down, a few far above -- which is where the collapse shows.

    A window a wrong file cannot leave is not a check, and this is the
    case that proves this one is not that.
    """
    folder = tmp_path / "ladder"
    folder.mkdir()
    values = [f"{1 + (index % 5) * 0.01:.2f}" for index in range(180)]
    values = values + [f"{900 + index:.2f}" for index in range(20)]
    described = _describe(
        folder, fixtures.single_column_table("amount", values), stem="steep"
    )
    column = described.columns[0]
    facts = column.facts
    assert isinstance(facts, contract.NumericFacts)
    low = facts.percentiles.minimum
    high = facts.percentiles.maximum
    assert low is not None and high is not None
    spread = [
        f"{low + (high - low) * index / 199:.2f}" for index in range(200)
    ]
    outcome = _measure(
        folder,
        described,
        fixtures.single_column_table("amount", spread),
        "collapsed.csv",
    )
    assert _verdicts(outcome, "ladder.p50") == [validation.MISSED]


def test_the_ladder_window_accepts_the_twin_of_the_steep_column(
    tmp_path: pathlib.Path,
) -> None:
    """...and the same window accepts the twin the generator writes.

    The pair matters: a window that rejected the collapse mutant by
    being narrow would reject the conforming twin too, and a report
    that accused a conforming twin would be worse than no report.
    """
    folder = tmp_path / "ladder-green"
    folder.mkdir()
    values = [f"{1 + (index % 5) * 0.01:.2f}" for index in range(180)]
    values = values + [f"{900 + index:.2f}" for index in range(20)]
    described = _describe(
        folder, fixtures.single_column_table("amount", values), stem="steep"
    )
    outcome = _measure(
        folder, described, _twin_text(described), "steep-twin.csv"
    )
    for rung in ("ladder.p10", "ladder.p50", "ladder.p90"):
        assert _verdicts(outcome, rung) != [validation.MISSED]
