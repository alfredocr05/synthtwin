"""The fix round of release 37's landing: the outside review's items 1, 2, 4, 8, 13 and 14.

WHY. The one outside review of release 37 (gpt-6-astra, ultra) returned REJECT with fifteen items. The landing fixed
those that put a real value into the twin where the public head wrote none, or broke the default path; the rest are
carried with their owners (plan decision P4-D549). Each clause below is red on its mutant.

* ITEM 1. A person's detail column (`inside_text.MODE_DETAIL`) kept a word most rows write as its layout, wherever it
  stood: addresses where most rows name one street kept that street, and an e-mail domain whose words are in the
  layout's vocabulary (`north.com`) or that reads as a reserved one by its words alone (`example1.com`) was kept whole.
  A word now counts toward the layout share only in a link's path or query or in a key, a host's naming labels are
  never kept, and a reserved domain is read on each label whole (mutants: the share counted anywhere; the naming
  labels kept; the labels read by their words).
* ITEM 2. A made-up word of a length no made-up word was left at is words run together and cut: on addresses whose
  street words are two letters long it wrote a real street word in about one cell in twenty-five. Such a word is drawn
  again where a real cell writes it (mutant: not drawn again).
* ITEM 4. A key of figures alone written at its own width was kept off the real keys read as numbers only where the
  real key was at most five figures long, so a made-up `201` equalled a real `000201` read as a number (mutant: the
  real keys read at five figures at most).
* ITEM 8. The relations zone's fit of a number kept between rounds was keyed without the scale its response is read
  on, so a round that let go the event label beside an event's time took the fit made on hazard scores (mutant: the
  scale left out of the key).
* ITEM 13. The start-of-run check's glance counted lines as rows, so a table of notes of many lines read as many times
  its rows and was refused (mutant: a line counted as a record).
* ITEM 14. The order zone grew a set by copying it for every run of rows: quadratic in the persons (mutant: the copy
  put back).

Every table here is drawn by the standard library's `random` from a seed, at run time; nothing is committed.
"""

from __future__ import annotations

import ast
import json
import pathlib
import random
import re

from synthtwin import inside_relations as R, inside_text, reading

ROWS = 20000
PRODUCT = pathlib.Path(__file__).resolve().parent.parent / "src" / "synthtwin"


def _stand_in(cells: "list[str]") -> "list[str]":
    """The description's twin of a free-text column, in miniature: one made-up value a real value, as long as it."""
    names: "dict[str, str]" = {}
    for cell in cells:
        if cell not in names:
            tag = f"{len(names) + 1}"
            names[cell] = ("!" * max(0, len(cell) - len(tag))) + tag
    return [names[cell] for cell in cells]


