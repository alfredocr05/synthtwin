"""Which hole spelling is one column's judgement, and which is a declaration.

THE DEFECT THIS GATE EXISTS FOR, reproduced before anything was
touched. A key of `missing_by_source` is either the judging column's own
business -- a stand-in number or a calendar placeholder that column's
distribution made absent -- or something that reaches the whole table: a
word the person declared, or one of this package's own. The generator
and the validator both need the difference, and both worked it out by
COUNTING the cells of every key DENOTING the judged candidate against
the verdict's `n_occurrences`.

No count can answer it. Two keys can write ONE candidate day. A 500-row
table whose `end` column held twenty `1900-01-01 00:00:00` a placeholder
pass judged, beside thirty `1900-01-01T00:00:00` the person declared,
put 50 cells against a verdict of 20 -- so the judged spelling was read
as a declaration of the whole table, the `start` column's eighty
legitimate values of that spelling were re-read as absent, and
**validating the REAL table against its own description exited 3 with
thirteen obligations missed**: both presence counts, three counts of
cells, the marks census, the count at midnight and seven rungs of its
date ladder.

The repair publishes the fact instead of inferring it: each decision
names the published spellings its own pass took out (contract 5.5,
invariant V5), gathered where the producer removes the cell. The two
reproductions below are the reviewer's own, and the third is the
opposite failure -- landing 2b.3's -- which the same rule must keep
closed, because a rule that fixed one by breaking the other is what this
file is here to stop.

Every table is built by seeded neutral code at runtime (plan D13).
"""

import datetime
import json
import pathlib
import sys

import pytest

from synthtwin import contract, errors

from tests import fixtures

SPACED = "1900-01-01 00:00:00"
TEED = "1900-01-01T00:00:00"


def _exit_of(argv: "list[str]") -> int:
    """Run one synthtwin command in this process and return its exit code."""
    from synthtwin import cli

    before = sys.argv
    sys.argv = ["synthtwin"] + argv
    try:
        code = cli.main()
    except SystemExit as stop:
        return 0 if stop.code is None else int(stop.code)
    finally:
        sys.argv = before
    return code


def _days(first: "datetime.date", count: int, step: int = 1) -> "list[str]":
    return [
        f"{(first + datetime.timedelta(days=step * place)).isoformat()} 00:00:00"
        for place in range(count)
    ]


def _run(
    folder: pathlib.Path,
    names: "list[str]",
    rows: "list[list[str]]",
    flags: "list[str]",
    seed: str = "4",
) -> "tuple[dict, int, int, list[str]]":
    """Describe, build, and check the twin AND the real table.

    Returns the description, the twin's exit code, the real table's exit
    code, and the twin's own cells of the first column.
    """
    folder.mkdir(parents=True, exist_ok=True)
    table = folder / "table.csv"
    table.write_text(
        fixtures.rows_to_csv(names, rows), encoding="utf-8", newline=""
    )
    assert (
        _exit_of(
            ["profile", str(table), "--out-dir", str(folder), "--replace"]
            + flags
        )
        == 0
    )
    described = folder / "table-profile.json"
    assert (
        _exit_of(
            [
                "generate",
                str(described),
                "--out-dir",
                str(folder),
                "--seed",
                seed,
                "--replace",
            ]
        )
        == 0
    )
    twin = folder / "table-twin.csv"
    checked = folder / "check-twin"
    checked.mkdir()
    twin_exit = _exit_of(
        [
            "validate",
            str(described),
            "--twin",
            str(twin),
            "--out-dir",
            str(checked),
            "--replace",
        ]
    )
    real = folder / "check-real"
    real.mkdir()
    real_exit = _exit_of(
        [
            "validate",
            str(described),
            "--twin",
            str(table),
            "--out-dir",
            str(real),
            "--replace",
        ]
    )
    document = json.loads(described.read_text(encoding="utf-8"))
    written = twin.read_text(encoding="utf-8").splitlines()
    return document, twin_exit, real_exit, written


def _block(document: dict, name: str) -> dict:
    for block in document["columns"]:
        if block["name"] == name:
            return block
    raise AssertionError(f"no column named {name}")


