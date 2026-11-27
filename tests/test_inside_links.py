"""Gate file of lane W5-F14: two twins of one study join by the person column as the two real tables do.

THE GAP IT CLOSES (K-RU-01 family F14, the battery's link of the orders
table T5 to its cohort T1). Each table's twin was made on its own: the
twins' keys met only where both columns happened to be written in one
layout, and how many rows a person holds in one table never followed that
person's columns in the other (orders per patient by diabetes, 3.73
against 1.24 on the real tables of seed 1 at 20,000 rows, 1.67 against
1.59 on their twins). `synthtwin profile TABLE --linked-to OTHER` now
fits, inside, how the two real tables join (`inside_links.fit_zone`), and
`synthtwin generate DESCRIPTION --linked-to OTHER_DESCRIPTION` writes the
twin's persons as persons of OTHER's twin at the same seed
(`inside_links.link`).

WHAT IT HOLDS, each clause red on its mutant (lane W5-F14's report):

* The fit reads the relation: on an invented cohort whose orders follow
  a yes/no column and a number, the fit takes both and not the column
  drawn on its own (mutant: an intercept-only fit).
* The link keeps it: on a second draw of the cohort, the linked twin's
  orders per person by the yes/no column stand near the real ratio, not
  near one (mutant: each person's place drawn from one bin).
* The share found is the real one, and the blocks left unfound keep keys
  of their own that the linked twin does not hold, as written or merged,
  each at least the bound wide (mutant: every block linked).
* No twin key can be a real one: nothing is linked where the bound is
  nought or a key of the linked twin is shorter, merged, than the bound
  (mutant: the width check removed).
* The zone holds no key and its size does not follow the rows (mutant:
  the persons' keys written into the zone).
* Two tables of one study linked to one cohort twin each keep their own
  relation, and their persons meet as on the real tables (mutant: every
  table draws its places from the seed alone).
* Through the commands at the table floor: the orders twin's keys are
  cohort twin keys, the share found is the real one, the relation stands,
  the five checks pass, `validate` judges the linked twin as it judges
  the twin left alone, and a twin built without the option is not linked
  (mutants: `generate` reads no `--linked-to`; `profile` writes no zone).
* The pages: `profile` names the option in its sentence of the record's
  options and stays within 60 lines, `generate` on a line of its own, and
  `twin`, which does not read it, says so (mutants: the option on a line
  of its own on the profile page; the twin command's caution removed).
"""

from __future__ import annotations

import contextlib
import csv
import io
import json
import math
import pathlib
import random

import pytest

import reliability_battery as B
from synthtwin import cli, inside, inside_links, installation, parsing, results, twin_checks

# The invented cohort: a yes/no column, an age, and a label drawn on its own; each person's orders a Poisson count
# of a rate that follows the first two.
PERSONS = 6000
RATE = {"intercept": -0.2, "flag": 1.0, "age": 0.02}
# The bound of a person column written "P" and seven figures: a made-up key is at least this long, merged.
BOUND = 9


def _poisson(r: random.Random, rate: float) -> int:
    k, p = 0, math.exp(-rate)
    total, u = p, r.random()
    while u > total and k < 200:
        k += 1
        p *= rate / k
        total += p
    return k


def _cohort(n: int, seed: int, figures: int = 7) -> "dict[str, list[str]]":
    """An invented cohort: a key of a letter and ``figures`` figures, a yes/no column, an age, a label on its own."""
    r = random.Random(f"links-cohort-{seed}")
    low = 10 ** (figures - 1)
    keys = [f"P{k}" for k in r.sample(range(low, 10 * low), n)]
    flag = ["Y" if r.random() < 0.3 else "N" for _ in range(n)]
    age = [f"{int(min(90.0, max(18.0, r.gauss(55.0, 15.0))))}" for _ in range(n)]
    noise = [r.choice(("A", "B", "C")) for _ in range(n)]
    return {"patient_id": keys, "flag": flag, "age": age, "noise": noise}


def _orders(cohort: "dict[str, list[str]]", seed: int, orphans: int = 0) -> "list[str]":
    """The key column of an invented orders table: each cohort person's rows a Poisson count of its rate."""
    r = random.Random(f"links-orders-{seed}")
    out: "list[str]" = []
    for key, flag, age in zip(cohort["patient_id"], cohort["flag"], cohort["age"]):
        rate = math.exp(RATE["intercept"] + RATE["flag"] * (flag == "Y") + RATE["age"] * (int(age) - 55))
        out += [key] * _poisson(r, rate)
    for at in range(orphans):
        out += [f"Q{7000000 + at}"] * (1 + _poisson(r, 1.5))
    shuffled = list(out)
    r.shuffle(shuffled)
    return shuffled


