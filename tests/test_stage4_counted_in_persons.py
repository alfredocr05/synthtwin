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
    assert _NOTICE in f"{seen['screen']}"
    assert seen["role"] == taxonomy.ROLE_IDENTIFIER
    assert seen["evidence"] == taxonomy.rendered(taxonomy.EVIDENCE_HELD_IN_PEOPLE, ())
    # ...and the counter written apart from the product finds no value of
    # ANY column, under any subject column, that one to ten subjects hold.
    table = tmp_path / f"{kind}_long.csv"
    assert _real_misses(table, tmp_path) <= _CENSUS_ONLY
    counted = persons_counted.count_files(table, tmp_path)
    assert counted["subjects"] == ["patient"], counted
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
