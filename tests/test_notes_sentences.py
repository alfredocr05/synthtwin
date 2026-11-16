"""P4-D481 (lane NOTES): a column of sentences is described as free text; HIPAA first.

THE READING (`taxonomy.a_sentence`, `taxonomy.sentences_hold`): a present
cell is a sentence where it holds three words or more and a sentence mark --
a full stop, a question or exclamation mark (and their full-width, small,
ideographic, double and ellipsis forms) after a word that is no lone letter,
followed by a word or ending the cell; a colon or a semicolon between words
(two figures written together around it excepted); a line break between
words -- and a column whose reading would publish its levels is a column of
sentences where half or more of its present cells are sentences. Such a
column is described as free text (`taxonomy.EVIDENCE_SENTENCES_AS_TEXT`),
where no Safe Harbor hold, declared or held record number or open question
offering `identifier` holds it, and is put ONE question (`asking.
sentence_questions`): free text or record numbers, `text` carried so it is
not put again. The rare levels of a column of sentences are never named
(lane CODES-2's roads, `held_back_names_published`), nor those of a label
column one of whose held-back levels is a sentence or holds three words.

THE GATE: the GENERATED sentences of `tests/notes_sentences_forms.py` (every
variable-part family in thousands, every mark and every space of the one
definition in every position, a stop then a trailing mark, a short name or
place before the only stop) are read and what must not be read is not
(labels after a capitalised abbreviation opening the cell among them), each
red on its mutant (the word count, each mark, the share, the decimal point,
the stop after the last word, the abbreviation and its bounds); the short
cut reads as the whole reading, and answers a note of any script; a run of
marks is read in time linear in its length; the description (a constant, a
two-valued and a numbers-with-labels column of sentences; not an affixed
number), the reading handed over not decided again (nor taken without its
reading), the precedence of the holds, the people's hold replaced, the guard
(a column of sentences, a label column whose held-back levels hold a
sentence, and generated comments typed with a mark or none), the question
and its answer at the unit level and through the commands on a test
device; and ONE 20,000-row
case through the commands (THE SUITE'S TIME rule): a stock bank of 216
sentences, the name and place templates and a control column of codes,
1,000 people of 20 rows, the person column said. Every family in every mode
at 20,000 rows, and the price over the zoo and the goldens, are K-HZ-34's
(`tools/measurements/kpi_notes_sentences.py`, `kpi_run --slow`).
"""

from __future__ import annotations

import contextlib
import csv
import io
import json
import pathlib
import random

import pytest

import health_zoo as zoo
import notes_sentences_forms as forms
from synthtwin import asking, parsing, taxonomy


@contextlib.contextmanager
def _mutant(target: object, name: str, replacement: object):
    """One rule of the product replaced for the length of a block."""
    kept = getattr(target, name)
    setattr(target, name, replacement)
    try:
        yield
    finally:
        setattr(target, name, kept)


def _red(case: "object", target: object, name: str, replacement: object) -> None:
    """The case holds on the product and fails on its mutant."""
    case()  # type: ignore[operator]
    with _mutant(target, name, replacement), pytest.raises(AssertionError):
        case()  # type: ignore[operator]


def _words_three_or_more(cell: str) -> bool:
    """Three space-parted stretches holding a letter or a figure, read independently of the reader (the generated cells part words by spaces)."""
    held = 0
    for part in cell.replace("\n", " ").replace("\r", " ").split():
        if any(character.isalnum() for character in part):
            held += 1
    return held >= 3


GENERATED = forms.sentence_families(1500, 20261112)


def test_every_generated_sentence_of_every_family_is_read() -> None:
    """Every variable-part family (names with and without titles, family names, initials, dates, figures, places, relatives, telephones) and every stock sentence of three words or more is read as a sentence; red where no mark is read."""
    def case() -> None:
        unread = {
            family: [cell for cell in cells if _words_three_or_more(cell) and not taxonomy.a_sentence(cell)]
            for family, cells in GENERATED.items()
        }
        assert not any(unread.values()), {family: cells[:2] for family, cells in unread.items() if cells}
        assert sum(len(cells) for cells in GENERATED.values()) >= 13_000

    _red(case, taxonomy, "_holds_a_sentence_mark", lambda body: False)


def test_every_mark_and_every_space_in_every_position_is_read() -> None:
    """RULINGS 1 (4): every mark of the reading, before, after, doubled, glued to the next word and before a closing quote, every space of the word screen's one definition between the words, accented and non-Latin letters and full-width figures, and a stop followed by a trailing mark (a tick, dashes, a hash, a star, a bullet, a degree sign, an arrow; skeptic 1's item 2): every cell is a sentence, and a column of them is a column of sentences; red without the small forms, the joins, the line breaks, or the stop after the last word."""
    cells = forms.marks_and_spaces()
    trailing = [(what, cell) for what, cell in cells if what == "a stop, then a trailing mark"]

    def case() -> None:
        unread = [(what, cell) for what, cell in cells if not taxonomy.a_sentence(cell)]
        assert not unread, unread[:4]
        assert taxonomy.a_sentence_column([cell for _what, cell in cells])

    def trailing_case() -> None:
        unread = [cell for _what, cell in trailing if not taxonomy.a_sentence(cell)]
        assert not unread, unread[:4]

    assert len(cells) > 3_000 and len(trailing) >= 6 * len(forms.STOPS)
    _red(case, taxonomy, "_SENTENCE_STOPS", ".?!")
    _red(case, taxonomy, "_SENTENCE_JOINS", "")
    _red(case, taxonomy, "_SENTENCE_BREAKS", "")
    _red(trailing_case, taxonomy, "_ending_the_words", lambda place, last_word: False)


