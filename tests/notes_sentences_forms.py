"""Invented note columns for lane NOTES (plan P4-D481, K-HZ-34): sentences, and what is no sentence.

EVERY WORD, NAME, PLACE AND FIGURE HERE IS MADE UP: names and places are
built from syllables, the stock phrases are this module's own, and the
figures are drawn. Nothing is learnt from any real table.

THE GENERATED SENTENCES (`sentence_families`): openings, what was found and plans
of this module's own, each family carrying one variable part -- a person's
name with and without a title, a family name alone, initials; a date in
the spellings a date reader reads; a pressure, a weight, a score, a dose,
a count; a place of one or two capitalised words before a clinic, town or
hospital word; a relative and a name; a telephone number -- written with
every sentence mark and in every position (`marks_and_spaces`): the marks
of the reading, every space of the word screen's one definition between
the words, before and after a mark, doubled, glued to the word, beside
accented and non-Latin letters and full-width figures. WHAT MUST NOT BE
READ (`not_sentences`): short codes, complaints joined by commas, labels of
two words with a point, ancestry, facility, department and organism names,
Likert words, comments of two to four words, plain word strings with no
sentence mark, decimals, clocks and ratios.

THE TABLES (`notes_table`): one person column of 1,000 people of 20 rows
each at 20,000 rows, and note columns of each family (`TABLE_FAMILIES`):
stock banks of 5, 50, 216 and 900 sentences (the bank of five holding one
sentence of one word), free text all different, a mix of 70 per cent stock
and 30 per cent unique, the templates with one variable part, short codes
and complaints, and label columns whose few rows carry typed comments, with
a sentence mark and without.
"""

from __future__ import annotations

import random

GIVEN_A = ("Ma", "Te", "Ro", "Li", "Sa", "No", "Vi", "Ka", "Du", "Pe", "Jo", "Ha")
GIVEN_B = ("rin", "lo", "na", "vik", "sel", "tor", "ma", "bel")
FAMILY_A = ("Dor", "Kel", "Mar", "Ves", "Tal", "Gram", "Pol", "Wen", "Brak", "Sut")
FAMILY_B = ("by", "ton", "quist", "ridge", "ello", "mere", "stad", "wick")
PLACE_A = ("Bren", "Cal", "Dun", "Fen", "Hart", "Kil", "Lor", "Marl", "Pen", "Tor")
PLACE_B = ("moor", "wick", "dale", "ford", "holt", "mere", "ridge", "stow")
PLACE_C = ("Cross", "Green", "Vale", "End", "Hill")
PLACE_WORDS = ("clinic", "town", "hospital", "outreach", "surgery")
TITLES = ("Dr", "Dr.", "Mr", "Mrs", "Ms", "Prof", "Nurse")
RELATIVES = ("son", "daughter", "wife", "husband", "mother", "father", "sister", "brother")
MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
MONTH_NAMES = ("January", "March", "June", "October")

OPENINGS = (
    "Reviewed in clinic", "Seen at the bedside", "Brief follow-up", "Patient comfortable",
    "Settled overnight", "Ward round review", "Phone consultation", "Wound review", "Yearly check",
    "Same-day visit",
)
FOUND = (
    "Eating and drinking", "No fresh concerns", "Pain under control", "Walking unaided",
    "Dressing dry and intact", "Slept through the night", "Appetite improving", "Some nausea, now settled",
    "Passing urine normally", "No fever", "In good spirits", "Breathing easily",
)
PLANS = (
    "Plan: review if worse", "Plan: same care", "Recheck in a fortnight", "Home today",
    "Plan: bloods tomorrow", "Review as required", "Plan: refer to therapy", "Continue usual tablets",
)
SINGLE = ("Settled.", "Better.", "No change.", "Gone home.", "Reviewed.")
# A stock sentence of one word (no sentence by the reading, which asks three),
# the last of the bank of five (`notes_table`).
ONE_WORD_SENTENCE = "Stable."

