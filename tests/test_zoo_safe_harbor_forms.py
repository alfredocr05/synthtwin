"""P4-D445 (lane CZ-A): Safe Harbor identifier forms the zoo did not test before, held while unanswered.

EIGHT FORMS (`tests/safe_harbor_forms.py`, each an invented look-alike of
the zoo's own making, generic names, every value from its makers and
seeds): social security numbers dashed and undashed in one column, a few
spaced or with an en dash, one in fifty with a trailing capital letter; a
payer's member number in more than ten formats in one column; a name and a
record number in one cell; a relative's social security number beside the
patient's under neutral names; opaque tokens of 32 and 64 hexadecimal and
22 and 24 base64 characters; device lot and serial numbers and GS1-style
UDIs carrying a serial (21) or a lot (10); accession numbers in three
layouts and ISBT 128 blood-unit numbers; identifiers of 16 and 19 figures.

THE RULE (`taxonomy.identifier_form_hold`, asked first by
`taxonomy.safe_harbor_hold`): each form is held whole, as lane SH2's device
numbers are -- P4-D401's held block, its twin writing made-up values in its
own layouts -- and put the one Safe Harbor question, on every role but a
held identifier, free text among them; while an open question offering
`identifier` names the column, that question is the one put. Any other
answer or reading (`code`, `keep`, `measurement`) is no release; `no`
frees the column to the reading it had, `yes` holds it for good. AND A
BLANK KEEPS A COLUMN HELD IN PEOPLE HELD: its own question, put beside the
hold under another reading, names `identifier` now (`asking.held_back`
handed the columns held whole in people), so the person question's answer
does not publish it with its own question open.

AND THE HELD WALK PASSES OVER A LAYOUT OF ANOTHER BAND (`generation.
_fillings_outside_the_band`), and the rule-away mutant: their cases stand
in the gate's second file, `tests/test_zoo_safe_harbor_forms_walk.py`
(repair 2: this file read 181.6 CPU seconds with them, past the 180 a gate
file may take; every case kept).

REPAIR 1 (the orchestrator's LANE CZ-A RULINGS 1; skeptic 1 items 1 to 7,
each a variant of a form that published whole when answered a reading
that publishes, at 20,000 rows): social security numbers written with
another dash or space and a letter of either case after them, a space
before it or none; base64 tokens of 24 characters with no padding and
keys of 43 and 44; a name beside a labelled record number, after a
number sign, beside a family name ending in a point or opening with
small words, six figures at least (RULINGS 1 (2): a procedure's code of
four or five figures beside its label is none); whole numbers of sixteen
figures or more on ONE cell; GS1 UDIs with their application identifiers
in square brackets (lane SH2's reader); ISBT 128 unit numbers with their
check character or the data identifier `=`; accession numbers in the
letters-first and the year-first layouts with no dash. Each reading has
its cells here and a variant column beside its form in the zoo's table;
the closed lists the rule holds until `no` (codes of three capitals, two
figures, a dash and four figures; of 32 small hexadecimal characters; of
16 to 18 figures, the zoo's concept ids among them) are the price, named.

REPAIR 2 (the orchestrator's LANE CZ-A RULINGS 2 and 3; Codex's items 1 to
7 and the verify's items 1 to 5): an accession number the year first with
its dash, or with a dash between its capitals and its year, is a dashed
layout; a name beside a record number with a sole initial and its point,
or a family name with a curly apostrophe; a UUID read as the 32
hexadecimal characters it writes; a whole number of sixteen figures or
more in the exponent form a spreadsheet stores a number cell in; a column
named `sn` or `batch`. Each reading has its cells here, its column read
by the rule at 20,000 cells (Codex's and the verify's tables), and a
variant column beside its form in the zoo's table, measured through the
command at 20,000 rows by K-HZ-14. And K-HZ-14's measure: a later refused
round counts what the rounds before it showed (Codex item 3); the chance
of a figure run reads every run of a real value (Codex item 4); the long
numbers' question names a possible identifier (Codex item 5); the tokens'
form writes 64 hexadecimal capitals (Codex item 6).

THE GATE: every form at 600 rows, unanswered and with its columns answered
a reading that publishes values (`coded`): 0 real values in the
description, its summary, the questions file or the screen, 0 twin cells
holding a real value, and a question put; the forms' cell tests and the
code lists beside them (no false alarm); and ONE 20,000-row case (the
member numbers, a thousand people at the owner's floor, the reach of a set
of categories), THE SUITE'S TIME rule. The other 20,000-row runs, every
form in every mode, are K-HZ-14's (`tools/measurements/kpi_safe_harbor_
forms.py`, `kpi_run --slow`).
"""

from __future__ import annotations

import json
import pathlib

import pytest

import health_zoo as zoo
import safe_harbor_forms as forms
from synthtwin import taxonomy

# -- the cells ------------------------------------------------------------------


@pytest.mark.parametrize(("cell", "form"), [
    ("900-12-3456", "separated"),
    ("900 12 3456", "separated"),
    ("900–12–3456", "separated"),
    ("900-12-3456A", "separated"),
    ("900123456", "plain"),
    ("900123456Z", "plain"),
    (" 900-12-3456 ", "separated"),
    ("900-123-4567", ""),
    ("900-12 3456", ""),
    ("90-012-3456", ""),
    ("900-12-345", ""),
    ("900123456AB", ""),
    ("12345-6789", ""),
    # REPAIR 1, SKEPTIC 1 ITEM 1: the other dashes and spaces, and a letter
    # of either case after the number, a space before it or none.
    ("900-12-3456a", "separated"),
    ("900-12-3456 A", "separated"),
    ("900123456 z", "plain"),
    ("900\u201012\u20103456", "separated"),
    ("900\u201112\u20113456", "separated"),
    ("900\u201212\u20123456", "separated"),
    ("900\u221212\u22123456", "separated"),
    ("900\ufe6312\ufe633456", "separated"),
    ("900\uff0d12\uff0d3456", "separated"),
    ("900\u00a012\u00a03456", "separated"),
    ("900\u202f12\u202f3456", "separated"),
    ("900\u201112\u20113456b", "separated"),
    ("900-12\u20113456", ""),
    ("900-12-3456  A", ""),
    ("900-12-3456 AB", ""),
    ("900.12.3456", ""),
    ("900/12/3456", ""),
])
def test_a_social_security_number_is_read_in_each_of_its_forms(cell: str, form: str) -> None:
    assert taxonomy.social_security_form(cell) == form