def test_a_mark_glued_to_the_next_word_is_a_sentence_mark_only_in_the_scripts_written_without_spaces() -> None:
    """A full stop, question or exclamation mark, colon or semicolon glued to the next word, with no other mark in the cell (`Seen in clinic.Plan agreed`), marks no sentence -- a code list `E11.9;I10`, a hardware address and a dotted name are written so -- but after the full-width and ideographic marks of the scripts written with no space between sentences it does; red where any glued mark counts, and where none does."""
    cells = forms.glued_to_the_next_word()

    def case() -> None:
        wrong = [(mark, cell) for mark, cell, expected in cells if taxonomy.a_sentence(cell) != expected]
        assert not wrong, wrong[:4]

    assert sum(1 for _mark, _cell, expected in cells if expected) and sum(1 for _mark, _cell, expected in cells if not expected)
    _red(case, taxonomy, "_SENTENCE_UNSPACED", "")
    _red(case, taxonomy, "_SENTENCE_UNSPACED", "".join(forms.STOPS + forms.JOINS))


def test_what_is_no_sentence_is_not_read() -> None:
    """Short codes, labels of two words with a point, complaints joined by commas, comments of two to four words, ancestry, facility, department and organism names, Likert words, plain word strings with no mark, decimals, clocks, ratios and initials, and labels written after a capitalised abbreviation and its point (`St. Aldric Hospital`, `Dept. of Surgery`, `Dr. Marin Dorby`; the statistics check's item 1): none is a sentence; red where three words are no longer asked, where a decimal point, a clock or an initial counts as a mark, and where the abbreviation's point counts."""
    def case() -> None:
        read = [cell for cell in forms.NOT_SENTENCES if taxonomy.a_sentence(cell)]
        assert not read, read

    assert len(forms.abbreviated_labels()) >= 66
    _red(case, taxonomy, "SENTENCE_WORDS_AT_LEAST", 1)
    _red(case, taxonomy, "_SENTENCE_FULL_STOPS", "")
    _red(case, taxonomy, "_a_lone_letter_before", lambda body, letters, place: False)
    _red(case, taxonomy, "_a_capitalised_abbreviation", lambda body, run, place, first_word: False)


def test_a_short_name_before_the_only_stop_is_read_and_an_abbreviation_only_where_it_opens_the_cell() -> None:
    """The combined verify's major 2 (RULINGS 9 (2)): a made-up name or place of two to four letters right before a cell's only full stop, after an opening of words (`Seen with Malo. Plan agreed`, `Spoke to wife Tena. Will call back`), is a sentence -- the abbreviation's stop is no mark only where the abbreviation opens the cell, so the labels written after one (`St. Aldric Hospital`) keep their levels; and opening the cell before its only stop, a capitalised word of five letters or more or a word of small letters is read, a capitalised word of two to four letters is not (`Malo. Plan agreed`, a stated class of P4-D481 (c)); red where the abbreviation is read anywhere (repair 1's rule), where it runs to five letters, and where its first letter may be small (the combined verify's minor 4, V07 and V09)."""
    shorts = forms.short_names_before_the_only_stop()
    opening = forms.opening_words_before_the_only_stop()

    def case() -> None:
        unread = [cell for cell in shorts if not taxonomy.a_sentence(cell)]
        assert not unread, unread[:4]
        wrong = [(cell, expected) for cell, expected in opening if taxonomy.a_sentence(cell) != expected]
        assert not wrong, wrong[:4]
        read = [cell for cell in forms.abbreviated_labels() if taxonomy.a_sentence(cell)]
        assert not read, read[:4]

    kept = taxonomy._a_capitalised_abbreviation

    def anywhere(body: str, run: int, place: int, first_word: int) -> bool:
        return kept(body, run, place, place - run + 1)

    def any_case(body: str, run: int, place: int, first_word: int) -> bool:
        start = place - run + 1
        return 2 <= run <= 4 and start == first_word and all("a" <= one <= "z" for one in body[start + 1 : place + 1])

    assert len(shorts) >= 1_000 and sum(1 for _cell, expected in opening if not expected) >= 100
    _red(case, taxonomy, "_a_capitalised_abbreviation", anywhere)
    _red(case, taxonomy, "_ABBREVIATION_LETTERS_AT_MOST", 5)
    _red(case, taxonomy, "_a_capitalised_abbreviation", any_case)


def test_the_short_cut_reads_as_the_whole_reading() -> None:
    """`_ending_plainly` is a short cut, never a second rule: over 20,000 generated cells of words, marks, spaces and controls of ASCII, and as many of accented, Cyrillic, ideographic and full-width letters and figures, spaces that print nothing, combining accents and other marks (the short cut reads every script: the statistics check's item 7), `a_sentence` answers as the character-by-character reading does; red where a stretch of marks counts as a word."""
    draw = random.Random(481)
    plain = list("ab cD.!?:;,-\"()\n12 3Xy\t") + ["\xa0", "\u3002", "\uff0e", "\u2026", "\u200b", "\x01", "e", "J."]
    other = plain + ["\u00e9", "\u0416", "\u0436", "\u5b57", "\uff12", "\uff21", "\u200b", "\u00a0", "\u0301", "\u2713",
                     "\u00bd", "\u201d", "\u00bb", "\u03a9", "\u00df", "\u3000"]
    cells = ["".join(draw.choice(alphabet) for _ in range(draw.randint(1, 32)))
             for alphabet in (plain, other) for _cell in range(20_000)]

    def case() -> None:
        differ = []
        for cell in cells:
            whole = taxonomy._holds_a_sentence_mark(cell) and taxonomy._a_sentence_read_whole(cell)
            if taxonomy.a_sentence(cell) != whole:
                differ += [cell]
        assert not differ, differ[:4]

    assert sum(1 for cell in cells if not cell.isascii() and taxonomy._ending_plainly(cell)) > 100
    _red(case, taxonomy, "_a_word_in", lambda part: True)


OTHER_SCRIPTS = (
    ("Осмотрен", "дома", "сегодня", "жалоб", "нет", "давление", "норма", "лечение"),
    ("εξέταση", "στην", "κλινική", "σήμερα", "χωρίς", "πόνο", "θεραπεία", "συνεχίζεται"),
    ("Revisé", "côté", "été", "évalué", "réglé", "arrêté", "noté", "là"),
)