ORDER = ["patient_id", "flag", "age", "noise"]


def _zone(cohort: "dict[str, list[str]]", child: "list[str]") -> "dict[str, object]":
    parents = inside_links.persons_in(cohort["patient_id"])
    sample = inside_links.fit_sample(len(parents.keys))
    first = {name: [cohort[name][parents.first[at]] for at in sample] for name in ORDER[1:]}
    return inside_links.fit_zone("patient_id", child, parents, sample, first, ORDER, "cohort.csv")


def _checked(zone: "dict[str, object]") -> inside_links.Zone:
    found = inside_links.zone_of({"zones": {inside_links.ZONE: zone}})
    assert found is not None
    return found


def _ratio(cohort: "dict[str, list[str]]", child: "list[str]") -> float:
    """Rows a person here, the yes/no column's yes over its no."""
    counts: "dict[str, int]" = {}
    for key in child:
        counts[key] = counts.get(key, 0) + 1
    sums = {"Y": 0, "N": 0}
    sizes = {"Y": 0, "N": 0}
    for key, flag in zip(cohort["patient_id"], cohort["flag"]):
        sums[flag] += counts.get(key, 0)
        sizes[flag] += 1
    return (sums["Y"] / sizes["Y"]) / (sums["N"] / sizes["N"])


def _twin_child(child: "list[str]", seed: int) -> "list[str]":
    """A twin of the orders' key column as its description makes it: the same blocks, made-up keys of its own."""
    r = random.Random(f"links-twin-child-{seed}")
    sizes: "dict[str, int]" = {}
    for key in child:
        sizes[key] = sizes.get(key, 0) + 1
    out: "list[str]" = []
    for at, size in enumerate(sorted(sizes.values())):
        out += [f"P2{at:08d}"] * size
    r.shuffle(out)
    return out


def _wide(cohort: "dict[str, list[str]]") -> "dict[str, list[str]]":
    """A twin of the cohort: the same columns, made-up keys written wider (a letter and nine figures)."""
    out = dict(cohort)
    out["patient_id"] = [f"P1{at:08d}" for at in range(len(cohort["patient_id"]))]
    return out


@pytest.fixture(scope="module")
def fitted() -> "tuple[dict[str, list[str]], list[str], dict[str, object]]":
    cohort = _cohort(PERSONS, 1)
    child = _orders(cohort, 1)
    return cohort, child, _zone(cohort, child)


def test_the_fit_reads_the_relation(fitted) -> None:  # type: ignore[no-untyped-def]
    _cohort_cells, _child, zone = fitted
    terms = [tuple(term) for term in zone["terms"]]
    assert ("level", "flag", "Y") in terms, terms
    assert ("score", "age", "") in terms, terms
    assert not [term for term in terms if term[1] == "noise"], terms
    beta = zone["beta"]
    assert isinstance(beta, list)
    assert beta[1 + terms.index(("level", "flag", "Y"))] > 0.5


def test_the_link_keeps_the_relation(fitted) -> None:  # type: ignore[no-untyped-def]
    cohort, child, zone = fitted
    other = _wide(_cohort(PERSONS, 2))
    twin = _twin_child(child, 2)
    linked = inside_links.link(_checked(zone), twin, {name: other[name] for name in ORDER}, 0, BOUND)
    assert linked.refused == ""
    assert set(linked.cells) <= set(other["patient_id"])
    real = _ratio(cohort, child)
    made = _ratio(other, linked.cells)
    assert real > 2.0
    assert abs(made / real - 1.0) < 0.2, (made, real)
    # The rows of every block are kept: the same blocks, under new keys.
    assert sorted(_sizes(linked.cells)) == sorted(_sizes(twin))


def _sizes(cells: "list[str]") -> "list[int]":
    counted: "dict[str, int]" = {}
    for cell in cells:
        counted[cell] = counted.get(cell, 0) + 1
    return list(counted.values())


def test_the_share_found_is_the_real_one_and_the_rest_keep_keys_of_their_own() -> None:
    cohort = _cohort(PERSONS, 3)
    child = _orders(cohort, 3, orphans=500)
    zone = _checked(_zone(cohort, child))
    assert zone.found < zone.persons
    other = _wide(_cohort(PERSONS, 4))
    twin = _twin_child(child, 4)
    linked = inside_links.link(zone, twin, {name: other[name] for name in ORDER}, 3, BOUND)
    assert linked.refused == ""
    keys = set(linked.cells)
    parents = set(other["patient_id"])
    found = len(keys & parents)
    assert abs(found - round(len(keys) * zone.found / zone.persons)) <= 1
    own = keys - parents
    assert len(own) == linked.own > 0
    merged_parents = {parsing.merged_key(key) for key in parents}
    for key in own:
        assert parsing.merged_key(key) not in merged_parents
        assert len(parsing.merged_key(key)) >= BOUND