@pytest.mark.parametrize(("cell", "held"), [
    ("1EG4TE5MK73", True), ("1EG4-TE5-MK73", True), ("9AA9AA9AA99", True),
    ("0EG4TE5MK73", False), ("1SG4TE5MK73", False), ("1EG4TE5MK7", False), ("1EG4TE5MKZ3", False),
])
def test_a_beneficiary_identifier_is_read_in_its_layout(cell: str, held: bool) -> None:
    assert taxonomy._a_beneficiary_number(cell) is held


@pytest.mark.parametrize(("cell", "held"), [
    ("Gonzalez, Maria K [1234567]", True),
    ("Gonzalez,Maria (1234567)", True),
    ("De La Cruz, Ana [123456]", True),
    ("O'Neil-Ray, Jo B. [MR123456]", True),
    ("Gonzalez, Maria", False),
    ("Maria Gonzalez [1234567]", False),
    ("Gonzalez, Maria [123]", False),
    ("cbc, diff [1234567]", False),
    ("Gonzalez, Maria [12-34567]", False),
    # REPAIR 1, SKEPTIC 1 ITEM 3: a labelled number, a number after a
    # number sign, a family name ending in a point or opening with small
    # words.
    ("Gonzalez, Maria K [REC 1234567]", True),
    ("Gonzalez, Maria K (REC: 1234567)", True),
    ("Gonzalez, Maria K #1234567", True),
    ("Gonzalez, Maria K [#1234567]", True),
    ("Gonzalez Jr., Mario [1234567]", True),
    ("de la Cruz, Maria [1234567]", True),
    ("van der Berg, Anna (MR123456)", True),
    ("Gonzalez, Maria K [RECXY 1234567]", False),
    ("Gonzalez, Maria K [REC - 1234567]", False),
    ("de, Maria [1234567]", False),
    ("cbc, diff #1234567", False),
    ("Gonzalez, Maria #12345", False),
    # ...and THE ORCHESTRATOR'S NARROWING (LANE CZ-A RULINGS 1 (2)): six
    # figures at least, so a label beside a code of four or five figures,
    # with letters after them or not, is none.
    ("De La Cruz, Ana [12345]", False),
    ("O'Neil-Ray, Jo B. [MR12345]", False),
    ("Repair, Open (41234)", False),
    ("Sodium, Serum [5678]", False),
    ("Drugname, Extended (5000MG)", False),
    # REPAIR 2, CODEX ITEM 2: a sole given-name initial with its point, and
    # a family name written with the curly apostrophe.
    ("Smith, J. [2000000]", True),
    ("Smith, J [2000000]", True),
    ("Smith, Jo B. [2000000]", True),
    (f"O{forms.CURLY_APOSTROPHE}Neil, Jo [2000000]", True),
    (f"O{forms.CURLY_APOSTROPHE}Neil, J. #2000000", True),
    ("Smith, J.. [2000000]", False),
    ("Smith, j. [2000000]", False),
    ("Smith, JO. [2000000]", False),
    ("Smith, 1. [2000000]", False),
    ("Sodium, S. [5678]", False),
])
def test_a_name_beside_a_record_number_is_read(cell: str, held: bool) -> None:
    assert taxonomy._a_name_beside_a_number(cell) is held


@pytest.mark.parametrize(("cell", "held"), [
    ("0123456789abcdef0123456789abcdef", True),
    ("0123456789ABCDEF0123456789ABCDEF", True),
    ("0123456789abcdef" * 4, True),
    ("0123456789aBcdef0123456789abcdef", False),
    ("01234567890123456789012345678901", False),
    ("abcdefabcdefabcdefabcdefabcdefab", False),
    ("duhzu2y3FHPhjwUmodosmJ", True),
    ("duhzu2y3FHPhjwUmodosmJ==", True),
    ("ABCDEFGHIJKLMNOPQRSTUV", False),
    ("duhzu2y3FHPhjwUmodosm", False),
    # REPAIR 1, SKEPTIC 1 ITEM 2: 24 characters with no padding, and a key
    # of 32 bytes, 43 characters or 44 with its `=`.
    ("duhzu2y3FHPhjwUmodosmJ4x", True),
    ("duhzu2y3FHPhjwUmodosmJ4xduhzu2y3FHPhjwUmodo", True),
    ("duhzu2y3FHPhjwUmodosmJ4xduhzu2y3FHPhjwUmodo=", True),
    ("duhzu2y3FHPhjwUmodosmJ4xduhzu2y3FHPhjwUmodos", True),
    ("duhzu2y3FHPhjwUmodosmJ=", False),
    ("duhzu2y3FHPhjwUmodosmJ4x==", False),
    ("duhzu2y3FHPhjwUmodosmJ4xduhzu2y3FHPhjwUmod==", False),
    ("ABCDEFGHIJKLMNOPQRSTUVWX", False),
    ("duhzu2y3 FHPhjwUmodosmJ4", False),
    # REPAIR 2, THE VERIFY'S ITEM 1: a UUID, the 32 hexadecimal characters
    # in five groups of 8, 4, 4, 4 and 12 joined by dashes, in one case, in
    # braces or not; mixed case or mis-grouped is none.
    # REPAIR 2, CODEX ITEM 6: the 64 in capitals.
    ("0123456789ABCDEF" * 4, True),
    ("0123456789ABCDEF" * 3 + "0123456789abcdef", False),
    ("0123abcd-0123-4567-89ab-0123456789ab", True),
    ("0123ABCD-0123-4567-89AB-0123456789AB", True),
    ("{0123abcd-0123-4567-89ab-0123456789ab}", True),
    ("{0123ABCD-0123-4567-89AB-0123456789AB}", True),
    (" 0123abcd-0123-4567-89ab-0123456789ab ", True),
    ("0123abcd-0123-4567-89AB-0123456789ab", False),
    ("0123abcd0-123-4567-89ab-0123456789ab", False),
    ("0123abcd-0123-4567-89ab-0123-56789ab", False),
    ("0123abcd-0123-4567-89ab-0123456789ag", False),
    ("01234567-0123-4567-8901-012345678901", False),
    ("(0123abcd-0123-4567-89ab-0123456789ab)", False),
    ("{0123abcd-0123-4567-89ab-0123456789ab", False),
])
def test_an_opaque_token_is_read(cell: str, held: bool) -> None:
    assert taxonomy._a_hexadecimal_or_base64_token(cell) is held