def test_the_short_cut_answers_a_note_of_any_script_ending_in_a_full_stop() -> None:
    """The statistics check's item 7 (the combined verify's minor 4, V10 and V11): 900 generated notes of three to seven Cyrillic, Greek or accented Latin words, each word ending in a letter of no ASCII, closed by a full stop, a question or an exclamation mark, are answered by the short cut, the character-by-character reading never asked; red where the short cut reads ASCII text alone, and where a letter of another script is no word's character to it."""
    draw = random.Random(4813)
    cells = [" ".join(draw.choice(words) for _ in range(draw.randint(3, 7))) + draw.choice(".?!")
             for words in OTHER_SCRIPTS for _cell in range(300)]

    def refused(body: str) -> bool:
        raise AssertionError("the whole reading was asked")

    def case() -> None:
        with _mutant(taxonomy, "_a_sentence_read_whole", refused):
            unread = [cell for cell in cells if not taxonomy.a_sentence(cell)]
        assert not unread, unread[:4]

    plain = taxonomy._ending_plainly
    assert all(not cell.isascii() for cell in cells)
    _red(case, taxonomy, "_ending_plainly", lambda body: body.isascii() and plain(body))
    _red(case, taxonomy, "_a_word_character", lambda one: one < "\x80" and one.isalnum())


def _settled_for_the_others_at_half(spellings: "dict[str, int]", present: int) -> bool:
    """`sentences_hold` settled for the other cells as soon as THEY hold half (skeptic 1's mutant M02)."""
    sentences = others = 0
    for spelling, rows in spellings.items():
        if taxonomy.a_sentence(spelling):
            sentences += rows
        else:
            others += rows
        if 2 * others >= present:
            return False
        if 2 * sentences >= present:
            return True
    return 2 * sentences >= present


def test_half_the_cells_make_a_column_of_sentences() -> None:
    """A comparison of counts: half the present cells sentences is a column of sentences whichever kind of cell comes first, one fewer is not; red on a strict half, and where the pass settles for the other cells at their half."""
    sentence, label = "Seen in clinic. Plan agreed.", "Nil by mouth"

    def case() -> None:
        assert taxonomy.sentences_hold({sentence: 10, label: 10}, 20)
        assert taxonomy.sentences_hold({label: 10, sentence: 10}, 20)
        assert not taxonomy.sentences_hold({sentence: 9, label: 11}, 20)
        assert taxonomy.a_sentence_column([sentence] * 10 + [label] * 10)
        assert taxonomy.a_sentence_column([label] * 10 + [sentence] * 10)

    _red(case, taxonomy, "sentences_hold", lambda spellings, present: 2 * sum(
        rows for cell, rows in spellings.items() if taxonomy.a_sentence(cell)) > present)
    _red(case, taxonomy, "sentences_hold", _settled_for_the_others_at_half)


def test_a_long_cell_is_read_on_its_first_4000_characters() -> None:
    """A note of 4,500 characters whose first mark stands past character 200 is a sentence; one whose only mark stands past character 4,000 is not (the read bound, a stated limit of P4-D481 (c)); red where the bound is cut to 200, and where it is lifted."""
    early = " ".join(["word"] * 60) + " seen today. " + " ".join(["more"] * 840)
    late = " ".join(["word"] * 840) + " seen today. " + " ".join(["more"] * 60)
    assert len(early) >= 4_500 and len(late) >= 4_500
    assert 200 < early.index(".") < 4_000 < late.index(".")

    def case() -> None:
        assert taxonomy.a_sentence(early)
        assert not taxonomy.a_sentence(late)

    _red(case, taxonomy, "SENTENCE_READ_AT_MOST", 200)
    _red(case, taxonomy, "SENTENCE_READ_AT_MOST", 10_000)


def test_a_run_of_marks_is_read_in_time_linear_in_its_length() -> None:
    """Skeptic 1's item 5: a word followed by 3,900 stops before another word (glued, spaced, behind marks that are no word's), by 3,900 colons, by stops between closers, by 3,900 spaces before a stop, or by 1,990 stops and 1,990 spaces before a stop and a word (each stop's spaces read once: the combined verify's minor 4, V13, 0.15 s where they are read again for every stop), is read in under 0.05 CPU seconds (0.29 s for 3,990 stops, and four times longer for each doubling, before repair 1), its answer the rule's; each cell within the read bound; the best of three runs."""
    import time

    cells = [
        ("Seen in clinic" + "!" * 3_900 + "x", False),
        ("Seen in clinic " + "." * 3_900 + " ✓ ok", False),
        ("Seen in clinic" + "." * 3_900 + " " + "✓" * 3 + " ok", False),
        ("Seen in clinic" + ":" * 3_900 + "x", False),
        ("Seen in clinic" + ".\"" * 1_950 + " ok", True),
        ("Seen in clinic" + " " * 3_900 + ". ok", True),
        ("Seen in clinic" + "." * 1_990 + " " * 1_990 + ". x", True),
    ]
    for cell, expected in cells:
        assert len(cell) <= taxonomy.SENTENCE_READ_AT_MOST
        spent = 1.0
        for _run in range(3):
            started = time.process_time()
            read = taxonomy._a_sentence_read_whole(cell[: taxonomy.SENTENCE_READ_AT_MOST])
            spent = min(spent, time.process_time() - started)
            assert read == expected, cell[:30]
        assert spent < 0.05, (cell[:30], spent)


def _settings(floor: int = 11) -> taxonomy.Settings:
    return taxonomy.Settings(small_cell_floor=floor)


