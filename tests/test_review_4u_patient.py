"""Batch 4u's outside review, items 3, 5 and 8: the patient layer's checks, the trend close's work, the report's figures.

Item 3: where `grain` stands, `synthtwin validate` checks the person column
and each patient-fixed column on each patient's FIRST POSITION -- the row
the published position column puts first, ties and absent readings by row
order, as the producer read it (`patient_layer`'s position column, read
before the description held it) -- never on the patient's first stored
row. Read on the stored row, a table whose visits are stored newest first
missed its own patient-fixed counts.

Item 5: the trend close's exact steps (G16.15, `patient_walk._exact_close`)
keep each step's patients in a heap with stale entries skipped, so a
patient is added or removed in a bounded number of reads and no list is
shifted; the results are the lowest-patient reference's, as before.

Item 8: the report beside a chained twin states the figures lane CHG
measured with its grouping gate (plan P4-D492), not the ones measured
before it.

The tables are invented. Item 3's cases run the shipped commands with the
patient layer's sub-switch set on in their own process
(`cli._PATIENT_LAYER_SHIPPED`, off in the shipped command, as
tests/test_stage6_switch_on.py sets it).
"""

import datetime
import json
import pathlib
import random

import pytest

import fixtures
from synthtwin import asking, chain_validation, cli, reading, results, validation


def _ran(argv: "list[str]") -> "tuple[results.Result, str]":
    """One command line through `cli.run`, and every character its screen showed."""
    screen: "list[tuple[str, str]]" = []
    made = cli.run(argv, screen=screen)
    return made, "".join(text for _stream, text in screen)


def _answered_as_the_person(questions: pathlib.Path, person: str) -> int:
    """The questions answered as the person who holds the table; how many were open and are answered now.

    The person column `identifier` (rows sharing a value are one person),
    the subject question with the person column's name, and every other
    question `no` where `no` is offered (the other columns name no person,
    place or record).
    """
    document = json.loads(questions.read_text(encoding="utf-8"))
    answered = 0
    for entry in document["asked"]:
        if f"{entry.get('your_answer') or ''}":
            continue
        offered = [choice["answer"] for choice in entry["answers_you_can_give"]]
        if entry.get("column") == person and "identifier" in offered:
            entry["your_answer"] = "identifier"
            answered += 1
        elif "no" in offered:
            entry["your_answer"] = "no"
            answered += 1
    subject = document[asking.BETWEEN_COLUMNS].get(asking.ROWS_PER_PERSON)
    if isinstance(subject, dict) and not f"{subject.get('your_answer') or ''}":
        subject["your_answer"] = person
        answered += 1
    questions.write_text(json.dumps(document, indent=1) + "\n", encoding="utf-8", newline="\n")
    return answered


# -- item 3: the blocks counted in patients read at each patient's first position


def _visits_text(counts: "list[int]", sites: "list[str]", odd: "list[int]", seed: int, newest_first: bool) -> str:
    """Visits of a patient a month apart from its own first day, a site fixed for the patient, a reading.

    Patient `p` has `counts[p]` visits and site `sites[p]`; each patient of
    `odd` has its newest visit written with the other site. With
    `newest_first` each patient's visits stand newest first, the patients
    one after another (Codex's table); otherwise every row stands in a drawn
    order, save that each patient of `odd` has its newest visit before its
    other visits, so its first stored row is the visit the producer does
    not read first.
    """
    draw = random.Random(seed)
    origin = datetime.date(2021, 1, 4)
    items: "list[tuple[int, int]]" = []
    for p in range(len(counts)):
        order = list(range(counts[p]))
        if newest_first:
            order.reverse()
        items += [(p, k) for k in order]
    if not newest_first:
        draw.shuffle(items)
        for p in odd:
            places = [at for at in range(len(items)) if items[at][0] == p]
            newest = [at for at in places if items[at][1] == counts[p] - 1][0]
            items[places[0]], items[newest] = items[newest], items[places[0]]
    lines = ["pid,visit_date,site,reading"]
    for p, k in items:
        day = origin + datetime.timedelta(days=(p * 37) % 330 + 30 * k)
        site = sites[p]
        if p in odd and k == counts[p] - 1:
            site = "B" if site == "A" else "A"
        lines += [f"P{p + 1:05d},{day.isoformat()},{site},{round(100 + draw.gauss(0, 10), 1)}"]
    return "\n".join(lines) + "\n"