@pytest.mark.parametrize(("name", "held"), [
    ("device_lot", True), ("device_serial", True), ("LotNumber", True), ("serialno", True),
    ("implant_udi", True), ("SERIAL_NBR", True),
    ("case_date_serial", False), ("serial_date", False), ("parking_slot", False), ("allotment", False),
    ("pilot_study", False), ("serum_level", False),
    # REPAIR 2, THE VERIFY'S ITEM 5: a serial number's short name, read
    # whole; not `batch`, the lot's other name (the shared test table's
    # constant column is named so: its price, named in plan P4-D445).
    ("sn", True), ("SN", True), ("device_sn", True), ("DeviceSN", True),
    ("sn_date", False), ("snomed_id", False), ("snack", False), ("batch", False), ("batch_no", False),
])
def test_a_name_says_a_device_number(name: str, held: bool) -> None:
    assert taxonomy.named_as_device_numbers(name) is held


@pytest.mark.parametrize(("cell", "form"), [
    ("S24-012345", "dashed"), ("SH19-1234", "dashed"), ("S24012345", "undashed"),
    ("24S12345", "year first"),
    ("S2-012345", ""), ("ABCD24-012345", ""), ("S24-123", ""), ("2024-01-05", ""), ("24-012345", ""),
    # REPAIR 2, CODEX ITEM 1 AND THE VERIFY'S ITEM 3: the year first with
    # its dash is a dashed layout.
    ("24S-5", "year first dashed"), ("24S-100000", "year first dashed"), ("24SP-012345", "year first dashed"),
    ("24S012345", "year first"), ("24S--012345", ""), ("24S-", ""),
    # REPAIR 2, THE VERIFY'S ITEM 4: a dash between the capitals and the
    # year, the letters first or the year first, is a dashed layout.
    ("S-24-012345", "dashed"), ("SP-24-012345", "dashed"), ("CYT-24-001234", "dashed"), ("S-24012345", "dashed"),
    ("CYT-24-00123456", "dashed"), ("24-S-012345", "year first dashed"), ("24-SP012345", "year first dashed"),
    ("S--24-012345", ""), ("S-2-012345", ""), ("S-24--012345", ""), ("24--S-012345", ""), ("S-24-123", ""),
    ("ABCD-24-012345", ""), ("s-24-012345", ""),
    # ...but no month's abbreviation beside such a dash: those are dates
    # (repair 2's price), read as before the repair.
    ("01-APR-20", ""), ("06-NOV-22", ""), ("NOV-06-2022", ""), ("24-MAR-012345", ""), ("MAR-24-012345", ""),
    ("06NOV-22", "year first"), ("06NOV2022", "year first"), ("NOV22-012345", "dashed"),
])
def test_an_accession_number_is_read_in_its_layouts(cell: str, form: str) -> None:
    assert taxonomy.accession_form(cell) == form


@pytest.mark.parametrize(("cell", "held"), [
    ("Q4012 24 123456 00", True), ("Q40122412345600", True), ("Q4012 24 123456", True),
    ("Q4012 24 12345 00", False), ("q4012 24 123456 00", False), ("Q401 24 123456 00", False),
    # REPAIR 1, SKEPTIC 1 ITEM 5: a check character after the sequence or
    # after the flags, spaced or bare, and the data identifier `=`.
    ("Q4012 24 123456 K", True), ("Q401224123456K", True), ("Q4012 24 123456 00 K", True),
    ("Q40122412345600K", True), ("Q4012 24 123456 *", True), ("=Q40122412345600", True),
    ("=Q4012 24 123456 00", True),
    ("Q4012 24 123456 k", False), ("Q4012 24 123456 00 KK", False), ("==Q4012 24 123456", False),
    ("Q4012 24  123456 K", False), ("Q4012 24 123456 000 K", False),
])
def test_a_blood_unit_number_is_read_in_its_layout(cell: str, held: bool) -> None:
    assert taxonomy._a_blood_unit_number(cell) is held


def test_a_whole_number_of_fifteen_figures_is_long() -> None:
    assert taxonomy._a_long_whole_number("123456789012345")
    assert not taxonomy._a_long_whole_number("12345678901234")
    assert not taxonomy._a_long_whole_number("1234567890123.45")


@pytest.mark.parametrize(("cell", "held"), [
    # REPAIR 2, THE VERIFY'S ITEM 2: a whole number of sixteen figures or
    # more in the exponent form a spreadsheet stores a NUMBER cell in,
    # fifteen significant figures or more, read as the figures are.
    ("1.2345678901234568E+18", True),
    ("1.23456789012345E+18", True),
    ("8.234567890123457e+18", True),
    ("1.2345678901234568E18", True),
    ("1.234567890123456E+15", True),
    (" 9.87654321098765E+19 ", True),
    ("6.02E+23", False),
    ("1.2E+18", False),
    ("1.2345678901234568E+14", False),
    ("1.23456789012345678E+15", False),
    ("1.2345678901234568E-18", False),
    ("-1.2345678901234568E+18", False),
    ("1.2345678901234568E++18", False),
    ("1.2345678901234568E+18x", False),
    ("0.12345678901234567E+17", False),
    ("123456789012", False),
    # ...of twenty figures at most: a float's spelling past them is a
    # magnitude (the taxonomy contract's spread near the float's range).
    ("1.2345678901234568E+19", True),
    ("1.2345678901234568E+20", False),
    ("9.999999999999999e24", False),
    ("1.5568479229996504e+308", False),
])
def test_a_long_number_in_exponent_form_is_read(cell: str, held: bool) -> None:
    assert taxonomy._a_long_number_in_exponent_form(cell) is held
    assert taxonomy._forms_of_a_cell(cell.strip()) == ((taxonomy.HELD_LONG_NUMBERS, 0) if held else ("", 0))


