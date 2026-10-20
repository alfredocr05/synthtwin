"""P4-D406 (lane HX2): on a table of several rows a person, every published value is counted in persons.

THE FINDING (measured on lane HX's head 5793f7b0; P4-D401 and K-S3-64's
stated shapes). The floor -- every printed count nought or at least eleven
-- counted ROWS, so a value one patient holds on fourteen rows passed it:
beside a declared person column, health plan numbers `XKH#########` (142 of
150 published whole at 20,000 rows, 19,929 twin cells) and account numbers
`ACC########` (137 of 150, 19,886 twin cells); and a name, a street address
or a full birth date beside a patient key whose person question is open.

THE RULE. Where the table has a SUBJECT column -- declared (a person column
named or answered) or a candidate (every column the open person question is
put to) -- each value the description publishes for any other column is held
by at least eleven DIFFERENT subjects under every subject column, as well as
passing the row floor. A column ATTACHED to the subject (one value a person,
as a name or a birth date is) counts every value it publishes; any other
column counts the values the row floor would publish because eleven rows hold
them, while its points along the range stay judged as the floor judges them
on a table of one row a person. A column that would publish such a value is
held as a record number counted in people (contract NF126): no value, the
census its counts imply, made-up values in its layouts in the twin, and its
printed counts the whole column's, held by every subject. A subject column
counts only where it repeats and holds at least eleven different values. A
table whose subject columns are each different on every row, or that has
none, is described exactly as before.

THE GATE: (1) the counted shapes at 600 and 20,000 rows publish no value
fewer than eleven subjects hold and the twin writes none; (2) byte identity
where no subject column repeats; (3) two candidates, a value passing under one
and failing under the other: not published; (4) every twin validates; (5) the
pieces the mutants break -- rows counted for subjects, the first candidate
alone, a subject counted twice under the cap, the remainder (the held
column's counts) counted where fewer than eleven subjects stand -- each pinned
here.
"""

from __future__ import annotations

import contextlib
import io
import json
import pathlib
import random

import pytest

from synthtwin import cli, profile, reading, taxonomy

import persons_counted
import unanswered_identifier_shapes as shapes

_NOTICE = "VALUES HELD BY FEWER THAN 11 PEOPLE"


def _profile(table: pathlib.Path, folder: pathlib.Path, *extra: str) -> "tuple[int, str]":
    screen = io.StringIO()
    with shapes.nobody_at_the_keyboard():
        with contextlib.redirect_stdout(screen), contextlib.redirect_stderr(screen):
            code = cli.main(["profile", f"{table}", "--out-dir", f"{folder}", "--replace", *extra])
    return code, screen.getvalue()


def _twin_validates(table: pathlib.Path, folder: pathlib.Path) -> int:
    stem = table.name[: -len(".csv")]
    quiet = io.StringIO()
    with contextlib.redirect_stdout(quiet), contextlib.redirect_stderr(quiet):
        assert cli.main(["generate", f"{folder / (stem + '-profile.json')}", "--out-dir",
                         f"{folder}", "--seed", "0", "--replace"]) == 0
        return cli.main(["validate", f"{folder / (stem + '-profile.json')}", "--twin",
                         f"{folder / (stem + '-twin.csv')}", "--out-dir", f"{folder}",
                         "--replace"])


def _described(folder: pathlib.Path, stem: str) -> "dict[str, object]":
    return json.loads((folder / f"{stem}-profile.json").read_text(encoding="utf-8"))


def _block(described: "dict[str, object]", name: str) -> "dict[str, object]":
    return [one for one in described["columns"] if one["name"] == name][0]


# -- (1) and (4): the counted shapes, at both sizes ------------------------


@pytest.mark.parametrize("rows", (600, 20000))
@pytest.mark.parametrize("kind", shapes.COUNTED)
def test_a_value_fewer_than_eleven_people_hold_is_not_published(
    tmp_path: pathlib.Path, kind: str, rows: int
) -> None:
    """0 real values or fragments published, 0 in the twin, and the twin validates."""
    seen = shapes.run(tmp_path, kind, rows)
    assert seen["profile_exit"] == 0 and seen["generate_exit"] == 0
    assert seen["validate_exit"] == 0, seen
    assert seen["description_values"] == 0, seen
    assert seen["description_fragments"] == 0, seen
    assert seen["twin_cells"] == 0, seen
    assert seen["twin_fragments"] == 0, seen
    assert seen["role"] == taxonomy.ROLE_IDENTIFIER
    # A shape the person question is put to itself (128 names over 600
    # rows beside the padded key) is held by lane HX's rule, its own
    # question open; every other is held by the count in people.
    asked_itself = bool(seen["asked"])
    if asked_itself:
        assert kind == "name_keyzero" and rows == 600, seen["asked"]
        assert seen["evidence"] == taxonomy.rendered(taxonomy.EVIDENCE_UNANSWERED_IDENTITY, ())
    else:
        assert _NOTICE in f"{seen['screen']}"
        assert seen["evidence"] == taxonomy.rendered(taxonomy.EVIDENCE_HELD_IN_PEOPLE, ())
    # ...and the counter written apart from the product finds no value of
    # ANY column, under any subject column, that one to ten subjects hold.
    table = tmp_path / f"{kind}_long.csv"
    assert _real_misses(table, tmp_path) <= _CENSUS_ONLY
    counted = persons_counted.count_files(table, tmp_path)
    assert counted["subjects"] == ["patient"] + ([kind] if asked_itself else []), counted
    assert counted["few"] == 0, counted
    # A declared person column publishes its census of rows a person
    # counted in people: no entry of one to ten people stands apart.
    if kind.endswith("_beside"):
        block = _block(_described(tmp_path, f"{kind}_long"), "patient")
        cells = [line.split(",")[0] for line in
                 table.read_text(encoding="utf-8").splitlines()[1:]]
        assert persons_counted.census_few(block, cells) == 0, block[
            "n_distinct_by_occurrences"]


def test_the_stated_shapes_have_no_people_to_count_in(tmp_path: pathlib.Path) -> None:
    """A name with no patient key beside it: no subject column, described as before."""
    seen = shapes.run(tmp_path, "name", 600)
    counted = persons_counted.count_files(tmp_path / "name_long.csv", tmp_path)
    assert counted["subjects"] == []
    assert _NOTICE not in f"{seen['screen']}"
    assert seen["description_values"] > 0