def test_a_column_of_sentences_is_described_as_free_text() -> None:
    """`profile_column(..., forced_text=True)`: a stock bank read as a set of categories is described as free text, its evidence the sentence that names no value, no level published and its repetition kept; a column of codes keeps its bytes; without the flag the bank is read as before (`sentences` recorded either way)."""
    bank = forms.stock_pool()[10:60]
    values = [bank[place % 50] for place in range(2_000)]
    codes = [f"Soft {kind}" for kind in "ABCDE"] * 400
    plain = taxonomy.profile_column("note", 1, values, len(values), _settings())
    forced = taxonomy.profile_column("note", 1, values, len(values), _settings(), forced_text=True)
    assert plain.role == taxonomy.ROLE_CATEGORICAL and plain.sentences
    assert forced.role == taxonomy.ROLE_TEXT and forced.sentences
    assert forced.detection_evidence == taxonomy.rendered(taxonomy.EVIDENCE_SENTENCES_AS_TEXT, ())
    said = json.dumps(forced.details)
    assert not any(json.dumps(cell)[1:-1] in said for cell in bank)
    assert forced.details["n_distinct_by_occurrences"] == {"40": 50}
    coded = taxonomy.profile_column("diet", 1, codes, len(codes), _settings(), forced_text=True)
    assert coded == taxonomy.profile_column("diet", 1, codes, len(codes), _settings())
    assert coded.role == taxonomy.ROLE_CATEGORICAL and not coded.sentences


def _roles_columns() -> "dict[str, tuple[str, list[str]]]":
    """A constant, a two-valued and a numbers-with-labels column of sentences, and an affixed number whose shared text is a sentence, each with the role the base reads it under."""
    draw = random.Random(4812)
    stock = forms.stock_pool()[20:25]
    numbers = [f"{draw.uniform(1, 400):.1f}" if place % 5 < 2 else stock[place % 5] for place in range(20_000)]
    return {
        "constant": (taxonomy.ROLE_CONSTANT, [stock[0]] * 2_000),
        "two_valued": (taxonomy.ROLE_BINARY, [stock[place % 2] for place in range(2_000)]),
        "numbers_with_labels": (taxonomy.ROLE_COMPOUND, numbers),
        "affixed": (taxonomy.ROLE_AFFIXED, [f"Seen in clinic {draw.randint(1, 5_000)}. Plan agreed." for _ in range(20_000)]),
    }


def test_a_constant_a_two_valued_and_a_numbers_with_labels_column_of_sentences_are_free_text() -> None:
    """Skeptic 1's item 4: each role that publishes levels is reached by a column of sentences and described as free text under `forced_text` -- a constant and a two-valued column of stock sentences (2,000 rows) and numbers beside stock sentences, their label half 60 per cent of 20,000 cells -- while an affixed number whose shared text is a sentence (`Seen in clinic 4. Plan agreed.` over 5,000 figures, 20,000 cells) keeps its role and its numbers: its affixes are text every row wears, published as on the base; red where any of the three roles leaves `SENTENCE_ROLES`, and where the affixed role joins it."""
    columns = _roles_columns()

    def case() -> None:
        for name, (role, values) in columns.items():
            plain = taxonomy.profile_column(name, 1, values, len(values), _settings())
            forced = taxonomy.profile_column(name, 1, values, len(values), _settings(), forced_text=True)
            assert plain.role == role, (name, plain.role)
            if role == taxonomy.ROLE_AFFIXED:
                assert forced == plain and not plain.sentences, name
            else:
                assert forced.role == taxonomy.ROLE_TEXT and forced.sentences, (name, forced.role)

    roles = taxonomy.SENTENCE_ROLES
    for role in (taxonomy.ROLE_CONSTANT, taxonomy.ROLE_BINARY, taxonomy.ROLE_COMPOUND):
        _red(case, taxonomy, "SENTENCE_ROLES", tuple(one for one in roles if one != role))
    _red(case, taxonomy, "SENTENCE_ROLES", roles + (taxonomy.ROLE_AFFIXED,))


def test_a_column_of_sentences_read_before_is_not_decided_again() -> None:
    """The statistics check's item 7: the reading a column's first description found a column of sentences, handed over with ``sentences_read``, is described as free text field for field as a reading made afresh is, without deciding its role or reading its sentences again; a reading that is not the one handed over is decided as before; red where the hand-over is not taken."""
    bank = forms.stock_pool()[10:60]
    values = [bank[place % 50] for place in range(2_000)]
    kept: "list[taxonomy.HeldReading]" = []
    first = taxonomy.profile_column("note", 1, values, len(values), _settings(), kept=kept)
    assert first.sentences and first.role in taxonomy.SENTENCE_ROLES and len(kept) == 1
    afresh = taxonomy.profile_column("note", 1, values, len(values), _settings(), forced_text=True)

    def refused(*arguments: object, **keywords: object) -> object:
        raise RuntimeError("the role was decided again")

    def case() -> None:
        with _mutant(taxonomy, "_decision", refused), _mutant(taxonomy, "sentences_hold", refused):
            handed = taxonomy.profile_column("note", 1, values, len(values), _settings(), handed_over=kept[0],
                                             forced_text=True, sentences_read=True)
        assert handed == afresh

    case()
    with _mutant(taxonomy, "_same_reading", lambda *arguments, **keywords: False), pytest.raises(RuntimeError):
        case()
    other = list(values)
    other[0] = bank[1]
    assert taxonomy.profile_column("note", 1, other, len(other), _settings(), handed_over=kept[0], forced_text=True,
                                   sentences_read=True) == taxonomy.profile_column(
        "note", 1, other, len(other), _settings(), forced_text=True)
    # ...AND THE WORD OF A HAND-OVER IS TAKEN ONLY WITH ITS READING (the combined
    # verify's minor 4, V21): a column of codes handed a reading of sentences is
    # decided as before, its levels kept.
    codes = [f"Soft {kind}" for kind in "ABCDE"] * 400

    def taken_only_with_its_reading() -> None:
        handed = taxonomy.profile_column("note", 1, codes, len(codes), _settings(), handed_over=kept[0],
                                         forced_text=True, sentences_read=True)
        assert handed == taxonomy.profile_column("note", 1, codes, len(codes), _settings(), forced_text=True)
        assert handed.role == taxonomy.ROLE_CATEGORICAL and not handed.sentences

    _red(taken_only_with_its_reading, taxonomy, "_same_reading", lambda *arguments, **keywords: True)