def _described_with_grain(folder: pathlib.Path, text: str) -> "tuple[pathlib.Path, pathlib.Path, dict[str, object]]":
    """The table described by the shipped command, its questions answered as the person who holds it, until grain stands."""
    folder.mkdir(parents=True, exist_ok=True)
    table = fixtures.write(folder, "visits.csv", text)
    first, said = _ran(["profile", str(table)])
    assert first.verdict == results.NO_MISS, said[-2000:]
    questions = folder / "visits-questions.json"
    for _round in range(4):
        if not _answered_as_the_person(questions, "pid"):
            break
        again, said = _ran(["profile", str(table), "--answers", str(questions), "--replace-description"])
        assert again.verdict == results.NO_MISS, said[-2000:]
    profile_path = folder / "visits-profile.json"
    described = json.loads(profile_path.read_text(encoding="utf-8"))
    return table, profile_path, described


def _checked(
    monkeypatch: pytest.MonkeyPatch, profile_path: pathlib.Path, measured: pathlib.Path
) -> "list[validation.Check]":
    """`synthtwin validate` of one file against the description: the outcome's checks."""
    outcomes: "list[validation.Outcome]" = []
    measure = validation.measure

    def kept(*given: object, **named: object) -> validation.Outcome:
        outcome = measure(*given, **named)  # type: ignore[arg-type]
        outcomes.extend([outcome])
        return outcome

    monkeypatch.setattr(validation, "measure", kept)
    done, said = _ran(["validate", str(profile_path), "--twin", str(measured)])
    monkeypatch.setattr(validation, "measure", measure)
    assert done.verdict in (results.NO_MISS, results.MISSED), said[-3000:]
    assert len(outcomes) == 1, said[-2000:]
    return list(outcomes[0].checks)


def _patient_fixed(described: "dict[str, object]") -> "list[str]":
    grain = described["relationships"]["grain"]  # type: ignore[index]
    return sorted(entry["column"] for entry in grain["classes"] if entry["class"] == "patient_fixed")  # type: ignore[index]