def _labs(cohort: "dict[str, list[str]]", seed: int) -> "list[str]":
    """The key column of a second invented table of the study: each person's rows follow the age alone."""
    r = random.Random(f"links-labs-{seed}")
    out: "list[str]" = []
    for key, age in zip(cohort["patient_id"], cohort["age"]):
        out += [key] * _poisson(r, math.exp(-1.5 + 0.05 * (int(age) - 55)))
    r.shuffle(out)
    return out


def _age_ratio(cohort: "dict[str, list[str]]", child: "list[str]") -> float:
    """Rows a person here, persons of 65 or more over persons under 45."""
    counts: "dict[str, int]" = {}
    for key in child:
        counts[key] = counts.get(key, 0) + 1
    sums = {True: 0, False: 0}
    sizes = {True: 0, False: 0}
    for key, age in zip(cohort["patient_id"], cohort["age"]):
        if 45 <= int(age) < 65:
            continue
        sums[int(age) >= 65] += counts.get(key, 0)
        sizes[int(age) >= 65] += 1
    return (sums[True] / sizes[True]) / (sums[False] / sizes[False])


def test_two_tables_of_the_study_link_to_one_cohort(fitted) -> None:  # type: ignore[no-untyped-def]
    cohort, orders, orders_zone = fitted
    labs = _labs(cohort, 1)
    labs_zone = _zone(cohort, labs)
    other = _wide(_cohort(PERSONS, 8))
    columns = {name: other[name] for name in ORDER}
    linked_orders = inside_links.link(_checked(orders_zone), _twin_child(orders, 8), columns, 0, BOUND,
                                      "orders-profile.json")
    linked_labs = inside_links.link(_checked(labs_zone), _twin_child(labs, 9), columns, 0, BOUND, "labs-profile.json")
    keys = set(other["patient_id"])
    assert set(linked_orders.cells) <= keys and set(linked_labs.cells) <= keys
    assert abs(_ratio(other, linked_orders.cells) / _ratio(cohort, orders) - 1.0) < 0.2
    assert abs(_age_ratio(other, linked_labs.cells) / _age_ratio(cohort, labs) - 1.0) < 0.2
    # Persons in both tables: the two tables meet through the cohort's columns, as on the real ones.
    real_both = len(set(orders) & set(labs))
    made_both = len(set(linked_orders.cells) & set(linked_labs.cells))
    assert abs(made_both / real_both - 1.0) < 0.15, (made_both, real_both)


def test_no_key_is_linked_where_it_could_be_a_real_one(fitted) -> None:  # type: ignore[no-untyped-def]
    _cohort_cells, child, zone = fitted
    narrow = _cohort(PERSONS, 5)
    twin = _twin_child(child, 5)
    columns = {name: narrow[name] for name in ORDER}
    refused = inside_links.link(_checked(zone), twin, columns, 0, BOUND)
    assert refused.refused == inside_links.REFUSED_NOT_WIDER
    assert refused.cells == twin
    unbounded = inside_links.link(_checked(zone), twin, {name: _wide(narrow)[name] for name in ORDER}, 0, 0)
    assert unbounded.refused == inside_links.REFUSED_NO_BOUND
    assert unbounded.cells == twin


def test_a_key_written_anew_clears_the_other_table_s_real_keys_too() -> None:
    """Codex's review of batch 4y, item 4: a block left unfound whose key the linked twin holds took a new key checked
    against this table's bound alone, so it could be a real key of the linked table (`P48188937`). Here this
    table's twin and the linked twin both write "P9" and seven figures (nine characters, this table's bound), and
    the linked table's real keys are nine characters long (its bound ten): no key is written anew, and every key the
    link writes is a key of one of the two twins; where the linked table's bound is nine, keys are written anew and
    each clears it (mutant: the linked table's bound not read)."""
    cohort = _cohort(PERSONS, 3)
    child = _orders(cohort, 3, orphans=500)
    zone = _checked(_zone(cohort, child))
    assert zone.found < zone.persons
    other = dict(_cohort(PERSONS, 4))
    other["patient_id"] = [f"P9{at:07d}" for at in range(PERSONS)]
    sizes: "dict[str, int]" = {}
    for key in child:
        sizes[key] = sizes.get(key, 0) + 1
    twin: "list[str]" = []
    for at, size in enumerate(sorted(sizes.values())):
        twin += [f"P9{at:07d}"] * size
    random.Random(12).shuffle(twin)
    columns = {name: other[name] for name in ORDER}
    made_up = set(other["patient_id"]) | set(twin)
    strict = inside_links.link(zone, twin, columns, 0, 9, "table-profile.json", 10)
    assert strict.refused == ""
    assert set(strict.cells) <= made_up, sorted(set(strict.cells) - made_up)[:5]
    wide = inside_links.link(zone, twin, columns, 0, 9, "table-profile.json", 9)
    anew = set(wide.cells) - made_up
    assert anew and all(len(parsing.merged_key(key)) >= 9 for key in anew)
    unread = inside_links.link(zone, twin, columns, 0, 9, "table-profile.json")
    assert set(unread.cells) <= made_up