def _detail(cells: "list[str]") -> "list[str]":
    entry = inside_text.entry_of(cells, inside_text.MODE_DETAIL, [], [row // 4 for row in range(len(cells))], 11)
    assert entry is not None
    written = inside_text.write_column(inside_text.zone_of({"c": entry}), "c", _stand_in(cells), 7)
    assert written is not None
    return written


def _words(cells: "list[str]") -> "set[str]":
    found: "set[str]" = set()
    for cell in cells:
        found |= {word.lower() for word in re.findall(r"[A-Za-z]+", cell)}
    return found


# -- item 1 ----------------------------------------------------------------------------------------------------------


def test_a_street_most_rows_name_is_no_layout_word() -> None:
    draw = random.Random(37)
    real = [f"{draw.randint(1, 9999)} {'Cedar' if draw.random() < 0.6 else 'Maple'} {draw.choice(('St', 'Ave'))}"
            for _ in range(ROWS)]
    twin = _detail(real)
    assert not set(twin) & set(real)
    assert not {"cedar", "maple"} & _words(twin), sorted(_words(twin))[:10]
    assert all(re.fullmatch(r"\d{1,4} [A-Z][a-z]+ (St|Ave)", cell) for cell in twin)


def test_a_mail_domain_is_never_kept_whole_and_a_reserved_one_is_read_on_its_labels() -> None:
    draw = random.Random(38)
    for domain in ("north.com", "example1.com", "mail.west.org"):
        real = [f"{draw.choice(('anna', 'bruno', 'carla'))}.{draw.choice(('itoh', 'lopez', 'marsh'))}{draw.randint(1, 9999)}@"
                f"{domain}" for _ in range(ROWS)]
        twin = _detail(real)
        assert not set(twin) & set(real), domain
        hosts = {cell.split("@", 1)[1] for cell in twin}
        assert domain not in hosts, domain
        labels = set(domain.split(".")[:-1])
        assert not [host for host in hosts if set(host.split(".")[:-1]) & labels], (domain, sorted(hosts)[:5])
    # ...while a link's path keeps its words where most rows write them, and a reserved host is kept.
    real = [f"https://portal.example.org/chart/P{4000000 + draw.randrange(5000):07d}/{draw.randint(100000, 999999)}"
            for _ in range(ROWS)]
    twin = _detail(real)
    assert all(re.fullmatch(r"https://portal\.example\.org/chart/P\d{7}/\d{6}", cell) for cell in twin), twin[:3]


# -- item 2 ----------------------------------------------------------------------------------------------------------


def test_a_word_made_up_at_a_length_no_made_up_word_has_is_no_real_word() -> None:
    draw = random.Random(39)
    streets = ("Li", "Ho", "Lu", "Bo", "Su")
    real = [f"{draw.randint(10000, 99999)} {draw.choice(streets)} St" for _ in range(ROWS)]
    twin = _detail(real)
    assert not set(twin) & set(real)
    held = [cell for cell in twin if {word for word in re.findall(r"[A-Za-z]+", cell)} & set(streets)]
    assert not held, held[:5]
    # ...and the word itself, drawn at a length no made-up word is left at (two letters here: the plan above took
    # three-letter words): the first letters of the made-up words run together spell `li`, `ho`, `bo`, `su` and `lu`
    # often enough that 2,000 draws meet them (mutant: not drawn again), and never one of them now.
    entry = inside_text.entry_of(real, inside_text.MODE_DETAIL, [], [row // 4 for row in range(len(real))], 11)
    assert entry is not None
    writer = inside_text._writer_of(entry, inside_text._stream(7, "c", "text"))
    assert 2 not in writer.neutral and {"li", "ho", "lu", "bo", "su"} <= writer.taken
    slot = {"cases": {"title": 1}}
    drawn = [inside_text._neutral_drawn(writer, slot, 2) for _ in range(2_000)]
    assert not [word for word in drawn if word.lower() in {"li", "ho", "lu", "bo", "su"}], sorted(set(drawn))[:10]


# -- item 4 ----------------------------------------------------------------------------------------------------------


def test_a_key_of_figures_alone_equals_no_real_key_read_as_a_number_at_any_width() -> None:
    values = [f"{100 + (row % 900)}" for row in range(ROWS)]
    real = ["000201" if cell == "201" else cell for cell in values]
    names: "dict[str, str]" = {}
    for cell in real:
        names.setdefault(cell, f"Z{len(names) + 1:04d}")
    stand_in = [names[cell] for cell in real]
    entry = inside_text.entry_of(real, inside_text.MODE_IDENTIFIER, [], [row // 20 for row in range(ROWS)], 11)
    assert entry is not None
    twin = inside_text.write_column(inside_text.zone_of({"c": entry}), "c", stand_in, 7)
    assert twin is not None
    numbers = {int(cell) for cell in real}
    assert not [cell for cell in twin if cell.isdigit() and int(cell) in numbers]


# -- item 8 ----------------------------------------------------------------------------------------------------------


def _timed(rows: int) -> "dict[str, list[str]]":
    draw = random.Random("event-kept")
    out: "dict[str, list[str]]" = {"x": [], "days": [], "event": []}
    for _row in range(rows):
        x = draw.gauss(0.0, 1.0)
        days = max(1, int(200 + 35 * x + draw.gauss(0.0, 30.0)))
        out["x"] += [f"{x:.4f}"]
        out["days"] += [f"{days}"]
        out["event"] += ["Y" if days < 200 else "N"]
    return out


def _timed_zone(columns: "dict[str, list[str]]", names: "list[str]", kept: "R.KeptFits | None") -> "tuple[str, set[str]]":
    rows = len(columns["x"])
    sample = R.sample_rows(rows)
    specs = {"x": R.ColumnSpec("x", 0, R.NUMBER, 0, (), ""), "days": R.ColumnSpec("days", 1, R.NUMBER, 0, (), ""),
             "event": R.ColumnSpec("event", 2, R.LABEL, 0, ("N", "Y"), "")}
    encoded = [R.encode(specs[name], columns[name], sample) for name in names]
    present = [each for each in encoded if each is not None]
    timed = R.event_times(present)
    zone = R.fit_zone(present, len(sample), rows, None, "", None, kept)
    return json.dumps(zone, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False), timed


def _held(kept: "R.KeptFits") -> "R.KeptFits":
    stats = json.loads(json.dumps(kept.made_stats, allow_nan=False))
    models = json.loads(json.dumps(kept.made_models, allow_nan=False))
    return R.KeptFits(held_stats=stats, held_models=models)


def test_a_fit_kept_on_hazard_scores_is_never_taken_for_the_same_number_read_on_normal_scores() -> None:
    columns = _timed(6000)
    first = R.KeptFits()
    _zone, timed = _timed_zone(columns, ["x", "days", "event"], first)
    assert timed == {"days"}, timed
    again, timed = _timed_zone(columns, ["x", "days"], _held(first))
    assert timed == set()
    assert again == _timed_zone(columns, ["x", "days"], None)[0]


# -- item 13 ---------------------------------------------------------------------------------------------------------


def test_the_glance_counts_a_quoted_cell_of_many_lines_as_one_row(tmp_path: pathlib.Path) -> None:
    note = "\n".join(f"line {k}" for k in range(40))
    body = "".join(f'{row},"{note}",{row % 7}\n' for row in range(3000))
    table = tmp_path / "notes.csv"
    table.write_bytes(("id,note,grade\n" + body).encode("utf-8"))
    seen = reading.glance(str(table))
    assert seen is not None and seen.columns == 3
    assert 2850 <= seen.rows <= 3150, seen.rows
    # ...a first record left open past the opening says nothing.
    open_header = tmp_path / "open.csv"
    open_header.write_bytes(('"a,b\n' + "1,2\n" * 100_000).encode("utf-8"))
    assert reading.glance(str(open_header)) is None


# -- item 14 ---------------------------------------------------------------------------------------------------------


def test_the_order_zone_grows_no_set_by_copying_it() -> None:
    tree = ast.parse((PRODUCT / "inside_order.py").read_text(encoding="utf-8"))
    copied = []
    for node in ast.walk(tree):
        if (isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)
                and isinstance(node.value, ast.BinOp) and isinstance(node.value.op, ast.BitOr)
                and isinstance(node.value.left, ast.Name) and node.value.left.id == node.targets[0].id):
            copied += [node.lineno]
    assert not copied, copied
