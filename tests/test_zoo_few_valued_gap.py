"""P4-D440 (lane GG): few-valued numbers with a gap written as their own values.

THE DEFECT, measured on batch 4k's merged head 589f3d72 at the owner's
table floor of 20,000 rows (planning-notes wave6/GG/base-*-20k.log). A
continuous or count column of a few values with a wide gap among them --
a 1-to-5 score beside `-99`, a pain score 0 to 10 beside `-99`, decimal
scores 1.0 to 5.0 beside `-99`, a 1-to-7 scale, a days' supply of 7, 14,
30 and 90 days -- was drawn by G5's strata from the ladder, and its twin
lost a whole level (the zoo's `surveys_pro.q2_score` wrote no `3`), wrote
cells inside the stretch the description publishes as empty (`-91` x25
beside a published gap `[-99, 1]`; `-51` x149 in the pain score), spread
the rest evenly (4,594 cells on each level), wrote numbers the column
never holds (`8` and `13` in the days' supply) and missed its published
mode pair (`quantity`: 8,607 published at `30`, 103 written there).

THE RULE (plan P4-D440, contract VL1 to VL5, method G6.9). Such a column
publishes `few_values`, every number it writes in its own spelling and no
count, and the twin writes exactly those spellings, each at a count
solved from what the block already publishes: the sign counts, the mode
pair, the tails, the hundred and one rungs and the floored histogram,
then the style and width censuses and the mean.

THE GATE, each fault a case red on its own mutant: a level dropped; a
value in a published gap; even spreading; `-99` re-spelled `-99.0`; a
published `mode_count` missed; a column with no wide gap keeps its bytes;
and lane HX's case -- the warehouse export's `patient_key`, 60 keys, its
question unanswered, prints none of its keys at 20,000 rows. The
mutants run through the library below the table floor, which only the
internal switches reach; the floor-size proofs are one case per writer,
and the lane's sweep at 20,000 rows is K-HZ-12's, under
`kpi_run.py --slow`. The shapes and the counter are
`tests/few_valued_shapes.py`'s, which the driver shares. GG acts only
after `no` to a column's Safe Harbor question (the stand-ins page's
ZS.4): unanswered, a column of the class is described and written as
before, byte for byte, and `yes` holds it.
"""

from __future__ import annotations

import csv
import dataclasses
import io
import json
import pathlib
import random
import sys

import pytest

from synthtwin import asking, cli, contract, errors, generation, parsing, profile, reading, rendering, taxonomy, validation

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import few_valued_shapes as shapes  # noqa: E402
import fixtures  # noqa: E402
import health_zoo  # noqa: E402

SETTINGS = taxonomy.Settings()
SEED = 0
SHAPES = shapes.SHAPES
GAPPED = shapes.GAPPED
GAPLESS = shapes.GAPLESS
CLEAN = {"levels_lost": 0, "cells_in_gap": 0, "cells_off_list": 0, "mode_missed": 0, "rungs_off": 0}


def _described(
    folder: pathlib.Path,
    header: "list[str]",
    body: "list[list[str]]",
    released: "tuple[str, ...]" = tuple(SHAPES),
) -> "tuple[contract.Profile, dict[str, object]]":
    """The library's description, each column in ``released`` answered `no` to its Safe Harbor question."""
    path = fixtures.write(folder, "t.csv", fixtures.rows_to_csv(header, body))
    document = profile.build_document(
        reading.read_table(str(path)), SETTINGS, [], safe_harbor_no=list(released)
    )
    written = fixtures.write_profile(folder, "t-profile.json", document)
    return contract.load_profile(str(written)), json.loads(written.read_text(encoding="utf-8"))


def _twin_cells(described: contract.Profile) -> "dict[str, list[str]]":
    text = rendering.twin_csv(generation.generate(described, SEED))
    rows = list(csv.reader(io.StringIO(text)))
    return {rows[0][place]: [row[place] for row in rows[1:]] for place in range(len(rows[0]))}


def _blocks(document: "dict[str, object]") -> "dict[str, dict[str, object]]":
    return {f"{block['name']}": block for block in document["columns"]}  # type: ignore[union-attr, index]


def _measured(
    described: "tuple[contract.Profile, dict[str, object]]",
    header: "list[str]",
    body: "list[list[str]]",
    names: "tuple[str, ...]" = tuple(SHAPES),
) -> "dict[str, dict[str, int]]":
    twin = _twin_cells(described[0])
    blocks = _blocks(described[1])
    found: "dict[str, dict[str, int]]" = {}
    for name in names:
        place = header.index(name)
        found[name] = shapes.faults(
            blocks[name], [row[place] for row in body], twin[name], taxonomy._quantile
        )
    return found


def _column(described: contract.Profile, name: str) -> contract.ColumnBlock:
    for column in described.columns:
        if column.name == name:
            return column
    raise AssertionError(name)


@pytest.fixture(scope="module")
def small(tmp_path_factory: pytest.TempPathFactory) -> "tuple[tuple[contract.Profile, dict[str, object]], list[str], list[list[str]]]":
    folder = tmp_path_factory.mktemp("gg-small")
    header, body = shapes.table(SHAPES, 600)
    return _described(folder, header, body), header, body


def test_a_gapped_column_lists_its_values_and_a_gapless_one_does_not(small) -> None:
    (described, _document), _header, _body = small
    for name in GAPPED:
        facts = _column(described, name).facts
        assert isinstance(facts, contract.NumericFacts) and facts.few_values, name
    assert _column(described, "score5").facts.few_values == ("-99", "1", "2", "3", "4", "5")  # type: ignore[union-attr]
    assert _column(described, "dec_score").facts.few_values[0] == "-99"  # type: ignore[union-attr]
    for name in GAPLESS:
        facts = _column(described, name).facts
        assert isinstance(facts, contract.NumericFacts) and not facts.few_values, name


def test_the_twin_writes_every_listed_value_and_nothing_else(small) -> None:
    described, header, body = small
    found = _measured(described, header, body)
    for name in GAPPED:
        assert found[name] == CLEAN, (name, found[name])


def _no_list(_cells: object, _details: object) -> "list[str]":
    return []