def test_the_description_decides_a_column_of_sentences_once(tmp_path: pathlib.Path) -> None:
    """The statistics check's item 7 through `profile.build_document` (the combined verify's minor 4, V22): a column of 50 stock sentences on 2,000 rows is described as free text with no more decisions of a role than a column of five codes in its place -- the reading its first description found a column of sentences is handed over, not decided again; red where the hand-over is not taken."""
    bank = forms.stock_pool()[10:60]
    calls: "list[int]" = []
    decided = taxonomy._decision

    def counted(*arguments: object, **keywords: object) -> object:
        calls.append(1)
        return decided(*arguments, **keywords)  # type: ignore[arg-type]

    def decisions(values: "list[str]") -> "tuple[int, dict]":
        calls.clear()
        with _mutant(taxonomy, "_decision", counted):
            document = _document(tmp_path, ["note"], [[value] for value in values], [])
        return len(calls), _blocks(document)["note"]

    def case() -> None:
        sentences, block = decisions([bank[place % 50] for place in range(2_000)])
        codes, coded = decisions([f"Soft {kind}" for kind in "ABCDE"] * 400)
        assert block["role"] == taxonomy.ROLE_TEXT and coded["role"] == taxonomy.ROLE_CATEGORICAL
        assert sentences == codes >= 1, (sentences, codes)

    _red(case, taxonomy, "_same_reading", lambda *arguments, **keywords: False)


def _document(
    folder: pathlib.Path, header: "list[str]", rows: "list[list[str]]", declared: "list[str]", **options: object
) -> "dict[str, object]":
    """`profile.build_document` of an invented table, read from a file as the command reads it."""
    from synthtwin import profile, reading

    path = folder / "t.csv"
    path.write_bytes(zoo.csv_bytes(header, rows))
    return profile.build_document(reading.read_table(f"{path}"), _settings(), declared, **options)  # type: ignore[arg-type]


def _blocks(document: "dict[str, object]") -> "dict[str, dict]":
    return {f"{block['name']}": block for block in document["columns"]}  # type: ignore[union-attr]


def test_the_holds_keep_precedence_and_the_people_s_hold_gives_way(tmp_path: pathlib.Path) -> None:
    """N5 and N10 through `profile.build_document` (a test device of 2,000 rows and 100 people, the person column declared): a stock bank is free text; a title template lane CZ-E holds keeps its hold and its reason; a bank of 900 whose rare sentences few people hold is free text, not held as record numbers; a column of codes keeps its levels; a declared record number stays one; red without the reading."""
    header, rows = forms.notes_table(2_000, 7, ("tpl216", "remark_t", "tpl900", "codes30"))
    said = taxonomy.rendered(taxonomy.EVIDENCE_SENTENCES_AS_TEXT, ())

    def case() -> None:
        reasons: "dict[str, str]" = {}
        document = _document(tmp_path, header, rows, ["subject_id"], top_code=True,
                             harbor_year=taxonomy.SAFE_HARBOR_REFERENCE_YEAR, harbor_reasons=reasons,
                             five_figures=[], subjects=["subject_id"])
        blocks = _blocks(document)
        assert blocks["tpl216"]["role"] == taxonomy.ROLE_TEXT and blocks["tpl216"]["detection_evidence"] == said
        assert blocks["tpl900"]["role"] == taxonomy.ROLE_TEXT, blocks["tpl900"]["role"]
        assert reasons.get("remark_t") == taxonomy.HELD_IDENTIFIER_WORDS, reasons
        assert blocks["remark_t"]["detection_evidence"] != said
        assert blocks["codes30"]["role"] == taxonomy.ROLE_CATEGORICAL

    _red(case, taxonomy, "sentences_hold", lambda spellings, present: False)
    declared = _blocks(_document(tmp_path, header, rows, ["subject_id", "tpl216"]))
    assert declared["tpl216"]["role"] == taxonomy.ROLE_IDENTIFIER


def test_the_rare_levels_of_a_column_of_sentences_are_never_named() -> None:
    """N8: lane CODES-2's roads name no held-back level of a column of sentences, whatever the answer, and its question is not put for them; NOR OF A LABEL COLUMN ANY OF WHOSE HELD-BACK LEVELS IS A SENTENCE (skeptic 1's item 1, a HIPAA blocker: codes beside comments typed by few people, each naming a made-up person, answered `no`, with the code declared and without); a column of words keeps its roads; red without the guard, and on the mutant of each of its two new conditions."""
    sentences = ["Seen in clinic. Plan agreed."] * 40 + [f"Seen with Ma{tag}rin Dorby. Plan agreed." for tag in "abcdef"]
    words = ["Not done"] * 40 + ["TNP", "HI", "LO", "QNS", "NR", "ND"]
    given = ("Marin", "Telo", "Rona", "Livik", "Sasel", "Notor")
    comments = [forms.RARE_COMMENTS[place].format(g=name, f="Dorby") for place, name in enumerate(given)]
    coded = [code for code in forms.RESULT_CODES for _row in range(40)] + comments

    def levels_of(cells: "list[str]", how: str) -> "tuple[taxonomy._Levels, taxonomy._Cells]":
        read = taxonomy._read_the_column(cells, len(cells), taxonomy.Settings(small_cell_floor=11, held_back_named=how))
        label_counts, label_mixed = taxonomy._label_maps(read.cells)
        return taxonomy._levels(label_counts, label_mixed, read.cells.settings), read.cells

    def case() -> None:
        levels, cells = levels_of(sentences, taxonomy.HELD_BACK_NAMED_ANSWERED)
        assert levels.suppressed_levels == 6 and levels.held_back_names
        assert taxonomy.held_back_names_published(levels, cells, True, True) == ()
        assert not taxonomy.held_back_nameable(levels, cells, True, True)
        kept, kept_cells = levels_of(words, taxonomy.HELD_BACK_NAMED_ANSWERED)
        assert taxonomy.held_back_names_published(kept, kept_cells, True, True)

    def comments_case() -> None:
        levels, cells = levels_of(coded, taxonomy.HELD_BACK_NAMED_ANSWERED)
        assert not taxonomy.sentences_hold(cells.label_counts, len(cells.present))
        assert levels.suppressed_levels == 6 and sorted(levels.held_back_names) == sorted(comments)
        for declared in (True, False):
            assert taxonomy.held_back_names_published(levels, cells, True, declared) == (), declared
            assert not taxonomy.held_back_nameable(levels, cells, True, declared), declared
        kept, kept_cells = levels_of(words, taxonomy.HELD_BACK_NAMED_ANSWERED)
        assert taxonomy.held_back_names_published(kept, kept_cells, True, False)
        assert taxonomy.held_back_nameable(kept, kept_cells, True, True)

    with _mutant(taxonomy, "_a_sentence_among", lambda names: False):
        _red(case, taxonomy, "sentences_hold", lambda spellings, present: False)
    _red(comments_case, taxonomy, "_a_sentence_among", lambda names: False)
    # ...each new condition alone: the naming without its guard, the question without its own.
    published, nameable = taxonomy.held_back_names_published, taxonomy.held_back_nameable

    def published_unguarded(levels: "taxonomy._Levels", cells: "taxonomy._Cells", total: bool, declared: bool) -> object:
        with _mutant(taxonomy, "_a_sentence_among", lambda names: False):
            return published(levels, cells, total, declared)

    def nameable_unguarded(levels: "taxonomy._Levels", cells: "taxonomy._Cells", total: bool, declared: bool) -> object:
        with _mutant(taxonomy, "_a_sentence_among", lambda names: False):
            return nameable(levels, cells, total, declared)

    _red(comments_case, taxonomy, "held_back_names_published", published_unguarded)
    _red(comments_case, taxonomy, "held_back_nameable", nameable_unguarded)