# -- (2) byte identity where no subject column repeats ---------------------


def _visits(rows: int, subjects: "int | None") -> str:
    draw = random.Random(4)
    lines = ["subject_id,site,score,taken"]
    for place in range(rows):
        who = place if subjects is None else place % subjects
        lines += [f"P{who + 1:05d},{('north', 'south', 'east', 'west')[place % 4]},"
                  f"{draw.randint(0, 100)},2024-0{1 + place % 9}-1{place % 10}"]
    return "\n".join(lines) + "\n"


@pytest.mark.parametrize(
    "shape", ["one row a person", "a long table with no subject column"]
)
def test_no_repeating_subject_column_is_described_byte_for_byte(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, shape: str
) -> None:
    """Nothing of the count runs, so every byte is the base product's."""

    def refused(*_args: object, **_kwargs: object) -> object:
        raise AssertionError("the count in people ran where no subject column repeats")

    monkeypatch.setattr(profile, "_counted_in_subjects", refused)
    monkeypatch.setattr(profile, "_layouts_in_subjects", refused)
    monkeypatch.setattr(taxonomy, "with_census_in_people", refused)
    table = tmp_path / "visits.csv"
    if shape == "one row a person":
        table.write_text(_visits(1200, None), encoding="utf-8", newline="\n")
        code, screen = _profile(table, tmp_path, "--identifier", "subject_id")
    else:
        shapes.write_table(tmp_path, "dob", 600)
        table = tmp_path / "dob_long.csv"
        code, screen = _profile(table, tmp_path)
    assert code == 0
    assert _NOTICE not in screen


def test_a_subject_column_different_on_every_row_counts_nothing(tmp_path: pathlib.Path) -> None:
    """Named as a subject, a column of one row a person changes no byte."""
    table = tmp_path / "visits.csv"
    table.write_text(_visits(1200, None), encoding="utf-8", newline="\n")
    read = reading.read_table(str(table))
    settings = taxonomy.Settings()
    before = profile.serialize(profile.build_document(read, settings, ["subject_id"]))
    after = profile.serialize(
        profile.build_document(read, settings, ["subject_id"], subjects=["subject_id"])
    )
    assert after == before


# -- (3) two candidates ----------------------------------------------------


def test_a_value_passing_under_one_candidate_and_failing_under_another_is_not_published(
    tmp_path: pathlib.Path,
) -> None:
    table = tmp_path / "two.csv"
    table.write_text(persons_counted.two_candidates(600), encoding="utf-8", newline="\n")
    code, screen = _profile(table, tmp_path)
    assert code == 0
    north = [row for row in table.read_text(encoding="utf-8").splitlines() if ",North," in row]
    people = {row.split(",")[0] for row in north}
    visits = {row.split(",")[1] for row in north}
    assert len(people) >= 11 and len(visits) == 5 and len(north) >= 11
    described = _described(tmp_path, "two")
    labels = [level["label"] for level in _block(described, "site").get("levels", [])]
    assert "north" not in labels
    assert "north" not in json.dumps(_block(described, "site")).casefold()
    counted = persons_counted.count_files(table, tmp_path)
    assert counted["subjects"] == ["patient", "visit"]
    assert counted["few"] == 0, counted
    assert _NOTICE in screen
    assert _twin_validates(table, tmp_path) == 0
    assert _real_misses(table, tmp_path) <= _CENSUS_ONLY


# -- (5) the pieces the mutants break --------------------------------------


def test_the_count_is_of_subjects_not_rows() -> None:
    held = profile.subjects_holding(["x"] * 14, ["s1"] * 14, 11)
    assert held["x"].rows == 14
    assert held["x"].holders == ("s1",)


def test_the_cap_keeps_at_most_the_floor_and_never_a_subject_twice() -> None:
    values = ["x"] * 40
    subjects = [f"s{place % 20}" for place in range(40)]
    held = profile.subjects_holding(values, subjects, 11)
    assert held["x"].rows == 40
    assert len(held["x"].holders) == 11
    assert len(set(held["x"].holders)) == 11
    twice = profile.subjects_holding(["y"] * 6, ["a", "a", "b", "b", "a", "c"], 11)
    assert twice["y"].holders == ("a", "b", "c")


def test_the_remainder_is_held_by_eleven_people_or_none(tmp_path: pathlib.Path) -> None:
    """C (three patients) is withheld, and what the column prints is held by eleven or more.

    The column is held whole, so its printed counts are its totals, and the
    rows behind them -- every row whose value it does not name -- belong to
    eleven patients or more; the real table meets its own description.
    """
    table = tmp_path / "sites.csv"
    table.write_text(persons_counted.site_table(1200), encoding="utf-8", newline="\n")
    rows = [line.split(",") for line in table.read_text(encoding="utf-8").splitlines()[1:]]
    c_people = {row[0] for row in rows if row[1] == "C"}
    c_rows = [row for row in rows if row[1] == "C"]
    assert 1 <= len(c_people) <= 10 and len(c_rows) >= 11
    code, _screen = _profile(table, tmp_path, "--identifier", "patient")
    assert code == 0
    block = _block(_described(tmp_path, "sites"), "site")
    labels = [level["label"] for level in block.get("levels", [])]
    assert "c" not in labels
    held = {row[0] for row in rows if row[1].casefold() not in labels}
    assert block["n_missing"] == 0 or len(held) >= 11, (block["n_missing"], len(held), labels)
    counted = persons_counted.count_files(table, tmp_path)
    assert counted["few"] == 0, counted
    assert _twin_validates(table, tmp_path) == 0
    assert _real_misses(table, tmp_path) <= _CENSUS_ONLY


