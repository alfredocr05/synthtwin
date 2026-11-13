"""P4-D478 (lane CZ-F): persons' names read from their values, and from a column name that says so; HIPAA first.

THE READER (`taxonomy.persons_names_hold`, asked last by
`taxonomy.safe_harbor_hold` on a role that publishes its levels): a column
whose different present values are, two in three or more, a person's name
written whole (`taxonomy.a_persons_name`), `taxonomy.NAMES_AT_LEAST` of them
or more (`HELD_PERSONS_NAMES`); or a column whose name says it holds a
person's name -- a patient's, a relative's or a clinician's
(`taxonomy.named_as_persons_names`) -- whose different values are, two in
three, a name written whole or one name word, whatever their number
(`HELD_NAMED_AS_PERSONS_NAMES`). Each held whole and put the one Safe
Harbor question with its own sentence, freed only by `no` or
`--identifier`.

THE CASES: every family of GENERATED names (`tests/persons_names_forms.py`,
a thousand a family) is read, and every family it must not read is not;
the named false alarms (procedure labels, ancestries, organisms, medicines,
departments, note types, countries) are not held, a county's name and a
column of a hundred labels or more in capitals that read as names are
(the stated price, freed by `no`); the edges of the rule (99 and 100
names, two in three by cells but not by values and the reverse,
placeholders and one-word values among the names); the column names that
say a name and those that do not (`drug_name`, `surgeon_specialty`,
`provider_npi`); each case red on its mutant -- the count floor, the
two-in-three share, the particle list, the heading list and the call in
`safe_harbor_hold`; the description at a test size names the column for
the command to hold, and beside a person column, and for zoo tables
holding no names, keeps its bytes; through the commands at 2,000 rows (a
test size) in every mode; and ONE 20,000-row case, the names column alone
at the owner's floor, unanswered (THE SUITE'S TIME rule). Every layout in
every mode at 20,000 rows, and the price over the whole zoo, are
K-HZ-30's (`tools/measurements/kpi_persons_names.py`, `kpi_run --slow`).

LANE CZ-F'S REPAIR (skeptic 1 and the statistics check): a health
message's name field (`FAMILY^GIVEN^M`, every filled and empty part), every
space and dash of the product's one definition (since batch 4s's merge,
`taxonomy._SCREEN_SPACE_RANGES` and `taxonomy._SCREEN_DASHES`) in every position, the
apostrophes, decomposed accents, a spaced hyphen, the particles added, a
two-letter family name given first and a title after the comma, each a
generated family; the different values read drawn from cells spread over
the whole column; the heading arm's participles, qualified roles and staff
headings, each with its control of ordinary labels, and a family name with
its initials under a clinician's heading; a names column beside an OPEN
person question keeps its bytes; each red on its mutant.

LANE CZ-F'S REPAIR 2 (Codex's review and the combined verify): under a
name that says a person's name, one or two family names are held as sixty
are, the flags' words not; every suffix the family-name reader reads, with
and without its point, in capitals and in small letters, after the family
name and after a comma, beside a particle, is read under such a name, each
with its controls; the cells are walked by a step that shares no factor
with their count, so a layout repeating every 12 rows is met in every
phase and labels at rows 48 j no longer fill the values read; a laboratory
and a pharmacy qualify only their technicians; K-HZ-30's counter reads
the decoded strings of a JSON file and the escapes of a text for the eye;
the question says the values read are a sample and names the name field
and the small words of a family name; each red on its mutant.

BATCH 4s'S MERGE (the orchestrator's LANE CODES-2 RULINGS 7 (4)): the
reader's spaces and dashes are the product's one definition -- over all
1,114,112 code points it reads a character as a space exactly where the
word screen does, as a dash exactly where `taxonomy._SCREEN_DASHES` names
it, and every other character as written, its old list of 35 spaces and
11 dashes held inside -- and a cell holding the soft hyphen U+00AD, a
space of that definition which the reader read as a dash, is read both
ways, each reading red on its mutant.
"""

from __future__ import annotations

import pathlib
import random

import pytest

import health_zoo as zoo
import persons_names_forms as names
from synthtwin import asking, profile, reading, taxonomy

_HOLDS = frozenset(taxonomy.PERSONS_NAMES_HOLDS)


def _hold(cells: "list[str]", name: str = "label", role: str = taxonomy.ROLE_CATEGORICAL) -> str:
    return taxonomy.persons_names_hold(name, role, cells, frozenset())


def _column(values: "list[str]", rows: int = 4000) -> "list[str]":
    """A column cycling through its values, every one on several rows."""
    return [values[row % len(values)] for row in range(max(rows, len(values)))]


def _made_up(count: int, seed: int, words: int = 1) -> "list[str]":
    """``count`` different made-up capitalised words, or phrases of ``words`` of them."""
    draw = random.Random(seed)
    made: "dict[str, bool]" = {}
    while len(made) < count:
        made[" ".join(names.made_up_word(draw, draw.choice((2, 3))) for _place in range(words))] = True
    return list(made)


# -- the reach at the unit level: every family generated, in thousands -----------


@pytest.mark.parametrize("family", names.FAMILIES_READ)
def test_every_generated_name_is_read(family: str) -> None:
    """Each family of names, a thousand spellings, read whole (`a_persons_name`)."""
    written = names.spellings(family)
    assert len(written) >= 1000, (family, len(written))
    missed = [text for text in written if not taxonomy.a_persons_name(text)]
    assert not missed, (family, len(missed), missed[:6])


@pytest.mark.parametrize("family", names.FAMILIES_NOT_READ)
def test_no_spelling_of_the_other_families_is_read(family: str) -> None:
    """Small letters alone, figures, five name words, names joined by a semicolon, scripts with no capitals, one word, a short word inside, past 60 characters: never a name written whole (the first four the reader's stated limits)."""
    written = names.spellings(family)
    assert len(written) >= 900, (family, len(written))
    read = [text for text in written if taxonomy.a_persons_name(text)]
    assert not read, (family, len(read), read[:6])


def test_the_particle_list_is_red_on_its_mutants(monkeypatch: pytest.MonkeyPatch) -> None:
    """THE PARTICLE LIST'S MUTANTS: with no particle, the names holding one go unread; with any short word a particle, `or`, `of`, `and` and `with` stand in a name."""
    particles = names.spellings("particles")
    inside = names.spellings("a_short_word_inside")
    monkeypatch.setattr(taxonomy, "_PERSONS_NAME_PARTICLES", frozenset())
    assert [text for text in particles if not taxonomy.a_persons_name(text)]
    monkeypatch.setattr(taxonomy, "_PERSONS_NAME_PARTICLES", frozenset({"or", "of", "and", "with"}))
    assert [text for text in inside if taxonomy.a_persons_name(text)]


@pytest.mark.parametrize("text", [
    "Cedar, Aaa", "O'Cedar, Aaa", "Aaa Cedar", "JUNIPERR, BHQ", "Cedar, A.", "CEDAR, AB", "Müller, Jürgen",
    "O’Brien, Sean", "al-Rashid, Omar", "Ludwig van Beethoven", "Smith Jr., John", "Dr. Okafor",
])
def test_the_named_shapes_are_read(text: str) -> None:
    """The shapes the public head published whole (lane CZ-A2's statistician), and their neighbours."""
    assert taxonomy.a_persons_name(text)


@pytest.mark.parametrize("text", [
    "Black or African American", "consult Cardiology", "Escherichia coli", "E. coli", "Lisinopril",
    "Fracture of Femur", "cedar, aaa", "Cedar, Aaa; Birch, Bbb", "Cedar 2, Aaa", "Progress note",
])
def test_the_named_false_alarms_are_no_name(text: str) -> None:
    """An ancestry (`or` is no particle), a service after a verb, organisms, a drug, a label with `of`, small letters, a list, a figure, a label in small letters after its first word."""
    assert not taxonomy.a_persons_name(text)


# -- the column: the count floor and the two-in-three share ----------------------------


def test_the_count_floor_99_and_100_names() -> None:
    """THE COUNT FLOOR: 99 different names are no column of names by their values, 100 are."""
    assert taxonomy.NAMES_AT_LEAST == 100
    assert _hold(_column(names.names_of(99, "comma"))) == ""
    assert _hold(_column(names.names_of(100, "comma"))) == taxonomy.HELD_PERSONS_NAMES


def test_the_count_floor_is_red_on_its_mutant(monkeypatch: pytest.MonkeyPatch) -> None:
    """THE COUNT FLOOR'S MUTANT: with a floor of one, 25 procedure labels written `Excision, Complete` are held."""
    procedures = [f"{word}, {other}" for word, other in zip(_made_up(25, 3), _made_up(25, 4))]
    assert _hold(_column(procedures)) == ""
    monkeypatch.setattr(taxonomy, "NAMES_AT_LEAST", 1)
    assert _hold(_column(procedures)) == taxonomy.HELD_PERSONS_NAMES