def test_the_verify_s_item_2_long_numbers_as_number_cells_are_held_at_20000_rows() -> None:
    """REPAIR 2, THE VERIFY'S ITEM 2 (the orchestrator's LANE CZ-A RULINGS 3 (1)): a column of NUMBER cells.

    A thousand made-up identifiers of nineteen figures, each on 20 rows, as
    a spreadsheet stores them in NUMBER cells and synthtwin's reader keeps
    them (`1.2345678901234568E+18`, or cut to fifteen significant figures):
    read as labels before and published whole (1,000 values in the
    description, 20,000 of 20,000 twin cells equal); one such cell holds
    the column now, beside the twelve-figure numbers of a case column too.
    The workbook through the command at 20,000 rows is K-HZ-14's
    `long_ids_numbers`.
    """
    import random

    draw = random.Random(9)
    stored = [forms.as_a_spreadsheet_stores("8" + forms._figures(draw, 18)) for _person in range(1000)]
    assert len(set(stored)) == 1000 and all("E+18" in value for value in stored)
    cells = [value for value in stored for _row in range(20)]
    assert taxonomy.identifier_form_hold("case_number", cells, frozenset({""})) == taxonomy.HELD_LONG_NUMBERS
    mixed = [f"{100000000000 + person}" for person in range(19999)] + [stored[0]]
    assert taxonomy.identifier_form_hold("case_number", mixed, frozenset({""})) == taxonomy.HELD_LONG_NUMBERS
    measured = [f"{draw.uniform(1.0, 9.9):.3E}" for _row in range(20000)]
    assert taxonomy.identifier_form_hold("reading", measured, frozenset({""})) == ""


@pytest.mark.parametrize(("cell", "held"), [
    ("(01)01234567890128(21)AB123456", True),
    ("[01]01234567890128[17]271231[21]AB123456", True),
    ("[01] 01234567890128 [21] AB123456", True),
    ("[01]0123456789012[21]AB123456", False),
    ("[10]01234567890128", False),
])
def test_a_udi_is_read_with_its_application_identifiers_in_square_brackets(cell: str, held: bool) -> None:
    """REPAIR 1, SKEPTIC 1 ITEM 6: lane SH2's device reader reads GS1's `[01]` as it reads `(01)`, fourteen figures after it."""
    assert taxonomy._a_device_identifier(cell) is held


@pytest.mark.parametrize(("name", "cells", "held"), [
    ("ssn", ["900123456"] * 50 + ["900-12-3456"], taxonomy.HELD_SOCIAL_SECURITY),
    ("ssn", ["900123456"] * 50, ""),
    ("member_id", ["XKH123456789"] * 40 + ["1EG4TE5MK73"], taxonomy.HELD_BENEFICIARIES),
    ("label", ["cbc"] * 40 + ["Gonzalez, Maria K [1234567]"], taxonomy.HELD_NAMES_WITH_NUMBERS),
    ("tok", ["0123456789abcdef" * 2] * 2 + ["word"], taxonomy.HELD_TOKENS),
    ("tok", ["0123456789abcdef" * 2] + ["word"] * 2, ""),
    ("acc", ["S24-012345", "S24012345", "24S12345"], taxonomy.HELD_ACCESSIONS),
    ("acc", ["VCV000017661", "VCV000007105", "VCV000012374"], ""),
    ("unit", ["Q4012 24 123456 00", "Q40122412345600", "x"], taxonomy.HELD_UNIT_NUMBERS),
    ("claim", ["1234567890123456", "8234567890123456789", ""], taxonomy.HELD_LONG_NUMBERS),
    ("dose", ["12", "40", "500"], ""),
    # REPAIR 1: each reading added, on one cell or on two in three.
    ("member_ref", ["x"] * 40 + ["900\u201112\u20113456"], taxonomy.HELD_SOCIAL_SECURITY),
    ("member_ref", ["x"] * 40 + ["900-12-3456 a"], taxonomy.HELD_SOCIAL_SECURITY),
    ("tok", ["duhzu2y3FHPhjwUmodosmJ4x", "Zuhzu2y3FHPhjwUmodosmJ4y", "word"], taxonomy.HELD_TOKENS),
    ("label", ["cbc"] * 40 + ["Gonzalez, Maria K [REC 1234567]"], taxonomy.HELD_NAMES_WITH_NUMBERS),
    ("label", ["cbc"] * 40 + ["Gonzalez, Maria K #1234567"], taxonomy.HELD_NAMES_WITH_NUMBERS),
    ("label", ["Repair, Open (41234)"] * 30 + ["Sodium, Serum [5678]"] * 30, ""),
    ("claim", ["123456789012"] * 40 + ["1234567890123456"], taxonomy.HELD_LONG_NUMBERS),
    ("claim", ["12"] * 40 + ["123456789012345"], ""),
    ("unit", ["Q4012 24 123456 K", "Q401224123457*", "x"], taxonomy.HELD_UNIT_NUMBERS),
    # REPAIR 1, SKEPTIC 1 ITEM 4: accession numbers with no dash in both
    # the letters-first and the year-first layouts are held; a list of
    # one undashed layout stays spared (one code system writes one).
    ("acc", ["S24012345", "H23012346", "24S12345"], taxonomy.HELD_ACCESSIONS),
    ("acc", ["S24012345", "H23012346", "C22000017"], ""),
    ("acc", ["24S12345", "23H1234", "22C17"], ""),
    # REPAIR 2, CODEX ITEM 1 AND THE VERIFY'S ITEM 3: the year first with
    # its dash, alone or beside the year first undashed.
    ("acc", ["24S-012345", "24S012346", "23H-12347"], taxonomy.HELD_ACCESSIONS),
    ("acc", ["24S-12345", "23H-1234", "22C-17"], taxonomy.HELD_ACCESSIONS),
    # ...and THE VERIFY'S ITEM 4: a dash between the capitals and the year,
    # cells of fifteen characters among them.
    ("acc", ["CYT-24-00123456", "CYT-23-00123457", "word"], taxonomy.HELD_ACCESSIONS),
    ("acc", ["24-S-012345", "S-23-012346", "word"], taxonomy.HELD_ACCESSIONS),
])
def test_the_column_rule_reads_each_form(name: str, cells: "list[str]", held: str) -> None:
    assert taxonomy.identifier_form_hold(name, cells, frozenset({""})) == held


