"""Safe Harbor identifier forms the zoo did not test before (plan P4-D445): eight invented look-alikes.

Every table here is written from scratch by this module's own makers and
seeds, with generic column names; no value is copied from anywhere. Each
FORM is one kind of the catalogue (`KINDS`) and one table, several rows
a person, at the owner's table floor at the KPI size (20,000 rows, 1,000
people, 20 rows each) and as the suite's smoke below it (600 rows, 100
people):

1. `ssn_letters`: social security numbers in one column, dashed and
   undashed, a few spaced or written with an en dash, and about one in
   fifty carrying one trailing capital letter (`900-12-3456A`).
2. `member_numbers`: a payer's member number in many formats in one
   column: social-security-shaped about a fifth, plain nine figures
   about a fifth, nine figures and a letter a few, an eleven-character
   letters-and-figures form in the public beneficiary layout a few, and
   the rest letters and figures of 6 to 15 characters in ten layouts.
3. `name_and_record`: a person's name and record number in one cell,
   `Lastname, Firstname M [1234567]`, the names from the zoo's own name
   maker, a few written `Lastname,Firstname (1234567)`.
4. `relative_numbers`: a relative's identifier beside the patient's: a
   second and a third social-security-shaped column under neutral names.
5. `opaque_tokens`: opaque tokens, 32 and 64 hexadecimal characters in
   either case, 22 and 24 base64 characters.
6. `device_numbers`: device lot and serial numbers (`A12345`,
   `SN-0042-77`, ten figures) and GS1-style unique device identifiers
   whose application identifiers carry a serial `(21)` or a lot `(10)`.
7. `accession_and_units`: specimen accession numbers (a letter, a
   two-figure year and a sequence, in three layouts in one column) and
   blood-unit numbers in the ISBT 128 layout (a made-up facility code, a
   two-figure year, a six-figure sequence and two flag figures).
8. `long_ids`: identifiers of 16 and 19 figures, which a reader that
   takes them as numbers changes (a float keeps about 15 figures).

Beside each form stand ordinary columns of the same table -- a closed
list of codes of 6 to 15 characters among them (`plan_code`,
`test_code`, `kit_code`), so a rule that reads every such code as an
identifier is seen as the false alarm it is.

AND A VARIANT COLUMN BESIDE A FORM for each reading lane CZ-A's repair 1
added (skeptic 1 items 1 to 7, the orchestrator's LANE CZ-A RULINGS 1
(0)), drawn from a second stream of the table's seed so the form's own
columns keep their bytes: `member_ref`, social security numbers written
with another dash or space and a letter of either case after a few;
`access_key`, base64 keys of 24 characters with no padding and of 43 or
44; `chart_label`, a name beside a labelled record number (`[REC
1234567]`, `(REC: 1234567)`, `#1234567`, `Lastname Jr.`, `de la
Lastname`); `implant_ref`, UDIs whose application identifiers stand in
square brackets; `specimen_ref`, accession numbers in the letters-first
and the year-first layouts with no dash; `unit_ref`, unit numbers with
their check character, or with `=` before them; `case_number`, numbers
of 12 to 18 figures, about half of 16 or more. AND FOUR CLOSED LISTS the
rule reaches or spares (the orchestrator's LANE CZ-A RULINGS 1 (2), the
statistics skeptic's item 2): `procedure_label`, labels with a code of
five figures in brackets (spared: a record number has six figures at
least); `catalogue_code`, codes of three capitals, two figures, a dash
and four figures (held as accession numbers); `item_code`, codes of 32
small hexadecimal characters (held as tokens); `concept_code`, codes of
16 to 18 figures (held as long numbers) -- the price, held until the
person answers `no`.

AND A VARIANT COLUMN for each reading lane CZ-A's repair 2 added (Codex's
items 1 and 2 and the verify's items 1 to 5, the orchestrator's LANE CZ-A
RULINGS 2 and 3), drawn from a third stream so no column above moves a
byte: `session_ref`, UUIDs in small letters, capitals or braces;
`band_label`, a name with a sole initial and its point, or a family name
with a curly apostrophe, beside a record number; `block_ref`, accession
numbers the year first with its dash, `24S-100000` upward (Codex's
table); `slide_ref`, accession numbers with a dash between their capitals
and their year; `sn`, a device's serial number under its short name. And
the long identifiers written as a workbook of NUMBER cells, each in a
float's own spelling, the exponent form among them (`as_a_spreadsheet_
stores`; K-HZ-14's `long_ids_numbers`). The tokens' form writes its 64
hexadecimal characters in capitals too (Codex item 6).
"""

from __future__ import annotations

import contextlib
import csv
import io
import json
import pathlib
import random
import time

import health_zoo as zoo

SEED = 20261104
# The people of a form's table: its rows divided by `ROWS_A_PERSON`, and
# never fewer than `SMOKE_PEOPLE` -- so the KPI size holds the owner's
# floor of 1,000 people, each on 20 rows, which puts an identifier's
# 1,000 different values inside the reach of a set of categories (at most
# 1,000 levels at 20,000 rows), and the smoke 100 (the zoo's smoke wants
# 100). A maker's `people` draws another density.
ROWS_A_PERSON = 20
SMOKE_PEOPLE = 100

KIND_SSN = "ssn_letters"
KIND_MEMBER = "member_numbers"
KIND_NAME_RECORD = "name_and_record"
KIND_RELATIVE = "relative_numbers"
KIND_TOKENS = "opaque_tokens"
KIND_DEVICES = "device_numbers"
KIND_ACCESSION = "accession_and_units"
KIND_LONG = "long_ids"
KINDS = (
    KIND_SSN, KIND_MEMBER, KIND_NAME_RECORD, KIND_RELATIVE, KIND_TOKENS, KIND_DEVICES, KIND_ACCESSION, KIND_LONG,
)
# A DRIVER'S FORM, NOT THE CATALOGUE'S (Codex's review of batch 4q, item 1):
# a name beside a record number of its own on every row, the numbers
# running on from one another, as Codex's table had them. K-HZ-14 runs it
# beside the forms (`DRIVER_KINDS`); the zoo's catalogue does not hold it.
KIND_NAME_ROWS = "name_and_record_rows"
DRIVER_KINDS = KINDS + (KIND_NAME_ROWS,)

# The ordinary columns beside every form: a visit's kind and a charge.
VISIT_KINDS = (("Office", 50.0), ("Telehealth", 20.0), ("Urgent", 20.0), ("Inpatient", 10.0))
# Closed lists of codes of 6 to 15 characters, letters and figures: a
# payer's plan codes, a laboratory's test codes, a supplier's kit codes.
PLAN_CODES = zoo._zipf(("HMOBASIC", "PPOPLUS01", "EPOSTD", "HMOSENIOR2", "PPOGOLD", "MEDSUPPA", "HDHPSAVE15"))
TEST_CODES = zoo._zipf(("CBCDIFF", "BMP8PANEL", "LIPIDFULL", "TSHREFLEX", "CHEM14X", "UACULTURE", "PTINR002"))
KIT_CODES = zoo._zipf(("KIT2040A", "TRAYSTD10", "SETCVC07", "PACKORTHO3"))
# The letters a payer's beneficiary layout uses (the public layout drops
# S, L, O, I, B and Z, which read as figures).
BENEFICIARY_LETTERS = "ACDEFGHJKMNPQRTUVWXY"
# The other dashes and spaces a social security number may be written
# with: a hyphen, a non-breaking hyphen, a figure dash, a minus sign, a
# small and a full-width hyphen-minus, a non-breaking and a narrow
# non-breaking space.
ODD_MARKS = ("\u2010", "\u2011", "\u2012", "\u2212", "\ufe63", "\uff0d", "\u00a0", "\u202f")
# The second stream a table's variant columns and closed lists are drawn
# from: the table's seed and this step.
VARIANT_SEED_STEP = 104729
CAPITALS = "ABCDEFGHJKLMNPQRSTUVWXYZ"
HEX = "0123456789abcdef"
BASE64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"


