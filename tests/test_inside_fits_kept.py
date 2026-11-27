"""Gate file of lane SPEED-2M, part 1: the relations zone's fits kept between rounds, the zone the same bytes.

THE FITS KEPT. A person who answers the questions file describes the
table again, and each round refitted the whole relations zone (about an
hour a round at the fit's 200,000 rows). Each round's screen statistics
and models are now kept beside the record (`inside_relations.KeptFits`,
the command's `_fits_kept_read` and `_fits_kept_written`), each under a
digest of everything it was made from, and a later round takes a fit
only where every input is the same.

WHAT IT HOLDS THEM TO, each clause red on its mutant (scripts/mutants.py
of the lane's notes):

* A zone fitted with fits kept, and again with the first round's fits
  held, is the zone fitted with none, byte for byte, and the second
  round makes no fit (mutant: the second round reads none held).
* A column changed between the rounds: the zone is the one a fit of the
  changed table with none kept makes, byte for byte, while the columns
  that do not read the change are taken (mutants: a statistic's key
  without its parent's; a model's key without the parents chosen; a
  column's key without its values; the key without the rows' persons).
* The persons changed between the rounds: the zone is the fresh fit's.
* Through the command: a table described twice writes the same record,
  byte for byte, the second time taking every fit; the fits sit beside
  the record carrying its protected marker, its mode 0600; a second
  description with a column declared otherwise writes the record a
  description with nothing kept writes (mutant: the fits written are
  never read).

Every table here is drawn by the standard library's `random` from a
seed, at run time; nothing is committed.
"""

from __future__ import annotations

import json
import math
import os
import pathlib
import random
import stat
import sys
import typing

import pytest

from synthtwin import inside, inside_relations as R

NUMBER, LABEL = R.NUMBER, R.LABEL


def _table(people: int, seed: int) -> "dict[str, list[str]]":
    """An invented visits table: a person's arm (one value a person), a visit count, flags, numbers and a label moved by them."""
    r = random.Random(f"fits-kept-{seed}")
    out: "dict[str, list[str]]" = {name: [] for name in ("pid", "arm", "visit", "f1", "x", "y", "z", "w")}
    for person in range(people):
        arm = r.random() < 0.4
        share = r.gauss(0.0, 1.0)
        for visit in range(1 + r.randrange(8)):
            f1 = r.random() < (0.6 if arm else 0.3)
            x = 0.8 * f1 + share + r.gauss(0.0, 1.0)
            y = 0.5 * x * x - x + r.gauss(0.0, 0.7)
            u = r.random() + 0.15 * x + 0.2 * (f1 and x > 0)
            z = "a" if u < 0.35 else "b" if u < 0.65 else "c" if u < 0.9 else "d"
            w = 0.0 if r.random() < (0.5 if z == "a" else 0.2) else abs(r.gauss(2.0 + x, 1.0))
            out["pid"] += [f"P{person:05d}"]
            out["arm"] += ["T" if arm else "C"]
            out["visit"] += [f"{visit + 1}"]
            out["f1"] += ["Y" if f1 else "N"]
            out["x"] += [f"{x:.2f}"]
            out["y"] += ["" if r.random() < 0.03 else f"{y:.2f}"]
            out["z"] += [z]
            out["w"] += [f"{w:.1f}"]
    return out


KINDS = {"arm": LABEL, "visit": NUMBER, "f1": LABEL, "x": NUMBER, "y": NUMBER, "z": LABEL, "w": NUMBER}


def _encoded(columns: "dict[str, list[str]]", person: str = "pid") -> "tuple[list[R.Encoded], int, int, list[int] | None]":
    names = list(columns)
    rows = len(columns[names[0]])
    persons = R.persons_of(columns[person]) if person else None
    if persons is not None and not persons.repeats:
        persons = None
    sample = R.sample_rows(rows, persons=persons)
    encoded = []
    for place, name in enumerate(names):
        kind = KINDS.get(name, "")
        spellings = tuple(sorted(set(columns[name]))) if kind == LABEL else ()
        why = "" if kind else R.NAMES_THE_PERSON
        found = R.encode(R.ColumnSpec(name, place, kind, 0, spellings, why), columns[name], sample, persons)
        if found is not None:
            encoded.append(found)
    owners = [persons.person[row] for row in sample] if persons is not None else None
    return encoded, len(sample), rows, owners