def _shared(name_values: int, other_values: int, name_rows: int, other_rows: int) -> "list[str]":
    named = names.names_of(name_values, "given_first")
    others = [f"code {place}" for place in range(other_values)]
    return [one for one in named for _row in range(name_rows)] + [one for one in others for _row in range(other_rows)]


def test_two_in_three_counts_values_not_cells() -> None:
    """THE SHARE: names on 94 per cent of the cells but 60 per cent of the values are no column of names; on 9 per cent of the cells but 80 per cent of the values they are."""
    assert _hold(_shared(150, 100, 10, 1)) == ""
    assert _hold(_shared(200, 50, 1, 40)) == taxonomy.HELD_PERSONS_NAMES


def test_the_share_is_red_on_its_mutant(monkeypatch: pytest.MonkeyPatch) -> None:
    """THE SHARE'S MUTANT: with one in three enough, names on 60 per cent of the values hold the column."""
    monkeypatch.setattr(taxonomy, "_BULK_TAKEN", 1)
    assert _hold(_shared(150, 100, 10, 1)) == taxonomy.HELD_PERSONS_NAMES


def test_placeholders_and_one_word_values_among_the_names() -> None:
    """A placeholder on a third of the rows and 300 family names alone beside 1,000 whole names: held; a placeholder named as absent is set aside."""
    whole = names.names_of(1000, "comma")
    single = names.names_of(300, "family", seed=7)
    cells = [one for one in whole for _row in range(10)] + single + ["UNKNOWN"] * 5000
    assert _hold(cells) == taxonomy.HELD_PERSONS_NAMES
    assert taxonomy.persons_names_hold("label", taxonomy.ROLE_CATEGORICAL, cells, frozenset({"UNKNOWN"})) == (
        taxonomy.HELD_PERSONS_NAMES
    )


@pytest.mark.parametrize("role", [taxonomy.ROLE_IDENTIFIER, taxonomy.ROLE_TEXT, taxonomy.ROLE_COUNT,
                                  taxonomy.ROLE_DATETIME])
def test_a_role_that_publishes_no_level_is_not_read(role: str) -> None:
    """Only a role that publishes its levels is read: a held identifier, free text, numbers and dates keep their bytes."""
    assert _hold(_column(names.names_of(300, "comma")), role=role) == ""


# -- the named false alarms at the column level, and the stated price ---------------------


@pytest.mark.parametrize(("label", "values"), [
    ("procedures, 25 labels written as a family name and a given name",
     [f"{word}, {other}" for word, other in zip(_made_up(25, 3), _made_up(25, 4))]),
    ("ancestries", ["White", "Black or African American", "Asian", "American Indian or Alaska Native",
                    "Native Hawaiian or Other Pacific Islander", "Other", "Unknown", "Declined"]),
    ("organisms, 150 written genus and species", [f"{genus} {species.lower()}" for genus, species in
                                                  zip(_made_up(150, 5), _made_up(150, 6))] + ["E. coli"]),
    ("medicines, mostly one word", _made_up(140, 7) + _made_up(40, 8, words=2)),
    ("departments and note types", ["Internal Medicine", "Progress Note", "Emergency Department", "Cardiology",
                                    "Discharge Summary", "consult Cardiology", "Operative Note", "Radiology"]),
    ("countries and languages, mostly one word", _made_up(120, 9) + _made_up(60, 10, words=2)),
])
def test_the_named_false_alarms_are_not_held(label: str, values: "list[str]") -> None:
    """The price at the unit level: labels of codes and categories the shape partly reads stay published (the count or the share)."""
    assert _hold(_column(values)) == "", label


def test_a_county_s_name_is_rightly_reached() -> None:
    """`Cook County` reads as a name: 150 different counties under a neutral name are held -- a county is a place smaller than a state, which the Safe Harbor question rightly reaches."""
    counties = [f"{word} County" for word in _made_up(150, 11)]
    assert _hold(_column(counties)) == taxonomy.HELD_PERSONS_NAMES


def test_a_hundred_labels_in_capitals_are_the_stated_price() -> None:
    """THE READER'S STATED PRICE: a column of 150 different labels of two capitalised words and no figure reads as names and is held until `no` frees it."""
    assert _hold(_column(_made_up(150, 12, words=2))) == taxonomy.HELD_PERSONS_NAMES


# -- the heading arm -------------------------------------------------------------------------


_NAMED_HEADINGS = (
    "patient_full_name", "last_nm", "LastName", "PatientLastName", "lname", "FNAME", "pt_nm", "mothers_maiden_name",
    "emergency_contact_name", "guarantor_name", "surgeon", "primary_surgeon", "Surgeon1", "attending_md",
    "ATTENDING_MD", "performed_by", "signed_by", "SurgeonName", "surgeonname", "anesthesiologist", "anesthetist",
    "referring_provider", "ordering_physician", "charge_nurse", "note_author", "reading_radiologist",
    "name_of_surgeon", "NAME_LAST", "name_first", "orderedby", "procedure_performed_by", "provider", "operator",
    "resident", "reader", "primary_care_provider", "anesthesia_provider", "provider_name", "signed",
    "name_of_provider",
)
_NOT_NAMED_HEADINGS = (
    "name", "drug_name", "assay_name", "item_name", "surgeon_specialty", "provider_kind", "resident_state",
    "surgeon_key", "provider_npi", "attending_code", "patient_label", "staff_label", "room", "nurse_unit",
    "imaging_tech", "billing_provider", "social_worker", "np", "pa",
)


@pytest.mark.parametrize("name", _NAMED_HEADINGS)
def test_a_name_that_says_a_person_s_name(name: str) -> None:
    """The heading arm's closed list: a part of a name, `name` after a person, or a clinician's role (the orchestrator's LANE CZ-F RULINGS 1 (2))."""
    assert taxonomy.named_as_persons_names(name)


@pytest.mark.parametrize("name", _NOT_NAMED_HEADINGS)
def test_a_name_that_says_no_person_s_name(name: str) -> None:
    """`name` alone or after a thing, and a role before another word: no person's name by the heading."""
    assert not taxonomy.named_as_persons_names(name)


@pytest.mark.parametrize(("name", "values", "held"), [
    ("surgeon", names.names_of(40, "comma"), True),
    ("attending_name", names.names_of(3, "given_first"), True),
    ("patient_surname", names.names_of(30, "family"), True),
    ("performed_by", ["Dr. Okafor", "Dr. Lindqvist", "Dr Mensah"], True),
    ("surgeon_key", [f"S{10000 + place}" for place in range(40)], False),
    ("provider_npi", [f"{1000000000 + 7919 * place}" for place in range(40)], False),
    ("signed", ["Yes", "No"], False),
    ("signed", ["Yes", "No", "Unknown"], False),
    ("resident", ["Resident", "Non-resident"], False),
    ("drug_name", _made_up(300, 13), False),
])
def test_the_heading_arm_reads_the_values_whatever_their_number(name: str, values: "list[str]", held: bool) -> None:
    """Under a name that says a person's name, two in three of the values a name written whole or a family name alone, however few: held; codes, numbers, a flag's words and a name that says no person: not."""
    found = _hold(_column(values), name=name)
    assert found == (taxonomy.HELD_NAMED_AS_PERSONS_NAMES if held else ""), (name, found)


def test_the_heading_list_is_red_on_its_mutant(monkeypatch: pytest.MonkeyPatch) -> None:
    """THE HEADING LIST'S MUTANT: with no clinician's role, no person beside `name` and no word naming a part of a name, 40 surgeons and 30 family names go unheld."""
    surgeons = _column(names.names_of(40, "comma"))
    families = _column(names.names_of(30, "family"))
    monkeypatch.setattr(taxonomy, "_CLINICIAN_ROLE_WORDS", frozenset())
    monkeypatch.setattr(taxonomy, "_NAME_OF_WORDS", frozenset())
    monkeypatch.setattr(taxonomy, "_NAME_HEADING_WORDS", frozenset())
    assert _hold(surgeons, name="surgeon") == ""
    assert _hold(families, name="patient_surname") == ""


# -- linear in the rows ----------------------------------------------------------------------


def test_each_different_value_is_read_once_up_to_the_bound(monkeypatch: pytest.MonkeyPatch) -> None:
    """ONE PASS: 200,000 different names read at most `_SAFE_HARBOR_MEMO` values; 20,000 different labels that are no name settle within the first third of that bound."""
    read: "list[str]" = []
    kind_of = taxonomy._persons_name_kind

    def counting(text: str, named: bool) -> int:
        read.append(text)
        return kind_of(text, named)

    monkeypatch.setattr(taxonomy, "_persons_name_kind", counting)
    many = [f"{name} {suffix}" for suffix in ("Aa", "Bb") for name in names.names_of(100000, "given_first")]
    assert _hold(many) == taxonomy.HELD_PERSONS_NAMES
    assert len(read) <= taxonomy._SAFE_HARBOR_MEMO
    read.clear()
    assert _hold([f"code {place}" for place in range(20000)]) == ""
    assert len(read) <= taxonomy._SAFE_HARBOR_MEMO // 3 + 1


