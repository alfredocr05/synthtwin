"""A pool's stand-ins name no person's key and no run its published exclusions keep back (the orchestrator's LANE I4m RULINGS 21 (3)).

Codex's review of batch 4o, item 3: lane PL's pool in people chose its start from the
published levels alone, one place wider than the widest (`8888` beside `201` to
`204`), while the same block's `figure_openings` kept every run of four figures
opening with `8` back -- because person 0's rare `8888`, also person 0's declared key,
opened so. The description printed `pool_in_people.number_from` `8888` and the twin
wrote it into 20 cells at 20,000 rows, where 591b356f and 2af926ce held the column.
Now the start honours the published openings (`taxonomy.pool_stand_in_starts`), a
pool whose walks would write a person's key is held (`profile._described_with_pool`),
and the generator keeps the pool's stand-ins off the real runs as every other
held-back stand-in (`generation._label_content`, method G8.3d, mirrored by the oracle).
Each case is red on 015d5003 and on the mutant its comment names.
"""

from __future__ import annotations

import collections
import importlib.util
import json
import pathlib

import fixtures
import released_hold_cases as cases

from synthtwin import contract, generation, parsing, profile, reading, taxonomy

KEY = cases.KEY_OF_PERSON_0


def _key_written(found: "dict[str, object]") -> "tuple[int, int, int]":
    """Description texts holding the key, twin cells of the column holding it, and twin cells equal to it."""
    twin: "list[str]" = found["twin"]  # type: ignore[assignment]
    return (
        found["text"].count(KEY),  # type: ignore[union-attr]
        sum(1 for cell in twin if KEY in cell),
        sum(1 for cell in twin if cell == KEY),
    )


def test_a_rare_code_that_is_a_key_unanswered(tmp_path: pathlib.Path) -> None:
    # Codex's case, seed 0, nothing answered: held and asked (its `A` settles
    # nothing, LANE I4m RULINGS 21 (2)); `8888` in no file and no twin cell (one in
    # the description and 20 twin cells on 015d5003).
    found = cases.run(tmp_path / "unanswered", cases.a_code_that_is_a_key())
    assert found["exits"] == [0, 0], found["exits"]
    assert _key_written(found) == (0, 0, 0)
    assert "pool_in_people" not in found["block"]  # type: ignore[operator]


def test_a_rare_code_that_is_a_key_answered_no(tmp_path: pathlib.Path) -> None:
    # Answered `no`, the pool is offered: its only starts, `8888` and wider, hold a
    # run its own `figure_openings` keep back, so the column keeps its hold.
    # Mutant: the openings not read by `_start_fits`.
    found = cases.run(tmp_path / "no", cases.a_code_that_is_a_key(), ("no",))
    assert found["exits"] == [0, 0, 0], found["exits"]
    assert _key_written(found) == (0, 0, 0)


def test_a_rare_code_that_is_a_key_declared_a_code(tmp_path: pathlib.Path) -> None:
    # Declared a code, the block names no openings (the person's word that it is no
    # key): the start `8888` is then a person's key, so the column keeps its hold.
    # Mutant: `_a_stand_in_is_a_key` never true.
    found = cases.run(tmp_path / "code", cases.a_code_that_is_a_key(), typed=("--code", "kind"))
    assert found["exits"] == [0, 0], found["exits"]
    assert _key_written(found) == (0, 0, 0)
    assert "pool_in_people" not in found["block"]  # type: ignore[operator]


OPENINGS = {4: "9|7|6|5|4|3|2|1"}


def test_the_start_honours_the_published_openings() -> None:
    settings = taxonomy.Settings()
    published, written = ["201", "202", "203", "204", "a"], ["201", "202", "203", "204", "A"]
    assert taxonomy.pool_stand_in_starts(published, written, (1, 0), settings, frozenset()) == {
        "number_from": "8888", "word_from": ""}
    assert taxonomy.pool_stand_in_starts(published, written, (1, 0), settings, frozenset(), False, OPENINGS) is None
    assert taxonomy.pool_stand_in_starts(published, written, (1, 0), settings, frozenset(), False, {4: "9|8"}) == {
        "number_from": "8888", "word_from": ""}