def _fitted(columns: "dict[str, list[str]]", kept: "R.KeptFits | None", person: str = "pid") -> str:
    encoded, sample, rows, owners = _encoded(columns, person)
    zone = R.fit_zone(encoded, sample, rows, owners, person, None, kept)
    return json.dumps(zone, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _held(kept: "R.KeptFits") -> "R.KeptFits":
    """The fits a round made, as the next round reads them back: through their JSON, as the file holds them."""
    stats = json.loads(json.dumps(kept.made_stats, allow_nan=False))
    models = json.loads(json.dumps(kept.made_models, allow_nan=False))
    return R.KeptFits(held_stats=stats, held_models=models)


@pytest.fixture(scope="module")
def fresh() -> "dict[str, typing.Any]":
    columns = _table(700, 1)
    first = R.KeptFits()
    return {"columns": columns, "none": _fitted(columns, None), "first": first, "kept": _fitted(columns, first)}


def test_a_zone_fitted_with_fits_kept_is_the_zone_fitted_with_none(fresh: "dict[str, typing.Any]") -> None:
    assert fresh["kept"] == fresh["none"]
    first = fresh["first"]
    assert first.taken == 0 and first.fitted > 20, (first.taken, first.fitted)
    again = _held(first)
    assert _fitted(fresh["columns"], again) == fresh["none"]
    assert again.fitted == 0, again.fitted
    assert again.taken == first.fitted, (again.taken, first.fitted)
    # ...and what the second round keeps is what the first made: the file never grows.
    assert sorted(again.made_stats) == sorted(first.made_stats)
    assert sorted(again.made_models) == sorted(first.made_models)


def test_a_column_changed_between_rounds_is_refitted_and_the_zone_is_the_fresh_one(
        fresh: "dict[str, typing.Any]") -> None:
    changed = {name: list(cells) for name, cells in fresh["columns"].items()}
    r = random.Random("changed")
    # `f1` changed on a tenth of its rows: every later column reads it, the earlier ones do not.
    changed["f1"] = [("N" if cell == "Y" else "Y") if r.random() < 0.1 else cell for cell in changed["f1"]]
    held = _held(fresh["first"])
    assert _fitted(changed, held) == _fitted(changed, None)
    assert held.taken > 0 and held.fitted > 0, (held.taken, held.fitted)
    # A number changed in its last column: only its own fits are made again (two targets, each screening the six
    # columns before it, and their two models), every other one taken.
    late = {name: list(cells) for name, cells in fresh["columns"].items()}
    late["w"] = [f"{float(cell) + 0.1:.1f}" if place % 7 == 0 else cell for place, cell in enumerate(late["w"])]
    held = _held(fresh["first"])
    assert _fitted(late, held) == _fitted(late, None)
    assert 0 < held.fitted <= 2 * 6 + 2 and held.taken == fresh["first"].fitted - held.fitted, (held.taken, held.fitted)


def test_a_column_whose_rows_are_reordered_is_refitted(fresh: "dict[str, typing.Any]") -> None:
    # `w`'s numbers above its spike at nought moved among their own rows: the same values, so the same entry (grid,
    # counts), and the same state on every row, each number on another row.
    moved = {name: list(cells) for name, cells in fresh["columns"].items()}
    places = [place for place, cell in enumerate(moved["w"]) if cell != "0.0"]
    numbers = [moved["w"][place] for place in places]
    random.Random("reordered").shuffle(numbers)
    for place, cell in zip(places, numbers):
        moved["w"][place] = cell
    held = _held(fresh["first"])
    assert _fitted(moved, held) == _fitted(moved, None)
    assert held.fitted > 0


def test_a_change_in_a_column_no_response_chooses_keeps_the_others_models(fresh: "dict[str, typing.Any]") -> None:
    # `visit` (a sequence, fitted on nothing) shifted by one: a parent every later response screens.
    moved = {name: list(cells) for name, cells in fresh["columns"].items()}
    moved["visit"] = [f"{int(cell) + 1}" for cell in moved["visit"]]
    held = _held(fresh["first"])
    assert _fitted(moved, held) == _fitted(moved, None)


def test_the_persons_changed_between_rounds_give_the_fresh_zone(fresh: "dict[str, typing.Any]") -> None:
    regrouped = {name: list(cells) for name, cells in fresh["columns"].items()}
    regrouped["pid"] = [f"Q{place // 3:05d}" for place in range(len(regrouped["pid"]))]
    held = _held(fresh["first"])
    assert _fitted(regrouped, held) == _fitted(regrouped, None)


# -- through the command ------------------------------------------------------------------------------------------

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(pathlib.Path(REPO_ROOT, "tools", "measurements")))