# -- the description at a test size ---------------------------------------------------------


def _described(header: "list[str]", body: "list[list[str]]", folder: pathlib.Path) -> "tuple[str, dict[str, str]]":
    """The command's first description of a table: its text, and the columns named for the command to hold, with their holds."""
    path = folder / "t.csv"
    path.write_bytes(zoo.csv_bytes(header, body))
    reasons: "dict[str, str]" = {}
    document = profile.build_document(
        reading.read_table(f"{path}"), taxonomy.Settings(), [], top_code=True, five_figures=[], ages_held=[],
        harbor_year=taxonomy.SAFE_HARBOR_REFERENCE_YEAR, harbor_reasons=reasons, ages_established={},
    )
    from synthtwin import canonical

    return canonical.serialize(document), reasons


@pytest.mark.parametrize(("layout", "shape", "hold"), [
    ("alone", "comma", taxonomy.HELD_PERSONS_NAMES),
    ("alone", "mixed", taxonomy.HELD_PERSONS_NAMES),
    ("heading", "given_first", taxonomy.HELD_PERSONS_NAMES),
    ("surname", "family", taxonomy.HELD_NAMED_AS_PERSONS_NAMES),
    ("clinician", "comma", taxonomy.HELD_NAMED_AS_PERSONS_NAMES),
])
def test_the_description_names_the_column_for_the_command_to_hold(
    layout: str, shape: str, hold: str, tmp_path: pathlib.Path,
) -> None:
    """At 2,000 rows (the library path, a test size): the names column is named with its hold."""
    header, body, column, _real = names.table(layout, shape, 2000)
    _text, reasons = _described(header, body, tmp_path)
    assert reasons.get(column) == hold, reasons