def test_codex_item_1_the_year_first_dashed_column_is_held_at_20000_rows() -> None:
    """REPAIR 2, CODEX ITEM 1 (the orchestrator's LANE CZ-A RULINGS 2 (1)): its table's column, read by the rule.

    `24S-100000` to `24S-100999`, each on 20 rows: the year first with its
    dash, read as no dashed layout before, published all 1,000 when
    answered `keep` and `code`; held now. The same column through the
    command at 20,000 rows, unanswered, truthful, coded and `no`, is
    K-HZ-14's `block_ref` (`kpi_run --slow`). And the verify's item 3: the
    year first half dashed, half not, `24S-012345` beside `24S012345`.
    """
    codex = [f"24S-{100000 + person}" for person in range(1000) for _row in range(20)]
    assert taxonomy.identifier_form_hold("block_ref", codex, frozenset({""})) == taxonomy.HELD_ACCESSIONS
    import random

    draw = random.Random(3)
    halves = []
    for person in range(1000):
        letter, year, sequence = draw.choice("SHCMB"), draw.randint(19, 26), f"{draw.randint(0, 999999):06d}"
        halves += [f"{year}{letter}-{sequence}" if person % 2 else f"{year}{letter}{sequence}"] * 20
    assert taxonomy.identifier_form_hold("specimen_accession", halves, frozenset({""})) == taxonomy.HELD_ACCESSIONS


def test_the_verify_s_item_4_accessions_dashed_after_their_capitals_are_held_at_20000_rows() -> None:
    """REPAIR 2, THE VERIFY'S ITEM 4 (the orchestrator's LANE CZ-A RULINGS 3 (1)): a dash between capitals and year.

    A thousand made-up accession numbers on 20 rows each, written
    `S-24-012345`, `SP-24-...`, `CY-24-...`, `H-24-...` or the year first
    `24-S-012345`: read as no accession number before and published whole
    when answered a reading that publishes; held now. Through the command
    at 20,000 rows: K-HZ-14's `slide_ref`.
    """
    import random

    draw = random.Random(4)
    values = forms._distinct(draw, 1000, forms.accession_dashed_twice)
    cells = [value for value in values for _row in range(20)]
    assert taxonomy.identifier_form_hold("specimen_accession", cells, frozenset({""})) == taxonomy.HELD_ACCESSIONS
    # ...AND ITS PRICE, NARROWED: dates of a two-figure year written `01-APR-20`
    # (the zoo's `registry_extract.op_date`) are no accession numbers.
    months = ("JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC")
    dates = [f"{draw.randint(1, 28):02d}-{draw.choice(months)}-{draw.randint(20, 24)}" for _row in range(20000)]
    assert taxonomy.identifier_form_hold("op_date", dates, frozenset({""})) == ""


def test_codex_item_6_the_token_form_writes_64_hexadecimal_capitals() -> None:
    """REPAIR 2, CODEX ITEM 6 (the orchestrator's LANE CZ-A RULINGS 2 (6)): the form's maker tries what it names.

    The tokens' form names 64 hexadecimal characters in either case, and
    its maker wrote them in small letters alone; it writes capitals too
    now, each read as a token, and the catalogue's pattern takes them.
    """
    import re

    header, body = forms.opaque_tokens(600, forms.SEED)
    place = header.index("record_token")
    tokens = {row[place] for row in body}
    capitals = [value for value in tokens if len(value) == 64 and value == value.upper() and value != value.lower()]
    smalls = [value for value in tokens if len(value) == 64 and value == value.lower() and value != value.upper()]
    assert capitals and smalls, (len(capitals), len(smalls))
    assert all(taxonomy._a_hexadecimal_or_base64_token(value) for value in capitals)
    import pandas

    checks = [one for one in forms.TABLE_OF[forms.KIND_TOKENS].checks if one.column == "record_token"]
    assert len(checks) == 1
    assert checks[0].run({"text": {"record_token": pandas.Series(sorted(tokens))}}) == 0
    assert checks[0].run({"text": {"record_token": pandas.Series(capitals[:1] + ["0123456789ABCDEf" * 4])}}) == 1
    assert re.fullmatch("[0-9A-F]{64}", capitals[0])


@pytest.mark.parametrize("written", ["lower", "upper", "braced"])
def test_the_verify_s_item_1_uuids_are_held_at_20000_rows(written: str) -> None:
    """REPAIR 2, THE VERIFY'S ITEM 1, THE BLOCKER (the orchestrator's LANE CZ-A RULINGS 3 (1)): a column of UUIDs.

    A thousand made-up UUIDs on 20 rows each, small letters, capitals or
    in braces: read as no token before, published whole when answered
    `keep` and a reading that publishes (1,000 values in the description,
    20,000 of 20,000 twin cells equal); held now. The same column through
    the command at 20,000 rows is K-HZ-14's `session_ref`.
    """
    import random

    draw = random.Random(5)
    cells: "list[str]" = []
    for _person in range(1000):
        value = forms.uuid(draw)
        value = value.upper() if written == "upper" else (f"{{{value}}}" if written == "braced" else value)
        cells += [value] * 20
    assert taxonomy.identifier_form_hold("record_token", cells, frozenset({""})) == taxonomy.HELD_TOKENS


@pytest.mark.parametrize("spelling", ["initial", "curly"])
def test_codex_item_2_names_beside_numbers_are_held_at_20000_rows(spelling: str) -> None:
    """REPAIR 2, CODEX ITEM 2 (the orchestrator's LANE CZ-A RULINGS 2 (2)): its two columns, read by the rule.

    A thousand made-up names (the zoo's name maker), each with a record
    number from 2000000 up on 20 rows, written `Lastname, F. [2000000]`
    or with a curly apostrophe, `O'Lastname, Firstname [2000000]`: read
    as no name before, published whole under a code reading; held now.
    The same spellings through the command at 20,000 rows are K-HZ-14's
    `band_label`.
    """
    import random

    draw = random.Random(7)
    cells: "list[str]" = []
    for person in range(1000):
        last, first, initial = forms._name(draw)
        written = (
            f"{last}, {initial}. [{2000000 + person}]" if spelling == "initial"
            else f"O{forms.CURLY_APOSTROPHE}{last}, {first} [{2000000 + person}]"
        )
        cells += [written] * 20
    assert taxonomy.identifier_form_hold("band_label", cells, frozenset({""})) == taxonomy.HELD_NAMES_WITH_NUMBERS