def test_codex_s_visits_stored_newest_first_meet_their_own_patient_fixed_site(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Codex's table (batch 4u's outside review, item 3), at the table floor, through the shipped commands.

    20,000 rows, 2,000 patients: 1,000 of five visits and 1,000 of fifteen,
    each patient's visits stored newest first; the column `site` A or B by
    patient, alternating, and one A patient's newest visit written B. The
    producer reads `site` at each patient's first position (its oldest
    visit) and publishes it patient-fixed. The real table, checked against
    its own description, misses no check of the person column or of `site`;
    nor does its twin. On the reviewed head the checks of `site` read the stored
    first row, the newest visit, and four of them read MISSED (A 999 and B
    1,001 against the published 1,000 and 1,000). MUTANT: the validator's
    patient rows taken in stored order (`patients_first_rows` handed no
    position readings).
    """
    monkeypatch.setattr(cli, "_PATIENT_LAYER_SHIPPED", True)
    counts = [5] * 1000 + [15] * 1000
    sites = ["A" if p % 2 == 0 else "B" for p in range(2000)]
    text = _visits_text(counts, sites, [0], 7, newest_first=True)
    table, profile_path, described = _described_with_grain(tmp_path / "codex", text)
    grain = described["relationships"]["grain"]  # type: ignore[index]
    assert isinstance(grain, dict) and grain["person"] == "pid" and grain["position"] == "visit_date", grain
    assert "site" in _patient_fixed(described), grain["classes"]
    counted = ["pid", *_patient_fixed(described)]
    checks = _checked(monkeypatch, profile_path, table)
    missed = [(check.column, check.fact, check.subcheck) for check in checks if check.column in counted and check.verdict == validation.MISSED]
    held = [check for check in checks if check.column in counted and check.verdict == validation.HELD]
    assert missed == [] and len(held) >= 10 * len(counted), (missed, len(held))
    made, said = _ran(["generate", str(profile_path)])
    assert made.verdict in (results.NO_MISS, results.MISSED), said[-2000:]
    twin_checks = _checked(monkeypatch, profile_path, tmp_path / "codex" / "visits-twin.csv")
    twin_missed = [(check.column, check.fact, check.subcheck) for check in twin_checks if check.column in counted and check.verdict == validation.MISSED]
    assert twin_missed == [], twin_missed


@pytest.mark.parametrize("seed", [11, 12])
def test_generated_visits_in_any_stored_order_meet_their_patient_fixed_columns(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, seed: int
) -> None:
    """GENERATED tables at the table floor: about 1,400 patients of 2 to 25 visits, every row in a drawn order.

    The column `site` is fixed for each patient but 3 to 8 of value A, each with its
    newest visit written B and standing before its other visits (fewer
    than the producer's allowance of patients holding two cells, so the
    column stays patient-fixed). The real table, checked against its own
    description, misses no check of the person column or of a
    patient-fixed column; on the reviewed head the counts of `site` read the
    newest visits and are missed. MUTANT: as Codex's table's.
    """
    monkeypatch.setattr(cli, "_PATIENT_LAYER_SHIPPED", True)
    draw = random.Random(seed)
    counts: "list[int]" = []
    while sum(counts) < 20_000:
        counts += [draw.randint(2, 25)]
    sites = [draw.choice(["A", "B"]) for _p in counts]
    odd = draw.sample([p for p in range(len(counts)) if sites[p] == "A"], draw.randint(3, 8))
    text = _visits_text(counts, sites, odd, seed, newest_first=False)
    table, profile_path, described = _described_with_grain(tmp_path / f"g{seed}", text)
    grain = described["relationships"]["grain"]  # type: ignore[index]
    assert isinstance(grain, dict) and grain["position"] == "visit_date", grain
    counted = ["pid", *_patient_fixed(described)]
    assert "site" in counted, grain["classes"]
    checks = _checked(monkeypatch, profile_path, table)
    missed = [(check.column, check.fact, check.subcheck) for check in checks if check.column in counted and check.verdict == validation.MISSED]
    assert missed == [], missed


def test_the_patients_first_rows_follow_the_position_readings_ties_and_absent_by_row_order(tmp_path: pathlib.Path) -> None:
    """GENERATED: 400 small tables of 3 to 40 patients in a drawn row order, a reading for each row (some absent, some tied).

    `patients_first_rows` handed the position readings takes, for each
    patient in the order it first stands, the row of its least reading,
    ties by row order, and a patient with no reading its first row; handed
    none, the first stored row, as before. MUTANT: the readings set aside.
    """
    draw = random.Random(4003)
    for case in range(400):
        patients = draw.randint(3, 40)
        owner: "list[int]" = []
        for p in range(patients):
            owner += [p] * draw.randint(1, 6)
        draw.shuffle(owner)
        stamps: "list[object]" = [None if draw.random() < 0.15 else draw.randint(0, 9) for _row in owner]
        path = fixtures.write(tmp_path, f"t{case}.csv", "pid,x\n" + "".join(f"Q{p},{row}\n" for row, p in enumerate(owner)))
        table = reading.read_table(str(path))
        expected: "list[int]" = []
        firsts: "list[int]" = []
        seen: "dict[int, bool]" = {}
        for row in range(len(owner)):
            p = owner[row]
            if p in seen:
                continue
            seen[p] = True
            rows = [one for one in range(len(owner)) if owner[one] == p]
            present = sorted((int(f"{stamps[one]}"), one) for one in rows if stamps[one] is not None)
            expected += [present[0][1] if present else rows[0]]
            firsts += [row]
        assert chain_validation.patients_first_rows(table, {}, "pid", stamps) == expected, case
        assert chain_validation.patients_first_rows(table, {}, "pid") == firsts, case


# -- item 5: the trend close adds and takes away a holder in bounded work


class _Moved(list):  # type: ignore[type-arg]
    """A holder list whose work is counted: each entry read, and each entry a slice or a deletion shifts."""

    work = 0

    def __getitem__(self, at):  # type: ignore[no-untyped-def]
        _Moved.work += 1
        return list.__getitem__(self, at)

    def __iter__(self):  # type: ignore[no-untyped-def]
        for one in list.__iter__(self):
            _Moved.work += 1
            yield one

    def __setitem__(self, at, value):  # type: ignore[no-untyped-def]
        if isinstance(at, slice):
            start = at.start if at.start is not None else 0
            _Moved.work += len(self) - start + len(value)
        else:
            _Moved.work += 1
        list.__setitem__(self, at, value)

    def __delitem__(self, at):  # type: ignore[no-untyped-def]
        _Moved.work += len(self) - (at if isinstance(at, int) and at >= 0 else 0)
        list.__delitem__(self, at)


def _counted_close(monkeypatch: pytest.MonkeyPatch, codes: "list[int]", rho: int, count: int, window: "tuple[int, int]") -> "tuple[int, int, list[int]]":
    """`_exact_close` on one cell of `count` patients of `rho` rows: its `S_P`, the work its holders did, the codes after it."""
    from synthtwin import patient_walk

    real = patient_walk._hold

    def counted(holders, held, p):  # type: ignore[no-untyped-def]
        real(holders, held, p)
        for step in held:
            if step not in holders:
                continue
            if type(holders[step]) is list:
                holders[step] = _Moved(holders[step])
            elif type(getattr(holders[step], "heap", None)) is list:
                holders[step].heap = _Moved(holders[step].heap)

    monkeypatch.setattr(patient_walk, "_hold", counted)
    cells = [f"{code}" for code in codes]
    patients = patient_walk._Patients(count, {}, {}, [rho] * count, [rho * p for p in range(count)])
    total = sum(patient_walk._s_of(codes[rho * p:rho * p + rho]) for p in range(count))
    _Moved.work = 0
    got = patient_walk._exact_close(cells, codes, list(range(count)), patients, rho, total, window)
    monkeypatch.setattr(patient_walk, "_hold", real)
    assert cells == [f"{code}" for code in codes]
    return got, _Moved.work, codes


def test_codex_s_three_row_patients_close_in_work_that_grows_with_the_rows(monkeypatch: pytest.MonkeyPatch) -> None:
    """Codex's shape (batch 4u's outside review, item 5): `N` three-row patients of codes `(0, 0, 1)`, `S_P = 2 N`, window `[0, 0]`.

    The close takes a patient's 1 to its first row, the least patient a
    round (each move takes 4 off `S_P`, so the lower half of the patients
    move); each patient moved leaves the holders of its two steps and joins
    two others. The work its holders do (each entry read, and each entry a
    list shifts) at `N` = 2,000, 4,000 and 8,000 grows as the rows do (at
    most 2.6 times a doubling: a heap's reads grow as `N log N`), and the
    cell is met with the lower half at `(1, 0, 0)`. On the reviewed head
    each patient taken from the front of an ascending list shifted every
    later entry, and the work grew four times a doubling (the 157.9 CPU
    seconds Codex measured at 2,000,001 rows against 2.075 at 200,001).
    MUTANT: each step's holders an ascending list again.
    """
    work: "dict[int, int]" = {}
    for count in (2000, 4000, 8000):
        got, work[count], codes = _counted_close(monkeypatch, [0, 0, 1] * count, 3, count, (0, 0))
        assert got == 0 and codes == [1, 0, 0] * (count // 2) + [0, 0, 1] * (count // 2), got
    assert work[8000] <= 2.6 * work[4000] and work[4000] <= 2.6 * work[2000], work


@pytest.mark.parametrize("seed", [31, 32])
def test_generated_cells_close_in_work_that_grows_with_the_rows(monkeypatch: pytest.MonkeyPatch, seed: int) -> None:
    """GENERATED cells: `N` patients of `rho` rows (3 to 6), codes of 0 and 1, so every step is held by many patients.

    A window drawn below `S_P`, the same for each size, so the close moves
    patients a round each. The work the holders do grows at most 2.6 times
    when `N` doubles from 1,500 to 3,000 and from 3,000 to 6,000, and at
    1,500 the close's `S_P` and codes equal those of the lowest-patient
    reference tests/test_stage6_patient_generate.py holds. MUTANT: as
    Codex's shape's.
    """
    from test_stage6_patient_generate import _lowest_patient_close

    from synthtwin import patient_walk

    draw = random.Random(seed)
    rho = draw.randint(3, 6)
    pattern = [draw.randint(0, 1) for _k in range(rho)]
    if sum(pattern) in (0, rho):
        pattern[0] = 1 - pattern[0]
    work: "dict[int, int]" = {}
    for count in (1500, 3000, 6000):
        codes = []
        for _p in range(count):
            mine = list(pattern)
            draw.shuffle(mine)
            codes += mine
        total = sum(patient_walk._s_of(codes[rho * p:rho * p + rho]) for p in range(count))
        window = (total - 2 * count, total - 2 * count)
        expected_codes = list(codes)
        got, work[count], after = _counted_close(monkeypatch, codes, rho, count, window)
        if count == 1500:
            patients = patient_walk._Patients(count, {}, {}, [rho] * count, [rho * p for p in range(count)])
            expected = _lowest_patient_close([f"{c}" for c in expected_codes], expected_codes, list(range(count)), patients, rho, total, window)
            assert (got, after) == (expected, expected_codes)
    assert work[6000] <= 2.6 * work[3000] and work[3000] <= 2.6 * work[1500], work


# -- item 8: the report beside a chained twin states lane CHG's measured figures


def _clinic_text(rows: int, seed: int) -> str:
    """An invented clinic: an age, a gender, a group that follows age, a pressure that follows age, an event."""
    draw = random.Random(seed)
    lines = ["age,gender,group,pressure,event"]
    for _row in range(rows):
        age = draw.randint(18, 88)
        gender = draw.choice(["f", "m"])
        group = draw.choice(["a", "b", "c"]) if age < 50 else draw.choice(["c", "d"])
        pressure = f"{round(100 + age * 0.5 + draw.gauss(0, 8), 1)}"
        event = "1" if draw.random() < 0.05 + age / 120 else "0"
        lines += [f"{age},{gender},{group},{pressure},{event}"]
    return "\n".join(lines) + "\n"


def _chained_report(folder: pathlib.Path, rows: int, seed: int) -> str:
    """The clinic described over two rounds (the subject question answered `one row each`), its twin made; the twin's report."""
    folder.mkdir(parents=True, exist_ok=True)
    table = fixtures.write(folder, "clinic.csv", _clinic_text(rows, seed))
    first, said = _ran(["profile", str(table)])
    assert first.verdict == results.NO_MISS, said[-2000:]
    questions = folder / "clinic-questions.json"
    document = json.loads(questions.read_text(encoding="utf-8"))
    document[asking.BETWEEN_COLUMNS][asking.ROWS_PER_PERSON]["your_answer"] = asking.ANSWER_ONE_ROW_EACH
    questions.write_text(json.dumps(document, indent=1) + "\n", encoding="utf-8", newline="\n")
    second, said = _ran(["profile", str(table), "--answers", str(questions), "--replace-description"])
    assert second.verdict == results.NO_MISS, said[-2000:]
    described = json.loads((folder / "clinic-profile.json").read_text(encoding="utf-8"))
    assert described["relationships"]["statistical"] is not None, said[-2000:]
    made, said = _ran(["generate", str(folder / "clinic-profile.json")])
    assert made.verdict in (results.NO_MISS, results.MISSED), said[-2000:]
    return (folder / "clinic-twin-report.txt").read_text(encoding="utf-8")


_MEASURED = ("about one pair of columns in thirteen", "one in ten at the most", "about one in thirty-five", "about 14 to 16 in 100", "(about 10 on a fresh sample)")
_BEFORE = ("columns in seven", "17 in 100", "one in twenty")


def test_a_chained_twin_s_report_states_the_grouping_gate_s_measured_figures(tmp_path: pathlib.Path) -> None:
    """Codex's item 8: the report beside a chained twin states lane CHG's figures, measured with its grouping gate (P4-D492).

    About one pair of unrelated columns in thirteen called related, one in
    ten at the most, against about one in thirty-five on a fresh sample;
    about 14 to 16 in 100 effects that are not significant come out
    significant, against about 10. The reviewed head still stated the
    figures measured before the gate (one pair in seven; 17 in 100 against
    9). MUTANT: the words before the gate restored.
    """
    report = _chained_report(tmp_path / "clinic", 1200, 7)
    for words in _MEASURED:
        assert words in report, words
    for words in _BEFORE:
        assert words not in report, words


@pytest.mark.parametrize("seed", [21, 22, 23])
def test_every_generated_chained_twin_s_report_carries_the_measured_figures_and_no_other_twin_s(
    tmp_path: pathlib.Path, seed: int
) -> None:
    """GENERATED clinics of 1,000 to 3,000 rows: each chained twin's report carries the measured paragraph whole, once.

    And the twin of the same table described by the internal unswitched
    setting carries none of it (its columns were built on their own).
    MUTANT: as the case before.
    """
    from synthtwin import rendering

    draw = random.Random(seed)
    rows = draw.randint(1000, 3000)
    report = _chained_report(tmp_path / "chained", rows, seed)
    paragraph = "\n".join(rendering._INVENTED_RELATIONSHIPS)
    assert report.count(paragraph) == 1
    for words in _MEASURED:
        assert words in paragraph, words
    plain = tmp_path / "plain"
    plain.mkdir()
    table = fixtures.write(plain, "clinic.csv", _clinic_text(rows, seed))
    screen: "list[tuple[str, str]]" = []
    made = cli.run(["profile", str(table)], screen=screen, unswitched=True)
    assert made.verdict == results.NO_MISS
    built = cli.run(["generate", str(plain / "clinic-profile.json")], screen=screen, unswitched=True)
    assert built.verdict in (results.NO_MISS, results.MISSED)
    unswitched = (plain / "clinic-twin-report.txt").read_text(encoding="utf-8")
    assert rendering._INVENTED_RELATIONSHIPS[0] not in unswitched
    for words in _MEASURED:
        assert words not in unswitched, words