def test_the_call_in_safe_harbor_hold_is_red_on_its_mutant(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """THE CALL'S MUTANT: with `persons_names_hold` away, the names column alone is named for nothing."""
    header, body, column, _real = names.table("alone", "comma", 2000)
    monkeypatch.setattr(taxonomy, "persons_names_hold", lambda name, role, cells, absent: "")
    _text, reasons = _described(header, body, tmp_path)
    assert column not in reasons, reasons


def _beside_a_declared_person(folder: pathlib.Path) -> "tuple[bytes, bytes, list[list[str]]]":
    """The names column beside its person column, the person question answered `identifier` (a person column declared): the description, the twin and the questions of the second run."""
    import json

    import unanswered_identifier_shapes as shapes
    from synthtwin import cli

    header, body, _column_name, _real = names.table("beside", "comma", 2000)
    folder.mkdir(parents=True, exist_ok=True)
    source = folder / "names.csv"
    source.write_bytes(zoo.csv_bytes(header, body))
    questions = folder / "names-questions.json"
    with shapes.nobody_at_the_keyboard():
        assert cli.main(["profile", f"{source}", "--replace"], small_tables_refused=False) == 0
        document = json.loads(questions.read_text(encoding="utf-8"))
        for entry in zoo._entries(document):
            if entry.get("column") == names.PERSON and zoo._asks_for_people(entry):
                entry["your_answer"] = "identifier"
        questions.write_text(json.dumps(document, indent=2), encoding="utf-8", newline="\n")
        assert cli.main(["profile", f"{source}", "--replace", "--answers", f"{questions}"],
                        small_tables_refused=False) == 0
        assert cli.main(["generate", f"{folder / 'names-profile.json'}", "--replace", "--seed", "0"],
                        small_tables_refused=False) == 0
    asked = [zoo._offered(entry) for entry in zoo._entries(json.loads(questions.read_text(encoding="utf-8")))
             if entry.get("column") == "patient_label"]
    return (folder / "names-profile.json").read_bytes(), (folder / "names-twin.csv").read_bytes(), asked


def test_beside_a_declared_person_column_the_column_keeps_its_bytes(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Beside a declared person column the names column is held in people and put no Safe Harbor question (`cli`'s rule for a column the people count holds whole): its description and twin are byte for byte those without the reader."""
    described, twin, asked = _beside_a_declared_person(tmp_path / "head")
    assert not asked, asked
    monkeypatch.setattr(taxonomy, "persons_names_hold", lambda name, role, cells, absent: "")
    assert _beside_a_declared_person(tmp_path / "away")[:2] == (described, twin)


@pytest.mark.parametrize("name", ["patients", "notes", "medication_administration", "appointments", "relatives"])
def test_zoo_tables_holding_no_name_keep_their_bytes(name: str, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Every column outside the names' shapes keeps its bytes: zoo tables at 600 rows are described byte for byte as without the reader."""
    table = zoo.table_named(name)
    header, body = table.build(zoo.SMOKE_ROWS, zoo.seed_of(table))
    path = tmp_path / f"{name}{table.suffix}"
    path.write_bytes(table.write(header, body))

    def described() -> str:
        from synthtwin import canonical

        reasons: "dict[str, str]" = {}
        document = profile.build_document(
            reading.read_table(f"{path}"), taxonomy.Settings(), [], top_code=True, five_figures=[], ages_held=[],
            harbor_year=taxonomy.SAFE_HARBOR_REFERENCE_YEAR, harbor_reasons=reasons, ages_established={},
        )
        assert not set(reasons.values()) & _HOLDS, reasons
        return canonical.serialize(document)

    text = described()
    monkeypatch.setattr(taxonomy, "persons_names_hold", lambda name, role, cells, absent: "")
    assert described() == text


# -- through the commands a person types ----------------------------------------------------


@pytest.mark.parametrize(("layout", "shape", "mode"), [
    ("alone", "comma", "unanswered"),
    ("alone", "apostrophe", "truthful"),
    ("alone", "capitals", "coded"),
    ("alone", "given_first", "no"),
    ("beside", "comma", "unanswered"),
    ("clinician", "comma", "unanswered"),
    ("alone", "comma", "typed"),
    ("alone", "caret", "measured"),
    ("alone", "zero_width", "unanswered"),
])
def test_the_bar_through_the_commands_at_2000_rows(layout: str, shape: str, mode: str, tmp_path: pathlib.Path) -> None:
    """Profile, its rounds of answers, generate and validate at 2,000 rows (100 people, a test size under the owner's floor): no real name shown or written, the column held and asked; `no` frees what its question offers."""
    seen = names.measure(tmp_path / f"{layout}-{mode}", layout, shape, 2000, mode, small_tables_refused=False)
    assert not names.failures(seen), (names.failures(seen), seen)
    if mode == "no":
        assert seen["shown"] and seen["twin_folded"], seen
    if layout != "beside" and mode == "unanswered":
        assert ["no", "yes"] in seen["asked"], seen  # type: ignore[operator]


def test_the_names_column_alone_at_20000_rows(tmp_path: pathlib.Path) -> None:
    """THE ONE 20,000-ROW CASE: 1,000 names, one a person on 20 rows, alone under a neutral name, unanswered, the table floor on."""
    seen = names.measure(tmp_path / "alone", "alone", "comma", zoo.KPI_ROWS, "unanswered")
    assert not names.failures(seen), (names.failures(seen), seen)
    assert ["no", "yes"] in seen["asked"], seen  # type: ignore[operator]
    assert seen["different_names"] == names.PEOPLE


# -- the question's words --------------------------------------------------------------------


@pytest.mark.parametrize(("hold", "words"), [
    (taxonomy.HELD_PERSONS_NAMES, "written as a person's name is written whole"),
    (taxonomy.HELD_NAMED_AS_PERSONS_NAMES, "its name says it holds a person's name"),
])
def test_each_hold_is_put_its_question_with_its_own_words(hold: str, words: str) -> None:
    """Each hold's reason and its sentence: what was seen, no value, `no` and `yes` offered, held until answered; and (repair 2, Codex's items 3 and 5) what was LOOKED AT -- every different value or a sample of 4,096 met in cells spread over the column -- and the shapes read, the name field cut at `^` and the small words of a family name among them."""
    reason = asking._HELD_BECAUSE[hold]
    assert reason in asking.PERSONS_NAMES_REASONS
    assert reason in asking.SH2_HELD_REASONS and reason in asking.SH2_SAFE_HARBOR_REASONS
    question = asking._safe_harbor_question("c", "categorical", reason, 1937)
    text = question.shape
    assert words in text and "held back" in text, text
    for looked_at in ("of its different values read -- every one, or, where it holds more than 4,096, a sample of "
                      "4,096 met in cells spread over the whole column --", "cut at ^", "such as de or van"):
        assert looked_at in text, (looked_at, text)
    assert taxonomy.PERSONS_NAMES_READ_AT_MOST == taxonomy._SAFE_HARBOR_MEMO == 4096
    assert sorted(choice.answer for choice in question.choices) == ["no", "yes"]


# -- lane CZ-F's repair: the reach closed by generated cases, each red on its mutant ---------------------------


_POSITIONS = (
    lambda last, given, mark: f"{last},{mark}{given}",
    lambda last, given, mark: f"{given}{mark}{last}",
    lambda last, given, mark: f"{mark}{last}, {given}",
    lambda last, given, mark: f"{last}, {given}{mark}",
    lambda last, given, mark: f"{last}, {mark} {given}",
    lambda last, given, mark: f"{last},{mark}{mark}{given}",
)


def _the_one_definition() -> "dict[str, str]":
    """Every space and dash of the product's one definition (batch 4s's merge): each code point the word screen reads as a space (`taxonomy._a_space_of_the_screen`, `taxonomy._SCREEN_SPACE_RANGES`), read as one, and each dash of `taxonomy._SCREEN_DASHES`, read as `-`."""
    marks = {chr(code): " " for code in range(0x110000) if taxonomy._a_space_of_the_screen(chr(code))}
    for character in taxonomy._SCREEN_DASHES:
        marks[character] = "-"
    return marks


def _unread_marks(marks: "dict[str, str]", each: int = 20) -> "list[str]":
    """Every space and dash of ``marks`` in every position, ``each`` names each: those left unread."""
    draw = random.Random(names.SEED)
    unread: "list[str]" = []
    for character, read_as in marks.items():
        for _name in range(each):
            last, other, given = (names.made_up_word(draw, 2) for _place in range(3))
            if read_as == " ":
                written = [position(last, given, character) for position in _POSITIONS]
            else:
                written = [f"{last}{character}{other}, {given}", f"{given} {last}{character}{other}",
                           f"{last} {character} {other}, {given}"]
            unread += [text for text in written if not taxonomy.a_persons_name(text)]
    return unread


def test_every_space_and_dash_of_the_one_definition_in_every_position_is_read(monkeypatch: pytest.MonkeyPatch) -> None:
    """ONE GENERATED CASE (skeptic 1 item 2; since batch 4s's merge, over the product's one definition): each of its 2,474 spaces -- the zero-width, format and control characters and the Unicode spaces -- in six positions, and each of its 11 dashes (10 at lane CZ-F's merge; the horizontal bar U+2015 joined at lane CZ-A2's) inside a double family name, is read, two names each; with the definition emptied, the zero-width and format characters and the dashes past ASCII go unread."""
    marks = _the_one_definition()
    spaces = {character for character, read_as in marks.items() if read_as == " "}
    assert len(spaces) == 2474 and len(marks) - len(spaces) == 11
    assert {"\u200b", "\u200e", "\ufeff", "\u2060", "\u00a0", "\u00ad", "\x01", "\u202e", "\U000e0041"} <= spaces
    assert {"\u2011", "\u2212", "\ufe58"} <= set(marks) - spaces
    assert not _unread_marks(marks, each=2)
    monkeypatch.setattr(taxonomy, "_a_space_of_the_screen", lambda character: False)
    monkeypatch.setattr(taxonomy, "_SCREEN_DASHES", "")
    unread = _unread_marks(marks, each=2)
    assert any("\u200b" in text for text in unread) and any("\u2011" in text for text in unread)


# The reader's own list of spaces and dashes before batch 4s's merge (lane
# CZ-F's repair, LANE CZ-F RULINGS 2 (3)), written out: 35 spaces, and 11
# dashes -- those of `_SSN_MARKS` that are no space, U+FE58 and the soft hyphen.
_SPACES_BEFORE_THE_MERGE = (
    "\t\n\x0b\x0c\r\x1c\x1d\x1e\x1f\x85\xa0\u1680\u2000\u2001\u2002\u2003\u2004\u2005\u2006"
    "\u2007\u2008\u2009\u200a\u2028\u2029\u202f\u205f\u3000\u200b\u200c\u200d\u200e\u200f\u2060\ufeff"
)
_DASHES_BEFORE_THE_MERGE = "-\u2013\u2014\u2010\u2011\u2012\u2212\ufe63\uff0d\ufe58\u00ad"


def test_the_readers_spaces_and_dashes_are_the_one_definition_over_every_code_point() -> None:
    """THE GENERATED AGREEMENT CASE OF BATCH 4s'S MERGE (the orchestrator's LANE CODES-2 RULINGS 7 (4)): over all 1,114,112 code points the reader of persons' names reads a character as a space exactly where the word screen does -- its predicate (`_a_space_of_the_screen`) and its own reader of words (`_words_of`) alike --, as `-` exactly where `_SCREEN_DASHES` names it, as a straight apostrophe exactly where `_PERSONS_NAME_APOSTROPHES` does, and every other character as written; no character is two of these; the reader's own list before the merge is held inside, each character read as it read it but the soft hyphen, a space now read both ways (`_name_readings`). MUTANTS (run at the merge): the reader's list before the merge, or a dash definition holding the soft hyphen, is red here."""
    every = "".join(chr(code) for code in range(0x110000))
    read = taxonomy._name_read(every)
    assert len(read) == len(every) == 1114112
    dashes = frozenset(taxonomy._SCREEN_DASHES)
    apostrophes = frozenset(taxonomy._PERSONS_NAME_APOSTROPHES)
    spaces = frozenset(code for code in range(0x110000) if taxonomy._a_space_of_the_screen(every[code]))
    both = sorted(hex(code) for code in spaces if every[code] in dashes or every[code] in apostrophes)
    both += sorted(hex(ord(character)) for character in dashes & apostrophes)
    wrong = [
        hex(code) for code in range(0x110000)
        if read[code] != (" " if code in spaces else "-" if every[code] in dashes else "'" if every[code] in apostrophes else every[code])
    ]
    assert not both and not wrong, (both[:20], wrong[:20])
    assert len(spaces) == 2474 and len(dashes) == 11  # the horizontal bar U+2015 joined at lane CZ-A2's merge
    # ...and the word screen's own reader of words cuts at exactly those spaces: every code point once, each after an
    # `A`, read in one text -- its words joined are the text without them, one more word than there are spaces.
    written = "".join("A" + character for character in every) + "A"
    kept = "".join("A" + ("" if code in spaces else every[code]) for code in range(0x110000)) + "A"
    words = taxonomy._words_of(written)
    cut_alike = len(words) == len(spaces) + 1 and "".join(words) == kept
    assert cut_alike, "the word screen cuts a text at a character that is no space of the definition, or not at one that is"
    assert all(taxonomy._a_space_of_the_screen(character) for character in _SPACES_BEFORE_THE_MERGE)
    assert [character for character in _DASHES_BEFORE_THE_MERGE if character not in dashes] == ["\u00ad"]
    assert taxonomy._a_space_of_the_screen("\u00ad") and taxonomy._name_readings("Aaa\u00adCedar") == ("Aaa Cedar", "Aaa-Cedar")
    assert taxonomy._name_readings("Aaa Cedar") == ("Aaa Cedar",)


def test_the_soft_hyphen_is_read_as_a_space_and_as_a_dash(monkeypatch: pytest.MonkeyPatch) -> None:
    """BATCH 4s'S MERGE: the soft hyphen U+00AD is a space of the product's one definition, one that prints nothing, and was this reader's dash, so a cell holding one is read both ways and the stronger reading kept: `<U+00AD>Cedar, Aaa`, `Cedar<U+00AD>, Aaa` and `Aaa<U+00AD>Cedar` are names only as a space, `O<U+00AD>Cedar, Aaa` and `Aaa d<U+00AD>Cedar` only as a dash, 20 names each, and 300 of each held under a neutral name; EACH READING'S MUTANT leaves its own forms unread and unheld."""
    soft = "\u00ad"
    draw = random.Random(names.SEED)
    as_space: "list[str]" = []
    as_dash: "list[str]" = []
    for _name in range(20):
        last, given = names.made_up_word(draw, 2), names.made_up_word(draw, 2)
        as_space += [f"{soft}{last}, {given}", f"{last}{soft}, {given}", f"{given}{soft}{last}"]
        as_dash += [f"O{soft}{last}, {given}", f"{given} d{soft}{last}"]
    assert all(taxonomy.a_persons_name(text) for text in as_space + as_dash)
    whole = names.names_of(300, "comma")
    space_column = _column([f"{soft}{one}" for one in whole])
    dash_column = _column([f"O{soft}{one}" for one in whole])
    assert _hold(space_column) == taxonomy.HELD_PERSONS_NAMES and _hold(dash_column) == taxonomy.HELD_PERSONS_NAMES
    with monkeypatch.context() as patched:
        patched.setattr(taxonomy, "_name_readings", lambda text: (text.replace(soft, " "),))
        assert all(taxonomy.a_persons_name(text) for text in as_space)
        assert not [text for text in as_dash if taxonomy.a_persons_name(text)]
        assert _hold(dash_column) == ""
    with monkeypatch.context() as patched:
        patched.setattr(taxonomy, "_name_readings", lambda text: (text.replace(soft, "-"),))
        assert all(taxonomy.a_persons_name(text) for text in as_dash)
        assert not [text for text in as_space if taxonomy.a_persons_name(text)]
        assert _hold(space_column) == ""


def test_the_caret_family_covers_every_part_filled_or_empty() -> None:
    """A health message's name field (skeptic 1 item 1): parts 3 to 7 in each of their 32 patterns, in capitals and in mixed case, each read whole; a coded value with figures, a fourth part that is no suffix and a family name alone are not."""
    draw = random.Random(names.SEED)
    for pattern in names.CARET_PATTERNS:
        for capitals in (True, False):
            written = [names.caret_spelling(draw, pattern, capitals) for _name in range(30)]
            assert all(taxonomy.a_persons_name(text) for text in written), (pattern, capitals, written[:3])
    for text in ("2345-7^Glucose^LN", "CEDAR^AAA^B^ZZTOP", "CEDAR^^^", "CEDAR,AAA^B", "^AAA^B", "cedar^aaa"):
        assert not taxonomy.a_persons_name(text), text


def test_the_caret_form_is_red_on_its_mutant(monkeypatch: pytest.MonkeyPatch) -> None:
    """THE CARET'S MUTANT: with the name field read as no name, 300 names `CEDAR^AAA^B` alone and three under `person_name` go unheld."""
    alone = _column(names.names_of(300, "caret"))
    few = _column(names.names_of(3, "caret"))
    assert _hold(alone) == taxonomy.HELD_PERSONS_NAMES
    assert _hold(few, name="person_name") == taxonomy.HELD_NAMED_AS_PERSONS_NAMES
    monkeypatch.setattr(taxonomy, "_caret_name_kind", lambda text: taxonomy._NOT_A_NAME)
    assert _hold(alone) == "" and _hold(few, name="person_name") == ""


@pytest.mark.parametrize(("family", "mutant", "value"), [
    ("apostrophe_variants", "_PERSONS_NAME_APOSTROPHES", "'"),
    ("decomposed_accents", "_COMBINING_MARKS", ()),
    ("more_particles", "_PERSONS_NAME_PARTICLES", frozenset({"van", "von", "de", "la", "le"})),
])
def test_each_family_of_the_repair_is_red_on_its_mutant(
    family: str, mutant: str, value: object, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """THE APOSTROPHES', THE COMBINING MARKS' AND THE PARTICLES' MUTANTS (skeptic 1 item 5 (d)): each family's generated names read, and some go unread without its list."""
    written = names.spellings(family)
    assert all(taxonomy.a_persons_name(text) for text in written)
    monkeypatch.setattr(taxonomy, mutant, value)
    assert [text for text in written if not taxonomy.a_persons_name(text)]


def test_a_degree_after_one_word_is_a_family_name(monkeypatch: pytest.MonkeyPatch) -> None:
    """`Minh Do` and `Lin Pa` are names (skeptic 1 item 5 (d)); `Ann Lee Do`, `Smith, John MD` and `John Smith, MD` keep their degree; THE MUTANT reading a degree after one word leaves the first two unread."""
    for text in ("Minh Do", "Lin Pa", "Ann Lee Do", "Smith, John MD", "John Smith, MD", "Cedar, Mrs. Aaa",
                 "GARCIA Y LOPEZ, JUAN", "Aaa von und zu Cedar", "Cedar - Birch, Aaa", "Mu\u0308ller, Jo"):
        assert taxonomy.a_persons_name(text), text
    monkeypatch.setattr(taxonomy, "_a_degree_after", lambda tokens, comma: len(tokens) > 1 and (
        taxonomy._without_points(tokens[-1]) in taxonomy._PERSONS_NAME_DEGREES
        or taxonomy._without_points(tokens[-1]) in taxonomy._PERSONS_NAME_SUFFIXES))
    assert not taxonomy.a_persons_name("Minh Do") and not taxonomy.a_persons_name("Lin Pa")


def test_an_era_at_the_column_s_start_does_not_fill_the_bound() -> None:
    """THE SPREAD (skeptic 1 item 4): 206,000 cells in date order, 5,000 people in small letters on 10 rows each, then 12,000 written `Family, Given` on 13 rows each -- 0.706 of the different values names -- are held, as the same cells shuffled are; read in row order the small letters filled the bound and the column was not held."""
    whole = names.names_of(15000, "comma")
    early = [one.lower() for one in whole[:5000]]
    cells = [one for one in early for _row in range(10)] + [one for one in whole[3000:] for _row in range(13)]
    assert len(cells) == 206000
    assert _hold(cells) == taxonomy.HELD_PERSONS_NAMES
    shuffled = list(cells)
    random.Random(5).shuffle(shuffled)
    assert _hold(shuffled) == taxonomy.HELD_PERSONS_NAMES


# The column names of skeptic 1's item 3 and the statistics check's item 1:
# a thing performed, ordered or signed, a payer or a service, a machine's
# operator, a place's residents, a card's reader -- each holding 40
# invented labels, 25 payers' names or a flag's words.
_THINGS = (
    "procedure_performed", "test_ordered", "lab_ordered", "medication_ordered", "diet_ordered", "study_ordered",
    "imaging_ordered", "exam_performed", "block_performed", "consent_signed", "date_signed", "insurance_provider",
    "service_provider", "home_health_provider", "PROCEDURE_PERFORMED", "TestOrdered", "machine_operator",
    "procedure_operator", "county_resident", "city_resident", "state_resident", "card_reader", "badge_reader",
    "insurance_provider_name", "service_provider_name", "INSURANCEPROVIDERNAME", "PROCEDUREPERFORMED", "row_rn",
)


@pytest.mark.parametrize("name", _THINGS)
def test_a_thing_performed_ordered_or_provided_is_no_person(name: str) -> None:
    """No person's name by the heading: 40 invented labels of one to three capitalised words, 25 payers and three flag words under it are not held."""
    assert not taxonomy.named_as_persons_names(name)
    labels = _made_up(40, 21, words=1)[:15] + _made_up(15, 22, words=2) + _made_up(10, 23, words=3)
    for values in (labels, _made_up(25, 24, words=2), ["Signed", "Not Signed", "Pending"],
                   ["Referred", "Not Referred", "Declined"], ["Northside", "Lakeview", "Cedarbrook"]):
        assert _hold(_column(values), name=name) == "", (name, values[:3])


def test_the_participle_and_qualifier_rules_are_red_on_their_mutants(monkeypatch: pytest.MonkeyPatch) -> None:
    """THE MUTANTS: a participle or a qualified role read as a clinician's role after any word names `procedure_performed`, `insurance_provider` and `county_resident`; with no qualifier, `referring_provider` names no person."""
    assert taxonomy.named_as_persons_names("referring_provider")
    monkeypatch.setattr(taxonomy, "_CLINICIAN_ROLE_WORDS", taxonomy._CLINICIAN_ROLE_WORDS
                        | taxonomy._PARTICIPLE_ROLE_WORDS | taxonomy._QUALIFIED_ROLE_WORDS)
    assert all(taxonomy.named_as_persons_names(name) for name in
               ("procedure_performed", "insurance_provider", "county_resident"))
    monkeypatch.undo()
    monkeypatch.setattr(taxonomy, "_CLINICIAN_QUALIFIERS", frozenset())
    assert not taxonomy.named_as_persons_names("referring_provider")


# The staff headings of skeptic 1's item 5 (b), added to the closed list
# (and `circulator`, `anesthesia_provider`, which the orchestrator's LANE
# CZ-F RULINGS 2 (6)(b) names beside them).
_STAFF_HEADINGS = (
    "doctor", "doctor_name", "dr_name", "prescriber", "prescriber_name", "practitioner", "practitioner_name",
    "therapist", "technician", "tech_name", "pharmacist", "midwife", "consultant", "hospitalist", "intensivist",
    "cardiologist", "dentist", "perfusionist", "first_assistant", "scrub_tech", "administered_by", "entered_by",
    "documented_by", "verified_by", "collected_by", "reviewed_by", "dictated_by", "cosigned_by",
    "employee_name", "staff_name", "user_name", "ordering_md", "crna", "circulator", "anesthesia_provider",
    # ...and, closing the class (the stopping rule): the clinician of a
    # visit, an appointment or a patient, a sign-off's other participles, and
    # the forms in capitals with no mark between their words.
    "servicing_provider", "encounter_provider", "visit_provider", "appointment_provider", "assigned_provider",
    "responsible_provider", "patient_provider", "recorded_by", "charted_by", "witnessed_by", "completed_by",
    "attested_by", "transcribed_by", "dispensed_by", "created_by", "updated_by", "modified_by", "edited_by",
    "changed_by", "PRIMARYSURGEON", "ATTENDINGPHYSICIAN", "REFERRINGPROVIDER", "CHARGENURSE", "PERFORMEDBY",
    "rn", "rn_name", "circulating_rn", "scrub_rn", "relief_rn", "lpn", "cna", "rnfa",
)


def _ordinary_labels() -> "list[str]":
    """Forty labels a staff heading could hold that name no person: roles, sources, services, statuses."""
    made = _made_up(10, 31)
    return [
        "Self", "Nurse", "Patient", "Caregiver", "Family Member", "Charge Nurse", "Home Health Aide", "Parent",
        "Pharmacist", "Physician", "Student Nurse", "Staff", "System", "Interface", "Patient Portal", "Device",
        "Outside Lab", "Unassigned", "Internal Medicine", "Cardiology", "General Surgery", "Pediatrics",
        "Obstetrics", "Neurosurgery", "Anesthesia", "Emergency", "Critical Care", "Physical Therapy",
        "Not Signed", "Signed", "Pending", "Declined",
    ] + [f"{made[place]} {('Clinic', 'Service', 'Unit', 'Department', 'Center')[place % 5]}" for place in range(8)]


@pytest.mark.parametrize("name", _STAFF_HEADINGS)
def test_a_staff_heading_holds_names_and_not_its_ordinary_labels(name: str) -> None:
    """Each staff heading added (skeptic 1 item 5 (b)): 40 invented names under it are held; its control, 40 ordinary labels such a column could hold, is not."""
    assert taxonomy.named_as_persons_names(name)
    assert _hold(_column(names.names_of(40, "comma")), name=name) == taxonomy.HELD_NAMED_AS_PERSONS_NAMES
    labels = _ordinary_labels()
    assert len(set(labels)) == 40
    assert _hold(_column(labels), name=name) == ""


def test_the_role_and_service_words_are_red_on_their_mutant(monkeypatch: pytest.MonkeyPatch) -> None:
    """THE MUTANT: with no word of a role, a source, a service or a status, the 40 ordinary labels under `administered_by` and `surgeon` are held."""
    monkeypatch.setattr(taxonomy, "_ROLE_AND_SERVICE_WORDS", frozenset())
    monkeypatch.setattr(taxonomy, "_SERVICE_ENDINGS", ())
    monkeypatch.setattr(taxonomy, "_NOT_PERSONS_NAME_WORDS", frozenset())
    for name in ("administered_by", "surgeon"):
        assert _hold(_column(_ordinary_labels()), name=name) == taxonomy.HELD_NAMED_AS_PERSONS_NAMES


def test_a_family_name_and_its_initials_under_a_clinician_s_heading(monkeypatch: pytest.MonkeyPatch) -> None:
    """`Smith J`, `Smith J.`, `SMITH J`, `Smith J.A.` (skeptic 1 item 5 (c)): 60 under `surgeon` are held; under a neutral name, 60 and 150 are not (`Vitamin D`, `Stage I` have the shape); THE MUTANT with no such form leaves `surgeon` unheld."""
    draw = random.Random(names.SEED)
    written = list(dict.fromkeys(
        draw.choice((f"{word} {letter}", f"{word} {letter}.", f"{word.upper()} {letter}", f"{word} {letter}.A.",
                     f"{word} {letter} A"))
        for word, letter in ((names.made_up_word(draw, 2), draw.choice(names.INITIALS)) for _name in range(600))
    ))
    assert len(written) >= 150
    assert _hold(_column(written[:60]), name="surgeon") == taxonomy.HELD_NAMED_AS_PERSONS_NAMES
    assert _hold(_column(written[:60]), name="staff_label") == ""
    assert _hold(_column(written[:150])) == ""
    assert not [text for text in written if taxonomy.a_persons_name(text) and " A" not in text]
    monkeypatch.setattr(taxonomy, "_a_family_name_and_initials", lambda text: False)
    assert _hold(_column(written[:60]), name="surgeon") == ""


def test_one_whole_name_among_codes_under_a_clinician_s_heading_is_not_held(monkeypatch: pytest.MonkeyPatch) -> None:
    """THE HEADING ARM'S SHARE (skeptic 1 item 7 (a)): `surgeon` with one whole name among 40 codes is not held; THE MUTANT with no share holds it."""
    values = ["Okafor, Ade"] + [f"S{10000 + place}" for place in range(40)]
    assert _hold(_column(values), name="surgeon") == ""
    monkeypatch.setattr(taxonomy, "_BULK_TAKEN", 0)
    assert _hold(_column(values), name="surgeon") == taxonomy.HELD_NAMED_AS_PERSONS_NAMES


def _surnames_beside_a_declared_person() -> "tuple[str, dict[str, str]]":
    """`patient_surname` beside a declared person column, 300 people on four rows: 20 common family names held by 14 or 15 people each, and 10 rare ones held by one each; described as the command's first description does."""
    from synthtwin import canonical

    common = names.names_of(20, "family", seed=11)
    rare = names.names_of(10, "family", seed=12)
    header = ["patient_key", "patient_surname"]
    body: "list[list[str]]" = []
    for who in range(300):
        surname = rare[who] if who < 10 else common[who % 20]
        body += [[f"{100000 + who}", surname] for _row in range(4)]
    with __import__("tempfile").TemporaryDirectory() as folder:
        path = pathlib.Path(folder) / "t.csv"
        path.write_bytes(zoo.csv_bytes(header, body))
        reasons: "dict[str, str]" = {}
        document = profile.build_document(
            reading.read_table(f"{path}"), taxonomy.Settings(), ["patient_key"], subjects=["patient_key"],
            top_code=True, five_figures=[], ages_held=[], harbor_year=taxonomy.SAFE_HARBOR_REFERENCE_YEAR,
            harbor_reasons=reasons, ages_established={},
        )
    return canonical.serialize(document), reasons


def test_common_family_names_beside_a_declared_person_keep_lane_pl_s_reason(monkeypatch: pytest.MonkeyPatch) -> None:
    """THE PROFILE BRANCH (skeptic 1 item 7 (b)): beside a declared person column, family names common enough to publish keep the few-people hold's own reason, and the description its bytes, as without the reader; reverted, the reason is the heading arm's."""
    text, reasons = _surnames_beside_a_declared_person()
    assert reasons.get("patient_surname") == taxonomy.HELD_LEVELS_OF_FEW_PEOPLE, reasons
    monkeypatch.setattr(taxonomy, "persons_names_hold", lambda name, role, cells, absent: "")
    assert _surnames_beside_a_declared_person() == (text, reasons)


def _beside_an_open_person_question(folder: pathlib.Path) -> "tuple[bytes, bytes, list[list[str]]]":
    """The names column beside its person column, nobody answering (the person question open): the description, the twin and the questions put to the names column."""
    import json

    import unanswered_identifier_shapes as shapes
    from synthtwin import cli

    header, body, column, _real = names.table("beside", "comma", 2000)
    folder.mkdir(parents=True, exist_ok=True)
    source = folder / "names.csv"
    source.write_bytes(zoo.csv_bytes(header, body))
    with shapes.nobody_at_the_keyboard():
        assert cli.main(["profile", f"{source}", "--replace"], small_tables_refused=False) == 0
        assert cli.main(["generate", f"{folder / 'names-profile.json'}", "--replace", "--seed", "0"],
                        small_tables_refused=False) == 0
    questions = json.loads((folder / "names-questions.json").read_text(encoding="utf-8"))
    asked = [zoo._offered(entry) for entry in zoo._entries(questions) if entry.get("column") == column]
    return (folder / "names-profile.json").read_bytes(), (folder / "names-twin.csv").read_bytes(), asked


def test_beside_an_open_person_question_the_column_keeps_its_bytes(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Skeptic 1 item 6: beside a person column whose question is open, the names column the people count holds is put no Safe Harbor question that run, its description and twin byte for byte those without the reader; the question follows once the person question is answered `keep` (K-HZ-30's coded items)."""
    described, twin, asked = _beside_an_open_person_question(tmp_path / "head")
    assert not [one for one in asked if one == ["no", "yes"]], asked
    monkeypatch.setattr(taxonomy, "persons_names_hold", lambda name, role, cells, absent: "")
    assert _beside_an_open_person_question(tmp_path / "away")[:2] == (described, twin)


def test_a_names_column_the_people_count_does_not_hold_is_held_and_asked(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """...and one the count in people does not hold whole is described again, held as before and asked its Safe Harbor question: here the second description is forced by reading the first as if that count had not held it."""
    import json

    import unanswered_identifier_shapes as shapes
    from synthtwin import cli

    real = profile.build_document
    rounds: "list[list[str]]" = []

    def build(*arguments: object, **named: object) -> object:
        document = real(*arguments, **named)  # type: ignore[arg-type]
        counted = named.get("counted_in_subjects")
        held = named.get("unanswered") or []
        if named.get("subjects") and isinstance(counted, list) and isinstance(held, list):
            rounds.append(list(held))
            if names.COLUMN["beside"] in counted:
                counted.remove(names.COLUMN["beside"])
        return document

    monkeypatch.setattr(profile, "build_document", build)
    header, body, column, real_names = names.table("beside", "comma", 2000)
    source = tmp_path / "names.csv"
    source.write_bytes(zoo.csv_bytes(header, body))
    with shapes.nobody_at_the_keyboard():
        assert cli.main(["profile", f"{source}", "--replace"], small_tables_refused=False) == 0
    assert len(rounds) == 2 and column not in rounds[0] and column in rounds[1], rounds
    questions = json.loads((tmp_path / "names-questions.json").read_text(encoding="utf-8"))
    assert ["no", "yes"] in [zoo._offered(entry) for entry in zoo._entries(questions) if entry.get("column") == column]
    text = (tmp_path / "names-profile.json").read_text(encoding="utf-8")
    assert not [name for name in real_names if name in text]


def test_a_specialty_s_name_is_no_name_under_a_staff_heading() -> None:
    """Thirty one-word services under `consultant` -- made-up stems ending as a specialty's name does (`-ology`, `-iatry`, `-iatrics`, `-ics`, `-surgery`, `-medicine`) -- are not held; 30 family names alone there are."""
    stems = [word.lower() for word in _made_up(30, 41)]
    endings = ("ology", "iatry", "iatrics", "ics", "surgery", "medicine")
    services = [f"{stem.capitalize()}{endings[place % len(endings)]}" for place, stem in enumerate(stems)]
    assert _hold(_column(services), name="consultant") == ""
    assert _hold(_column(names.names_of(30, "family")), name="consultant") == taxonomy.HELD_NAMED_AS_PERSONS_NAMES


def _run_together(name: str) -> str:
    """A column's name in capitals with no mark between its words."""
    return "".join(character for character in name if character.isalpha()).upper()


def test_a_name_run_together_in_capitals_reads_as_written_apart(monkeypatch: pytest.MonkeyPatch) -> None:
    """ONE GENERATED CASE (the unseparated forms of the orchestrator's LANE CZ-F RULINGS 1 (2)): every heading of the gate's lists, written in capitals with no mark between its words, says a person's name exactly where it does written apart (`PATIENTLASTNAME`, `PRIMARYSURGEON`, `REFERRINGPROVIDER`; never `INSURANCEPROVIDER`, `PROCEDUREPERFORMED`, `ITEMNAME`, `PANELNAME`); THE MUTANTS: read whole, the first go unread; with a part of a name written short after another word, `ITEMNAME` and `PANELNAME` name a person."""
    named = (*_NAMED_HEADINGS, *_STAFF_HEADINGS, "PatientLastName", "pt_last_name", "subscriber_last_name",
             "guarantor_last_name", "surgeon_last_name", "next_of_kin_name", "circulating_nurse")
    apart = (*_NOT_NAMED_HEADINGS, *_THINGS, "panel_name", "dept_name", "concept_name", "model_name", "level_name")
    assert not [name for name in named if not taxonomy.named_as_persons_names(_run_together(name))]
    assert not [name for name in apart if taxonomy.named_as_persons_names(_run_together(name))]
    for name in ("PATIENTLASTNAME", "PRIMARYSURGEON", "REFERRINGPROVIDER", "EMERGENCYCONTACTNAME", "NEXTOFKINNAME"):
        assert taxonomy.named_as_persons_names(name), name
    monkeypatch.setattr(taxonomy, "_run_together_read", lambda word: [word])
    assert not [name for name in ("PATIENTLASTNAME", "PRIMARYSURGEON", "REFERRINGPROVIDER", "CHARGENURSE")
                if taxonomy.named_as_persons_names(name)]
    monkeypatch.undo()
    monkeypatch.setattr(taxonomy, "_NAMES_WRITTEN_SHORT", frozenset())
    assert taxonomy.named_as_persons_names("ITEMNAME") and taxonomy.named_as_persons_names("PANELNAME")


def test_family_names_under_a_name_run_together_are_held(monkeypatch: pytest.MonkeyPatch) -> None:
    """30 family names alone under `PERSONLASTNAME` are held, as under `person_last_name`; 30 payers' names under `INSURANCEPROVIDERNAME` are not; THE MUTANT reading such a name whole leaves the first unheld."""
    families = _column(names.names_of(30, "family"))
    assert _hold(families, name="PERSONLASTNAME") == taxonomy.HELD_NAMED_AS_PERSONS_NAMES
    assert _hold(families, name="person_last_name") == taxonomy.HELD_NAMED_AS_PERSONS_NAMES
    assert _hold(_column(_made_up(30, 24, words=2)), name="INSURANCEPROVIDERNAME") == ""
    monkeypatch.setattr(taxonomy, "_run_together_read", lambda word: [word])
    assert _hold(families, name="PERSONLASTNAME") == ""


def test_a_qualified_role_before_name_counts_only_first_or_after_a_qualifier(monkeypatch: pytest.MonkeyPatch) -> None:
    """`provider_name`, `referring_provider_name` and `patient_provider_name` say a clinician's name; `insurance_provider_name` and `service_provider_name` do not; THE MUTANT reading a qualified role anywhere before `name` names the last two."""
    for name in ("provider_name", "referring_provider_name", "patient_provider_name", "primary_care_provider_name"):
        assert taxonomy.named_as_persons_names(name), name
    for name in ("insurance_provider_name", "service_provider_name", "machine_operator_name"):
        assert not taxonomy.named_as_persons_names(name), name
    monkeypatch.setattr(taxonomy, "_a_role_before", lambda words, place: place > 0 and taxonomy._a_role_word(
        words[place - 1]))
    assert taxonomy.named_as_persons_names("insurance_provider_name")
    assert taxonomy.named_as_persons_names("service_provider_name")


def test_the_qualifiers_and_participles_added_are_red_on_their_mutant(monkeypatch: pytest.MonkeyPatch) -> None:
    """THE MUTANT: with the build's qualifiers, qualified roles and participles alone, `visit_provider`, `servicing_provider`, `recorded_by`, `created_by`, `rn` and `circulating_rn` name no person."""
    added = ("visit_provider", "servicing_provider", "recorded_by", "created_by", "rn", "circulating_rn")
    assert all(taxonomy.named_as_persons_names(name) for name in added)
    monkeypatch.setattr(taxonomy, "_CLINICIAN_QUALIFIERS", taxonomy._CLINICIAN_QUALIFIERS - frozenset({
        "servicing", "encounter", "visit", "appointment", "assigned", "responsible", "patient", "pt", "circulating",
        "relief"}))
    monkeypatch.setattr(taxonomy, "_QUALIFIED_ROLE_WORDS", taxonomy._QUALIFIED_ROLE_WORDS - frozenset({
        "rn", "rns", "lpn", "cna", "rnfa"}))
    monkeypatch.setattr(taxonomy, "_PARTICIPLE_ROLE_WORDS", taxonomy._PARTICIPLE_ROLE_WORDS - frozenset({
        "recorded", "charted", "witnessed", "completed", "attested", "transcribed", "dispensed", "created",
        "updated", "modified", "edited", "changed"}))
    assert not [name for name in added if taxonomy.named_as_persons_names(name)]


# -- lane CZ-F's repair 2: Codex's review and the combined verify --------------------------------------------


_FEW_HEADINGS = ("patient_surname", "surgeon", "PERSONLASTNAME")


@pytest.mark.parametrize("name", _FEW_HEADINGS)
def test_one_or_two_family_names_under_a_heading_are_held(name: str) -> None:
    """CODEX'S ITEM 1: under a name that says a person's name, one family name on every row, two in turn, three and sixty are held -- the minimum of three name words is withdrawn; the flags' words are no name, alone or in pairs (`Yes`, `Yes` and `No`, `Unknown`, `None` and `Other`, `N/A`): not held."""
    families = names.names_of(60, "family", seed=31)
    roles = {1: taxonomy.ROLE_CONSTANT, 2: taxonomy.ROLE_BINARY}
    for count in (1, 2, 3, 60):
        cells = _column(families[:count], rows=600)
        found = _hold(cells, name=name, role=roles.get(count, taxonomy.ROLE_CATEGORICAL))
        assert found == taxonomy.HELD_NAMED_AS_PERSONS_NAMES, (name, count, found)
    for flags in (["Yes"], ["Yes", "No"], ["Unknown"], ["None", "Other"], ["N/A"], ["Self"], ["Pending", "Signed"]):
        assert _hold(_column(flags, rows=600), name=name, role=roles.get(len(flags), taxonomy.ROLE_CATEGORICAL)) == ""


def test_every_suffix_the_family_name_reader_reads_is_read_under_a_heading() -> None:
    """CODEX'S ITEM 2, ONE GENERATED CASE: every suffix the family-name reader reads (`suffix_forms`: 240 ways, with and without its point, a first capital, capitals and small letters, after the family name and after a comma, beside a particle, the family name in capitals or not), 60 family names each, under `patient_surname`: held; ITS CONTROLS, not held: the same values under a neutral name, and the same suffix after a family name holding a figure."""
    families = names.names_of(60, "family", seed=33)
    forms = names.suffix_forms()
    assert len(forms) == 240
    unread: "list[str]" = []
    for form in forms:
        written = [names.with_suffix(family, form) for family in families]
        if _hold(_column(written, rows=600), name="patient_surname") != taxonomy.HELD_NAMED_AS_PERSONS_NAMES:
            unread += [written[0]]
        assert _hold(_column(written, rows=600), name="patient_label") == "", written[0]
        coded = [names.with_suffix(f"{family[:2]}{place % 10}{family[2:]}", form) for place, family in enumerate(families)]
        assert _hold(_column(coded, rows=600), name="patient_surname") == "", coded[0]
    assert not unread, (len(unread), unread[:8])


def test_a_family_name_alone_is_read_as_the_family_name_reader_reads_it() -> None:
    """The family-name reader's one definition (`taxonomy._a_name_suffix`, `_a_family_name_read`): a suffix after a family name alone or after its comma, particles before it, up to three name words in capitals (`VAN CEDAR, JR.`), and the name field's suffix part, are a family name alone; a suffix alone, a flag's word with a suffix and four name words are not."""
    for text in ("Cedar Jr.", "Cedar, Jr.", "cedar".capitalize() + " sr", "van Cedar, iii", "VAN CEDAR, JR.",
                 "de la Cruz Birch", "CEDAR^^^JR", "CEDAR BIRCH^^^", "O'Cedar IV."):
        assert taxonomy._a_family_name_alone(text), text
    for text in ("Jr.", "Unknown Jr.", "Yes, Jr.", "van", "Cedar, Aaa, Jr.", "Cedar Birch Oak Elm, Jr.", "cedar jr."):
        assert not taxonomy._a_family_name_alone(text), text
    assert all(taxonomy._a_name_suffix(word) for word in ("Jr.", "JR", "jr", "Sr.", "II", "iii", "IV."))


def _walked_blocks() -> "list[str]":
    """49,152 cells in blocks of 12: the first cell of each one of 1,400 names written in small letters, the 11 others names written `Family, Given`, 4,096 of them on 11 rows each (74.5 per cent of the different values names)."""
    whole = names.names_of(4096 + 1400, "comma", seed=43)
    small = [one.lower() for one in whole[4096:]]
    people = [one for one in whole[:4096] for _row in range(11)]
    random.Random(44).shuffle(people)
    cells: "list[str]" = []
    for block in range(4096):
        cells += [small[block % 1400]] + people[block * 11: block * 11 + 11]
    return cells


def test_the_walk_meets_every_phase_of_a_layout_repeating_every_12_rows() -> None:
    """THE COMBINED VERIFY'S ITEM 1 (the orchestrator's LANE CZ-F RULINGS 5 (1)): blocks of 12 rows, a name in small letters first and 11 names after it, are held whichever row the column starts at -- the step of the rows over 4,096 met only the small letters and settled the column unheld."""
    cells = _walked_blocks()
    assert len(cells) == 49152
    for shift in (0, 1, 5, 11):
        assert _hold(cells[shift:] + cells[:shift]) == taxonomy.HELD_PERSONS_NAMES, shift


def test_labels_at_rows_48_j_no_longer_fill_the_values_read() -> None:
    """CODEX'S ITEM 3 IN THE OTHER DIRECTION: 4,096 capitalised two-word labels at rows 48 j among 10,000 code labels in small letters, 200,000 rows -- 29.06 per cent of the different values name-shaped -- are not held; with the step of the rows over 4,096 the values read were the 4,096 labels alone, and the column was held."""
    labels = [f"{one} {other}" for one, other in zip(names.names_of(4096, "family", seed=41),
                                                   names.names_of(4096, "family", seed=42))]
    codes = [f"code{place:05d} item" for place in range(10000)]
    cells: "list[str]" = []
    for row in range(200000):
        cells += [labels[row // 48] if row % 48 == 0 and row // 48 < 4096 else codes[(row - row // 48 - 1) % 10000]]
    assert round(len(set(labels)) / len(set(cells)), 4) == 0.2906
    assert _hold(cells) == ""


def test_the_walk_reads_each_cell_once(monkeypatch: pytest.MonkeyPatch) -> None:
    """THE WALK (`taxonomy._walk_step`): its step shares no factor with the cells' count, so it reads every cell once -- every count from 1 to 600 and a few to 4,095 cell by cell, and the step's factor at the counts of the layouts above and at 2,000,000 rows."""
    import math

    read: "list[str]" = []

    def reading(text: str, named: bool) -> int:
        read.append(text)
        return taxonomy._A_NAME_WRITTEN_WHOLE

    monkeypatch.setattr(taxonomy, "_persons_name_kind", reading)
    for total in [*range(1, 601), 1009, 1024, 2048, 2187, 3000, 4095]:
        read.clear()
        cells = [f"v{place}" for place in range(total)]
        _hold(cells)
        assert sorted(read) == sorted(cells), total
    for total in (4096, 49152, 116400, 200000, 206000, 2000000):
        step = taxonomy._walk_step(total)
        assert 1 <= step < total and math.gcd(step, total) == 1, (total, step)


def test_a_laboratory_or_a_pharmacy_qualifies_only_its_technicians() -> None:
    """THE COMBINED VERIFY'S ITEM 2 (the orchestrator's LANE CZ-F RULINGS 5 (2)): a laboratory's or a pharmacy's provider, operator or reader is the laboratory or the pharmacy itself -- `lab_provider`, `laboratory_provider`, `pharmacy_provider` and their `_name` forms, each holding 12 one-word organisations, are named no person and not held; their technicians, `lab_tech`, `pharmacy_tech`, `laboratory_techs`, `PHARMACYTECH`, still are."""
    organisations = names.names_of(12, "family", seed=51)
    for name in ("lab_provider", "laboratory_provider", "pharmacy_provider", "lab_provider_name",
                 "laboratory_provider_name", "pharmacy_provider_name", "LABPROVIDER", "lab_operator", "pharmacy_reader"):
        assert not taxonomy.named_as_persons_names(name), name
        assert _hold(_column(organisations), name=name) == "", name
    for name in ("lab_tech", "pharmacy_tech", "laboratory_techs", "PHARMACYTECH", "lab_tech_name"):
        assert taxonomy.named_as_persons_names(name), name
        assert _hold(_column(names.names_of(40, "comma")), name=name) == taxonomy.HELD_NAMED_AS_PERSONS_NAMES


_ESCAPED_NAMES = ("Cedar,\tAaa", "Birch,\nBbb", "Maño, Ccc", "Oak,​Ddd")


def _escaped_seen(texts: "list[str]") -> "dict[str, int]":
    return {key: value for key, value in names.counted(list(_ESCAPED_NAMES), texts, []).items() if key.startswith("shown")}


def test_the_counter_reads_decoded_json_strings_and_escaped_text() -> None:
    """CODEX'S ITEM 4 (K-HZ-30's counter, `persons_names_forms.published_texts`): a name holding a tab, a line break, a letter past ASCII or a zero-width space stands in a JSON file as `\\t`, `\\n` or `\\u....`, and in a text for the eye as `\\x09` or `\\u200b`; read through the decoded strings of the JSON, keys and values, and the escapes of the text decoded and folded, every one is found."""
    import json

    document = json.dumps({"columns": [{"levels": {name: 200 for name in _ESCAPED_NAMES}, "note": ["x"]}]})
    assert all(name not in document for name in _ESCAPED_NAMES)
    assert _escaped_seen(names.published_texts(document, True))["shown"] == len(_ESCAPED_NAMES)
    display = "values: cedar,\\x09aaa (200), birch,\\x0abbb (200), ma\\xf1o, ccc (200), oak,\\u200bddd (200)"
    assert _escaped_seen(names.published_texts(display, False))["shown_folded"] == len(_ESCAPED_NAMES)
    assert names.published_texts("plain words", False) == ["plain words"]


def test_the_counter_s_old_re_encoding_is_red(monkeypatch: pytest.MonkeyPatch) -> None:
    """THE COUNTER'S MUTANT, the re-encoding it replaces (`json.dumps(json.loads(text))`, the text for the eye read as written): the tab's, the line break's and the zero-width space's names are missed."""
    import json

    monkeypatch.setattr(names, "published_texts", lambda text, json_file: (
        [text, json.dumps(json.loads(text), ensure_ascii=False)] if json_file else [text]))
    document = json.dumps({"levels": {name: 200 for name in _ESCAPED_NAMES}})
    assert _escaped_seen(names.published_texts(document, True))["shown"] < len(_ESCAPED_NAMES)
    display = "values: cedar,\\x09aaa (200), birch,\\x0abbb (200)"
    assert _escaped_seen(names.published_texts(display, False))["shown_folded"] == 0


@pytest.mark.parametrize(("layout", "shape", "mode"), [
    ("few_surname", "one", "coded"),
    ("suffix_surname", "suffix_jr", "typed"),
])
def test_few_and_suffixed_family_names_through_the_commands_at_2000_rows(
    layout: str, shape: str, mode: str, tmp_path: pathlib.Path,
) -> None:
    """Codex's items 1 and 2 through profile, its answers, generate and validate at 2,000 rows (a test size): one family name on every row under `patient_surname`, a reading that publishes asked for it; 60 family names each followed by ` Jr.`, `--code` typed: no real name shown or written, the column held and asked."""
    seen = names.measure(tmp_path / f"{layout}-{mode}", layout, shape, 2000, mode, small_tables_refused=False)
    assert not names.failures(seen), (names.failures(seen), seen)
    assert ["no", "yes"] in seen["asked"], seen  # type: ignore[operator]