@pytest.mark.parametrize("pool", [forms.PLAN_CODES, forms.TEST_CODES, forms.KIT_CODES, zoo.PROC, zoo.HCPCS, zoo.PCS,
                                  zoo.NDC, zoo.RXNORM, zoo.LOINC, forms.PROCEDURE_LABELS])
def test_no_closed_list_of_codes_is_read_as_an_identifier_form(pool: "tuple[tuple[str, float], ...]") -> None:
    cells = [value for value, _weight in pool for _copy in range(30)]
    assert taxonomy.identifier_form_hold("code", cells, frozenset()) == ""


@pytest.mark.parametrize(("pool", "held"), [
    (forms.CATALOGUE_CODES, taxonomy.HELD_ACCESSIONS),
    (forms.ITEM_CODES, taxonomy.HELD_TOKENS),
    (forms.CONCEPT_CODES, taxonomy.HELD_LONG_NUMBERS),
    # ...and the zoo's own concept ids, two of sixteen figures and more in
    # an extension's namespace among them: one such cell holds the column.
    (zoo.SNOMED, taxonomy.HELD_LONG_NUMBERS),
])
def test_the_price_three_closed_lists_are_held_until_no(pool: "tuple[tuple[str, float], ...]", held: str) -> None:
    """THE PRICE, NAMED (the orchestrator's LANE CZ-A RULINGS 1 (2)): closed lists the forms' rule holds.

    Codes of three capitals, two figures, a dash and four figures read as
    accession numbers, of 32 small hexadecimal characters as tokens, of 16
    to 18 figures as long numbers: each column is put the Safe Harbor
    question and held until the person answers `no` (a `code` answer is no
    release). K-HZ-14 counts them at 20,000 rows (`false_alarms_freed_by_
    no`), owner lane CZ-A2.
    """
    cells = [value for value, _weight in pool for _copy in range(30)]
    assert taxonomy.identifier_form_hold("code", cells, frozenset()) == held


def test_a_held_form_is_put_its_question_with_its_own_words() -> None:
    from synthtwin import asking

    for hold, reason in zip(taxonomy.IDENTIFIER_FORM_HOLDS, asking.IDENTIFIER_FORM_REASONS):
        assert asking._HELD_BECAUSE[hold] == reason
        question = asking._safe_harbor_question("c", "free_text", reason, 1937)
        assert [choice.answer for choice in question.choices] == ["no", "yes"]
        assert question.taken == "yes"
    assert len(set(taxonomy.IDENTIFIER_FORM_HOLDS)) == len(taxonomy.IDENTIFIER_FORM_HOLDS) == 8


def test_codex_item_5_the_long_numbers_question_names_a_possible_identifier() -> None:
    """REPAIR 2, CODEX ITEM 5 (the orchestrator's LANE CZ-A RULINGS 2 (5)): the hold stays, the words say may be.

    A duration of 1000000000000000 nanoseconds is a measurement as long as
    a record number, so the question no longer says such numbers are no
    measurement and are a record number given to one person: it says they
    may be, or a measurement in small units, and holds the column until it
    is answered, its unanswered reading `yes`.
    """
    from synthtwin import asking

    question = asking._safe_harbor_question("c", "count", asking.BECAUSE_SAFE_HARBOR_LONG_NUMBERS, 1937)
    said = question.shape
    assert "may be a record, account or claim number given to one person" in said
    assert "a measurement counted in small units, such as a duration in nanoseconds" in said
    assert "exponent form" in said
    assert "which no measurement is" not in said and "number so long is a" not in said
    assert [choice.answer for choice in question.choices] == ["no", "yes"] and question.taken == "yes"
    assert taxonomy._forms_of_a_cell("1000000000000000") == (taxonomy.HELD_LONG_NUMBERS, 0)
    assert taxonomy.identifier_form_hold("duration_ns", ["1000000000000000"] * 30, frozenset()) == (
        taxonomy.HELD_LONG_NUMBERS)


# -- the forms through the command ----------------------------------------------------


def _questions_put(seen: "dict", column: str) -> "list[list[str]]":
    return seen["columns"][column]["asked"]  # type: ignore[no-any-return]


def _check(seen: "dict", runs: bool = True) -> None:
    """0 real values written, 0 twin cells equal to one, a question put to each identifier column.

    ``runs``: and 0 twin cells carrying a real value's run of five figures
    or more inside another (at 600 rows, where chance gives none; at 20,000
    a held column's made-up runs meet the real ones at chance, which K-HZ-14
    records beside its measurement).
    """
    assert seen["profile"] == 0 and seen["generate"] == 0, seen.get("screen")
    for column in forms.IDENTIFIERS[seen["kind"]]:
        counted = seen["columns"][column]
        what = f"{seen['kind']}.{column} at {seen['rows']} rows, {seen['mode']}: {counted}"
        assert counted["description_values"] == 0, what
        assert counted["twin_cells_equal"] == 0, what
        assert not runs or counted["twin_cells"] == 0, what
        offered = _questions_put(seen, column)
        assert any("identifier" in one or one == ["no", "yes"] for one in offered), what
        if seen["mode"] == "coded":
            assert counted["role"] == "identifier", what


@pytest.mark.parametrize("mode", ["unanswered", "coded"])
@pytest.mark.parametrize("kind", forms.KINDS)
def test_each_form_is_held_at_600_rows(tmp_path: pathlib.Path, kind: str, mode: str) -> None:
    _check(forms.measure(tmp_path, kind, 600, mode, small_tables_refused=False))