def test_the_published_openings_alone_keep_a_rare_run_off_the_start(tmp_path: pathlib.Path) -> None:
    # The library at a test size (LANE I4m RULINGS 18 (4)): `8888` five people hold,
    # nobody's key, beside `201` to `204` and `A` (a column of labels, whose block
    # publishes its openings), answered `no`. The openings keep `8` of four figures
    # back, so `8888` is no start, nor is anything wider. Mutant: the openings not
    # read by `_start_fits` (the start `8888`, the rare run itself, printed).
    lines = ["patient_key,kind"]
    for who in range(300):
        for row in range(4):
            lines += [f"{100000 + who},{KEY if who < 5 else cases.CODES[(who * 4 + row) % len(cases.CODES)]}"]
    path = tmp_path / "rare.csv"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    document = profile.build_document(
        reading.read_table(f"{path}"), taxonomy.Settings(), ["patient_key"], subjects=["patient_key"],
        safe_harbor_no=["kind"],
    )
    assert KEY not in json.dumps(document)


def test_the_profiler_reads_the_runs_as_the_generator_does() -> None:
    # `taxonomy.stand_in_runs_stand` restates `generation._figure_run_stands` over
    # every run of a cell: the same answer on each spelling and each set of openings.
    for openings in (OPENINGS, {4: "9|8"}, {3: "", 4: "9"}, {5: "9", 9: "9"}, {4: ""}, {6: "1|2"}):
        for spelling in ("8888", "88888", "9999", "7000", "0888", "08888", "A8888", "123", "5390206",
                         "1230", "X01234Y0001", "88", "999999", "8000", "100000", "2024-01-05"):
            stands = True
            for whole, start, end in generation._figure_runs_of(spelling):
                if end - whole >= parsing.FIGURE_RUN_KEY_WIDTH and not generation._figure_run_stands(
                    spelling[start:end], openings, spelling[whole:end]
                ):
                    stands = False
            assert taxonomy.stand_in_runs_stand(spelling, openings) == stands, (spelling, openings)


def _pool_described(folder: pathlib.Path) -> "dict[str, object]":
    """A pool counted in people whose start is `8888`: 300 people on four rows, `7777` five people hold, declared a code."""
    lines = ["patient_key,kind"]
    for who in range(300):
        for row in range(4):
            lines += [f"{100000 + who},{'7777' if who < 5 else cases.CODES[(who * 4 + row) % 4]}"]
    path = folder / "pool.csv"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return profile.build_document(
        reading.read_table(f"{path}"), taxonomy.Settings(), ["patient_key"], forced_codes=["kind"], subjects=["patient_key"]
    )


def _oracle() -> object:
    path = pathlib.Path(__file__).resolve().parents[1] / "tools" / "reference" / "make_generation_reference_vectors.py"
    spec = importlib.util.spec_from_file_location("make_generation_reference_vectors", path)
    module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


def test_the_generator_keeps_an_older_start_off_the_published_openings(tmp_path: pathlib.Path) -> None:
    # A description written before this rule: its pool starts at `8888` beside
    # openings that keep every `8` of four figures back. The generator's pass
    # renames it, as it renames every other held-back stand-in, and the oracle
    # writes the same cells (A-P4-59). Mutant: the pool's cells returned before
    # the pass (015d5003's early return).
    document = _pool_described(tmp_path)
    block = [one for one in document["columns"] if one["name"] == "kind"][0]  # type: ignore[union-attr, index]
    assert block["pool_in_people"]["number_from"] == KEY  # type: ignore[index]
    block["figure_openings"] = {"4": OPENINGS[4]}  # type: ignore[index]
    path = fixtures.write_profile(tmp_path, "t-profile.json", document)
    plan = generation.plan_generation(contract.load_profile(f"{path}"))
    written = [generation._label_content(one)[0] for one in plan.columns if one.column.name == "kind"][0]
    assert [cell for cell in written if KEY in cell] == []
    assert collections.Counter(written) == collections.Counter(
        _oracle()._label_content(json.loads(json.dumps(block)))  # type: ignore[attr-defined]
    )
    twin = generation.generate(contract.load_profile(f"{path}"), 0)
    assert [cell for cell in twin.columns[twin.names.index("kind")] if KEY in cell] == []
