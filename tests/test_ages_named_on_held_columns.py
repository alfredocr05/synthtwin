"""A held column is never rewritten as ages by its name (the orchestrator's LANE I4m RULINGS 21 (1)).

Codex's review of batch 4o, item 1: lane SH3's rule read a column whose name says
age as ages whatever share of its cells lay past 125, and reached `age_key`, record
numbers `00001` to `02000` its open question held; it top-coded the keys, read the
hold and its exclusions off the top-coded cells, and the twin wrote 19,600 real keys
at 20,000 rows, where 591b356f and 2af926ce wrote none. Now a column an open question
holds is read as its cells and its answers read it, and a column the count in people
holds is held from its cells as written; only an answer that it holds ages reads it so
(plan P4-D454). Each case is red on 015d5003 and on the mutant its comment names.
"""

from __future__ import annotations

import csv
import pathlib

import released_hold_cases as cases

from synthtwin import parsing, profile, reading, taxonomy


def test_record_numbers_named_as_an_age_unanswered_keep_their_hold(tmp_path: pathlib.Path) -> None:
    # Codex's case, its padded question unanswered, seed 1: 0 twin cells equal to a
    # real key and 0 merging with one (19,600 and 19,600 on 015d5003). Mutant: the
    # name read beside an open question (`name_read` always true).
    found = cases.run(tmp_path / "unanswered", cases.record_numbers_named_as_ages(), seed=1)
    assert found["exits"] == [0, 0], found["exits"]
    assert "identifier" in found["put"][0][0], found["put"]
    block = found["block"]
    assert block["role"] == "identifier" and "top_coded" not in block, block  # type: ignore[operator]
    assert block["n_distinct"] == 2000, block["n_distinct"]  # type: ignore[index]
    assert cases.equal_cells(found["real"], found["twin"]) == 0  # type: ignore[arg-type]
    assert cases.merged_cells(found["real"], found["twin"]) == 0  # type: ignore[arg-type]


def test_record_numbers_named_as_an_age_answered_identifier_keep_their_hold(tmp_path: pathlib.Path) -> None:
    found = cases.run(tmp_path / "identifier", cases.record_numbers_named_as_ages(), ("identifier",), seed=1)
    assert found["exits"] == [0, 0, 0], found["exits"]
    assert "top_coded" not in found["block"]  # type: ignore[operator]
    assert cases.equal_cells(found["real"], found["twin"]) == 0  # type: ignore[arg-type]
    assert cases.merged_cells(found["real"], found["twin"]) == 0  # type: ignore[arg-type]


def test_record_numbers_named_as_an_age_answered_as_ages_are_read_as_ages(tmp_path: pathlib.Path) -> None:
    # Answered a measurement, and then yes to the question its name now puts, the
    # column is read as ages: top-coded at 90, no twin cell past it. Its twin cells
    # equal to a real value are then ages the person said they are (measured, named
    # in the round's report).
    found = cases.run(tmp_path / "ages", cases.record_numbers_named_as_ages(), ("measurement", "yes"), seed=1)
    assert found["exits"] == [0, 0, 0, 0], found["exits"]
    assert any("yes" in offered for offered in found["put"][1]), found["put"]
    assert found["block"]["top_coded"] == 90, found["block"]  # type: ignore[index]
    numbers = [float(cell) for cell in found["twin"] if cell.strip()]  # type: ignore[union-attr]
    assert numbers and max(numbers) <= 90


def test_record_numbers_named_as_an_age_beside_people_keep_their_hold(tmp_path: pathlib.Path) -> None:
    # Beside a declared person column no question is put: the count in people holds
    # the column, and it is held from its cells as written, not from the `1` to `90`
    # the name's top-code wrote. Mutant: the hold read off the top-coded cells (the
    # step back to the cells as written removed).
    found = cases.run(tmp_path / "people", cases.record_numbers_named_as_ages_beside_people(), seed=1)
    assert found["exits"] == [0, 0], found["exits"]
    block = found["block"]
    assert block["role"] == "identifier" and "top_coded" not in block, block  # type: ignore[operator]
    assert cases.equal_cells(found["real"], found["twin"]) == 0  # type: ignore[arg-type]
    assert cases.merged_cells(found["real"], found["twin"]) == 0  # type: ignore[arg-type]


def test_a_held_column_its_cells_top_code_keeps_its_made_up_keys_off_the_real_ones(tmp_path: pathlib.Path) -> None:
    # The sibling sweep's case (LANE I4m RULINGS 21 (6)): `001` to `125` under
    # `age_key`, its question unanswered, is held, and its cells reach the ages, so
    # lane SH's top-code reaches it. The generator's fold of a held column named as
    # ages wrote the walk's made-up keys as their remainders by the mark: all 20,000
    # twin cells on 54 real keys (015d5003 and aab23a54). The top-code alone writes
    # them at or below 90, as 2af926ce did: no real key but the top-code's own `90`
    # (the stated limit of a zero-filled column the age reach takes, lane HB2).
    # Mutant: the generator's fold read off the column's name again.
    found = cases.run(tmp_path / "reach", cases.record_numbers_within_the_age_reach())
    assert found["exits"] == [0, 0], found["exits"]
    assert "identifier" in found["put"][0][0], found["put"]
    block = found["block"]
    assert block["role"] == "identifier" and block["top_coded"] == 90, block  # type: ignore[index]
    keys = {parsing.merged_key(cell) for cell in found["real"]}  # type: ignore[union-attr]
    met = {parsing.merged_key(cell) for cell in found["twin"] if cell.strip() and parsing.merged_key(cell) in keys}  # type: ignore[union-attr]
    assert met <= {"90"}, sorted(met)[:12]
    assert cases.equal_cells(found["real"], found["twin"]) == 0  # type: ignore[arg-type]


def _block(path: pathlib.Path, header: "list[str]", rows: "list[list[str]]", **more: object) -> "dict[str, object]":
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)
    document = profile.build_document(
        reading.read_table(f"{path}"), taxonomy.Settings(), [], top_code=True, **more  # type: ignore[arg-type]
    )
    return [one for one in document["columns"] if one["name"] == header[0]][0]  # type: ignore[union-attr, index, no-any-return]


def test_the_name_reads_ages_only_where_no_question_holds_the_column(tmp_path: pathlib.Path) -> None:
    # The library at a test size (LANE I4m RULINGS 18 (4)): numbers `1` to `200`
    # under `age_key`, most past 125, are read as ages by the name where no question
    # is open (lane SH3's rule, kept), and as they are written while one is open.
    rows = [[f"{number}"] for number in range(1, 201) for _row in range(10)]
    assert _block(tmp_path / "open.csv", [cases.AGE_KEY], rows)["top_coded"] == 90
    held = _block(tmp_path / "held.csv", [cases.AGE_KEY], rows, unanswered=[cases.AGE_KEY])
    assert "top_coded" not in held and held["n_distinct"] == 200, held