# THE MARKS OF THE READING (`taxonomy.a_sentence`): a full stop, a question or
# exclamation mark and their full-width, small, ideographic, double and
# ellipsis forms; a colon and a semicolon and their full-width and small
# forms; a line break.
STOPS = (
    ".", "?", "!", "．", "！", "？", "﹒", "﹖", "﹗", "。", "｡",
    "․", "‼", "⁇", "⁈", "⁉", "…",
)
JOINS = (":", ";", "：", "；", "﹕", "﹔")
BREAKS = ("\n", "\r", "\r\n", "\x85", " ", " ")
# THE SPACES OF THE WORD SCREEN'S ONE DEFINITION a generated sentence writes
# between its words (RULINGS 1 (4)): tab, the vertical tab and form feed, the
# no-break space, the spaces of U+1680 and U+2000 to U+200F, U+202F, U+205F,
# U+2060, U+3000, U+FEFF.
SPACES = (
    " ", "\t", "\x0b", "\x0c", " ", " ", " ", " ", " ", " ", " ",
    " ", " ", " ", " ", " ", " ", "​", "‌", "‍", "‎",
    "‏", " ", " ", "⁠", "　", "﻿",
)
# THE MARKS A NOTE MAY CARRY AFTER ITS LAST STOP (lane NOTES's repair 1, skeptic
# 1's item 2), with a space before or glued: a tick, dashes, a hash, a star, a
# bullet, a degree sign, an arrow. A stop after the last word ends the
# sentence whatever follows it.
TRAILING = (" ✓", " --", " #", "*", " •", " °", "✓", " ->")
# Words of other scripts and accents, and full-width figures, a sentence may hold.
OTHER_WORDS = (
    ("Revisé", "en", "clinique"), ("Osmotren", "v", "klinike"), ("Осмотрен", "в", "клинике"),
    ("εξέταση", "στην", "κλινική"),
    ("患者", "状态", "稳定"), ("seen", "２", "times"), ("Gesund", "nach", "Therapie"),
)


def made_up_name(draw: random.Random) -> "tuple[str, str]":
    """A made-up given name and family name, built from syllables."""
    return draw.choice(GIVEN_A) + draw.choice(GIVEN_B), draw.choice(FAMILY_A) + draw.choice(FAMILY_B)


def made_up_place(draw: random.Random) -> str:
    """A made-up place of one or two capitalised words."""
    place = draw.choice(PLACE_A) + draw.choice(PLACE_B)
    if draw.random() < 0.4:
        place = f"{place} {draw.choice(PLACE_C)}"
    return place


def _a_date(draw: random.Random) -> str:
    month = draw.randint(1, 12)
    day = draw.randint(1, 28)
    year = draw.randint(2015, 2026)
    return draw.choice((
        f"{month:02d}/{day:02d}", f"{month}/{day}/{year}", f"{day} {MONTHS[month - 1]}",
        f"{MONTHS[month - 1]} {day}", f"{year}-{month:02d}-{day:02d}", f"{day:02d}.{month:02d}.{year}",
        f"{draw.choice(MONTH_NAMES)} {day}, {year}", f"{day}-{MONTHS[month - 1]}-{year}",
    ))


def _a_telephone(draw: random.Random) -> str:
    return draw.choice((
        f"555-{draw.randint(1000, 9999)}", f"(555) {draw.randint(200, 999)}-{draw.randint(1000, 9999)}",
        f"555.{draw.randint(200, 999)}.{draw.randint(1000, 9999)}",
    ))


def _variable(family: str, draw: random.Random) -> str:
    """One made-up variable part of a family."""
    given, last = made_up_name(draw)
    if family == "name":
        return draw.choice((f"{given} {last}", f"{last} team", f"{given} {last}, nurse"))
    if family == "title":
        return f"{draw.choice(TITLES)} {draw.choice((last, given + ' ' + last))}"
    if family == "family":
        return last
    if family == "initials":
        return draw.choice((f"{given[0]}.{last[0]}.", f"{given[0]}{last[0]}", f"{given[0]}. {last}"))
    if family == "date":
        return _a_date(draw)
    if family == "figure":
        return draw.choice((
            f"BP {draw.randint(90, 180)}/{draw.randint(50, 110)}", f"weight {draw.randint(40, 140)} kg",
            f"pain score {draw.randint(0, 10)}/10", f"dose {draw.choice((5, 10, 20, 40))} mg",
            f"{draw.randint(2, 9)} falls this year", f"temp {draw.choice(('36.6', '37.1', '38.2'))}",
        ))
    if family == "place":
        return f"{made_up_place(draw)} {draw.choice(PLACE_WORDS)}"
    if family == "relative":
        return f"{draw.choice(RELATIVES)} {given} {last}"
    if family == "telephone":
        return _a_telephone(draw)
    return ""


VARIABLE_FAMILIES = ("name", "title", "family", "initials", "date", "figure", "place", "relative", "telephone")
_TEMPLATES = (
    "{o}. Seen with {v}. {p}.", "{o}, discussed with {v}. {p}.", "{v} to review tomorrow. {p}.",
    "{o}. {f}. Next contact: {v}.", "{o}; {v} aware. {f}.", "{f}. Plan agreed with {v}!",
    "{o}. Is {v} informed? {p}.", "{o}\n{v} called\n{p}.",
)


