"""The self-test L2b and the two reports of chain A, behind the chain's switch (lane ST, plan P4-D458).

NOT IN FORCE. Invariant S12 stands: no shipped command turns the chain
on, so every description, summary, questions file and twin a person
makes is byte for byte what it was. This file is lane ST's gate:

- THE SAMPLE UNDER G4: `chain.sample_rows` holds one occurrence count
  for each different row and at most `m` keyed entries, and takes the
  first build's rows in the first build's order;
- every rule of the self-test and of the two reports red on its mutant;
- REPAIR 1 (LANE ST RULINGS 3 and 4): a named private folder open to other
  accounts refused, a fault of the self-test never moving the run, the
  worst of three trial keys, shares on joint estimates, F1's part for each
  level of a label column, a pair's table at the finest level its cells
  support and its code-scale correlation beside it (BC-ARCH 4.2's design
  at 20,000 rows, the one case here at that size), a family showing no
  relationship not judged (the null table ST5 at 5,000 rows, a test size),
  the ceiling through `run()`, the support rule through the estimate
  builders, the shared F1 line and the chain-off block, and the private
  report's new lines, each red on its mutant;
- THE FOLLOW-UP (LANE ST RULINGS 7 (1)): a family or part of fewer than
  five comparisons reads `not carried` where every one stands past the
  line on its own word, else `not judged`, its reason counting the
  estimates showing a relationship the trial twin keeps inside; K-BC-11
  records the family-runs that rule leaves; and five behaviours of repair
  2 guarded (RULINGS 7 (2)); each red on its mutant.

Every fixture is invented here.
"""

import dataclasses
import hashlib
import random

from synthtwin import chain


def _first_build_sample(hashes, tabled, size):
    """The first build's selection, written out: one tuple for each tabled row, all of them sorted."""
    seen = {}
    keyed = []
    for at in range(len(tabled)):
        one = hashes[tabled[at]]
        occurrence = seen[one] if one in seen else 0
        seen[one] = occurrence + 1
        key = hashlib.blake2b(one + occurrence.to_bytes(8, "big"), digest_size=8, person=b"synthtwin.smp.1").digest()
        keyed += [(key, one, occurrence, at)]
    keyed = sorted(keyed)
    return [entry[3] for entry in keyed[: min(size, len(keyed))]]


def test_the_bounded_selection_takes_the_first_builds_rows_in_its_order():
    """Equal rows, skipped rows, a sample larger than the table and none at all, on 400 invented tables."""
    rng = random.Random(4580)
    for _trial in range(400):
        rows = rng.randint(0, 300)
        pool = [rng.getrandbits(256).to_bytes(32, "big") for _ in range(rng.randint(1, 12))]
        hashes = [rng.choice(pool) if rng.random() < 0.6 else rng.getrandbits(256).to_bytes(32, "big") for _ in range(rows)]
        tabled = [row for row in range(rows) if rng.random() < 0.9]
        size = rng.randint(0, 340)
        assert chain.sample_rows(hashes, tabled, size) == _first_build_sample(hashes, tabled, size)


def test_the_selection_holds_at_most_the_sample_of_keyed_entries(monkeypatch):
    """The heap never holds more than `min(m, n)` entries (the first build held one for every row)."""
    held = []
    real_add = chain._heap_add

    def counting(heap, entry):
        real_add(heap, entry)
        held.append(len(heap))

    monkeypatch.setattr(chain, "_heap_add", counting)
    hashes = [hashlib.blake2b(row.to_bytes(8, "big"), digest_size=32).digest() for row in range(5000)]
    taken = chain.sample_rows(hashes, list(range(5000)), 200)
    assert len(taken) == 200 and max(held) == 200


# -- ONE WALK: the self-test deals as the generator deals (G16.9) ---------------

import types  # noqa: E402

from synthtwin import chain_rules, chain_selftest, chain_walk, contract, generation, twinstore  # noqa: E402

_ROWS = 600


def _ladder(name, bands, l1, l2, ordered):
    """An invented ladder: `bands` L0 bands, their L1 and L2 maps, which of them hold a value band."""
    counts = (bands, 1 + max(l1), 1 + max(l2))
    return chain_rules.Ladder(name, tuple((f"b{at}",) for at in range(bands)), (tuple(range(bands)), tuple(l1), tuple(l2)), counts, tuple([0] * bands), tuple(ordered))