def test_rare_typed_comments_with_or_without_a_mark_are_never_named() -> None:
    """The combined verify's new item 1, a HIPAA blocker (RULINGS 9 (1)): comments typed where a code was expected, each naming a made-up person, held back six at a time beside five codes of 40 rows and answered `no` -- GENERATED from sixteen templates with twelve made-up names each, every one written with its sentence marks (`Brother Marin Dorby called. Will ring back.`), with none (`Brother Marin Dorby called Will ring back`), and with none and each other space of the word screen's one definition between its words, three to seven words -- are named by no road, the code declared or not, and the question is not put for them; six two-word names and six short codes beside the codes keep their roads (P4-D471's limit (a)); red where three words no longer count, where two do, and where four are asked (the spaces' reading pinned by the source mutant of the repair's report)."""
    comments = forms.generated_comments(12, 4814)
    codes = [code for code in forms.RESULT_CODES for _row in range(40)]
    names = [" ".join(forms.made_up_name(random.Random(4815 + place))) for place in range(6)]
    short = ["TNP", "HI", "LO", "QNS", "NR", "ND"]
    batches: "list[list[str]]" = []
    for kind in ("marked", "no mark", "no mark, other spaces"):
        written = [comment for what, comment in comments if what == kind]
        batches += [written[start : start + 6] for start in range(0, len(written), 6)]

    def levels_of(cells: "list[str]") -> "tuple[taxonomy._Levels, taxonomy._Cells]":
        read = taxonomy._read_the_column(cells, len(cells), taxonomy.Settings(
            small_cell_floor=11, held_back_named=taxonomy.HELD_BACK_NAMED_ANSWERED))
        label_counts, label_mixed = taxonomy._label_maps(read.cells)
        return taxonomy._levels(label_counts, label_mixed, read.cells.settings), read.cells

    readings = [(batch, levels_of(codes + batch)) for batch in batches]
    controls = [(batch, levels_of(codes + batch)) for batch in (names, short)]

    def case() -> None:
        named = []
        for batch, (levels, cells) in readings:
            assert sorted(levels.held_back_names) == sorted(batch), batch[:2]
            for declared in (True, False):
                if taxonomy.held_back_names_published(levels, cells, True, declared) or taxonomy.held_back_nameable(
                    levels, cells, True, declared
                ):
                    named += [(declared, batch[0])]
        assert not named, (len(named), named[:4])
        for batch, (levels, cells) in controls:
            for declared in (True, False):
                assert sorted(taxonomy.held_back_names_published(levels, cells, True, declared)) == sorted(batch)
                assert taxonomy.held_back_nameable(levels, cells, True, declared), (declared, batch[0])

    assert len(batches) >= 60 and all(len(batch) == 6 for batch in batches)
    assert sum(1 for what, comment in comments if what == "no mark" and not taxonomy.a_sentence(comment)) >= 150
    _red(case, taxonomy, "_three_words_or_more", lambda name: False)
    _red(case, taxonomy, "SENTENCE_WORDS_AT_LEAST", 2)
    _red(case, taxonomy, "SENTENCE_WORDS_AT_LEAST", 4)


def test_the_question_names_no_value_and_is_not_put_again() -> None:
    """The question offers `text` and `identifier`, `text` standing, says the description's own counts and no cell, and says that publishing the phrases is not offered yet; a column answered `text` is asked nothing; `text` reads back as carried, in its own family, and is kept in `answered_before`; red where the question no longer finds the column."""
    bank = forms.stock_pool()[10:60]
    document = {"columns": [{
        "name": "note", "role": taxonomy.ROLE_TEXT, "n_present": 2000, "n_distinct": 50,
        "words": {"min": 3, "max": 9, "mean": 6.4},
        "detection_evidence": taxonomy.rendered(taxonomy.EVIDENCE_SENTENCES_AS_TEXT, ()),
    }, {"name": "codes", "role": taxonomy.ROLE_CATEGORICAL, "detection_evidence": "a set"}]}

    def case() -> None:
        put = asking.sentence_questions(document, (), 11)
        assert [(question.name, [choice.answer for choice in question.choices], question.taken) for question in put] == [
            ("note", [asking.ANSWER_TEXT, asking.ANSWER_IDENTIFIER], asking.ANSWER_TEXT)]

    # Red where the question no longer finds the column the description reads so.
    _red(case, asking, "_SENTENCES_EVIDENCE", "")
    asked = asking.sentence_questions(document, (), 11)
    assert "2000 values, 50 of them different, about 6 words" in asked[0].shape
    assert "not offered yet" in asked[0].shape
    assert not any(cell in asked[0].shape for cell in bank)
    assert asking.sentence_questions(document, ("note",), 11) == []
    file = asking.questions_document("t", asked, [])
    for entry in zoo._entries(file):
        entry["your_answer"] = asking.ANSWER_TEXT
    answers = asking.answers_in(file, "t-questions.json")
    assert answers.sentences_text == ("note",) and not answers.identifiers
    kept = asking.answered_before(asking.Given(columns=("note",), sentences_text=("note",)))
    assert [(entry["column"], entry["your_answer"]) for entry in kept] == [("note", asking.ANSWER_TEXT)]
    assert asking._family_of(asking.ANSWER_TEXT, (asking.ANSWER_TEXT, asking.ANSWER_IDENTIFIER)) == asking._FAMILY_SENTENCES
    carried = asking.questions_document("t", [], [], answered=kept, answered_columns=["note"])
    again = asking.answers_in(carried, "t-questions.json")
    assert again.sentences_text == ("note",)