def sentence_families(count: int, seed: int) -> "dict[str, list[str]]":
    """Generated sentences by family: `count` of each variable-part family, and the stock phrases."""
    draw = random.Random(seed)
    found: "dict[str, list[str]]" = {}
    for family in VARIABLE_FAMILIES:
        cells: "list[str]" = []
        while len(cells) < count:
            template = draw.choice(_TEMPLATES)
            cells += [template.format(
                o=draw.choice(OPENINGS), f=draw.choice(FOUND), p=draw.choice(PLANS), v=_variable(family, draw),
            )]
        found[family] = cells
    found["stock"] = stock_pool()
    return found


def stock_pool() -> "list[str]":
    """Every stock sentence of this module: an opening, an opening and a plan or a finding, or all three."""
    pool = [f"{o}." for o in OPENINGS]
    pool += [f"{o}. {p}." for o in OPENINGS for p in PLANS]
    pool += [f"{o}. {m}." for o in OPENINGS for m in FOUND]
    pool += [f"{o}. {m}. {p}." for o in OPENINGS for m in FOUND for p in PLANS]
    return pool


def marks_and_spaces() -> "list[tuple[str, str]]":
    """Every mark of the reading in every position, every space of the one definition between the words: (what, cell)."""
    found: "list[tuple[str, str]]" = []
    words = ("Seen", "in", "clinic")
    after = ("Plan", "agreed")
    for space in SPACES:
        body = space.join(words)
        rest = space.join(after)
        for stop in STOPS:
            found += [
                ("stop ending the cell", f"{body}{stop}"),
                ("stop, space before", f"{body}{space}{stop}"),
                ("stop doubled", f"{body}{stop}{stop}"),
                ("stop before a word", f"{body}{stop}{space}{rest}"),
                ("stop before a closing quote", f"\"{body}{stop}\""),
                ("stop, spaces doubled", f"{body}{space}{space}{stop}{space}{space}{rest}"),
            ]
        for join in JOINS:
            found += [
                ("join before a word", f"{rest}{join}{space}{body}"),
                ("join, space before", f"{rest}{space}{join}{space}{body}"),
            ]
        for line in BREAKS:
            found += [("a line break between words", f"{body}{line}{rest}")]
        for stop in STOPS:
            for mark in TRAILING:
                found += [
                    ("a stop, then a trailing mark", f"{body}{stop}{mark}"),
                    ("two sentences, then a trailing mark", f"{body}{stop}{space}{rest}{stop}{mark}"),
                ]
    for parts in OTHER_WORDS:
        for stop in STOPS:
            found += [("other letters and figures", " ".join(parts) + stop)]
        for join in JOINS:
            found += [("other letters, a join", f"{parts[0]}{join} {parts[1]} {parts[2]}")]
    return found


# The marks of the scripts written with no space between sentences, written
# here and not taken from the reader: a sentence may run on after one with no
# space; after any other mark it may not (`glued_to_the_next_word`).
UNSPACED = ("\u3002", "\uff61", "\uff0e", "\uff01", "\uff1f", "\uff1a", "\uff1b")


def glued_to_the_next_word() -> "list[tuple[str, str, bool]]":
    """Every mark glued to the next word, with no other mark in the cell: (mark, cell, whether it is a sentence) -- one after the marks of `UNSPACED` alone."""
    found: "list[tuple[str, str, bool]]" = []
    for space in SPACES:
        for stop in STOPS:
            found += [(stop, f"Seen{space}in{space}clinic{stop}Plan{space}agreed", stop in UNSPACED)]
        for join in JOINS:
            found += [(join, f"Plan{space}agreed{join}Seen{space}in{space}clinic", join in UNSPACED)]
    return found


def abbreviated_labels() -> "tuple[str, ...]":
    """Labels written after a capitalised abbreviation and its point (lane NOTES's repair 1, the statistics check's item 1): a facility (`St.`, `Mt.`, `Ft.`, `Univ.`, `Gen.` before a made-up name and a clinic or hospital word), a department (`Dept.`, `Div.` of a specialty), a titled made-up name (`Dr.`, `Mr.`, `Mrs.`, `Prof.`), a medicine's label (`Vit.`, `Inj.`)."""
    found: "list[str]" = []
    names = [a + b for a in PLACE_A[:6] for b in PLACE_B[:3]]
    for short in ("St", "Mt", "Ft", "Univ", "Gen"):
        for place, name in enumerate(names):
            found += [f"{short}. {name} {('Hospital', 'Clinic', 'Medical Center', 'Health Centre')[place % 4]}"]
    for short in ("Dept", "Div"):
        for unit in ("Surgery", "Medicine", "Cardiology", "Pediatrics", "Internal Medicine", "Obstetrics and Gynecology"):
            found += [f"{short}. of {unit}"]
    for short in ("Dr", "Mr", "Mrs", "Prof"):
        for given in GIVEN_A[:6]:
            found += [f"{short}. {given}{GIVEN_B[0]} {FAMILY_A[0]}{FAMILY_B[1]}"]
    found += [f"Vit. {kind} tablets" for kind in ("D3", "B12", "C", "K")] + [f"Inj. {kind} given" for kind in ("B12", "K")]
    return tuple(found)


