"""Layer L0's leftovers (lane BT3b, plan P4-D467; method G5.7c and G6.9).

THE GATE OF LANE BT3b. First the item that made the lane a prerequisite
of lane CHON (LANE CHON RULINGS 8 (1)): a column written as its listed
values (method G6.9, a survey score of `-99` and 1 to 5) took its counts
from the published facts the listed census reads, never from its L0
bands, so on a chained description `generate` refused it ("an L0 band of
the column ... holds 3649 cells where its published count is 3651"): a
description the product writes and its own `generate` refuses. The
census now pins each band's cut rank first (G6.9 step 0), and G5.7a's
(P6) makes such a column without its band totals (rule B3) where a band
holds cells and no listed value, so the internal check never fires.

An invented survey table of 20,000 rows goes through `cli.main` with the
chain's switch, the subject question answered 'one row each' and the
fixed test key; `generate` then reads the chain as lane CHON's switch
makes it read it (the description's chain where one stands), and
`validate` reads the twin with the chain's lines. Each L0 band's
published count is checked against the cells as the file wrote them,
and the twin's cells against the published count, band by band; no
published band or table cell counts 1 to 10 rows. The oracle's frozen
cases (tests/reference/generation-branch-vectors-34.json) hold the
product to the method's text. Every table here is invented; the key is a
fixed test key.
"""

import contextlib
import io
import json
import os
import pathlib
import random

import pytest

import fixtures

from synthtwin import asking, cli, contract, generation

TEST_KEY = bytes(range(32))
SURVEY_ROWS = 20_000
SURVEY_SEED = 20261113
SURVEY_COLUMNS = ["respondent", "mood_word", "pain_score", "sleep_score", "scale_sum", "followed_up"]
SCORES = ("pain_score", "sleep_score", "scale_sum")
MOODS = (("very low", 10.0), ("low", 22.0), ("middling", 31.0), ("good", 26.0), ("very good", 11.0))
FOLLOWED = (("yes", 47.0), ("no", 33.0), ("not reached", 20.0))
VECTORS = pathlib.Path(__file__).resolve().parent / "reference" / "generation-branch-vectors-34.json"


def _installation(folder: pathlib.Path) -> pathlib.Path:
    """A data folder holding the fixed test key."""
    data = folder / "data"
    data.mkdir(mode=0o700)
    if os.name != "nt":
        data.chmod(0o700)
    key = data / "chain-key"
    key.touch(mode=0o600)
    if os.name != "nt":
        key.chmod(0o600)
    key.write_bytes(TEST_KEY)
    return data


def _pick(draw: random.Random, weighted: "tuple[tuple[str, float], ...]") -> str:
    point = draw.random() * sum(weight for _word, weight in weighted)
    for word, weight in weighted:
        point -= weight
        if point < 0:
            return word
    return weighted[-1][0]


def _survey(rows: int, seed: int) -> "tuple[str, dict[str, list[str]]]":
    """An invented survey: two scores of 1 to 5 beside the code -99, their sum beside 999, two word columns."""
    draw = random.Random(seed)
    cells: "dict[str, list[str]]" = {name: [] for name in SURVEY_COLUMNS}
    lines = [",".join(SURVEY_COLUMNS)]
    for index in range(rows):
        first = min(5, 1 + int(draw.random() * 5.4))
        second = min(5, 1 + int(draw.triangular(0.0, 5.0, 3.0)))
        written = [
            f"S{40000 + index}",
            _pick(draw, MOODS),
            f"{first}" if draw.random() > 0.08 else "-99",
            f"{second}" if draw.random() > 0.05 else "-99",
            f"{first + second}" if draw.random() > 0.06 else "999",
            _pick(draw, FOLLOWED),
        ]
        for name, cell in zip(SURVEY_COLUMNS, written):
            cells[name] += [cell]
        lines += [",".join(written)]
    return "\n".join(lines) + "\n", cells


def _quietly(command: "list[str]", chain: "cli.ChainRun | None" = None) -> "tuple[int, str]":
    said = io.StringIO()
    with contextlib.redirect_stdout(said), contextlib.redirect_stderr(said):
        code = cli.main(command, chain=chain) if chain is not None else cli.main(command)
    return code, said.getvalue()