def test_the_zone_holds_no_key_and_its_size_does_not_follow_the_rows() -> None:
    sizes = []
    for persons in (3000, 6000):
        cohort = _cohort(persons, 6)
        child = _orders(cohort, 6)
        zone = _zone(cohort, child)
        written = json.dumps(zone)
        sizes += [len(written)]
        for key in set(cohort["patient_id"]) | set(child):
            assert key not in written
    assert sizes[1] <= 1.05 * sizes[0], sizes


def test_a_damaged_zone_is_refused(fitted) -> None:  # type: ignore[no-untyped-def]
    _cohort_cells, _child, zone = fitted
    for name, value in (("bins", [[0.5]]), ("beta", ["x"]), ("version", 2), ("terms", [["other", "a", ""]])):
        damaged = dict(zone)
        damaged[name] = value
        with pytest.raises(inside_links.LinksError):
            inside_links.zone_of({"zones": {inside_links.ZONE: damaged}})
    assert inside_links.zone_of({"zones": {}}) is None


# -- through the commands, at the table floor ------------------------------------------------------------------


FLOOR_PERSONS = 20000


def _places(folder: pathlib.Path) -> inside.Places:
    return inside.Places(pathlib.Path(folder, "installation", "synthtwin", "inside"), (), (),
                         installation.system_name(), ())


def _write(path: pathlib.Path, header: "list[str]", rows: "list[list[str]]") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(",".join(header) + "\n")
        for row in rows:
            handle.write(",".join(row) + "\n")


def _run(folder: pathlib.Path, argv: "list[str]") -> "tuple[int, str]":
    said = io.StringIO()
    with B.installed(folder), contextlib.redirect_stdout(said), contextlib.redirect_stderr(said):
        code = cli.main(argv)
    return code, said.getvalue()


def _column(path: pathlib.Path, name: str) -> "list[str]":
    with open(path, encoding="utf-8", newline="") as handle:
        return [row[name] for row in csv.DictReader(handle)]


@pytest.fixture(scope="module")
def commands(tmp_path_factory: pytest.TempPathFactory) -> "dict[str, object]":
    folder = tmp_path_factory.mktemp("inside-links")
    cohort = _cohort(FLOOR_PERSONS, 7)
    child = _orders(cohort, 7)
    r = random.Random("links-amounts")
    cohort_path = pathlib.Path(folder, "data", "cohort.csv")
    orders_path = pathlib.Path(folder, "data", "orders.csv")
    _write(cohort_path, ORDER, [[cohort[name][at] for name in ORDER] for at in range(FLOOR_PERSONS)])
    _write(orders_path, ["patient_id", "dose"], [[key, f"{r.choice((1, 2, 5, 10)) * r.random():.1f}"] for key in child])
    out = pathlib.Path(folder, "out")
    out.mkdir()
    said: "dict[str, str]" = {}
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(inside, "default_places", lambda: _places(folder))
        for name, argv in (
            ("cohort", ["profile", f"{cohort_path}", "--out-dir", f"{out}", "--person", "patient_id"]),
            ("orders", ["profile", f"{orders_path}", "--out-dir", f"{out}", "--person", "patient_id",
                        "--linked-to", f"{cohort_path}"]),
            ("cohort twin", ["generate", f"{out / 'cohort-profile.json'}", "--seed", "0"]),
            ("orders twin", ["generate", f"{out / 'orders-profile.json'}", "--seed", "0", "--linked-to",
                             f"{out / 'cohort-profile.json'}"]),
            ("orders alone", ["generate", f"{out / 'orders-profile.json'}", "--seed", "0", "--out-dir",
                              f"{pathlib.Path(folder, 'alone')}"]),
        ):
            if name == "orders alone":
                pathlib.Path(folder, "alone").mkdir()
            code, words = _run(folder, argv)
            assert code == 0, (name, words[-600:])
            said[name] = words
    return {"folder": folder, "out": out, "said": said, "orders": orders_path, "cohort": cohort_path,
            "real": (cohort, child)}