NOT_SENTENCES = abbreviated_labels() + (
    # short codes and labels of two words, with a point or not
    "NPO", "Nil by mouth", "Fluids only", "Soft diet", "Low salt", "Dysphagia A", "Seen.", "No addendum.",
    "Not done.", "Patient declined.", "Pt. refused", "E. coli", "S. aureus", "K. pneumoniae",
    # complaints joined by commas, and comments of two to four words
    "chest pain, breathless", "fever, cough", "fall, hip pain", "sickness, loose stools", "Patient stable",
    "Patient said \"fine\" today", "Wound clean...", "Rose 5%.",
    # ancestry, facility, department and organism names, Likert words
    "Black or African American", "Not Hispanic", "Ward 3", "Maternity", "General Medicine Ward",
    "Strongly agree", "Neither agree nor disagree", "Somewhat disagree",
    # plain word strings with no mark, decimals, clocks, ratios, initials, lists
    # glued by a mark, addresses
    "E11.9;I10;N18.3", "aa:bb:cc:dd:ee:ff", "first.last@host.org seen", "BP:120/80 HR:72 RR:16",
    "Dose \uff13\uff0e\uff15 mg daily", "Seen at \uff11\uff10\uff1a\uff13\uff10 today",
    "seen clinic with nurse unchanged", "referred for review of results", "Dose 3.5 mg daily",
    "Seen at 10:30 today", "titre 1:40 noted", "J. K. Smith seen", "version 4.2.1 here", "500 mg BID",
    "1-2 tabs at night", "q6h as needed", "p.Arg117His heterozygous variant", "c.35delG in GJB2 gene",
)


# COMMENTS TYPED WHERE A LABEL WAS EXPECTED (lane NOTES's repair 1, skeptic 1's
# item 1): twelve, each naming a made-up person, seven a relative too, each on
# two rows of one or two people (`comment_rows`).
RARE_COMMENTS = (
    "Spoke to wife {g} {f}. Agreed.", "Reviewed by {g} {f} today.", "Son {g} {f} visiting.",
    "Brother {g} {f} called. Will ring back.", "Daughter {g} {f} to collect. Discussed.",
    "Seen with husband {g} {f}. Plan agreed.", "Mother {g} {f} present. Happy.", "Discussed with {g} {f}. Agreed.",
    "{g} {f} phoned the ward.", "Message left for {g} {f}. No reply.", "Consent witnessed by {g} {f}.",
    "Spoke to sister {g} {f} by phone.",
)
RESULT_CODES = ("Normal", "Abnormal", "Borderline", "Not done", "Repeat")
WARD_LABELS = ("Bed rest", "Walking aid", "Up and about")
# ...AND THE SAME COMMENTS TYPED WITH NO SENTENCE MARK (lane NOTES's repair 2,
# the combined verify's new item 1: `Brother Sana Talby called back`), and
# comments of three words with a mark and without, for the generated case.
SHORT_COMMENTS = ("Called {g} {f}.", "{g} {f} phoned.", "Saw {g} {f}!", "{g} {f} visiting?")


def without_marks(comment: str) -> str:
    """A comment with every sentence mark taken out and its spaces kept single (`Brother Sana Talby called back`)."""
    return " ".join("".join(" " if character in ".?!:;" else character for character in comment).split())


def generated_comments(count: int, seed: int) -> "list[tuple[str, str]]":
    """Rare typed comments, each naming a made-up person (`RARE_COMMENTS`, `SHORT_COMMENTS`): (how it is written, the comment), every template with its sentence marks, with none, and with none and another space of the word screen's one definition between its words (`SPACES`, in turn)."""
    draw = random.Random(seed)
    found: "list[tuple[str, str]]" = []
    for template in RARE_COMMENTS + SHORT_COMMENTS:
        for place in range(count):
            given, last = made_up_name(draw)
            marked = template.format(g=given, f=last)
            plain = without_marks(marked)
            found += [("marked", marked), ("no mark", plain),
                      ("no mark, other spaces", plain.replace(" ", SPACES[1 + place % (len(SPACES) - 1)]))]
    return found