@pytest.mark.parametrize("mode", ["unanswered", "coded"])
def test_long_identifiers_in_a_workbook_are_held_as_text_of_their_widths(tmp_path: pathlib.Path, mode: str) -> None:
    """Form 8 written as an Excel workbook of text cells: held, and the twin's cells are text of 16 and 19 figures."""
    seen = forms.measure(tmp_path, forms.KIND_LONG, 600, mode, small_tables_refused=False, book=True)
    _check(seen)
    from synthtwin import reading

    twin = reading.read_table(f"{tmp_path / 'long_references-twin.xlsx'}")
    for column, width in (("claim_number", 16), ("order_number", 19)):
        cells = twin.columns[twin.column_names.index(column)]
        assert {len(cell) for cell in cells} == {width} and all(cell.isdigit() for cell in cells), column


def test_the_member_numbers_are_held_at_20000_rows(tmp_path: pathlib.Path) -> None:
    """THE ONE 20,000-ROW CASE (THE SUITE'S TIME rule): a thousand people, each number on 20 rows, read as codes."""
    seen = forms.measure(tmp_path, forms.KIND_MEMBER, zoo.KPI_ROWS, "coded")
    _check(seen, runs=False)
    assert seen["columns"]["member_id"]["people"] == 1000
    assert ["no", "yes"] in _questions_put(seen, "member_id")


def _lot_table(folder: pathlib.Path) -> pathlib.Path:
    """A hundred people on six rows each and a kit's lot named so, three lots each a third of the people's."""
    import csv

    folder.mkdir(parents=True, exist_ok=True)
    source = folder / "lots.csv"
    with open(source, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["patient_ref", "kit_lot", "charge"])
        for row in range(600):
            person = row % 100
            writer.writerow([forms.patient_ref(person), ("A20417", "B33018", "C40221")[person % 3], f"{row % 97 + 1}.50"])
    return source


def _answered(folder: pathlib.Path, source: pathlib.Path, harbor: str) -> "dict":
    """The patient key answered `identifier`, the lot `keep` to the person question and ``harbor`` to its Safe Harbor question."""
    seen: "dict" = {}
    for _round_of in range(3):
        document = json.loads((folder / "lots-questions.json").read_text(encoding="utf-8"))
        for entry in zoo._entries(document):
            offered = zoo._offered(entry)
            if entry.get("column") == "patient_ref" and "identifier" in offered:
                entry["your_answer"] = "identifier"
            elif entry.get("column") == "kit_lot" and sorted(offered) == ["no", "yes"]:
                entry["your_answer"] = harbor
            elif entry.get("column") == "kit_lot" and "keep" in offered:
                entry["your_answer"] = "keep"
        answers = folder / "lots-questions.json"
        answers.write_text(json.dumps(document), encoding="utf-8", newline="\n")
        seen = _round(folder, source, answers)
    return seen


@pytest.mark.parametrize(("harbor", "role"), [("no", "categorical"), ("yes", "identifier")])
def test_no_frees_a_form_and_yes_holds_it(tmp_path: pathlib.Path, harbor: str, role: str) -> None:
    """A column named as a device's lot, three lots each a third of the people's: held and asked; `no` frees it."""
    source = _lot_table(tmp_path)
    first = _round(tmp_path, source)
    block = [column for column in first["columns"] if column["name"] == "kit_lot"][0]
    assert block["role"] == "identifier"
    second = _answered(tmp_path, source, harbor)
    block = [column for column in second["columns"] if column["name"] == "kit_lot"][0]
    assert block["role"] == role
    answered = json.loads((tmp_path / "lots-questions.json").read_text(encoding="utf-8"))
    given = [entry for entry in answered.get("answered_before") or [] if entry.get("column") == "kit_lot"]
    assert [entry.get("your_answer") for entry in given][-1:] == [harbor]