def _chained_generate(monkeypatch: pytest.MonkeyPatch, command: "list[str]") -> "tuple[int, str]":
    """`synthtwin generate` reading the description's chain, as lane CHON's switch makes it read one where it stands."""
    built = contract.load_profile
    monkeypatch.setattr(contract, "load_profile", lambda raw_path, chain=False: built(raw_path, True))
    try:
        return _quietly(command)
    finally:
        monkeypatch.setattr(contract, "load_profile", built)


def _switched_survey(folder: pathlib.Path, text: str) -> "tuple[tuple[int, str], pathlib.Path, pathlib.Path]":
    """The survey through the switched `profile`, then its questions answered as the person who holds it answers them.

    Each score's Safe Harbor question is answered `no` (a score names no
    person, place, date or record), which lists its values (method G6.9,
    plan P4-D440), and the description is written again from the answers.
    """
    table = fixtures.write(folder, "survey.csv", text)
    data = _installation(folder)
    out = folder / "out"
    out.mkdir()
    arguments = ["profile", str(table), "--out-dir", str(out), "--identifier", "respondent"]
    for name in SCORES:
        arguments += ["--measurement", name]
    first = _quietly(arguments, cli.ChainRun(rows_per_person=asking.ANSWER_ONE_ROW_EACH, folder=str(data)))
    if first[0] != 0:
        return first, out / "survey-profile.json", data
    questions = out / "survey-questions.json"
    document = json.loads(questions.read_text(encoding="utf-8"))
    for entry in document["asked"]:
        if entry.get("column") in SCORES:
            entry["your_answer"] = "no"
    fixtures.write(out, questions.name, json.dumps(document, indent=2))
    answered = _quietly(
        ["profile", str(table), "--out-dir", str(out), "--answers", str(questions)],
        cli.ChainRun(rows_per_person=asking.ANSWER_ONE_ROW_EACH, folder=str(data), replace_description=True),
    )
    return answered, out / "survey-profile.json", data


@pytest.fixture(scope="module")
def survey(tmp_path_factory: pytest.TempPathFactory) -> "dict[str, object]":
    """The invented survey through the switched `profile` and its answers round."""
    folder = tmp_path_factory.mktemp("survey")
    text, cells = _survey(SURVEY_ROWS, SURVEY_SEED)
    profiled, described, data = _switched_survey(folder, text)
    return {"profiled": profiled, "described": described, "cells": cells, "data": data}


def _twin_cells(path: pathlib.Path, name: str) -> "list[str]":
    lines = path.read_text(encoding="utf-8").splitlines()
    at = lines[0].split(",").index(name)
    return [line.split(",")[at] for line in lines[1:]]


def _band_counts(cells: "list[str]", edges: "list[float]") -> "list[int]":
    counted = [0 for _band in range(len(edges) + 1)]
    for cell in cells:
        value = float(cell)
        counted[sum(1 for edge in edges if edge <= value)] += 1
    return counted


def _ladder(document: "dict[str, object]") -> "dict[str, dict[str, object]]":
    statistical = document["relationships"]["statistical"]  # type: ignore[index]
    return {f"{entry['column']}": entry for entry in statistical["ladder"]}  # type: ignore[index]


def _edges(column: "dict[str, object]", entry: "dict[str, object]") -> "list[float]":
    """Each L0 band's lower rung but the first, read off the published ladder of the column."""
    rungs: "dict[str, object]" = {}
    rungs.update(column["percentiles"])  # type: ignore[arg-type]
    rungs.update(column.get("percentiles_between") or {})  # type: ignore[arg-type]
    return [float(f"{rungs[band[0][0]]}") for band in entry["l0"][1:]]  # type: ignore[index]


