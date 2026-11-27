"""Batch 4u's outside review, items 1, 2 and 4: the chain's rule steps, the locality gate and the band index.

ITEM 1 (a real date count written by an order rule). The rule steps read
a candidate column `B` on the file's own cells. A column whose values
read as dates, answered `yes` to its date question, is described with
those values as blank cells (plan P4-D446) and its block left `empty`;
an order rule then computed it again from an ordinary amount beside it,
and on the review's table at 20,000 rows the twin wrote 19,908 of its
20,000 cells equal to a real date count (the review measured 19,995 on
its own walk). `chain_order.computed_refused` now refuses such a block:
the dated-values remark, the role `empty`, a withheld present count.

ITEM 2 (a shared network location looked up before the locality gate).
The switched `profile` resolved the data folder, the table and the
output folder before `validate_local_path` read them, so a table on a
shared network location, or a data folder there, was looked up before
any refusal. The gate now reads every path as typed, first.

ITEM 4 (quadratic work before the size guard's selection). Each starting
band's `L0` band was found by scanning every `L0` band for every
starting band, in the chain's reading of a column and in
`chain_rules.small_group_bands`; `chain_rules.l0_of_starts` reads an
index of the names instead, with the scan's answer place for place.

Each case was run red on the reviewed head 3d534e76 and on its mutant
(the change reverted): item 1's on the refusal removed, item 2's on the
gate removed, item 4's on the index replaced by the scan.
"""

import csv
import json
import pathlib
import random

import pytest

import fixtures
from synthtwin import asking, chain_order, chain_rules, cli, installation, results, taxonomy


def _ran(argv: "list[str]") -> "tuple[str, str]":
    """One command line through `cli.run`: its verdict and every character its screen showed."""
    screen: "list[tuple[str, str]]" = []
    made = cli.run(argv, screen=screen)
    return made.verdict, "".join(text for _stream, text in screen)


# -- ITEM 1: A COLUMN OF DATES HELD IS NEVER COMPUTED BACK ------------------