def test_the_text_answer_has_its_own_key_at_the_keyboard() -> None:
    """Skeptic 1's item 4 (M27): `text` is typed as key 20 and key 20 reads back as `text`; red where the key is gone."""
    from synthtwin import cli

    def case() -> None:
        assert cli._ANSWER_KEYS.get("20") == asking.ANSWER_TEXT
        assert cli._KEY_OF.get(asking.ANSWER_TEXT) == "20"

    _red(case, cli, "_ANSWER_KEYS", {key: answer for key, answer in cli._ANSWER_KEYS.items() if key != "20"})
    _red(case, cli, "_KEY_OF", {answer: key for answer, key in cli._KEY_OF.items() if answer != asking.ANSWER_TEXT})


def test_one_question_a_column_and_text_is_not_asked_again_through_the_commands(tmp_path: pathlib.Path) -> None:
    """Skeptic 1's item 4 (M25, M26) on a TEST DEVICE (2,000 rows, 100 people of 20 rows -- the fewest people the library describes -- the table floor lifted; LANE I4m RULINGS 18: a test size, no product twin): stock banks of 216 and 900 sentences, the person column not said, are each put exactly ONE question -- the sentence question, offering `text` and `identifier` -- in place of the question whether the column names the person, which this file would put them too; answered `text`, the next run puts them none and carries the answers; red where the other question stands beside it, and where the answer is not carried."""
    import unanswered_identifier_shapes as shapes
    from synthtwin import cli

    header, rows = forms.notes_table(2_000, 20261112, ("tpl216", "tpl900", "codes30"))
    source = tmp_path / "notes.csv"
    source.write_bytes(zoo.csv_bytes(header, rows))
    questions = tmp_path / "notes-questions.json"
    screen = io.StringIO()
    notes = ("tpl216", "tpl900")

    def entries() -> "list[dict]":
        return [entry for entry in zoo._entries(json.loads(questions.read_text(encoding="utf-8")))
                if entry.get("column") in notes]

    with shapes.nobody_at_the_keyboard(), contextlib.redirect_stdout(screen), contextlib.redirect_stderr(screen):
        assert cli.main(["profile", f"{source}", "--replace"], small_tables_refused=False) == 0
        first = entries()
        assert sorted((entry["column"], sorted(zoo._offered(entry))) for entry in first) == [
            (column, sorted([asking.ANSWER_TEXT, asking.ANSWER_IDENTIFIER])) for column in notes]
        document = json.loads(questions.read_text(encoding="utf-8"))
        for entry in zoo._entries(document):
            if entry.get("column") in notes:
                entry["your_answer"] = asking.ANSWER_TEXT
        questions.write_text(json.dumps(document, indent=2), encoding="utf-8", newline="\n")
        assert cli.main(["profile", f"{source}", "--replace", "--answers", f"{questions}"], small_tables_refused=False) == 0
    assert not [entry for entry in entries() if entry.get("your_answer") in ("", None)]
    assert sorted(f"{entry.get('your_answer')}" for entry in entries()) in ([], [asking.ANSWER_TEXT] * 2)


def test_the_validator_s_hand_over_reads_filler_as_free_text(tmp_path: pathlib.Path) -> None:
    """``described_text``, the validator's hand-over of the columns its description read as free text for their sentences: a twin's filler of 50 made-up values in groups (no word in them) is read as free text there, and as a set of categories without it; a column it does not name keeps its reading."""
    filler = [f"{chr(35 + place % 50)}!!!! !!!! !!!!" for place in range(2_000)]
    header = ["subject_id", "note", "diet"]
    rows = [[f"S{100000 + place // 20}", filler[place], ("Soft A", "Low B")[place % 2]] for place in range(2_000)]
    handed = _blocks(_document(tmp_path, header, rows, ["subject_id"], described_text=["note"]))
    plain = _blocks(_document(tmp_path, header, rows, ["subject_id"]))
    assert handed["note"]["role"] == taxonomy.ROLE_TEXT
    assert handed["note"]["detection_evidence"] == taxonomy.rendered(taxonomy.EVIDENCE_SENTENCES_AS_TEXT, ())
    assert plain["note"]["role"] == taxonomy.ROLE_CATEGORICAL
    assert handed["diet"] == plain["diet"]


CASE_FAMILIES = ("tpl216", "remark_n", "remark_p", "codes30")


