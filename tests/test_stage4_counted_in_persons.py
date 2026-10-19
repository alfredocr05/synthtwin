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
    # A declared person column publishes the census its counts imply.
    if kind.endswith("_beside"):
        census = _block(_described(tmp_path, f"{kind}_long"), "patient")[
            "n_distinct_by_occurrences"
        ]
        assert isinstance(census, dict) and len(census) <= 2, census


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
    monkeypatch.setattr(taxonomy, "with_even_census", refused)
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
    held = profile.subjects_holding(["x"] * 14, ["s1"] * 14, lambda cell: (cell,), 11)
    assert held["x"].rows == 14
    assert held["x"].holders == ("s1",)


def test_the_cap_keeps_at_most_the_floor_and_never_a_subject_twice() -> None:
    values = ["x"] * 40
    subjects = [f"s{place % 20}" for place in range(40)]
    held = profile.subjects_holding(values, subjects, lambda cell: (cell,), 11)
    assert held["x"].rows == 40
    assert len(held["x"].holders) == 11
    assert len(set(held["x"].holders)) == 11
    twice = profile.subjects_holding(["y"] * 6, ["a", "a", "b", "b", "a", "c"],
                                     lambda cell: (cell,), 11)
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
        cli.main(["validate", f"{folder / (stem + '-profile.json')}", "--twin",
                  f"{table}", "--out-dir", f"{checked}", "--replace"])
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