def _missed(folder: pathlib.Path) -> "list[str]":
    """Every obligation the check under this folder reported MISSED."""
    found: "list[str]" = []
    for path in sorted(folder.glob("*quality.txt")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if "MISSED" in line and "[" in line:
                found += [line.strip()]
    return found


# -- the reviewer's two reproductions ----------------------------------


@pytest.mark.parametrize("seed", ["4", "11"])
def test_a_declared_word_sharing_a_judged_day_leaves_the_real_table_whole(
    tmp_path: pathlib.Path, seed: str
) -> None:
    """The reproduction, as it was written: 500 rows, two columns, one day.

    `end` holds twenty cells spelled `1900-01-01 00:00:00`, which its own
    placeholder pass judges, beside thirty spelled `1900-01-01T00:00:00`,
    which the person declared. `start` holds eighty legitimate values of
    the FIRST spelling -- ordinary dates a hundred days apart begin in
    1890, so nothing about that column is unusual.

    Before the repair the judged spelling was read as a declaration of
    the whole table and `start`'s eighty values were re-described as
    absent: the REAL table exited 3 with thirteen obligations missed.
    """
    end = [SPACED] * 20 + [TEED] * 30 + _days(datetime.date(2020, 1, 1), 450)
    start = [SPACED] * 80 + _days(datetime.date(1890, 1, 1), 420, step=100)
    rows = [[end[place], start[place]] for place in range(500)]
    folder = tmp_path / f"plain-{seed}"
    document, twin_exit, real_exit, _written = _run(
        folder, ["end", "start"], rows, ["--missing-value", TEED], seed
    )
    assert real_exit == 0, _missed(folder / "check-real")
    assert twin_exit == 0, _missed(folder / "check-twin")
    # The description says which of the two keys the pass took, and it
    # is the fact the whole repair rests on.
    ended = _block(document, "end")
    assert ended["missing_by_source"] == {SPACED: 20, TEED: 30}
    judged = [
        entry
        for entry in ended["sentinel_verdicts"]
        if entry["verdict"] == "read_as_missing"
    ]
    assert len(judged) == 1, ended["sentinel_verdicts"]
    assert judged[0]["spellings"] == [SPACED], judged[0]
    # ...and `start` is an ordinary column of 500 values, which is what
    # the promotion destroyed.
    assert _block(document, "start")["n_present"] == 500
    assert _block(document, "start")["n_missing"] == 0


def test_the_same_when_the_declared_word_is_pooled_beside_a_built_in_one(
    tmp_path: pathlib.Path,
) -> None:
    """The reviewer's second reproduction: a pooled hole in the way.

    The thirty declared cells are spelled `NA`, one ordinary date is
    replaced by `NULL`, and the floor is eleven -- so `NULL` is pooled
    into `n_missing_withheld` and the count rule saw a hole it could not
    attribute. The pooled remainder was added to the keys denoting the
    candidate, which is what made 21 cells stand against a verdict of
    20 and promoted the judged spelling a second way.

    **WHAT THE POOL HOLDS CHANGED, AND WHAT THIS TEST CLAIMS DID NOT**
    (plan P4-D293, the merge-close of 2026-09-18). A pool of ONE is a
    pool that names a row -- here by subtraction, 51 absent cells less
    the 50 the spellings census covers -- so the pool is now raised by
    the smallest NAMED spelling until it names none. This column's
    smallest named spelling is the judged one, worn by 20 cells, so the
    pool holds 21 and `missing_by_source` publishes `{"NA": 30}` alone.
    **That is a measured cost of P4-D293 and it is stated in that entry:
    a spelling that clears the floor on its own can be taken into the
    pool to hide a lone stray beside it, and the sentinel verdict then
    publishes no spelling for its candidate.** What this test exists for
    is unmoved and is asserted below: the verdict still reads
    `read_as_missing` over the right candidate at its own 20 occurrences,
    the pooled remainder is NOT added to the keys denoting it, the
    judging column's neighbour still holds all 500 of its values, and
    both files validate at nought.
    """
    end = (
        [SPACED] * 20
        + ["NA"] * 30
        + ["NULL"]
        + _days(datetime.date(2020, 1, 1), 449)
    )
    start = [SPACED] * 80 + _days(datetime.date(1890, 1, 1), 420, step=100)
    rows = [[end[place], start[place]] for place in range(500)]
    folder = tmp_path / "pooled"
    document, twin_exit, real_exit, _written = _run(
        folder,
        ["end", "start"],
        rows,
        ["--missing-value", "NA", "--smallest-group", "11"],
    )
    assert real_exit == 0, _missed(folder / "check-real")
    assert twin_exit == 0, _missed(folder / "check-twin")
    ended = _block(document, "end")
    # The lone `NULL` is pooled, and P4-D293 then raises the pool by the
    # smallest named spelling -- the judged one, 20 cells -- so 21 stand
    # here where 1 stood before that entry.
    assert ended["n_missing_withheld"] == 21, "the pooled hole must be there"
    assert ended["missing_by_source"] == {"NA": 30}, ended["missing_by_source"]
    assert ended["n_missing"] == 51, ended["n_missing"]
    judged = [
        entry
        for entry in ended["sentinel_verdicts"]
        if entry["verdict"] == "read_as_missing"
    ]
    # THE CLAIM THIS TEST WAS WRITTEN FOR. The pooled remainder is not
    # added to the cells denoting the candidate: 21 are pooled and the
    # verdict still counts its own 20.
    assert len(judged) == 1, ended["sentinel_verdicts"]
    assert judged[0]["n_occurrences"] == 20, judged[0]
    # A spelling inside the pool is not named, which is the cost above.
    assert judged[0]["spellings"] == [], judged[0]
    assert _block(document, "start")["n_present"] == 500


# -- and the opposite failure, which the same rule must keep closed ----


def test_a_judged_spelling_still_stays_the_judging_columns_own(
    tmp_path: pathlib.Path,
) -> None:
    """Landing 2b.3's defect, which a count rule fixed and could lose again.

    `discharge` judges its fifty `1900-01-01 00:00:00` cells: they stand
    decades away from its other dates. `birth` holds one hundred and
    eighty-seven cells of the SAME spelling among dates of the 1900s,
    where the spelling is an ordinary value and no pass touches it.

    A judgement made on one column's distribution must not reach the
    other. If it did, `birth`'s 187 values would be described as absent
    and the real table would miss its own obligations.
    """
    discharge = [SPACED] * 50 + _days(datetime.date(2024, 1, 1), 450)
    birth = [SPACED] * 187 + _days(datetime.date(1900, 1, 2), 313, step=7)
    rows = [[discharge[place], birth[place]] for place in range(500)]
    folder = tmp_path / "judged-alone"
    document, twin_exit, real_exit, _written = _run(
        folder, ["discharge", "birth"], rows, []
    )
    assert real_exit == 0, _missed(folder / "check-real")
    assert twin_exit == 0, _missed(folder / "check-twin")
    assert _block(document, "birth")["n_present"] == 500
    assert _block(document, "birth")["n_missing"] == 0
    judged = [
        entry
        for entry in _block(document, "discharge")["sentinel_verdicts"]
        if entry["verdict"] == "read_as_missing"
    ]
    assert judged and judged[0]["spellings"] == [SPACED]


def test_a_declared_word_still_reaches_every_column(
    tmp_path: pathlib.Path,
) -> None:
    """The other direction: a declaration is never narrowed to one column.

    The person declares `1900-01-01 00:00:00`. Both columns hold cells
    of it, and both must publish it among their absent cells: a
    declaration is made once and means "no value" wherever it appears.
    """
    first = [SPACED] * 40 + _days(datetime.date(2024, 1, 1), 460)
    second = [SPACED] * 25 + _days(datetime.date(2019, 1, 1), 475, step=3)
    rows = [[first[place], second[place]] for place in range(500)]
    folder = tmp_path / "declared"
    document, twin_exit, real_exit, _written = _run(
        folder, ["first", "second"], rows, ["--missing-value", SPACED]
    )
    assert real_exit == 0, _missed(folder / "check-real")
    assert twin_exit == 0, _missed(folder / "check-twin")
    for name, count in (("first", 40), ("second", 25)):
        block = _block(document, name)
        assert block["missing_by_source"] == {SPACED: count}
        assert block["missing_by_class"]["(declared-missing)"] == count
        # No pass judged it, so no decision names it -- which is
        # exactly how both readers now know it is a declaration.
        for entry in block["sentinel_verdicts"]:
            assert entry["spellings"] == [], entry


# -- the published fact itself -----------------------------------------


def test_a_kept_candidate_names_no_spelling(tmp_path: pathlib.Path) -> None:
    """A decision that kept its candidate took no cell out of the column."""
    values = [str(number) for number in range(-5000, 5000, 50)] + ["-999"] * 15
    folder = tmp_path / "kept"
    folder.mkdir()
    table = folder / "table.csv"
    table.write_text(
        fixtures.rows_to_csv(["reading"], [[value] for value in values]),
        encoding="utf-8",
        newline="",
    )
    assert (
        _exit_of(["profile", str(table), "--out-dir", str(folder), "--replace"])
        == 0
    )
    document = json.loads(
        (folder / "table-profile.json").read_text(encoding="utf-8")
    )
    entries = document["columns"][0]["sentinel_verdicts"]
    assert entries, "the column must publish a decision at all"
    for entry in entries:
        assert entry["verdict"] == "kept_as_a_number"
        assert entry["spellings"] == []


def test_the_loader_refuses_a_decision_naming_a_spelling_that_was_never_published(
    tmp_path: pathlib.Path,
) -> None:
    """Invariant V5, on a real description with one key moved.

    A decision naming a spelling the column does not publish among its
    absent cells is a document that says a word the person declared was
    one column's own judgement -- the mistake the key exists to end --
    so the loader refuses it by name rather than reading it.
    """
    values = [str(number) for number in range(1, 200)] + ["-999"] * 15
    folder = tmp_path / "refused"
    folder.mkdir()
    table = folder / "table.csv"
    table.write_text(
        fixtures.rows_to_csv(["reading"], [[value] for value in values]),
        encoding="utf-8",
        newline="",
    )
    assert (
        _exit_of(["profile", str(table), "--out-dir", str(folder), "--replace"])
        == 0
    )
    written = folder / "table-profile.json"
    document = json.loads(written.read_text(encoding="utf-8"))
    block = document["columns"][0]
    assert block["sentinel_verdicts"][0]["spellings"] == ["-999"]
    block["sentinel_verdicts"][0]["spellings"] = ["zz"]
    edited = folder / "edited.json"
    edited.write_text(
        fixtures.canonical_text(document)
        if hasattr(fixtures, "canonical_text")
        else json.dumps(document, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    with pytest.raises(errors.ProfileError) as caught:
        contract.load_profile(str(edited))
    said = f"{caught.value}"
    assert "V5" in said, said
    # ...and the refusal names no spelling of the person's table.
    assert "zz" not in said, said


# -- landing 2b.14: the claim is CHECKED on the way back in ------------


@pytest.mark.parametrize("floor", ["11", "1"])
def test_a_judged_pass_whose_other_spelling_the_floor_pooled(
    tmp_path: pathlib.Path, floor: str
) -> None:
    """One pass, two spellings of its day, and only one clears the floor.

    This is the shape that decides whether V5's new count bound is `at
    most` or `exactly`, so it is measured rather than assumed. `end`
    holds twenty cells spelled `1900-01-01 00:00:00` beside five spelled
    `1900-01-01T00:00:00`; NOTHING is declared, so its placeholder pass
    judges all twenty-five. At a floor of eleven the description may
    name only the first, and publishes one spelling worth twenty cells
    against an `n_occurrences` of twenty-five, pooling the other five;
    at a floor of one it names both and the two come to exactly
    twenty-five.

    A bound demanding equality would refuse the first of those, which is
    a description a producer writes. Both must load, both must round
    trip, and `start`'s eighty legitimate values of the judged spelling
    must survive either way.
    """
    end = [SPACED] * 20 + [TEED] * 5 + _days(datetime.date(2020, 1, 1), 475)
    start = [SPACED] * 80 + _days(datetime.date(1890, 1, 1), 420, step=100)
    rows = [[end[place], start[place]] for place in range(500)]
    folder = tmp_path / f"pooled-judged-{floor}"
    document, twin_exit, real_exit, _written = _run(
        folder, ["end", "start"], rows, ["--smallest-group", floor]
    )
    assert real_exit == 0, _missed(folder / "check-real")
    assert twin_exit == 0, _missed(folder / "check-twin")
    ended = _block(document, "end")
    judged = [
        entry
        for entry in ended["sentinel_verdicts"]
        if entry["verdict"] == "read_as_missing"
    ]
    assert len(judged) == 1, ended["sentinel_verdicts"]
    # The pass took all twenty-five cells either way...
    assert judged[0]["n_occurrences"] == 25, judged[0]
    if floor == "11":
        # ...but at eleven only one spelling may be named, so the cells
        # its `spellings` cover fall SHORT of `n_occurrences`.
        assert ended["missing_by_source"] == {SPACED: 20}
        assert ended["n_missing_withheld"] == 5
        assert judged[0]["spellings"] == [SPACED], judged[0]
    else:
        assert ended["missing_by_source"] == {SPACED: 20, TEED: 5}
        assert ended["n_missing_withheld"] == 0
        assert judged[0]["spellings"] == [SPACED, TEED], judged[0]
    assert _block(document, "start")["n_present"] == 500
    assert _block(document, "start")["n_missing"] == 0


def _plain_description(folder: pathlib.Path) -> "tuple[pathlib.Path, dict]":
    """The reviewer's plain reproduction, described and left on disk."""
    end = [SPACED] * 20 + [TEED] * 30 + _days(datetime.date(2020, 1, 1), 450)
    start = [SPACED] * 80 + _days(datetime.date(1890, 1, 1), 420, step=100)
    folder.mkdir(parents=True, exist_ok=True)
    table = folder / "table.csv"
    table.write_text(
        fixtures.rows_to_csv(
            ["end", "start"],
            [[end[place], start[place]] for place in range(500)],
        ),
        encoding="utf-8",
        newline="",
    )
    assert (
        _exit_of(
            [
                "profile",
                str(table),
                "--out-dir",
                str(folder),
                "--replace",
                "--missing-value",
                TEED,
            ]
        )
        == 0
    )
    written = folder / "table-profile.json"
    return written, json.loads(written.read_text(encoding="utf-8"))


def _refused(folder: pathlib.Path, document: dict, tag: str) -> str:
    """Write a hand-edited description, load it, return the refusal."""
    edited = folder / f"{tag}.json"
    edited.write_text(
        json.dumps(document, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    with pytest.raises(errors.ProfileError) as caught:
        contract.load_profile(str(edited))
    return f"{caught.value}"


def test_the_loader_refuses_a_decision_claiming_a_declared_word(
    tmp_path: pathlib.Path,
) -> None:
    """V5's count bound, on the exact document the old loader accepted.

    `end` publishes two hole spellings of one placeholder day: twenty
    cells its own pass judged, and thirty the person declared. The
    description is edited to say the decision took BOTH -- which is the
    claim no count in the block could ever contradict, and which the
    loader carried through to both consumers before landing 2b.14.

    It is refused on the block's own arithmetic: fifty absent cells
    against a verdict of twenty. The narrower forgery, naming only the
    declared spelling, is refused the same way at thirty against twenty.
    """
    folder = tmp_path / "forged"
    _written, document = _plain_description(folder)
    ended = _block(document, "end")
    judged = [
        entry
        for entry in ended["sentinel_verdicts"]
        if entry["verdict"] == "read_as_missing"
    ]
    assert judged[0]["spellings"] == [SPACED], "the base must be the honest one"
    assert judged[0]["n_occurrences"] == 20, judged[0]

    both = json.loads(json.dumps(document))
    for entry in _block(both, "end")["sentinel_verdicts"]:
        if entry["verdict"] == "read_as_missing":
            entry["spellings"] = sorted([SPACED, TEED])
    said = _refused(folder, both, "both")
    assert "V5" in said, said
    assert "50" in said and "20" in said, said

    only = json.loads(json.dumps(document))
    for entry in _block(only, "end")["sentinel_verdicts"]:
        if entry["verdict"] == "read_as_missing":
            entry["spellings"] = [TEED]
    narrow = _refused(folder, only, "only")
    assert "V5" in narrow, narrow
    # ...and neither refusal prints a spelling of anybody's table
    # (contract C5-N5, R15): what is wrong is counted, never quoted.
    for message in (said, narrow):
        assert SPACED not in message, message
        assert TEED not in message, message


def test_the_loader_refuses_two_decisions_claiming_one_spelling(
    tmp_path: pathlib.Path,
) -> None:
    """A cell is taken out once, so two passes cannot both have taken it."""
    folder = tmp_path / "twice"
    _written, document = _plain_description(folder)
    ended = _block(document, "end")
    first = [
        entry
        for entry in ended["sentinel_verdicts"]
        if entry["verdict"] == "read_as_missing"
    ][0]
    second = json.loads(json.dumps(first))
    # A second candidate day, ordered after the first (V4), naming the
    # spelling the first decision already claimed.
    second["candidate"] = "9999-12-31"
    ended["sentinel_verdicts"] = [first, second]
    said = _refused(folder, document, "twice")
    assert "V5" in said, said
    assert SPACED not in said, said
