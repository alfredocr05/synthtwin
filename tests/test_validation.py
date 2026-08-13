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

import dataclasses
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
) -> contract.Profile:
    """Profile one table's text through the real producer and loader."""
    return _described(folder, text, declared, stem)[0]


def _described(
    folder: pathlib.Path,
    text: str,
    declared: "list[str] | None" = None,
    stem: str = "table",
) -> "tuple[contract.Profile, str]":
    """The same, with the description's own bytes beside it.

    The bytes are what tells a PUBLISHED string from a MEASURED one:
    every label a result may name is one the description itself
    carries, so a string that is in neither the description nor this
    module's own fixed words is a string read out of the measured file.
    """
    table_path = fixtures.write(folder, f"{stem}.csv", text)
    table = reading.read_table(str(table_path))
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
    line against it either, because repeated candidate descriptions
    would binary-search a number the file's own description withholds.
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


def test_the_kept_set_recovers_all_three_published_routes(
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


def test_the_offsets_corner_is_named_with_its_citation(
    tmp_path: pathlib.Path,
) -> None:
    """A datetime column whose offsets are the single withheld key.

    The verdict must be AUTHORIZED-DEVIATION, and it must APPEAR with
    the passage that authorizes it: a deviation the validator fails to
    name is itself a red test.
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
    named = [
        check
        for check in outcome.checks
        if check.subcheck == "offsets.map"
    ]
    assert len(named) == 1
    assert named[0].verdict == validation.AUTHORIZED_DEVIATION
    assert named[0].citation


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
