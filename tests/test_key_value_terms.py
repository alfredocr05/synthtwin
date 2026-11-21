"""Terms of lane KV beside its gate file, each case red on its own mutant (plan P4-D487; the lane's last step, the orchestrator's LANE KV RULINGS 7, and batch 4t's merge of the lane).

The scoped verify of repair 2 read both terms as right on the head and
found no case of the gate file `tests/test_key_value.py` red when either
was dropped: (1) the value column's `yes` holding the blocks its Safe
Harbor question lists, on a form whose every word the floor's people
hold, and (2) the recount of V19 reading a COMMON key block counted
absent on its rows alone. The two cases stand in a file of their own so
that the gate file stays under its three CPU minutes. At batch 4t's
merge of the lane the gate file's two older cases of the same terms
moved here beside them, for the same bar (the orchestrator's ruling R4
of the merge step): the scoped verify's blocker, any yes holds (LANE KV
RULINGS 6 (1)), and its major, a key block counted absent recounted on
its rows alone (6 (2)). The merge's own case follows them: a rare key
lane NOTES's reader reads as a sentence is named on no road (the NOTES
seam, the step's ruling R1). Every case reads the gate file's invented
tables and its helpers.
"""

from __future__ import annotations

import csv
import io
import pathlib
import random

import pytest

import test_key_value as key_value
from synthtwin import generation, profile, taxonomy, twinstore, validation

_REAL_COUNT_CHECK = validation._key_count_check


def test_any_yes_holds_the_listed_blocks_where_the_floors_people_hold_every_word(tmp_path: pathlib.Path) -> None:
    """THE LISTED BLOCKS' `yes` (the orchestrator's LANE KV RULINGS 7 (1), on 6 (1)), HIPAA first: ANY YES HOLDS, where the listed blocks' own line decides.

    In `profile._key_block` a listed block that holds no dates is held by
    `asked.question_put and (asked.safe_yes or not (asked.safe_no or
    asked.dates_no))`. With `asked.safe_yes or` dropped (the scoped verify
    2's mutant RM1), the coded identifier form at the table floor, its
    Safe Harbor answer corrected to `yes` beside the `no` about values
    that read as dates, published all 25 towns and all 10 family names and
    wrote each on 1,939 twin cells, and no case was red: the gate file's
    coded form draws 150 people over twelve words of each kind, some
    words held by fewer than the floor's people, so each block of words
    is held by its pool in people (`_pool_released` reads the `yes` too)
    before that line is read. Here 300 people hold six words of each
    kind, fifty people a word: the careless `no` to both questions
    describes the blocks of towns, family names and given names and
    publishes their words, so the line alone decides for them (the block
    of street names is held whatever is answered, by the question
    offering `identifier` its own values would be put, K7), and `yes`
    beside the `no` about dates, or beside both `no`, holds the four
    blocks of words and publishes no word. Red on RM1, and on the gate
    file's mutant that drops the `yes` for every block.
    """
    header, rows, words = key_value._coded_answers(1, people=300, each=6)
    coded = key_value._table(tmp_path, header, rows, "coded-floor-words.csv")
    every_word: "set[str]" = set()
    for found in words.values():
        every_word |= found
    # ...the premise: no word is rare, so the careless `no` to both
    # questions describes the blocks of towns, family names and given
    # names and publishes their words.
    careless = key_value._described(coded, [], safe_harbor_no=["answer"], dated_values_no=["answer"])
    described = key_value._key_blocks(careless, "answer")
    for key in ("Q6105", "Q6106", "Q6107"):
        assert described[key.casefold()]["role"] != taxonomy.ROLE_IDENTIFIER, key
        assert words[key] <= key_value._leaves(described[key.casefold()], set()), key
    answers: "tuple[dict[str, object], ...]" = (
        {"keyed_yes": ["answer"], "dated_values_no": ["answer"]},
        {"keyed_yes": ["answer"], "safe_harbor_no": ["answer"], "dated_values_no": ["answer"]},
    )

    def held() -> None:
        for given in answers:
            document = key_value._described(coded, [], **given)
            blocks = key_value._key_blocks(document, "answer")
            for key in words:
                assert blocks[key.casefold()]["role"] == taxonomy.ROLE_IDENTIFIER, (given, key)
            assert not key_value._leaves(key_value._block(document, "answer"), set()) & every_word, given

    key_value._red(held, profile, "_key_block", key_value._key_block_without_the_yes)