_OWN_CENSUS = generation._listed_census


def _level_dropped(column: contract.ColumnBlock, facts: contract.NumericFacts) -> "tuple[list[str], list[object]]":
    cells, notes = _OWN_CENSUS(column, facts)
    middle = facts.few_values[len(facts.few_values) // 2]
    neighbour = facts.few_values[len(facts.few_values) // 2 + 1]
    return [neighbour if cell == middle else cell for cell in cells], list(notes)


def _spread_evenly(column: contract.ColumnBlock, facts: contract.NumericFacts) -> "tuple[list[str], list[object]]":
    cells, notes = _OWN_CENSUS(column, facts)
    share = len(cells) // len(facts.few_values)
    spread: "list[str]" = []
    for place, text in enumerate(facts.few_values):
        spread += [text] * (share if place < len(facts.few_values) - 1 else len(cells) - share * place)
    return spread, list(notes)


def _respelled(column: contract.ColumnBlock, facts: contract.NumericFacts) -> "tuple[list[str], list[object]]":
    cells, notes = _OWN_CENSUS(column, facts)
    return [f"{cell}.0" if cell == "-99" else cell for cell in cells], list(notes)


def _mode_forgotten(column: contract.ColumnBlock, facts: contract.NumericFacts) -> "tuple[list[str], list[object]]":
    cells, notes = _OWN_CENSUS(column, dataclasses.replace(facts, mode=None, mode_count=0))
    return cells, list(notes)


@pytest.mark.parametrize(
    "mutant, fault, names",
    [
        ("level_dropped", "levels_lost", GAPPED),
        ("no_list", "cells_in_gap", ("score5", "pain")),
        ("spread_evenly", "rungs_off", GAPPED),
        ("respelled", "cells_off_list", ("score5", "pain", "dec_score", "scale7")),
        ("mode_forgotten", "mode_missed", ("score5", "pain", "dec_score", "scale7")),
    ],
)
def test_each_fault_is_red_on_its_mutant(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
    mutant: str,
    fault: str,
    names: "tuple[str, ...]",
) -> None:
    if mutant == "no_list":
        monkeypatch.setattr(taxonomy, "_few_values_of", _no_list)
    else:
        monkeypatch.setattr(generation, "_listed_census", {
            "level_dropped": _level_dropped,
            "spread_evenly": _spread_evenly,
            "respelled": _respelled,
            "mode_forgotten": _mode_forgotten,
        }[mutant])
    header, body = shapes.table(SHAPES, 600)
    found = _measured(_described(tmp_path, header, body), header, body)
    red = [name for name in names if found[name][fault] > 0]
    assert red, (mutant, {name: found[name] for name in names})


def test_a_column_without_a_wide_gap_keeps_its_bytes(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, small
) -> None:
    """The plan's Must-NOT: a column with no wide gap is written as before.

    Its description carries no list, and its twin's cells -- written in
    the same table as five listed columns, whose census draws every word
    G4.3 budgets -- are the cells the strata write with the rule withdrawn
    for every column. The mutant reads any published empty stretch as a
    wide gap, so a scale whose bins are merely finer than its step lists
    its values, and the gapless twins move.
    """
    (described, _document), header, body = small
    held = _twin_cells(described)
    monkeypatch.setattr(taxonomy, "_few_values_of", _no_list)
    withdrawn = _twin_cells(_described(tmp_path, header, body)[0])
    for name in GAPLESS:
        assert held[name] == withdrawn[name], name
    monkeypatch.undo()
    monkeypatch.setattr(taxonomy, "_a_wide_gap", lambda *_given: True)
    mutant = tmp_path / "mutant"
    mutant.mkdir()
    moved = _twin_cells(_described(mutant, header, body)[0])
    assert any(moved[name] != held[name] for name in GAPLESS)


def test_unanswered_a_gapped_column_is_described_and_written_as_before(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The stand-ins page's ZS.4: GG acts only after `no` to the Safe Harbor question.

    Unanswered, a column of the class publishes no list and its twin is
    the one the strata write, cell for cell the twin with the rule
    withdrawn. The mutant releases a column nobody answered, and the
    unanswered twin moves.
    """
    header, body = shapes.table(SHAPES, 600)
    unanswered = _described(tmp_path, header, body, released=())[0]
    for name in GAPPED:
        assert not _column(unanswered, name).facts.few_values, name  # type: ignore[union-attr]
    as_before = _twin_cells(unanswered)
    monkeypatch.setattr(taxonomy, "_few_values_of", _no_list)
    withdrawn = tmp_path / "withdrawn"
    withdrawn.mkdir()
    assert _twin_cells(_described(withdrawn, header, body, released=())[0]) == as_before
    monkeypatch.undo()
    monkeypatch.setattr(profile, "_few_values_released", lambda _name, _answered: True)
    mutant = tmp_path / "mutant"
    mutant.mkdir()
    moved = _twin_cells(_described(mutant, header, body, released=())[0])
    assert any(moved[name] != as_before[name] for name in GAPPED)


def test_the_command_puts_the_question_and_yes_holds_the_column(tmp_path: pathlib.Path) -> None:
    """The Safe Harbor question is put to each gapped column; `yes` holds it, `no` lists it.

    Through the command, at 600 rows (the conftest's internal switch
    lifts the table floor): the questions file asks each gapped column
    no other question names -- the days' supply, in the ages' reach, is
    asked SH's own -- and a column answered `yes` is held as a record
    number, while one answered `no` publishes its list.
    """
    header, body = shapes.table(SHAPES, 600)
    table = fixtures.write(tmp_path, "t.csv", fixtures.rows_to_csv(header, body))
    assert shapes.quiet(cli.main, ["profile", f"{table}", "--replace"]) in (0, 3)
    questions = json.loads((tmp_path / "t-questions.json").read_text(encoding="utf-8"))
    entries: "list[dict[str, object]]" = []
    for key in ("about_your_file", "asked"):
        entries += [one for one in (questions.get(key) or []) if isinstance(one, dict)]
    put = {
        f"{one.get('column')}" for one in entries
        if "a wide stretch among them" in f"{one.get('what_synthtwin_saw')}"
    }
    assert set(GAPPED) - {"days_supply"} <= put, put
    shapes.answered(cli.main, tmp_path, table, {"score5": "yes"})
    described = contract.load_profile(str(tmp_path / "t-profile.json"))
    assert _column(described, "score5").role == "identifier"
    assert _column(described, "pain").facts.few_values  # type: ignore[union-attr]
    assert asking.BECAUSE_SAFE_HARBOR_FEW_VALUES in asking.SAFE_HARBOR_REASONS


def test_at_the_floor_the_zoo_surveys_and_the_lane_shapes_write_only_their_values(tmp_path: pathlib.Path) -> None:
    """One case per writer at 20,000 rows: the zoo's surveys and the lane's shapes, through the command.

    Every level written, none in a gap or off the list, the mode pair met,
    every rung where the description puts it, and each score's valid mean
    (`-99` aside) inside the real table's own half-split gap; the days'
    supply answered as the zoo answers it writes only real values. The
    command refuses nothing here: 20,000 rows is the floor.
    """
    zoo_header, zoo_body = health_zoo.surveys(20_000, 20261016)
    kept = [zoo_header.index(name) for name in ("respondent_id", "q2_score", "q3_score", "scale_total")]
    lane = {name: SHAPES[name] for name in GAPPED}
    more_header, more_body = shapes.table(lane, 20_000)
    header = [zoo_header[place] for place in kept] + more_header
    body = [[row[place] for place in kept] + right for row, right in zip(zoo_body, more_body)]
    table = fixtures.write(tmp_path, "t.csv", fixtures.rows_to_csv(header, body))
    assert shapes.quiet(cli.main, ["profile", f"{table}", "--replace"], small_tables_refused=True) in (0, 3)
    answers = {name: "measurement" for name in header}
    answers["respondent_id"] = "identifier"
    shapes.answered(cli.main, tmp_path, table, answers)
    written = tmp_path / "t-profile.json"
    described = (contract.load_profile(str(written)), json.loads(written.read_text(encoding="utf-8")))
    names = ("q2_score", "q3_score", "scale_total") + GAPPED
    found = _measured(described, header, body, names)
    for name in names:
        assert found[name] == CLEAN, (name, found[name])
    twin = _twin_cells(described[0])
    for name in ("q2_score", "q3_score"):
        place = header.index(name)
        real = [float(row[place]) for row in body if row[place] != "-99"]
        halves = (real[0::2], real[1::2])
        gap = abs(sum(halves[0]) / len(halves[0]) - sum(halves[1]) / len(halves[1]))
        made = [float(cell) for cell in twin[name] if cell != "-99"]
        assert abs(sum(made) / len(made) - sum(real) / len(real)) <= gap, name
    days = set(row[header.index("days_supply")] for row in body)
    assert set(twin["days_supply"]) == days


def test_a_patient_key_whose_question_is_open_prints_none_of_its_keys(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Lane HX's case, held by GG's gate (the zoo plan's 2.4, row 45).

    Sixty patient keys of six figures beside `-1`, read as numbers, are a
    few-valued column with a wide gap: unanswered, the hold of plan
    P4-D401 describes the column as a record number, so no key is listed,
    no rung, mode or tail prints one, and no twin cell is a real key. The
    mutant withdraws that hold -- no column is taken as unanswered -- and
    the value list, once the Safe Harbor question is answered `no`,
    prints every key.
    """
    for mutated in (False, True):
        # The held run at the table floor; its mutant through the internal
        # switch at 600 rows, ten rows a key, where the list would name all.
        header, body = shapes.keyed_export(600 if mutated else 20_000)
        keys = {float(row[1]) for row in body if row[1] != "-1"}
        folder = tmp_path / ("mutant" if mutated else "held")
        folder.mkdir()
        if mutated:
            monkeypatch.setattr(asking, "unanswered_identities", lambda *_given, **_named: ())
        table = fixtures.write(folder, "t.csv", fixtures.rows_to_csv(header, body))
        assert shapes.quiet(
            cli.main, ["profile", f"{table}", "--replace"], small_tables_refused=not mutated
        ) in (0, 3)
        shapes.answered(cli.main, folder, table, {"EncounterKey": "identifier"})
        assert shapes.quiet(cli.main, ["generate", f"{folder / 't-profile.json'}", "--replace", "--seed", "0"]) == 0
        twin = _twin_cells(contract.load_profile(str(folder / "t-profile.json")))["patient_key"]
        shown = shapes.keys_shown(folder, keys)
        equal = sum(1 for cell in twin if shapes.number(cell) in keys)
        if mutated:
            assert shown > 0 and equal > 0, (shown, equal)
        else:
            assert (shown, equal) == (0, 0)


# REPAIR 1 (skeptic 1's items 2 to 5, the statistics skeptic's items 1 and
# 2, the orchestrator's LANE GG RULINGS 1 and 2): each case below is red
# on its own mutant.


def _command_run(
    folder: pathlib.Path,
    header: "list[str]",
    body: "list[list[str]]",
    answers: "dict[str, str]",
    declared: "tuple[str, ...]" = (),
    refused: bool = True,
) -> "dict[str, list[str]]":
    """Profile through the command, answer every round from ``answers``, generate at seed 0: the twin's cells."""
    folder.mkdir(parents=True, exist_ok=True)
    table = fixtures.write(folder, "t.csv", fixtures.rows_to_csv(header, body))
    extra: "list[str]" = []
    for name in declared:
        extra += ["--identifier", name]
    assert shapes.quiet(cli.main, ["profile", f"{table}", "--replace"] + extra, small_tables_refused=refused) in (0, 3)
    _answered_keeping(folder, table, answers, extra)
    assert shapes.quiet(cli.main, ["generate", f"{folder / 't-profile.json'}", "--replace", "--seed", "0"]) == 0
    return _twin_cells(contract.load_profile(str(folder / "t-profile.json")))


def _answered_keeping(
    folder: pathlib.Path, table: pathlib.Path, answers: "dict[str, str]", extra: "list[str]"
) -> None:
    """Every round answered from ``answers`` alone -- a question no answer names is left open."""
    questions = folder / "t-questions.json"
    for _round in range(4):
        if not questions.is_file():
            return
        document = json.loads(questions.read_text(encoding="utf-8"))
        entries: "list[dict[str, object]]" = []
        for key in ("about_your_file", "asked"):
            entries += [one for one in (document.get(key) or []) if isinstance(one, dict) and "answers_you_can_give" in one]
        checklist = document.get("checklist") or {}
        entries += [one for one in (checklist.get("columns") or []) if isinstance(one, dict) and "answers_you_can_give" in one]
        changed = False
        for entry in entries:
            offered = [f"{choice.get('answer')}" for choice in entry["answers_you_can_give"]]  # type: ignore[union-attr]
            wanted = answers.get(f"{entry.get('column', '')}", "")
            given = ""
            for choice in wanted.split("/"):
                if choice and choice in offered:
                    given = choice
                    break
            if entry.get("your_answer", "") != given:
                changed = True
            entry["your_answer"] = given
        questions.write_text(json.dumps(document, indent=2), encoding="utf-8", newline="\n")
        code = shapes.quiet(cli.main, ["profile", f"{table}", "--replace", "--answers", f"{questions}"] + extra)
        assert code in (0, 3), code
        if not changed:
            return


def _harbor_put(folder: pathlib.Path, column: str) -> bool:
    """Whether GG's Safe Harbor question stands in the questions file for ``column``."""
    questions = json.loads((folder / "t-questions.json").read_text(encoding="utf-8"))
    for key in ("about_your_file", "asked"):
        for one in questions.get(key) or []:
            if (
                isinstance(one, dict)
                and one.get("column") == column
                and "a wide stretch among them" in f"{one.get('what_synthtwin_saw')}"
            ):
                return True
    return False


def test_three_figure_patient_keys_beside_minus_one_are_held_unanswered(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Skeptic 1's item 2 (HIPAA, live on the base): k60f3mp at 20,000 rows.

    Sixty patient keys of three figures in sequence beside a warehouse key's `-1`
    on 2 % of rows -- here beside a declared person column; k60f3m, the
    same keys without it, is a column of the next case's one table --
    printed all sixty and wrote 19,556 of 20,000 twin cells real on the
    base, because the `-1` defeated the fixed-width question's hold (lane
    HX4's addendum: one ordinary token must not defeat a hold). Set
    aside, the keys are asked that question as the same keys without the
    `-1` are, and held unanswered: no key in the column's facts, its
    questions or any line naming it; GG's Safe Harbor question never
    put, for P4-D401's question reaches the column first; and the twin's
    cells equal to a real key are chance's alone, the held column's
    made-up keys drawn from the 900 three-figure numbers, 60 of them real
    (about keys/900 of its cells, 1,304 of 20,000; none by construction
    once lane ID-ROOM, plan P4-D432, merges). The mutant withdraws the
    set-aside, at 600 rows through the internal switch, and the keys
    print.
    """
    header, body = shapes.keys_in_sequence(20_000, person=True)
    keys = {float(row[1]) for row in body if row[1] != "-1"}
    folder = tmp_path / "k60f3mp"
    twin = _command_run(
        folder, header, body, {"EncounterKey": "identifier"}, ("patient",)
    )["patient_key"]
    described = contract.load_profile(str(folder / "t-profile.json"))
    assert _column(described, "patient_key").role == "identifier"
    assert shapes.column_keys_shown(folder, keys, "patient_key") == 0
    assert not _harbor_put(folder, "patient_key")
    equal = sum(1 for cell in twin if shapes.number(cell) in keys)
    assert equal <= len(twin) // 10, equal
    monkeypatch.setattr(asking, "_beside_width_placeholders", lambda *_given: [])
    # ...and lane HB's key-name route, which holds a column named as a key on its
    # own since lane HB's merge (plan P4-D442, rule (14)): withdrawn too, so the
    # mutant shows the set-aside is what holds these keys by their values.
    monkeypatch.setattr(asking, "named_as_a_key", lambda *_given: False)
    header, body = shapes.keys_in_sequence(600)
    keys = {float(row[1]) for row in body if row[1] != "-1"}
    folder = tmp_path / "mutant"
    _command_run(folder, header, body, {"EncounterKey": "identifier"}, refused=False)
    assert shapes.column_keys_shown(folder, keys, "patient_key") > 0


def test_a_rare_listed_value_waits_while_a_question_offering_identifier_is_open(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Skeptic 1's item 3, rule U (c) (the stand-ins page's ZS.1 and ZS.3): case `uc` at 20,000 rows.

    A score of 1 to 5 beside `-99` with a `7` on five rows, answered `no`
    to its Safe Harbor question and `measurement` to its checklist entry,
    beside sixty six-figure patient keys whose question is left open:
    the list would name the `7` five rows hold, and `no` widens what is
    published, so it waits -- the column is described as before. Once
    the key's question is answered, the list names `7` and the twin
    writes it. The mutant releases a rare value whatever is open, at 600
    rows through the internal switch, and the `7` is listed beside the
    open key.
    """
    header, body = shapes.beside_a_key(20_000)
    answers = {"EncounterKey": "identifier", "score": "no/measurement"}
    folder = tmp_path / "uc"
    folder.mkdir()
    table = fixtures.write(folder, "t.csv", fixtures.rows_to_csv(header, body))
    assert shapes.quiet(cli.main, ["profile", f"{table}", "--replace"], small_tables_refused=True) in (0, 3)
    _answered_keeping(folder, table, answers, [])
    held = contract.load_profile(str(folder / "t-profile.json"))
    assert not _column(held, "score").facts.few_values  # type: ignore[union-attr]
    answers["patient_key"] = "code"
    _answered_keeping(folder, table, answers, [])
    assert shapes.quiet(cli.main, ["generate", f"{folder / 't-profile.json'}", "--replace", "--seed", "0"]) == 0
    released = contract.load_profile(str(folder / "t-profile.json"))
    twin = _twin_cells(released)
    assert "7" in _column(released, "score").facts.few_values  # type: ignore[union-attr]
    assert twin["score"].count("7") == 5
    monkeypatch.setattr(profile, "_rare_list_released", lambda _rare, _released: True)
    header, body = shapes.beside_a_key(600)
    mutant = tmp_path / "mutant"
    _command_run(mutant, header, body, {"EncounterKey": "identifier", "score": "no/measurement"}, refused=False)
    moved = contract.load_profile(str(mutant / "t-profile.json"))
    assert "7" in _column(moved, "score").facts.few_values  # type: ignore[union-attr]


def test_the_safe_harbor_question_stands_beside_the_checklist_entry_in_the_first_round(
    tmp_path: pathlib.Path,
) -> None:
    """Skeptic 1's item 5 (the stand-ins page's ZS.3: "in the first round ... so one round settles them all").

    The first questions file asks a gapped score both GG's Safe Harbor
    question and its checklist entry, so one round of answers settles
    both and K-S3-66's rounds do not grow. Red on the source mutant that
    takes the entry off the checklist while that question stands, as the
    build did (planning-notes wave6/GG/r2): the entry then waits a round.
    """
    header, body = shapes.table({"score5": SHAPES["score5"]}, 600)
    table = fixtures.write(tmp_path, "t.csv", fixtures.rows_to_csv(header, body))
    assert shapes.quiet(cli.main, ["profile", f"{table}", "--replace"]) in (0, 3)
    questions = json.loads((tmp_path / "t-questions.json").read_text(encoding="utf-8"))
    listed = [
        one for one in ((questions.get("checklist") or {}).get("columns") or [])
        if isinstance(one, dict) and one.get("column") == "score5"
    ]
    assert _harbor_put(tmp_path, "score5") and listed
    # ...in words true of every such column (Codex's review, item 6): the
    # list names the values two cells or more hold, and says what becomes
    # of a number one cell holds; the old words claimed every value did.
    seen = [
        f"{one.get('what_synthtwin_saw')}"
        for key in ("about_your_file", "asked")
        for one in questions.get(key) or []
        if isinstance(one, dict) and one.get("column") == "score5"
        and "a wide stretch among them" in f"{one.get('what_synthtwin_saw')}"
    ]
    assert seen and "a number one cell holds is left off the list" in seen[0], seen
    assert "every one on two cells or more" not in seen[0]


def test_at_the_floor_a_many_valued_lab_column_keeps_its_shares(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The statistics skeptic's items 1 and 2 at 20,000 rows, through the library.

    A heart rate of 61 values beside -99 and a glucose of 46 beside 999,
    released: every level written, none in the gap or off the list, the
    mode pair met, and the share measure clean -- no listed value held by
    eleven real cells or more, outside the tails, written on fewer than a
    quarter of them (the build wrote 61, held by 175 real cells, on 2).
    A potassium to one decimal beside -99 whose tail holds values on one
    cell each is listed all the same: its singletons are left off the
    list, no cell lands in the gap, -99 is never written -99.0 and every
    listed level is present. The middle-of-room mutant starts each free
    boundary at the middle of its room, and a value starves.
    """
    header, body = shapes.table(shapes.LABS, 20_000, 4242)
    described = _described(tmp_path, header, body, released=tuple(header))
    twin = _twin_cells(described[0])
    blocks = _blocks(described[1])
    for name in header:
        place = header.index(name)
        real = [row[place] for row in body]
        found = shapes.faults(blocks[name], real, twin[name], taxonomy._quantile)
        listed = blocks[name]["few_values"]
        assert isinstance(listed, list) and listed, name
        assert set(listed) <= set(twin[name]), name
        assert (found["cells_in_gap"], found["cells_off_list"], found["mode_missed"]) == (0, 0, 0), (name, found)
        assert shapes.starved(blocks[name], real, twin[name]) == [], name
    assert "-99.0" not in twin["k_dec"]
    monkeypatch.setattr(
        generation, "_listed_ladder_ranks", lambda _facts, numbers, *_given: [None] * (len(numbers) + 1)
    )
    mutant = tmp_path / "mutant"
    mutant.mkdir()
    moved = _twin_cells(_described(mutant, header, body, released=tuple(header))[0])
    starving = []
    for name in ("hr61", "glu46"):
        place = header.index(name)
        starving += shapes.starved(blocks[name], [row[place] for row in body], moved[name])
    assert starving


_OWN_FEW_VALUES = taxonomy._few_values_of


def _every_value_on_two_cells(cells: object, details: object) -> "list[str]":
    """The build's listing rule: a column with any number on one cell lists nothing."""
    held: "dict[str, int]" = {}
    for cell in cells.classified:  # type: ignore[attr-defined]
        if cell.kind == parsing.NUMBER:
            held[cell.text] = (held[cell.text] if cell.text in held else 0) + 1
    if held and min(held.values()) < 2:
        return []
    return _OWN_FEW_VALUES(cells, details)  # type: ignore[arg-type]


def test_a_number_on_one_cell_leaves_the_rest_of_the_column_listed(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The orchestrator's LANE GG RULINGS 1 (1), the statistics skeptic's item 2.

    A potassium to one decimal beside -99, two of its values on one cell
    each: the rest are listed, the singletons never printed, and the twin
    writes no cell in the gap and never `-99.0`. The mutant is the build's
    rule -- a column with any number on one cell lists nothing -- and
    the twin writes cells deep inside the gap and `-99.0`.
    """
    header, body = shapes.table({"k_dec": shapes.LABS["k_dec"]}, 600, 4242)
    real = [row[0] for row in body]
    alone = [text for text in set(real) if real.count(text) == 1]
    assert alone
    for mutated in (False, True):
        if mutated:
            monkeypatch.setattr(taxonomy, "_few_values_of", _every_value_on_two_cells)
        folder = tmp_path / ("mutant" if mutated else "listed")
        folder.mkdir()
        described = _described(folder, header, body, released=("k_dec",))
        block = _blocks(described[1])["k_dec"]
        found = shapes.faults(block, real, _twin_cells(described[0])["k_dec"], taxonomy._quantile)
        if mutated:
            assert found["cells_in_gap"] + found["cells_off_list"] > 0, found
        else:
            listed = block["few_values"]
            assert isinstance(listed, list) and listed and not set(alone) & set(listed)
            assert (found["cells_in_gap"], found["cells_off_list"]) == (0, 0), found


@pytest.mark.parametrize(
    "case, written",
    [
        ("two_spellings", ("3", "3.0")),
        ("leading_nought", ("3", "003")),
        ("minus_nought", ("1", "-0")),
    ],
)
def test_a_number_written_two_ways_or_off_the_plain_family_is_not_listed(
    tmp_path: pathlib.Path, case: str, written: "tuple[str, str]"
) -> None:
    """Skeptic 1's item 4 D, K and N: each number written ONE way in the plain decimal family.

    A score of 1 to 5 beside -99 lists its values; written with `3` and
    `3.0` both, with `003`, or with `-0` as its only nought, it lists
    none, for the twin could not write the column's own spellings back
    from a list naming one of them. Red on the source mutants that drop
    the condition `each written one way` and the parsing guards against a
    leading nought and a minus nought (planning-notes wave6/GG/r2).
    """
    header, body = shapes.table({"score5": SHAPES["score5"]}, 600)
    listed = _described(tmp_path, header, body, released=("score5",))[1]
    assert _blocks(listed)["score5"].get("few_values"), case
    # `3` and `3.0` on alternate cells; every `3` as `003`; every `1` as
    # `-0`, the column's only nought.
    seen = 0
    respelled: "list[list[str]]" = []
    for (cell,) in body:
        if cell == written[0]:
            seen = seen + 1
            if case != "two_spellings" or seen % 2 == 0:
                cell = written[1]
        respelled += [[cell]]
    body = respelled
    folder = tmp_path / case
    folder.mkdir()
    assert not _blocks(_described(folder, header, body, released=("score5",))[1])["score5"].get("few_values"), case


def test_the_validator_counts_cells_off_the_list_and_listed_values_never_written(tmp_path: pathlib.Path) -> None:
    """Skeptic 1's item 4 J: `few_values.off_the_list` and `few_values.written`, each exact.

    A twin of a score beside -99 written as the twin writes it is held on
    both; with `-99.0` for `-99`, or `-91` on one cell, it misses the
    first; with every `3` written `4`, the second.
    """
    header, body = shapes.table({"score5": SHAPES["score5"]}, 600)
    described = _described(tmp_path, header, body, released=("score5",))[0]
    cells = _twin_cells(described)["score5"]

    def verdicts(written: "list[str]", name: str) -> "dict[str, str]":
        path = tmp_path / f"{name}.csv"
        path.write_text("score5\n" + "".join(f"{cell}\n" for cell in written), encoding="utf-8", newline="\n")
        outcome = validation.measure(described, str(path))
        return {
            check.subcheck: check.verdict
            for check in outcome.checks
            if check.subcheck in ("few_values.off_the_list", "few_values.written")
        }

    held = verdicts(cells, "held")
    assert held == {"few_values.off_the_list": validation.HELD, "few_values.written": validation.HELD}, held
    respelled = verdicts(["-99.0" if cell == "-99" else cell for cell in cells], "respelled")
    assert respelled["few_values.off_the_list"] == validation.MISSED
    in_gap = verdicts(["-91"] + cells[1:], "in_gap")
    assert in_gap["few_values.off_the_list"] == validation.MISSED
    unwritten = verdicts(["4" if cell == "3" else cell for cell in cells], "unwritten")
    assert unwritten["few_values.written"] == validation.MISSED


def test_a_loaded_list_longer_than_the_column_holds_is_refused(tmp_path: pathlib.Path) -> None:
    """Skeptic 1's item 4 L: the contract's VL2, at load.

    A description whose list names more numbers than its `n_distinct`
    counts -- or whose count of different numbers is not its count of
    different spellings -- is refused with VL2's words, so the census is
    never asked to write a value the column never held.
    """
    header, body = shapes.table({"score5": SHAPES["score5"]}, 600)
    document = _described(tmp_path, header, body, released=("score5",))[1]
    for broken in ("longer", "uncounted"):
        changed = json.loads(json.dumps(document))
        block = _blocks(changed)["score5"]
        if broken == "longer":
            block["few_values"] = list(block["few_values"]) + ["6"]  # type: ignore[call-overload]
        else:
            block["n_distinct_values"] = int(block["n_distinct_values"]) + 1  # type: ignore[call-overload]
        path = fixtures.write_profile(tmp_path, f"{broken}.json", changed)
        with pytest.raises(errors.ProfileError) as raised:
            contract.load_profile(str(path))
        assert contract.INVARIANTS["VL2"] in " ".join(f"{raised.value}".split()), broken


# REPAIR 2 (the orchestrator's LANE GG RULINGS 3, from the lane's verify,
# wave6/GG-verify.md, and Codex's review): each case below is red on its own
# mutant, the source mutants in planning-notes wave6/GG/r4/mutants.py.


def test_a_number_on_one_cell_at_a_gaps_edge_leaves_the_column_listed(tmp_path: pathlib.Path) -> None:
    """The verify's item 1 (LANE GG RULINGS 3 (2)), at 20,000 rows through the library.

    A days' supply with one `13` and one `83`, a Likert score beside `-98`
    and `-44` with one stray `-77`, a potassium beside `-99` with one
    `-50`: each one-cell number an edge of a published empty stretch,
    which kept the whole column out of the class, so the four faults came
    back at full size (`83` on 212 twin cells, `-77` on 89, 978 cells of
    `-99.0`). Each column is listed now, the strays left off and never
    printed in the list, the stretches meeting at a stray read as one:
    no twin cell inside a published stretch, none off the list, `-99`
    never `-99.0`, and the edge the twin then misses named
    (`empty_edges`). Red on the rule that refused a column whose edge
    was not listed (source mutant `edge` of planning-notes wave6/GG/r4).
    """
    header, body = shapes.edge_strays(20_000)
    described = _described(tmp_path, header, body, released=tuple(header))
    made = generation.generate(described[0], SEED)
    rows = list(csv.reader(io.StringIO(rendering.twin_csv(made))))
    twin = {rows[0][place]: [row[place] for row in rows[1:]] for place in range(len(rows[0]))}
    blocks = _blocks(described[1])
    for name in header:
        block = blocks[name]
        listed = block.get("few_values")
        assert isinstance(listed, list) and listed, name
        assert not set(shapes.EDGE_STRAYS[name]) & set(listed), name
        real = [row[header.index(name)] for row in body]
        found = shapes.faults(block, real, twin[name], taxonomy._quantile)
        assert (found["cells_in_gap"], found["cells_off_list"]) == (0, 0), (name, found)
        assert set(listed) <= set(twin[name]), name
        assert "empty_edges" in [one.fact for one in made.deviations if one.column == name], name
    assert "-99.0" not in twin["k_edge"]


def test_three_figure_keys_beside_minus_ninety_nine_or_on_forty_in_a_hundred_rows_are_held(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The verify's item 2 (HIPAA, live on the pushed head; LANE GG RULINGS 3 (1)), at 20,000 rows.

    Sixty three-figure keys beside `-99` on 2 % of rows (k60f3m99) printed
    all sixty and wrote 19,617 twin cells real; beside `-1` on 40 %
    (k60f3m40), 57 and 12,061. Every negative whole number and run of
    nines is set aside now, whatever its share, where the floor's cells
    are left: both are held unanswered, no key in the column's own facts,
    GG's question not put. Red on today's rule, which set aside `-d` alone
    under a cap of one cell in three: each mutant at 600 rows through the
    internal switch prints the keys.
    """
    shaped = {"k60f3m99": {"placeholder": "-99"}, "k60f3m40": {"share": 0.4}}

    def keys_of(body: "list[list[str]]", place: int = 1) -> "set[float]":
        return {float(row[place]) for row in body if not row[place].startswith("-")}

    # Both shapes in one table, a column each: each column goes red on its
    # own mutant at this size too (planning-notes wave6/GG/r4,
    # keys-combined-*.log: 60 and 58 keys printed, GG's question put) --
    # and skeptic 1's k60f3m beside them (`PatientKeyC`, `-1` on 2 %), one
    # command run for the three, so the gate keeps within its minutes.
    header, body = shapes.keys_beside_placeholders(20_000, plain=True)
    folder = tmp_path / "keys"
    twin = _command_run(folder, header, body, {"EncounterKey": "identifier"})
    described = contract.load_profile(str(folder / "t-profile.json"))
    # ...and `PatientKeyD`, six-figure keys beside `-1` and `-9999` on 2 %
    # each (the verify 2's s1, AT GG'S MERGE (3) 1: live on bd76c75c, 60
    # keys printed and 19,224 twin cells real): held unanswered, red on its
    # mutant M13 (the width route's set-aside run again only `if not
    # beside`, so the sign route's rest keeps `-9999` and the column reads
    # as a measurement).
    for name in ("patient_key", "PatientKeyB", "PatientKeyC", "PatientKeyD"):
        keys = keys_of(body, header.index(name))
        assert _column(described, name).role == "identifier", name
        assert shapes.column_keys_shown(folder, keys, name) == 0, name
        assert not _harbor_put(folder, name), name
        equal = sum(1 for cell in twin[name] if shapes.number(cell) in keys)
        assert equal <= len(twin[name]) // 10, (name, equal)
    own = asking._beside_width_placeholders

    def capped(present: "list[str]", floor: int) -> "list[str]":
        rest = own(present, floor)
        return [] if 3 * (len(present) - len(rest)) > len(present) else rest

    mutants = {
        "k60f3m99": ("_a_width_route_placeholder", asking._a_width_placeholder),
        "k60f3m40": ("_beside_width_placeholders", capped),
    }
    for name, (attribute, mutant) in mutants.items():
        with monkeypatch.context() as patched:
            patched.setattr(asking, attribute, mutant)
            # ...and lane HB's key-name route withdrawn, as in the case above.
            patched.setattr(asking, "named_as_a_key", lambda *_given: False)
            header, body = shapes.keys_in_sequence(600, **shaped[name])  # type: ignore[arg-type]
            folder = tmp_path / f"mutant-{name}"
            _command_run(folder, header, body, {"EncounterKey": "identifier"}, refused=False)
            assert shapes.column_keys_shown(folder, keys_of(body), "patient_key") > 0, name


def test_a_column_held_as_declined_counted_dates_is_not_offered_the_question(tmp_path: pathlib.Path) -> None:
    """The verify 2's s2 (batch 4m's merge, AT GG'S MERGE (3) 2), at 20,000 rows through the command.

    Day counts written `45.001` to `45.005` -- a point between thousands --
    beside `-99` on 8 % of rows, declared `--date-count score excel-1900`:
    the reading is declined, so the column is held as declined counted
    dates (the orchestrator's LANE HX2 ADDENDUM 2), and GG's Safe Harbor
    question is not put: its `no` could never release a list. Red on the
    mutant M16, which drops build_document's declined-dates clause from the
    few-valued class test: the column stays held and the question is put.
    """
    draw = random.Random(20261029)
    body = [
        [f"{9000000 + index}", "-99" if draw.random() < 0.08 else f"45.00{draw.randint(1, 5)}"]
        for index in range(20_000)
    ]
    folder = tmp_path / "score"
    folder.mkdir()
    table = fixtures.write(folder, "t.csv", fixtures.rows_to_csv(["EncounterKey", "score"], body))
    options = ["--date-count", "score", "excel-1900"]
    assert shapes.quiet(cli.main, ["profile", f"{table}", "--replace"] + options) in (0, 3)
    assert _column(contract.load_profile(str(folder / "t-profile.json")), "score").role == "identifier"
    assert not _harbor_put(folder, "score")


def test_the_width_set_aside_leaves_the_floors_cells_and_reads_a_run_of_nines_as_a_value(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """LANE GG RULINGS 3 (1)'s floor, and Codex's review, item 2.

    The set-aside leaves at least the floor's cells or none. A pulse of 99
    to 159 holds `100` beside its `99`, so the `99` is one of its values,
    not a placeholder: no question offering `identifier` is put and the
    column is described and written as before (Codex: held as a key, its
    twin 16 to 998 with 18,688 cells outside the source's range). Red on
    the mutant that sets every run of nines aside.
    """
    assert asking._beside_width_placeholders(["-1"] * 30 + ["123"] * 10, 11) == []
    assert asking._beside_width_placeholders(["-1"] * 30 + ["123"] * 11, 11) == ["123"] * 11
    assert asking._beside_width_placeholders(["9999"] + ["123"] * 11, 11) == ["123"] * 11
    header, body = shapes.pulse(20_000)
    present = [row[0] for row in body]
    assert "99" in asking._beside_width_placeholders(present + ["-1"], 11)
    folder = tmp_path / "pulse"
    twin = _command_run(folder, header, body, {})["pulse"]
    assert _column(contract.load_profile(str(folder / "t-profile.json")), "pulse").role != "identifier"
    assert {float(cell) for cell in twin} <= {float(cell) for cell in present}

    def every_nines(present: "list[str]", floor: int) -> "list[str]":
        rest = [one for one in present if not asking._a_width_route_placeholder(one)]
        return rest if floor <= len(rest) < len(present) else []

    monkeypatch.setattr(asking, "_beside_width_placeholders", every_nines)
    header, body = shapes.pulse(600)
    mutant = tmp_path / "mutant"
    _command_run(mutant, header, body, {}, refused=False)
    assert _column(contract.load_profile(str(mutant / "t-profile.json")), "pulse").role == "identifier"


def test_the_validator_keeps_back_the_count_of_cells_off_the_list(tmp_path: pathlib.Path) -> None:
    """Codex's review, item 1: one `4.5` among a score's cells was printed as `achieved 1`.

    The count of cells off the list is a number counted in the measured
    file, so the line keeps it back (V5.4) and says why; the verdict is
    MISSED as before. Red on the source mutant that prints it.
    """
    pairs = (("-99", 120), ("1", 240), ("2", 330), ("3", 450), ("4", 380), ("5", 480))
    header, body = shapes.counted(pairs)
    described = _described(tmp_path, header, body, released=("score",))[0]
    cells = [row[0] for row in body]
    cells[cells.index("5")] = "4.5"
    path = tmp_path / "measured.csv"
    path.write_text("score\n" + "".join(f"{cell}\n" for cell in cells), encoding="utf-8", newline="\n")
    checks = [
        check for check in validation.measure(described, str(path)).checks
        if check.subcheck == "few_values.off_the_list"
    ]
    assert [check.verdict for check in checks] == [validation.MISSED]
    assert checks[0].achieved == "" and "NOT SHOWN" in " ".join(checks[0].note), checks[0]


def test_the_written_forms_are_met_across_the_values_between(tmp_path: pathlib.Path) -> None:
    """Codex's review, item 3: `-99.00`, `1.0`, `2`, `3.0`, `4.00`, `5.0` and `6`, every one repeated.

    With the one-decimal form met first, no boundary joins the two-decimal
    form to the plain one, and the solver wrote 9,372 plain cells for
    9,440 and 4,863 two-decimal ones for 4,795, blaming the facts. A row
    now moves between two values of the two forms past the values
    between, each keeping its count: every form's published count met
    and neither census named. At a tenth of Codex's counts, through the
    library; red on the source mutant without that step.
    """
    header, body = shapes.counted(tuple((text, held // 10) for text, held in shapes.FORMS))
    described = _described(tmp_path, header, body, released=("score",))
    block = _blocks(described[1])["score"]
    assert block.get("few_values"), block
    made = generation.generate(described[0], SEED)
    rows = list(csv.reader(io.StringIO(rendering.twin_csv(made))))
    held: "dict[str, int]" = {}
    for (cell,) in rows[1:]:
        form = "plain" if "." not in cell else f"{len(cell.split('.')[1])}"
        held[form] = held.get(form, 0) + 1
    wanted = {"plain": block["numeric_styles"]["plain"]}  # type: ignore[index]
    wanted.update(block["fraction_widths"])  # type: ignore[arg-type]
    assert held == wanted, (held, wanted)
    named = [one.fact for one in made.deviations if one.column == "score"]
    assert "fraction_widths" not in named and "numeric_styles" not in named, named


def test_the_mode_keeps_its_place_where_the_cells_left_off_need_room(tmp_path: pathlib.Path) -> None:
    """Codex's review, item 4: `-100`, `-99` and 1 to 98 on 20 cells each, beside one `50.5`.

    Every listed value already holds as many cells as the mode may, so
    the one cell of the number left off has nowhere to go, and the solver
    gave the mode pair up whole (`-100` written 103 times of 200 at
    20,000 rows, another value 302). The mode's count is raised by one
    now, every other value's bound with it: still the mode, one cell over
    its published count, that count named. Red on the source mutant that
    gives the pair up.
    """
    header, body = shapes.mode_room(20)
    described = _described(tmp_path, header, body, released=("score",))
    block = _blocks(described[1])["score"]
    assert len(block.get("few_values") or []) == 100 and block["mode"] == -100, block.get("mode")
    made = generation.generate(described[0], SEED)
    rows = list(csv.reader(io.StringIO(rendering.twin_csv(made))))
    held: "dict[str, int]" = {}
    for (cell,) in rows[1:]:
        held[cell] = held.get(cell, 0) + 1
    # `-100` is still the twin's mode -- the tie rule names the smallest --
    # one cell over its published count, and that count is named.
    assert held["-100"] == block["mode_count"] + 1, held["-100"]
    assert max(held.values()) == held["-100"]
    assert "mode_count" in [one.fact for one in made.deviations]


def test_a_list_the_count_in_people_would_hold_is_never_offered(tmp_path: pathlib.Path) -> None:
    """Codex's review, item 5: a score whose `7` is one declared patient's, 20 rows.

    The count in people holds the score, and its name had already
    entered the class, so GG's question offered `no` with a list `no`
    could never release. The class is decided on the block `no` would
    publish, list and all: the question is not put. At 20,000 rows
    through the command; red on the source mutant that decides it first.
    """
    header, body = shapes.one_patients_value()
    folder = tmp_path / "patients"
    _command_run(folder, header, body, {}, ("patient",))
    assert not _harbor_put(folder, "score")