def _dense(path: pathlib.Path, rows: int, columns: int) -> None:
    import kpi_inside_scale

    kpi_inside_scale.write_dense(rows, columns, path)


def _profile(folder: pathlib.Path, table: pathlib.Path, extra: "list[str]",
             monkeypatch: "pytest.MonkeyPatch") -> "tuple[bytes, R.KeptFits, pathlib.Path]":
    """`synthtwin profile` of ``table`` into ``folder``/out, the record in the test's data folder; the record, the fits, its path."""
    import contextlib
    import io

    from synthtwin import cli, installation

    def places() -> inside.Places:
        return inside.Places(pathlib.Path(installation.data_folder(), inside.FOLDER), (), (), installation.system_name())

    seen: "list[R.KeptFits]" = []
    original = R.fit_zone

    def watched(*args: typing.Any, **kwargs: typing.Any) -> "dict[str, object]":
        kept = args[6] if len(args) > 6 else kwargs.get("kept")
        if isinstance(kept, R.KeptFits):
            seen.append(kept)
        return original(*args, **kwargs)

    monkeypatch.setattr(inside, "default_places", places)
    monkeypatch.setattr(R, "fit_zone", watched)
    out = pathlib.Path(folder, "out")
    out.mkdir(parents=True, exist_ok=True)
    said = io.StringIO()
    with contextlib.redirect_stdout(said), contextlib.redirect_stderr(said):
        code = cli.main(["profile", f"{table}", "--out-dir", f"{out}", "--replace", "--person", "pid",
                         "--identifier", "code", *extra])
    assert code == 0, said.getvalue()[-3000:]
    record = cli._inside_record_at(pathlib.Path(out, f"{table.stem}-profile.json"), places().private)
    assert record.is_file(), record
    assert len(seen) == 1
    return record.read_bytes(), seen[0], record


@pytest.fixture(scope="module")
def dense_table(tmp_path_factory: pytest.TempPathFactory) -> pathlib.Path:
    path = pathlib.Path(tmp_path_factory.mktemp("fits-kept-table"), "dense.csv")
    _dense(path, 20000, 14)
    return path


def test_a_table_described_twice_writes_the_same_record_taking_every_fit(
        tmp_path: pathlib.Path, dense_table: pathlib.Path, monkeypatch: "pytest.MonkeyPatch") -> None:
    first, made, record = _profile(tmp_path, dense_table, [], monkeypatch)
    assert made.taken == 0 and made.fitted > 0
    kept = pathlib.Path(f"{record}-fits")
    assert kept.is_file() and inside.carries_marker(kept)
    if os.name != "nt":
        assert stat.S_IMODE(kept.stat().st_mode) == 0o600
    second, again, _record = _profile(tmp_path, dense_table, [], monkeypatch)
    assert second == first
    assert again.fitted == 0 and again.taken == made.fitted, (again.taken, again.fitted, made.fitted)