# NAMES AND PLACES OF TWO TO FOUR LETTERS BEFORE A CELL'S ONLY FULL STOP (lane
# NOTES's repair 2, the combined verify's major 2): `Seen with Ann. Plan
# reviewed` is a sentence -- the abbreviation's stop is no mark only where the
# abbreviation opens the cell.
SHORT_GIVEN = tuple(a + b for a in GIVEN_A for b in ("lo", "na", "ma")) + GIVEN_A[:6]
SHORT_PLACES = PLACE_A
SHORT_OPENINGS = ("Seen with", "Reviewed by", "Spoke to wife", "Lives with son", "Transferred from",
                  "Discussed with", "Called daughter", "Plan made with")
SHORT_AFTER = ("Plan agreed", "Plan reviewed", "Will call back", "Stable", "follow up", "Review in 2 weeks")


def short_names_before_the_only_stop() -> "tuple[str, ...]":
    """A made-up name or place of two to four letters, capitalised, right before the cell's only full stop, after an opening of words (`Seen with Malo. Plan agreed`)."""
    return tuple(f"{opening} {word}. {after}" for opening in SHORT_OPENINGS for word in SHORT_GIVEN + SHORT_PLACES
                 for after in SHORT_AFTER)


def opening_words_before_the_only_stop() -> "tuple[tuple[str, bool], ...]":
    """A word opening the cell right before its only full stop, two words or more after it: (cell, whether it is a sentence) -- a capitalised word of five letters or more, or one of small letters, is read; a capitalised word of two to four letters is an abbreviation and is not (`Malo. Plan agreed`, P4-D481 (c))."""
    found: "list[tuple[str, bool]]" = []
    longer = tuple(a + b for a in GIVEN_A for b in ("rin", "vik", "sel", "tor")) + ("Fever", "Settled", "Walking")
    short = SHORT_GIVEN + SHORT_PLACES + ("Seen", "Fell", "Pain")
    for after in SHORT_AFTER:
        if len(after.split()) < 2:
            continue
        found += [(f"{word}. {after}", True) for word in longer]
        found += [(f"{word.lower()}. {after}", True) for word in short]
        found += [(f"{word}. {after}", False) for word in short]
    return tuple(found)
# Two-part notes of a script written with no space, each naming a made-up
# clinician (`remark_c`): a neighbour the reading does not read (fewer than
# three words), recorded apart (P4-D481 (c)).
CJK_FAMILY = ("林", "陈", "吴", "孙", "郑")
CJK_GIVEN = ("明", "华")
CJK_FOUND = ("病情稳定", "继续观察", "明日复查")


def comment_rows(n: int, seed: int) -> "dict[int, str]":
    """The rows of `RARE_COMMENTS`, each comment on two rows: of one person (even comments) or of two."""
    placed: "dict[int, str]" = {}
    for place, template in enumerate(RARE_COMMENTS):
        given, last = made_up_name(random.Random(seed + 7001 + place))
        text = template.format(g=given, f=last)
        first = place * 1600 + 3
        for row in (first, first + (1 if place % 2 == 0 else 40)):
            if row < n:
                placed[row] = text
    return placed