def _fixture():
    """Three invented columns on 600 rows and a chain of three families: a root, a child of one parent, one of two."""
    rng = random.Random(458)
    scales = {
        "a": _ladder("a", 4, (0, 0, 1, 1), (0, 0, 0, 0), (True, True, True, False)),
        "b": _ladder("b", 3, (0, 1, 1), (0, 0, 0), (True, True, True)),
        "c": _ladder("c", 5, (0, 0, 1, 1, 2), (0, 0, 0, 1, 1), (True, True, True, True, False)),
    }
    codes = {"a": [rng.randrange(4) for _ in range(_ROWS)]}
    codes["b"] = [min(2, code // 2 + rng.randrange(2)) for code in codes["a"]]
    codes["c"] = [min(4, codes["a"][row] + codes["b"][row] + rng.randrange(2)) for row in range(_ROWS)]
    linear = {name: bytes(rng.randrange(256) for _ in range(_ROWS)) for name in scales}
    columns = {
        name: chain.SampleColumn(name, "continuous", scales[name], bytes(codes[name]), linear[name], None, bytes([1] * _ROWS), None, -1, None, None, None)
        for name in scales
    }
    families = (
        chain_rules.Family("a", 0, (), None, ()),
        chain_rules.Family("b", 1, (("a", 1),), 0, ()),
        chain_rules.Family("c", 0, (("a", 1), ("b", 1)), 1, ()),
    )
    hashes = tuple(rng.getrandbits(64) for _ in range(_ROWS))
    inputs = chain.SelftestInputs(_ROWS, hashes, tuple(columns[name] for name in ("a", "b", "c")), families, ())
    return inputs, columns


def _generation_walk(inputs, columns, seeds):
    """Each family dealt by `generation._chain_family` on the same bands, tables and words: band codes and cell indices."""
    walk_columns = {}
    for step, name in enumerate(("a", "b", "c")):
        family = [family for family in inputs.families if family.child == name][0]
        bands, _cells = chain_selftest.child_bands(columns[name], family.level)
        ladder = columns[name].ladder
        walk_columns[name] = generation._WalkColumn(step, family.level, ladder.maps, ladder.counts, bands.ordered, bands)
    families = []
    for family in inputs.families:
        table = chain_selftest._sample_table(inputs, family, columns)
        families += [contract.ChainFamily(family.child, family.level, family.parents, family.anchor, table)]
    walk = generation._Walk(list(range(_ROWS)), (), walk_columns, tuple(families))
    found = {}
    for place, family in enumerate(families):
        sums = chain_walk.packed(_ROWS, chain_walk.SUM_WIDTH)
        for row, total in enumerate(chain_selftest.walk_sums(seeds, place)):
            chain_walk.put(sums, row, total)
        finished = [twinstore.held_column([f"c{at}" for at in range(_ROWS)]) for _name in ("a", "b", "c")]
        generation._chain_family(walk, family, sums, finished, types.SimpleNamespace(placing=False), [None, None, None])
        step = walk.columns[family.child].step
        found[family.child] = (bytes(walk.columns[family.child].codes), [int(cell[1:]) for cell in twinstore.column_cells(finished[step])])
    return found


def _selftest_walk(inputs, columns, seeds, deal=None):
    """The same chain dealt by the self-test's own walk (`chain_selftest.deal_family`)."""
    deal = deal or chain_selftest.deal_family
    dealt = {}
    found = {}
    for place, family in enumerate(inputs.families):
        bands, _cells = chain_selftest.child_bands(columns[family.child], family.level)
        parents = []
        for name, level in family.parents:
            codes, width, chain_level = dealt[name]
            ladder = columns[name].ladder
            parents += [chain_selftest.Parent(codes, width, ladder.maps, chain_level, level, ladder.counts)]
        table = chain_selftest._sample_table(inputs, family, columns)
        result, _aimed = deal(parents, bands, table, chain_selftest.walk_sums(seeds, place))
        dealt[family.child] = (result.bands, result.band_width, family.level)
        found[family.child] = (bytes(result.bands), [chain_walk.read_code(result.index, result.index_width, row) for row in range(_ROWS)])
    return found


def test_one_walk_the_self_test_and_the_generator_deal_the_same_bands_and_cells():
    """Handed the same words, the self-test's walk and `generation._chain_family` deal the same band codes and cell indices."""
    inputs, columns = _fixture()
    seeds = chain_selftest.row_seeds(inputs.hashes)
    assert _selftest_walk(inputs, columns, seeds) == _generation_walk(inputs, columns, seeds)


def test_one_walk_is_red_on_a_walk_that_differs():
    """MUTANT: the self-test's walk orders the rows by their hidden scores the other way round."""

    def reversed_order(parents, bands, table, sums):
        top = 12 * 65535
        return chain_selftest.deal_family(parents, bands, table, [top - total for total in sums])

    inputs, columns = _fixture()
    seeds = chain_selftest.row_seeds(inputs.hashes)
    assert _selftest_walk(inputs, columns, seeds, reversed_order) != _generation_walk(inputs, columns, seeds)


def test_the_trial_twin_holds_each_columns_own_sample_cells():
    """The trial twin is a rearrangement: each column holds exactly its own sample rows' cells, once each."""
    inputs, columns = _fixture()
    seeds = chain_selftest.row_seeds(inputs.hashes)
    source, moved = chain_selftest.trial_twin(inputs, seeds)
    assert moved == 0
    for name in ("a", "b", "c"):
        assert sorted(source[name]) == list(range(_ROWS))


# -- THE WORDS AND THE YARDSTICK AGAINST THE ORACLE'S FROZEN VECTORS -----------

import json  # noqa: E402
import pathlib  # noqa: E402

_VECTORS = json.loads((pathlib.Path(__file__).resolve().parent / "reference" / "selftest-oracle-vectors.json").read_text(encoding="utf-8"))


def test_the_words_are_the_oracles():
    """SplitMix64's words of each sampled row, keyed by the constant and the row's content hash, and the four splits."""
    case = _VECTORS["words"]
    seeds = chain_selftest.row_seeds(case["hashes"])
    assert seeds == case["seeds"]
    assert [[chain_selftest.word(seed, k) for k in range(4)] for seed in seeds] == case["words"]
    assert list(chain_selftest.groups_of(seeds)) == case["groups"]
    assert [list(held) for held in chain_selftest.HALF_GROUPS] == _VECTORS["halves"]["groups"]
    # MUTANT: equal rows told apart by their place in the sample.
    assert case["mutant_equal_rows_one_seed"] and seeds[0] != seeds[2]


def test_the_walks_words_and_the_shuffle_are_the_oracles():
    """Each family's hidden sums read words 1 + 3 f to 3 + 3 f; each column's shuffle reads word 1 + 3 F + c."""
    case = _VECTORS["walk_sums"]
    seeds = chain_selftest.row_seeds(_VECTORS["words"]["hashes"])
    assert chain_selftest.walk_sums(seeds, 0)[1] == case["family_0"]
    assert chain_selftest.walk_sums(seeds, 1)[1] == case["family_1"] != case["mutant_from_word_0"]
    shuffle = _VECTORS["shuffle"]
    for column in range(2):
        assert chain_selftest.shuffle_order(seeds, shuffle["families"], column) == shuffle[f"column_{column}"]


def _estimates(rows):
    return [chain_selftest.Estimate(("F1", f"{at}"), "F1", value, twin, shuffle, halves, "difference", null) for at, (value, twin, shuffle, null, halves) in enumerate(rows)]


def test_the_yardstick_is_scaled_to_the_whole_table():
    """h * sqrt(n_s / n); RULE W2 on n times it; MUTANT: unscaled, it is sqrt(10) times wider at 20,000 of 200,000."""
    case = _VECTORS["yardstick"]
    estimate = chain_selftest.Estimate(("F1",), "F1", 0.3, 0.3, 0.3, case["halves"])
    whole, rest = chain_selftest._yardstick(estimate)
    assert whole == case["h"] and abs(rest * 2 ** 0.5 - case["replicate"]) < 1e-15
    assert abs(whole * (20000 / 200000) ** 0.5 - case["scaled_20000_of_200000"]) < 1e-15
    assert abs(whole / case["scaled_20000_of_200000"] - case["mutant_unscaled_over_scaled"]) < 1e-12


def _family_rows():
    rows = []
    for at in range(8):
        base = 0.40 + 0.01 * at
        halves = [base + 0.004 * ((at + j) % 3 - 1) for j in range(8)]
        rows += [(base, base + 0.001, base - 0.2, base - 0.2, halves)]
    return rows


def test_a_familys_judged_word_is_the_oracles():
    """Carried, approximate, not carried and not judged, each on the oracle's case; the unscaled yardstick is its mutant."""
    case = _VECTORS["judged"]
    close = _family_rows()
    loose = [(value, value + 0.003, shuffle, null, halves) for value, _twin, shuffle, null, halves in close]
    far = [(value, value - 0.15, shuffle, null, halves) for value, _twin, shuffle, null, halves in close]

    def word(rows, sample, table_rows):
        return chain_selftest.word_of([chain_selftest.score(one, sample, table_rows, 11) for one in _estimates(rows)])[0]

    assert word(close, 20000, 20000) == case["close_at_20000_of_20000"] == "carried"
    assert word(close, 20000, 200000) == case["close_at_20000_of_200000"] == "carried"
    assert word(loose, 20000, 200000) == case["loose_at_20000_of_200000"] == "approximate"
    assert word(far, 20000, 200000) == case["far_at_20000_of_200000"] == "not carried"
    assert word(close[:4], 20000, 20000) == case["four_estimates"] == "not judged"
    # MUTANT: the yardstick unscaled (the sample's own precision) reads the loose family carried.
    assert word(loose, 20000, 20000) == case["mutant_loose_unscaled"] == "carried"
    # Inside the yardstick but keeping less of the relationships than a fresh half: approximate.
    keeping_less = []
    for at in range(8):
        base = 0.40 + 0.01 * at
        halves = [base + 0.02, base - 0.02] + [base + 0.05 * (1 if j % 2 == 0 else -1) for j in range(6)]
        keeping_less += [(base, base + 0.07, base - 0.2, base - 0.2, halves)]
    assert word(keeping_less, 20000, 20000) == case["keeping_less_at_20000_of_20000"] == "approximate"
    assert case["mutant_keeping_less_without_the_rule"] == "carried"


# -- THE TWO REPORTS, THROUGH THE COMMAND (attack list items 1 to 10) ----------

import contextlib  # noqa: E402
import io  # noqa: E402
import os  # noqa: E402

import pytest  # noqa: E402

import chain_twins  # noqa: E402
from synthtwin import asking, chain_grades, cli, rendering  # noqa: E402
import importlib.util  # noqa: E402

_SCANNER_SPEC = importlib.util.spec_from_file_location(
    "st_scan_imports", pathlib.Path(__file__).resolve().parents[1] / "tools" / "offline_scan" / "scan_imports.py"
)
scan_imports = importlib.util.module_from_spec(_SCANNER_SPEC)
_SCANNER_SPEC.loader.exec_module(scan_imports)

_KEY = chain_twins.oc.TEST_KEY


def _quiet(argv, run):
    said = io.StringIO()
    with contextlib.redirect_stdout(said), contextlib.redirect_stderr(said):
        code = cli.main(argv, chain=run)
    return code, said.getvalue()


def _installation(folder):
    data = folder / "data"
    data.mkdir(mode=0o700)
    if os.name != "nt":
        data.chmod(0o700)
    key = data / "chain-key"
    key.touch(mode=0o600)
    if os.name != "nt":
        key.chmod(0o600)
    key.write_bytes(_KEY)
    return data


def _report_name(name):
    """The private report's file name for a table's name (`chain_selftest.report_stem`)."""
    return chain_selftest.report_stem(name) + "-" + chain_selftest.REPORT_FILE + ".txt"


def _profile(folder, data, private_folder=None, name=None, rows=800):
    """A switched profile of the invented clinic, its open questions answered as the data is (as chain_twins does)."""
    out = folder / "out"
    out.mkdir(exist_ok=True)
    table = chain_twins._write(out / "clinic.csv", chain_twins.HEADER, chain_twins._clinic_rows(rows))
    run = cli.ChainRun(folder=str(data), private_folder=private_folder, name=name, rows_per_person=asking.ANSWER_ONE_ROW_EACH)
    code, said = _quiet(["profile", str(table), "--out-dir", str(out)], run)
    questions = out / "clinic-questions.json"
    asked = json.loads(questions.read_text(encoding="utf-8"))
    if asked["asked"] and code == 0:
        for entry in asked["asked"]:
            offered = str(entry["answers_you_can_give"])
            if "'measurement'" in offered:
                entry["your_answer"] = "measurement"
            elif "'keep'" in offered:
                entry["your_answer"] = "keep"
        questions.write_text(json.dumps(asked, indent=1) + "\n", encoding="utf-8", newline="\n")
        again = cli.ChainRun(folder=str(data), private_folder=private_folder, name=name, replace_description=True,
                             rows_per_person=asking.ANSWER_ONE_ROW_EACH)
        code, said = _quiet(["profile", str(table), "--out-dir", str(out), "--answers", str(questions)], again)
    return code, said, out


def _shared_report(out):
    loaded = contract.load_profile(str(out / "clinic-profile.json"), chain=True)
    twin = generation.generate(loaded, 1)
    return loaded, twin, rendering.report(loaded, twin)


@pytest.fixture(scope="module")
def switched(tmp_path_factory):
    folder = tmp_path_factory.mktemp("switched")
    data = _installation(folder)
    # The suite's own default (tests/conftest.py) is per test; this module's
    # one switched run is made once, under the same default.
    with pytest.MonkeyPatch.context() as own:
        own.setitem(cli.main.__kwdefaults__, "small_tables_refused", False)
        own.setitem(cli.run.__kwdefaults__, "small_tables_refused", False)
        code, said, out = _profile(folder, data)
    assert code == 0, said
    loaded, twin, report = _shared_report(out)
    private = data / "private-reports" / _report_name("clinic")
    return {"folder": folder, "data": data, "out": out, "said": said, "loaded": loaded, "twin": twin, "report": report,
            "private": private, "words": json.loads((out / "clinic-profile.json").read_text(encoding="utf-8"))["relationships"]["statistical"]["words"]}


def _private_problems(text, words, key_file):
    """What the private report owes (contract 4.6b.8, R7) and lacks: an empty list where it holds everything."""
    problems = []
    for sentence in (chain_selftest.ACT_ON, chain_selftest.WHICH_TWIN):
        if sentence not in text:
            problems += [f"missing: {sentence[:30]}"]
    for code, name in chain_grades.FAMILIES:
        if not any(line.strip().startswith(f"{code} {name}: structural ") and "; judged " in line for line in text.splitlines()):
            problems += [f"family {code} lacks both grades"]
    for entry in words:
        first, second = entry["columns"]
        structural = chain_selftest.EXACT_AT if entry["word"] == "exact" else entry["word"]
        if f"  {first} and {second}: structural {structural}; judged " not in text:
            problems += [f"pair {first} and {second} lacks both grades"]
    if f"key file is at {key_file}" not in text:
        problems += ["the key file's path is missing"]
    if _KEY.hex() in text or _KEY.decode("latin-1") in text:
        problems += ["the key's bytes are in the report"]
    return problems


def test_a_switched_run_writes_the_private_report_in_the_private_folder(switched):
    """Attack 5: the report beside the key file alone, the folder 0700 and the file 0600, both grades, the key's path."""
    private = switched["private"]
    assert private.exists(), switched["said"]
    if os.name != "nt":
        assert private.stat().st_mode & 0o777 == 0o600
        assert private.parent.stat().st_mode & 0o777 == 0o700
    text = private.read_text(encoding="utf-8")
    assert _private_problems(text, switched["words"], switched["data"] / "chain-key") == []
    # Attack 6: nothing else is written: no sample, no trial twin, no spill file.
    assert sorted(entry.name for entry in private.parent.iterdir()) == [_report_name("clinic")]
    assert sorted(entry.name for entry in switched["data"].iterdir()) == ["chain-key", "chain-ledger", "private-reports"]


def test_the_private_reports_rules_are_red_on_their_mutants(switched):
    """MUTANTS: the sentence saying which grade to act on missing; a pair's judged grade missing; the key's bytes written."""
    text = switched["private"].read_text(encoding="utf-8")
    key_file = switched["data"] / "chain-key"
    assert _private_problems(text.replace(chain_selftest.ACT_ON, ""), switched["words"], key_file)
    first, second = switched["words"][0]["columns"]
    cut = "\n".join(line for line in text.splitlines() if not line.startswith(f"  {first} and {second}: "))
    assert _private_problems(cut, switched["words"], key_file)
    assert _private_problems(text + _KEY.hex(), switched["words"], key_file)


def test_no_shared_file_holds_a_judged_word_a_sample_size_or_a_reason(switched):
    """Attacks 1 and 2: the description, summary, questions file and the shared report hold none of the private report's words."""
    shared = [switched["report"]]
    for name in ("clinic-profile.json", "clinic-profile.txt", "clinic-questions.json"):
        shared += [(switched["out"] / name).read_text(encoding="utf-8")]
    private_only = ["judged carried", "judged approximate", "judged not carried", "judged not judged", "Judged on a sample",
                    "The replicate", chain_selftest.ACT_ON[:20], chain_selftest.BEFORE_THE_POLISH, "no chain is published"]
    for text in shared:
        for phrase in private_only:
            assert phrase not in text


def test_the_private_folder_beside_the_description_is_refused(tmp_path):
    """Attack 5: a private folder that is the description's folder is refused in plain words, and nothing is written there."""
    data = _installation(tmp_path)
    code, said, out = _profile(tmp_path, data, private_folder=str(tmp_path / "out"))
    assert code == 0, said
    assert "The private report was not written" in said
    assert not [entry for entry in out.iterdir() if "private-report" in entry.name]


def test_nothing_is_written_when_the_ledger_refuses_the_run(switched):
    """The same table described again under another name is refused by the ledger, and no private report is written for it."""
    out = switched["out"]
    run = cli.ChainRun(folder=str(switched["data"]), name="another", rows_per_person=asking.ANSWER_ONE_ROW_EACH)
    code, said = _quiet(["profile", str(out / "clinic.csv"), "--out-dir", str(switched["folder"] / "elsewhere")], run)
    assert code != 0, said
    assert not (switched["data"] / "private-reports" / _report_name("another")).exists()


def test_the_shared_files_stand_byte_for_byte_with_the_self_test_stubbed(tmp_path, monkeypatch):
    """Attack 4: the description, summary and questions file, and the shared report, are the same with the self-test a stub."""
    first = tmp_path / "first"
    first.mkdir()
    code, said, out_first = _profile(first, _installation(first))
    assert code == 0, said

    def nonsense(inputs, words, floor, off=""):
        found = chain_selftest.not_judged("a stub's nonsense", words)
        return chain_selftest.Judged(found.families, found.pairs, chain_selftest.Controls(0.99, 0.01, True, "stub"), 7, 13, 5, ("stub",))

    monkeypatch.setattr(chain_selftest, "run", nonsense)
    second = tmp_path / "second"
    second.mkdir()
    code, said, out_second = _profile(second, _installation(second))
    assert code == 0, said
    for name in ("clinic-profile.json", "clinic-profile.txt", "clinic-questions.json"):
        assert (out_first / name).read_bytes() == (out_second / name).read_bytes(), name
    assert _shared_report(out_first)[2] == _shared_report(out_second)[2]


def test_the_shared_report_is_a_function_of_the_description_and_the_seed(tmp_path):
    """Attack 3: the clinic with its rows in another order describes byte for byte alike, and its shared report too."""
    first = tmp_path / "first"
    first.mkdir()
    code, said, out_first = _profile(first, _installation(first))
    assert code == 0, said
    second = tmp_path / "second"
    (second / "out").mkdir(parents=True)
    rows = chain_twins._clinic_rows(800)
    rows = rows[400:] + rows[:400]
    chain_twins._write(second / "out" / "clinic.csv", chain_twins.HEADER, rows)
    data = _installation(second)
    code, said = _quiet(["profile", str(second / "out" / "clinic.csv"), "--out-dir", str(second / "out")], cli.ChainRun(folder=str(data), rows_per_person=asking.ANSWER_ONE_ROW_EACH))
    questions = json.loads((out_first / "clinic-questions.json").read_text(encoding="utf-8"))
    if questions["asked"]:
        (second / "out" / "answers.json").write_text(json.dumps(questions, indent=1) + "\n", encoding="utf-8", newline="\n")
        run = cli.ChainRun(folder=str(data), replace_description=True, rows_per_person=asking.ANSWER_ONE_ROW_EACH)
        code, said = _quiet(["profile", str(second / "out" / "clinic.csv"), "--out-dir", str(second / "out"), "--answers", str(second / "out" / "answers.json")], run)
    assert code == 0, said
    assert (out_first / "clinic-profile.json").read_bytes() == (second / "out" / "clinic-profile.json").read_bytes()
    assert _shared_report(out_first)[2] == _shared_report(second / "out")[2]


# -- ATTACK 9: ONE ZONE P IMPORT SITE ------------------------------------------


def _private_import_flags(tmp_path, module, function):
    """Scan a package of the self-test and one importing module: the zone P import flags."""
    tree = tmp_path / "tree" / "synthtwin"
    tree.mkdir(parents=True)
    (tree / "__init__.py").write_text("", encoding="utf-8", newline="\n")
    (tree / "chain_selftest.py").write_text("def word(seed, position):\n    return seed + position\n", encoding="utf-8", newline="\n")
    text = f"def {function}():\n    from synthtwin import chain_selftest\n    return chain_selftest.word(1, 0)\n"
    (tree / f"{module}.py").write_text(text, encoding="utf-8", newline="\n")
    return [line for line in scan_imports.scan_tree(tmp_path / "tree") if "zone P module" in line]


def test_the_scanner_admits_the_one_named_site_and_is_red_on_a_second(tmp_path):
    """The row of _PRIVATE_IMPORT_SITES alone: cli._private_report; another function, another module: flagged."""
    assert _private_import_flags(tmp_path / "one", "cli", "_private_report") == []
    assert _private_import_flags(tmp_path / "two", "cli", "_chained_description")
    assert _private_import_flags(tmp_path / "three", "summary", "_private_report")
    assert scan_imports._MODULE_ZONES["synthtwin.chain_selftest"] == "P"


# -- ATTACKS 7 AND 8, AND THE RULES' MUTANTS -----------------------------------


def test_rule_w2_leaves_a_pair_not_judged_where_n_h_is_under_the_floor():
    """RULE W2: a pair's table is judged only where n times its scaled yardstick reaches f; MUTANT: dropped."""
    tight = chain_selftest.Estimate(("pair", "a", "b"), "pair", 0.0, 0.0001, 0.2, [0.0001, 0.0002, 0.0001, 0.0001], "distance")
    assert not chain_selftest.score(tight, 20000, 20000, 11).judged
    assert chain_selftest.pair_word(chain_selftest.score(tight, 20000, 20000, 11), 0, [], ())[0] == chain_selftest.NOT_JUDGED
    assert chain_selftest.score(tight, 20000, 20000, 1).judged
    wide = chain_selftest.Estimate(("pair", "a", "b"), "pair", 0.0, 0.001, 0.2, [0.02, 0.03, 0.02, 0.025], "distance")
    assert chain_selftest.score(wide, 20000, 200000, 11).judged


def _design(rows, levels):
    """A logistic model's design: one two-valued predictor whose level-1 rows hold `levels` events."""
    x_rows, y, groups = [], [], []
    for row in range(rows):
        level = 1.0 if row < 200 else 0.0
        event = 1.0 if (row < levels if level else row % 3 == 0) else 0.0
        x_rows += [[1.0, level]]
        y += [event]
        groups += [row % 16]
    return chain_selftest.Design(x_rows, y, [0.0] * rows, groups)


def test_the_supported_estimate_rule_needs_22_events_a_level_and_11_in_every_half():
    """A model whose predictor's level holds 21 events is not supported; with 120 it is; MUTANT: the rule dropped."""
    model = chain_selftest.Model("F4", "y", ("x",))
    assert chain_selftest.supported(model, _design(2000, 120))
    assert not chain_selftest.supported(model, _design(2000, 21))
    assert chain_selftest.SUPPORT == 22 and chain_selftest.HALF_SUPPORT == 11


def test_the_ceiling_names_a_skewed_columns_raw_and_log_scales_at_best_approximate():
    """THE CEILING: a skewed column's raw or log scale reads at best approximate, in the private report's family line."""
    family = chain_selftest.FamilyWord("F2", "correlations", chain_selftest.CARRIED, "inside", 9, 9, 0.8, ("cost",))
    judged = chain_selftest.Judged(
        tuple(family if code == "F2" else chain_selftest.FamilyWord(code, name, chain_selftest.NOT_JUDGED, "-", 0, 0, None) for code, name in chain_selftest.FAMILY_NAMES),
        (), chain_selftest.Controls(0.8, 0.1, True, "held"), 100, 1000, 0, ())
    text = chain_selftest.report_text(judged, [], (), {}, "t", "/k")
    assert "On the raw or log scale of cost (skewed): at best approximate." in text
    # MUTANT: the ceiling dropped (no skewed column named) leaves the line out.
    unskewed = dataclasses.replace(family, ceiling=())
    text = chain_selftest.report_text(dataclasses.replace(judged, families=tuple(unskewed if one.family == "F2" else one for one in judged.families)), [], (), {}, "t", "/k")
    assert "(skewed)" not in text
    assert chain_selftest.SKEW_CEILING == 0.2


def _related_inputs(rows=6000):
    """Three invented columns, the second and third following the first, chained as the walk deals them."""
    rng = random.Random(9)
    ladder = _ladder("u", 4, (0, 0, 1, 1), (0, 0, 0, 0), (True, True, True, True))
    first = [rng.randrange(4) for _ in range(rows)]
    columns = []
    for name, codes in (("u", first), ("v", [min(3, code + rng.randrange(2)) for code in first]),
                        ("w", [max(0, code - rng.randrange(2)) for code in first])):
        linear = bytes(min(255, 64 * code + rng.randrange(64)) for code in codes)
        columns += [chain.SampleColumn(name, "continuous", dataclasses.replace(ladder, column=name), bytes(codes), linear,
                                       None, bytes([1] * rows), None, -1, None, None, None)]
    flag = [1 if rng.random() < 0.15 + 0.2 * code else 0 for code in first]
    two = chain_rules.Ladder("y", (("no",), ("yes",)), ((0, 1), (0, 1), (0, 1)), (2, 2, 2), (0, 0), (False, False))
    columns += [chain.SampleColumn("y", "binary", two, bytes(flag), None, None, None, (0, 1), -1, None, None, None)]
    families = (chain_rules.Family("u", 0, (), None, ()), chain_rules.Family("v", 0, (("u", 0),), 0, ()),
                chain_rules.Family("w", 0, (("u", 0),), 0, ()), chain_rules.Family("y", 0, (("u", 0),), 0, ()))
    words = [{"columns": [a, b], "word": "exact" if "u" in (a, b) else "implied"}
             for a, b in (("u", "v"), ("u", "w"), ("u", "y"), ("v", "w"), ("v", "y"), ("w", "y"))]
    return chain.SelftestInputs(rows, tuple(rng.getrandbits(64) for _ in range(rows)), tuple(columns), families, ()), words


def test_the_controls_judge_nothing_where_the_replicate_falls_short(monkeypatch):
    """THE CONTROLS: a run whose replicate lands inside less than a fresh sample would judges nothing and says why.

    MUTANT: the controls skipped. With the replicate's bar raised past any
    run's reach, every family reads `not judged` with the controls' reason;
    a self-test that skipped them would judge the same run.
    """
    inputs, words = _related_inputs()
    judged = chain_selftest.run(inputs, words, 11)
    assert judged.controls.held, judged.controls.why
    assert any(family.word != chain_selftest.NOT_JUDGED for family in judged.families)
    monkeypatch.setattr(chain_selftest, "REPLICATE_AT_LEAST", 1.01)
    voided = chain_selftest.run(inputs, words, 11)
    assert not voided.controls.held and "replicate" in voided.controls.why
    assert all(family.word == chain_selftest.NOT_JUDGED for family in voided.families)
    assert all(pair.word == chain_selftest.NOT_JUDGED for pair in voided.pairs)


def test_the_patient_words_never_call_a_trend_flat_and_name_complete_follow_up():
    """Attack 8, on hand-built `grain` objects as contract 4.6c.9 writes them (the merge's case at the end of this file reads lane GRa's own)."""
    grain = {
        "person": "sid",
        "census": {"lo": 9, "bands": [{"r": 8, "patients": 1200}], "top": {"patients": 0, "rows": 0}},
        "grid": [{"column": "lab", "u": "1", "L": 8, "K": 4}],
        "trend": [{"column": "lab", "cell": ["arm a"], "q": "3"}],
    }
    lines = chain_selftest.patient_lines(grain)
    text = "\n".join(lines)
    assert "carried by a published trend for the groups arm a" in text
    assert "approximate or unconstrained, NOT flat" in text
    assert "On a table where every patient has every visit, change over visits is not published in December." in text
    open_census = dict(grain, census={"lo": 9, "bands": [{"r": 2, "patients": 300}, {"r": 8, "patients": 900}], "top": {"patients": 0, "rows": 0}})
    assert "every patient has every visit" not in "\n".join(chain_selftest.patient_lines(open_census))
    assert " flat" not in text.replace("NOT flat", "")
    assert chain_selftest.patient_lines(None) == ["This description carries no patient layer: each row is read as one person's."]


# -- THE SHARED BLOCK (rendering.report on a switched twin) ---------------------


def _block(report):
    lines = report.splitlines()
    start = [at for at, line in enumerate(lines) if chain_grades.HEADING in line][0]
    end = start
    while lines[end].strip():
        end += 1
    return lines[start:end]


def test_the_shared_block_is_the_structural_grades_and_the_descriptions_words_and_nothing_else(switched):
    """One line a family F1 to F10, one line a pair with the description's own word, 4.6b.13's line, and nothing else."""
    block = _block(switched["report"])
    loaded = switched["loaded"]
    expected = ["1. " + chain_grades.HEADING]
    expected += [f"{code} {name}: {grade}." for code, name, grade in chain_grades.family_grades(False, False)]
    expected += [chain_grades.PAIRS_HEADING]
    moved = {deviation.column for deviation in switched["twin"].deviations if deviation.fact == "chain"}
    assert not moved
    expected += [f"   {first} and {second}: {word}" for first, second, word in loaded.relationships.words]
    expected += [chain_grades.ONCE_LINE]
    assert block == expected
    assert [(entry["columns"][0], entry["columns"][1], entry["word"]) for entry in switched["words"]] == list(loaded.relationships.words)
    # Paragraph 1 gives way to the block; paragraphs 2 and 3 stand.
    assert "1. EVERY COLUMN WAS BUILT ON ITS OWN" not in switched["report"]
    assert "2. EVERY ROW WAS BUILT ON ITS OWN" in switched["report"]


def test_the_shared_block_reads_the_words_never_recomputes_them(switched):
    """A pair's word is READ from the description's `words`: handed other words, the block prints them; MUTANT: recomputed."""
    loaded = switched["loaded"]
    flipped = tuple((first, second, "pinned" if word == "implied" else word) for first, second, word in loaded.relationships.words)
    edited = dataclasses.replace(loaded, relationships=dataclasses.replace(loaded.relationships, words=flipped))
    block = _block(rendering.report(edited, switched["twin"]))
    assert any(line.endswith(": pinned") for line in block)
    assert any(line.startswith("F2 correlations: P (pinned") for line in block)

    def recomputed(profile, twin):
        together = set()
        for family in profile.relationships.chain:
            names = [family.child] + [name for name, _level in family.parents]
            together |= {(a, b) for a in names for b in names if a != b}
        words = tuple((a, b, "exact" if (a, b) in together else "implied") for a, b, _word in profile.relationships.words)
        return rendering._between_columns_lines(dataclasses.replace(profile, relationships=dataclasses.replace(profile.relationships, words=words)), twin)

    assert not any(line.endswith(": pinned") for line in recomputed(edited, switched["twin"]))


def test_a_family_moved_in_this_twin_reads_a_and_is_named(switched):
    """A family dealt against a moved target: its pairs read A here and 'moved in this twin'; MUTANT: graded E."""
    loaded = switched["loaded"]
    family = [one for one in loaded.relationships.chain if one.parents][0]
    moved_twin = dataclasses.replace(switched["twin"], deviations=tuple(switched["twin"].deviations) + (generation._deviation(family.child, "chain", "-", "-", "-"),))
    block = rendering._between_columns_lines(loaded, moved_twin)
    parent = family.parents[0][0]
    pair_lines = [line for line in block if line.strip().startswith((f"{family.child} and {parent}:", f"{parent} and {family.child}:"))]
    assert pair_lines and all(chain_grades.MOVED + ", so A (approximate) here" in line for line in pair_lines)
    unmoved = rendering._between_columns_lines(loaded, switched["twin"])
    assert not any(chain_grades.MOVED in line for line in unmoved)


def test_an_unswitched_twin_keeps_the_independence_paragraph_word_for_word(tmp_path):
    """Attack 10: with the switch at its default the block is empty and paragraph 1 stands, word for word."""
    out = tmp_path / "out"
    out.mkdir()
    table = chain_twins._write(out / "clinic.csv", chain_twins.HEADER, chain_twins._clinic_rows(800))
    code, said = _quiet(["profile", str(table), "--out-dir", str(out)], None)
    assert code == 0, said
    loaded = contract.load_profile(str(out / "clinic-profile.json"))
    twin = generation.generate(loaded, 1)
    report = rendering.report(loaded, twin)
    assert rendering._between_columns_lines(loaded, twin) == []
    assert "\n".join(rendering._independence_lines()) in report
    assert chain_grades.HEADING not in report
    assert not (tmp_path / "data").exists()


def test_a_private_folder_that_cannot_be_made_is_said_in_plain_words(tmp_path):
    """A private folder named where a file stands: the description is written, and the report's failure is said."""
    data = _installation(tmp_path)
    blocked = tmp_path / "a-file"
    blocked.write_text("not a folder\n", encoding="utf-8", newline="\n")
    code, said, out = _profile(tmp_path, data, private_folder=str(blocked))
    assert code == 0, said
    assert "The private report could not be written" in said
    assert (out / "clinic-profile.json").exists()


# -- REPAIR 1: SAFETY FIRST (LANE ST RULINGS 3 (1)) ------------------------------


@pytest.mark.skipif(os.name == "nt", reason="a folder's group and other bits are POSIX modes")
def test_a_private_folder_other_accounts_may_open_is_refused(tmp_path):
    """RULINGS 3 (1)(a): a named private folder that stands with a group or other bit is refused in plain words, nothing written.

    MUTANT: the mode left unread writes the report into the open folder.
    """
    data = _installation(tmp_path)
    shared = tmp_path / "shared-folder"
    shared.mkdir()
    shared.chmod(0o750)
    code, said, out = _profile(tmp_path, data, private_folder=str(shared))
    assert code == 0, said
    assert "can be read or changed by other accounts on this computer" in said
    assert "chmod 700" in said
    assert list(shared.iterdir()) == []
    assert (out / "clinic-profile.json").exists()


@pytest.mark.parametrize("failure", ["FitStopped", "ZeroDivisionError", "ValueError", "RuntimeError"])
def test_a_self_test_that_stops_never_moves_the_run(tmp_path, monkeypatch, switched, failure):
    """RULINGS 3 (1)(b): any fault of the self-test leaves the exit code 0 and every shared byte as with it stubbed.

    The private report is still written, every word `not judged` for the
    reason 'the self-test stopped'. MUTANT: the fault let through ends the
    run with a traceback and a non-zero exit code.
    """
    kinds = {"FitStopped": chain_selftest.FitStopped, "ZeroDivisionError": ZeroDivisionError,
             "ValueError": ValueError, "RuntimeError": RuntimeError}

    def stopping(inputs, words, floor, off=""):
        raise kinds[failure]("a fault of the self-test's own")

    monkeypatch.setattr(chain_selftest, "run", stopping)
    data = _installation(tmp_path)
    code, said, out = _profile(tmp_path, data)
    assert code == 0, said
    for name in ("clinic-profile.json", "clinic-profile.txt", "clinic-questions.json"):
        assert (out / name).read_bytes() == (switched["out"] / name).read_bytes(), name
    assert _shared_report(out)[2] == switched["report"]
    text = (data / "private-reports" / _report_name("clinic")).read_text(encoding="utf-8")
    family_lines = [line for line in text.splitlines() if ": structural " in line and "; judged " in line]
    assert family_lines and all("; judged not judged (" + chain_selftest.STOPPED in line for line in family_lines)


# -- REPAIR 1: THE JUDGEMENT AGAINST THE ORACLE (A-P4-59) -------------------------


def _scored_rows(rows, sample=20000, table_rows=20000):
    return [chain_selftest.score(one, sample, table_rows, 11) for one in _estimates(rows)]


def test_a_familys_shares_are_read_on_its_joint_estimates():
    """RULINGS 4 (2)(a): the share inside and the replicate's read on the joint estimates, on all where fewer than five are joint."""
    case = _VECTORS["joint"]
    close = _family_rows()
    unrelated = []
    for at in range(4):
        base = 0.30 + 0.01 * at
        unrelated += [(base, base + 0.04, base, base, [base + 0.004 * ((at + j) % 3 - 1) for j in range(8)])]
    mixed = _scored_rows(close + unrelated)
    assert sum(1 for one in mixed if one.joint) == case["joint_count"]
    assert chain_selftest.word_of(mixed)[0] == case["mixed_at_20000_of_20000"] == "carried"
    assert chain_selftest.word_of(_scored_rows(close[:4] + unrelated))[0] == case["four_joint_falls_back"]
    # MUTANT: the shares read on every supported estimate.
    assert case["mutant_all_estimates"] == "approximate" != chain_selftest.word_of(mixed)[0]
    assert chain_selftest.JOINT_MINIMUM == 5


def _keyed(words_by_key):
    """Judged results of several keys, F1 reading each key's word and every other family `not judged`."""
    out = []
    for word in words_by_key:
        families = tuple(chain_selftest.FamilyWord(code, name, word if code == "F1" else chain_selftest.NOT_JUDGED, "-", 9, 9, 0.8)
                         for code, name in chain_selftest.FAMILY_NAMES)
        out += [chain_selftest.Judged(families, (chain_selftest.PairWord(("a", "b"), word, "-", (), (), word, 0),),
                                      chain_selftest.Controls(0.8, 0.1, True, "held"), 100, 1000, 0, ())]
    return out


def test_every_word_is_the_worst_of_the_three_trial_keys():
    """RULINGS 3 (2)(a): the worst of the keys' words, `not judged` where a key does not judge; each key's word kept."""
    case = _VECTORS["keys"]
    for words, expected in ((["carried", "carried", "approximate"], case["carried_carried_approximate"]),
                            (["carried", "not judged", "carried"], case["carried_not_judged_carried"]),
                            (["approximate", "not carried", "carried"], case["approximate_not_carried"])):
        found = chain_selftest.combined(_keyed(words))
        assert found.families[0].word == expected and found.pairs[0].word == expected
        assert found.families[0].keys == tuple(words)
    # MUTANT: the first key's word alone reads carried.
    assert case["mutant_first_key"] == "carried" != case["carried_carried_approximate"]
    assert chain_selftest.TRIAL_KEYS == 3


def _scored_word(word):
    """A Scored estimate whose own word is `word`."""
    estimate = chain_selftest.Estimate(("pair", "a", "b", "code"), "pair", 0.3, 0.3, 0.0, [0.3] * 8)
    return chain_selftest.Scored(estimate, word == "carried", True, False, 0.8 if word == "not carried" else 0.2, True, True)


def test_a_pair_reads_the_worst_of_its_table_and_its_correlation():
    """RULINGS 4 (1)(a): table and code-scale correlation; THE CEILING on a skewed pair; MUTANT: the cross-table alone."""
    case = _VECTORS["pairs"]
    table = _scored_word("carried")
    assert chain_selftest.pair_word(table, 0, [_scored_word("not carried")], ())[0] == case["table_carried_correlation_not"]
    log = dataclasses.replace(_scored_word("carried"), estimate=chain_selftest.Estimate(("pair", "a", "b", "log"), "pair", 0.3, 0.3, 0.0, [0.3] * 8))
    assert chain_selftest.pair_word(table, 0, [_scored_word("carried"), log], ("a",))[0] == case["table_carried_skewed_correlation_carried"]
    assert chain_selftest.pair_word(table, 0, None, ())[0] == case["table_carried_log_not_judged"]
    assert chain_selftest.pair_word(table, 0, [], ())[0] == case["mutant_table_alone"] == "carried"
    halves = [0.004, 0.005, 0.003, 0.004]
    inside = chain_selftest.Estimate(("pair", "a", "b", "L0"), "pair", 0.0, 0.003, 0.2, halves, "distance")
    far = chain_selftest.Estimate(("pair", "a", "b", "L0"), "pair", 0.0, 0.15, 0.2, halves, "distance")
    assert chain_selftest.one_word(chain_selftest.score(inside, 20000, 20000, 1)) == case["one_distance_inside"]
    assert chain_selftest.one_word(chain_selftest.score(far, 20000, 20000, 1)) == case["one_distance_far"]
    between = chain_selftest.Estimate(("pair", "a", "b", "code"), "pair", 0.35, 0.30, 0.0, [0.36, 0.34, 0.35, 0.35, 0.36, 0.34, 0.35, 0.35])
    assert chain_selftest.one_word(chain_selftest.score(between, 20000, 200000, 11)) == case["one_correlation_between"]
    # A correlation the sample shows none of reads approximate, never not carried; MUTANT: that rule dropped.
    unshown = chain_selftest.Estimate(("pair", "a", "b", "code"), "pair", 0.005, -0.02, -0.03, [0.02, -0.01, 0.0, 0.01, 0.01, 0.0, 0.005, 0.005])
    assert chain_selftest.one_word(chain_selftest.score(unshown, 20000, 20000, 11)) == case["one_correlation_unshown"] == "approximate"
    assert case["mutant_unshown_without_the_rule"] == "not carried"


def test_a_pairs_table_is_read_at_the_finest_level_its_cells_support():
    """RULINGS 3 (4): L0, then L1, then L2, every cell holding rows at 22 on the sample and 11 in each half; MUTANT: halves unread."""
    case = _VECTORS["levels"]
    sparse = ({0: 300, 1: 21}, [{0: 150, 1: 11}] * 8)
    halved = ({0: 300, 1: 30}, [{0: 150, 1: 15}] * 7 + [{0: 150, 1: 10}])
    merged = ({0: 330}, [{0: 165}] * 8)
    assert chain_selftest.first_supported_level([sparse, halved, merged]) == case["sparse_then_merged"] == 2
    assert chain_selftest.first_supported_level([merged, merged, merged]) == case["full_at_l0"] == 0
    assert chain_selftest.first_supported_level([sparse, halved, halved]) == case["none"] == -1
    assert case["mutant_without_halves"] == 1


def _sparse_pair_inputs(rows=4000, small=18):
    """Two invented columns whose L0 table holds one cell of `small` rows: band 3 of `p` beside band 3 of `q`."""
    rng = random.Random(31)
    ladder = _ladder("p", 4, (0, 0, 1, 1), (0, 0, 0, 0), (True, True, True, True))
    first, second = [], []
    for row in range(rows):
        a = rng.randrange(3)
        first += [a]
        second += [rng.randrange(3)]
    for row in range(small):
        first[row], second[row] = 3, 3
    for row in range(small, small + 400):
        first[row], second[row] = 3, rng.randrange(3)
    columns = tuple(chain.SampleColumn(name, "categorical", dataclasses.replace(ladder, column=name), bytes(codes), None, None, None, None, -1, None, None, None)
                    for name, codes in (("p", first), ("q", second)))
    inputs = chain.SelftestInputs(rows, tuple(rng.getrandbits(64) for _ in range(rows)), columns,
                                  (chain_rules.Family("p", 0, (), None, ()), chain_rules.Family("q", 0, (("p", 0),), 0, ())), ())
    return inputs


def test_a_pair_with_a_sparse_cell_at_l0_is_judged_at_l1():
    """RULINGS 3 (4) through the builder: an 18-row cell at L0 moves the pair to L1; MUTANT: L0 always (the first build)."""
    inputs = _sparse_pair_inputs()
    seeds = chain_selftest.row_seeds(inputs.hashes)
    groups = chain_selftest.groups_of(seeds)
    sampled = chain_selftest.sample_view(inputs)
    views = {"sample": sampled, "twin": sampled, "shuffle": sampled}
    estimate, level = chain_selftest.pair_table(views, groups, inputs.columns[0], inputs.columns[1])
    assert level == 1 and estimate is not None and estimate.key[3] == "L1"
    full = _sparse_pair_inputs(small=60)
    seeds = chain_selftest.row_seeds(full.hashes)
    views = {side: chain_selftest.sample_view(full) for side in ("sample", "twin", "shuffle")}
    assert chain_selftest.pair_table(views, chain_selftest.groups_of(seeds), full.columns[0], full.columns[1])[1] == 0


def test_f1s_label_levels_are_the_oracles():
    """RULINGS 3 (2)(b): a label's levels read as outcomes: 22 rows or more, its empty band aside, the ten largest."""
    case = _VECTORS["labels"]
    codes = [0] * 40 + [1] * 22 + [2] * 21 + [3] * 60 + [4] * 30 + list(range(5, 17)) * 25
    ladder = _ladder("lab", 17, tuple([0] * 17), tuple([0] * 17), tuple([False] * 17))
    column = chain.SampleColumn("lab", "categorical", ladder, bytes(codes), None, None, None, None, case["missing"], None, None, None)
    assert chain_selftest.label_levels(column) == case["levels"]
    assert chain_selftest.LABEL_LEVELS == 10


def test_a_table_without_relationships_judges_no_family_between_columns_the_line():
    """RULINGS 4 (6): the line is twice the chance share of joint estimates, P(|t_4| > 2) = 0.116."""
    case = _VECTORS["unrelated"]
    assert chain_selftest.NO_RELATIONSHIP_UNDER == case["line"] == 2 * chain_selftest.CHANCE_JOINT
    assert case["null_table_nine_in_a_hundred"] and not case["related_thirty_in_a_hundred"]
    assert chain_selftest.sees_no_relationship(9, 100) is case["null_table_nine_in_a_hundred"]
    assert chain_selftest.sees_no_relationship(30, 100) is case["related_thirty_in_a_hundred"]
    # LANE ST RULINGS 6 (1)(a): the SHARE alone. Two joint coefficients of
    # six read a third, over twice chance: the family is judged, its shares
    # falling back to every supported estimate. MUTANT: repair 1's count
    # clause (fewer than five joint) leaves it unjudged.
    assert chain_selftest.sees_no_relationship(2, 6) is case["two_of_six"] is False
    assert case["mutant_two_of_six_with_the_count_clause"] is True


# -- REPAIR 1: THE RULES THROUGH run() AND THE ESTIMATE BUILDERS (RULINGS 3 (5)) ----


def _with_label(placed=False, rows=6000):
    """The related fixture and a label of three levels following `u`, placed in `u`'s family or dealt alone."""
    inputs, words = _related_inputs(rows)
    rng = random.Random(77)
    u = list(inputs.columns[0].l0)
    codes = bytes(min(2, code // 2 + (1 if rng.random() < 0.2 else 0)) if rng.random() < 0.9 else rng.randrange(3) for code in u)
    three = chain_rules.Ladder("lab", (("a",), ("b",), ("c",)), ((0, 1, 2), (0, 1, 2), (0, 0, 0)), (3, 3, 1), (0, 0, 0), (False, False, False))
    label = chain.SampleColumn("lab", "categorical", three, codes, None, None, None, None, -1, None, None, None)
    family = chain_rules.Family("lab", 0, (("u", 0),), 0, ()) if placed else chain_rules.Family("lab", 0, (), None, ())
    names = [column.name for column in inputs.columns]
    words = words + [{"columns": [name, "lab"], "word": "exact" if placed and name == "u" else "implied"} for name in names]
    return dataclasses.replace(inputs, columns=inputs.columns + (label,), families=inputs.families + (family,)), words


def _family(judged, code):
    return [one for one in judged.families if one.family == code][0]


def test_f1_reads_each_level_of_a_label_column_as_a_part(monkeypatch):
    """RULINGS 3 (2)(b): a label's levels by the bands of every other column are F1's own part, and F1 reads the worst.

    The label follows `u` but the chain deals it alone, so its part reads
    not carried and so does F1. MUTANT: the part dropped reads F1 carried.
    """
    inputs, words = _with_label()
    judged = chain_selftest.run(inputs, words, 11, keys=1)
    f1 = _family(judged, "F1")
    parts = {part[0]: part[1] for part in f1.parts}
    assert parts[chain_selftest.LEVEL_PART] == chain_selftest.NOT_CARRIED, f1
    assert f1.word == chain_selftest.NOT_CARRIED
    monkeypatch.setattr(chain_selftest, "_label_rate_estimates", lambda *args, **kwargs: [])
    dropped = _family(chain_selftest.run(inputs, words, 11, keys=1), "F1")
    assert chain_selftest.LEVEL_PART not in {part[0] for part in dropped.parts} and dropped.word == chain_selftest.CARRIED


def test_the_ceiling_names_a_skewed_column_through_run():
    """RULINGS 3 (5): a skewed column on the related fixture is named under F2 to F6 and on each pair holding it.

    MUTANT: the ceiling dropped in run() (no column named) is red here.
    """
    inputs, words = _related_inputs()
    skewed = tuple(dataclasses.replace(column, skew=0.3) if column.name == "v" else column for column in inputs.columns)
    judged = chain_selftest.run(dataclasses.replace(inputs, columns=skewed), words, 11, keys=1)
    for code in ("F2", "F3", "F4", "F5", "F6"):
        assert _family(judged, code).ceiling == ("v",), code
    for pair in judged.pairs:
        assert pair.ceiling == (("v",) if "v" in pair.columns else ())
        if "v" in pair.columns:
            assert pair.word != chain_selftest.CARRIED
    text = chain_selftest.report_text(judged, words, (), {}, "t", "/k")
    assert "On the raw or log scale of v (skewed): at best approximate." in text


def _flags_with(events_in_band, rows=4000):
    """A 0/1 outcome over two bands: band 1 holds 600 rows and `events_in_band` events, band 0 the rest at one in three."""
    flags, codes = [], []
    for row in range(rows):
        band = 1 if row < 600 else 0
        codes += [band]
        flags += [1.0 if (row < events_in_band if band else row % 3 == 0) else 0.0]
    return flags, codes


def test_a_band_of_21_events_gives_no_rate():
    """RULINGS 3 (5): through `_rates_in_cells`, a band of 21 events yields no rate; one of 220 does; MUTANT: support dropped."""
    seeds = chain_selftest.row_seeds(tuple(range(4000)))
    groups = chain_selftest.groups_of(seeds)
    for events, expected in ((21, False), (220, True)):
        flags, codes = _flags_with(events)
        left = {}
        found = chain_selftest._rates_in_cells("F1", ("F1", "y", "x", "band"), {"sample": flags, "twin": flags, "shuffle": flags},
                                               {"sample": codes, "twin": codes, "shuffle": codes}, groups, left)
        assert any(one.key[-1] == "1" for one in found) is expected
        assert ("rate cells" in left) is (not expected)


def test_an_unsupported_design_gives_no_model_estimates():
    """RULINGS 3 (5): through `_model_estimates`, a predictor level of 21 events gives no estimate and is counted."""
    rows = 2000
    view = chain_selftest.View(rows, {"x": [0] * rows, "y": [0] * rows}, {
        "x": [1.0 if row < 200 else 0.0 for row in range(rows)],
        "y": [1.0 if (row < 21 if row < 200 else row % 3 == 0) else 0.0 for row in range(rows)],
    }, {})
    views = {"sample": view, "twin": view, "shuffle": view}
    groups = bytes(row % 16 for row in range(rows))
    left = {}
    model = chain_selftest.Model("F4", "y", ("x",))
    assert chain_selftest._model_estimates(model, views, groups, {"x": (0.1, 0.3), "y": (0.3, 0.46)}, [], left) == []
    assert left == {"models": 1}


def test_a_shuffle_landing_inside_voids_the_run(monkeypatch):
    """RULINGS 3 (5): the shuffle's bar moved past every share voids the run through run(); MUTANT: the shuffle unread.

    A run is void where the shuffle lands inside on the joint estimates
    within SHUFFLE_UNDER of the replicate's share, so at 2 (not -1, which
    under this sign is a bar no shuffle reaches) every shuffle is within it.
    """
    inputs, words = _related_inputs()
    monkeypatch.setattr(chain_selftest, "SHUFFLE_UNDER", 2.0)
    voided = chain_selftest.run(inputs, words, 11, keys=1)
    assert not voided.controls.held and "shuffle" in voided.controls.why
    assert all(one.word == chain_selftest.NOT_JUDGED for one in voided.families + voided.pairs)


def test_a_private_folder_holding_a_twin_is_refused(tmp_path):
    """RULINGS 3 (5): a named private folder holding a twin file is refused in plain words; MUTANT: the scan dropped."""
    data = _installation(tmp_path)
    holding = tmp_path / "holding"
    holding.mkdir(mode=0o700)
    if os.name != "nt":
        holding.chmod(0o700)
    (holding / "old-twin.csv").write_text("a\n1\n", encoding="utf-8", newline="\n")
    code, said, _out = _profile(tmp_path, data, private_folder=str(holding))
    assert code == 0, said
    assert "holds a description or a twin" in said
    assert sorted(entry.name for entry in holding.iterdir()) == ["old-twin.csv"]


def test_the_private_report_states_its_precision(switched):
    """RULINGS 3 (5): the precision line, with the sample's and the table's rows; MUTANT: the line dropped."""
    text = switched["private"].read_text(encoding="utf-8")
    found = [line for line in text.splitlines() if line.startswith("Judged on a sample of ")]
    assert len(found) == 1
    import re

    said = re.fullmatch(r"Judged on a sample of (\d+) rows of your (\d+)-row table, at the precision of your whole table\.", found[0])
    assert said is not None and 0 < int(said.group(1)) <= int(said.group(2))


def test_a_family_reads_the_worst_word_of_its_parts_through_run(monkeypatch):
    """RULINGS 3 (5): a family whose one part reads not carried reads not carried; MUTANT: the worst-of-parts rule dropped."""
    real = chain_selftest.word_of

    def one_part_worse(scored):
        found = real(scored)
        parts = {one.estimate.part for one in scored}
        word = chain_selftest.NOT_CARRIED if parts == {"three columns together"} else chain_selftest.CARRIED
        return (word,) + found[1:]

    monkeypatch.setattr(chain_selftest, "word_of", one_part_worse)
    inputs, words = _related_inputs()
    f1 = _family(chain_selftest.run(inputs, words, 11, keys=1), "F1")
    assert "three columns together" in {part[0] for part in f1.parts}
    assert f1.word == chain_selftest.NOT_CARRIED and f1.why == "the worst word of its parts"


def test_f7_is_never_judged_while_the_chain_reads_one_row_a_person():
    """RULINGS 3 (5): F7 reads not judged on every judged run; MUTANT: F7 judged as any other family."""
    inputs, words = _related_inputs()
    f7 = _family(chain_selftest.run(inputs, words, 11, keys=1), "F7")
    assert f7.word == chain_selftest.NOT_JUDGED and "several rows a person" in f7.why


def test_the_self_tests_work_and_memory_stand_flat_in_the_tables_rows(monkeypatch):
    """RULINGS 3 (6), skeptic 12a: one sample as part of 200,000 rows or of 2,000,000: the same estimates and the same peak."""
    import gc
    import tracemalloc

    inputs, words = _related_inputs(2000)
    # One run first, unmeasured: the interpreter's own first-call
    # allocations (caches, interned values) fall outside both peaks.
    chain_selftest.run(dataclasses.replace(inputs, rows=1000000), words, 11, keys=1)
    found = {}
    for rows in (200000, 2000000):
        counted = []
        real_score = chain_selftest.score

        def counting(estimate, sample, table_rows, floor, real_score=real_score, counted=counted):
            counted.append(estimate.key)
            return real_score(estimate, sample, table_rows, floor)

        monkeypatch.setattr(chain_selftest, "score", counting)
        gc.collect()
        tracemalloc.start()
        chain_selftest.run(dataclasses.replace(inputs, rows=rows), words, 11, keys=1)
        peak = tracemalloc.get_traced_memory()[1]
        tracemalloc.stop()
        monkeypatch.setattr(chain_selftest, "score", real_score)
        found[rows] = (counted, peak)
    assert found[200000][0] == found[2000000][0]
    assert abs(found[200000][1] - found[2000000][1]) <= 0.10 * found[200000][1]


def test_a_switched_twin_whose_chain_is_off_grades_every_family_n_and_gives_no_reason(switched, tmp_path):
    """RULINGS 3 (6), skeptic 7 (RULINGS 1 (9)): no chain published, the block grades every family N, no reason, no pair.

    MUTANT: the independence paragraph printed for a switched description
    whose chain is off (the build) is red here.
    """
    document = json.loads((switched["out"] / "clinic-profile.json").read_text(encoding="utf-8"))
    document["relationships"]["statistical"] = None
    import fixtures

    path = fixtures.write_profile(tmp_path, "clinic-off-profile.json", document)
    loaded = contract.load_profile(str(path), chain=True)
    assert loaded.relationships.switched and not loaded.relationships.ladder
    report = rendering.report(loaded, generation.generate(loaded, 1))
    block = _block(report)
    expected = ["1. " + chain_grades.HEADING] + [f"{code} {name}: {grade}." for code, name, grade in chain_grades.off_grades()]
    assert block == expected + [chain_grades.ONCE_LINE]
    assert all(line.endswith(": N (not carried).") for line in block[1:10])
    assert "1. EVERY COLUMN WAS BUILT ON ITS OWN" not in report and "2. EVERY ROW WAS BUILT ON ITS OWN" in report
    for reason in (chain.OFF_PERSON, chain.OFF_FEW, "no chain is published", "because", chain_grades.PAIRS_HEADING[:20]):
        assert all(reason not in line for line in block)
    assert chain_grades.PAIRS_HEADING not in report


# -- REPAIR 1: TWO TABLES OF THE BATTERY ------------------------------------------


def _described_chain(tmp_path, name, rows, seed=1):
    """An invented table of the battery's, described with the chain behind its switch under the test key."""
    import analyst_tables

    from synthtwin import profile, reading, taxonomy

    path = tmp_path / f"{name}-{rows}.csv"
    path.write_text(analyst_tables.text(name, rows, seed), encoding="utf-8", newline="\n")
    settings = taxonomy.Settings()
    table = reading.read_table(str(path), small_cell_floor=settings.small_cell_floor)
    document = profile.build_document(table, settings, [], [], [])
    chained = chain.describe(table, document, settings, chain.ChainSwitch(f"{name}-{rows}", _KEY, rows_per_person=chain.ROWS_UNASKED))
    return chained.selftest, chained.statistical["words"]


def test_the_null_table_takes_the_branch_that_sees_no_relationship(tmp_path, monkeypatch):
    """RULINGS 4 (6): on ST5 (no column related to another) no family between columns is judged, family by family.

    5,000 rows, a test size. Every family's share of joint estimates stands
    under twice chance, so each reads `not judged` for that reason (or for
    too few estimates); no correlation reads `not carried`, none being
    shown. MUTANT: the branch dropped judges ST5's families.
    """
    inputs, words = _described_chain(tmp_path, "ST5", 5000)
    judged = chain_selftest.run(inputs, words, 11, keys=1)
    assert judged.controls.held
    for code in ("F1", "F2", "F3", "F4", "F5", "F6", "F9"):
        family = _family(judged, code)
        assert family.word == chain_selftest.NOT_JUDGED and (family.unrelated or "fewer than" in family.why), family
    assert _family(judged, "F1").unrelated and "under twice the share chance gives" in _family(judged, "F1").why
    monkeypatch.setattr(chain_selftest, "NO_RELATIONSHIP_UNDER", 0.0)
    judged_anyway = chain_selftest.run(inputs, words, 11, keys=1)
    assert any(one.word != chain_selftest.NOT_JUDGED for one in judged_anyway.families if one.family in ("F1", "F2", "F9"))


def test_a_skewed_pair_exact_on_its_table_is_not_called_carried_at_20000_rows(tmp_path, monkeypatch):
    """RULINGS 4 (1)(d): BC-ARCH 4.2's design at 20,000 rows: crp and cost hold one family, yet crp|cost never reads carried.

    MUTANT: the pair read on its cross-table alone reads crp|cost carried.
    """
    inputs, words = _described_chain(tmp_path, "SD", 20000)
    exact = {(entry["columns"][0], entry["columns"][1]): entry["word"] for entry in words}
    assert exact[("crp", "cost")] == "exact"
    judged = chain_selftest.run(inputs, words, 11)
    crp_cost = [pair for pair in judged.pairs if pair.columns == ("crp", "cost")][0]
    assert crp_cost.word != chain_selftest.CARRIED and crp_cost.ceiling, crp_cost
    real = chain_selftest.pair_word
    monkeypatch.setattr(chain_selftest, "pair_word", lambda table, level, correlations, ceiling: real(table, level, [], ()))
    alone = [pair for pair in chain_selftest.run(inputs, words, 11, keys=1).pairs if pair.columns == ("crp", "cost")][0]
    assert alone.word == chain_selftest.CARRIED


# -- REPAIR 1: THE PRIVATE REPORT'S NEW LINES ---------------------------------------


def test_f1s_shared_line_grades_three_columns_across_families_n():
    """RULINGS 3 (6), skeptic 6: contract 4.6b.8's N for three or more columns across families; MUTANT: the part left out."""
    grades = {code: grade for code, _name, grade in chain_grades.family_grades(False, False)}
    assert grades["F1"].endswith("; N for three or more columns across families")
    assert "E (exact at the published bands) inside each family of columns" in grades["F1"]


def test_the_twins_numbers_stand_in_only_for_what_is_judged_carried():
    """RULINGS 4 (1)(b): WHICH_TWIN as amended; an exact pair is exact at its family's published bands; MUTANT: the old sentence."""
    assert chain_selftest.WHICH_TWIN.startswith(
        "WHICH TWIN TO USE. Where a pair or an analysis is judged carried, the twin's numbers can stand in for your table's.")
    assert "Where a pair reads exact or pinned" not in chain_selftest.WHICH_TWIN
    assert chain_selftest.EXACT_AT in chain_selftest.WHICH_TWIN
    assert "develop the code on the twin and run it unchanged on your real table" in chain_selftest.WHICH_TWIN


def _judged_for_report(sample, rows):
    family = chain_selftest.FamilyWord("F2", "correlations", chain_selftest.APPROXIMATE, "outside", 9, 5, 0.8,
                                       keys=("carried", "approximate", "carried"))
    families = tuple(family if code == "F2" else chain_selftest.FamilyWord(code, name, chain_selftest.NOT_JUDGED, "-", 0, 0, None)
                     for code, name in chain_selftest.FAMILY_NAMES)
    held = chain_selftest.Controls(0.8, 0.1, True, "held", 0.4)
    return chain_selftest.Judged(families, (), held, sample, rows, 0, (),
                                 ("the linear model of a on b, c", "the logistic model of y on a"),
                                 (("rate cells", 7), ("models", 1), ("RULE W2", 2)), (held, held, held))


def test_the_private_report_keeps_each_key_names_its_models_and_counts_what_was_left_out():
    """RULINGS 3 (2)(a), 3 (6) 12b and 4 (8): each key's word, the models by outcome, the left-out counts and RULE W2's sentence.

    MUTANTS: any of the four lines dropped.
    """
    text = chain_selftest.report_text(_judged_for_report(20000, 20000), [], (), {}, "t", "/k")
    assert "judged approximate (outside; 5 of 9 supported estimates inside, the replicate 80%; under the trial keys: carried, approximate, carried)" in text
    assert "  The linear model of a on b, c." not in text and "  the linear model of a on b, c." in text
    assert f"At most {chain_selftest.MODELS_A_KIND} outcomes of each kind are modelled" in text
    assert "7 rate cells, 0 correlations, 1 models and 0 pairs' tables at every level." in text
    assert "Left not judged by RULE W2: 2 pairs. " + chain_selftest.RULE_W2_SCOPE in text
    assert "every binary column" not in text
    assert "Each word is the worst of 3 trial keys, run one after another." in text


def test_a_sample_smaller_than_the_table_says_pairs_underclaim():
    """RULINGS 4 (4): on a sample smaller than the table the report says once that pairs read approximate more often."""
    smaller = chain_selftest.report_text(_judged_for_report(20000, 200000), [], (), {}, "t", "/k")
    assert smaller.count(chain_selftest.SMALLER_SAMPLE) == 1
    whole = chain_selftest.report_text(_judged_for_report(20000, 20000), [], (), {}, "t", "/k")
    assert chain_selftest.SMALLER_SAMPLE not in whole


# -- REPAIR 2: THE PERSON'S OWN FILES (LANE ST RULINGS 5 (1), Codex's items 1, 2 and 8) --


def _custom_profile(folder, data, table, private_folder=None, name=None, extra=(), rows_per_person=asking.ANSWER_ONE_ROW_EACH):
    """One switched profile run of `table` into `folder`/out, the open questions left open.

    The subject question (lane GRa, plan P4-D449) is answered in advance
    by `rows_per_person`, `one row each` unless a case says otherwise, as
    the line's other chain tests answer it (batch 4q's merge of lane ST).
    """
    out = folder / "out"
    out.mkdir(parents=True, exist_ok=True)
    run = cli.ChainRun(folder=str(data), private_folder=private_folder, name=name, rows_per_person=rows_per_person)
    code, said = _quiet(["profile", str(table), "--out-dir", str(out)] + list(extra), run)
    return code, said, out


def _private_dir(folder, name="private"):
    held = folder / name
    held.mkdir(mode=0o700)
    if os.name != "nt":
        held.chmod(0o700)
    return held


@pytest.mark.parametrize("ending", [".txt", ".new"])
def test_the_private_report_never_lands_on_the_table_it_describes(tmp_path, ending):
    """Codex's item 1: the table stored where the report or its temporary name would go is refused, the table untouched.

    The table's own bytes sit at the private report's file (or at its
    temporary name) in the private folder named for the run, under the
    name `clinic`. MUTANT: the samefile test dropped writes the report over
    the table (or removes it at the temporary name).
    """
    data = _installation(tmp_path)
    private = _private_dir(tmp_path)
    stem = chain_selftest.report_stem("clinic") + "-" + chain_selftest.REPORT_FILE
    table = chain_twins._write(private / (stem + ending), chain_twins.HEADER, chain_twins._clinic_rows(800))
    before = table.read_bytes()
    code, said, out = _custom_profile(tmp_path, data, table, private_folder=str(private), name="clinic")
    assert code == 0, said
    assert table.read_bytes() == before
    assert "is the table you asked synthtwin to describe under another name" in said, said
    assert sorted(entry.name for entry in private.iterdir()) == [table.name]


def test_two_names_never_share_one_private_report(tmp_path):
    """Codex's item 1: `trial A` and `trial_A` (and names differing only in case) keep a report each; MUTANT: the bare stem."""
    assert chain_selftest.report_stem("trial A") != chain_selftest.report_stem("trial_A")
    assert chain_selftest.report_stem("Clinic").lower() != chain_selftest.report_stem("clinic").lower()
    assert chain_selftest.report_stem("clinic") == chain_selftest.report_stem("clinic")
    assert chain_selftest.report_stem("trial A").startswith("trial_A-")
    table = chain_twins._write(tmp_path / "clinic.csv", chain_twins.HEADER, chain_twins._clinic_rows(800))
    private = _private_dir(tmp_path)
    for name in ("trial A", "trial_A"):
        own = tmp_path / name.replace(" ", "-")
        own.mkdir()
        code, said, _out = _custom_profile(own, _installation(own), table, private_folder=str(private), name=name)
        assert code == 0, said
    reports = sorted(entry.name for entry in private.iterdir())
    assert reports == sorted(_report_name(name) for name in ("trial A", "trial_A"))


def test_a_network_private_folder_is_refused_before_any_filesystem_call(tmp_path, monkeypatch):
    """Codex's item 2: the folder AS GIVEN passes the locality gate before anything looks at it (a recorded-call fake).

    `\\\\server\\share\\private` is refused on the string, and no stat, link
    or listing call ever names it. MUTANT: the folder resolved and listed
    first (the build) records those calls.
    """
    data = _installation(tmp_path)
    table = chain_twins._write(tmp_path / "clinic.csv", chain_twins.HEADER, chain_twins._clinic_rows(800))
    recorded = []
    for name in ("stat", "lstat", "listdir", "scandir", "mkdir"):
        real = getattr(os, name)

        def recording(*args, real=real, name=name, **kwargs):
            if args and isinstance(args[0], (str, os.PathLike)) and "server" in os.fspath(args[0]):
                recorded.append((name, os.fspath(args[0])))
            return real(*args, **kwargs)

        monkeypatch.setattr(os, name, recording)
    code, said, out = _custom_profile(tmp_path, data, table, private_folder="\\\\server\\share\\private")
    assert code == 0, said
    assert recorded == []
    assert "The private report was not written." in said and "two slashes" in said
    assert (out / "clinic-profile.json").exists() and (out / "clinic-questions.json").exists()
    validated = []
    real_gate = cli.validate_local_path

    def gate(raw, *, purpose):
        validated.append((raw, purpose))
        return real_gate(raw, purpose=purpose)

    monkeypatch.setattr(cli, "validate_local_path", gate)
    again = tmp_path / "again"
    again.mkdir()
    _custom_profile(again, _installation(again), table, private_folder="\\\\server\\share\\private")
    assert ("\\\\server\\share\\private", "private folder") in validated


@pytest.mark.skipif(os.name == "nt" or (hasattr(os, "geteuid") and os.geteuid() == 0), reason="a POSIX mode no account but root bypasses")
def test_a_private_folder_no_one_may_read_never_moves_the_run(tmp_path):
    """Codex's item 8: a named folder of mode 000 leaves exit 0, every shared byte and the questions file, and says so.

    MUTANT: the folder listed outside the report's own handler ends the
    run with a traceback before the questions file is written.
    """
    table = chain_twins._write(tmp_path / "clinic.csv", chain_twins.HEADER, chain_twins._clinic_rows(800))
    plain = tmp_path / "plain"
    plain.mkdir()
    code, said, out_plain = _custom_profile(plain, _installation(plain), table)
    assert code == 0, said
    closed = tmp_path / "closed"
    closed.mkdir()
    locked = _private_dir(closed, "locked")
    locked.chmod(0o000)
    try:
        code, said, out = _custom_profile(closed, _installation(closed), table, private_folder=str(locked))
    finally:
        locked.chmod(0o700)
    assert code == 0, said
    assert "could not be looked into" in said
    for name in ("clinic-profile.json", "clinic-profile.txt", "clinic-questions.json"):
        assert (out / name).read_bytes() == (out_plain / name).read_bytes(), name
    assert list(locked.iterdir()) == []


# -- REPAIR 2: THE JUDGED WORDS (LANE ST RULINGS 5 (2) to (4) and 6 (1) to (3)) --------


def _family_scored(joint_strong, total, inside=True):
    """`total` coefficients of one model, `joint_strong` of them far from nought (the twin off them where not `inside`)."""
    out = []
    for at in range(total):
        value = 0.9 if at < joint_strong else 0.001
        halves = [value + 0.01, value - 0.01] * 4
        twin = value + (0.001 if inside or at >= joint_strong else 0.5)
        out += [chain_selftest.score(chain_selftest.Estimate(("F4", "y", f"x{at}"), "F4", value, twin, 0.0, halves),
                                     20000, 20000, 11)]
    return out


def test_a_model_with_three_strong_coefficients_of_eight_is_judged():
    """RULINGS 6 (1)(a) and (d): the share alone; three joint coefficients of eight read 0.375, over twice chance.

    MUTANT: repair 1's count clause (fewer than five joint) leaves the model
    unjudged, the oracle's `mutant_three_of_eight_with_the_count_clause`.
    """
    scored = _family_scored(3, 8, inside=False)
    assert sum(1 for one in scored if one.joint) == 3
    found = chain_selftest.family_word("F4", "logistic regression", scored)
    # The twin off its three strong coefficients reads so (not carried),
    # where the count clause left it unjudged and K-BC-11 never saw it.
    assert not found.unrelated and found.word == chain_selftest.NOT_CARRIED, found
    assert _VECTORS["unrelated"]["three_of_eight"] is False
    assert _VECTORS["unrelated"]["mutant_three_of_eight_with_the_count_clause"] is True


def test_a_family_the_share_rule_leaves_says_its_counts_and_nothing_more():
    """RULINGS 6 (1)(b): one joint estimate of twenty is under twice chance: not judged, its counts given, no claim beyond them."""
    found = chain_selftest.family_word("F4", "logistic regression", _family_scored(1, 20))
    assert found.word == chain_selftest.NOT_JUDGED and found.unrelated
    assert found.why.startswith("only 1 of its 20 supported estimates stand beyond their yardstick")
    for claim in ("no relationship", "nothing a twin could carry or miss"):
        assert claim not in found.why
        assert claim not in chain_selftest.NONE_JOINT


def _codex3_inputs(rows=20000, seed=3):
    """Codex's item 3, invented: two identical numbers, 19,960 readings k/6 in +-100, 20 at +1,000,000 and 20 at -1,000,000.

    Every `L0` band is one linear code, so the trial twin keeps both
    columns' codes, and their table, exactly, while the extremes the clip
    folds into codes 0 and 255 part.
    """
    rng = random.Random(seed)
    values = [1000000.0] * 20 + [-1000000.0] * 20 + [rng.randrange(-600, 601) / 6.0 for _row in range(rows - 40)]
    ordered = sorted(values)
    lo, hi = ordered[rows // 100], ordered[rows - rows // 100 - 1]
    codes = bytes(max(0, min(255, int(256 * (value - lo) / (hi - lo)))) for value in values)
    beyond = {row: values[row] for row in range(rows) if values[row] < lo or values[row] > hi}
    ladder = chain_rules.Ladder("a", tuple((f"c{k}",) for k in range(256)),
                                (tuple(range(256)), tuple(k // 16 for k in range(256)), tuple(k // 64 for k in range(256))),
                                (256, 16, 4), tuple(0 for _k in range(256)), tuple(True for _k in range(256)))
    columns = tuple(chain.SampleColumn(name, "continuous", dataclasses.replace(ladder, column=name), codes, codes, None,
                                       bytes([1] * rows), None, -1, 0.0, lo, hi, beyond) for name in ("a", "b"))
    families = (chain_rules.Family("a", 0, (), None, ()), chain_rules.Family("b", 0, (("a", 0),), 0, ()))
    return chain.SelftestInputs(rows, tuple(rng.getrandbits(64) for _ in range(rows)), columns, families, ()), values


def test_a_pair_whose_extremes_part_is_never_called_carried_at_20000_rows(monkeypatch):
    """RULINGS 5 (2), Codex's item 3 at 20,000 rows: table and codes kept, the raw scale lost: not carried, named.

    The real columns' raw Pearson correlation is 1.0; under the trial's own
    row arrangement it falls to about 0.08. MUTANT: the raw scale unread
    (the build and repair 1) reads the pair carried under all three keys.
    """
    import statistics

    inputs, values = _codex3_inputs()
    words = [{"columns": ["a", "b"], "word": "exact"}]
    judged = chain_selftest.run(inputs, words, 11)
    pair = judged.pairs[0]
    assert all(one.held for one in judged.key_controls)
    assert pair.word == chain_selftest.NOT_CARRIED and pair.keys == (chain_selftest.NOT_CARRIED,) * 3, pair
    assert pair.extreme and pair.table == chain_selftest.CARRIED
    assert "its correlation on the code scale carried" in pair.why and "its correlation on the raw scale not carried" in pair.why
    text = chain_selftest.report_text(judged, words, (), {}, "t", "/k")
    assert "      On the raw scale of a and b (extreme values): at best approximate." in text
    source, _moved = chain_selftest.trial_twin(inputs, chain_selftest.row_seeds(inputs.hashes))
    assert statistics.correlation([values[row] for row in source["a"]], [values[row] for row in source["b"]]) < 0.5
    monkeypatch.setattr(chain_selftest, "raw_excess", lambda column: {})
    unread = chain_selftest.run(inputs, words, 11).pairs[0]
    assert unread.word == chain_selftest.CARRIED and not unread.extreme


def test_a_comparison_skipped_is_never_an_affirmation():
    """RULINGS 5 (3), Codex's item 5: five joint estimates inside, four moved by the shuffle (.727 against .455): never carried.

    MUTANT: fewer than five comparisons read as keeping the relationships
    (the build and repair 1) reads carried, the oracle's
    `mutant_few_comparisons_affirmed`.
    """
    halves = [1.025, 0.975, 1.05, 0.95, 1.05, 0.95, 1.05, 0.95]
    estimates = [chain_selftest.Estimate(("F2", "a", f"b{at}", "code"), "F2", 1.0, 1.08, 0.89 if at < 4 else 0.91, halves)
                 for at in range(5)]
    scored = [chain_selftest.score(one, 20000, 20000, 11) for one in estimates]
    assert sum(1 for one in scored if one.recovery is not None) == 4
    found = chain_selftest.word_of(scored)
    assert found[0] in (chain_selftest.NOT_JUDGED, chain_selftest.NOT_CARRIED) and found[0] != chain_selftest.CARRIED
    assert found[0] == _VECTORS["comparisons"]["four_comparisons"] == chain_selftest.NOT_JUDGED
    assert _VECTORS["comparisons"]["mutant_few_comparisons_affirmed"] == chain_selftest.CARRIED
    assert "kept" not in found[1] and "keeping the relationships as a fresh half does" not in found[1]


def test_a_family_moved_in_this_twin_reads_a_on_its_family_lines_too(switched):
    """RULINGS 5 (3), Codex's item 6: F1, F4 and F9 name the moved family and grade it A; MUTANT: the lines before the move."""
    loaded = switched["loaded"]
    family = [one for one in loaded.relationships.chain if one.parents][0]
    moved_twin = dataclasses.replace(switched["twin"], deviations=tuple(switched["twin"].deviations) + (generation._deviation(family.child, "chain", "-", "-", "-"),))
    block = rendering._between_columns_lines(loaded, moved_twin)
    lines = {line.split(" ", 1)[0]: line for line in block if line[:1] == "F"}
    for code in ("F1", "F4", "F9"):
        assert f"except in the families of {family.child}, {chain_grades.MOVED}, which read A (approximate)" in lines[code], lines[code]
    assert lines["F2"] == [line for line in rendering._between_columns_lines(loaded, switched["twin"]) if line.startswith("F2 ")][0]
    unmoved = {line.split(" ", 1)[0]: line for line in rendering._between_columns_lines(loaded, switched["twin"]) if line[:1] == "F"}
    assert chain_grades.MOVED not in unmoved["F1"]


@pytest.mark.parametrize("off", [chain.OFF_FEW, chain.OFF_PERSON])
def test_a_chain_off_private_report_grades_as_its_shared_report_does(off):
    """RULINGS 5 (3), Codex's item 7: with no chain, the private structural grades are the shared block's; MUTANT: E for F1."""
    judged = chain_selftest.run(None, [], 11, off)
    text = chain_selftest.report_text(judged, [], (chain_selftest.OFF_PREFIX + off,), {}, "t", "/k", None, off)
    for code, name, grade in chain_grades.off_grades():
        assert f"  {code} {name}: structural {grade}; judged not judged ({off})." in text, code
    assert "structural E (exact at the published bands)" not in text


def test_a_label_pair_counts_its_support_on_the_complete_cases(monkeypatch):
    """RULINGS 5 (4), Codex's item 4: labels of 488, 16 and 488 complete cases read on two levels; MUTANT: every row counted."""
    rng = random.Random(41)
    rows = 1500
    codes, values = [], []
    for row in range(rows):
        level = 0 if row < 488 else 1 if row < 1004 else 2
        codes += [level]
        values += [None if (level == 1 and row >= 488 + 16) else float(rng.randrange(256))]
    three = chain_rules.Ladder("lab", (("a",), ("b",), ("c",)), ((0, 1, 2), (0, 1, 2), (0, 0, 0)), (3, 3, 1), (0, 0, 0), (False, False, False))
    label = chain.SampleColumn("lab", "categorical", three, bytes(codes), None, None, None, None, -1, None, None, None)
    groups = chain_selftest.groups_of(chain_selftest.row_seeds(tuple(rng.getrandbits(64) for _ in range(rows))))
    assert chain_selftest.label_levels_halved(label, groups, values) == [0, 2]
    assert chain_selftest.label_levels_halved(label, groups) == [0, 1, 2]


def test_a_triple_cell_under_the_support_rule_is_counted_left_out():
    """RULINGS 5 (4), Codex's item 15: a three-column cell of 21 events yields no rate and is counted; MUTANT: no counter."""
    rows = 4000
    flags = [1.0 if (row < 21 or (row >= 600 and row % 3 == 0)) else 0.0 for row in range(rows)]
    x = [1 if row < 600 else 0 for row in range(rows)]
    z = [0] * rows
    view = chain_selftest.View(rows, {"x": x, "z": z}, {}, {})
    views = {"sample": view, "twin": view, "shuffle": view}
    left = {}
    found = chain_selftest._triple_rate_estimates("y", {"sample": flags, "twin": flags, "shuffle": flags}, views,
                                                  bytes(row % 16 for row in range(rows)), ("x", "z"), {"x": (0, 1), "z": (0,)}, left)
    assert not any(one.key[-1] == "1" for one in found)
    assert left["rate cells"] >= 1


def _label_reads(rows):
    """The lines `_label_rate_estimates` runs on a label of three levels by an other column of `rows // 96` bands."""
    import sys

    bands = rows // 96
    labels = [row % 3 for row in range(rows)]
    other = [row // 96 for row in range(rows)]
    view = chain_selftest.View(rows, {"lab": labels, "o": other}, {}, {})
    views = {"sample": view, "twin": view, "shuffle": view}
    groups = bytes((row // 3) % 16 for row in range(rows))
    code = chain_selftest._label_rate_estimates.__code__
    counted = [0]

    def tracer(frame, event, arg):
        if frame.f_code is code:
            def lines(frame, event, arg):
                if event == "line":
                    counted[0] += 1
                return lines
            return lines
        return None

    sys.settrace(tracer)
    try:
        found = chain_selftest._label_rate_estimates("lab", -1, [0, 1, 2], views, groups, {"o": bands})
    finally:
        sys.settrace(None)
    return counted[0], found


def test_a_labels_level_totals_are_counted_once_in_linear_work():
    """RULINGS 5 (4), Codex's item 9 (G4): 3,072, 6,144 and 12,288 rows of 96 a band: the reads grow with the rows, not their square.

    MUTANT: each level's total summed again for every band (the build)
    reads about 16 times the lines at four times the rows.
    """
    small, found = _label_reads(3072)
    assert found and all(one.null == 1 / 3 for one in found)
    large, _found = _label_reads(12288)
    assert large <= 4.4 * small, (small, large)


# -- REPAIR 2: THE GUARDS THE VERIFY FOUND MISSING (LANE ST RULINGS 6 (2)) --------------


def test_run_reads_three_trial_keys_by_default_and_the_report_keeps_each(switched):
    """FIX 2: run() with its default keys judges under three, every word holds three keys; MUTANT: `range(1)` in run()."""
    inputs, words = _related_inputs(3000)
    judged = chain_selftest.run(inputs, words, 11)
    assert len(judged.key_controls) == 3
    assert all(len(one.keys) == 3 for one in judged.families + judged.pairs)
    text = switched["private"].read_text(encoding="utf-8")
    assert "Each word is the worst of 3 trial keys, run one after another." in text and "  Trial key 2: " in text


def _sparse_everywhere(rows=4000, small=18):
    """Two invented columns whose one small cell is kept apart at L0, L1 and L2 alike."""
    inputs = _sparse_pair_inputs(rows, small)
    flat = _ladder("p", 4, (0, 1, 2, 3), (0, 1, 2, 3), (True, True, True, True))
    columns = tuple(dataclasses.replace(column, ladder=dataclasses.replace(flat, column=column.name)) for column in inputs.columns)
    return dataclasses.replace(inputs, columns=columns)


def test_a_pair_sparse_at_every_level_is_not_judged_with_its_reason():
    """FIX 3: no level supports the pair: `pair_table` gives (None, -1) and the pair reads not judged; MUTANT: L0 taken anyway."""
    inputs = _sparse_everywhere()
    seeds = chain_selftest.row_seeds(inputs.hashes)
    views = {side: chain_selftest.sample_view(inputs) for side in ("sample", "twin", "shuffle")}
    assert chain_selftest.pair_table(views, chain_selftest.groups_of(seeds), inputs.columns[0], inputs.columns[1]) == (None, -1)
    judged = chain_selftest.run(inputs, [{"columns": ["p", "q"], "word": "exact"}], 11, keys=1)
    pair = judged.pairs[0]
    assert pair.word == chain_selftest.NOT_JUDGED and pair.table == chain_selftest.NOT_JUDGED and pair.level == -1, pair
    assert dict(judged.left)["pairs' tables"] == 1
    word, why = chain_selftest.pair_word(None, -1, [], ())
    assert word == chain_selftest.NOT_JUDGED and "at every level (L0, L1 and L2)" in why


def test_a_label_level_of_21_events_gives_no_part_estimate():
    """FIX 4: through `_label_rate_estimates`, a label level of 21 rows in a band yields no part; one of 60 does; MUTANT: support dropped."""
    rows = 3000
    labels = [0 if row < 21 else 1 if row < 600 else 2 if row < 1200 else (row % 2) for row in range(rows)]
    other = [0 if row < 1200 else 1 for row in range(rows)]
    view = chain_selftest.View(rows, {"lab": labels, "o": other}, {}, {})
    views = {"sample": view, "twin": view, "shuffle": view}
    left = {}
    found = chain_selftest._label_rate_estimates("lab", -1, [0, 1], views, bytes((row // 2) % 16 for row in range(rows)), {"o": 2}, left)
    keys = {(one.key[1], one.key[4]) for one in found}
    assert ("lab=0", "0") not in keys and ("lab=0", "1") in keys and ("lab=1", "0") in keys
    assert left["rate cells"] >= 1


def test_a_band_of_30_events_with_a_thin_half_gives_no_rate():
    """FIX 4: 30 events in a band, ten of them in one half of the first split: no rate; MUTANT: the halves' rule dropped."""
    rows = 4000
    flags, codes = _flags_with(30, rows)
    groups = bytearray(row % 16 for row in range(rows))
    held = [row for row in range(30)]
    for at, row in enumerate(held):
        groups[row] = (2 * at) % 16 if at < 20 else (2 * at + 1) % 16
    left = {}
    found = chain_selftest._rates_in_cells("F1", ("F1", "y", "x", "band"), {"sample": flags, "twin": flags, "shuffle": flags},
                                           {"sample": codes, "twin": codes, "shuffle": codes}, bytes(groups), left)
    assert not any(one.key[-1] == "1" for one in found)
    assert left["rate cells"] >= 1
    assert sum(1 for row in held if groups[row] & 1) == 10


def test_k_bc_11s_structural_part_counts_a_missed_family_and_spares_a_moved_one():
    """FIX 7: a MISSED family not named moved, holding one exact pair, and one within-column stop read 1, 1 and 1.

    The same family named 'moved in this twin' reads 0 and 0. MUTANT: the
    measurement left unread (`extra = {}`) reads 0 everywhere.
    """
    import analyst_battery as battery

    extra = {"families": [{"child": "a", "parents": ["b"]}], "verdicts": {"0": "MISSED"},
             "pairs": [["a", "b", "exact", "carried", "carried", 0, ["carried"] * 3, True, True, 0.5]],
             "within_stops": ["T/within:c"], "within_robust": 4}
    run = battery.TableRun("T", 20000, 1, battery.Yardstick(battery.Panel({}, {}), {}, set()), {}, {},
                           {"moved": []}, 0.0, 0.0, {}, 0.0, extra)
    found = battery._structural(run)
    assert (found["families"], found["pairs"], found["within"]) == (1, 1, 1)
    named = dataclasses.replace(run, report={"moved": ["a and b"]})
    assert (battery._structural(named)["families"], battery._structural(named)["pairs"]) == (0, 0)


# -- REPAIR 2: THE CHAIN-OFF REASON AND THE REPORT'S WORDS (RULINGS 6 (3), Codex 13, 14, 16) --


def test_a_person_table_with_its_chain_off_says_why_on_every_line(tmp_path):
    """FIX 5 with Codex's items 16 and 7: OFF_PERSON's words reach F7's line, the patient line, and N grades.

    An invented table of 200 people, four rows each, `pid` declared an
    identifier: the chain is off for several rows a person. MUTANTS: the
    prefix read at 24 characters (the build: 'no chain is published for this
    table'); the patient line reading one row a person; F1 graded E.
    """
    data = _installation(tmp_path)
    rng = random.Random(4)
    rows = []
    for person in range(200):
        age = rng.randint(18, 90)
        for _visit in range(4):
            rows += [[f"P{person:05d}", f"{age}", f"{round(100 + age * 0.5 + rng.gauss(0, 8), 1)}", "1" if rng.random() < 0.2 else "0"]]
    table = chain_twins._write(tmp_path / "visits.csv", ["pid", "age", "pressure", "event"], rows)
    code, said, _out = _custom_profile(tmp_path, data, table, extra=["--identifier", "pid"])
    assert code == 0, said
    text = (data / "private-reports" / _report_name("visits")).read_text(encoding="utf-8")
    assert f"  F7 several rows per person: structural N (not carried); judged not judged ({chain.OFF_PERSON})." in text
    assert "This table holds several rows a person, and this description describes none of them" in text
    assert "each row is read as one person's" not in text
    assert "  F1 subgroup rates and cross-tables: structural N (not carried);" in text
    assert chain_selftest.OFF_PREFIX == "no chain is published: " and len(chain_selftest.OFF_PREFIX) == 23
    assert chain._off(chain.OFF_PERSON, {}, [], "").notes[-1] == chain_selftest.OFF_PREFIX + chain.OFF_PERSON


def test_a_skewed_column_with_a_second_code_caps_its_raw_scale_alone():
    """FIX 6: where a second code exists, the raw scale alone reads at best approximate, on family and pair lines alike."""
    family = chain_selftest.FamilyWord("F2", "correlations", chain_selftest.CARRIED, "inside", 9, 9, 0.8, ("crp", "lact"),
                                       logged=("crp",))
    families = tuple(family if code == "F2" else chain_selftest.FamilyWord(code, name, chain_selftest.NOT_JUDGED, "-", 0, 0, None)
                     for code, name in chain_selftest.FAMILY_NAMES)
    pair = chain_selftest.PairWord(("crp", "ward"), chain_selftest.CARRIED, "its correlation on the second code (the log scale) carried",
                                   ("crp",), logged=("crp",))
    judged = chain_selftest.Judged(families, (pair,), chain_selftest.Controls(0.8, 0.1, True, "held"), 100, 1000, 0, ())
    text = chain_selftest.report_text(judged, [{"columns": ["crp", "ward"], "word": "implied"}], (), {}, "t", "/k")
    assert text.count("      On the raw scale of crp (skewed): at best approximate.") == 2
    assert "      On the raw or log scale of lact (skewed): at best approximate." in text
    assert "raw or log scale of crp" not in text


def test_rule_w2s_sentence_states_its_measured_scope():
    """Codex's item 13: never 'only below the table floor'; a yardstick of nought at any size and a raised floor are named."""
    said = chain_selftest.RULE_W2_SCOPE
    assert "only below the table floor" not in said and "binds only below" not in said
    assert "a yardstick of nought is left out at any size" in said and "--smallest-group" in said
    tight = chain_selftest.Estimate(("pair", "a", "b", "L0"), "pair", 0.0, 0.0, 0.2, [0.0, 0.0, 0.0, 0.0], "distance")
    assert not chain_selftest.score(tight, 2000000, 2000000, 11).judged


def test_a_part_line_prints_its_count_on_its_own_basis():
    """Codex's item 14: 15 of 20 joint inside (of 100 supported) is never printed 15 of 100; MUTANT: the joint basis dropped."""
    part = ("each level of a label column", chain_selftest.APPROXIMATE, "-", 100, 15, 20, True)
    plain = ("at the published bands", chain_selftest.CARRIED, "-", 100, 85, 100, False)
    family = chain_selftest.FamilyWord("F1", "subgroup rates and cross-tables", chain_selftest.APPROXIMATE, "the worst word of its parts",
                                       100, 15, 0.8, (), (part, plain), 20, True)
    families = tuple(family if code == "F1" else chain_selftest.FamilyWord(code, name, chain_selftest.NOT_JUDGED, "-", 0, 0, None)
                     for code, name in chain_selftest.FAMILY_NAMES)
    judged = chain_selftest.Judged(families, (), chain_selftest.Controls(0.8, 0.1, True, "held"), 100, 1000, 0, ())
    text = chain_selftest.report_text(judged, [], (), {}, "t", "/k")
    assert "      each level of a label column: judged approximate (15 of its 20 joint estimates inside, of 100 supported)." in text
    assert "      at the published bands: judged carried (85 of 100 supported estimates inside)." in text
    assert "15 of 100" not in text


# -- REPAIR 2: K-BC-11'S HARNESS (LANE ST RULINGS 5 (5), Codex's items 10, 11 and 12) ----


def test_k_bc_11_counts_an_error_against_a_yardstick_of_nought():
    """Codex's item 10: real a = b = i, twin b = 2047 - i: correlations 1 and -1 with h = 0 stand outside every threshold."""
    import analyst_battery as battery

    assert battery._yardsticks_off(-1.0, 1.0, 0.0) == float("inf")
    assert battery._yardsticks_off(1.0, 1.0, 0.0) == 0.0
    pairs = [["a", "b", "implied", "carried", "carried", 0, ["carried"] * 3, False, True, battery._yardsticks_off(-1.0, 1.0, 0.0)]]
    assert battery._pairs_missed(pairs, lambda one: one[3]) == ["a~b"]


def test_k_bc_11s_dates_stop_where_a_present_date_reads_as_none():
    """Codex's item 11: 128 real dates and 128 `bad-date` twin cells: the within-column check stops; MUTANT: coerced to blanks."""
    import analyst_battery as battery

    real = battery.read("when\n" + "\n".join(f"2024-01-{1 + at % 28:02d}" for at in range(128)) + "\n", "real")
    twin = battery.read("when\n" + "\n".join("bad-date" for _at in range(128)) + "\n", "twin")
    plan = battery.within_plan("T", [battery.Column("when", "date", [], None, 0.0)])
    assert battery.run_panel(plan, real).status["T within when"] == "ok"
    assert battery.run_panel(plan, twin).status["T within when"] != "ok"


def test_k_bc_11_counts_unnamed_families_report_by_report():
    """Codex's item 12: one complete report then one with no family lines leaves families unnamed; MUTANT: the union."""
    import analyst_battery as battery

    families = list(battery.REPORT_FAMILIES)
    full = {"block": True, "named": families, "private_named": families}
    empty = {"block": True, "named": families, "private_named": []}

    def one(report):
        return battery.TableRun("T", 20000, 1, battery.Yardstick(battery.Panel({}, {}), {}, set()), {}, {}, report, 0.0, 0.0, {}, 0.0, {})

    found = battery.kpi_11([one(full), one(empty)])
    assert found["families_unnamed_private"] == 10 and found["families_unnamed_shared"] == 0
    assert battery.kpi_11([one(full), one(full)])["families_unnamed_private"] == 0


def test_the_private_report_says_a_pairs_word_belongs_to_this_description(switched):
    """RULINGS 6 (4): the chain is drawn under the description's name, so a pair's word is this description's; said once."""
    text = switched["private"].read_text(encoding="utf-8")
    assert text.count(chain_selftest.PAIRS_BELONG) == 1
    assert text.index(chain_selftest.PAIRS_BELONG) > text.index("PAIRS OF COLUMNS")


def test_a_skewed_pairs_raw_scale_reads_at_best_approximate():
    """RULINGS 5 (2) with BC-ARCH 4.2 item 2: a raw-scale correlation inside its yardstick on a skewed pair reads approximate.

    MUTANT: the ceiling held to the code scale alone reads the pair carried
    on its raw scale.
    """
    raw = dataclasses.replace(_scored_word("carried"), estimate=chain_selftest.Estimate(
        ("pair", "a", "b", "raw"), "pair", 0.3, 0.3, 0.0, [0.3] * 8, "difference", 0.0, chain_selftest.RAW_PART))
    word, why = chain_selftest.pair_word(_scored_word("carried"), 0, [raw], ("a",))
    assert word == chain_selftest.APPROXIMATE
    assert "its correlation on the raw scale (at best approximate: a skewed) approximate" in why
    assert chain_selftest.pair_word(_scored_word("carried"), 0, [raw], ())[0] == chain_selftest.CARRIED


# -- THE FOLLOW-UP (LANE ST RULINGS 7 (1) AND (2)): EVERY COMPARISON PAST THE LINE, FIVE BEHAVIOURS GUARDED --

_PAST = _VECTORS["past_the_line"]
_COUNTED = "estimates beyond their yardstick from their value were the columns unrelated are inside on the trial twin"


def _few_comparison_rows(name):
    """The oracle's three cases of the amendment of 2026-11-06, each `(sample, twin, shuffle, null, halves)` with h = 0.1."""
    even = [0.05, -0.05] * 4
    wide = [0.15, -0.15] + [0.05, -0.05] * 3

    def at(value, twin, shuffle, halves=even):
        return (value, twin, shuffle, 0.0, [value + held for held in halves])

    near_nought = [at(0.06, 0.08, 0.09), at(-0.05, -0.03, -0.02), at(0.04, 0.06, 0.07), at(-0.04, -0.02, -0.01)]
    cases = {
        "censored_logistic": [at(0.87, 0.30, 0.02), at(0.55, 0.15, -0.03), at(0.35, 0.10, 0.01)] + near_nought
        + [at(0.05, 0.07, 0.08, wide)],
        "blank_linear": [at(1.43, 0.12, 0.02), at(1.42, 0.89, -0.01), at(1.39, 0.12, 0.03), at(0.07, 0.15, -0.057)]
        + [at(0.02, 0.03, 0.04), at(0.02, 0.03, 0.01), at(0.02, 0.03, 0.04, wide), at(0.01, 0.02, 0.03, wide)],
        "mixed": [at(0.87, 0.30, 0.02), at(0.55, 0.15, -0.03), at(0.35, 0.33, 0.01)] + near_nought + [at(0.05, 0.07, 0.08)],
    }
    return _scored_rows(cases[name])


def _shape(scored):
    """Joint estimates, comparisons, the replicate inside and the twin inside, counted."""
    return (sum(1 for one in scored if one.joint), sum(1 for one in scored if one.recovery is not None),
            sum(1 for one in scored if one.replicate_inside), sum(1 for one in scored if one.twin_inside))


def test_a_model_missed_past_the_line_on_its_three_strong_coefficients_reads_not_carried():
    """RULINGS 7 (1), HC's geometry: three strong coefficients of eight (8.7, 5.5 and 3.5 yardsticks) missed past the line.

    The replicate inside on seven of eight, the trial twin on five (0.625,
    0.875 less 0.25: near); three comparisons, each past the line on its own
    word: `not carried`, its reason counting none of the three inside. On
    4a00d827 the family read `not judged`, 'inside the yardstick about as
    often as the replicate' the whole of its reason (the oracle's
    `mutant_censored_logistic_before_the_amendment`).
    """
    scored = _few_comparison_rows("censored_logistic")
    assert _shape(scored) == (3, 3, 7, 5)
    found = chain_selftest.family_word("F4", "logistic regression", scored)
    assert found.word == chain_selftest.NOT_CARRIED == _PAST["censored_logistic"], found
    assert not found.few_comparisons and not found.unrelated
    assert found.why.endswith(f"; 0 of its 3 {_COUNTED}"), found.why
    assert _PAST["mutant_censored_logistic_before_the_amendment"] == chain_selftest.NOT_JUDGED


def test_a_linear_model_with_a_comparison_kept_short_of_the_line_is_not_judged_with_its_count():
    """RULINGS 7 (1), BL's geometry: three coefficients near 14 yardsticks outside (0.93, 0.37 and 0.93 of the shuffle's gap).

    The replicate 0.75; four comparisons, the fourth (0.7 yardsticks from
    nought) kept inside: not every comparison stands past the line, so `not
    judged`, the reason giving that none of the three showing a relationship
    is inside, never 'about as often as the replicate' alone. MUTANTS: the
    all-comparisons clause dropped reads `not carried`; the reason without
    the count.
    """
    scored = _few_comparison_rows("blank_linear")
    assert _shape(scored) == (3, 4, 6, 5)
    found = chain_selftest.family_word("F3", "linear regression", scored)
    assert found.word == chain_selftest.NOT_JUDGED == _PAST["blank_linear"] and found.few_comparisons, found
    assert found.why.startswith("inside the yardstick about as often as the replicate over all 8 of its supported estimates")
    assert found.why.endswith(f"; 0 of its 3 {_COUNTED}"), found.why
    assert _PAST["mutant_blank_linear_without_the_all_clause"] == chain_selftest.NOT_CARRIED


def test_mixed_comparisons_read_not_judged_with_the_count():
    """RULINGS 7 (1): three comparisons, one the twin keeps inside and two past the line: `not judged`, the count given.

    MUTANTS: the all-comparisons clause dropped reads `not carried` (the
    oracle's `mutant_mixed_without_the_all_clause`); the reason without the
    count leaves 'about as often as the replicate' its whole reason.
    """
    scored = _few_comparison_rows("mixed")
    assert _shape(scored) == (3, 3, 8, 6)
    found = chain_selftest.family_word("F4", "logistic regression", scored)
    assert found.word == chain_selftest.NOT_JUDGED == _PAST["mixed"] and found.few_comparisons, found
    assert found.why.endswith(f"; 1 of its 3 {_COUNTED}"), found.why
    assert _PAST["mutant_mixed_without_the_all_clause"] == chain_selftest.NOT_CARRIED
    # A part reads the same rule: its own word and reason.
    word, why = chain_selftest.word_of(scored)[:2]
    assert word == chain_selftest.NOT_JUDGED and why.endswith(f"; 1 of its 3 {_COUNTED}")


def test_a_comparison_the_twin_keeps_inside_never_stands_past_the_line():
    """RULINGS 7 (1): a comparison stands past the line where it reads `not carried` on its own, never on its ratio alone.

    Codex's case of RULINGS 5 (3): five joint estimates, all inside on the
    trial twin, four moved by the shuffle at .727 of its gap: `not judged`,
    5 of the 5 counted inside. MUTANT: the ratio alone (the oracle's
    `mutant_four_comparisons_on_the_ratio_alone`) calls it `not carried`.
    """
    halves = [1.025, 0.975, 1.05, 0.95, 1.05, 0.95, 1.05, 0.95]
    estimates = [chain_selftest.Estimate(("F2", "a", f"b{at}", "code"), "F2", 1.0, 1.08, 0.89 if at < 4 else 0.91, halves)
                 for at in range(5)]
    found = chain_selftest.word_of([chain_selftest.score(one, 20000, 20000, 11) for one in estimates])
    assert found[0] == chain_selftest.NOT_JUDGED and found[1].endswith(f"; 5 of its 5 {_COUNTED}"), found
    assert _VECTORS["comparisons"]["mutant_four_comparisons_on_the_ratio_alone"] == chain_selftest.NOT_CARRIED


def test_k_bc_11_records_the_families_the_comparisons_rule_left():
    """RULINGS 7 (1): K-BC-11 counts the family-runs the comparisons rule left and those whose chain twin misses, named.

    MUTANT: the battery's record left unread counts none.
    """
    import analyst_battery as battery

    extra = {"few_comparisons": ["F3", "F4"], "unrelated": ["F9"]}
    run = battery.TableRun("T", 20000, 1, battery.Yardstick(battery.Panel({}, {}), {}, set()), {}, {"chain": [None]},
                           {"judged": {}}, 0.0, 0.0, {}, 0.0, extra)
    with pytest.MonkeyPatch.context() as patched:
        patched.setattr(battery, "_misses_target", lambda r, family: family in ("F4", "F9"))
        patched.setattr(battery, "_structural", lambda r: dict.fromkeys(
            ("families", "pairs", "within", "not_measured", "families_held", "within_read"), 0))
        found = battery.kpi_11([run])
    assert found["families_not_judged_by_the_comparisons_rule"] == 2
    assert found["families_not_judged_by_the_comparisons_rule_missed"] == 1
    assert found["not_judged_by_the_comparisons_rule_missed"] == "T-1 F4"
    assert found["families_not_judged_by_the_share_rule_missed"] == 1 and found["overclaims_judged"] == 0


def _beyond_column(rows, rng):
    """A fine column of `rows` readings within 100 of nought, 1 in 100 rows at plus or minus 1,000,000, its codes clipped."""
    values = [rng.choice((1000000.0, -1000000.0)) if row % 100 == 0 else rng.randrange(-600, 601) / 6.0 for row in range(rows)]
    ordered = sorted(values)
    lo, hi = ordered[rows // 50], ordered[rows - rows // 50 - 1]
    codes = bytes(max(0, min(255, int(256 * (value - lo) / (hi - lo)))) for value in values)
    beyond = {row: values[row] for row in range(rows) if values[row] < lo or values[row] > hi}
    ladder = chain_rules.Ladder("a", tuple((f"c{k}",) for k in range(256)),
                                (tuple(range(256)), tuple(k // 16 for k in range(256)), tuple(k // 64 for k in range(256))),
                                (256, 16, 4), tuple(0 for _k in range(256)), tuple(True for _k in range(256)))
    column = chain.SampleColumn("a", "continuous", ladder, codes, codes, None, bytes([1] * rows), None, -1, 0.0, lo, hi, beyond)
    return column, values


def _raw_pair_estimates(partner_codes, binary, rows=2000):
    """`pair_correlations` of a fine column read beyond its clip and a partner of three labels or two values (a test size)."""
    rng = random.Random(7)
    column, _values = _beyond_column(rows, rng)
    width = 2 if binary else 3
    ladder = chain_rules.Ladder("b", tuple((f"v{k}",) for k in range(width)), (tuple(range(width)),) * 3, (width,) * 3,
                                (0,) * width, (False,) * width)
    partner = chain.SampleColumn("b", "categorical", ladder, bytes(partner_codes), None, None, None,
                                 (0, 1) if binary else None, -1, None, None, None)
    inputs = chain.SelftestInputs(rows, tuple(rng.getrandbits(64) for _ in range(rows)), (column, partner), (), ())
    groups = chain_selftest.groups_of(chain_selftest.row_seeds(inputs.hashes))
    sample = chain_selftest.sample_view(inputs)
    assert len(sample.excess["a"]) == len(column.beyond) > 0
    turned = {name: [(row + rows // 2) % rows for row in range(rows)] for name in ("a", "b")}
    views = {"sample": sample, "twin": sample, "shuffle": chain_selftest.mapped_view(sample, turned)}
    return chain_selftest.pair_correlations(views, groups, column, partner, set())


def test_a_number_and_label_pair_reads_its_correlation_ratio_on_the_raw_scale():
    """RULINGS 7 (2), the verify's (ii): a label partner of a column read beyond its clip gives a raw-scale estimate.

    MUTANT: the label branch's raw scale dropped gives the code scale alone.
    """
    found = _raw_pair_estimates([row % 3 for row in range(2000)], False)
    assert [one.key for one in found] == [("pair", "a", "b", "code"), ("pair", "a", "b", "raw")]
    assert found[1].part == chain_selftest.RAW_PART


def test_a_number_and_two_valued_pair_reads_its_correlation_on_the_raw_scale():
    """RULINGS 7 (2), the verify's (iii): a two-valued partner of a column read beyond its clip gives a raw-scale estimate.

    MUTANT: the two-valued branch's raw scale dropped gives the code scale alone.
    """
    found = _raw_pair_estimates([row % 2 for row in range(2000)], True)
    assert [one.key for one in found] == [("pair", "a", "b", "code"), ("pair", "a", "b", "raw")]
    assert found[1].part == chain_selftest.RAW_PART


def test_describe_hands_the_self_test_each_reading_beyond_the_clip(tmp_path, monkeypatch):
    """RULINGS 7 (2), the verify's (i): Codex's two columns through `chain.describe` at 20,000 rows.

    Both sample columns carry every reading beyond the clip the description
    publishes (380 a column here, the 40 at plus and minus 1,000,000 among
    them), and the pair holds a raw-scale estimate. MUTANT: describe never
    handing them over leaves both None and no raw-scale estimate.
    """
    from synthtwin import profile, reading, taxonomy

    rng = random.Random(3)
    values = [1000000.0] * 20 + [-1000000.0] * 20 + [rng.randrange(-600, 601) / 6.0 for _row in range(19960)]
    rng.shuffle(values)
    path = tmp_path / "cx3.csv"
    path.write_text("a,b\n" + "".join(f"{value:.4f},{value:.4f}\n" for value in values), encoding="utf-8", newline="\n")
    settings = taxonomy.Settings()
    found = reading.read_table(str(path), small_cell_floor=settings.small_cell_floor)
    document = profile.build_document(found, settings, [], [], [])
    chained = chain.describe(found, document, settings, chain.ChainSwitch("cx3", _KEY, rows_per_person=chain.ROWS_UNASKED))
    assert chained.selftest is not None
    held = {column.name: column for column in chained.selftest.columns}
    first, second = held["a"], held["b"]
    written = [float(f"{value:.4f}") for value in values]
    outside = sum(1 for value in written if value < first.lo or value > first.hi)
    assert len(first.beyond or {}) == len(second.beyond or {}) == outside >= 40
    assert sorted(value for value in first.beyond.values() if abs(value) == 1000000.0) == [-1000000.0] * 20 + [1000000.0] * 20
    keys = []
    scored = chain_selftest.score

    def spy(estimate, sample, rows, floor):
        keys.append(estimate.key)
        return scored(estimate, sample, rows, floor)

    monkeypatch.setattr(chain_selftest, "score", spy)
    chain_selftest.judge_one(chained.selftest, chained.statistical["words"], settings.small_cell_floor,
                             chain_selftest.SELFTEST_CONSTANT)
    assert ("pair", "a", "b", "raw") in keys


def test_the_answers_file_at_the_private_reports_name_is_refused_and_left_unchanged(tmp_path):
    """RULINGS 7 (2), the verify's (iv): the questions file you answered, stored at the report's name, is refused, unchanged.

    MUTANT: the answers file dropped from the protected places writes the
    report over it.
    """
    data = _installation(tmp_path)
    private = _private_dir(tmp_path)
    table = chain_twins._write(tmp_path / "clinic.csv", chain_twins.HEADER, chain_twins._clinic_rows(800))
    code, said, out = _custom_profile(tmp_path, data, table, private_folder=str(private), name="clinic")
    assert code == 0, said
    answers = private / _report_name("clinic")
    answers.write_bytes((out / "clinic-questions.json").read_bytes())
    before = answers.read_bytes()
    again = cli.ChainRun(folder=str(data), private_folder=str(private), name="clinic", replace_description=True,
                         rows_per_person=asking.ANSWER_ONE_ROW_EACH)
    code, said = _quiet(["profile", str(table), "--out-dir", str(out), "--answers", str(answers)], again)
    assert code == 0, said
    assert answers.read_bytes() == before
    assert "is the questions file you answered under another name" in said, said
    assert sorted(entry.name for entry in private.iterdir()) == [answers.name]


def test_k_bc_11_reads_a_pair_of_numbers_on_the_raw_scale_beside_its_ranks():
    """RULINGS 7 (2), the verify's (v): ranks that agree and a raw-scale Pearson that parts put the pair outside.

    Two equal invented numbers with 20 rows at each of plus and minus
    1,000,000; on the twin the second's extremes stand just past its other
    readings, every rank kept: Spearman's correlation lands inside, Pearson's
    on the raw scale outside. MUTANT: the raw-scale Pearson dropped leaves
    the pair inside on its ranks alone.
    """
    import analyst_battery as battery

    rng = random.Random(5)
    values = [1000000.0] * 20 + [-1000000.0] * 20 + [rng.randrange(-600, 601) / 6.0 for _row in range(1960)]
    rng.shuffle(values)
    kept = [101.0 if value > 100 else -101.0 if value < -100 else value for value in values]
    real = battery.read("x,y\n" + "".join(f"{value},{value}\n" for value in values), "real")
    twin = battery.read("x,y\n" + "".join(f"{value},{other}\n" for value, other in zip(values, kept)), "twin")
    columns = [battery.Column(name, "number", [], None, 0.0) for name in ("x", "y")]
    plan = battery.pair_plan("T", columns, [("x", "y")], real)
    found = {one.key: one for one in battery.compare(battery.yardstick(plan, real, battery.groups_of(real, "T", 1)),
                                                     battery.run_panel(plan, twin))}
    assert found["T/pair:x~y"].inside
    assert "T/pair_r:x~y" in found and not found["T/pair_r:x~y"].inside, found


# -- BATCH 4q'S MERGE OF LANE ST: THE PRIVATE REPORT BESIDE LANE GRa'S PATIENT LAYER AND SUBJECT QUESTION --


def _visit_table(path, patients, visits):
    """An invented visit table of `patients` people with `visits` rows each, numbers as keys (lane GRa's `_visits`, no dropout)."""
    draw = random.Random(12)
    rows = []
    for patient in range(patients):
        arm = draw.choice(["a", "b"])
        age = draw.randint(30, 80)
        base = draw.gauss(100, 12)
        slope = 1.5 if arm == "b" else 0.3
        for visit in range(visits):
            day = 1 + 30 * visit + draw.randint(0, 5)
            date = f"{2024 + day // 336}-{1 + (day // 28) % 12:02d}-{1 + day % 28:02d}"
            rows += [[f"{patient + 1}", arm, draw.choice(["F", "M"]), f"{age}", date,
                      f"{base + slope * visit + draw.gauss(0, 6):.1f}", draw.choice(["clinic", "home", "phone"])]]
    return chain_twins._write(path, ["pid", "arm", "gender", "age", "visit_date", "value", "site"], rows)


def test_a_patient_layers_private_report_says_what_its_description_carries(tmp_path):
    """The merge's case: where the switched description publishes its patient layer, the private report says so.

    An invented visit table of 1,200 people of four rows each; the subject
    question is answered `pid` from the questions file, as lane GRa's
    command test does, so the description's `grain` and chain are the
    patient layer's. The report reads the patient layer as the description
    writes it, grades each family as a description with a patient layer,
    and says the self-test judges no patient layer, never that no chain is
    published or that each row is one person's. Measured on the merge
    before this case (2,500 people of eight rows, 20,000 rows, through the
    command): all four of those sentences were false. MUTANTS: the patient
    layer read from the description before its chain; the grades and the
    reason chosen as for a table whose chain is off.
    """
    data = _installation(tmp_path)
    private = _private_dir(tmp_path)
    out = tmp_path / "out"
    out.mkdir()
    table = _visit_table(out / "visits.csv", 1200, 4)
    code, said = _quiet(["profile", str(table), "--out-dir", str(out)], cli.ChainRun(folder=str(data), private_folder=str(private)))
    assert code == 0, said
    questions = json.loads((out / "visits-questions.json").read_text(encoding="utf-8"))
    questions[asking.BETWEEN_COLUMNS][asking.ROWS_PER_PERSON]["your_answer"] = "pid"
    answers = tmp_path / "answers.json"
    answers.write_text(json.dumps(questions), encoding="utf-8", newline="\n")
    again = cli.ChainRun(folder=str(data), private_folder=str(private), replace_description=True)
    code, said = _quiet(["profile", str(table), "--out-dir", str(out), "--answers", str(answers)], again)
    assert code == 0, said
    written = json.loads((out / "visits-profile.json").read_text(encoding="utf-8"))
    assert isinstance(written["relationships"]["grain"], dict) and written["relationships"]["grain"]["person"] == "pid"
    assert isinstance(written["relationships"]["statistical"], dict)
    text = (private / _report_name("visits")).read_text(encoding="utf-8")
    assert "  The patient layer stands, by pid." in text
    assert "each row is read as one person's" not in text
    assert "no chain is published" not in text
    assert f"The self-test did not run, so nothing is judged: {chain_selftest.PATIENT_LAYER}." in text
    assert "  F7 several rows per person: structural E for patient-level rates inside a family;" in text
    for code_name, family_name in chain_selftest.FAMILY_NAMES:
        line = [one for one in text.split("\n") if one.startswith(f"  {code_name} {family_name}: structural ")]
        assert len(line) == 1 and line[0].endswith(f"judged not judged ({chain_selftest.PATIENT_LAYER})."), (code_name, line)


def test_a_private_report_whose_subject_question_is_open_says_why_no_chain_stands(tmp_path):
    """The merge's case: while the subject question holds the chain, the patient line gives that reason.

    The invented clinic, its subject question left open: no chain is
    published (`chain.OFF_SUBJECT`), and the report's patient line says
    why, never that each row is read as one person's. MUTANT: the line
    without the subject question's holds.
    """
    data = _installation(tmp_path)
    private = _private_dir(tmp_path)
    table = chain_twins._write(tmp_path / "clinic.csv", chain_twins.HEADER, chain_twins._clinic_rows(800))
    code, said, out = _custom_profile(tmp_path, data, table, private_folder=str(private), name="clinic", rows_per_person="")
    assert code == 0, said
    assert json.loads((out / "clinic-profile.json").read_text(encoding="utf-8"))["relationships"]["statistical"] is None
    text = (private / _report_name("clinic")).read_text(encoding="utf-8")
    assert f"  This description carries no patient layer and no chain between columns: {chain.OFF_SUBJECT}." in text
    assert "each row is read as one person's" not in text
    for off in (chain.OFF_SUBJECT, chain.OFF_NO_PERSON, chain.OFF_HELD_REPEATS):
        assert chain_selftest.patient_lines(None, off) == [f"This description carries no patient layer and no chain between columns: {off}."]