def test_a_second_description_declared_otherwise_writes_the_record_a_fresh_one_writes(
        tmp_path: pathlib.Path, dense_table: pathlib.Path, monkeypatch: "pytest.MonkeyPatch") -> None:
    _first, _made, _record = _profile(pathlib.Path(tmp_path, "rounds"), dense_table, [], monkeypatch)
    declared = ["--code", "n01", "--replace-description"]
    second, again, _record = _profile(pathlib.Path(tmp_path, "rounds"), dense_table, declared, monkeypatch)
    fresh, none_held, _record = _profile(pathlib.Path(tmp_path, "fresh"), dense_table, declared, monkeypatch)
    assert none_held.taken == 0
    assert second == fresh
    assert again.taken > 0 and again.fitted > 0, (again.taken, again.fitted)


# -- the conditional pass (lane STATS-B) under the kept fits, merged in batch 4zz ------------------------------------


def _masked(rows: int, masked: bool) -> "dict[str, list[str]]":
    """An age, a treatment given to the older, and an outcome the treatment lowers as age raises it: the treatment's
    patients' odds stand near the others', so it reads as nothing against the intercept alone and enters only by the
    conditional pass. With ``masked`` False the treatment column is drawn apart from everything (age and outcome the
    same cells), so the pass adds nothing."""
    draw = random.Random("masked")
    apart = random.Random("apart")
    out: "dict[str, list[str]]" = {"age": [], "treated": [], "outcome": []}
    for _row in range(rows):
        age = draw.gauss(60.0, 12.0)
        treated = draw.random() < 1.0 / (1.0 + math.exp(-0.12 * (age - 60.0)))
        eta = -1.0 + 0.06 * (age - 60.0) - 0.7 * treated
        outcome = draw.random() < 1.0 / (1.0 + math.exp(-eta))
        written = treated if masked else apart.random() < 0.5
        out["age"] += [f"{age:.1f}"]
        out["treated"] += ["Y" if written else "N"]
        out["outcome"] += ["Y" if outcome else "N"]
    return out


def _masked_zone(columns: "dict[str, list[str]]", kept: "R.KeptFits | None") -> "tuple[str, set[str]]":
    rows = len(columns["age"])
    sample = R.sample_rows(rows)
    specs = [R.ColumnSpec("age", 0, NUMBER, 0, (), ""), R.ColumnSpec("treated", 1, LABEL, 0, ("N", "Y"), ""),
             R.ColumnSpec("outcome", 2, LABEL, 0, ("N", "Y"), "")]
    encoded = [R.encode(spec, columns[spec.name], sample) for spec in specs]
    zone = R.fit_zone([each for each in encoded if each is not None], len(sample), rows, None, "", None, kept)
    outcome = [entry for entry in zone["columns"] if entry["name"] == "outcome"][0]  # type: ignore[union-attr, index]
    parents = {term[1] for term in outcome["value"]["terms"] if isinstance(term, list) and len(term) > 1}
    return json.dumps(zone, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False), parents


def test_the_parents_the_conditional_pass_adds_are_kept_under_every_candidate_they_read() -> None:
    # Round one: the masked treatment enters by the conditional pass; the zone with fits kept is the fresh one.
    masked = _masked(6000, True)
    first = R.KeptFits()
    made, parents = _masked_zone(masked, first)
    assert "treated" in parents and "age" in parents, parents
    assert made == _masked_zone(masked, None)[0]
    added = [entry for entry in first.made_models.values() if sorted(entry) == ["added"] and entry["added"]]
    assert added, first.made_models
    # Round two on the same table: everything taken, the same zone.
    again = _held(first)
    assert _masked_zone(masked, again)[0] == made
    assert again.fitted == 0
    # Round two with the treatment column drawn apart: the screen chooses the same parents (age), but the pass reads a
    # candidate that changed, so it is made again and adds nothing -- the fresh zone (mutant: the pass's key reads the
    # screen's parents alone, so the last round's treatment is added again).
    apart = _masked(6000, False)
    held = _held(first)
    zone, parents = _masked_zone(apart, held)
    assert "treated" not in parents, parents
    assert zone == _masked_zone(apart, None)[0]