def _people(n: int, people: "int | None" = None) -> int:
    return people if people else max(n // ROWS_A_PERSON, SMOKE_PEOPLE)


def _second(seed: int) -> random.Random:
    """The stream a table's variant columns and closed lists draw from, apart from its own columns'."""
    return random.Random(seed + VARIANT_SEED_STEP)


def _third(seed: int) -> random.Random:
    """The stream repair 2's variant columns draw from, apart from the form's and repair 1's, so neither moves a byte."""
    return random.Random(seed + 2 * VARIANT_SEED_STEP)


def _code_list(make: "object", count: int, seed: int) -> "tuple[tuple[str, float], ...]":
    """A closed list of ``count`` different codes of one maker, drawn at its own seed, weighted as the zoo weighs."""
    return zoo._zipf(tuple(_distinct(random.Random(seed), count, make)))


def patient_ref(person: int) -> str:
    """The table's own patient key, the column that names the people the rows are about."""
    return f"P{1000000 + person:07d}"


def _figures(draw: random.Random, count: int, first_nought: bool = True) -> str:
    written = f"{draw.randint(0 if first_nought else 1, 9)}"
    for _place in range(count - 1):
        written += f"{draw.randint(0, 9)}"
    return written


def _letters(draw: random.Random, count: int, alphabet: str = CAPITALS) -> str:
    written = ""
    for _place in range(count):
        written += alphabet[draw.randrange(len(alphabet))]
    return written


def social_number(draw: random.Random) -> "tuple[str, str, str]":
    """A made-up social-security-shaped number's three parts, in the 900 area that is never issued."""
    return f"9{draw.randint(0, 99):02d}", f"{draw.randint(1, 99):02d}", f"{draw.randint(1, 9999):04d}"


def ssn_written(parts: "tuple[str, str, str]", form: str, letter: str = "") -> str:
    """One social security number in one of the forms an export writes."""
    area, group, serial = parts
    joined = {"dashed": "-", "plain": "", "spaced": " ", "en dash": "–"}[form]
    return f"{area}{joined}{group}{joined}{serial}{letter}"


def _distinct(draw: random.Random, count: int, make: "object") -> "list[str]":
    """`count` different values of one maker, in the order they were drawn."""
    seen: "dict[str, bool]" = {}
    while len(seen) < count:
        value = make(draw)  # type: ignore[operator]
        if value not in seen:
            seen[value] = True
    return list(seen)


def _person_rows(n: int, draw: random.Random, people: int) -> "list[int]":
    """The person each row is about: every person on one row at least, the rows dealt evenly and shuffled."""
    order = [place % people for place in range(n)]
    draw.shuffle(order)
    return order


def _ordinary(draw: random.Random) -> "list[str]":
    return [zoo._pick(draw, VISIT_KINDS), f"{draw.lognormvariate(5.0, 0.8):.2f}"]


def ssn_odd_marks(draw: random.Random) -> str:
    """A social security number written with another dash or space (`ODD_MARKS`), one in fifty with a letter of either case after it, a space before it or none."""
    area, group, serial = social_number(draw)
    mark = draw.choice(ODD_MARKS)
    letter = ""
    if draw.random() < 0.02:
        letter = draw.choice(("", " ")) + draw.choice(CAPITALS + CAPITALS.lower())
    return f"{area}{mark}{group}{mark}{serial}{letter}"


def ssn_letters(n: int, seed: int, people: "int | None" = None) -> "tuple[list[str], list[list[str]]]":
    """Social security numbers, dashed and undashed in one column, a few spaced or en-dashed, one in fifty lettered.

    And beside them `member_ref`, another number of each person written
    with another dash or space (`ssn_odd_marks`).
    """
    draw = random.Random(seed)
    count = _people(n, people)
    numbers = _distinct(draw, count, social_number)
    forms: "list[tuple[str, str]]" = []
    for _person in numbers:
        roll = draw.random()
        form = "dashed" if roll < 0.48 else ("plain" if roll < 0.94 else ("spaced" if roll < 0.97 else "en dash"))
        letter = draw.choice(CAPITALS) if draw.random() < 0.02 else ""
        forms += [(form, letter)]
    odd = _distinct(_second(seed), count, ssn_odd_marks)
    header = ["patient_ref", "ssn", "visit_kind", "charge", "member_ref"]
    rows: "list[list[str]]" = []
    for person in _person_rows(n, draw, count):
        form, letter = forms[person]
        rows += [
            [patient_ref(person), ssn_written(numbers[person], form, letter)] + _ordinary(draw)  # type: ignore[arg-type]
            + [odd[person]]
        ]
    return header, rows


def beneficiary_number(draw: random.Random) -> str:
    """Eleven characters in the public beneficiary layout: figure, letter, either, figure, letter, either, figure, two letters, two figures."""
    written = ""
    for place in "9AX9AX9AA99":
        if place == "9":
            written += f"{draw.randint(1 if not written else 0, 9)}"
        elif place == "A" or draw.random() < 0.5:
            written += BENEFICIARY_LETTERS[draw.randrange(len(BENEFICIARY_LETTERS))]
        else:
            written += f"{draw.randint(0, 9)}"
    return written


# The member number's other layouts, letters and figures of 6 to 15
# characters, each a function of the draw.
MEMBER_LAYOUTS = (
    lambda d: _letters(d, 3) + _figures(d, 9),
    lambda d: _letters(d, 1) + _figures(d, 8),
    lambda d: _figures(d, 9, False) + "0" + _figures(d, 1),
    lambda d: _letters(d, 2) + _figures(d, 6),
    lambda d: "M" + _figures(d, 7) + "-" + _figures(d, 2),
    lambda d: _letters(d, 4) + _figures(d, 11),
    lambda d: _figures(d, 6, False),
    lambda d: _letters(d, 1) + _figures(d, 4) + _letters(d, 1) + _figures(d, 4),
    lambda d: _figures(d, 3, False) + _letters(d, 2) + _figures(d, 5),
    lambda d: _letters(d, 2) + _figures(d, 2) + _letters(d, 2) + _figures(d, 4) + _letters(d, 1),
)


def member_number(draw: random.Random, letters: float = 0.55) -> str:
    """One payer's member number, its format drawn: more than ten formats in one column.

    Social-security-shaped about a fifth, plain nine figures about a fifth,
    nine figures and a letter a few, the beneficiary layout a few, and the
    rest (``letters``, about a half) in the ten other layouts of letters
    and figures; a smaller ``letters`` gives the plain nine figures what
    it takes away.
    """
    roll = draw.random()
    if roll < 0.20:
        return ssn_written(social_number(draw), "dashed")
    if roll < 0.40 + (0.55 - letters):
        return _figures(draw, 9, False)
    if roll < 0.42 + (0.55 - letters):
        return _figures(draw, 9, False) + draw.choice(CAPITALS)
    if roll < 0.45 + (0.55 - letters):
        return beneficiary_number(draw)
    return MEMBER_LAYOUTS[draw.randrange(len(MEMBER_LAYOUTS))](draw)  # type: ignore[no-untyped-call]


def member_numbers(
    n: int, seed: int, people: "int | None" = None, letters: float = 0.55,
) -> "tuple[list[str], list[list[str]]]":
    """A payer's member number in more than ten formats in one column, beside its plan's code."""
    draw = random.Random(seed)
    count = _people(n, people)
    numbers = _distinct(draw, count, lambda d: member_number(d, letters))
    header = ["patient_ref", "member_id", "plan_code", "visit_kind", "charge"]
    rows: "list[list[str]]" = []
    for person in _person_rows(n, draw, count):
        rows += [[patient_ref(person), numbers[person], zoo._pick(draw, PLAN_CODES)] + _ordinary(draw)]
    return header, rows


def _name(draw: random.Random) -> "tuple[str, str, str]":
    """A made-up name from the zoo's own name maker (`health_zoo_wide`'s first and last names), and an initial."""
    import health_zoo_wide as wide

    first = draw.choice(wide.FIRST_NAMES)
    last = draw.choice(wide.LAST_NAMES)
    return last, first, draw.choice(CAPITALS)


# The small words a family name may open with, and the words after it.
PARTICLES = ("de la", "van der", "da", "del", "von")
SUFFIXES = ("Jr.", "Sr.")


def chart_label(draw: random.Random, record: str) -> str:
    """A name beside a labelled record number: `[REC 1234567]`, `(REC: 1234567)`, `#1234567`, a `Jr.` or a `de la`."""
    last, first, middle = _name(draw)
    roll = draw.random()
    if roll < 0.3:
        return f"{last}, {first} {middle} [REC {record}]"
    if roll < 0.5:
        return f"{last}, {first} {middle} (REC: {record})"
    if roll < 0.7:
        return f"{last}, {first} {middle} #{record}"
    if roll < 0.85:
        return f"{last} {draw.choice(SUFFIXES)}, {first} [{record}]"
    return f"{draw.choice(PARTICLES)} {last}, {first} [{record}]"


def procedure_label(draw: random.Random) -> str:
    """A procedure's label with its code of five figures in brackets, its words and code made up: `Repair, Open (41234)`."""
    words = ("Repair", "Excision", "Drainage", "Revision", "Insertion", "Removal", "Closure")
    ways = ("Open", "Endoscopic", "Partial", "Complete", "Percutaneous")
    opening, closing = draw.choice((("(", ")"), ("[", "]")))
    return f"{draw.choice(words)}, {draw.choice(ways)} {opening}{_figures(draw, 5, False)}{closing}"


PROCEDURE_LABELS = _code_list(procedure_label, 25, SEED + 1)
# The curly apostrophe a word processor writes in a family name.
CURLY_APOSTROPHE = "\u2019"


def band_label(draw: random.Random, record: str) -> str:
    """A name beside a record number with a sole initial and its point, `Lastname, F. [2000000]`, or a family name with a curly apostrophe."""
    last, first, middle = _name(draw)
    if draw.random() < 0.5:
        return f"{last}, {middle}. [{record}]"
    return f"O{CURLY_APOSTROPHE}{last}, {first} [{record}]"


def name_and_record(n: int, seed: int, people: "int | None" = None) -> "tuple[list[str], list[list[str]]]":
    """A name and a record number in one cell, `Lastname, Firstname M [1234567]`, a few `Lastname,Firstname (1234567)`.

    And beside them `chart_label`, each person's name beside a labelled
    record number (`chart_label`), and `procedure_label`, a closed list of
    labels with a code of five figures in brackets. AND (repair 2)
    `band_label`, each person's name with a sole initial and its point or
    a family name with a curly apostrophe beside a record number from
    2000000 up (`band_label`, Codex item 2's two spellings).
    """
    draw = random.Random(seed)
    count = _people(n, people)
    records = [f"{record}" for record in draw.sample(range(1000000, 9999999), count)]
    labels: "list[str]" = []
    for record in records:
        last, first, middle = _name(draw)
        if draw.random() < 0.05:
            labels += [f"{last},{first} ({record})"]
        else:
            labels += [f"{last}, {first} {middle} [{record}]"]
    # ...the labelled record numbers drawn from 2000000 up, so none shares its
    # figures with the patient key (`P1000000` up), which the coded mode
    # publishes as the person's answer `keep` reads it: a record number equal
    # to a published key's figures is no value of the label published, and
    # the linear counter would read it as one (K-HZ-14 at 686b6ac: one record,
    # `1000436`, beside the key `P1000436`).
    extra = _second(seed)
    charts = [chart_label(extra, f"{record}") for record in extra.sample(range(2000000, 9999999), count)]
    third = _third(seed)
    bands = [band_label(third, f"{record}") for record in third.sample(range(2000000, 9999999), count)]
    header = [
        "patient_ref", "patient_label", "kit_code", "visit_kind", "charge", "chart_label", "procedure_label",
        "band_label",
    ]
    rows: "list[list[str]]" = []
    for person in _person_rows(n, draw, count):
        rows += [
            [patient_ref(person), labels[person], zoo._pick(draw, KIT_CODES)] + _ordinary(draw)
            + [charts[person], zoo._pick(extra, PROCEDURE_LABELS), bands[person]]
        ]
    return header, rows


# The first record number of `name_and_record_rows`: past the patient keys'
# figures (`P1000000` up), which the coded mode publishes.
ROW_RECORDS_FROM = 3000000


def given_of(person: int) -> str:
    """A made-up given name of three letters, one a person: `Aaa`, `Aab`, ... (Codex's table)."""
    return chr(65 + person // 676) + chr(97 + (person // 26) % 26) + chr(97 + person % 26)


def name_and_record_rows(n: int, seed: int, people: "int | None" = None) -> "tuple[list[str], list[list[str]]]":
    """A name and a record number of its own on every row, `Cedar, Aaa [3000000]`, the numbers running on (Codex's table).

    Codex's review of batch 4q, item 1: 1,000 people of 20 records each at
    20,000 rows, every row its own record number, the person's twenty in a
    run, so a twin drawing any seven figures meets a real one by chance;
    beside the patient key, a visit's kind and a charge. The numbers do not
    read the seed: the rows are the table's, the seed draws the rest.
    """
    draw = random.Random(seed)
    count = _people(n, people)
    header = ["patient_ref", "visit_label", "visit_kind", "charge"]
    rows: "list[list[str]]" = []
    for row in range(n):
        person = row * count // n
        rows += [
            [patient_ref(person), f"Cedar, {given_of(person)} [{ROW_RECORDS_FROM + row}]"] + _ordinary(draw)
        ]
    return header, rows


def relative_numbers(n: int, seed: int, people: "int | None" = None) -> "tuple[list[str], list[list[str]]]":
    """A patient's social security number, and a partner's and a guardian's beside it under neutral names."""
    draw = random.Random(seed)
    count = _people(n, people)
    numbers = _distinct(draw, 3 * count, lambda d: ssn_written(social_number(d), "dashed"))
    patients, partners, guardians = numbers[:count], numbers[count:2 * count], numbers[2 * count:]
    # ...a guardian's number undashed, as another part of the same export wrote it.
    guardians = [number.replace("-", "") for number in guardians]
    header = ["patient_ref", "ssn", "partner_ssn", "guardian_id", "visit_kind", "charge"]
    rows: "list[list[str]]" = []
    for person in _person_rows(n, draw, count):
        partner = partners[person] if person % 3 else ""
        guardian = guardians[person] if person % 4 == 0 else ""
        rows += [[patient_ref(person), patients[person], partner, guardian] + _ordinary(draw)]
    return header, rows


def token(draw: random.Random) -> str:
    """An opaque token: 32 or 64 hexadecimal characters in either case, or 22 base64 characters, padded or not.

    The 64 in capitals too (lane CZ-A's repair 2, Codex item 6: the maker
    wrote them in small letters alone, so no seed tried the capitals the
    form names); each branch draws as many figures as before, so only the
    case of those tokens moved.
    """
    roll = draw.random()
    if roll < 0.3:
        return _letters(draw, 32, HEX)
    if roll < 0.45:
        return _letters(draw, 32, HEX).upper()
    if roll < 0.6:
        return _letters(draw, 64, HEX)
    if roll < 0.7:
        return _letters(draw, 64, HEX).upper()
    if roll < 0.85:
        return _letters(draw, 22, BASE64)
    return _letters(draw, 22, BASE64) + "=="


def key_token(draw: random.Random) -> str:
    """A key in base64: 24 characters with no padding (eighteen bytes), or a key of 32 bytes, 43 characters or 44 with its `=`."""
    roll = draw.random()
    if roll < 0.5:
        return _letters(draw, 24, BASE64)
    if roll < 0.75:
        return _letters(draw, 43, BASE64)
    return _letters(draw, 43, BASE64) + "="


ITEM_CODES = _code_list(lambda d: _letters(d, 32, HEX), 50, SEED + 2)


def uuid(draw: random.Random) -> str:
    """A made-up UUID: 32 small hexadecimal characters in five groups of 8, 4, 4, 4 and 12 joined by dashes."""
    groups = [_letters(draw, count, HEX) for count in (8, 4, 4, 4, 12)]
    return "-".join(groups)


def session_token(draw: random.Random) -> str:
    """A UUID as systems write it: small letters about half, capitals a quarter, in braces a quarter."""
    value = uuid(draw)
    roll = draw.random()
    if roll < 0.5:
        return value
    if roll < 0.75:
        return value.upper()
    return f"{{{value}}}"


def opaque_tokens(n: int, seed: int, people: "int | None" = None) -> "tuple[list[str], list[list[str]]]":
    """A record token a system issues, opaque: hexadecimal and base64 of several lengths in one column.

    And beside it `access_key`, base64 keys of 24, 43 and 44 characters
    (`key_token`), and `item_code`, a closed list of codes of 32 small
    hexadecimal characters. AND (repair 2) `session_ref`, UUIDs in small
    letters, capitals or braces (`session_token`, the verify's item 1).
    """
    draw = random.Random(seed)
    count = _people(n, people)
    tokens = _distinct(draw, count, token)
    extra = _second(seed)
    keys = _distinct(extra, count, key_token)
    sessions = _distinct(_third(seed), count, session_token)
    header = [
        "patient_ref", "record_token", "test_code", "visit_kind", "charge", "access_key", "item_code", "session_ref",
    ]
    rows: "list[list[str]]" = []
    for person in _person_rows(n, draw, count):
        rows += [
            [patient_ref(person), tokens[person], zoo._pick(draw, TEST_CODES)] + _ordinary(draw)
            + [keys[person], zoo._pick(extra, ITEM_CODES), sessions[person]]
        ]
    return header, rows


def device_lot(draw: random.Random) -> str:
    """A manufacturing lot: a letter and five figures, two figures, two letters and four, or `LOT` and six."""
    roll = draw.random()
    if roll < 0.5:
        return _letters(draw, 1) + _figures(draw, 5)
    if roll < 0.8:
        return _figures(draw, 2, False) + _letters(draw, 2) + _figures(draw, 4)
    return "LOT" + _figures(draw, 6)


def device_serial(draw: random.Random) -> str:
    """A device's serial number: `SN-` and four and two figures, ten figures, or two letters and eight figures."""
    roll = draw.random()
    if roll < 0.4:
        return "SN-" + _figures(draw, 4) + "-" + _figures(draw, 2)
    if roll < 0.75:
        return _figures(draw, 10, False)
    return _letters(draw, 2) + _figures(draw, 8)


def device_udi(draw: random.Random, serial: str, lot: str) -> str:
    """A GS1-style unique device identifier carrying a serial (21) or a lot (10), its device number made up."""
    device = f"0{_figures(draw, 13)}"
    expiry = f"{draw.randint(26, 29)}{draw.randint(1, 12):02d}{draw.randint(1, 28):02d}"
    roll = draw.random()
    if roll < 0.4:
        return f"(01){device}(17){expiry}(21){serial}"
    if roll < 0.7:
        return f"(01){device}(10){lot}(21){serial}"
    if roll < 0.85:
        return f"(01){device}(11){expiry}(10){lot}"
    return f"(01) {device} (21) {serial}"


def bracket_udi(draw: random.Random, serial: str) -> str:
    """A GS1-style UDI whose application identifiers stand in square brackets: `[01]`, an expiry `[17]`, a serial `[21]`."""
    device = f"0{_figures(draw, 13)}"
    expiry = f"{draw.randint(26, 29)}{draw.randint(1, 12):02d}{draw.randint(1, 28):02d}"
    return f"[01]{device}[17]{expiry}[21]{serial}"


# The lots a log's devices come from: a lot holds many devices.
LOTS = 40


def device_numbers(n: int, seed: int, people: "int | None" = None) -> "tuple[list[str], list[list[str]]]":
    """An implant log: a device's lot and serial numbers in their own columns and in a UDI, beside its kit code.

    And beside them `implant_ref`, UDIs whose application identifiers
    stand in square brackets, and (repair 2) `sn`, another device's serial
    number under its short name (`device_serial`, the verify's item 5).
    """
    draw = random.Random(seed)
    count = _people(n, people)
    serials = _distinct(draw, count, device_serial)
    lot_list = _distinct(draw, LOTS, device_lot)
    lots = [lot_list[draw.randrange(LOTS)] for _place in range(count)]
    udis = [device_udi(draw, serial.replace("-", ""), lot) for serial, lot in zip(serials, lots)]
    extra = _second(seed)
    implants = _distinct(extra, count, lambda d: bracket_udi(d, _letters(d, 2) + _figures(d, 6)))
    shorts = _distinct(_third(seed), count, device_serial)
    header = [
        "patient_ref", "device_lot", "device_serial", "device_udi", "kit_code", "visit_kind", "charge", "implant_ref",
        "sn",
    ]
    rows: "list[list[str]]" = []
    for person in _person_rows(n, draw, count):
        rows += [
            [patient_ref(person), lots[person], serials[person], udis[person], zoo._pick(draw, KIT_CODES)]
            + _ordinary(draw) + [implants[person], shorts[person]]
        ]
    return header, rows


def accession(draw: random.Random) -> str:
    """A specimen accession number: a letter, a two-figure year and a sequence, in three layouts."""
    letter = draw.choice("SHCMB")
    year = f"{draw.randint(19, 26)}"
    sequence = _figures(draw, 6)
    roll = draw.random()
    if roll < 0.6:
        return f"{letter}{year}-{sequence}"
    if roll < 0.85:
        return f"{letter}{year}{sequence}"
    return f"{year}{letter}{sequence.lstrip('0') or '0'}"


# A made-up facility code: a letter and four figures, this module's own.
FACILITY = "Q4012"


def blood_unit(draw: random.Random) -> str:
    """A blood-unit number in the ISBT 128 layout: facility, two-figure year, six-figure sequence, two flag figures."""
    year = f"{draw.randint(22, 26)}"
    sequence = _figures(draw, 6)
    flags = f"{draw.choice((0, 0, 0, 1, 2))}{draw.randint(0, 9)}"
    if draw.random() < 0.7:
        return f"{FACILITY} {year} {sequence} {flags}"
    return f"{FACILITY}{year}{sequence}{flags}"


def accession_undashed(draw: random.Random) -> str:
    """An accession number with no dash: letters first (`S24012345`) about three in five, else the year first (`24S12345`)."""
    letter = draw.choice("SHCMB")
    year = f"{draw.randint(19, 26)}"
    sequence = _figures(draw, 6)
    if draw.random() < 0.6:
        return f"{letter}{year}{sequence}"
    return f"{year}{letter}{sequence.lstrip('0') or '0'}"


# The check character an ISBT 128 unit number may end with: a figure, a
# capital or a star.
UNIT_CHECK = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ*"


def unit_checked(draw: random.Random) -> str:
    """A blood-unit number with its check character, spaced or bare, after its flags or not, or bare with `=` before it."""
    year = f"{draw.randint(22, 26)}"
    sequence = _figures(draw, 6)
    flags = f"{draw.choice((0, 0, 0, 1, 2))}{draw.randint(0, 9)}"
    check = draw.choice(UNIT_CHECK)
    roll = draw.random()
    if roll < 0.5:
        return f"{FACILITY} {year} {sequence} {check}"
    if roll < 0.7:
        return f"{FACILITY}{year}{sequence}{check}"
    if roll < 0.85:
        return f"{FACILITY} {year} {sequence} {flags} {check}"
    return f"={FACILITY}{year}{sequence}{flags}"


CATALOGUE_CODES = _code_list(lambda d: _letters(d, 3) + _figures(d, 2) + "-" + _figures(d, 4), 30, SEED + 3)


def year_first_block(person: int, seed: int = SEED) -> str:
    """An accession number the year first with its dash, a capital and a sequence counted up: `24S-100000` upward.

    At the form's seed the sequence counts up from 100000 (Codex's table);
    at a control's seed (`CONTROL_SEED_STEP` steps away) from a thousand
    further for each step, so a control table's values are other values
    and the chance of a figure run has a control to read (K-HZ-14 at
    `e8e33cb` read the column's controls as the real values themselves).
    """
    step = ((seed - SEED) // CONTROL_SEED_STEP) % 899 if seed != SEED else 0
    return f"24S-{100000 + step * 1000 + person}"


def accession_dashed_twice(draw: random.Random) -> str:
    """An accession number with a dash between its capitals and its year: `S-24-012345`, `SP-24-012345`, `24-S-012345`."""
    letters = draw.choice(("S", "SP", "CY", "H", "CYT"))
    year = f"{draw.randint(19, 26)}"
    sequence = _figures(draw, 6)
    if draw.random() < 0.75:
        return f"{letters}-{year}-{sequence}"
    return f"{year}-{letters}-{sequence}"


def accession_and_units(n: int, seed: int, people: "int | None" = None) -> "tuple[list[str], list[list[str]]]":
    """A transfusion and specimen log: accession numbers in three layouts, ISBT 128 unit numbers, a test code.

    And beside them `specimen_ref`, accession numbers with no dash in two
    layouts (`accession_undashed`), `unit_ref`, unit numbers with their
    check character (`unit_checked`), and `catalogue_code`, a closed list
    of codes of three capitals, two figures, a dash and four figures. AND
    (repair 2) `block_ref`, accession numbers the year first with its dash
    and a sequence counted up, `24S-100000` upward (Codex item 1's table),
    and `slide_ref`, accession numbers with a dash between their capitals
    and their year (`accession_dashed_twice`, the verify's item 4).
    """
    draw = random.Random(seed)
    count = _people(n, people)
    accessions = _distinct(draw, count, accession)
    units = _distinct(draw, count, blood_unit)
    extra = _second(seed)
    specimens = _distinct(extra, count, accession_undashed)
    checked = _distinct(extra, count, unit_checked)
    slides = _distinct(_third(seed), count, accession_dashed_twice)
    header = [
        "patient_ref", "specimen_accession", "blood_unit", "test_code", "visit_kind", "charge",
        "specimen_ref", "unit_ref", "catalogue_code", "block_ref", "slide_ref",
    ]
    rows: "list[list[str]]" = []
    for person in _person_rows(n, draw, count):
        rows += [
            [patient_ref(person), accessions[person], units[person], zoo._pick(draw, TEST_CODES)] + _ordinary(draw)
            + [specimens[person], checked[person], zoo._pick(extra, CATALOGUE_CODES), year_first_block(person, seed),
               slides[person]]
        ]
    return header, rows


CONCEPT_CODES = _code_list(lambda d: _figures(d, d.choice((16, 17, 18)), False), 40, SEED + 4)


def long_ids(n: int, seed: int, people: "int | None" = None) -> "tuple[list[str], list[list[str]]]":
    """Identifiers of 16 and 19 figures, which a reader taking them as numbers changes.

    And beside them `case_number`, numbers of 12, 13, 14, 16, 17 and 18
    figures in one column, about half of 16 or more, and `concept_code`,
    a closed list of codes of 16 to 18 figures.
    """
    draw = random.Random(seed)
    count = _people(n, people)
    sixteen = _distinct(draw, count, lambda d: _figures(d, 16, False))
    nineteen = _distinct(draw, count, lambda d: "8" + _figures(d, 18))
    extra = _second(seed)
    cases = _distinct(extra, count, lambda d: _figures(d, d.choice((12, 13, 14, 16, 17, 18)), False))
    header = ["patient_ref", "claim_number", "order_number", "visit_kind", "charge", "case_number", "concept_code"]
    rows: "list[list[str]]" = []
    for person in _person_rows(n, draw, count):
        rows += [
            [patient_ref(person), sixteen[person], nineteen[person]] + _ordinary(draw)
            + [cases[person], zoo._pick(extra, CONCEPT_CODES)]
        ]
    return header, rows


MAKERS = {
    KIND_SSN: ssn_letters,
    KIND_MEMBER: member_numbers,
    KIND_NAME_RECORD: name_and_record,
    KIND_RELATIVE: relative_numbers,
    KIND_TOKENS: opaque_tokens,
    KIND_DEVICES: device_numbers,
    KIND_ACCESSION: accession_and_units,
    KIND_LONG: long_ids,
    KIND_NAME_ROWS: name_and_record_rows,
}
# The columns of each form that hold a Safe Harbor identifier.
IDENTIFIERS = {
    KIND_SSN: ("ssn", "member_ref"),
    KIND_MEMBER: ("member_id",),
    KIND_NAME_RECORD: ("patient_label", "chart_label", "band_label"),
    KIND_RELATIVE: ("ssn", "partner_ssn", "guardian_id"),
    KIND_TOKENS: ("record_token", "access_key", "session_ref"),
    KIND_DEVICES: ("device_lot", "device_serial", "device_udi", "implant_ref", "sn"),
    KIND_ACCESSION: ("specimen_accession", "blood_unit", "specimen_ref", "unit_ref", "block_ref", "slide_ref"),
    KIND_LONG: ("claim_number", "order_number", "case_number"),
    KIND_NAME_ROWS: ("visit_label",),
}
# The closed lists of codes beside them: the first of each kind stay codes
# (no rule reaches them); `procedure_label` stays a label (its codes have
# five figures); `catalogue_code`, `item_code` and `concept_code` are the
# price, held until `no` (`HELD_UNTIL_NO`).
CODES_BESIDE = {
    KIND_MEMBER: ("plan_code",),
    KIND_NAME_RECORD: ("kit_code", "procedure_label"),
    KIND_TOKENS: ("test_code", "item_code"),
    KIND_DEVICES: ("kit_code",),
    KIND_ACCESSION: ("test_code", "catalogue_code"),
    KIND_LONG: ("concept_code",),
}
HELD_UNTIL_NO = ("catalogue_code", "item_code", "concept_code")


# -- the catalogue's tables (lane E0c's form, plan P4-D431) -----------------

_SSN = r"\d{3}[-– ]?\d{2}[-– ]?\d{4}[A-Z]?"


def _table(
    name: str, kind: str, header: "tuple[str, ...]", knows: "dict[str, str]",
    checks: "tuple[zoo.Check, ...]",
) -> zoo.Table:
    return zoo.Table(
        name, ".csv", MAKERS[kind], lambda head, rows: zoo.csv_bytes(head, rows),
        {kind: header}, {"patient_ref": "identifier", **knows}, zoo._csv_reader(), checks,
        person="patient_ref",
        leaks=tuple((column, "values") for column in IDENTIFIERS[kind]),
    )


def _listed(kind: str, column: str, pool: "tuple[tuple[str, float], ...]") -> zoo.Check:
    return zoo._listed(kind, f"{column} keeps its codes", column, zoo._levels(pool))


CATALOGUE_TABLES: "tuple[zoo.Table, ...]" = (
    _table(
        "social_numbers", KIND_SSN, ("patient_ref", "ssn", "visit_kind", "charge", "member_ref"),
        {"ssn": "identifier", "member_ref": "identifier"},
        (zoo._pattern(KIND_SSN, "social security numbers in their forms", "ssn", _SSN),),
    ),
    _table(
        "payer_members", KIND_MEMBER, ("patient_ref", "member_id", "plan_code", "visit_kind", "charge"),
        {"member_id": "identifier", "plan_code": "code"},
        (zoo._pattern(KIND_MEMBER, "member numbers of letters and figures", "member_id", r"[0-9A-Z-]{6,15}"),
         _listed(KIND_MEMBER, "plan_code", PLAN_CODES)),
    ),
    _table(
        "labelled_patients", KIND_NAME_RECORD,
        ("patient_ref", "patient_label", "kit_code", "visit_kind", "charge", "chart_label", "procedure_label",
         "band_label"),
        {"patient_label": "identifier", "kit_code": "code", "chart_label": "identifier", "procedure_label": "code",
         "band_label": "identifier"},
        (zoo._pattern(KIND_NAME_RECORD, "a name and a record number in one cell", "patient_label",
                      r"[A-Z][a-z]+, ?[A-Z][a-z]+( [A-Z])? ?[\[(]\d{7}[\])]"),
         _listed(KIND_NAME_RECORD, "kit_code", KIT_CODES),
         _listed(KIND_NAME_RECORD, "procedure_label", PROCEDURE_LABELS)),
    ),
    _table(
        "relatives", KIND_RELATIVE, ("patient_ref", "ssn", "partner_ssn", "guardian_id", "visit_kind", "charge"),
        {"ssn": "identifier", "partner_ssn": "identifier", "guardian_id": "identifier"},
        (zoo._pattern(KIND_RELATIVE, "the patient's social security number", "ssn", r"\d{3}-\d{2}-\d{4}"),
         zoo._pattern(KIND_RELATIVE, "a partner's social security number", "partner_ssn", r"\d{3}-\d{2}-\d{4}"),
         zoo._pattern(KIND_RELATIVE, "a guardian's number of nine figures", "guardian_id", r"\d{9}")),
    ),
    _table(
        "issued_tokens", KIND_TOKENS,
        ("patient_ref", "record_token", "test_code", "visit_kind", "charge", "access_key", "item_code",
         "session_ref"),
        {"record_token": "identifier", "test_code": "code", "access_key": "identifier", "item_code": "code",
         "session_ref": "identifier"},
        (zoo._pattern(KIND_TOKENS, "hexadecimal and base64 tokens", "record_token",
                      r"[0-9a-f]{32}|[0-9A-F]{32}|[0-9a-f]{64}|[0-9A-F]{64}|[A-Za-z0-9+/]{22}(==)?"),
         _listed(KIND_TOKENS, "test_code", TEST_CODES),
         _listed(KIND_TOKENS, "item_code", ITEM_CODES)),
    ),
    _table(
        "implant_log", KIND_DEVICES,
        ("patient_ref", "device_lot", "device_serial", "device_udi", "kit_code", "visit_kind", "charge", "implant_ref",
         "sn"),
        {"device_lot": "identifier", "device_serial": "identifier", "device_udi": "identifier", "kit_code": "code",
         "implant_ref": "identifier", "sn": "identifier"},
        (zoo._pattern(KIND_DEVICES, "lot numbers", "device_lot", r"[A-Z]\d{5}|\d{2}[A-Z]{2}\d{4}|LOT\d{6}"),
         zoo._pattern(KIND_DEVICES, "serial numbers", "device_serial", r"SN-\d{4}-\d{2}|\d{10}|[A-Z]{2}\d{8}"),
         zoo._pattern(KIND_DEVICES, "UDIs with their application identifiers", "device_udi",
                      r"\(01\) ?\d{14}( ?\((10|11|17|21)\) ?[0-9A-Z]+)+"),
         _listed(KIND_DEVICES, "kit_code", KIT_CODES)),
    ),
    _table(
        "specimen_units", KIND_ACCESSION,
        ("patient_ref", "specimen_accession", "blood_unit", "test_code", "visit_kind", "charge",
         "specimen_ref", "unit_ref", "catalogue_code", "block_ref", "slide_ref"),
        {"specimen_accession": "identifier", "blood_unit": "identifier", "test_code": "code",
         "specimen_ref": "identifier", "unit_ref": "identifier", "catalogue_code": "code", "block_ref": "identifier",
         "slide_ref": "identifier"},
        (zoo._pattern(KIND_ACCESSION, "accession numbers in three layouts", "specimen_accession",
                      r"[A-Z]\d{2}-?\d{6}|\d{2}[A-Z]\d{1,6}"),
         zoo._pattern(KIND_ACCESSION, "ISBT 128 unit numbers", "blood_unit", r"[A-Z]\d{4} ?\d{2} ?\d{6} ?\d{2}"),
         _listed(KIND_ACCESSION, "test_code", TEST_CODES),
         _listed(KIND_ACCESSION, "catalogue_code", CATALOGUE_CODES)),
    ),
    _table(
        "long_references", KIND_LONG,
        ("patient_ref", "claim_number", "order_number", "visit_kind", "charge", "case_number", "concept_code"),
        {"claim_number": "identifier", "order_number": "identifier", "case_number": "identifier",
         "concept_code": "code"},
        (zoo._pattern(KIND_LONG, "claim numbers of sixteen figures", "claim_number", r"\d{16}"),
         zoo._pattern(KIND_LONG, "order numbers of nineteen figures", "order_number", r"\d{19}"),
         _listed(KIND_LONG, "concept_code", CONCEPT_CODES)),
    ),
)
TABLE_OF = {table.kinds and next(iter(table.kinds)): table for table in CATALOGUE_TABLES}
# ...and the driver's own form, beside them and outside the catalogue.
NAME_ROWS_TABLE = _table(
    "visit_records", KIND_NAME_ROWS, ("patient_ref", "visit_label", "visit_kind", "charge"),
    {"visit_label": "identifier"},
    (zoo._pattern(KIND_NAME_ROWS, "a name beside a record number of its own on every row", "visit_label",
                  r"Cedar, [A-Z][a-z]{2} \[\d{7}\]"),),
)
TABLE_OF[KIND_NAME_ROWS] = NAME_ROWS_TABLE


# -- K-HZ-14, per form: what is real in what the commands write --------------

# The modes a form is measured in: nobody answering; the zoo's truthful
# answers round by round (the person question `identifier` for the
# patient key and `keep` for the rest, `yes` to the Safe Harbor question
# for an identifier, as `health_zoo.answer_generally` gives them, so the
# table is counted in the patient key's people); the person question
# answered `keep` for every column, the patient key's too, so nothing
# counts the table in people, and the form's columns answered with a
# reading that publishes values -- `code` where a question offers it,
# else `keep` or `measurement` -- their Safe Harbor question left blank
# (`coded`: a member number read as a code column, a relative's number
# kept as what it was read as, on a table counted in rows); and `no` to
# every Safe Harbor question, which says what that answer frees.
MODES = ("unanswered", "truthful", "coded", "no")
# The seed of the control table a twin's figure runs are counted against,
# and how many such tables K-HZ-14 reads (`chance_of_runs`).
CONTROL_SEED_STEP = 7919
CONTROL_TABLES = 20
# The readings `coded` answers a form's column with, the first offered.
CODED_READINGS = ("code", "keep", "measurement")
ANSWER_ROUNDS_AT_MOST = 6


def as_a_spreadsheet_stores(value: str) -> str:
    """A whole number as a spreadsheet stores it in a NUMBER cell, typed or computed: a float's own spelling.

    Below 10**16 the figures of the float nearest it (a sixteen-figure
    number past 2**53 rounded); from there the exponent form, either as
    the shortest spelling that reads back the same float
    (`8.234567890123457E+18`, an odd number) or as the spreadsheet's cut
    to fifteen significant figures (`8.23456789012346E+18`, an even one).
    """
    number = int(value)
    if number < 10 ** 16:
        return f"{int(float(number))}"
    if number % 2:
        return repr(float(number)).upper()
    return f"{float(number):.14E}"


# The long identifiers' columns a workbook of NUMBER cells stores as numbers
# (the verify's item 2 of lane CZ-A's repair 1, `long_ids` written so).
NUMBER_COLUMNS = ("claim_number", "order_number", "case_number")


def book_bytes(header: "list[str]", rows: "list[list[str]]", numbers: bool = False) -> bytes:
    """A table as an Excel workbook whose every cell is text, as an exporter that keeps an identifier's figures writes it.

    ``numbers``: the long identifiers' columns (`NUMBER_COLUMNS`) are
    NUMBER cells instead, as a person typing them or a formula leaves
    them, each in a float's own spelling (`as_a_spreadsheet_stores`), the
    exponent form among them; every other cell text.
    """
    import workbooks

    body: "list[tuple[int, list[str]]]" = [
        (1, [workbooks.cell(f"{zoo._letter(place)}1", header[place], "inlineStr") for place in range(len(header))])
    ]
    typed = [numbers and header[place] in NUMBER_COLUMNS for place in range(len(header))]
    for index in range(len(rows)):
        body += [(index + 2, [
            workbooks.cell(f"{zoo._letter(place)}{index + 2}", as_a_spreadsheet_stores(rows[index][place]))
            if typed[place] and rows[index][place].strip()
            else workbooks.cell(f"{zoo._letter(place)}{index + 2}", rows[index][place], "inlineStr")
            for place in range(len(header))
        ])]
    last = f"{zoo._letter(len(header) - 1)}{len(rows) + 1}"
    return workbooks.package(
        [
            ("[Content_Types].xml", workbooks._content_types(1, False, False, False)),
            ("_rels/.rels", workbooks._root_rels()),
            ("xl/workbook.xml", workbooks._workbook([("Export", "")])),
            ("xl/_rels/workbook.xml.rels", workbooks._workbook_rels(1, False)),
            ("xl/styles.xml", workbooks._styles()),
            ("xl/worksheets/sheet1.xml", workbooks.sheet(body, dimension=f"A1:{last}")),
        ]
    )


def _write(
    folder: pathlib.Path, table: zoo.Table, rows: int, seed: int, people: "int | None", book: bool = False,
    numbers: bool = False,
) -> pathlib.Path:
    header, body = table.build(rows, seed, people) if people else table.build(rows, seed)  # type: ignore[call-arg]
    if book:
        source = folder / f"{table.name}.xlsx"
        source.write_bytes(book_bytes(header, body, numbers))
        return source
    source = folder / f"{table.name}.csv"
    with open(source, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(body)
    return source


def _column(path: pathlib.Path, name: str) -> "list[str]":
    """A column's cells as text, from a CSV file or, through synthtwin's own reader, a workbook."""
    if path.suffix == ".xlsx":
        from synthtwin import reading

        read = reading.read_table(f"{path}")
        return list(read.columns[read.column_names.index(name)])
    with open(path, encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        header = next(reader)
        place = header.index(name)
        return [row[place] if place < len(row) else "" for row in reader]


def _answer_no(document: "dict") -> None:
    """Every Safe Harbor question answered `no`, every other left as the zoo's answers left it."""
    for entry in zoo._entries(document):
        if sorted(zoo._offered(entry)) == ["no", "yes"]:
            entry["your_answer"] = "no"


def _answer_coded(document: "dict", columns: "tuple[str, ...]") -> None:
    """The person question `keep` everywhere; the form's columns a reading that publishes values, their Safe Harbor question blank."""
    for entry in zoo._entries(document):
        if zoo._asks_for_people(entry) and "keep" in zoo._offered(entry):
            entry["your_answer"] = "keep"
            continue
        if f"{entry.get('column', '')}" not in columns:
            continue
        offered = zoo._offered(entry)
        if sorted(offered) == ["no", "yes"]:
            entry["your_answer"] = ""
            continue
        entry["your_answer"] = next((reading for reading in CODED_READINGS if reading in offered), "")


def measure(
    folder: pathlib.Path, kind: str, rows: int, mode: str = "unanswered",
    seed: int = SEED, people: "int | None" = None, small_tables_refused: "bool | None" = None,
    book: bool = False, numbers: bool = False,
) -> "dict[str, object]":
    """One form's table through profile (and its rounds of answers), generate at seed 0 and validate.

    Returns, per column, its role at the first and at the last
    description, the questions put to it, and for each identifier column
    what of its real values the files carry (`unanswered_identifier_
    shapes.count_real`, linear: whole values and fragments in the
    description, its summary, the questions file and the screen, at every
    round, and the twin's report and quality files (lane CZ-A's repair 1,
    skeptic 1 item 11); twin cells holding one), the twin cells equal to a
    real value, and the product's own seconds apart from the counting;
    and under `twin_values` each identifier column's different twin
    values, for K-HZ-14's chance of a figure run (`chance_of_runs`).
    """
    import unanswered_identifier_shapes as shapes
    from synthtwin import cli

    table = TABLE_OF[kind]
    folder.mkdir(parents=True, exist_ok=True)
    source = _write(folder, table, rows, seed, people, book, numbers)
    refused = rows >= zoo.KPI_ROWS if small_tables_refused is None else small_tables_refused
    screen = io.StringIO()
    texts: "list[str]" = []
    first_roles: "dict[str, str]" = {}
    put: "dict[str, list[list[str]]]" = {}
    profile = folder / f"{table.name}-profile.json"
    questions = folder / f"{table.name}-questions.json"
    started = time.perf_counter()
    found: "dict[str, object]" = {
        "kind": kind, "rows": rows, "mode": mode, "book": book, "numbers": numbers, "columns": {},
    }

    def read_round() -> None:
        texts.extend([profile.read_text(encoding="utf-8"), questions.read_text(encoding="utf-8"),
                      (folder / f"{table.name}-profile.txt").read_text(encoding="utf-8")])
        for entry in zoo._entries(json.loads(questions.read_text(encoding="utf-8"))):
            asked = put.setdefault(f"{entry.get('column', '')}", [])
            offered = sorted(zoo._offered(entry))
            if offered not in asked:
                asked += [offered]

    with shapes.nobody_at_the_keyboard():
        with contextlib.redirect_stdout(screen), contextlib.redirect_stderr(screen):
            code = cli.main(["profile", f"{source}", "--replace"], small_tables_refused=refused)
            found["profile"] = code
            if code == 0:
                read_round()
                first_roles.update({f"{c['name']}": f"{c['role']}"
                                    for c in json.loads(profile.read_text(encoding="utf-8"))["columns"]})
                rounds = 0
                while mode != "unanswered" and rounds < ANSWER_ROUNDS_AT_MOST:
                    document = json.loads(questions.read_text(encoding="utf-8"))
                    if not [e for e in zoo._entries(document) if not f"{e.get('your_answer') or ''}"]:
                        break
                    before = json.dumps(document, sort_keys=True)
                    zoo.answer_generally(table, document)
                    if mode == "no":
                        _answer_no(document)
                    if mode == "coded":
                        _answer_coded(document, IDENTIFIERS[kind])
                    if json.dumps(document, sort_keys=True) == before:
                        break
                    questions.write_text(json.dumps(document, indent=2), encoding="utf-8", newline="\n")
                    code = cli.main(["profile", f"{source}", "--replace", "--answers", f"{questions}"],
                                    small_tables_refused=refused)
                    rounds += 1
                    if code != 0:
                        break
                    read_round()
                found["rounds"] = rounds
                found["answers"] = code
            found["profile_seconds"] = round(time.perf_counter() - started, 1)
            stage = time.perf_counter()
            generated = (cli.main(["generate", f"{profile}", "--replace", "--seed", "0"], small_tables_refused=refused)
                         if code == 0 else -1)
            found["generate_seconds"] = round(time.perf_counter() - stage, 1)
            stage = time.perf_counter()
            validated = (cli.main(["validate", f"{profile}", "--replace"], small_tables_refused=refused)
                         if generated == 0 else -1)
            found["validate_seconds"] = round(time.perf_counter() - stage, 1)
    found["generate"], found["validate"] = generated, validated
    found["product_seconds"] = round(time.perf_counter() - started, 1)
    # A REFUSED ROUND IS COUNTED TOO (lane CZ-A's repair 2, Codex item 3):
    # what the rounds before it wrote and the screen printed is read as
    # every other run's is, so an identifier shown in a round that passed
    # is counted though a later answer round was refused; the last
    # description written names the roles, and no twin is read.
    if code != 0:
        found["screen"] = screen.getvalue()[-400:]
    texts += [screen.getvalue()]
    if generated == 0:
        for written in (f"{table.name}-twin-report.txt", f"{table.name}-twin-quality.txt"):
            if (folder / written).is_file():
                texts += [(folder / written).read_text(encoding="utf-8")]
    found["twin_values"] = {}
    counting = time.perf_counter()
    described = (
        {f"{c['name']}": c for c in json.loads(profile.read_text(encoding="utf-8"))["columns"]}
        if first_roles and profile.is_file() else {}
    )
    for name in IDENTIFIERS[kind]:
        described.setdefault(name, {"role": None})
    twin = folder / f"{table.name}-twin{source.suffix}"
    real_rows = _column(source, "patient_ref")
    # THE CHANCE OF A FIGURE RUN (the orchestrator's LANE I4m RULINGS 6 (3):
    # never recorded as chance without a measurement of it): the same form
    # drawn at another seed, values the twin never read, counted in the same
    # twin cells by the same counter.
    control = folder / "control"
    control.mkdir(exist_ok=True)
    control_source = _write(control, table, rows, seed + CONTROL_SEED_STEP, people, book, numbers)
    for name in described:
        entry: "dict[str, object]" = {
            "role_unanswered": first_roles.get(name), "role": described[name]["role"], "asked": put.get(name, []),
        }
        if name in IDENTIFIERS[kind]:
            real_cells = _column(source, name)
            real = sorted({cell for cell in real_cells if cell.strip()})
            cells = _column(twin, name) if generated == 0 and twin.is_file() else []
            entry.update(shapes.count_real(real, texts, cells, linear=True))
            known = set(real)
            entry["twin_cells_equal"] = len([cell for cell in cells if cell in known])
            entry["twin_complete_tokens"] = complete_tokens(real, cells)
            unseen = sorted({cell for cell in _column(control_source, name) if cell.strip()} - known)
            entry["twin_cells_control"] = shapes.count_real(unseen, [], cells, linear=True)["twin_cells"]
            entry["different"] = len(real)
            entry["people"] = len(set(real_rows))
            found["twin_values"][name] = sorted({cell for cell in cells if cell.strip()})  # type: ignore[index]
        found["columns"][name] = entry  # type: ignore[index]
    found["counting_seconds"] = round(time.perf_counter() - counting, 1)
    return found


# The fewest figures a run of a real value holds to be counted by the
# chance of a figure run (`carrying_runs`).
CHANCE_RUN_FIGURES = 5


def figure_runs(value: str) -> "list[str]":
    """Each run of figures of a value, whole, of `CHANCE_RUN_FIGURES` figures or more."""
    runs: "list[str]" = []
    run = ""
    for character in value + " ":
        if "0" <= character <= "9":
            run += character
            continue
        if len(run) >= CHANCE_RUN_FIGURES:
            runs += [run]
        run = ""
    return runs


# The marks that join the parts of one code, so a run beside them stands in
# that code's word (as `synthtwin.taxonomy.OWN_WORD_JOINS` reads a layout).
WORD_JOINS = "-./_+"


def inner_runs(value: str) -> "list[str]":
    """Each run of figures of a value of two words or more, of `CHANCE_RUN_FIGURES` figures or more.

    A word is a stretch of letters, figures and the marks that join a
    code's parts (`WORD_JOINS`) holding a letter or a figure; any other
    character -- a space, a bracket, `#`, `:`, a comma -- parts words. In
    a value of two words or more, every such run stands inside a wider
    value, however it is glued in its word (`[1234567]`, `[MR1234567]`,
    `#MR1234567`, `[1234567A]`, `[REC-1234567]`: batch 4q's fix round 2,
    the verify's blocker 1); a value of one word (`MR1234567`,
    `S24-123456`) holds none: it is one key.
    """
    words = 0
    worded = False
    for place in range(len(value) + 1):
        joined = place < len(value) and (value[place].isalnum() or value[place] in WORD_JOINS)
        if not joined:
            words = words + 1 if worded else words
            worded = False
        elif value[place].isalnum():
            worded = True
    return figure_runs(value) if words >= 2 else []


def complete_tokens(real: "list[str]", cells: "list[str]") -> int:
    """How many twin cells hold a COMPLETE real record token inside a wider cell (Codex's review of batch 4q, item 1).

    A real token is any run of figures of a real value, of
    `CHANCE_RUN_FIGURES` figures or more (`figure_runs`): a record number
    beside a name, glued to its label or standing alone, a sequence beside
    a facility's code. A twin cell holds one where one of its runs inside a
    wider value (`inner_runs`: a cell of two words or more, however the run
    is glued in its word; the verify of the fix round, blocker 1) is that
    token whole, so the whole-cell counts never see it: the record number
    stands complete inside a wider made-up value. LINEAR: the real tokens
    in a set, each different twin cell read once.
    """
    tokens: "set[str]" = set()
    for value in real:
        tokens.update(figure_runs(value))
    found = 0
    seen: "dict[str, int]" = {}
    for cell in cells:
        if cell not in seen:
            seen[cell] = 1 if any(run in tokens for run in inner_runs(cell)) else 0
        found += seen[cell]
    return found


def carrying_runs(real: "list[str]", twin_values: "list[str]") -> int:
    """How many twin values hold, inside a run of figures of their own, a run of five figures or more of a real value.

    EVERY RUN OF A REAL VALUE (lane CZ-A's repair 2, Codex item 4): a UDI
    `(01)02211351444010(17)290712(21)2722647430` holds three runs, and a
    twin value `ZZ2722647430` holding the third carries it -- the counter
    that read a value whole and its longest run of figures alone read 0
    there. LINEAR: the real runs in sets by their lengths; each twin
    value's runs read once, through windows of those lengths.
    """
    by_length: "dict[int, set[str]]" = {}
    for value in real:
        for run in figure_runs(value):
            by_length.setdefault(len(run), set()).add(run)
    lengths = sorted(by_length)
    carrying = 0
    for value in twin_values:
        held = False
        for run in figure_runs(value):
            for size in lengths:
                if size > len(run) or held:
                    break
                seen = by_length[size]
                held = any(run[start:start + size] in seen for start in range(len(run) - size + 1))
            if held:
                break
        carrying += 1 if held else 0
    return carrying


def chance_of_runs(kind: str, column: str, rows: int, twin_values: "list[str]") -> "dict[str, object]":
    """The different twin values of a column carrying a real value's run of five figures or more, against chance.

    THE CHANCE, MEASURED ONCE A COLUMN (lane CZ-A's repair 1, the
    statistics skeptic's item 3; the orchestrator's LANE CZ-A RULINGS 1
    (4)): ``twin_values`` are the column's different twin values, every
    mode's together, so a made-up value written in three modes is counted
    once; each is read against the real values (the form at `SEED`) and
    against those of `CONTROL_TABLES` tables of the form at other seeds,
    which the twin never read, by the linear counter. EVERY RUN of a real
    value counts, on the real side and the controls' alike
    (`carrying_runs`, repair 2, Codex item 4). Returns the real count,
    each control's, their mean, and how many controls reach the real
    count (the percentile: that many in `CONTROL_TABLES`).
    """
    table = TABLE_OF[kind]

    def values_at(seed: int) -> "set[str]":
        header, body = table.build(rows, seed)  # type: ignore[call-arg]
        place = header.index(column)
        return {row[place] for row in body if place < len(row) and row[place].strip()}

    real = values_at(SEED)
    found = carrying_runs(sorted(real), twin_values)
    controls = [
        carrying_runs(sorted(values_at(SEED + step * CONTROL_SEED_STEP) - real), twin_values)
        for step in range(1, CONTROL_TABLES + 1)
    ]
    return {
        "twin_values": len(twin_values), "carrying": found, "controls": controls,
        "control_mean": round(sum(controls) / len(controls), 2),
        "controls_reaching": len([count for count in controls if count >= found]),
    }