def _real_misses(table: pathlib.Path, folder: pathlib.Path) -> "set[str]":
    """What the REAL table misses of its own description.

    A held column publishes the census of repetition its counts imply, not
    the table's own (C6-80a, as under P4-D401), so the real table may miss
    that census and nothing else.
    """
    stem = table.name[: -len(".csv")]
    quiet = io.StringIO()
    checked = folder / "real-check"
    checked.mkdir(exist_ok=True)
    with contextlib.redirect_stdout(quiet), contextlib.redirect_stderr(quiet):
        code = cli.main(["validate", f"{folder / (stem + '-profile.json')}", "--twin",
                         f"{table}", "--out-dir", f"{checked}", "--replace"])
    assert code in (0, 3)
    missed: "set[str]" = set()
    for report in checked.glob("*.txt"):
        for line in report.read_text(encoding="utf-8").splitlines():
            if line.rstrip().endswith(": MISSED"):
                missed.add(line.strip().split(" ")[0])
    return missed


_CENSUS_ONLY = {"distinct.n_distinct_by_occurrences"}


def test_a_candidate_of_fewer_than_eleven_values_counts_nothing(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A code of seven values put the person question is no subject: every other column stands."""
    draw = random.Random(5)
    lines = ["value,other"]
    for place in range(800):
        lines += [f"{('north', 'south', 'east')[draw.randrange(3)]},row{place % 7}"]
    table = tmp_path / "seven.csv"
    table.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    code, screen = _profile(table, tmp_path)
    assert code == 0
    assert "other" in json.dumps(json.loads(
        (tmp_path / "seven-questions.json").read_text(encoding="utf-8"))["asked"])
    assert _NOTICE not in screen
    block = _block(_described(tmp_path, "seven"), "value")
    assert sorted(level["label"] for level in block["levels"]) == ["east", "north", "south"]


def test_a_column_attached_to_its_people_counts_every_value_it_publishes(
    tmp_path: pathlib.Path,
) -> None:
    """Birth dates of 150 patients on four rows each: no date reaches eleven rows, none is published.

    The row floor's reason fails nowhere here -- no birth date stands on
    eleven rows -- so only the attachment (one date a patient) reaches the
    dates the ladder of the column prints.
    """
    draw = random.Random(13)
    born = [f"{draw.randint(1930, 2005)}-{draw.randint(1, 12):02d}-{draw.randint(1, 28):02d}"
            for _person in range(150)]
    lines = ["patient,dob,value"]
    for place in range(600):
        person = place % 150
        lines += [f"REC{40000000 + 13 * person:08d},{born[person]},{draw.uniform(3, 150):.1f}"]
    table = tmp_path / "born.csv"
    table.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    code, screen = _profile(table, tmp_path, "--identifier", "patient")
    assert code == 0
    block = _block(_described(tmp_path, "born"), "dob")
    assert block["role"] == taxonomy.ROLE_IDENTIFIER
    for day in set(born):
        assert day not in json.dumps(block)
    assert persons_counted.count_files(table, tmp_path)["few"] == 0
    assert _NOTICE in screen
    assert _twin_validates(table, tmp_path) == 0


# -- the first repair (skeptic 1 of lane HX2) ------------------------------


def _profiled(tmp_path: pathlib.Path, stem: str, text: str, *extra: str) -> "tuple[pathlib.Path, str]":
    table = tmp_path / f"{stem}.csv"
    table.write_text(text, encoding="utf-8", newline="\n")
    code, screen = _profile(table, tmp_path, *extra)
    assert code == 0, screen
    return table, screen


def _held(block: "dict[str, object]") -> bool:
    return block["role"] == taxonomy.ROLE_IDENTIFIER and block[
        "detection_evidence"] == taxonomy.rendered(taxonomy.EVIDENCE_HELD_IN_PEOPLE, ())


def test_the_two_candidates_in_the_other_order_publish_nothing_either(
    tmp_path: pathlib.Path,
) -> None:
    """Item 7: the value failing under the FIRST candidate only is held too."""
    table, screen = _profiled(tmp_path, "two", persons_counted.two_candidates_reversed(600))
    described = _described(tmp_path, "two")
    assert "north" not in json.dumps(_block(described, "site")).casefold()
    counted = persons_counted.count_files(table, tmp_path)
    assert counted["subjects"] == ["visit", "patient"]
    assert counted["few"] == 0, counted
    assert _NOTICE in screen


def test_the_remainder_the_floor_merges_is_counted_in_people(tmp_path: pathlib.Path) -> None:
    """Item 3: rare sites of three patients, merged into one remainder of more than eleven rows."""
    table, _screen = _profiled(tmp_path, "rest", persons_counted.remainder_table(2000),
                               "--identifier", "patient")
    rows = [line.split(",") for line in table.read_text(encoding="utf-8").splitlines()[1:]]
    rare = [row for row in rows if row[1].startswith("Rare")]
    assert len({row[0] for row in rare}) == 3 and len(rare) >= 11
    block = _block(_described(tmp_path, "rest"), "site")
    assert _held(block), block
    assert "suppressed_rows" not in block
    assert persons_counted.count_files(table, tmp_path)["few"] == 0
    assert _twin_validates(table, tmp_path) == 0


def test_a_column_written_for_two_people_publishes_no_statistic_of_them(
    tmp_path: pathlib.Path,
) -> None:
    """Item 3: fifteen readings of two patients -- their mean, spread and points are not published."""
    table, _screen = _profiled(tmp_path, "dose", persons_counted.sparse_table(2000),
                               "--identifier", "patient")
    block = _block(_described(tmp_path, "dose"), "dose")
    assert _held(block), block
    for statistic in ("mean", "std", "percentiles", "levels"):
        assert statistic not in block
    assert persons_counted.count_files(table, tmp_path)["few"] == 0
    assert _twin_validates(table, tmp_path) == 0


@pytest.mark.parametrize("kind", ("name_open", "address_open"))
def test_no_layout_fewer_than_eleven_people_wear_is_named(
    tmp_path: pathlib.Path, kind: str
) -> None:
    """Item 4: each layout the held column names is worn by eleven patients or more."""
    seen = shapes.run(tmp_path, kind, 600)
    assert seen["validate_exit"] == 0, seen
    table = tmp_path / f"{kind}_long.csv"
    block = _block(_described(tmp_path, f"{kind}_long"), kind)
    rows = [line.split(",") for line in table.read_text(encoding="utf-8").splitlines()[1:]]
    from synthtwin import parsing
    present = [row[1] for row in rows]
    convention = parsing.layout_convention(present)
    named = [form for form in block["layout_forms"] if form != taxonomy.SUPPRESSED_LABEL]
    for form in named:
        wearing = {row[0] for row in rows
                   if parsing.layout_form(row[1], convention) == form}
        assert len(wearing) >= 11, (form, len(wearing))
    assert persons_counted.count_files(table, tmp_path)["few"] == 0


@pytest.mark.parametrize("small", (False, True))
def test_the_person_census_is_counted_in_people(tmp_path: pathlib.Path, small: bool) -> None:
    """Item 6: groups of eleven people or more stand as they are; a pool of three takes more in."""
    table, _screen = _profiled(tmp_path, "people", persons_counted.census_table(small),
                               "--identifier", "patient")
    block = _block(_described(tmp_path, "people"), "patient")
    census = {int(key): value for key, value in block["n_distinct_by_occurrences"].items()}
    cells = [line.split(",")[0] for line in table.read_text(encoding="utf-8").splitlines()[1:]]
    assert persons_counted.census_few(block, cells) == 0, census
    if not small:
        assert census == {1: 30, 2: 40, 3: 25, 4: 20, 5: 15}
        assert _real_misses(table, tmp_path) == set()
    else:
        assert 9 not in census and 7 not in census, census
        assert sum(census.values()) == 133
        assert sum(size * people for size, people in census.items()) == len(cells)
    assert _twin_validates(table, tmp_path) == 0


@pytest.mark.parametrize("differing", (0.0, 0.25))
def test_a_measurement_attached_to_its_people_counts_its_points(
    tmp_path: pathlib.Path, differing: float
) -> None:
    """Item 7: one size a patient is held; a quarter of the later rows changed, it is not."""
    table, _screen = _profiled(tmp_path, "tall", persons_counted.size_table(differing),
                               "--identifier", "patient")
    block = _block(_described(tmp_path, "tall"), "size")
    if differing == 0.0:
        assert _held(block), block
        assert persons_counted.count_files(table, tmp_path)["few"] == 0
    else:
        assert block["role"] == taxonomy.ROLE_CONTINUOUS, block["role"]
    assert _twin_validates(table, tmp_path) == 0


@pytest.mark.parametrize("written", ("iso", "us"))
def test_dates_and_times_of_day_are_counted_in_people_at_their_points(
    tmp_path: pathlib.Path, written: str
) -> None:
    """Ruling of 2026-10-19 15:42, item 2: a visit date or a time a few patients hold is no point.

    No date stands on eleven rows, so the row floor's own reason holds
    none: the dates' points, each held by a patient or two, are what the
    count reaches. Written `04/17/2019`, a cell is the ISO point only read
    again in the block's format (item 7).
    """
    table, _screen = _profiled(tmp_path, "visits", persons_counted.visit_table(2000, written),
                               "--identifier", "patient")
    described = _described(tmp_path, "visits")
    assert _held(_block(described, "seen")), _block(described, "seen")["role"]
    assert _held(_block(described, "at")), _block(described, "at")["role"]
    assert _block(described, "value")["role"] == taxonomy.ROLE_CONTINUOUS
    assert persons_counted.count_files(table, tmp_path)["few"] == 0
    assert _twin_validates(table, tmp_path) == 0


def test_a_cell_is_read_as_each_published_value_it_can_be() -> None:
    """Item 7: a prefix, a mapping key and a word of a sentence are published values."""
    block: "dict[str, object]" = {
        "name": "x",
        "variants": {"Smithfield": 12},
        "remarks": ["the value Northgate stands on 14 rows"],
        "wrappers": [{"prefix": "CHF ", "count": 20}],
    }
    published = profile._published_in(block, True)
    assert "smithfield" in published.words
    assert "northgate" in published.words
    assert published.prefixes == ("chf",)
    keys = profile._keys_of("CHF 12.5", published, {})
    assert "pchf" in keys
    dated = profile._Published(frozenset({"2019-04-17"}), frozenset(), (), "month-first-date")
    assert "w2019-04-17" in profile._keys_of("04/17/2019", dated, {})


def test_a_written_form_fewer_than_eleven_people_wear_is_not_published(
    tmp_path: pathlib.Path,
) -> None:
    """Item 4 beside labels: two patients' own codes wear a form on more than eleven rows.

    Each code stands on too few rows to be named and the remainder the
    floor merges is held by many patients, so only the form -- a letter,
    two figures, a hyphen and a figure, worn by two people -- is a value
    of fewer than eleven; the row floor alone publishes it.
    """
    table, _screen = _profiled(tmp_path, "forms", persons_counted.forms_table(2000),
                               "--identifier", "patient")
    block = _block(_described(tmp_path, "forms"), "site")
    assert _held(block), block
    assert persons_counted.count_files(table, tmp_path)["few"] == 0
    assert _twin_validates(table, tmp_path) == 0


def test_a_pool_that_spreads_back_into_its_real_groups_takes_one_more(
    tmp_path: pathlib.Path,
) -> None:
    """Three patients on five rows, pooled with twenty-two on four, would print the real three."""
    table, _screen = _profiled(tmp_path, "people", persons_counted.census_twin_table(),
                               "--identifier", "patient")
    block = _block(_described(tmp_path, "people"), "patient")
    census = {int(key): value for key, value in block["n_distinct_by_occurrences"].items()}
    cells = [line.split(",")[0] for line in table.read_text(encoding="utf-8").splitlines()[1:]]
    assert persons_counted.census_few(block, cells) == 0, census
    assert census.get(5) != 3, census
    assert sum(census.values()) == 120
    assert sum(size * people for size, people in census.items()) == len(cells)
    assert _twin_validates(table, tmp_path) == 0


def test_a_filler_code_put_the_person_question_blanks_no_date(tmp_path: pathlib.Path) -> None:
    """Ruling of 2026-10-19 15:42, item 3: seven filler values count only what is attached to them."""
    table, _screen = _profiled(tmp_path, "filler", persons_counted.filler_table(800))
    block = _block(_described(tmp_path, "filler"), "seen")
    assert block["role"] == taxonomy.ROLE_DATETIME, block["role"]
    region = _block(_described(tmp_path, "filler"), "region")
    assert [level["label"] for level in region["levels"]] == ["north", "south"], region
    counted = persons_counted.count_files(table, tmp_path)
    assert counted["subjects"] == ["other"], counted
    assert counted["few"] == 0, counted


# -- lane HX2's second repair: skeptic 1, round 2 --------------------------
#
# Item 1 is the `_keyzero` shapes of `shapes.COUNTED` above: a birth date and
# a name beside a patient key of seven figures padded with zeros, which the
# codes-or-measurements question holds, at 600 and 20,000 rows.


def _x_rows(table: pathlib.Path) -> "list[list[str]]":
    return [line.split(",") for line in table.read_text(encoding="utf-8").splitlines()[1:]]


@pytest.mark.parametrize("rows", (2000, 20000))
def test_a_person_column_in_two_layouts_publishes_a_census_its_twin_meets(
    tmp_path: pathlib.Path, rows: int
) -> None:
    """Item 2: twenty patients keyed `P#####` beside 130 keyed `REC########`.

    Spread over the whole column the pooled census (13 and 14 rows a
    person at 2,000 rows) left no way to fill the 268 rows of `P#####`
    from twenty people; each layout's rows are spread over its own share
    of the people instead (`taxonomy._even_census`).
    """
    table, _screen = _profiled(tmp_path, "systems", persons_counted.two_systems_table(rows),
                               "--identifier", "patient")
    block = _block(_described(tmp_path, "systems"), "patient")
    assert len([form for form in block["layout_forms"] if form != "(withheld)"]) == 2, block
    # The census closes on the column's own counts and prints no real
    # group, judged by the counter alone (Codex's review of lane HX2, item
    # 11: no expected value drawn from the product's own helper).
    cells = [row[0] for row in _x_rows(table)]
    census = {int(key): value for key, value in block["n_distinct_by_occurrences"].items()}
    assert sum(census.values()) == len(set(cells))
    assert sum(size * people for size, people in census.items()) == len(cells)
    assert persons_counted.census_few(block, cells) == 0
    assert _twin_validates(table, tmp_path) == 0


def test_a_declared_identifier_beside_the_person_names_no_layout_three_people_wear(
    tmp_path: pathlib.Path,
) -> None:
    """Item 3: `x` declared beside `patient`; three patients' plans are written `ZQ-#####`."""
    table, _screen = _profiled(tmp_path, "plans", persons_counted.plan_rare_table(20000),
                               "--identifier", "patient", "--identifier", "x")
    described = _described(tmp_path, "plans")
    assert described["settings"]["person_columns"] == ["patient", "x"]
    block = _block(described, "x")
    assert "zq" not in json.dumps(block).casefold(), block
    summary = (tmp_path / "plans-profile.txt").read_text(encoding="utf-8")
    assert "ZQ" not in summary and "@@-%%%%%" not in summary
    assert persons_counted.count_files(table, tmp_path)["few"] == 0
    assert _twin_validates(table, tmp_path) == 0


def test_the_layouts_pool_prints_no_count_of_fewer_than_eleven_people(
    tmp_path: pathlib.Path,
) -> None:
    """Item 4: `ZQ-#####` pooled alone printed `(withheld)` on the rows of its three patients."""
    table, _screen = _profiled(tmp_path, "plans", persons_counted.plan_rare_table(20000),
                               "--identifier", "patient")
    block = _block(_described(tmp_path, "plans"), "x")
    rows = _x_rows(table)
    zq = [row for row in rows if row[1].startswith("ZQ")]
    assert len({row[0] for row in zq}) == 3 and len(zq) >= 11
    pool = block["layout_forms"].get("(withheld)", 0)
    named = [form for form in block["layout_forms"] if form != "(withheld)"]
    assert pool != len(zq), block["layout_forms"]
    assert named == [] and pool == block["n_present"], block["layout_forms"]
    assert persons_counted.count_files(table, tmp_path)["few"] == 0
    assert _twin_validates(table, tmp_path) == 0


def test_spellings_of_one_key_are_one_person(tmp_path: pathlib.Path) -> None:
    """Item 6: `Q87.4` six patients hold, their keys written three ways, is not published."""
    table = tmp_path / "spelled.csv"
    table.write_text(persons_counted.spellings_table(2000), encoding="utf-8", newline="\n")
    code, _screen = _profile(table, tmp_path)
    assert code == 0
    rows = _x_rows(table)
    holders = {persons_counted.subject_of(row[0]) for row in rows if row[1] == "Q87.4"}
    written = {row[0] for row in rows if row[1] == "Q87.4"}
    assert len(holders) == 6 and len(written) >= 11, (len(holders), len(written))
    block = _block(_described(tmp_path, "spelled"), "x")
    assert "q87.4" not in json.dumps(block).casefold()
    assert persons_counted.count_files(table, tmp_path)["few"] == 0
    twin = (tmp_path / "spelled-twin.csv")
    # The key's own twin misses its three case layouts on lane HX's head as
    # here (a held candidate written three ways: lane HX's, not this one).
    assert _twin_validates(table, tmp_path) in (0, 3)
    assert "Q87.4" not in twin.read_text(encoding="utf-8")


def test_the_subject_key_merges_spellings_and_never_splits_one() -> None:
    keys = profile.subject_keys(["REC20000007", "rec20000007", "REC-20000007", "REC 0020000007",
                                 "Rec20000008", "", "  ", "000", "A-01-02"])
    assert keys[:4] == ["rec20000007"] * 4
    assert keys[4] == "rec20000008"
    assert keys[5] == keys[6] == ""
    assert keys[7] == "0"
    assert keys[8] == "a12" == persons_counted.subject_of("A-01-02")
    for cell in ("REC-0007", "rec7", "Rec 7", "REC_7"):
        assert profile.subject_keys([cell]) == [persons_counted.subject_of(cell)] == ["rec7"]
    # Every spelling of nobody is ONE unknown subject (Codex's review, item 3).
    nobody = profile.subject_keys(list(persons_counted.NOBODY_FORMS) + ["  ", "unknown"])
    assert nobody[:-1] == [""] * (len(persons_counted.NOBODY_FORMS) + 1)
    assert nobody[-1] == "unknown"
    assert [persons_counted.subject_of(one) for one in persons_counted.NOBODY_FORMS] == [""] * 11
    assert profile.subject_keys(["N/A", "missing"], ("missing",)) == ["", ""]
    held = profile.subjects_holding(["x"] * 6, ["P1", "p1", "P-1", "P01", "p 1", "P2"], 11)
    assert held["x"].holders == ("p1", "p2")


@pytest.mark.parametrize("rows", (2000, 20000))
def test_a_name_in_capitals_on_some_rows_is_held_and_its_twin_is_a_stated_limit(
    tmp_path: pathlib.Path, rows: int
) -> None:
    """Item 5: names in capitals on 15 % of rows are held; no name published, none in the twin.

    The held column's layouts (five or more, beside a pool) are each met
    by an even census the generator's identifier packing walk does not
    always find: the twin misses a few rows of each named layout. A stated
    limit of the generator (plan P4-D406; owner CODES-1 part C), counted
    apart in K-S3-65 as `labs` and `diagnoses_procedures` are.
    """
    table, _screen = _profiled(tmp_path, "caps", persons_counted.capitals_table(rows))
    block = _block(_described(tmp_path, "caps"), "x")
    assert _held(block), block
    names = {row[1] for row in _x_rows(table)}
    text = json.dumps(block)
    assert not [name for name in names if name in text]
    assert persons_counted.count_files(table, tmp_path)["few"] == 0
    validated = _twin_validates(table, tmp_path)
    twin = (tmp_path / "caps-twin.csv").read_text(encoding="utf-8")
    assert not [name for name in names if name in twin]
    # THE STATED LIMIT, pinned: a twin that comes to meet its layouts
    # turns this red, and P4-D406, STATE and K-S3-65's `GENERATOR_LIMITS`
    # are corrected with it.
    assert validated == 3


def test_a_key_tuple_is_kept_once_and_a_day_is_read_only_where_one_is_published() -> None:
    """Item 7: a column of cells each different keeps one reference a row, and parses no day twice."""
    published = profile._published_in({"name": "x", "levels": [{"label": "Glucose"}]}, True)
    memo: "dict[str, tuple[str, ...]]" = {}
    interned: "dict[tuple[str, ...], tuple[str, ...]]" = {}
    first = profile._cell_keys("note one", published, {}, frozenset(), memo, interned)
    memo = {}
    second = profile._cell_keys("note two", published, {}, frozenset(), memo, interned)
    assert first == second and first is second
    stamps = profile._published_in({"name": "t", "role": taxonomy.ROLE_DATETIME,
                                    "format": "month-first-date", "n_present": 40}, True)
    assert stamps.date_format == ""
    days = profile._published_in({"name": "t", "role": taxonomy.ROLE_DATETIME,
                                  "format": "month-first-date",
                                  "date_percentiles": {"p50": "2019-04-17"}}, True)
    assert days.date_format == "month-first-date"


def test_a_spread_is_kept_only_where_the_layouts_can_hold_it() -> None:
    """Item 2: 13 and 14 rows a person cannot fill 268 rows from twenty; 2 and 3 can fill 405 and 395.

    The parts are the rows the POOLED people hold in each part, the groups
    kept standing where they are (Codex's review of lane HX2, item 1).
    """
    assert not taxonomy._spread_meets_layouts({13: 2, 14: 141}, [268, 1732])
    assert taxonomy._spread_meets_layouts({2: 316, 3: 56}, [405, 395])
    assert taxonomy._spread_meets_layouts({13: 2, 14: 141}, [2000])
    assert not taxonomy._spread_meets_layouts({4: 10}, [21, 19])
    assert taxonomy._spread_meets_layouts({4: 10}, [20, 20])
    # Fourteen rows from groups of three: no deal (Codex's item 1).
    assert not taxonomy._spread_meets_layouts({3: 12}, [14, 22])
    assert taxonomy._spread_meets_layouts({3: 12}, [15, 21])
    # Each PART must be possible, not the totals alone (the combined
    # verify's item 3): 15 rows from 13 and 14 cannot be, though
    # 144 <= 150 <= 153.
    assert not taxonomy._spread_meets_layouts({13: 100, 14: 50}, [15, 1985])
    # A census of sizes further apart is not judged: it is unmet, and the
    # caller publishes a census it can prove instead.
    assert not taxonomy._spread_meets_layouts({1: 302, 2: 67, 18: 16, 19: 4}, [422, 378])
    assert not taxonomy._spread_meets_layouts({4: 10}, [])


# -- lane HX2's third repair: Codex's review and the combined verify --------


def _census(block: "dict[str, object]") -> "dict[int, int]":
    census = block["n_distinct_by_occurrences"]
    assert isinstance(census, dict)
    return {int(key): int(value) for key, value in census.items()}


def _closes(block: "dict[str, object]", cells: "list[str]") -> None:
    census = _census(block)
    present = [cell for cell in cells if cell]
    assert sum(census.values()) == len(set(present)), census
    assert sum(size * people for size, people in census.items()) == len(present), census


def test_a_pooled_census_is_published_only_where_the_twin_can_deal_it(
    tmp_path: pathlib.Path,
) -> None:
    """Codex's item 1: groups of three cannot fill the 14 rows of one patient's `P#####`.

    The pooled spread is not published where it cannot be dealt into the
    layouts' parts; what is published closes, prints no real group, and
    the twin meets it.
    """
    table, _screen = _profiled(tmp_path, "deal", persons_counted.layouts_census_table(),
                               "--identifier", "patient")
    block = _block(_described(tmp_path, "deal"), "patient")
    cells = [row[0] for row in _x_rows(table)]
    _closes(block, cells)
    assert persons_counted.census_few(block, cells) == 0, block["n_distinct_by_occurrences"]
    assert _census(block) != {3: 12, 10: 88}, block["n_distinct_by_occurrences"]
    assert _twin_validates(table, tmp_path) == 0


@pytest.mark.xfail(
    strict=True,
    reason=(
        "STATED LIMIT (P4-D406 (c), lane MG): a person column's own layouts "
        "are counted in the OTHER subject columns, not in its own people: "
        "three patients keyed `P#####` print `P#####` on their 30 rows beside "
        "a census of ten rows a person. Counted in itself, a placeholder key "
        "such as `UNKNOWN` (one subject) pooled every layout of the column and "
        "its twin missed its own validation (K-S3-64's key_word shape)."
    ),
)
def test_a_layout_three_patients_keys_wear_is_not_named(tmp_path: pathlib.Path) -> None:
    """Codex's item 1, the part recorded: the person column's own layouts in its own people."""
    table, _screen = _profiled(tmp_path, "own", persons_counted.own_layout_table(),
                               "--identifier", "patient")
    block = _block(_described(tmp_path, "own"), "patient")
    named = [form for form in block["layout_forms"] if form != "(withheld)"]
    assert named == [], block["layout_forms"]
    assert block["layout_forms"].get("(withheld)", 0) != 30, block["layout_forms"]
    assert _twin_validates(table, tmp_path) == 0


def test_a_key_written_in_twelve_cases_is_one_person(tmp_path: pathlib.Path) -> None:
    """Codex's item 2: every raw key differs, yet `special` is held by five people on 60 rows."""
    table, _screen = _profiled(tmp_path, "cases", persons_counted.case_variants_table(),
                               "--identifier", "patient")
    block = _block(_described(tmp_path, "cases"), "flag")
    assert "special" not in json.dumps(block), block
    assert persons_counted.count_files(table, tmp_path)["few"] == 0
    assert _twin_validates(table, tmp_path) == 0


def test_every_spelling_of_nobody_is_one_unknown_person(tmp_path: pathlib.Path) -> None:
    """Codex's item 3: 22 visits of one unnamed patient in eleven spellings publish no `unk`."""
    table, _screen = _profiled(tmp_path, "nobody", persons_counted.nobody_table(),
                               "--identifier", "patient")
    block = _block(_described(tmp_path, "nobody"), "label")
    assert "unk" not in json.dumps(block), block
    assert persons_counted.count_files(table, tmp_path)["few"] == 0
    assert _twin_validates(table, tmp_path) == 0


def test_a_candidate_whose_own_values_are_not_held_is_still_a_subject(
    tmp_path: pathlib.Path,
) -> None:
    """Codex's item 4: a key read as free text publishes nothing itself, and the birth dates beside it are counted."""
    text, births = persons_counted.free_text_key_table()
    table, _screen = _profiled(tmp_path, "free", text)
    described = _described(tmp_path, "free")
    block = _block(described, "dob")
    published = json.dumps(block)
    assert not [birth for birth in births if birth in published], block
    counted = persons_counted.count_files(table, tmp_path)
    assert "patient" in counted["subjects"] and counted["few"] == 0, counted
    assert _twin_validates(table, tmp_path) == 0


@pytest.mark.parametrize("case", ("clock", "days", "comma"))
def test_a_cell_is_counted_as_the_value_its_column_reads_it_as(
    tmp_path: pathlib.Path, case: str
) -> None:
    """Codex's item 5: `8:30` is the `08:30` printed, `19000` a date, `10,07` the number 10.07."""
    if case == "clock":
        table, _screen = _profiled(tmp_path, "read", persons_counted.clock_table(),
                                   "--identifier", "patient")
        block = _block(_described(tmp_path, "read"), "clock")
        assert "08:30" not in json.dumps(block) and "8:30" not in json.dumps(block), block
    elif case == "days":
        table, _screen = _profiled(tmp_path, "read", persons_counted.day_count_table("plain"),
                                   "--identifier", "patient", "--date-count", "day",
                                   "days-since-1970")
        block = _block(_described(tmp_path, "read"), "day")
        assert "2022-" not in json.dumps(block) and "2023-" not in json.dumps(block), block
    else:
        table, _screen = _profiled(tmp_path, "read", persons_counted.comma_table(),
                                   "--identifier", "patient", "--decimal-comma", "m")
        block = _block(_described(tmp_path, "read"), "m")
        assert "percentiles" not in block, block
    assert block["role"] == taxonomy.ROLE_IDENTIFIER, block["role"]
    assert persons_counted.count_files(table, tmp_path)["few"] == 0
    assert _twin_validates(table, tmp_path) == 0


def test_the_oracle_reads_a_clock_whatever_the_hour_width() -> None:
    """Codex's item 5: the counter written apart reads `8:30` as the published `08:30` too."""
    block = {"name": "clock", "role": "time_of_day", "clock_heaps": [{"value": "08:30", "count": 36}]}
    assert persons_counted.is_published("8:30", block, persons_counted.leaves(block))
    assert not persons_counted.is_published("8:31", block, persons_counted.leaves(block))
    days = {"name": "d", "role": "datetime", "date_percentiles": {"p05": "2022-01-08"}}
    assert persons_counted.is_published("19000", days, persons_counted.leaves(days),
                                        ("days-since-1970", False))
    numbers = {"name": "m", "role": "continuous", "percentiles": {"p05": 10.07}}
    assert persons_counted.is_published("10,07", numbers, persons_counted.leaves(numbers),
                                        ("", True))


def test_a_census_spread_back_into_its_real_small_group_is_not_printed(
    tmp_path: pathlib.Path,
) -> None:
    """Codex's item 6: a hundred patients on nine rows and one on ten; the even spread is exactly that."""
    table, _screen = _profiled(tmp_path, "nine", persons_counted.nine_and_ten_table(),
                               "--identifier", "patient")
    block = _block(_described(tmp_path, "nine"), "patient")
    cells = [row[0] for row in _x_rows(table)]
    census = _census(block)
    assert census != {9: 100, 10: 1}, census
    assert all(people >= 11 for people in census.values()), census
    _closes(block, cells)
    assert persons_counted.census_few(block, cells) == 0
    assert _twin_validates(table, tmp_path) == 0


def test_the_census_oracle_exempts_no_census_drawn_from_counts() -> None:
    """Codex's item 11: an even spread that reproduces a real group of one prints it."""
    cells = [f"P{person}" for person in range(101) for _row in range(10 if person == 0 else 9)]
    block = {"n_distinct_by_occurrences": {"09": 100, "10": 1}, "n_present": len(cells),
             "layout_forms": {"@%": 101, "@%%": 810}}
    assert persons_counted.census_few(block, cells) == 1
    block["n_distinct_by_occurrences"] = {"08": 11, "09": 78, "10": 12}
    assert persons_counted.census_few(block, cells) == 0


def test_a_layout_census_of_nothing_but_a_pool_two_people_hold_is_not_printed(
    tmp_path: pathlib.Path,
) -> None:
    """Codex's item 7: `A12345` and `BB23456` on two patients' rows printed `(withheld)` 20."""
    table, _screen = _profiled(tmp_path, "pool", persons_counted.pool_only_table(),
                               "--identifier", "patient")
    block = _block(_described(tmp_path, "pool"), "x")
    assert block["layout_forms"] == {}, block["layout_forms"]
    assert persons_counted.count_files(table, tmp_path)["few"] == 0
    assert _twin_validates(table, tmp_path) == 0


def test_a_run_of_four_hundred_figures_is_no_number(tmp_path: pathlib.Path) -> None:
    """Codex's item 8: ordinary profiling accepts it, and so does the count in people."""
    code, _screen = _profile(_written(tmp_path, "long", persons_counted.long_figures_table()),
                             tmp_path, "--identifier", "patient")
    assert code == 0
    published = profile._published_in({"name": "n", "percentiles": {"p50": 9.0}}, True)
    assert profile._keys_of("item " + "9" * 400 + " value 7", published, {}) == ()
    assert persons_counted._figures("item " + "9" * 400) is None


def _written(tmp_path: pathlib.Path, stem: str, text: str) -> pathlib.Path:
    table = tmp_path / f"{stem}.csv"
    table.write_text(text, encoding="utf-8", newline="\n")
    return table


class _NeverAsked(tuple):  # type: ignore[type-arg]
    """A tuple a membership question must never be put to."""

    def __contains__(self, _item: object) -> bool:
        raise AssertionError("asked a tuple of held layouts, once a layout")


def _record_numbers(forms: "dict[str, int]") -> taxonomy.ColumnProfile:
    return taxonomy.ColumnProfile(
        name="x", position=1, role=taxonomy.ROLE_IDENTIFIER, statistical_type="code",
        quality_state="ok", structural_role="identifier",
        detection_evidence=taxonomy.note(taxonomy.EVIDENCE_HELD_IN_PEOPLE),
        n_present=sum(forms.values()), n_missing=0, missing_by_source={},
        missing_by_class={}, n_missing_blank=0, n_missing_withheld=0,
        details={"layout_forms": dict(forms), "n_code_alphabet": 0, "n_all_digits": 0},
        publication_notes=[], remarks=[],
    )


def test_held_layouts_are_asked_of_a_set() -> None:
    """Codex's item 9: pooling many layouts asks a set, never a tuple once a layout."""
    forms = {f"@{index:05d}": 11 for index in range(40)}
    pooled = taxonomy.layouts_counted_in_people(
        _record_numbers(forms), _NeverAsked(sorted(forms)[:20]), 11, False)
    census = pooled.details["layout_forms"]
    assert isinstance(census, dict)
    assert census.get("(withheld)") == 220 and len(census) == 21, census


def test_a_raised_floor_asks_a_set_of_subjects() -> None:
    """Codex's item 10: at a floor of 50,001 the count keeps a set beside each list.

    Asked of the list alone, 100,000 subjects cost about 3.75 billion
    comparisons before the cap; asked of a set, a hundred thousand.
    """
    import time

    subjects = [f"s{index}" for index in range(100000)]
    began = time.perf_counter()
    held = profile.subjects_holding(["x"] * 100000, subjects, 50001)
    assert len(held["x"].holders) == 50001
    assert time.perf_counter() - began < 3.0
    # At the default floor the list alone is kept, as before.
    assert profile.subjects_holding(["x"] * 30, subjects[:15] * 2, 11)["x"].holders == tuple(
        subjects[:11])


def test_the_counter_counts_a_published_prefix_in_people() -> None:
    """Codex's item 12: a block publishing the prefix `ZX` three of 120 people wear."""
    names = ["patient", "x"]
    patients = [f"REC{person:04d}" for person in range(120) for _row in range(12)]
    xs = [(f"ZX{10000 + person}" if person < 3 else f"AB{10000 + person}")
          for person in range(120) for _row in range(12)]
    described = {"settings": {"person_columns": ["patient"]},
                 "columns": [{"name": "patient", "role": "identifier"},
                             {"name": "x", "role": "identifier",
                              "layout_prefixes": {"(column)": "ZX"}}]}
    found = persons_counted.count(names, [patients, xs], described, ["patient"])
    assert found["few"] >= 1 and "x:prefix zx" in found["named"], found


@pytest.mark.parametrize("rows", (2000, 20000))
def test_a_layouts_pool_is_counted_under_every_candidate(
    tmp_path: pathlib.Path, rows: int
) -> None:
    """The combined verify's item 2: `ZZ-####` three households wear, beside `patient` and `acct`."""
    table, _screen = _profiled(tmp_path, "cards", persons_counted.two_card_table(rows))
    block = _block(_described(tmp_path, "cards"), "card")
    named = [form for form in block["layout_forms"] if form != "(withheld)"]
    assert named == [], block["layout_forms"]
    lines = [line.split(",") for line in table.read_text(encoding="utf-8").splitlines()[1:]]
    zz = [line for line in lines if line[2].startswith("ZZ")]
    assert block["layout_forms"].get("(withheld)", 0) != len(zz)
    counted = persons_counted.count_files(table, tmp_path)
    assert "acct" in counted["subjects"] and counted["few"] == 0, counted
    assert _twin_validates(table, tmp_path) == 0


def test_dates_declared_as_counts_and_not_read_are_held(tmp_path: pathlib.Path) -> None:
    """The orchestrator's addendum 2: Excel days written `42.345` publish no mean, point or tail."""
    table, screen = _profiled(tmp_path, "pointed", persons_counted.day_count_table("pointed"),
                              "--identifier", "patient", "--date-count", "day", "excel-1900")
    described = _described(tmp_path, "pointed")
    block = _block(described, "day")
    assert block["role"] == taxonomy.ROLE_IDENTIFIER, block
    for field in ("mean", "percentiles", "low_tail", "high_tail"):
        assert field not in block, field
    assert "42." not in json.dumps(block)
    assert _NOTICE in screen
    assert described["settings"]["forced_date_counts"] == []
    assert _twin_validates(table, tmp_path) == 0