def notes_table(n: int, seed: int, families: "tuple[str, ...]", person: bool = True) -> "tuple[list[str], list[list[str]]]":
    """A table of note columns, one person column of n // 20 people of 20 rows each where ``person``."""
    draw = random.Random(seed)
    commented = comment_rows(n, seed)
    people = max(n // 20, 1)
    subjects = [f"S{200000 + 7 * place}" for place in range(people)]
    clinicians = [made_up_name(random.Random(seed + 17 + place)) for place in range(40)]
    relatives = [made_up_name(random.Random(seed + 911 + place)) for place in range(people)]
    places = [made_up_place(random.Random(seed + 4243 + place)) for place in range(25)]
    pool = stock_pool()
    banks: "dict[int, list[str]]" = {}
    for size in (5, 20, 50, 216, 900):
        shuffled = list(pool)
        random.Random(seed + size).shuffle(shuffled)
        banks[size] = shuffled[:size]
    # ...the bank of five opens with a sentence of one word, its largest
    # group (lane NOTES's repair 2, the combined verify's minor 5): its shape
    # form is published and the twin owes it, a miss the free-text writer
    # makes on some tables (P4-D481 (b)), so K-HZ-34 reads the obligation.
    banks[5] = [ONE_WORD_SENTENCE] + banks[5][:4]
    weights = {size: [1.0 / (rank + 1) for rank in range(size)] for size in banks}
    codes3 = ["Nil by mouth", "Fluids only", "Normal diet"]
    codes30 = [f"{word} {kind}" for word in ("Soft", "Low", "High", "Thick", "Plain", "Mixed") for kind in ("A", "B", "C", "D", "E")]
    complaints = ["chest pain, breathless", "fever, cough", "belly pain", "fall, hip pain", "headache",
                  "sickness, loose stools", "back pain", "dizzy spells"]
    unique = 0

    def free_sentence(low: int, high: int) -> str:
        nonlocal unique
        unique += 1
        words = [draw.choice(("seen", "plan", "reviewed", "dressing", "walking", "settled", "tablets", "therapy",
                              "fluids", "pain", "sleep", "family", "visit", "results", "clinic"))
                 for _ in range(draw.randint(low, high))]
        return f"Note {unique}: " + " ".join(words) + "."

    header = (["subject_id"] if person else []) + list(families)
    rows: "list[list[str]]" = []
    for place in range(n):
        who = place // 20 if place // 20 < people else people - 1
        given, last = clinicians[who % 40]
        row = [subjects[who]] if person else []
        for family in families:
            plain = draw.choices(banks[20], weights[20])[0]
            if family.startswith("tpl"):
                size = int(family[3:])
                row += [draw.choices(banks[size], weights[size])[0]]
            elif family == "free":
                row += [free_sentence(5, 40)]
            elif family == "mix70":
                row += [draw.choices(banks[216], weights[216])[0] if draw.random() < 0.7 else free_sentence(5, 25)]
            elif family == "remark_n":
                row += [draw.choice(("Seen together with {g} {f}. Plan agreed.", "Spoke to {f} team.",
                                     "Case discussed with {g} {f}.")).format(g=given, f=last)
                        if draw.random() < 0.6 else plain]
            elif family == "remark_t":
                row += [f"Reviewed by Dr. {last}." if draw.random() < 0.6 else plain]
            elif family == "remark_d":
                row += [f"Next visit on {draw.randint(1, 12):02d}/{draw.choice((4, 11, 18, 25)):02d}."
                        if draw.random() < 0.6 else plain]
            elif family == "remark_f":
                row += [f"Weight {draw.randint(50, 110)} kg, steady." if draw.random() < 0.6 else plain]
            elif family == "remark_p":
                row += [f"Transferred from {draw.choice(places)} clinic." if draw.random() < 0.6 else plain]
            elif family == "remark_o":
                row += [f"Lives with daughter {relatives[who][0]} {relatives[who][1]}." if who < 100 else plain]
            elif family == "codes3":
                row += [draw.choices(codes3, (60, 25, 15))[0]]
            elif family == "codes30":
                row += [draw.choice(codes30)]
            elif family == "complaints":
                row += [draw.choices(complaints, [1.0 / (rank + 1) for rank in range(8)])[0]]
            elif family in ("result", "result_plain", "diet_note", "ward_note"):
                # ...a label column whose few rows carry a typed comment: codes
                # alone, 45 per cent stock sentences (no column of sentences) or
                # 60 per cent (a column of sentences, its sentences and labels
                # its own, so no other column publishes them), the rest short
                # labels; and codes beside the same comments typed with no
                # sentence mark (lane NOTES's repair 2).
                share = {"result": 0.0, "result_plain": 0.0, "diet_note": 0.45, "ward_note": 0.6}[family]
                labels = {"result": RESULT_CODES, "result_plain": RESULT_CODES, "diet_note": codes3,
                          "ward_note": WARD_LABELS}[family]
                sentence = f"{draw.choice(OPENINGS)}. Ward round done." if family == "ward_note" else plain
                chosen = sentence if draw.random() < share else draw.choice(labels)
                if place in commented:
                    chosen = without_marks(commented[place]) if family == "result_plain" else commented[place]
                row += [chosen]
            elif family == "remark_c":
                row += [f"{CJK_FAMILY[who % 5]}{CJK_GIVEN[who % 2]}医生查房。{draw.choice(CJK_FOUND)}。"]
            else:
                row += [""]
        rows += [row]
    return header, rows


# THE TABLES K-HZ-34 READS (`measure`), each 1,000 people of 20 rows at
# 20,000 rows: the stock banks, free text and the mix beside the control
# columns (codes and complaints, which must keep their levels), and the
# templates with one variable part beside the same controls, each under a
# NEUTRAL name (`remark_n`: a name; `_t` a title; `_d` a date; `_f` a
# figure; `_p` a place; `_o` a relative's own sentence): a column whose name
# says a place, a date or a name is held by its name first.
TABLE_FAMILIES = {
    "banks": ("tpl5", "tpl50", "tpl216", "tpl900", "free", "mix70", "codes3", "codes30", "complaints"),
    "templates": ("remark_n", "remark_t", "remark_d", "remark_f", "remark_p", "remark_o",
                  "codes3", "codes30", "complaints"),
    # ...and the neighbours (lane NOTES's repair 1): label columns whose few
    # rows carry a typed comment (`RARE_COMMENTS`; with no sentence mark in
    # `result_plain` since repair 2), answered `no` too, and the two-part
    # notes of a script written with no space (`remark_c`).
    "neighbours": ("result", "result_plain", "diet_note", "ward_note", "remark_c", "codes3", "codes30", "complaints"),
}
CONTROLS = ("codes3", "codes30", "complaints")
# The label columns of the neighbours, and the controls: their levels that 11
# people or more hold are published, as on the base; a value fewer hold is
# never shown or written (a comment named after `no` is skeptic 1's item 1,
# one typed with no mark the combined verify's new item 1).
LABEL_COLUMNS = ("result", "result_plain", "diet_note") + CONTROLS
# The neighbour the reading does not read, recorded apart and never failing.
NEIGHBOURS = ("remark_c",)
# THE MODES: nobody answering (the person question open); the person column
# said (`--identifier subject_id`); no person column at all (the table
# counted in rows); the person column said and every sentence question
# answered `text`; and answered `identifier`; and, for the neighbours, the
# person column said and every question offering `no` answered `no`.
MODES = ("unanswered", "person_said", "no_person", "text", "identifier")
TABLE_MODES = {"banks": MODES, "templates": MODES, "neighbours": ("unanswered", "person_said", "no")}
SEED = 20261112


def _folded(text: str) -> str:
    return " ".join(text.casefold().split())


def _leaves(node: object, out: "set[str]") -> None:
    """Every string of a decoded JSON document, folded: its keys and its values."""
    if isinstance(node, str):
        out.add(_folded(node))
    elif isinstance(node, dict):
        for key, value in node.items():
            out.add(_folded(f"{key}"))
            _leaves(value, out)
    elif isinstance(node, list):
        for value in node:
            _leaves(value, out)


def measure(folder: "object", table: str, mode: str, rows: int = 20_000) -> "dict[str, object]":
    """One table in one mode through the commands a person types (nobody at the keyboard, the table floor on): what each note column shows and writes.

    Counted by a counter linear in the data: each JSON file's decoded
    strings in a set, each text for the eye scanned once a different real
    value, each twin cell once against a set of the real values. EVERY
    DIFFERENT REAL VALUE of a note column is counted, whether the reading
    reads it as a sentence or not (lane NOTES's repair 1, the statistics
    check's item 5): of a label column of the neighbours, every value fewer
    than 11 people hold.
    """
    import contextlib
    import io
    import json
    import pathlib
    import time

    import health_zoo as zoo
    import unanswered_identifier_shapes as shapes
    from synthtwin import asking, cli, taxonomy

    here = pathlib.Path(f"{folder}")
    here.mkdir(parents=True, exist_ok=True)
    families = TABLE_FAMILIES[table]
    header, body = notes_table(rows, SEED, families, person=mode != "no_person")
    source = here / "notes.csv"
    source.write_bytes(zoo.csv_bytes(header, body))
    people: "dict[str, dict[str, set]]" = {}
    for place, name in enumerate(header):
        if name == "subject_id":
            continue
        held: "dict[str, set]" = {}
        for row in body:
            held.setdefault(row[place], set()).add(row[0] if mode != "no_person" else id(row))
        people[name] = held
    declared = ["--identifier", "subject_id"] if mode in ("person_said", "text", "identifier", "no") else []
    described, questions = here / "notes-profile.json", here / "notes-questions.json"
    screen = io.StringIO()
    seen: "dict[str, object]" = {"table": table, "mode": mode, "rows": rows}
    texts: "list[str]" = []
    leaves: "set[str]" = set()
    asked: "dict[str, list[str]]" = {}
    seconds = {"profile": 0.0, "generate": 0.0, "validate": 0.0}

    def read_round() -> None:
        for path in (described, questions):
            if path.is_file():
                _leaves(json.loads(path.read_text(encoding="utf-8")), leaves)
        summary = here / "notes-profile.txt"
        if summary.is_file():
            texts.append(_folded(summary.read_text(encoding="utf-8")))
        if questions.is_file():
            for entry in zoo._entries(json.loads(questions.read_text(encoding="utf-8"))):
                asked.setdefault(f"{entry.get('column', '')}", []).extend(zoo._offered(entry))

    with shapes.nobody_at_the_keyboard(), contextlib.redirect_stdout(screen), contextlib.redirect_stderr(screen):
        started = time.monotonic()
        seen["profile"] = cli.main(["profile", f"{source}", "--replace"] + declared, small_tables_refused=True)
        seconds["profile"] += time.monotonic() - started
        read_round()
        if seen["profile"] == 0 and mode in ("text", "identifier", "no"):
            asked_first = dict(asked)
            rounds = 0
            while rounds < 3:
                # ...`no` to every question offering it, round by round while a
                # new one is put (the neighbours); `text` or `identifier` to the
                # question of a column of sentences, once.
                document = json.loads(questions.read_text(encoding="utf-8"))
                before = json.dumps(document, sort_keys=True)
                for entry in zoo._entries(document):
                    offered = zoo._offered(entry)
                    if mode == "no" and "no" in offered:
                        entry["your_answer"] = "no"
                    elif mode != "no" and asking.ANSWER_TEXT in offered:
                        entry["your_answer"] = asking.ANSWER_TEXT if mode == "text" else asking.ANSWER_IDENTIFIER
                if json.dumps(document, sort_keys=True) == before:
                    break
                questions.write_text(json.dumps(document, indent=2), encoding="utf-8", newline="\n")
                started = time.monotonic()
                seen["answers"] = cli.main(["profile", f"{source}", "--replace", "--answers", f"{questions}"] + declared,
                                           small_tables_refused=True)
                seconds["profile"] += time.monotonic() - started
                rounds += 1
                asked.clear()
                read_round()
                if seen["answers"] != 0 or mode != "no":
                    break
            seen["rounds"] = rounds
            seen["asked_first"] = {name: sorted(set(offered)) for name, offered in asked_first.items()}
        if described.is_file() and seen["profile"] == 0 and seen.get("answers", 0) == 0:
            started = time.monotonic()
            seen["generate"] = cli.main(["generate", f"{described}", "--replace", "--seed", "0"], small_tables_refused=True)
            seconds["generate"] = time.monotonic() - started
            started = time.monotonic()
            seen["validate"] = cli.main(["validate", f"{described}", "--replace"], small_tables_refused=True)
            seconds["validate"] = time.monotonic() - started
    texts.append(_folded(screen.getvalue()))
    for name in ("notes-twin-report.txt", "notes-twin-quality.txt"):
        if (here / name).is_file():
            texts.append(_folded((here / name).read_text(encoding="utf-8")))
    twin: "dict[str, list[str]]" = {}
    if (here / "notes-twin.csv").is_file():
        import csv

        with open(here / "notes-twin.csv", encoding="utf-8", newline="") as handle:
            twin_rows = list(csv.reader(handle))
        twin = {name: [row[place] for row in twin_rows[1:]] for place, name in enumerate(twin_rows[0])}
    roles: "dict[str, str]" = {}
    moved: "dict[str, bool]" = {}
    levels: "dict[str, int]" = {}
    said = taxonomy.rendered(taxonomy.EVIDENCE_SENTENCES_AS_TEXT, ())
    if described.is_file():
        for block in json.loads(described.read_text(encoding="utf-8"))["columns"]:
            roles[f"{block['name']}"] = f"{block['role']}"
            moved[f"{block['name']}"] = block.get("detection_evidence") == said
            levels[f"{block['name']}"] = len(block.get("levels") or [])
    missed: "list[str]" = []
    quality = here / "notes-twin-quality.txt"
    if quality.is_file():
        # Each obligation the twin misses, under its column's name the report
        # writes on the line before it (`'column'`).
        column = ""
        for line in quality.read_text(encoding="utf-8").splitlines():
            bare = line.strip()
            if len(bare) > 2 and bare[0] == "'" and bare[-1] == "'":
                column = bare[1:-1]
            elif bare.endswith("MISSED") and "[" in bare:
                missed += [f"{column}: {bare}"]
    columns: "dict[str, dict[str, object]]" = {}
    for name, held in people.items():
        # EVERY DIFFERENT REAL VALUE (blank cells aside); of a label column of
        # the neighbours, those fewer than 11 people hold.
        counted = {cell for cell in held if cell.strip() and (name not in LABEL_COLUMNS or len(held[cell]) < 11)}
        shown: "list[str]" = []
        for cell in counted:
            folded = _folded(cell)
            if folded in leaves or any(folded in text for text in texts):
                shown += [cell]
        columns[name] = {
            "role": roles.get(name, ""),
            "moved": moved.get(name, False),
            "levels": levels.get(name, 0),
            "sentence_column": taxonomy.a_sentence_column([row[header.index(name)] for row in body]),
            "different": len(held),
            "counted": len(counted),
            "sentences_shown": len(shown),
            "sentences_shown_few_people": sum(1 for cell in shown if len(held[cell]) < 11),
            "twin_cells_real": sum(1 for cell in twin.get(name, []) if cell in counted),
            "asked": sorted(set(asked.get(name, []))),
        }
    seen["columns"] = columns
    seen["missed"] = missed
    seen["seconds"] = {key: round(value, 1) for key, value in seconds.items()}
    seen["product_seconds"] = round(sum(seconds.values()), 1)
    return seen