def test_the_orders_twin_joins_the_cohort_twin_as_the_real_tables_join(commands) -> None:  # type: ignore[no-untyped-def]
    out = commands["out"]
    cohort, child = commands["real"]
    twin_cohort = {name: _column(pathlib.Path(out, "cohort-twin.csv"), name) for name in ORDER}
    twin_child = _column(pathlib.Path(out, "orders-twin.csv"), "patient_id")
    assert set(twin_child) <= set(twin_cohort["patient_id"])
    real_share = len(set(child)) / FLOOR_PERSONS
    assert abs(len(set(twin_child)) / FLOOR_PERSONS - real_share) <= 1 / FLOOR_PERSONS
    real = _ratio(cohort, child)
    made = _ratio(twin_cohort, twin_child)
    assert abs(made / real - 1.0) < 0.2, (made, real)
    report = pathlib.Path(out, "orders-twin-report.txt").read_text(encoding="utf-8")
    assert "THIS TWIN'S PERSONS ARE PERSONS OF THE TWIN OF" in report
    assert "is linked to the twin of" in commands["said"]["orders twin"]


def test_a_twin_built_without_the_option_is_not_linked(commands) -> None:  # type: ignore[no-untyped-def]
    out = commands["out"]
    cohort, child = commands["real"]
    twin_cohort = {name: _column(pathlib.Path(out, "cohort-twin.csv"), name) for name in ORDER}
    alone = _column(pathlib.Path(commands["folder"], "alone", "orders-twin.csv"), "patient_id")
    assert "is linked to the twin of" not in commands["said"]["orders alone"]
    if set(alone) & set(twin_cohort["patient_id"]):
        # Keys written in one layout may meet by their made-up counters, but no relation follows them.
        assert abs(_ratio(twin_cohort, alone) - 1.0) < 0.5 * abs(_ratio(cohort, child) - 1.0)


def test_the_five_checks_pass_on_the_linked_twin(commands) -> None:  # type: ignore[no-untyped-def]
    outcome = twin_checks.run_checks(f"{commands['orders']}", f"{pathlib.Path(commands['out'], 'orders-twin.csv')}",
                                     person="patient_id")
    assert outcome.passed, [(check.code, check.lines) for check in outcome.checks if not check.passed]


def test_the_pages_name_the_option() -> None:
    for command in ("profile", "generate"):
        page = cli.command_page(command)
        assert "--linked-to" in page
        assert len(page.splitlines()) <= 60
        assert max(len(line) for line in page.splitlines()) <= 79
    assert "--linked-to FILE" in cli.command_page("generate")
    assert "--linked-to" not in cli.command_page("twin")


def test_the_twin_command_says_it_does_not_link(tmp_path: pathlib.Path) -> None:
    """`synthtwin twin` reads no --linked-to, and says so before anything else (mutant: the caution removed)."""
    screen: "list[tuple[str, str]]" = []
    cli.run(["twin", f"{tmp_path / 'absent.csv'}", "--linked-to", f"{tmp_path / 'cohort.csv'}"], screen=screen)
    said = " ".join(text for _stream, text in screen)
    assert "synthtwin twin does not read --linked-to" in said


def _validated(commands: "dict[str, object]", twin: pathlib.Path, name: str) -> "tuple[int, list[tuple[str, str, str]]]":
    folder = commands["folder"]
    assert isinstance(folder, pathlib.Path)
    out = pathlib.Path(folder, f"quality-{name}")
    out.mkdir(exist_ok=True)
    description = pathlib.Path(f"{commands['out']}", "orders-profile.json")
    with pytest.MonkeyPatch.context() as patch, B.installed(folder):
        patch.setattr(inside, "default_places", lambda: _places(folder))
        made = cli.run(["validate", f"{description}", "--twin", f"{twin}", "--out-dir", f"{out}"], screen=[])
    return results.exit_code(made), sorted((miss.column, miss.fact, miss.subcheck) for miss in made.misses)


def test_validate_judges_the_linked_twin_as_it_judges_the_twin_left_alone(commands) -> None:  # type: ignore[no-untyped-def]
    """The link moves only the keys, each a made-up key wider than any real one: the description's checks read the same."""
    linked = _validated(commands, pathlib.Path(f"{commands['out']}", "orders-twin.csv"), "linked")
    alone = _validated(commands, pathlib.Path(f"{commands['folder']}", "alone", "orders-twin.csv"), "alone")
    assert linked == alone