def _dated_beside_amount(rows: int, base: int, step: int, offsets: int, seed: int) -> str:
    """An amount of five figures with one decimal, and a column of the same amounts plus a tenth to a day."""
    draw = random.Random(seed)
    lines = ["amount,visit_day_number,group"]
    for row in range(rows):
        amount = base + (row % step) / 10
        later = amount + (1 + (row // step) % offsets) / 10
        lines += [f"{amount:.1f},{later:.1f},{draw.choice(['a', 'b'])}"]
    return "\n".join(lines) + "\n"


def _walked(folder: pathlib.Path, text: str) -> "tuple[dict[str, object], list[dict[str, str]], set[str]]":
    """The table through the shipped commands: the amount's date question `no`, the date column's `yes`, the subject question `one row each` where it is put; then `generate --seed 7`."""
    folder.mkdir(parents=True, exist_ok=True)
    table = fixtures.write(folder, "visits.csv", text)
    questions = folder / "visits-questions.json"
    verdict, said = _ran(["profile", str(table)])
    assert verdict == results.NO_MISS, said[-2000:]
    for _round in range(3):
        document = json.loads(questions.read_text(encoding="utf-8"))
        changed = False
        for entry in document["asked"]:
            wanted = {"amount": "no", "visit_day_number": "yes"}.get(f"{entry.get('column')}")
            if wanted is not None and entry["your_answer"] != wanted:
                entry["your_answer"] = wanted
                changed = True
        between = document[asking.BETWEEN_COLUMNS] if asking.BETWEEN_COLUMNS in document else {}
        if (
            isinstance(between, dict)
            and asking.ROWS_PER_PERSON in between
            and between[asking.ROWS_PER_PERSON]["your_answer"] != asking.ANSWER_ONE_ROW_EACH
        ):
            between[asking.ROWS_PER_PERSON]["your_answer"] = asking.ANSWER_ONE_ROW_EACH
            changed = True
        if not changed:
            break
        questions.write_text(json.dumps(document, indent=1) + "\n", encoding="utf-8", newline="\n")
        verdict, said = _ran(["profile", str(table), "--answers", str(questions), "--replace-description"])
        assert verdict == results.NO_MISS, said[-2000:]
    profile_path = folder / "visits-profile.json"
    described = json.loads(profile_path.read_text(encoding="utf-8"))
    _verdict, said = _ran(["generate", str(profile_path), "--seed", "7"])
    twin_path = folder / "visits-twin.csv"
    assert twin_path.is_file(), said[-2000:]
    with open(table, encoding="utf-8", newline="") as handle:
        real = {row["visit_day_number"] for row in csv.DictReader(handle)}
    with open(twin_path, encoding="utf-8", newline="") as handle:
        twin = list(csv.DictReader(handle))
    return described, twin, real


def _computed(described: "dict[str, object]") -> "list[object]":
    relationships = described["relationships"]
    statistical = relationships["statistical"] if isinstance(relationships, dict) else None
    rules = statistical["rules"] if isinstance(statistical, dict) and "rules" in statistical else []
    return [rule["computed"] for rule in rules if isinstance(rule, dict) and "computed" in rule]


def test_the_reviews_table_writes_no_real_date_count(tmp_path: pathlib.Path) -> None:
    """The review's own table at 20,000 rows: no rule computes the held column, no twin cell equals a real date count.

    On 3d534e76: an order rule computed `visit_day_number` from `amount`
    and the twin wrote 20,000 present cells, 19,908 equal to a real one.
    MUTANT: `computed_refused` without the date hold.
    """
    text = _dated_beside_amount(20000, 45000, 500, 10, 3)
    described, twin, real = _walked(tmp_path / "review", text)
    assert "visit_day_number" not in _computed(described)
    present = [row["visit_day_number"] for row in twin if row["visit_day_number"].strip()]
    assert [cell for cell in present if cell in real] == []
    assert len(twin) == 20000


@pytest.mark.parametrize("seed", [11, 12])
def test_drawn_tables_of_dates_beside_an_amount_write_no_real_date_count(tmp_path: pathlib.Path, seed: int) -> None:
    """Generated tables of the same shape, their day counts, steps and offsets drawn: no real date count written.

    MUTANT: `computed_refused` without the date hold.
    """
    draw = random.Random(seed)
    text = _dated_beside_amount(20000, draw.randint(40000, 47000), draw.choice([250, 400, 500]), draw.randint(4, 12), seed)
    described, twin, real = _walked(tmp_path / f"drawn{seed}", text)
    assert "visit_day_number" not in _computed(described)
    assert [row["visit_day_number"] for row in twin if row["visit_day_number"] in real] == []


def test_the_rule_steps_refuse_a_held_or_emptied_block_as_the_computed_column() -> None:
    """`computed_refused`'s three readings of a hold, each alone, beside an ordinary block it admits."""
    remark = taxonomy.rendered(taxonomy.REMARK_DATED_VALUES_HELD, ())
    ordinary: "dict[str, object]" = {"name": "later", "role": "continuous", "n_present": 20000, "remarks": []}
    assert not chain_order.computed_refused(ordinary, set(), set())
    assert chain_order.computed_refused(dict(ordinary, remarks=[remark]), set(), set())
    assert chain_order.computed_refused(dict(ordinary, role=taxonomy.ROLE_EMPTY, n_present=0), set(), set())
    assert chain_order.computed_refused(dict(ordinary, n_present=None), set(), set())


# -- ITEM 2: THE LOCALITY GATE BEFORE ANY LOOK-UP ----------------------------


def _watched(monkeypatch: pytest.MonkeyPatch) -> "list[str]":
    """Every path `pathlib.Path.resolve` is asked for whose text names the shared location."""
    asked: "list[str]" = []
    resolve = pathlib.Path.resolve

    def watched(self: pathlib.Path, strict: bool = False) -> pathlib.Path:
        if "review-host" in f"{self}":
            asked.append(f"{self}")
        return resolve(self, strict=strict)

    monkeypatch.setattr(pathlib.Path, "resolve", watched)
    return asked


def test_a_data_folder_on_a_shared_network_location_is_refused_before_it_is_looked_up(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The data folder named by the environment on `//review-host/share`: refused in words, never resolved or opened.

    MUTANT: the gate removed (the folder resolved, then opened).
    """
    (tmp_path / "local").mkdir()
    table = fixtures.write(tmp_path / "local", "cohort.csv", "a,b\n1,2\n3,4\n")
    for name in ("XDG_DATA_HOME", "LOCALAPPDATA"):
        monkeypatch.setenv(name, "//review-host/share")
    opened: "list[str]" = []
    monkeypatch.setattr(installation, "open_installation", lambda folder, *a, **k: opened.append(f"{folder}"))
    asked = _watched(monkeypatch)
    verdict, said = _ran(["profile", str(table)])
    assert verdict == results.REFUSED
    assert "is not a plain folder on this computer" in said
    assert asked == [] and opened == []


@pytest.mark.parametrize(
    "written",
    ["\\\\review-host\\share\\cohort.csv", "//review-host/share/cohort.csv"],
)
def test_a_table_on_a_shared_network_location_is_refused_before_it_is_looked_up(
    monkeypatch: pytest.MonkeyPatch, written: str
) -> None:
    """A table named on a shared network location: the run refuses it in the gate's words, and nothing resolved it.

    MUTANT: the gate removed (the table's folder resolved first).
    """
    asked = _watched(monkeypatch)
    verdict, said = _ran(["profile", written])
    assert verdict == results.REFUSED
    assert "shared network location" in said
    assert asked == []


# -- ITEM 4: THE BAND INDEX -------------------------------------------------


def _scanned(names: "tuple[object, ...]", l0: "tuple[tuple[object, ...], ...]") -> "dict[int, int]":
    """The scan the index replaced: for each place, the last `L0` band one of whose names equals its name."""
    found: "dict[int, int]" = {}
    for at in range(len(l0)):
        for place in range(len(names)):
            if names[place] in l0[at]:
                found[place] = at
    return found


def _drawn_name(draw: random.Random) -> object:
    kind = draw.randint(0, 5)
    if kind == 0:
        return f"w{draw.randint(0, 30)}"
    if kind == 1:
        return [draw.choice([None, "r1", "r2", "r3"]), draw.choice([None, "r4", "r5"])]
    if kind == 2:
        return [draw.choice(["x", "y", 3, 4.0])]
    if kind == 3:
        return (draw.choice(["x", "y", "list"]),)
    if kind == 4:
        return draw.randint(0, 9)
    return draw.choice(["pool", "list", "tuple"])


@pytest.mark.parametrize("seed", range(40))
def test_the_index_gives_the_scans_answer_place_for_place(seed: int) -> None:
    """Drawn names (words, ranges and levels as lists, tuples, numbers), some in several bands and some in none."""
    draw = random.Random(seed)
    names = tuple(_drawn_name(draw) for _place in range(draw.randint(1, 60)))
    l0 = tuple(
        tuple(draw.choice(names) if draw.random() < 0.8 else _drawn_name(draw) for _member in range(draw.randint(1, 4)))
        for _band in range(draw.randint(1, 40))
    )
    assert chain_rules.l0_of_starts(names, l0) == _scanned(names, l0)


class _Counted:
    """A name that counts every comparison made of it."""

    made = 0

    def __init__(self, value: int) -> None:
        self.value = value

    def __eq__(self, other: object) -> bool:
        _Counted.made += 1
        return isinstance(other, _Counted) and other.value == self.value

    def __hash__(self) -> int:
        return hash(self.value)


def test_the_index_compares_each_name_a_bounded_number_of_times() -> None:
    """1,500 starting bands, each its own `L0` band: at most three comparisons a name (the scan makes 1,500 a name).

    MUTANT: the index replaced by the scan (2,250,000 comparisons).
    """
    size = 1500
    names = tuple(_Counted(value) for value in range(size))
    l0 = tuple((_Counted(value),) for value in reversed(range(size)))
    _Counted.made = 0
    found = chain_rules.l0_of_starts(names, l0)
    assert _Counted.made <= 3 * size
    assert found == {place: size - 1 - place for place in range(size)}


def test_a_name_no_index_may_hold_is_read_by_the_scan() -> None:
    """A name that cannot be a key of an index: the scan's answer, never an error."""
    names: "tuple[object, ...]" = ({"a": 1}, "w")
    l0: "tuple[tuple[object, ...], ...]" = (("w",), ({"a": 1},))
    assert chain_rules.l0_of_starts(names, l0) == {0: 1, 1: 0}