def test_codex_item_3_a_later_refusal_counts_what_an_earlier_round_showed(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """REPAIR 2, CODEX ITEM 3 (the orchestrator's LANE CZ-A RULINGS 2 (3)): the measure counts before it returns.

    A harness whose first profile round passes and prints a real token on
    the screen, and whose answer round is then refused (as the person
    census refuses the device log, the accepted failing items): the
    measure returned before it counted, so the shown token read 0. It is
    counted now, and no twin is read.
    """
    import contextlib
    import io

    from synthtwin import cli

    real_main = cli.main
    shown: "list[str]" = []

    def refusing(arguments: "list[str]", **switches: object) -> int:
        if "--answers" in arguments:
            return 1
        code = real_main(arguments, **switches)  # type: ignore[arg-type]
        if arguments[0] == "profile":
            token = forms._column(pathlib.Path(arguments[1]), "record_token")[0]
            shown.append(token)
            print(f"a real value shown on the screen: {token}")
        return code

    monkeypatch.setattr(cli, "main", refusing)
    with contextlib.redirect_stdout(io.StringIO()):
        seen = forms.measure(tmp_path, forms.KIND_TOKENS, 300, "truthful", people=15, small_tables_refused=False)
    assert shown and seen["profile"] == 0 and seen["answers"] == 1 and seen["generate"] == -1, seen
    counted = seen["columns"]["record_token"]
    assert counted["description_values"] >= 1, counted
    assert counted["twin_cells"] == 0 and counted["twin_cells_equal"] == 0, counted


def test_codex_item_4_every_run_of_a_real_value_is_counted_by_the_chance_of_a_figure_run() -> None:
    """REPAIR 2, CODEX ITEM 4 (the orchestrator's LANE CZ-A RULINGS 2 (4)): the chance counter reads every run.

    The 20,000-row implant log holds the UDI `(01)00011782499301(17)
    261102(21)5382967221` (its people and lots since lane CZ-A2's fixture,
    plan P4-D469); a twin value `ZZ5382967221` holds its serial's ten
    figures. The counter that read a value whole and its longest run
    alone read 0; `carrying_runs` reads every run of five figures or more
    of each real value, inside a longer run too, on the real side and the
    controls' alike (`chance_of_runs` calls it for both).
    """
    import unanswered_identifier_shapes as shapes

    header, body = forms.device_numbers(zoo.KPI_ROWS, forms.SEED)
    place = header.index("device_udi")
    real = sorted({row[place] for row in body})
    udi = "(01)00011782499301(17)261102(21)5382967221"
    assert udi in real
    assert forms.figure_runs(udi) == ["00011782499301", "261102", "5382967221"]
    assert shapes.count_real([udi], [], ["ZZ5382967221"], linear=True)["twin_cells"] == 0
    assert forms.carrying_runs([udi], ["ZZ5382967221"]) == 1
    assert forms.carrying_runs(real, ["ZZ5382967221", "x9900011782499301", "ZZ53829672", "nothing"]) == 2


# -- a blank keeps a column held in people held -----------------------------------------


def _round(tmp_path: pathlib.Path, source: pathlib.Path, answers: "pathlib.Path | None" = None) -> "dict":
    import unanswered_identifier_shapes as shapes
    from synthtwin import cli

    import contextlib
    import io

    arguments = ["profile", f"{source}", "--replace"] + (["--answers", f"{answers}"] if answers else [])
    with shapes.nobody_at_the_keyboard(), contextlib.redirect_stdout(io.StringIO()), \
            contextlib.redirect_stderr(io.StringIO()):
        assert cli.main(arguments, small_tables_refused=False) == 0
    return json.loads((tmp_path / f"{source.stem}-profile.json").read_text(encoding="utf-8"))


def test_a_blank_keeps_a_column_held_in_people_held(tmp_path: pathlib.Path) -> None:
    """The zoo's labs at 600 rows: the result held in people while the person question is open stays held through a blank.

    Its own question (measurement, code or identifier) named `measurement`
    beside the hold, and once the person question was answered `keep` a
    blank kept that reading and published the column with its question
    open (the orchestrator's measurement, wave6/OQ); it names `identifier`
    now, and the blank keeps the column held.
    """
    table = zoo.table_named("labs")
    source = zoo.write_table(table, tmp_path, 600, zoo.seed_of(table))
    first = _round(tmp_path, source)
    roles = {f"{column['name']}": f"{column['role']}" for column in first["columns"]}
    assert roles["result_value"] == "identifier"
    questions = tmp_path / f"{source.stem}-questions.json"
    document = json.loads(questions.read_text(encoding="utf-8"))
    entries = zoo._entries(document)
    own = [entry for entry in entries if entry.get("column") == "result_value" and "identifier" in zoo._offered(entry)]
    assert own and all(entry["read_as_now"] == "identifier" for entry in own)
    for entry in entries:
        if zoo._asks_for_people(entry):
            entry["your_answer"] = "keep"
    questions.write_text(json.dumps(document), encoding="utf-8", newline="\n")
    second = _round(tmp_path, source, questions)
    roles = {f"{column['name']}": f"{column['role']}" for column in second["columns"]}
    assert roles["result_value"] == "identifier"


def test_a_blank_under_identifier_in_the_checklist_holds_where_no_person_column_counts_the_table(
    tmp_path: pathlib.Path,
) -> None:
    """THE BLANK'S OWN HOLD, pinned (skeptic 1 item 8; the orchestrator's LANE CZ-A RULINGS 1 (4)).

    A column of whole numbers read as a count is listed in the checklist
    under `measurement`, and a blank there keeps that reading. Where the
    column was held whole in people while the person question was open,
    `asking.held_back` wrote its entry under `identifier`; handed back
    blank once no person column counts the table, no open question holds
    it, so the blank alone does (`Answers.identities_held`, `cli`'s hold
    of a blank under `identifier`): the column is described as held record
    numbers until its entry is answered, and `measurement` frees it. The
    file handed back is the one synthtwin writes, its entry as the hold
    writes it. Mutant: `identities_held` emptied, the column published as
    a count with its entry blank.
    """
    import csv
    import random

    source = tmp_path / "counts.csv"
    draw = random.Random(11)
    with open(source, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["units", "visit_kind"])
        for _row in range(600):
            writer.writerow([f"{draw.randint(1, 60) * 5}", draw.choice(("Office", "Urgent", "Telehealth"))])
    first = _round(tmp_path, source)
    assert {f"{c['name']}": f"{c['role']}" for c in first["columns"]}["units"] == "count"
    questions = tmp_path / "counts-questions.json"
    document = json.loads(questions.read_text(encoding="utf-8"))
    listed = [entry for entry in document["checklist"]["columns"] if entry.get("column") == "units"]
    assert [entry["read_as_now"] for entry in listed] == ["measurement"]
    listed[0]["read_as_now"] = "identifier"
    questions.write_text(json.dumps(document), encoding="utf-8", newline="\n")
    held = _round(tmp_path, source, questions)
    assert {f"{c['name']}": f"{c['role']}" for c in held["columns"]}["units"] == "identifier"
    document = json.loads(questions.read_text(encoding="utf-8"))
    for entry in document["checklist"]["columns"]:
        if entry.get("column") == "units":
            entry["your_answer"] = "measurement"
    questions.write_text(json.dumps(document), encoding="utf-8", newline="\n")
    freed = _round(tmp_path, source, questions)
    assert {f"{c['name']}": f"{c['role']}" for c in freed["columns"]}["units"] == "count"


def test_a_form_the_count_in_a_declared_person_columns_people_holds_is_put_no_safe_harbor_question(
    tmp_path: pathlib.Path,
) -> None:
    """THE EXEMPTION OF 1bf4b295, pinned (skeptic 1 item 9; the orchestrator's LANE CZ-A RULINGS 1 (4)).

    The member numbers answered as the zoo answers them, the patient key
    `identifier`: the count in that column's people holds the member
    numbers whole already (plan P4-D406), so no answer could give one of
    their values back and no Safe Harbor question is added -- one round,
    the person question alone, nothing published. Mutant: the exemption
    withdrawn, the Safe Harbor question put and a second round asked.
    """
    seen = forms.measure(tmp_path, forms.KIND_MEMBER, 600, "truthful", small_tables_refused=False)
    counted = seen["columns"]["member_id"]
    assert counted["role"] == "identifier", counted
    assert counted["description_values"] == 0 and counted["twin_cells_equal"] == 0, counted
    assert ["no", "yes"] not in counted["asked"], counted["asked"]
    assert seen["rounds"] == 1, seen["rounds"]