def test_the_stock_bank_and_the_templates_at_20000_rows(tmp_path: pathlib.Path) -> None:
    """THE ONE 20,000-ROW CASE (1,000 people of 20 rows, the person column said, through the commands a person types, nobody at the keyboard, the table floor on): the stock bank of 216 sentences and the name and place templates are free text, put the question with `text` and `identifier`, and no whole sentence of theirs, exact or folded, is shown in the description, the summary, the questions file or on the screen; the codes column keeps its 30 labels; the twin writes no real sentence, and its stock bank keeps the real number of groups and their sizes (a grouping by the column, made-up words); the real table validates against its description, and so does the twin, missing nothing: the validator's hand-over of the columns its description read as free text for their sentences (`validation.described_text_here` into `profile.build_document`'s ``described_text``, batch 4t's merge of the lane) re-describes them as free text, where before it the validator read the twin's filler as labels and missed `axes.role` and `axes.statistical_type` of the three columns (validate exited 3); and the twin checked in groups of one column (lane SV, plan P4-D476) exits, says and writes what it does checked whole -- the agreement of the two readings on a notes table."""
    import unanswered_identifier_shapes as shapes
    from synthtwin import cli, reading, validation

    folder = tmp_path / "run"
    folder.mkdir()
    header, rows = forms.notes_table(zoo.KPI_ROWS, 20261112, CASE_FAMILIES)
    source = folder / "notes.csv"
    source.write_bytes(zoo.csv_bytes(header, rows))
    real = {name: [row[place] for row in rows] for place, name in enumerate(header)}
    screen = io.StringIO()
    seen: "list[object]" = []
    measure = validation.measure
    checked = folder / "checked"

    def validated() -> "tuple[int, str, dict[str, bytes]]":
        """The twin checked against its description into one folder, emptied first: the exit, the screen and the files."""
        checked.mkdir(exist_ok=True)
        for old in checked.iterdir():
            old.unlink()
        said = io.StringIO()
        with contextlib.redirect_stdout(said), contextlib.redirect_stderr(said):
            code = cli.main(["validate", f"{folder / 'notes-profile.json'}", "--out-dir", f"{checked}", "--replace"],
                            small_tables_refused=True)
        return code, said.getvalue(), {path.name: path.read_bytes() for path in sorted(checked.iterdir())}

    def keep(description: object, path: str, sheet: str = "") -> object:
        outcome = measure(description, path, sheet)  # type: ignore[arg-type]
        seen.extend([outcome])
        return outcome

    with shapes.nobody_at_the_keyboard(), contextlib.redirect_stdout(screen), contextlib.redirect_stderr(screen):
        assert cli.main(["profile", f"{source}", "--identifier", "subject_id", "--replace"], small_tables_refused=True) == 0
        assert cli.main(["generate", f"{folder / 'notes-profile.json'}", "--replace", "--seed", "0"], small_tables_refused=True) == 0
        validation.measure = keep  # type: ignore[assignment]
        try:
            whole = validated()
            real_code = cli.main(["validate", f"{folder / 'notes-profile.json'}", "--twin", f"{source}", "--replace"],
                                 small_tables_refused=True)
        finally:
            validation.measure = measure  # type: ignore[assignment]
        # ...AND THE SAME TWIN CHECKED IN GROUPS OF ONE COLUMN (lane SV, plan P4-D476): `GROUP_BYTES` and
        # `WALK_BYTES` at 1 read every file in the most groups there are, as lane SV's gate reads them.
        with pytest.MonkeyPatch.context() as groups:
            groups.setattr(reading, "GROUP_BYTES", 1)
            groups.setattr(reading, "WALK_BYTES", 1)
            in_groups = validated()
    described = json.loads((folder / "notes-profile.json").read_text(encoding="utf-8"))
    blocks = _blocks(described)
    questions = json.loads((folder / "notes-questions.json").read_text(encoding="utf-8"))
    asked = {f"{entry.get('column', '')}": sorted(zoo._offered(entry)) for entry in zoo._entries(questions)}
    texts = [(folder / name).read_text(encoding="utf-8").casefold()
             for name in ("notes-profile.json", "notes-profile.txt", "notes-questions.json")] + [screen.getvalue().casefold()]
    # ...and what the twin's check said and wrote, whole and in groups.
    texts += [said.casefold() for _code, said, _files in (whole, in_groups)]
    texts += [data.decode("utf-8", "replace").casefold() for _code, _said, files in (whole, in_groups) for data in files.values()]
    with open(folder / "notes-twin.csv", encoding="utf-8", newline="") as handle:
        twin_rows = list(csv.reader(handle))
    twin = {name: [row[place] for row in twin_rows[1:]] for place, name in enumerate(twin_rows[0])}
    written = ("tpl216", "remark_n", "remark_p")
    for column in written:
        assert blocks[column]["role"] == taxonomy.ROLE_TEXT, (column, blocks[column]["role"])
        assert asked.get(column) == sorted([asking.ANSWER_TEXT, asking.ANSWER_IDENTIFIER]), (column, asked.get(column))
        sentences = {cell for cell in real[column] if taxonomy.a_sentence(cell)}
        shown = [cell for cell in sentences
                 if any(cell.casefold() in text or json.dumps(cell)[1:-1].casefold() in text for text in texts)]
        assert not shown, (column, shown[:3])
        assert not set(twin[column]) & set(real[column]), column
    assert blocks["codes30"]["role"] == taxonomy.ROLE_CATEGORICAL
    assert len(blocks["codes30"]["levels"]) == 30  # type: ignore[arg-type]

    def sizes(cells: "list[str]") -> "list[int]":
        counted: "dict[str, int]" = {}
        for cell in cells:
            counted[cell] = counted.get(cell, 0) + 1
        return sorted(counted.values())

    assert sizes(twin["tpl216"]) == sizes(real["tpl216"])
    missed = [
        [(check.column, f"{check.subcheck or check.fact}".split(".")[-1])  # type: ignore[attr-defined]
         for check in outcome.checks if check.verdict == validation.MISSED]  # type: ignore[attr-defined]
        for outcome in seen
    ]
    assert real_code == 0 and missed[1] == [], missed[1][:6]
    # BATCH 4t'S MERGE OF THE LANE: the validator's hand-over landed, so the twin validates (exit 0, nothing
    # missed) where the lane's head read 3 on `axes.role` and `axes.statistical_type` of the three columns.
    assert whole[0] == 0 and missed[0] == [], (whole[0], missed[0][:8])
    assert whole[2] and in_groups == whole, (whole[1][-1500:], in_groups[1][-1500:])
    assert parsing.TABLE_ROW_FLOOR <= zoo.KPI_ROWS