def test_the_chained_survey_generates_and_validates_with_every_band_at_its_published_count(survey, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """LANE CHON RULINGS 8 (1): the description the product writes, its own `generate` makes and `validate` reads.

    Each score's L0 bands hold, in the twin, exactly the counts published,
    and those counts are the cells as the file wrote them (no value of
    these columns is changed by the description's rules); no band and no
    table cell of the chain counts 1 to 10 rows.
    """
    assert survey["profiled"][0] == 0, survey["profiled"][1][-2000:]
    document = json.loads(survey["described"].read_text(encoding="utf-8"))  # type: ignore[attr-defined]
    ladder = _ladder(document)
    statistical = document["relationships"]["statistical"]
    assert statistical["chain"], "the subject question answered, the chain is drawn"
    by_name = {f"{column['name']}": column for column in document["columns"]}
    for name in SCORES:
        assert by_name[name]["few_values"], name  # each score is written as its listed values (G6.9)
        assert name in ladder, name
    for entry in ladder.values():
        assert all(total == 0 or total >= 11 for total in entry["totals"]), entry["column"]
    for family in statistical["chain"]:
        assert all(cell == 0 or cell >= 11 for row in family["table"] for cell in row), family["child"]
    twin_folder = tmp_path / "twin"
    twin_folder.mkdir()
    made = _chained_generate(monkeypatch, ["generate", str(survey["described"]), "--out-dir", str(twin_folder), "--seed", "0"])
    assert made[0] == 0, made[1][-2000:]
    twin = twin_folder / "survey-twin.csv"
    for name in SCORES:
        entry = ladder[name]
        edges = _edges(by_name[name], entry)
        written = _band_counts(survey["cells"][name], edges)  # type: ignore[index]
        assert written == entry["totals"], name
        assert _band_counts(_twin_cells(twin, name), edges) == entry["totals"], name
    checked = _quietly(
        ["validate", str(survey["described"]), "--twin", str(twin), "--out-dir", str(twin_folder)],
        cli.ChainRun(folder=str(survey["data"])),
    )
    assert checked[0] == 0, checked[1][-2000:]


def test_red_with_the_band_totals_left_out_of_the_listed_census(survey, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The mutant: G6.9 step 0 taken out, `generate` refuses the chained survey with its internal check, as the base did."""
    monkeypatch.setattr(generation, "_listed_l0_pins", lambda facts, numbers, total: [])
    twin_folder = tmp_path / "twin"
    twin_folder.mkdir()
    made = _chained_generate(monkeypatch, ["generate", str(survey["described"]), "--out-dir", str(twin_folder), "--seed", "0"])
    assert made[0] != 0 and "an L0 band of the column" in made[1], made[1][-2000:]


def _listed_facts(few_values: "tuple[str, ...]") -> contract.NumericFacts:
    """A listed column's numeric facts, for G5.7a's (P6) alone (machine-free)."""
    facts = contract.NumericFacts.__new__(contract.NumericFacts)
    object.__setattr__(facts, "few_values", few_values)
    object.__setattr__(facts, "number_spellings", {})
    return facts


def test_p6_a_band_holding_cells_and_no_listed_value_is_made_without_its_band_totals() -> None:
    """G5.7a's (P6): such a band cannot be met by the listed census, so the column is laid by rule B3, never refused."""
    facts = _listed_facts(("1.0", "2.0", "3.0"))
    assert generation._listed_l0_room(facts, contract.L0Cuts((2.0, 3.0), (400, 300, 300), 1000))
    # [1.5, 2.0) holds 120 cells and no listed value.
    assert not generation._listed_l0_room(facts, contract.L0Cuts((1.5, 2.0), (280, 120, 600), 1000))
    # [2.0, 2.5) holds one listed value and no cell.
    assert not generation._listed_l0_room(facts, contract.L0Cuts((2.0, 2.5), (400, 0, 600), 1000))
    # A column the listed census does not write is not read.
    assert generation._listed_l0_room(_listed_facts(()), contract.L0Cuts((1.5, 2.0), (280, 120, 600), 1000))


def _codex_column(rows: int) -> str:
    """Codex's invented count (lane BT2's review, item 1): 1,000 whole numbers of 10 to 83 repeated, beside a label column."""
    draw = random.Random(54)
    base = [str(10 + draw.randrange(74)) for _each in range(1000)]
    cells = base * (rows // 1000)
    pick = random.Random(55)
    return "column_1,other\n" + "".join(f"{cell},{pick.choice(['a', 'b', 'c'])}\n" for cell in cells)


@pytest.fixture(scope="module")
def codex(tmp_path_factory: pytest.TempPathFactory) -> contract.Profile:
    """Codex's column at 20,000 rows, described with the chain's switch (one row each, the fixed test key), loaded behind it."""
    from synthtwin import chain, profile, reading, taxonomy

    folder = tmp_path_factory.mktemp("codex")
    path = fixtures.write(folder, "codex.csv", _codex_column(SURVEY_ROWS))
    table = reading.read_table(str(path), small_cell_floor=11)
    settings = taxonomy.Settings(small_cell_floor=11)
    document = profile.build_document(table, settings, [], [], ["column_1"])
    chained = chain.describe(table, document, settings, chain.ChainSwitch("codex", TEST_KEY, rows_per_person=chain.ROWS_ONE), None, ["column_1"])
    assert chained.statistical is not None
    relationships = dict(document["relationships"])  # type: ignore[call-overload]
    relationships["statistical"] = chained.statistical
    written = dict(document)
    written["relationships"] = relationships
    switched = fixtures.write_profile(folder, "codex-switched.json", written)
    return contract.load_profile(str(switched), chain=True)


def _heaps_broken(loaded: contract.Profile, seed: int) -> "list[tuple[float, int]]":
    """Each proven heap of the column (G5.7c step 1) with how many of its ranks the twin holds at another value."""
    cells = sorted(float(cell) for cell in generation.twin_column(generation.generate_held(loaded, seed), 0))
    broken: "list[tuple[float, int]]" = []
    for value, first, last in generation._l0_proven_heaps(loaded.columns[0].facts, len(cells)):  # type: ignore[arg-type]
        off = sum(1 for rank in range(first, last + 1) if cells[rank] != value)
        if off:
            broken += [(value, off)]
    return broken


def test_every_proven_heap_of_codexs_count_stands_whole_at_twenty_thousand_rows(codex) -> None:
    """LANE BT3 OWED ADDED (3): step 4 handed 41 of the heap of 56's 402 ranks to 55 at every seed; each heap now stands whole."""
    assert generation._l0_proven_heaps(codex.columns[0].facts, SURVEY_ROWS)  # type: ignore[arg-type]
    for seed in (0, 1, 2):
        assert _heaps_broken(codex, seed) == [], seed


def test_red_with_the_mode_step_free_of_the_heaps(codex, monkeypatch: pytest.MonkeyPatch) -> None:
    """The mutant: step 4 hands the mode's cells over whatever heap they hold, and the heap of 56 stands 41 ranks off."""
    monkeypatch.setattr(generation, "_l0_mode_room", lambda entries, own, side, heaps, giving: 10**9)
    assert _heaps_broken(codex, 0) == [(56.0, 41)]


def test_the_thirty_first_files_next_heap_case_is_red_with_the_mode_step_free_of_the_heaps(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The oracle's frozen answer for Codex's column (vectors 31, its answer moved by this fix, A-P4-59), red on the mutant."""
    import test_stage6_band_totals

    case = test_stage6_band_totals._oracle_cases()["l0_cells_next_heap"]
    (tmp_path / "fixed").mkdir()
    assert test_stage6_band_totals._moved(tmp_path / "fixed", "l0_cells_next_heap", case) == case["answer"]
    monkeypatch.setattr(generation, "_l0_mode_room", lambda entries, own, side, heaps, giving: 10**9)
    (tmp_path / "mutant").mkdir()
    assert test_stage6_band_totals._moved(tmp_path / "mutant", "l0_cells_next_heap", case) != case["answer"]


def _mode_step(values: "list[float]", sizes: "list[int]", pieces: "list[int]", today: "list[int]", heaps: "list[tuple[float, int, int]]") -> "list[int]":
    """G5.7c step 4 alone on hand-built strata (machine-free): the mode `20` published at 200 cells, today's twin holding it so."""
    facts = contract.NumericFacts.__new__(contract.NumericFacts)
    object.__setattr__(facts, "mode", 20.0)
    object.__setattr__(facts, "mode_count", 200)
    walls = tuple(
        generation._Piece(0, sum(sizes), None, False, None, False, "positive", False, False, 0)
        for _piece in range(max(pieces) + 1)
    )
    count = len(values)
    entries = generation._Entries(list(values), list(sizes), list(range(count)), [0] * count, list(sizes), list(pieces), count, list(today))
    was = generation._Entries(list(values), list(today), list(range(count)), [0] * count, list(today), list(pieces), count, list(today))
    generation._l0_mode_kept(facts, walls, entries, was, heaps)
    return entries.sizes


def _oracle_mode_step(values: "list[float]", sizes: "list[int]", pieces: "list[int]", heaps: "list[tuple[float, int, int]]") -> "list[int]":
    """The oracle's step 4 (A-P4-59) on the same strata, from the oracle module the vectors' own test loads."""
    import test_generation_reference

    moved: "list[int]" = test_generation_reference.gen.l0_mode_step(list(values), list(sizes), list(pieces), [False] * len(values), 20.0, 200, heaps)
    return moved


def test_a_neighbour_gives_the_mode_none_of_its_own_heaps_ranks() -> None:
    """Step 4's clause, the mode short of its count: `10`'s proven heap reaches the boundary with the mode, so `10` gives none.

    The mode `20` holds 190 cells of its published 200; its nearer
    neighbour on the tie is the lower, `10`, whose proven heap holds ranks
    0 to 149, every rank it holds, so the ten come from `30`. With four
    ranks of `10` free of its heap (146 to 149), `10` gives those four and
    `30` the other six. The oracle says the same. Red where the neighbour's
    heap no longer bounds what it gives (`10` would give all ten).
    """
    values = [10.0, 20.0, 30.0]
    for heap_end, wanted in ((149, [150, 200, 150]), (145, [146, 200, 154])):
        heaps = [(10.0, 0, heap_end)]
        assert _mode_step(values, [150, 190, 160], [0, 0, 0], [150, 200, 150], heaps) == wanted, heap_end
        assert _oracle_mode_step(values, [150, 190, 160], [0, 0, 0], heaps) == wanted, heap_end


def test_what_no_side_can_take_stays_on_the_mode() -> None:
    """Step 4's clause, the mode over its count: its own proven heap leaves its one neighbour of its piece no room.

    The mode `20` holds ranks 100 to 309, ten over its published 200; `10`
    lies in another piece, so `30` is its only side, and the mode's heap
    (ranks 110 to 309) reaches the boundary with `30`. No cell can cross
    without breaking the heap, so the ten stay on the mode. The oracle
    says the same. Red where the rest goes to the first side anyway.
    """
    values = [10.0, 20.0, 30.0]
    heaps = [(20.0, 110, 309)]
    assert _mode_step(values, [100, 210, 150], [0, 1, 1], [100, 200, 160], heaps) == [100, 210, 150]
    assert _oracle_mode_step(values, [100, 210, 150], [0, 1, 1], heaps) == [100, 210, 150]


def _oracle_cases() -> "dict[str, dict[str, object]]":
    cases: "dict[str, dict[str, object]]" = json.loads(VECTORS.read_text(encoding="utf-8"))["cases"]
    return cases


@pytest.mark.parametrize("name", sorted(_oracle_cases()))
def test_the_product_answers_every_case_of_the_thirty_fourth_file(name: str, tmp_path: pathlib.Path) -> None:
    """The frozen cases (A-P4-59): the product's cells and the oracle's, written from the method's text, agree."""
    import test_stage6_band_totals

    case = _oracle_cases()[name]
    answer = case["answer"]
    loaded = test_stage6_band_totals._case_profile(tmp_path, name, case)
    if case["rule"] == "room":
        laid = generation._l0_columns(loaded)[loaded.columns[0].name][0] is not None
        assert laid is answer["laid"], name  # type: ignore[index]
        return
    cells = tuple(generation.twin_column(generation.generate_held(loaded, int(f"{case['seed']}")), 0))
    assert test_stage6_band_totals._counted(cells) == answer["counts"], name  # type: ignore[index]