def test_a_common_key_block_counted_absent_is_recounted_on_its_rows_alone(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """V19 ON A COMMON KEY BLOCK COUNTED ABSENT (the orchestrator's LANE KV RULINGS 7 (2), on 6 (2)): the kind `common-absent` beside the gate file's pools counted absent.

    `validation._key_block_checks` passes each key block's
    `present_count_withheld` to its recount, as it passes the pool's. With
    the key blocks' flag passed False and the pool's kept (the scoped
    verify 2's mutant RM7b), validate exited 3 on the product's own twin
    at the table floor (a common key on one row of each of the 1,000
    people, a word for 5 of them: `by_key` of that key MISSED), and no case
    was red: the gate file's case reads pools only. Below the floor (a
    test device): a common key on one row of each of 120 people, a word on
    the rows of 5, is counted absent; the twin writes its made-up word in
    the floor's number of its cells (method G8.3d) where the real table
    holds its own five; both validate, the key's line HELD, the twin's
    rows of the key recounted here independently of the validator.
    """
    key_value._floor_lowered(monkeypatch)
    kind = "common-absent"
    source = tmp_path / f"absent-{kind}.csv"
    rows = key_value._pooled_rows(kind)
    table = key_value._long(tmp_path, f"absent-{kind}", rows)
    document = key_value._described(table, [], safe_harbor_no=["item_key", "item_value"], dated_values_no=["item_value"])
    block = key_value._key_blocks(document, "item_value")["skin_note"]
    present, missing = block["n_present"], block["n_missing"]
    assert isinstance(present, int) and isinstance(missing, int)
    assert present == 0 and block["present_count_withheld"] is True, block
    # ...the premise: the real table holds a word on the key's rows of 5 people.
    assert len([row for row in rows if row[1] == "skin_note" and row[2]]) == 5
    loaded = key_value._loaded(tmp_path, document)
    twin = generation.generate_held(loaded, 0)
    names = list(twin.names)
    cells = [list(twinstore.column_cells(column)) for column in twin.held_columns]
    path = tmp_path / f"absent-{kind}-twin.csv"
    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(names)
    writer.writerows(zip(*cells))
    path.write_text(out.getvalue(), encoding="utf-8", newline="\n")
    key_at = names.index("item_key")
    assert len([row for row in zip(*cells) if row[key_at].strip().casefold() == "skin_note"]) == present + missing

    def validated() -> None:
        for checked in (path, source):
            outcome = validation.measure(loaded, str(checked))
            assert not [check for check in outcome.checks if check.verdict == validation.MISSED], checked.name
            line = [check.verdict for check in outcome.checks if check.fact == "label.by_key" and check.subcheck == "by_key.skin_note"]
            assert line == [validation.HELD], checked.name

    # ...the mutant RM7b: each key block's flag passed False, the pool's kept.
    key_value._red(validated, validation, "_key_count_check", lambda name, label, counted, found, holding, found_holding, withheld=False: _REAL_COUNT_CHECK(name, label, counted, found, holding, found_holding, withheld and not label))


def test_any_yes_holds_what_the_keyed_clause_lists_whatever_the_other_answer(tmp_path: pathlib.Path) -> None:
    """THE SCOPED VERIFY'S BLOCKER (the orchestrator's LANE KV RULINGS 6 (1)), HIPAA first: ANY YES HOLDS.

    Measured at the table floor on 46df4166: the value column's Safe Harbor
    answer corrected to `yes` after its question about values that read as
    dates was answered `no` published all 25 towns and 10 family names of
    the coded identifier form and wrote each on 1,939 twin cells, where the
    base held the column whole (`_KeyedAsked.safe_yes` was read nowhere). A
    `yes` to EITHER question carrying the keyed clause -- the Safe Harbor
    question, or the question about values that read as dates, which the
    command passes as `keyed_yes` too -- holds the blocks of words, the
    date blocks and a number block's values that read as dates, whatever
    `no` the other question was given; two `no` describe them (the careless
    `no`, within the ruled bar).
    """
    header, rows, words = key_value._coded_answers(1)
    coded = key_value._table(tmp_path, header, rows, "coded-any-yes.csv")
    every_word: "set[str]" = set()
    for found in words.values():
        every_word |= found
    small_header, small_rows = key_value._small_long()
    dated = key_value._table(tmp_path, small_header, key_value._day_counts(small_rows), "dated-any-yes.csv")
    answers: "tuple[dict[str, object], ...]" = (
        {"keyed_yes": ["V"], "dated_values_no": ["V"]},
        {"keyed_yes": ["V"], "safe_harbor_no": ["V"], "dated_values_no": ["V"]},
        {"keyed_yes": ["V"], "safe_harbor_no": ["V"], "dated_held": ("V",)},
    )

    def held() -> None:
        for given in answers:
            document = key_value._described(coded, [], **key_value._the_value_columns(given, "answer"))
            blocks = key_value._key_blocks(document, "answer")
            for key in words:
                assert blocks[key.casefold()]["role"] == taxonomy.ROLE_IDENTIFIER, (given, key)
            assert not key_value._leaves(key_value._block(document, "answer"), set()) & every_word, given
            assert blocks["q6101"]["role"] in (taxonomy.ROLE_COUNT, taxonomy.ROLE_CONTINUOUS), given
        # ...the date blocks and a number block's values that read as dates,
        # after the `yes` beside the question about dates answered `no`.
        on_dates = key_value._key_blocks(key_value._described(dated, [], **key_value._the_value_columns(answers[0], "item_value")), "item_value")
        assert on_dates["line_placed_on"]["role"] == taxonomy.ROLE_IDENTIFIER
        assert on_dates["item_count"]["role"] == taxonomy.ROLE_COUNT
        assert key_value._largest_number(on_dates["item_count"]) < 45000
        careless = key_value._key_blocks(key_value._described(coded, [], safe_harbor_no=["answer"], dated_values_no=["answer"]), "answer")
        assert careless["q6107"]["role"] != taxonomy.ROLE_IDENTIFIER

    key_value._red(held, profile, "_key_block", key_value._key_block_without_the_yes)


def test_a_key_block_counted_absent_is_recounted_on_its_rows_alone(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """THE SCOPED VERIFY'S MAJOR (the orchestrator's LANE KV RULINGS 6 (2)): the product's own twin validates where a key block is counted absent.

    Measured at the table floor on 46df4166: a pool of one rare key of four
    people (form sp) and of two of five people each (form sp2), answered as
    the holder would, validated with exit 3 on `by_key.pool`: the pool is
    counted absent (`n_present` 0, its count withheld), the twin writes its
    made-up word in the floor's number of its cells (method G8.3d: 11 cells
    of 30) where the real table holds its own values, and V19 compared those
    present cells with 0. A block counted absent is recounted on its rows
    alone, its present cells not observed, as V17.2 reads a column counted
    absent: the twin and the real table meet it. Below the floor (a test
    device): one rare key of numbers and one of a town; the twin's rows of
    rare keys recounted here independently of the validator.
    """
    key_value._floor_lowered(monkeypatch)

    def validated() -> None:
        for kind in ("one-c", "one-n"):
            source = tmp_path / f"absent-{kind}.csv"
            table = key_value._long(tmp_path, f"absent-{kind}", key_value._pooled_rows(kind))
            document = key_value._described(table, [], safe_harbor_no=["item_key", "item_value"], dated_values_no=["item_value"])
            pool = key_value._block(document, "item_value")["by_key"]["pool"]  # type: ignore[index]
            assert pool["n_present"] == 0 and pool["present_count_withheld"] is True, kind
            loaded = key_value._loaded(tmp_path, document)
            value = [column for column in loaded.columns if column.name == "item_value"][0]
            assert value.key_pool is not None
            twin = generation.generate_held(loaded, 0)
            names = list(twin.names)
            cells = [list(twinstore.column_cells(column)) for column in twin.held_columns]
            path = tmp_path / f"absent-{kind}-twin.csv"
            out = io.StringIO()
            writer = csv.writer(out, lineterminator="\n")
            writer.writerow(names)
            writer.writerows(zip(*cells))
            path.write_text(out.getvalue(), encoding="utf-8", newline="\n")
            common = {label for label, _block in value.key_blocks}
            rare_rows = [row for row in zip(*cells) if row[names.index("item_key")].strip() and row[names.index("item_key")].strip().casefold() not in common]
            assert len(rare_rows) == value.key_pool.n_present + value.key_pool.n_missing, kind
            outcome = validation.measure(loaded, str(path))
            assert not [check for check in outcome.checks if check.verdict == validation.MISSED], kind
            pooled = [check for check in outcome.checks if check.fact == "label.by_key" and check.subcheck == "by_key.pool"]
            assert [check.verdict for check in pooled] == [validation.HELD], kind
            real = validation.measure(loaded, str(source))
            assert [check.verdict for check in real.checks if check.fact == "label.by_key" and check.verdict != validation.HELD] == [], kind

    key_value._red(validated, validation, "_key_count_check", lambda name, label, rows, found_rows, cells, found_cells, withheld=False: _REAL_COUNT_CHECK(name, label, rows, found_rows, cells, found_cells, False))


# -- the NOTES seam: batch 4t's merge of the lane (P4-D487's merge paragraph) --

# Pieces of a questionnaire's items in a script written with no space between
# its sentences, and that script's marks: the ideographic full stop, the
# full-width question mark, exclamation mark and full stop, and the halfwidth
# ideographic full stop.
_UNSPACED_PIECES = (
    "\u4eca\u65e5\u306e\u75db\u307f", "\u591c\u306e\u7720\u308a", "\u98df\u4e8b\u306e\u91cf",
    "\u6b69\u304f\u529b", "\u6c17\u5206", "\u54b3\u306e\u5177\u5408", "\u71b1\u306e\u6709\u7121",
    "\u85ac\u306e\u52b9\u304d\u76ee",
)
_UNSPACED_MARKS = ("\u3002", "\uff1f", "\uff01", "\uff0e", "\uff61")
_ROADS = ((taxonomy.ROLE_CATEGORICAL, False), (taxonomy.ROLE_LONG_TAIL, True), (taxonomy.ROLE_LONG_TAIL, False))


def _unspaced_sentences() -> "list[str]":
    """GENERATED: 240 question texts of a script written with no space between its sentences, three to five sentences each, parted and ended by one of that script's marks, each mark in turn."""
    draw = random.Random(20261114)
    found: "list[str]" = []
    for turn in range(240):
        parts = [draw.choice(_UNSPACED_PIECES) for _part in range(3 + turn % 3)]
        mark = _UNSPACED_MARKS[turn % len(_UNSPACED_MARKS)]
        found += [mark.join(parts) + mark]
    return found


def _keyed_names_pass_without_lane_notess_reader(names: "tuple[str, ...]", role: str, code: bool, comma: bool) -> bool:
    """MUTANT: lane NOTES's sentence reading not read in the line, the stand-in alone (the lane's branch)."""
    with key_value._mutant(taxonomy, "a_sentence", lambda text: False):
        return key_value._REAL_PASS(names, role, code, comma)


def test_a_rare_key_lane_notess_reader_reads_as_a_sentence_is_named_on_no_road(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """THE NOTES SEAM (batch 4t's merge of the lane; the step's ruling R1; LANE KV RULINGS 2 (2), the rule of LANE NOTES RULINGS 8 (1)), HIPAA first: a rare key that lane NOTES's reader reads as a sentence is named after no answer, on any road, ALL OR NONE.

    The lane's stand-in (`profile._reads_as_a_sentence`) counts words
    between the screen's spaces, so a question text of a script written
    with no space between its sentences holds one word to it and passes
    every other screen: on the merge commit each of the 240 generated
    texts was named beside the gate file's ordinary names on all three
    roads. Since the merge `keyed_names_pass` reads lane NOTES's own
    reader (`taxonomy.a_sentence`) beside the stand-in, so none is named;
    and at the table floor's rule (lowered, `_floor_lowered`) a key column
    of eight such rare texts pooled in people, answered `no`, names none.
    Red on the mutant that drops the reader from the line. The price was
    measured nil: no key of the six invented forms, of the gate file's
    generated texts or of the zoo's seven keyed tables reads newly as a
    sentence (P4-D487's merge paragraph).
    """
    family = _unspaced_sentences()
    # ...the premise: the stand-in reads none of them, lane NOTES's reader every one.
    assert not [name for name in family if profile._reads_as_a_sentence(name)]
    assert all(taxonomy.a_sentence(name) for name in family)
    texts: "list[str]" = []
    for name in family:
        if name not in texts:
            texts += [name]
    texts = texts[:8]
    assert len(texts) == 8
    key_value._floor_lowered(monkeypatch)
    rows = key_value._pooled_rows("")
    for place in range(24):
        # ...three people a text, four rows a person, so each key's twelve rows pool in people.
        rows += [[f"Q{5000 + 7 * place}", texts[place // 3], f"{(place + visit) % 9}"] for visit in range(4)]
    table = key_value._long(tmp_path, "asked-unspaced", rows)

    def refused() -> None:
        for name in family:
            for role, code in _ROADS:
                assert not profile.keyed_names_pass(key_value._ORDINARY + (name,), role, code, False), (role, code)
        block = key_value._block(key_value._described(table, [], safe_harbor_no=["item_key", "item_value"]), "item_key")
        assert "pool_in_people" in block and "held_back_names" not in block

    key_value._red(refused, profile, "keyed_names_pass", _keyed_names_pass_without_lane_notess_reader)
