"""The value readers' forms (plan P4-D472, lane CZ-E): seven shapes the zoo did not test, each an invented look-alike.

Every table here is written from scratch by this module's own makers and
seed (`SEED`), with generic column names; no value is copied from
anywhere, and every name is made up of syllables (`made_up_word`). Each
KIND is one table, several rows a person, 1,000 people on 20 rows each
at the KPI size (20,000 rows) and 100 at the suite's 600 rows; a kind
whose name ends in `_cases` is the same rows with no patient column, so
the command counts rows (one row a case):

1. `typed_remarks`: short remarks a person types, in four columns:
   remarks holding no identifier written for many people
   (`remark_plain`); remarks written for many people, each holding ONE
   identifier form (`remark_shared`: a month and a day, a telephone
   number, a run of seven to nine figures, a title before a name,
   initials, a relative's name, a family name and an initial); the same
   forms written for one to three people each (`remark_rare`); all three
   kinds in one column (`remark_mixed`); and remarks holding a name the
   readers do not read (`remark_open`: a name written first), the
   residual, measured and recorded.
2. `name_lists`: lists of names in one cell, `Last, F; Last, F`, cut at
   30 characters as a narrow export cuts them: a team's list written for
   many people (`team_common`), lists drawn per case (`team_rare`), and
   each person's own one or two companions (`companions`); and lists of
   `LAST, FIRST` names (`team_given`).
3. `name_labels`: a note template naming a clinician (`note_template`,
   `Dr <name> pre-op note` beside plain templates), and a case label
   opening with the patient's family name and initials (`case_label`,
   `SURNAME, KT - <procedure>` and `Surname, K.T. <procedure>`); and the
   residual: templates opening with a bare family name (`template_open`)
   and labels `Surname KT <procedure>` (`label_open`).
4. `area_codes`: a census tract's eleven figures with the state's
   leading nought (`area_a`), a block group's twelve (`area_b`), a
   tract's ten figures where a state of one figure lost its nought
   (`area_c`), and an area's rank of 1 to 10 beside them (`area_rank`).
5. `point_pairs`: a latitude and a longitude in one cell, with a comma
   (`point_pair`), a space (`point_spaced`) or in brackets
   (`point_wrapped`), a person's home or one of eight shared sites; and
   the same two numbers in two columns under neutral names (`point_n`,
   `point_e`).
6. `node_addresses`: four dotted groups (`node_dotted`), colon groups
   around `::` (`node_colon`) and a device's hardware address
   (`node_hardware`): six shared by many rows, one a person's device.
7. `age_bands`: each person's age as a five-year band (`age_band`,
   `90-94`, `95-99`, `100-104`), as band text whose bands widen
   (`band_text`, `18-44 yrs`, `90-94 yrs`, `>= 95 yrs`), as a ten-year
   band (`band_ten`, `90-99`, `100+`), as display text whose unit
   changes (`age_shown`) and its unit key (`age_key`).

THE REPAIRS' KINDS (`REPAIR_KINDS`, `REPAIR2_KINDS`) widen these: band
tops and schemes, odd marks, telephone numbers and date ranges, addresses
and points among words and among labels, the price kind of plain clinical
labels; and at the second repair visit remarks whose dates share days
(`seen_dates`, with a patient column and one row a case), adult age
groups (`adult_groups`) and values holding an identifier on exactly the
floor's eleven rows (`floor_forms_cases`).

THE FORMS each cell holds are kept in `META` beside the table (each
placed cell, its form, and the strings it counts as), so a measure
counts each form's real values in what the commands write
(`measure`). A column's forms the readers hold are `HELD_FORMS`; the
residual forms (`OPEN_FORMS`) are recorded, never failed.
"""

from __future__ import annotations

import contextlib
import io
import json
import pathlib
import random
import time

import health_zoo as zoo
import safe_harbor_forms as forms

SEED = 20261110
ROWS_A_PERSON = 20
SMOKE_PEOPLE = 100
# The seed step of a control table, whose values the twin never read.
CONTROL_SEED_STEP = 7919

KIND_REMARKS = "typed_remarks"
KIND_NAME_LISTS = "name_lists"
KIND_NAME_LABELS = "name_labels"
KIND_AREA_CODES = "area_codes"
KIND_POINT_PAIRS = "point_pairs"
KIND_NODE_ADDRESSES = "node_addresses"
KIND_AGE_BANDS = "age_bands"
KIND_SERIALS = "device_serials"
BASE_KINDS = (
    KIND_REMARKS, KIND_NAME_LISTS, KIND_NAME_LABELS, KIND_AREA_CODES,
    KIND_POINT_PAIRS, KIND_NODE_ADDRESSES, KIND_AGE_BANDS, KIND_SERIALS,
)
# The kinds measured without their patient column too (one row a case).
CASE_KINDS = (KIND_REMARKS, KIND_NAME_LISTS, KIND_NAME_LABELS, KIND_POINT_PAIRS, KIND_NODE_ADDRESSES, KIND_AGE_BANDS,
              KIND_SERIALS)
CASES = "_cases"

# META[(kind, n, seed, people)] = {column: {cell: (form, (needle, ...))}}
META: "dict[tuple[str, int, int, int | None], dict[str, dict[str, tuple[str, tuple[str, ...]]]]]" = {}

_HEADS = "bdfgjklmnprstvz"
_VOWELS = "aeiou"
_TAILS = "lmnrst"
CAPITALS = "ABCDEFGHJKLMNPRSTVW"


def made_up_word(draw: random.Random, syllables: int) -> str:
    """A made-up name of ``syllables`` syllables, capitalised: `Bolumet`."""
    written = ""
    for _place in range(syllables):
        written += draw.choice(_HEADS) + draw.choice(_VOWELS)
    return (written + draw.choice(_TAILS)).capitalize()


def _people(n: int, people: "int | None") -> int:
    return people if people else max(n // ROWS_A_PERSON, SMOKE_PEOPLE)


def _rows_of(order: "list[int]", count: int) -> "list[list[int]]":
    rows_of: "list[list[int]]" = [[] for _place in range(count)]
    for row, person in enumerate(order):
        rows_of[person] += [row]
    return rows_of


def _note(meta: dict, column: str, cell: str, form: str, needles: "tuple[str, ...]") -> None:
    meta.setdefault(column, {})[cell] = (form, tuple(needle for needle in needles if needle))


def _case(row: int) -> str:
    """The case's own number, every row one: what a table with no patient column counts its rows by."""
    return f"C{5000000 + row}"


# -- 1. typed remarks ------------------------------------------------------------

PLAIN_REMARKS = (
    "awaiting transport", "room not ready", "labs pending", "consent pending", "late arrival", "imaging delayed",
    "bed assigned", "weather delay", "insurance review", "case added", "patient declined", "seen in ED",
    "moved to Holding", "awaiting OR",
)
FORM_DATE = "date"
FORM_PHONE = "phone"
FORM_FIGURES = "figures"
FORM_TITLE = "title"
FORM_INITIALS = "initials"
FORM_RELATIVE = "relative"
FORM_FAMILY = "family_initial"
FORM_GIVEN = "family_given"
FORM_NAMES = "names"
FORM_SURNAME_LABEL = "surname_initials"
FORM_TEMPLATE = "named_template"
FORM_AREA = "area"
FORM_POINT = "point"
FORM_NODE = "node"
FORM_OVER_89 = "over89"
FORM_SERIAL = "serial"
# The residual forms the readers do not read (plan P4-D472's stated
# limits): recorded, never failed.
FORM_NAME_FIRST = "name_first"
FORM_BARE_TEMPLATE = "bare_template"
FORM_LABEL_NO_COMMA = "label_no_comma"
OPEN_FORMS = (FORM_NAME_FIRST, FORM_BARE_TEMPLATE, FORM_LABEL_NO_COMMA)
REMARK_FORMS = (FORM_DATE, FORM_PHONE, FORM_FIGURES, FORM_TITLE, FORM_INITIALS, FORM_RELATIVE, FORM_FAMILY)
REMARK_TEMPLATES = {
    FORM_DATE: ("moved to {x}", "rescheduled to {x}", "resume on {x}", "seen {x} in clinic", "postponed until {x}"),
    FORM_PHONE: ("call {x} if rash", "{x} cell", "callback {x}", "reach at {x}"),
    FORM_FIGURES: ("ref {x} on file", "acct {x} on hold", "auth {x} pending", "claim {x} sent"),
    FORM_TITLE: ("per Dr {x}", "Mrs {x} notified", "Mr. {x} declined", "Dr {x} to review"),
    FORM_INITIALS: ("consent by {x}", "per {x} (wife)", "pt {x} declined", "{x} at bedside"),
    FORM_RELATIVE: ("per daughter {x}", "son {x} at bedside", "wife {x} notified", "husband {x} to drive"),
    FORM_FAMILY: ("seen by {x}", "per {x} today", "{x} to sign"),
    FORM_NAME_FIRST: ("{x} to call back", "{x} called", "{x} will drive"),
}
_MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")


def _date_written(draw: random.Random) -> "tuple[str, tuple[str, ...]]":
    """A made-up month and day as a remark writes it: `3/14`, `03/14/31`, `Mar 14`, `14-Mar`, `2031-03-14`."""
    month, day = draw.randint(1, 12), draw.randint(1, 28)
    style = draw.randrange(5)
    if style == 0:
        written = f"{month}/{day}"
    elif style == 1:
        written = f"{month:02d}/{day:02d}/{draw.randint(25, 35)}"
    elif style == 2:
        written = f"{_MONTHS[month - 1]} {day}"
    elif style == 3:
        written = f"{day}-{_MONTHS[month - 1]}"
    else:
        written = f"20{draw.randint(25, 35)}-{month:02d}-{day:02d}"
    return written, (written,)


def _phone_written(draw: random.Random) -> "tuple[str, tuple[str, ...]]":
    """A made-up telephone number in the 555 exchange, in one of five layouts."""
    area, line = draw.randint(201, 989), draw.randint(100, 199)
    style = draw.randrange(5)
    written = (
        f"({area}) 555-0{line}", f"{area}-555-0{line}", f"{area}.555.0{line}", f"{area} 555 0{line}",
        f"+1 {area} 555 0{line}",
    )[style]
    return written, (written,)


def _identifier(form: str, draw: random.Random, given: "list[str]", family: "list[str]") -> "tuple[str, tuple[str, ...]]":
    """One made-up identifier of a form as a remark writes it, and the strings it counts as."""
    if form == FORM_DATE:
        return _date_written(draw)
    if form == FORM_PHONE:
        return _phone_written(draw)
    if form == FORM_FIGURES:
        written = f"{draw.randint(1, 9)}" + "".join(f"{draw.randint(0, 9)}" for _place in range(draw.choice((6, 7, 8))))
        return written, (written,)
    if form == FORM_TITLE:
        last = draw.choice(family)
        return last, (last,)
    if form == FORM_INITIALS:
        written = f"{draw.choice(CAPITALS)}.{draw.choice(CAPITALS)}."
        return written, (written,)
    if form == FORM_FAMILY:
        last = draw.choice(family)
        written = f"{last}, {draw.choice(CAPITALS)}"
        return written, (written, last)
    first, last = draw.choice(given), draw.choice(family)
    return f"{first} {last}", (first, last)


def _remark(form: str, draw: random.Random, given: "list[str]", family: "list[str]") -> "tuple[str, tuple[str, ...]]":
    inner, needles = _identifier(form, draw, given, family)
    return draw.choice(REMARK_TEMPLATES[form]).format(x=inner), needles


def typed_remarks(n: int, seed: int, people: "int | None" = None) -> "tuple[list[str], list[list[str]]]":
    """Cases, several a person, with five remark columns (the module's first kind)."""
    draw = random.Random(seed)
    count = _people(n, people)
    names = random.Random(seed + 11)
    given = forms._distinct(names, 300, lambda d: made_up_word(d, 2))
    family = forms._distinct(names, 600, lambda d: made_up_word(d, 3))
    order = forms._person_rows(n, draw, count)
    rows_of = _rows_of(order, count)
    meta: dict = {}
    columns = {name: [""] * n for name in ("remark_plain", "remark_shared", "remark_rare", "remark_mixed", "remark_open")}
    weights = [1.0 / (rank + 1) for rank in range(len(PLAIN_REMARKS))]
    for row in range(n):
        if draw.random() < 0.5:
            columns["remark_plain"][row] = draw.choices(PLAIN_REMARKS, weights)[0]
    holders = (12, 15, 25, 60, 150, 300)
    seen: "set[str]" = set()

    def deal(column: str, cell: str, how_many: int, rows_each: "tuple[int, ...]") -> None:
        # ...each of ``how_many`` people holds the cell on one row or more, a
        # person whose rows are all taken passed over for the next: a remark
        # dealt to twelve people is held by twelve (the statistics check of
        # lane CZ-E, item 3: one dealt so was held by ten, and the few-people
        # rule, not the readers, held its column).
        placed = 0
        for person in draw.sample(range(count), count):
            if placed >= how_many:
                break
            free = [row for row in rows_of[person] if not columns[column][row]]
            if not free:
                continue
            for row in draw.sample(free, min(draw.choice(rows_each), len(free))):
                columns[column][row] = cell
            placed += 1

    def fresh(form: str) -> "tuple[str, tuple[str, ...]]":
        while True:
            cell, needles = _remark(form, draw, given, family)
            if cell not in seen:
                seen.add(cell)
                return cell, needles

    for column in ("remark_shared", "remark_mixed"):
        for place_form, form in enumerate(REMARK_FORMS):
            for place in range(3):
                cell, needles = fresh(form)
                _note(meta, column, cell, form, needles)
                deal(column, cell, holders[(place * 2 + place_form) % len(holders)], (1, 2, 3))
    for column in ("remark_rare", "remark_mixed"):
        for form in REMARK_FORMS:
            for _place in range(40):
                cell, needles = fresh(form)
                _note(meta, column, cell, form, needles)
                deal(column, cell, draw.choice((1, 1, 1, 2, 3)), (1, 2, 3, 5, 8, 12, 20))
    for place in range(9):
        cell, needles = fresh(FORM_NAME_FIRST)
        _note(meta, "remark_open", cell, FORM_NAME_FIRST, needles)
        deal("remark_open", cell, holders[place % len(holders)], (1, 2, 3))
    for row in range(n):
        if not columns["remark_mixed"][row] and draw.random() < 0.6:
            columns["remark_mixed"][row] = draw.choices(PLAIN_REMARKS, weights)[0]
    header = ["case_ref", "patient_ref", "remark_plain", "remark_shared", "remark_rare", "remark_mixed", "remark_open",
              "visit_kind", "charge"]
    rows: "list[list[str]]" = []
    for row, person in enumerate(order):
        rows += [[_case(row), forms.patient_ref(person)] + [columns[name][row] for name in header[2:7]]
                 + forms._ordinary(draw)]
    META[(KIND_REMARKS, n, seed, people)] = meta
    return header, rows


# -- 2. lists of names in one cell -------------------------------------------------

LIST_WIDTH = 30


def _list_needles(items: "list[str]", cell: str) -> "tuple[str, ...]":
    """The names a list cell, cut or not, shows: each item whole, each family name whole, a cut family name of five letters or more."""
    needles: "list[str]" = []
    for item in items:
        last = item.split(",")[0]
        if item in cell:
            needles += [item, last]
        elif last in cell:
            needles += [last]
        else:
            tail = cell.split("; ")[-1]
            if len(tail) >= 5 and last.startswith(tail):
                needles += [tail]
    return tuple(dict.fromkeys(needles))


def name_lists(n: int, seed: int, people: "int | None" = None) -> "tuple[list[str], list[list[str]]]":
    """Cases, several a person, with four columns listing names (the module's second kind)."""
    draw = random.Random(seed)
    count = _people(n, people)
    names = random.Random(seed + 12)
    family = forms._distinct(names, 400, lambda d: made_up_word(d, 3))
    given = forms._distinct(names, 120, lambda d: made_up_word(d, 2))
    staff = [f"{last}, {draw.choice(CAPITALS)}" for last in family[:150]]
    staff_given = [f"{last.upper()}, {draw.choice(given).upper()} {draw.choice(CAPITALS)}" for last in family[:60]]
    order = forms._person_rows(n, draw, count)
    teams = [draw.sample(staff[:40], draw.choice((2, 3, 3, 4))) for _place in range(10)]
    given_teams = [draw.sample(staff_given, 2) for _place in range(6)]
    weights = [1.0 / (rank + 1) for rank in range(len(teams))]
    companion_of: "list[list[str]]" = []
    for person in range(count):
        mine = [f"{family[150 + person % 250]}, {draw.choice(CAPITALS)}"]
        if draw.random() < 0.6:
            mine += [f"{draw.choice(family[150:])}, {draw.choice(CAPITALS)}"]
        companion_of += [mine]
    meta: dict = {}
    header = ["case_ref", "patient_ref", "team_common", "team_rare", "companions", "team_given", "visit_kind", "charge"]
    rows: "list[list[str]]" = []
    for row, person in enumerate(order):
        common = rare = mate = named = ""
        if draw.random() < 0.7:
            items = draw.choices(teams, weights)[0]
            common = "; ".join(items)[:LIST_WIDTH]
            _note(meta, "team_common", common, FORM_NAMES, _list_needles(items, common))
        if draw.random() < 0.5:
            items = draw.sample(staff[40:], draw.choice((2, 3, 4)))
            rare = "; ".join(items)[:LIST_WIDTH]
            _note(meta, "team_rare", rare, FORM_NAMES, _list_needles(items, rare))
        if draw.random() < 0.5:
            items = companion_of[person]
            mate = "; ".join(items)[:LIST_WIDTH]
            _note(meta, "companions", mate, FORM_NAMES, _list_needles(items, mate))
        if draw.random() < 0.6:
            items = draw.choice(given_teams)
            named = "; ".join(items)
            _note(meta, "team_given", named, FORM_GIVEN, _list_needles(items, named))
        rows += [[_case(row), forms.patient_ref(person), common, rare, mate, named] + forms._ordinary(draw)]
    META[(KIND_NAME_LISTS, n, seed, people)] = meta
    return header, rows


# -- 3. labels naming a person ----------------------------------------------------

NAMED_TEMPLATES = ("Dr {s} pre-op note", "Dr {s} clinic", "Dr. {s} sedation set", "Dr {s} spine pathway")
BARE_TEMPLATES = ("{s} knee protocol", "{s} airway checklist", "{s} block template")
PLAIN_TEMPLATES = ("standard pre-op note", "general consent", "post-op order set", "pain protocol",
                   "fall risk bundle")
PROCEDURES = ("knee scope", "hip revision", "cataract", "dialysis", "port placement", "colonoscopy",
              "carpal tunnel", "bronchoscopy", "hernia repair", "tonsillectomy")


def name_labels(n: int, seed: int, people: "int | None" = None) -> "tuple[list[str], list[list[str]]]":
    """Cases, several a person: templates naming a clinician and case labels opening with the patient's name (the module's third kind)."""
    draw = random.Random(seed)
    count = _people(n, people)
    names = random.Random(seed + 13)
    family = forms._distinct(names, 700, lambda d: made_up_word(d, 3))
    order = forms._person_rows(n, draw, count)
    meta: dict = {}
    named = [form.format(s=family[place]) for place, form in enumerate(NAMED_TEMPLATES)]
    bare = [form.format(s=family[10 + place]) for place, form in enumerate(BARE_TEMPLATES)]
    for place, cell in enumerate(named):
        _note(meta, "note_template", cell, FORM_TEMPLATE, (family[place],))
    for place, cell in enumerate(bare):
        _note(meta, "template_open", cell, FORM_BARE_TEMPLATE, (family[10 + place],))
    pool = named + list(PLAIN_TEMPLATES)
    weights = [1.0 / (rank + 1) for rank in range(len(pool))]
    surname: "list[str]" = []
    initials: "list[str]" = []
    style: "list[int]" = []
    for person in range(count):
        surname += [family[100 + (person if draw.random() < 0.8 else draw.randrange(count)) % 600]]
        initials += [draw.choice(CAPITALS) + draw.choice(CAPITALS)]
        style += [draw.randrange(2)]
    header = ["case_ref", "patient_ref", "note_template", "case_label", "template_open", "label_open", "visit_kind",
              "charge"]
    rows: "list[list[str]]" = []
    for row, person in enumerate(order):
        template = draw.choices(pool, weights)[0] if draw.random() < 0.8 else ""
        opened = draw.choice(bare + list(PLAIN_TEMPLATES)) if draw.random() < 0.5 else ""
        procedure = draw.choice(PROCEDURES)
        last, letters = surname[person], initials[person]
        if style[person] == 0:
            label = f"{last.upper()}, {letters} - {procedure}"
            needles: "tuple[str, ...]" = (last.upper(), f"{last.upper()}, {letters}")
        else:
            label = f"{last}, {letters[0]}.{letters[1]}. {procedure}"
            needles = (last, f"{last}, {letters[0]}.{letters[1]}.")
        _note(meta, "case_label", label, FORM_SURNAME_LABEL, needles)
        open_label = f"{last} {letters} {procedure}"
        _note(meta, "label_open", open_label, FORM_LABEL_NO_COMMA, (last, f"{last} {letters}"))
        rows += [[_case(row), forms.patient_ref(person), template, label, opened, open_label] + forms._ordinary(draw)]
    META[(KIND_NAME_LABELS, n, seed, people)] = meta
    return header, rows


# -- 4. area codes ---------------------------------------------------------------------


def area_codes(n: int, seed: int, people: "int | None" = None) -> "tuple[list[str], list[list[str]]]":
    """Each person's census tract and block group (states 02 to 09, the nought kept, and lost), and an area rank (the fourth kind).

    Most codes are each held by many people, a quarter by few (1 to 8);
    with ``people`` equal to ``n`` the table is one row a person.
    """
    draw = random.Random(seed)
    count = _people(n, people)
    big = max(count // 30, 30)
    small = big // 3
    codes: "list[str]" = []
    while len(codes) < big + small:
        code = f"0{draw.choice('245689')}{draw.randrange(1, 200, 2):03d}{draw.randint(100, 9999):04d}{draw.choice(('00', '01', '02'))}"
        if code not in codes:
            codes += [code]
    small_counts = [draw.randint(1, 8) for _place in range(small)]
    rest = count - sum(small_counts)
    weights = [1.0 / (rank + 1) ** 0.7 for rank in range(big)]
    big_counts = [max(11, int(rest * weight / sum(weights))) for weight in weights]
    big_counts[0] += rest - sum(big_counts)
    holder: "list[int]" = []
    for place, how_many in enumerate(big_counts + small_counts):
        holder += [place] * how_many
    draw.shuffle(holder)
    tract_of = [codes[holder[person]] for person in range(count)]
    group_of = [tract + f"{draw.randint(1, 4)}" for tract in tract_of]
    rank_of = {code: f"{draw.randint(1, 10)}" for code in codes}
    order = forms._person_rows(n, draw, count)
    meta: dict = {}
    header = ["patient_ref", "area_a", "area_b", "area_c", "area_rank", "visit_kind", "charge"]
    rows: "list[list[str]]" = []
    for person in order:
        tract, group = tract_of[person], group_of[person]
        lost = tract[1:]
        _note(meta, "area_a", tract, FORM_AREA, (tract,))
        _note(meta, "area_b", group, FORM_AREA, (group,))
        _note(meta, "area_c", lost, FORM_AREA, (lost,))
        rows += [[forms.patient_ref(person), tract, group, lost, rank_of[tract]] + forms._ordinary(draw)]
    META[(KIND_AREA_CODES, n, seed, people)] = meta
    return header, rows


# -- 5. coordinate pairs ------------------------------------------------------------


def point_pairs(n: int, seed: int, people: "int | None" = None) -> "tuple[list[str], list[list[str]]]":
    """A point a row, half a person's home (one holder), half one of eight shared sites (the fifth kind)."""
    draw = random.Random(seed)
    count = _people(n, people)

    def point(d: random.Random) -> "tuple[str, str]":
        return f"{d.uniform(26.0, 47.0):.5f}", f"{d.uniform(-121.0, -71.0):.5f}"

    shared = [point(draw) for _place in range(8)]
    home = [point(draw) for _place in range(count)]
    weights = [1.0 / (rank + 1) for rank in range(len(shared))]
    order = forms._person_rows(n, draw, count)
    meta: dict = {}
    header = ["patient_ref", "point_pair", "point_spaced", "point_wrapped", "point_n", "point_e", "visit_kind",
              "charge"]
    rows: "list[list[str]]" = []
    for person in order:
        mine = draw.random() < 0.5
        north, east = home[person] if mine else draw.choices(shared, weights)[0]
        for column, cell in (("point_pair", f"{north},{east}"), ("point_spaced", f"{north} {east}"),
                             ("point_wrapped", f"({north}, {east})")):
            _note(meta, column, cell, FORM_POINT, (cell, north, east))
        _note(meta, "point_n", north, FORM_POINT, (north,))
        _note(meta, "point_e", east, FORM_POINT, (east,))
        rows += [[forms.patient_ref(person), f"{north},{east}", f"{north} {east}", f"({north}, {east})", north, east]
                 + forms._ordinary(draw)]
    META[(KIND_POINT_PAIRS, n, seed, people)] = meta
    return header, rows


# -- 6. network addresses -------------------------------------------------------------


def node_addresses(n: int, seed: int, people: "int | None" = None) -> "tuple[list[str], list[list[str]]]":
    """Dotted, colon and hardware addresses: six shared by many rows, one a person's device, a few one-offs (the sixth kind)."""
    draw = random.Random(seed)
    count = _people(n, people)

    def dotted(d: random.Random) -> str:
        return f"{d.choice((10, 172, 192, 100))}.{d.randint(0, 255)}.{d.randint(0, 255)}.{d.randint(1, 254)}"

    def colon(d: random.Random) -> str:
        groups = [f"{d.randint(0, 65535):x}" for _place in range(4)]
        return "fd00:" + ":".join(groups[:2]) + "::" + ":".join(groups[2:])

    def hardware(d: random.Random) -> str:
        return ":".join(f"{d.randint(0, 255):02x}" for _place in range(6))

    makers = {"node_dotted": dotted, "node_colon": colon, "node_hardware": hardware}
    shared = {column: forms._distinct(draw, 6, make) for column, make in makers.items()}
    own = {column: forms._distinct(draw, count, make) for column, make in makers.items()}
    weights = [1.0 / (rank + 1) for rank in range(6)]
    order = forms._person_rows(n, draw, count)
    meta: dict = {}
    header = ["patient_ref", "node_dotted", "node_colon", "node_hardware", "visit_kind", "charge"]
    rows: "list[list[str]]" = []
    for person in order:
        roll = draw.random()
        cells: "list[str]" = []
        for column, make in makers.items():
            if roll < 0.45:
                cell = draw.choices(shared[column], weights)[0]
            elif roll < 0.95:
                cell = own[column][person]
            else:
                cell = make(draw)
            _note(meta, column, cell, FORM_NODE, (cell,))
            cells += [cell]
        rows += [[forms.patient_ref(person)] + cells + forms._ordinary(draw)]
    META[(KIND_NODE_ADDRESSES, n, seed, people)] = meta
    return header, rows


# -- 7. ages past 89 inside bands ----------------------------------------------------


def _band_text(years: int) -> str:
    for low, high in ((0, 17), (18, 44), (45, 64), (65, 84), (85, 89), (90, 94)):
        if years <= high:
            return "<18 yrs" if low == 0 else f"{low}-{high} yrs"
    return ">= 95 yrs"


def age_bands(n: int, seed: int, people: "int | None" = None) -> "tuple[list[str], list[list[str]]]":
    """Each person's age as bands and display text (the seventh kind): 5 % of the people 90 to 94, 3.5 % 95 to 99, 1.5 % 100 to 104."""
    draw = random.Random(seed)
    count = _people(n, people)
    days_of: "list[int]" = []
    for _person in range(count):
        roll = draw.random()
        if roll < 0.03:
            days_of += [draw.randint(1, 27)]
        elif roll < 0.06:
            days_of += [draw.randint(28, 83)]
        elif roll < 0.09:
            days_of += [draw.randint(84, 729)]
        elif roll < 0.90:
            days_of += [int(draw.uniform(2, 89.99) * 365.25)]
        elif roll < 0.95:
            days_of += [int(draw.uniform(90, 94.99) * 365.25)]
        elif roll < 0.985:
            days_of += [int(draw.uniform(95, 99.99) * 365.25)]
        else:
            days_of += [int(draw.uniform(100, 104.99) * 365.25)]
    order = forms._person_rows(n, draw, count)
    meta: dict = {}
    header = ["patient_ref", "age_band", "band_text", "band_ten", "age_shown", "age_key", "visit_kind", "charge"]
    rows: "list[list[str]]" = []
    for person in order:
        days = days_of[person]
        years = int(days / 365.25)
        if days < 28:
            shown, key = f"{days} days", "1"
        elif days < 84:
            shown, key = f"{days // 7} weeks", "2"
        elif days < 730:
            shown, key = f"{int(days / 30.44)} mo", "3"
        else:
            shown, key = f"{years} yrs", "4"
        five = f"{(years // 5) * 5}-{(years // 5) * 5 + 4}"
        ten = "100+" if years >= 100 else f"{(years // 10) * 10}-{(years // 10) * 10 + 9}"
        text = _band_text(years)
        old = years >= 90
        for column, cell in (("age_band", five), ("band_text", text), ("band_ten", ten), ("age_shown", shown)):
            # ...an age of exactly 90 written `90 yrs` is the top-code's own
            # spelling of its one category, 90 and over: no age past 89.
            past = old and not (column == "age_shown" and years == 90)
            _note(meta, column, cell, FORM_OVER_89 if past else "none", (cell,) if past else ())
        rows += [[forms.patient_ref(person), five, text, ten, shown, key] + forms._ordinary(draw)]
    META[(KIND_AGE_BANDS, n, seed, people)] = meta
    return header, rows


# -- 8. device serial numbers by their values (the orchestrator's LANE CZ-E RULINGS 1, item (E)) ----


def _serial(draw: random.Random, layout: int) -> str:
    """A made-up device serial number in one of three makers' layouts: two capitals and eight figures, eight figures and a check capital, or dashed groups."""
    figures = f"{draw.randint(10000000, 99999999)}"
    if layout == 0:
        return draw.choice(CAPITALS) + draw.choice(CAPITALS) + figures
    if layout == 1:
        return figures + draw.choice(CAPITALS)
    return f"{draw.choice(CAPITALS)}{draw.randint(1, 9)}-{figures[:4]}-{figures[4:6]}"


def device_serials(n: int, seed: int, people: "int | None" = None) -> "tuple[list[str], list[list[str]]]":
    """Each person's one device, its serial number on every row of theirs, in one of three makers' layouts, under a generic name (the eighth kind)."""
    draw = random.Random(seed)
    count = _people(n, people)
    serial_of = forms._distinct(draw, count, lambda d: _serial(d, d.randrange(3)))
    order = forms._person_rows(n, draw, count)
    meta: dict = {}
    header = ["patient_ref", "tag_ref", "visit_kind", "charge"]
    rows: "list[list[str]]" = []
    for person in order:
        serial = serial_of[person]
        _note(meta, "tag_ref", serial, FORM_SERIAL, (serial,))
        rows += [[forms.patient_ref(person), serial] + forms._ordinary(draw)]
    META[(KIND_SERIALS, n, seed, people)] = meta
    return header, rows


# -- 9. THE REPAIR'S KINDS (the orchestrator's LANE CZ-E RULINGS 3; each an invented look-alike) ----


KIND_BAND_TOPS = "band_tops"
KIND_BAND_SCHEMES = "band_schemes"
KIND_ODD_MARKS = "odd_marks"
KIND_REMARKS_MORE = "remarks_more"
KIND_INLINE_NODES = "inline_nodes_cases"
KIND_SPARSE_NODES = "sparse_nodes_cases"
# Five-year bands topped from 100 by a spelling no band of the grammar
# read before the repair (RULINGS 3 (2)).
BAND_TOPS = {"top_amp": "100 & over", "top_interval": "(100, 105]", "top_up": "100 and up",
             "top_above": "100 or above", "top_older": "100 & older"}


def _ages_of(draw: random.Random, count: int) -> "list[int]":
    """Each person's age in years: 85 % 0 to 89, 7 % 90 to 94, 4 % 95 to 99, 4 % 100 to 104."""
    ages: "list[int]" = []
    for _person in range(count):
        roll = draw.random()
        low, high = (0, 89) if roll < 0.85 else (90, 94) if roll < 0.92 else (95, 99) if roll < 0.96 else (100, 104)
        ages += [draw.randint(low, high)]
    return ages


def band_tops(n: int, seed: int, people: "int | None" = None) -> "tuple[list[str], list[list[str]]]":
    """Each person's age as five-year bands under generic names, the group from 100 written `100 & over`, `(100, 105]`, `100 and up`, `100 or above` or `100 & older` (the repair's first kind)."""
    draw = random.Random(seed)
    count = _people(n, people)
    ages = _ages_of(draw, count)
    order = forms._person_rows(n, draw, count)
    meta: dict = {}
    header = ["patient_ref"] + list(BAND_TOPS) + ["visit_kind", "charge"]
    rows: "list[list[str]]" = []
    for person in order:
        age = ages[person]
        five = f"{(age // 5) * 5}-{(age // 5) * 5 + 4}"
        cells = [BAND_TOPS[column] if age >= 100 else five for column in BAND_TOPS]
        for column, cell in zip(BAND_TOPS, cells):
            _note(meta, column, cell, FORM_OVER_89 if age >= 90 else "none", (cell,) if age >= 90 else ())
        rows += [[forms.patient_ref(person)] + cells + forms._ordinary(draw)]
    META[(KIND_BAND_TOPS, n, seed, people)] = meta
    return header, rows


def _grouped(age: int, cuts: "tuple[tuple[int, int], ...]", written: "object", top: str, under: str = "") -> str:
    """An age's group among closed ``cuts`` written by ``written``, ``under`` below the first, ``top`` past the last."""
    if under and age < cuts[0][0]:
        return under
    for low, high in cuts:
        if low <= age <= high:
            return written(low, high)  # type: ignore[operator]
    return top


_UNEQUAL = ((0, 17), (18, 44), (45, 64), (65, 89), (90, 94), (95, 99))
_FROM_18_FIVE = ((18, 24),) + tuple((low, low + 4) for low in range(25, 100, 5))
_FROM_18_TEN = ((18, 29),) + tuple((low, low + 9) for low in range(30, 100, 10))
_NAMED_ONLY = ((18, 39), (40, 64), (65, 89), (90, 94), (95, 99))


def band_schemes(n: int, seed: int, people: "int | None" = None) -> "tuple[list[str], list[list[str]]]":
    """Each person's age in seven schemes of groups no unit word names (the repair's second kind): groups of unequal widths from 0 topped `100+` and `100 and up`; intervals from 0 (`(0, 18]` to `(99, 104]`); five-year groups opening `18-24` and ten-year groups opening `18-29` below `<18`; five-year intervals (`[0, 5)`, `(89, 94]`); and, under the heading `AGEGRP`, groups of unequal widths opening at 18 that only the heading names as ages."""
    draw = random.Random(seed)
    count = _people(n, people)
    ages = _ages_of(draw, count)
    order = forms._person_rows(n, draw, count)
    meta: dict = {}
    columns = ("grp_uneq", "grp_up", "grp_interval", "grp_from18_five", "grp_from18_ten", "grp_open89", "AGEGRP")
    header = ["patient_ref", *columns, "visit_kind", "charge"]
    rows: "list[list[str]]" = []
    for person in order:
        age = ages[person]
        cells = [
            _grouped(age, _UNEQUAL, lambda low, high: f"{low}-{high}", "100+"),
            _grouped(age, _UNEQUAL[:3] + ((65, 84), (85, 89), (90, 94), (95, 99)), lambda low, high: f"{low}-{high}",
                     "100 and up"),
            _grouped(age, ((0, 18), (19, 45), (46, 65), (66, 89), (90, 94), (95, 99), (100, 104)),
                     lambda low, high: f"({max(low - 1, 0)}, {high}]", "(104, 125]"),
            _grouped(age, _FROM_18_FIVE, lambda low, high: f"{low}-{high}", "100-104", "<18"),
            _grouped(age, _FROM_18_TEN, lambda low, high: f"{low}-{high}", "100+", "<18"),
            "[0, 5)" if age < 5 else f"({(age // 5) * 5 - 1}, {(age // 5) * 5 + 4}]",
            _grouped(age, _NAMED_ONLY, lambda low, high: f"{low}-{high}", "100+", "<18"),
        ]
        for column, cell in zip(columns, cells):
            _note(meta, column, cell, FORM_OVER_89 if age >= 90 else "none", (cell,) if age >= 90 else ())
        rows += [[forms.patient_ref(person)] + cells + forms._ordinary(draw)]
    META[(KIND_BAND_SCHEMES, n, seed, people)] = meta
    return header, rows


def _dealt(draw: random.Random, cells: "list[str]", rows_of: "list[list[int]]", cell: str, how_many: int) -> None:
    """A remark written on one to three rows of each of ``how_many`` people, each a different person."""
    placed = 0
    for person in draw.sample(range(len(rows_of)), len(rows_of)):
        if placed >= how_many:
            break
        free = [row for row in rows_of[person] if not cells[row]]
        if not free:
            continue
        for row in draw.sample(free, min(draw.choice((1, 2, 3)), len(free))):
            cells[row] = cell
        placed += 1


_HOLDERS = (12, 15, 25, 60, 150, 300)
_ODD_MARKS = ("\u2011", "\u2013", "\u2010", "\u2212", "\u2011", "\u2013")
_ODD_GAPS = ("\xa0", "\u202f", "\u2009", "\xa0", "\u202f", "\u3000")


def _remarks_table(kind: str, n: int, seed: int, people: "int | None",
                   seeded: "dict[str, list[tuple[str, str, tuple[str, ...]]]]",
                   draw: random.Random, count: int) -> "tuple[list[str], list[list[str]]]":
    """A patient table of remark columns, each seeded remark on 12 to 300 people, the rest plain remarks on half the rows."""
    order = forms._person_rows(n, draw, count)
    rows_of = _rows_of(order, count)
    meta: dict = {}
    cells = {column: [""] * n for column in seeded}
    for column, remarks in seeded.items():
        for place, (cell, form, needles) in enumerate(remarks):
            _note(meta, column, cell, form, needles)
            _dealt(draw, cells[column], rows_of, cell, _HOLDERS[place % len(_HOLDERS)])
    for row in range(n):
        for column in seeded:
            if not cells[column][row] and draw.random() < 0.5:
                cells[column][row] = draw.choice(PLAIN_REMARKS)
    header = ["patient_ref", *seeded, "visit_kind", "charge"]
    rows = [[forms.patient_ref(person)] + [cells[column][row] for column in seeded] + forms._ordinary(draw)
            for row, person in enumerate(order)]
    META[(kind, n, seed, people)] = meta
    return header, rows


def odd_marks(n: int, seed: int, people: "int | None" = None) -> "tuple[list[str], list[list[str]]]":
    """Remarks written for 12 to 300 people whose identifier carries the odd marks a form or a word processor writes (the repair's third kind): a telephone number and a date with a non-breaking hyphen, an en dash, a hyphen or a minus sign; a non-breaking, narrow or thin space after a title, after a relative's word, and after a family name's comma in a list."""
    draw = random.Random(seed)
    count = _people(n, people)
    names = random.Random(seed + 13)
    family = forms._distinct(names, 60, lambda d: made_up_word(d, 3))
    given = forms._distinct(names, 30, lambda d: made_up_word(d, 2))
    seeded: "dict[str, list[tuple[str, str, tuple[str, ...]]]]" = {column: [] for column in (
        "odd_phone", "odd_date", "odd_title", "odd_kin", "odd_list")}
    for place in range(6):
        mark, gap = _ODD_MARKS[place], _ODD_GAPS[place]
        phone = f"{draw.randint(201, 989)}{mark}555{mark}0{draw.randint(100, 199)}"
        seeded["odd_phone"] += [(("call {x}", "son {x}", "home {x}", "callback {x}", "cell {x}",
                                   "reach at {x}")[place].format(x=phone), FORM_PHONE, (phone,))]
        month, day = draw.randint(1, 12), draw.randint(1, 28)
        date = f"2031{mark}{month:02d}{mark}{day:02d}" if place % 2 else f"{month}{mark}{day}{mark}31"
        seeded["odd_date"] += [(("moved to {x}", "seen {x}", "resume {x}", "f/u {x}", "postponed to {x}",
                                  "rescheduled {x}")[place].format(x=date), FORM_DATE, (date,))]
        last = family[place]
        seeded["odd_title"] += [(("per Dr{g}{s}", "Mrs{g}{s} notified", "Dr.{g}{s} to review", "per Mr{g}{s}",
                                   "Ms{g}{s} called", "Dr{g}{s} clinic")[place].format(g=gap, s=last), FORM_TITLE, (last,))]
        first = given[place]
        seeded["odd_kin"] += [(("son{g}{f} at bedside", "wife{g}{f} notified", "per daughter{g}{f}",
                                 "husband{g}{f} to drive", "mother{g}{f} called", "friend{g}{f} called")[place].format(
                                     g=gap, f=first), FORM_RELATIVE, (first,))]
        one, two = family[10 + 2 * place], family[11 + 2 * place]
        seeded["odd_list"] += [(f"{one},{gap}K; {two},{gap}T", FORM_NAMES, (one, two))]
    return _remarks_table(KIND_ODD_MARKS, n, seed, people, seeded, draw, count)


def remarks_more(n: int, seed: int, people: "int | None" = None) -> "tuple[list[str], list[list[str]]]":
    """Remarks written for 12 to 300 people holding a telephone number written `AAA EEE-LLLL` with no word of a telephone beside it, and a range of two dates `M/D-M/D` (the repair's fourth kind)."""
    draw = random.Random(seed)
    count = _people(n, people)
    seeded: "dict[str, list[tuple[str, str, tuple[str, ...]]]]" = {"phone_spaced": [], "date_range": []}
    for place in range(6):
        phone = f"{draw.randint(201, 989)} 555-0{draw.randint(100, 199)}"
        seeded["phone_spaced"] += [(("son {x}", "home {x} after 5", "daughter at {x}", "wife {x}", "{x} (home)",
                                      "leave msg {x}")[place].format(x=phone), FORM_PHONE, (phone,))]
        month, day = draw.randint(1, 12), draw.randint(1, 20)
        span = f"{month}/{day}-{month}/{day + 7}"
        seeded["date_range"] += [(("out {x}", "away {x}", "inpatient {x}", "on hold {x}", "travel {x}",
                                    "leave {x}")[place].format(x=span), FORM_DATE, (span,))]
    return _remarks_table(KIND_REMARKS_MORE, n, seed, people, seeded, draw, count)


def _node_table(kind: str, n: int, seed: int, people: "int | None", sparse: bool) -> "tuple[list[str], list[list[str]]]":
    """One row a case, no patient column: device addresses and home points standing among words, or on one row in twenty of a column of labels holding figures (``sparse``)."""
    draw = random.Random(seed)
    count = _people(n, people)

    def dotted(d: random.Random) -> str:
        return f"{d.choice((10, 172, 192))}.{d.randint(0, 255)}.{d.randint(0, 255)}.{d.randint(1, 254)}"

    def point(d: random.Random) -> str:
        return f"{d.uniform(26.0, 47.0):.5f},{d.uniform(-121.0, -71.0):.5f}"

    shared_ip = forms._distinct(draw, 6, dotted)
    own_ip = forms._distinct(draw, count, dotted)
    shared_point = forms._distinct(draw, 8, point)
    own_point = forms._distinct(draw, count, point)
    labels = [f"{word} {place}" for word in ("Station", "Kiosk", "Bay", "Desk") for place in range(1, 11)]
    few = set(draw.sample(range(count), count // 20))
    order = forms._person_rows(n, draw, count)
    meta: dict = {}
    columns = ("src_sparse", "point_sparse") if sparse else ("src_ip", "src_login", "src_home", "src_hemi")
    header = ["case_ref", *columns, "visit_kind", "charge"]
    rows: "list[list[str]]" = []
    for row, person in enumerate(order):
        mine = draw.random() < 0.55
        address = own_ip[person] if mine else draw.choice(shared_ip)
        north, east = (own_point[person] if mine else draw.choice(shared_point)).split(",")
        if sparse:
            seeded = person in few
            cells = [own_ip[person] if seeded else draw.choice(labels),
                     own_point[person] if seeded else draw.choice(labels)]
            if seeded:
                _note(meta, "src_sparse", cells[0], FORM_NODE, (cells[0],))
                _note(meta, "point_sparse", cells[1], FORM_POINT, (cells[1],))
        else:
            cells = [f"IP {address}", f"login from {address}", f"home {north},{east}", f"N{north} W{east[1:]}"]
            for column, cell, needles in zip(columns, cells, ((address,), (address,), (f"{north},{east}",),
                                                              (f"N{north} W{east[1:]}",))):
                _note(meta, column, cell, FORM_NODE if "ip" in column or "login" in column else FORM_POINT,
                      (cell,) + needles)
        rows += [[_case(row), *cells] + forms._ordinary(draw)]
    meta["__persons__"] = {f"{row}": (forms.patient_ref(order[row]), ()) for row in range(len(order))}
    META[(kind, n, seed, people)] = meta
    return header, rows


def inline_nodes(n: int, seed: int, people: "int | None" = None) -> "tuple[list[str], list[list[str]]]":
    """A device's address after `IP ` or `login from `, a home point after `home ` or written `N<latitude> W<longitude>`, one row a case (the repair's fifth kind)."""
    return _node_table(KIND_INLINE_NODES, n, seed, people, False)


def sparse_nodes(n: int, seed: int, people: "int | None" = None) -> "tuple[list[str], list[list[str]]]":
    """A person's own device address, or home point, on the rows of one person in twenty of a column of labels holding figures (`Bay 5`), one row a case (the repair's sixth kind)."""
    return _node_table(KIND_SPARSE_NODES, n, seed, people, True)


KIND_PLAIN_LABELS = "plain_labels"
# The plain clinical labels of the price kind (the orchestrator's LANE CZ-E
# RULINGS 4 (3) (iv)): no identifier stands in any, each family written
# from parts of its own.
PLAIN_LABEL_COLUMNS = ("exam_name", "med_name", "service_name", "score_note", "abbrev_note")
_EXAM_PARTS = ("BRAIN", "HEAD", "CHEST", "ABDOMEN", "PELVIS", "LUMBAR SPINE", "KNEE", "SHOULDER", "HIP", "ANKLE")
_EXAM_CODES = ("MR", "CT", "XR", "US", "NM", "DR")
_DRUG_STEMS = ("ALVORIN", "BEXATOL", "CARDIPINE", "DOLMAZIDE", "ESOPRAZINE")
_RELEASE = ("DR", "ER", "MR", "XR", "SR")
_SERVICES = ("MS Clinic", "Cardiology Clinic", "Doctor Note", "Nurse Note", "Doctor Visit", "Office Visit", "Dr Office",
             "Main Office")
_SCORES = tuple(f"pain {over}/10" for over in range(0, 11)) + tuple(f"strength {over}/5" for over in range(0, 6))
_ABBREVIATIONS = tuple(f"{code} {word}" for code in ("I.C.U.", "A.M.A.", "P.E.G.", "A.B.G.", "C.H.F.", "U.T.I.")
                       for word in ("eval", "consult"))


def plain_labels(n: int, seed: int, people: "int | None" = None) -> "tuple[list[str], list[list[str]]]":
    """Plain clinical labels holding no identifier, each on many rows (the repair's seventh kind, the price): imaging exams' names with a modality code first, medicines' names with a release code, services' words after a title-like word, scores out of ten or five, and dotted clinical abbreviations."""
    draw = random.Random(seed)
    count = _people(n, people)
    pools = {
        "exam_name": [f"{code} {part}{contrast}" for code in _EXAM_CODES for part in _EXAM_PARTS
                      for contrast in ("", " WO CONTRAST")],
        "med_name": [f"{stem} {release} {form}" for stem in _DRUG_STEMS for release in _RELEASE
                     for form in ("TABLET", "CAPSULE")],
        "service_name": list(_SERVICES), "score_note": list(_SCORES), "abbrev_note": list(_ABBREVIATIONS),
    }
    order = forms._person_rows(n, draw, count)
    meta: dict = {}
    header = ["patient_ref", *PLAIN_LABEL_COLUMNS, "visit_kind", "charge"]
    rows: "list[list[str]]" = []
    for person in order:
        cells = [draw.choice(pools[column]) for column in PLAIN_LABEL_COLUMNS]
        rows += [[forms.patient_ref(person)] + cells + forms._ordinary(draw)]
    META[(KIND_PLAIN_LABELS, n, seed, people)] = meta
    return header, rows


# -- THE SECOND REPAIR'S KINDS (the orchestrator's LANE CZ-E RULINGS 6 and 7) --
KIND_SEEN_DATES = "seen_dates"
KIND_ADULT_GROUPS = "adult_groups"
KIND_FLOOR_FORMS = "floor_forms_cases"


def seen_dates(n: int, seed: int, people: "int | None" = None) -> "tuple[list[str], list[list[str]]]":
    """Visit remarks `seen M/D` with no year, their dates sharing days (the second repair's first kind; the combined verify's two shapes): 24 dates, four days in six months, each dealt to 12 to 300 people (`seen_md`), the same written day first (`seen_dm`), and each person's own date on 4 to 20 of their rows (`own_seen`) -- the score rule of repair 1 read every date of such a column as a score and published them."""
    draw = random.Random(seed)
    count = _people(n, people)
    order = forms._person_rows(n, draw, count)
    rows_of = _rows_of(order, count)
    meta: dict = {}
    columns = ("seen_md", "seen_dm", "own_seen")
    cells = {column: [""] * n for column in columns}
    months = (1, 3, 5, 7, 9, 11)
    for place, (month, day) in enumerate((month, day) for month in months for day in (3, 8, 14, 21)):
        md, dm = f"seen {month}/{day}", f"seen {day + 9}/{month}"
        _note(meta, "seen_md", md, FORM_DATE, (md, f"{month}/{day}"))
        _note(meta, "seen_dm", dm, FORM_DATE, (dm, f"{day + 9}/{month}"))
        _dealt(draw, cells["seen_md"], rows_of, md, _HOLDERS[place % len(_HOLDERS)])
        _dealt(draw, cells["seen_dm"], rows_of, dm, _HOLDERS[(place + 1) % len(_HOLDERS)])
    for person in range(count):
        month, day = draw.choice(months), draw.choice((3, 8, 14, 21, 25))
        own = f"seen {month}/{day} at home visit {person % 97}"
        rows = rows_of[person]
        for row in draw.sample(rows, min(draw.randint(4, 20), len(rows))):
            cells["own_seen"][row] = own
        _note(meta, "own_seen", own, FORM_DATE, (own,))
    for row in range(n):
        for column in ("seen_md", "seen_dm"):
            if not cells[column][row] and draw.random() < 0.5:
                cells[column][row] = draw.choice(PLAIN_REMARKS)
    header = ["patient_ref", *columns, "visit_kind", "charge"]
    rows = [[forms.patient_ref(person)] + [cells[column][row] for column in columns] + forms._ordinary(draw)
            for row, person in enumerate(order)]
    META[(KIND_SEEN_DATES, n, seed, people)] = meta
    return header, rows


# The adult groups of the second repair's second kind, under neutral names
# (the combined verify's item 2: groups of unequal widths opening at 16, 18
# or 21, and the repair's own `75-99` beside `100+`), and Codex's item 1's
# column named for ages (`<90` beside `90-94` and `95+`: the younger stay
# their own band) beside the same scheme under a neutral name.
_ADULT_SCHEMES = {
    "grp_a18": ((18, 44), (45, 64), (65, 89), (90, 94), (95, 99)),
    "grp_a16": ((16, 24), (25, 44), (45, 64), (65, 89), (90, 94), (95, 99)),
    "grp_a21": ((21, 39), (40, 59), (60, 74), (75, 89), (90, 94), (95, 99)),
    "grp_a75": ((18, 44), (45, 59), (60, 74), (75, 99)),
}


def adult_groups(n: int, seed: int, people: "int | None" = None) -> "tuple[list[str], list[list[str]]]":
    """Each adult's age in four schemes of groups under neutral names (`grp_a18`, `grp_a16`, `grp_a21`, `grp_a75`, each topped `100+`), and as `<90`, `90-94` or `95+` named for ages (`age_group`) and under a neutral name (`grp_lt90`, read as ages by its five-year band past 89 beside a band from 0) -- 80 % 18 to 89, 8 % 90 to 94, 6 % 95 to 99, 6 % 100 to 104 (the second repair's second kind)."""
    draw = random.Random(seed)
    count = _people(n, people)
    ages: "list[int]" = []
    for _person in range(count):
        roll = draw.random()
        low, high = (18, 89) if roll < 0.80 else (90, 94) if roll < 0.88 else (95, 99) if roll < 0.94 else (100, 104)
        ages += [draw.randint(low, high)]
    order = forms._person_rows(n, draw, count)
    meta: dict = {}
    columns = (*_ADULT_SCHEMES, "age_group", "grp_lt90")
    header = ["patient_ref", *columns, "visit_kind", "charge"]
    rows: "list[list[str]]" = []
    for person in order:
        age = ages[person]
        cells = [_grouped(age, cuts, lambda low, high: f"{low}-{high}", "100+") for cuts in _ADULT_SCHEMES.values()]
        lt90 = "<90" if age < 90 else "90-94" if age < 95 else "95+"
        cells += [lt90, lt90]
        for column, cell in zip(columns, cells):
            _note(meta, column, cell, FORM_OVER_89 if age >= 90 else "none", (cell,) if age >= 90 else ())
        rows += [[forms.patient_ref(person)] + cells + forms._ordinary(draw)]
    META[(KIND_ADULT_GROUPS, n, seed, people)] = meta
    return header, rows


# The forms of Codex's items 4, 5 and 6, each value on the floor's rows
# exactly -- eleven -- beside one ordinary label on every other row, one row
# a case (a table counted in rows publishes a level its eleven rows hold).
FLOOR_FORM_COLUMNS = (
    "hw_hyphen", "hw_letters", "v6_letters", "v6_short_letters", "hw_dots", "login_v6", "home_hemi", "home_spaced",
    "lat_lon", "kin_two", "comma_spaces", "intl_trunk", "intl_area",
)
FLOOR_ROWS = 11


def floor_forms(n: int, seed: int, people: "int | None" = None) -> "tuple[list[str], list[list[str]]]":
    """One row a case, no patient column (the second repair's third kind): in each column ONE value holding an identifier on exactly the floor's eleven rows beside one ordinary label on all the others -- a hardware address parted by hyphens, one of letters alone, a colon address of letters alone (eight groups, and around `::`), a hardware address of letters parted by points, a colon address of letters after `login from`, a home point written with degrees' marks and hemispheres' letters, with the letters apart, and each number after a label glued by `=`, a relative's name of two letters, a family name with three spaces after its comma, and an international number with a trunk nought or an area code in brackets."""
    draw = random.Random(seed)
    letters = "abcdef"

    def hexes(size: int, figures: bool) -> str:
        return "".join(draw.choice(letters + ("0123456789" if figures else "")) for _place in range(size))

    north, east = f"{draw.uniform(30.0, 46.0):.5f}", f"{draw.uniform(71.0, 120.0):.5f}"
    family = made_up_word(draw, 3)
    two = draw.choice(TWO_LETTER_NAMES[:10])
    values = {
        "hw_hyphen": "-".join(hexes(2, True) for _place in range(6)),
        "hw_letters": ":".join(hexes(2, False) for _place in range(6)),
        "v6_letters": ":".join(hexes(4, False) for _place in range(8)),
        "v6_short_letters": f"{hexes(4, False)}:{hexes(4, False)}::{hexes(3, False)}",
        "hw_dots": ".".join(hexes(4, False) for _place in range(3)),
        "login_v6": "login from " + ":".join(hexes(4, False) for _place in range(8)),
        "home_hemi": f"home {north}\xb0 N, {east}\xb0 W",
        "home_spaced": f"home {north} N, {east} W",
        "lat_lon": f"lat={north}, lon=-{east}",
        "kin_two": f"wife {two} notified",
        "comma_spaces": f"{family},   {draw.choice(CAPITALS)} scheduled",
        "intl_trunk": f"call +44 (0)20 {draw.randint(1000, 9999)} {draw.randint(1000, 9999)}",
        "intl_area": f"contact +44 (20) {draw.randint(1000, 9999)} {draw.randint(1000, 9999)}",
    }
    meta: dict = {}
    placed = {column: set(draw.sample(range(n), FLOOR_ROWS)) for column in FLOOR_FORM_COLUMNS}
    header = ["case_ref", *FLOOR_FORM_COLUMNS, "visit_kind", "charge"]
    rows: "list[list[str]]" = []
    for row in range(n):
        cells = [values[column] if row in placed[column] else "on file" for column in FLOOR_FORM_COLUMNS]
        rows += [[_case(row), *cells] + forms._ordinary(draw)]
    # ...each value counted whole and by the identifier inside it, where that
    # is long enough to be no other text's part (a name of two letters is not).
    inner = {
        "login_v6": values["login_v6"][len("login from "):], "home_hemi": north, "home_spaced": north,
        "lat_lon": north, "comma_spaces": family, "intl_trunk": values["intl_trunk"][len("call "):],
        "intl_area": values["intl_area"][len("contact "):],
    }
    for column in FLOOR_FORM_COLUMNS:
        _note(meta, column, values[column], FORM_NODE, (values[column], inner.get(column, "")))
    meta["__persons__"] = {f"{row}": (f"P{row:06d}", ()) for row in range(n)}
    META[(KIND_FLOOR_FORMS, n, seed, people)] = meta
    return header, rows


REPAIR_KINDS = (KIND_BAND_TOPS, KIND_BAND_SCHEMES, KIND_ODD_MARKS, KIND_REMARKS_MORE, KIND_INLINE_NODES,
                KIND_SPARSE_NODES, KIND_PLAIN_LABELS)
# The second repair's kinds, read unanswered and truthful as the first's
# (`seen_dates_cases` is `seen_dates` with no patient column, registered
# beside the other case kinds below).
REPAIR2_KINDS = (KIND_SEEN_DATES, KIND_SEEN_DATES + "_cases", KIND_ADULT_GROUPS, KIND_FLOOR_FORMS)
# The columns of bands whose published levels hold one category past 89 at
# most (`levels_past_89`).
BAND_COLUMNS = frozenset({"age_band", "band_text", "band_ten", *BAND_TOPS, "grp_uneq", "grp_up", "grp_interval",
                          "grp_from18_five", "grp_from18_ten", "grp_open89", "AGEGRP", *_ADULT_SCHEMES, "age_group",
                          "grp_lt90"})


MAKERS = {
    KIND_REMARKS: typed_remarks,
    KIND_NAME_LISTS: name_lists,
    KIND_NAME_LABELS: name_labels,
    KIND_AREA_CODES: area_codes,
    KIND_POINT_PAIRS: point_pairs,
    KIND_NODE_ADDRESSES: node_addresses,
    KIND_AGE_BANDS: age_bands,
    KIND_SERIALS: device_serials,
    KIND_BAND_TOPS: band_tops,
    KIND_BAND_SCHEMES: band_schemes,
    KIND_ODD_MARKS: odd_marks,
    KIND_REMARKS_MORE: remarks_more,
    KIND_INLINE_NODES: inline_nodes,
    KIND_SPARSE_NODES: sparse_nodes,
    KIND_PLAIN_LABELS: plain_labels,
    KIND_SEEN_DATES: seen_dates,
    KIND_ADULT_GROUPS: adult_groups,
    KIND_FLOOR_FORMS: floor_forms,
}
# Each kind's placed columns: those the readers must hold (`HELD`), the
# residual ones recorded (`OPEN`) and those beside them that hold no
# identifier and stay published (`PRICE`).
HELD = {
    KIND_REMARKS: ("remark_shared", "remark_rare", "remark_mixed"),
    KIND_NAME_LISTS: ("team_common", "team_rare", "companions", "team_given"),
    KIND_NAME_LABELS: ("note_template", "case_label"),
    KIND_AREA_CODES: ("area_a", "area_b", "area_c"),
    KIND_POINT_PAIRS: ("point_pair", "point_spaced", "point_wrapped", "point_n", "point_e"),
    KIND_NODE_ADDRESSES: ("node_dotted", "node_colon", "node_hardware"),
    KIND_AGE_BANDS: ("age_band", "band_text", "band_ten", "age_shown"),
    KIND_SERIALS: ("tag_ref",),
    KIND_BAND_TOPS: tuple(BAND_TOPS),
    KIND_BAND_SCHEMES: ("grp_uneq", "grp_up", "grp_interval", "grp_from18_five", "grp_from18_ten", "grp_open89",
                        "AGEGRP"),
    KIND_ODD_MARKS: ("odd_phone", "odd_date", "odd_title", "odd_kin", "odd_list"),
    KIND_REMARKS_MORE: ("phone_spaced", "date_range"),
    KIND_INLINE_NODES: ("src_ip", "src_login", "src_home", "src_hemi"),
    KIND_SPARSE_NODES: ("src_sparse", "point_sparse"),
    KIND_PLAIN_LABELS: (),
    KIND_SEEN_DATES: ("seen_md", "seen_dm", "own_seen"),
    KIND_ADULT_GROUPS: (*_ADULT_SCHEMES, "age_group", "grp_lt90"),
    KIND_FLOOR_FORMS: FLOOR_FORM_COLUMNS,
}
OPEN = {
    KIND_REMARKS: ("remark_open",),
    KIND_NAME_LABELS: ("template_open", "label_open"),
}
PRICE = {
    KIND_REMARKS: ("remark_plain",),
    KIND_AREA_CODES: ("area_rank",),
    KIND_AGE_BANDS: ("age_key",),
    KIND_PLAIN_LABELS: PLAIN_LABEL_COLUMNS,
}
# The truthful answer to each placed column's Safe Harbor question:
# `yes` where it holds an element (a clinician's name among them, the
# no-real-name rule of plan P4-D445's item 9), `no` where it holds none.
TRUTH_NO = ("remark_plain", "area_rank", "age_key") + PLAIN_LABEL_COLUMNS
# The general answers the zoo gives a placed column's reading question,
# as the person who holds the table knows it: a remark, a list, a label,
# a point, an address or a band is kept as what it was read as (`keep`,
# no record number of the rows), an area's code is a code.
KNOWS = {
    KIND_REMARKS: {"case_ref": "keep", "remark_shared": "keep", "remark_rare": "keep", "remark_mixed": "keep",
                   "remark_open": "keep", "remark_plain": "keep"},
    KIND_NAME_LISTS: {"case_ref": "keep", "team_common": "keep", "team_rare": "keep", "companions": "keep",
                      "team_given": "keep"},
    KIND_NAME_LABELS: {"case_ref": "keep", "note_template": "keep", "case_label": "keep", "template_open": "keep",
                       "label_open": "keep"},
    KIND_AREA_CODES: {"area_a": "code", "area_b": "code", "area_c": "code", "area_rank": "keep"},
    KIND_POINT_PAIRS: {"case_ref": "keep", "point_pair": "keep", "point_spaced": "keep", "point_wrapped": "keep",
                       "point_n": "keep", "point_e": "keep"},
    KIND_NODE_ADDRESSES: {"case_ref": "keep", "node_dotted": "keep", "node_colon": "keep", "node_hardware": "keep"},
    KIND_AGE_BANDS: {"case_ref": "keep", "age_band": "keep", "band_text": "keep", "band_ten": "keep",
                     "age_shown": "keep", "age_key": "code"},
    KIND_SERIALS: {"case_ref": "keep", "tag_ref": "keep"},
}
for _kind in REPAIR_KINDS + (KIND_SEEN_DATES, KIND_ADULT_GROUPS, KIND_FLOOR_FORMS):
    # ...each placed column of the repair's kinds is kept as what it was read
    # as, as the person who holds the table knows it.
    KNOWS[_kind] = {"case_ref": "keep", **{column: "keep" for column in HELD[_kind] + PRICE.get(_kind, ())}}


def _cases_of(kind: str) -> "object":
    """The maker of a kind's rows with no patient column, the case number first."""
    maker = MAKERS[kind]

    def made(n: int, seed: int, people: "int | None" = None) -> "tuple[list[str], list[list[str]]]":
        header, rows = maker(n, seed, people)
        place = header.index("patient_ref")
        meta = dict(META[(kind, n, seed, people)])
        meta["__persons__"] = {f"{row}": (rows[row][place], ()) for row in range(len(rows))}
        META[(kind + CASES, n, seed, people)] = meta
        kept = [index for index in range(len(header)) if index != place]
        if "case_ref" not in header:
            return ["case_ref"] + [header[index] for index in kept], [
                [_case(row)] + [rows[row][index] for index in kept] for row in range(len(rows))
            ]
        return [header[index] for index in kept], [[row[index] for index in kept] for row in rows]

    return made


for _kind in CASE_KINDS + (KIND_SEEN_DATES,):
    MAKERS[_kind + CASES] = _cases_of(_kind)  # type: ignore[assignment]
    HELD[_kind + CASES] = HELD[_kind]
    if _kind in OPEN:
        OPEN[_kind + CASES] = OPEN[_kind]
    if _kind in PRICE:
        PRICE[_kind + CASES] = PRICE[_kind]
    KNOWS[_kind + CASES] = KNOWS[_kind]


def _alone(kind: str, column: str) -> str:
    """A kind's one column beside its patient column, or beside its case number where it has none: the smallest table that shows a form."""
    maker = MAKERS[kind]
    name = f"{kind}__{column}"

    def made(n: int, seed: int, people: "int | None" = None) -> "tuple[list[str], list[list[str]]]":
        header, rows = maker(n, seed, people)  # type: ignore[operator]
        meta = META[(kind, n, seed, people)]
        META[(name, n, seed, people)] = meta
        kept = [header.index(one) for one in ("patient_ref", "case_ref") if one in header][:1] + [header.index(column)]
        return [header[index] for index in kept], [[row[index] for index in kept] for row in rows]

    MAKERS[name] = made  # type: ignore[assignment]
    HELD[name] = tuple(one for one in HELD[kind] if one == column)
    OPEN[name] = tuple(one for one in OPEN.get(kind, ()) if one == column)
    PRICE[name] = tuple(one for one in PRICE.get(kind, ()) if one == column)
    KNOWS[name] = {one: KNOWS[kind][one] for one in KNOWS[kind] if one in (column, "case_ref")}
    return name


def _column_alone(kind: str, column: str) -> str:
    """A kind's one column alone in its table, no patient column and no case number: what the command counts in rows."""
    maker = MAKERS[kind]
    name = f"{kind}__{column}_alone"

    def made(n: int, seed: int, people: "int | None" = None) -> "tuple[list[str], list[list[str]]]":
        header, rows = maker(n, seed, people)  # type: ignore[operator]
        meta = dict(META[(kind, n, seed, people)])
        place = header.index("patient_ref")
        meta["__persons__"] = {f"{row}": (rows[row][place], ()) for row in range(len(rows))}
        META[(name, n, seed, people)] = meta
        at = header.index(column)
        return [column], [[row[at]] for row in rows]

    MAKERS[name] = made  # type: ignore[assignment]
    HELD[name] = (column,)
    OPEN[name] = ()
    PRICE[name] = ()
    KNOWS[name] = {column: KNOWS[kind][column]}
    return name


# THE SMALLEST TABLES of each measured exposure, each one column at the
# owner's table floor (20,000 rows, 1,000 people): a remark written for
# many people beside the patient column; a rare remark, and a person's
# companions, beside a case number alone; an area code beside the patient
# column; a coordinate pair beside a case number; five-year bands and band
# text beside the patient column.
SMALLEST = (
    _alone(KIND_REMARKS, "remark_shared"),
    _alone(KIND_REMARKS + CASES, "remark_rare"),
    _alone(KIND_NAME_LISTS + CASES, "companions"),
    _alone(KIND_AREA_CODES, "area_a"),
    _alone(KIND_POINT_PAIRS + CASES, "point_pair"),
    _alone(KIND_AGE_BANDS, "age_band"),
    _alone(KIND_AGE_BANDS, "band_text"),
    _column_alone(KIND_SERIALS, "tag_ref"),
)
KINDS = tuple(MAKERS)


def table_of(kind: str) -> zoo.Table:
    """A kind's table in the zoo's form, its patient column named where it has one."""
    maker = MAKERS[kind]
    header, _rows = maker(zoo.SMOKE_ROWS, SEED)  # type: ignore[operator]
    person = "patient_ref" if "patient_ref" in header else ""
    knows = dict(KNOWS[kind])
    if person:
        knows["patient_ref"] = "identifier"
    return zoo.Table(
        kind, ".csv", maker, lambda head, rows: zoo.csv_bytes(head, rows),  # type: ignore[arg-type]
        {kind: tuple(header)}, knows, zoo._csv_reader(), (),
        person=person,
        leaks=tuple((column, "values") for column in HELD[kind] + OPEN.get(kind, ())),
    )


def placed(kind: str) -> "tuple[str, ...]":
    """A kind's columns measured: those held, the residual, and the price columns beside them."""
    return HELD[kind] + OPEN.get(kind, ()) + PRICE.get(kind, ())


def answer(table: zoo.Table, document: "dict", mode: str) -> None:
    """One round of answers: the zoo's general answers, then each placed column's Safe Harbor question as the column truly is; and, by ``mode``, `no` to every Safe Harbor question (`no`) or the person question `keep` and a reading that publishes values with the Safe Harbor question blank (`coded`)."""
    zoo.answer_generally(table, document, frozenset())
    for entry in zoo._entries(document):
        column = f"{entry.get('column', '')}"
        offered = sorted(answer for answer in zoo._offered(entry) if answer not in zoo.AGE_UNIT_ANSWERS)
        if column in placed(table.name) and offered == ["no", "yes"]:
            entry["your_answer"] = "no" if column in TRUTH_NO else "yes"
    if mode == "no":
        forms._answer_no(document)
    if mode == "coded":
        forms._answer_coded(document, HELD[table.name] + OPEN.get(table.name, ()))


def tagged_hits(
    needles: "list[tuple[str, str]]", texts: "list[str]", cells: "list[str]",
) -> "tuple[set[tuple[str, str]], dict[str, int]]":
    """ONE SCAN for every tag at once: which (tag, needle) pairs the texts hold, and for each tag how many twin cells hold one of its needles.

    The reading of `unanswered_identifier_shapes.count_real`'s linear
    counter (each needle searched as text, and as the runs of figures it
    stands as), every needle tagged with the group it counts for, so a
    column's forms, their strings and a control table's are read in one
    pass over the texts and one over the different twin cells, where a
    call a group read the texts once a group.
    """
    import unanswered_identifier_shapes as shapes

    by_text: "dict[str, list[tuple[str, str]]]" = {}
    by_key: "dict[str, list[tuple[str, str]]]" = {}
    for tag, needle in needles:
        as_text, keys = shapes._keys_of(needle)
        if as_text:
            listed = by_text.setdefault(needle, [])
            listed += [(tag, needle)]
        for key in keys:
            listed = by_key.setdefault(key, [])
            listed += [(tag, needle)]
    sizes = sorted({len(needle) for needle in by_text})

    def needles_in(text: str) -> "set[tuple[str, str]]":
        hits: "set[tuple[str, str]]" = set()
        for key in shapes._figure_runs(text):
            hits.update(by_key.get(key, ()))
        for size in sizes:
            for start in range(len(text) - size + 1):
                found = by_text.get(text[start:start + size])
                if found:
                    hits.update(found)
        return hits

    published: "set[tuple[str, str]]" = set()
    for text in dict.fromkeys(texts):
        published |= needles_in(text)
    by_tag: "dict[str, int]" = {}
    seen: "dict[str, set[str]]" = {}
    for cell in cells:
        if cell not in seen:
            seen[cell] = {tag for tag, _needle in needles_in(cell)}
        for tag in seen[cell]:
            by_tag[tag] = by_tag.get(tag, 0) + 1
    return published, by_tag


# How much of the words each question says it saw `measure` keeps.
SAW_KEPT = 160
# The fewest letters in one run, or characters in all, a string inside a
# placed cell holds for the verdict to read it (`distinctive`).
DISTINCT_LETTERS = 5
DISTINCT_CHARACTERS = 7


def distinctive(needle: str) -> bool:
    """Whether a string inside a placed cell is one a made-up value does not write by chance: a run of `DISTINCT_LETTERS` letters or more (a name) or `DISTINCT_CHARACTERS` characters or more (a telephone number, a date with its year, an address). A held column's twin writes made-up letters and figures in its cells' layouts (`zjvxue dz 10/14/58`), so two initials (`K.T.`) or a month and a day with no year (`4/5`) stand inside made-up cells by chance; those are counted apart (`needles_short`) and their whole cells stay counted (`shown`, `twin_equal`)."""
    return max((len(run) for run in _letter_runs(needle)), default=0) >= DISTINCT_LETTERS or len(needle) >= DISTINCT_CHARACTERS


# THE KPI'S OWN READING OF A CATEGORY PAST 89 (Codex's item 8 of lane CZ-E's
# review, the orchestrator's LANE CZ-E RULINGS 6 (7)): a published label is
# a category holding an age of 90 or more where the ages it names reach 90
# -- read here from its own figures and marks, never by the product's band
# reader, so a category crossing 90 (`75-99`, `66+`) counts beside `90+`.
_UPWARD_MARKS = ("+", ">", "≥", "∞")
_UPWARD_WORDS = ("over", "above", "older", "up", "more", "greater", "plus", "beyond")
_DOWNWARD_STRICT = ("under", "below", "less", "younger")
_DOWNWARD_MARKS = ("<", "≤")


def _figures_of(label: str) -> "list[int]":
    """The whole numbers a label writes, in their order."""
    found: "list[int]" = []
    run = ""
    for character in label + " ":
        if "0" <= character <= "9":
            run += character
        elif run:
            found += [int(run)]
            run = ""
    return found


def _letter_runs(label: str) -> "list[str]":
    """The runs of letters a label writes, in small letters (`100up` writes `up`)."""
    found: "list[str]" = []
    run = ""
    for character in label.lower() + " ":
        if character.isalpha():
            run += character
        elif run:
            found += [run]
            run = ""
    return found


def label_reaches_90(label: str) -> bool:
    """Whether a published label names a category holding an age of 90 or more (the KPI's own reading): open upward (`+`, `>`, `≥`, `over`, `and older`, `& up`, `or more`) whatever its first age; open downward to an age it holds (`<= 90`; `<90`, `under 90` hold 89 at most); an interval in brackets to its last age held (`(65, 90]` holds 90, `[85, 90)` does not); two ages, the last 90 or more (`75-99`, `90-94 yrs`); one age alone from 90 to 125."""
    small = label.lower()
    figures = _figures_of(small)
    if not figures:
        return False
    words = _letter_runs(small)
    if any(mark in small for mark in _UPWARD_MARKS) or any(word in _UPWARD_WORDS for word in words):
        return True
    if any(mark in small for mark in _DOWNWARD_MARKS) or any(word in _DOWNWARD_STRICT for word in words):
        inclusive = "<=" in small or "=<" in small or "≤" in small
        return figures[0] - (0 if inclusive else 1) >= 90
    opened = small.lstrip()[:1]
    if opened in "([" and len(figures) >= 2:
        closing = ")" if ")" in small else "]"
        return figures[1] - (1 if closing == ")" else 0) >= 90
    if len(figures) >= 2:
        return max(figures[:2]) >= 90
    return 90 <= figures[0] <= 125


def levels_past_89(block: "dict") -> int:
    """How many of a described column's published levels name a category holding an age of 90 or more (`label_reaches_90`, the KPI's own reading): Safe Harbor allows one category of 90 and older."""
    levels = block.get("levels") if isinstance(block, dict) else None
    labels = {f"{level.get('label', '')}" for level in levels or [] if isinstance(level, dict)}
    return len([label for label in labels if label and label_reaches_90(label)])


def measure(
    folder: pathlib.Path, kind: str, rows: int, mode: str = "unanswered", seed: int = SEED,
    people: "int | None" = None, small_tables_refused: "bool | None" = None, describe_only: bool = False,
) -> "dict[str, object]":
    """One kind's table through profile (and its rounds of answers), generate at seed 0 and validate, counted per column and form.

    ``describe_only`` stops after the descriptions (no twin, no
    validation): the price kind's first run, whose three held label
    columns the held block's generation does not fill in hours (plan
    P4-D472 (c): a writer's limit older than the lane, measured on the
    base's few-people route alike).

    The commands are those a person types (`cli.main`), nobody at the
    keyboard, the table floor on at 20,000 rows. For each placed column
    (`placed`) and each of its forms, split by whether the floor's people
    hold a placed cell (``many``: 11 people or more, else ``few``): the
    placed cells written whole in the description, its summary, the
    questions file and the screen of every round or the twin's report and
    quality files (`shown`), the strings each counts as found there
    (`needles_shown`; a string a cell of the residual or the price columns
    holds too is counted apart, `needles_shared`, and one a made-up value
    writes by chance, `needles_short`: `distinctive`), the twin cells equal to a placed cell
    (`twin_equal`), the twin cells holding a COMPLETE real run of five
    figures or more of one inside a wider cell (`runs`,
    `safe_harbor_forms.complete_tokens`), and the same strings of a
    control table at another seed (`control_needles_shown`,
    `control_twin_cells`), with the questions put to the column and its
    role at the first and the last description. Counted by the linear
    counter's reading (`unanswered_identifier_shapes.count_real(...,
    linear=True)`), every group of a column in one scan (`tagged_hits`).
    """
    import unanswered_identifier_shapes as shapes
    from synthtwin import cli

    table = table_of(kind)
    folder.mkdir(parents=True, exist_ok=True)
    header, body = MAKERS[kind](rows, seed, people)  # type: ignore[operator]
    source = folder / f"{kind}.csv"
    source.write_bytes(zoo.csv_bytes(header, body))
    refused = rows >= zoo.KPI_ROWS if small_tables_refused is None else small_tables_refused
    screen = io.StringIO()
    texts: "list[str]" = []
    first_roles: "dict[str, str]" = {}
    put: "dict[str, list[list[str]]]" = {}
    saw: "dict[str, list[str]]" = {}
    profile = folder / f"{kind}-profile.json"
    questions = folder / f"{kind}-questions.json"
    started = time.perf_counter()
    found: "dict[str, object]" = {"kind": kind, "rows": rows, "mode": mode, "people": people, "columns": {}}

    def read_round() -> None:
        texts.extend([profile.read_text(encoding="utf-8"), questions.read_text(encoding="utf-8"),
                      (folder / f"{kind}-profile.txt").read_text(encoding="utf-8")])
        for entry in zoo._entries(json.loads(questions.read_text(encoding="utf-8"))):
            asked = put.setdefault(f"{entry.get('column', '')}", [])
            offered = sorted(zoo._offered(entry))
            if offered not in asked:
                asked += [offered]
            said = saw.setdefault(f"{entry.get('column', '')}", [])
            seen_text = f"{entry.get('what_synthtwin_saw', '')}"[:SAW_KEPT]
            if seen_text not in said:
                said += [seen_text]

    generated = validated = -1
    with shapes.nobody_at_the_keyboard():
        with contextlib.redirect_stdout(screen), contextlib.redirect_stderr(screen):
            code = cli.main(["profile", f"{source}", "--replace"], small_tables_refused=refused)
            found["profile"] = code
            if code == 0:
                read_round()
                first_roles.update({f"{c['name']}": f"{c['role']}"
                                    for c in json.loads(profile.read_text(encoding="utf-8"))["columns"]})
                rounds = 0
                while mode != "unanswered" and rounds < forms.ANSWER_ROUNDS_AT_MOST:
                    document = json.loads(questions.read_text(encoding="utf-8"))
                    before = json.dumps(document, sort_keys=True)
                    answer(table, document, mode)
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
            found["profile_seconds"] = round(time.perf_counter() - started, 1)
            stage = time.perf_counter()
            if code == 0 and not describe_only:
                generated = cli.main(["generate", f"{profile}", "--replace", "--seed", "0"],
                                     small_tables_refused=refused)
            found["generate_seconds"] = round(time.perf_counter() - stage, 1)
            stage = time.perf_counter()
            if generated == 0:
                validated = cli.main(["validate", f"{profile}", "--replace"], small_tables_refused=refused)
            found["validate_seconds"] = round(time.perf_counter() - stage, 1)
    found["generate"], found["validate"] = generated, validated
    found["describe_only"] = describe_only
    found["product_seconds"] = round(time.perf_counter() - started, 1)
    if code != 0:
        found["screen"] = screen.getvalue()[-400:]
    texts += [screen.getvalue()]
    if generated == 0:
        for written in (f"{kind}-twin-report.txt", f"{kind}-twin-quality.txt"):
            if (folder / written).is_file():
                texts += [(folder / written).read_text(encoding="utf-8")]
    described = (
        {f"{c['name']}": c for c in json.loads(profile.read_text(encoding="utf-8"))["columns"]}
        if first_roles and profile.is_file() else {}
    )
    twin = folder / f"{kind}-twin.csv"
    twin_header: "list[str]" = []
    twin_rows: "list[list[str]]" = []
    if generated == 0 and twin.is_file():
        import csv

        with open(twin, encoding="utf-8", newline="") as handle:
            reader = csv.reader(handle)
            twin_header = next(reader)
            twin_rows = list(reader)
    meta = META[(kind, rows, seed, people)]
    _control_header, _control_rows = MAKERS[kind](rows, seed + CONTROL_SEED_STEP, people)  # type: ignore[operator]
    control_meta = META[(kind, rows, seed + CONTROL_SEED_STEP, people)]
    persons = (
        [body[row][header.index("patient_ref")] for row in range(len(body))]
        if "patient_ref" in header
        else [meta["__persons__"][f"{row}"][0] for row in range(len(body))]
    )
    counting = time.perf_counter()
    # ...the cells of the columns published by design (the residual and the
    # price): a string a held column's cell holds that one of these holds too
    # is shown for that column, not the held one, so it is counted apart
    # (`needles_shared`) and the strings the verdict reads are the others
    # (Codex's item 7 of lane CZ-E's review, the orchestrator's LANE CZ-E
    # RULINGS 6 (7)).
    by_design: "set[str]" = set()
    for column in OPEN.get(kind, ()) + PRICE.get(kind, ()):
        at_design = header.index(column)
        by_design.update(row[at_design] for row in body if row[at_design])
    for column in placed(kind):
        place = header.index(column)
        holders: "dict[str, set[str]]" = {}
        for row in range(len(body)):
            cell = body[row][place]
            if cell:
                holders.setdefault(cell, set()).add(persons[row])
        at = twin_header.index(column) if column in twin_header else -1
        cells = [row[at] for row in twin_rows if at < len(row)] if at >= 0 else []
        entry: "dict[str, object]" = {
            "role_first": first_roles.get(column), "role": (described.get(column) or {}).get("role"),
            "asked": put.get(column, []), "saw": saw.get(column, []), "forms": {},
            "levels_past_89": levels_past_89(described.get(column) or {}),
        }
        groups: "dict[str, dict[str, object]]" = {}
        for cell, (form, needles) in (meta.get(column) or {}).items():
            if not needles or cell not in holders:
                continue
            key = f"{form}|{'many' if len(holders[cell]) >= zoo.FLOOR else 'few'}"
            group = groups.setdefault(key, {"cells": set(), "needles": set()})
            group["cells"].add(cell)  # type: ignore[attr-defined]
            group["needles"].update(needles)  # type: ignore[attr-defined]
        every_needle = {needle for _cell, (_form, needles) in (meta.get(column) or {}).items() for needle in needles}
        tagged: "list[tuple[str, str]]" = []
        shared: "dict[str, int]" = {}
        short: "dict[str, int]" = {}
        for key, group in sorted(groups.items()):
            form = key.split("|")[0]
            own = [one for one in sorted(group["needles"])  # type: ignore[call-overload]
                   if not any(one in cell for cell in by_design)]
            shared[key] = len(group["needles"]) - len(own)  # type: ignore[arg-type]
            short[key] = len([one for one in own if not distinctive(one)])
            tagged += [(f"{key}|cell", one) for one in sorted(group["cells"])]  # type: ignore[call-overload]
            tagged += [(f"{key}|needle", one) for one in own if distinctive(one)]
            tagged += [(f"{key}|control", one) for one in sorted({
                needle for _cell, (other, strings) in (control_meta.get(column) or {}).items() if other == form
                for needle in strings
            } - every_needle)]
        published, by_tag = tagged_hits(tagged, texts, cells)
        for key, group in sorted(groups.items()):
            real = sorted(group["cells"])  # type: ignore[call-overload]
            known = set(real)
            entry["forms"][key] = {  # type: ignore[index]
                "cells": len(real),
                "shown": len([1 for tag, _one in published if tag == f"{key}|cell"]),
                "needles": len(group["needles"]) - shared[key] - short[key],  # type: ignore[arg-type]
                "needles_shared": shared[key],
                "needles_short": short[key],
                "needles_shown": len([1 for tag, _one in published if tag == f"{key}|needle"]),
                "twin_equal": len([cell for cell in cells if cell in known]),
                "twin_needles": by_tag.get(f"{key}|needle", 0),
                "runs": forms.complete_tokens(real, cells),
                "control_needles_shown": len([1 for tag, _one in published if tag == f"{key}|control"]),
                "control_twin_cells": by_tag.get(f"{key}|control", 0),
            }
        found["columns"][column] = entry  # type: ignore[index]
    found["counting_seconds"] = round(time.perf_counter() - counting, 1)
    return found


# -- THE GENERATED SPELLINGS (plan P4-D472): every form from a grammar written here, in thousands --------
#
# THE INDEPENDENT GRAMMAR (the orchestrator's LANE CZ-E RULINGS 3 (6)): no
# generator below iterates a reader's own list -- its layouts, titles or
# words; each writes its form from the grammar its docstring states, with
# lists written here letter by letter. A form's families the readers do
# not read are kept apart (`open_families`): their misses are counted and
# stated as limits in plan P4-D472, never asserted read; and the claim
# that a reader's reach is closed at the unit level is made for the
# generated spellings alone.

SWEEP_TEMPLATES = ("seen {x} in clinic", "{x} per note", "per {x}", "note: {x}; done")
MONTH_NAMES = ("January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
               "November", "December")
# The odd spaces a word processor, a form or a web page writes between
# words (every Unicode space, zero-width and format space: tab, newline,
# carriage return, form feed, vertical tab, U+0085, U+00A0, U+1680, U+2000
# to U+200F, U+2028, U+2029, U+202F, U+205F, U+2060, U+3000, U+FEFF) and
# its odd dashes (hyphen, non-breaking hyphen, figure dash, en dash, em
# dash, minus sign, small and full-width hyphen-minus).
ODD_SPACES = (
    "\t", "\n", "\r", "\x0b", "\x0c", "\x85", "\xa0", "\u1680", "\u2000", "\u2001", "\u2002", "\u2003", "\u2004",
    "\u2005", "\u2006", "\u2007", "\u2008", "\u2009", "\u200a", "\u200b", "\u200c", "\u200d", "\u200e", "\u200f",
    " ", " ", " ", " ", "⁠", "　", "﻿",
)
ODD_DASHES = ("\u2010", "\u2011", "\u2012", "\u2013", "\u2014", "\u2212", "\ufe63", "\uff0d")


def _cased(word: str) -> "tuple[str, ...]":
    """A month's name in title case, capitals and small letters -- but `may` in small letters, the verb."""
    return (word, word.upper(), word.lower()) if word.lower().rstrip(".") != "may" else (word, word.upper())


def _valid_days(month: int) -> "tuple[int, ...]":
    """The days of a month a sweep writes: 1, 12, 13 and the month's last."""
    last = 29 if month == 2 else 30 if month in (4, 6, 9, 11) else 31
    return (1, 12, 13, last)


# The marks of a date in figures: the slash, the hyphen and the point, a
# slash between spaces, and the odd dashes.
DATE_FIGURE_MARKS = ("/", "-", ".", " / ", "/ ", " /") + ODD_DASHES


def month_and_day_spellings() -> "list[str]":
    """Every spelling of a month and a day of the grammar, inside a remark: in figures -- month and day (the day first where it passes 12) with a slash, a slash between spaces or none of the dashes (a hyphen or a point writes a range or a decimal); month, day and a year of two figures, or a year of four figures first or last, with every mark of `DATE_FIGURE_MARKS`; a range of two dates (`3/14-3/21`, `3/14 - 3/21`, `3/14\u20133/21`) -- and with the month's name (three letters, a point after them or not, or whole; title case, capitals or small letters but `may`) before or after the day, an ordinal's ending or not, a space, a hyphen, a point, a comma, no mark or an odd space or dash between; `14th of March`, `14-Mar-2031`, `Mar 14, 2031`."""
    found: "list[str]" = []
    for month in range(1, 13):
        for day in _valid_days(month):
            written: "list[str]" = []
            for mark in ("/", " / ", "/ ", " /"):
                written += [f"{month}{mark}{day}", f"{month:02d}{mark}{day:02d}"]
                if day > 12:
                    written += [f"{day}{mark}{month}"]
            for mark in DATE_FIGURE_MARKS:
                for year in (f"{31:02d}", "2031"):
                    written += [f"{month}{mark}{day}{mark}{year}", f"{month:02d}{mark}{day:02d}{mark}{year}"]
                    if day > 12:
                        written += [f"{day}{mark}{month}{mark}{year}"]
                written += [f"2031{mark}{month:02d}{mark}{day:02d}"]
            later = day + 1 if day < 28 else 1
            for join in ("-", " - ", "\u2013", " to ", " thru "):
                written += [f"{month}/{day}{join}{month}/{later}"]
            # ...six figures glued (month, day, year; day, month, year; year,
            # month, day) and a year of two figures past 31 first, each read
            # where the zoo prices it at no false alarm (RULINGS 3 (5)).
            written += [f"{month:02d}{day:02d}31", f"{day:02d}{month:02d}31", f"31{month:02d}{day:02d}"]
            for mark in ("-", ".", "/"):
                written += [f"{45 + month}{mark}{month:02d}{mark}{day:02d}"]
            for name in (MONTH_NAMES[month - 1][:3], MONTH_NAMES[month - 1][:3] + ".", MONTH_NAMES[month - 1]):
                for spelled in _cased(name):
                    for ordinal in ("", "st" if day in (1, 31) else "th"):
                        for between in (" ", "-", ", ", "", "\xa0", "\u2011"):
                            if spelled.endswith(".") and between == "":
                                continue
                            written += [f"{spelled}{between}{day}{ordinal}", f"{day}{ordinal}{between}{spelled}"]
                        written += [f"{day}{ordinal} of {spelled}"]
                    written += [f"{day}-{spelled}-2031", f"{spelled} {day}, 2031"]
            for one in written:
                for template in SWEEP_TEMPLATES:
                    found += [template.format(x=one)]
    return found


# The prefixes of a ten-figure telephone number (a country's code `1`,
# `+` or not, a mark or none after it), the marks between its groups, and
# the extensions after it.
PHONE_PREFIXES = ("", "1 ", "1-", "1.", "1", "+1 ", "+1-", "+1.", "+1")
PHONE_MARKS = (" ", "-", ".", "/", " - ", "", "\u2013", "\u2011", "\u2212", "\xa0", "\u202f")
PHONE_EXTENSIONS = ("", " x12", " ext 345", " ext. 9")
PHONE_PLACES = ("son {x}", "{x} (home)", "call {x} if rash")


def telephone_spellings() -> "list[str]":
    """Every telephone number of the grammar, inside a remark with or without a word of a telephone: a prefix of `PHONE_PREFIXES`, an area code (three figures, the first 2 to 9) in brackets or not, a mark of `PHONE_MARKS`, an exchange (three figures, the first 2 to 9), a mark of `PHONE_MARKS`, four figures, an extension of `PHONE_EXTENSIONS`; and a local number (an exchange, a hyphen, a point, a space or ` - `, four figures) beside a word of a telephone (`call`, `phone`, `tel`, `cell`, `fax`, `pager`)."""
    found: "list[str]" = []
    draw = random.Random(SEED + 1)
    for _number in range(2):
        area = f"{draw.randint(2, 9)}{draw.randint(0, 9)}{draw.randint(0, 9)}"
        exchange = f"{draw.randint(2, 9)}{draw.randint(0, 9)}{draw.randint(0, 9)}"
        line = f"{draw.randint(0, 9999):04d}"
        for prefix in PHONE_PREFIXES:
            for bracket in (False, True):
                head = f"({area})" if bracket else area
                for first in PHONE_MARKS:
                    for second in PHONE_MARKS:
                        number = f"{prefix}{head}{first}{exchange}{second}{line}"
                        for extension in PHONE_EXTENSIONS:
                            for place in PHONE_PLACES:
                                found += [place.format(x=number + extension)]
        for word in ("call", "phone", "tel", "cell", "fax", "pager", "Call", "PH:"):
            for mark in ("-", ".", " ", " - "):
                found += [f"{word} {exchange}{mark}{line}", f"{exchange}{mark}{line} {word}"]
    return found


def figure_run_spellings() -> "list[str]":
    """Runs of seven to fifteen figures inside a remark: as their own word, after a label glued or not, before a letter."""
    found: "list[str]" = []
    draw = random.Random(SEED + 2)
    for size in range(7, 16):
        for _number in range(30):
            run = f"{draw.randint(1, 9)}" + "".join(f"{draw.randint(0, 9)}" for _place in range(size - 1))
            for written in (run, f"REF{run}", f"#{run}", f"{run}A", f"[{run}]", f"acct:{run}"):
                found += [template.format(x=written) for template in ("ref {x} on file", "{x} sent", "claim {x}")]
    return found


# The titles a name follows that the title reader closes, written here, and
# the spaces that may stand after one (an odd space among them).
TITLES_CLOSED = ("Dr", "Doctor", "Mr", "Mrs", "Ms", "Miss", "Mx", "Prof", "Professor", "Nurse", "Rev", "Fr", "Sr", "Capt")
TITLE_SPACES = (" ", "  ", "\xa0", "\u202f", "\t", "\u2003")


def title_spellings() -> "list[str]":
    """A title of `TITLES_CLOSED` (title case, capitals or small letters, a point after it or not), a space of `TITLE_SPACES`, then a made-up name in title case or capitals, with an apostrophe or a hyphen in it or not, inside a remark."""
    found: "list[str]" = []
    draw = random.Random(SEED + 3)
    names = forms._distinct(draw, 12, lambda d: made_up_word(d, 2))
    for title in TITLES_CLOSED:
        for spelled in (title, title.upper(), title.lower()):
            for point in ("", "."):
                for space in TITLE_SPACES:
                    for name in names:
                        for written_name in (name, name.upper(), f"O'{name}", f"{name}-{names[0]}"):
                            found += [f"per {spelled}{point}{space}{written_name} today",
                                      f"{spelled}{point}{space}{written_name} to review"]
    return found


def initials_spellings() -> "list[str]":
    """Two or three capitals each with its point, a space, an odd space or none between, the last point there or not, inside a remark -- every pair of capitals but those of the closed list of abbreviations (`taxonomy.NOT_INITIALS`, a list of what initials are NOT, so the sweep stays independent of what the reader reads)."""
    from synthtwin import taxonomy

    found: "list[str]" = []
    letters = "ABCDEFGHJKLMNPRSTVWY"
    for first in letters:
        for second in letters:
            pair = first + second
            if pair in taxonomy.NOT_INITIALS:
                continue
            for written in (f"{first}.{second}.", f"{first}. {second}.", f"{first}.{second}", f"{first}.\xa0{second}."):
                found += [f"consent by {written} today", f"per {written}"]
            third = letters[(letters.index(first) + letters.index(second)) % len(letters)]
            if pair + third not in taxonomy.NOT_INITIALS:
                found += [f"signed {first}.{second}.{third}. ok"]
    return found


def family_spellings() -> "list[str]":
    """A made-up family name (title case or capitals, an apostrophe or a hyphen in it or not), a comma with a run of spaces of any length, an odd space or none after it, and one or two initials with their points or not -- or a given name and a middle initial -- alone, in a list, or before more words."""
    found: "list[str]" = []
    draw = random.Random(SEED + 4)
    names = forms._distinct(draw, 60, lambda d: made_up_word(d, 3))
    given = forms._distinct(draw, 10, lambda d: made_up_word(d, 2))
    for place, name in enumerate(names):
        for family in (name, name.upper(), f"O'{name}", f"{name}-{names[(place + 1) % len(names)]}"):
            # ...any run of spaces after the comma (Codex's item 6 of lane
            # CZ-E's review: `Smith,   J scheduled`), odd ones among them.
            for comma in (", ", ",", ",\xa0", ",\u202f", ",   ", ",      ", ", \xa0 ", ",\u2003\u2003"):
                for after in ("K", "K.", "KT", "K.T.", f"{given[place % len(given)]} Q",
                              f"{given[place % len(given)].upper()} Q."):
                    item = f"{family}{comma}{after}"
                    found += [item, f"{item}; {names[(place + 2) % len(names)]}, A", f"{item} - knee scope"]
    return found


# The words naming a relative or a companion that the relative reader
# closes, written here.
RELATIVES_CLOSED = (
    "son", "daughter", "wife", "husband", "spouse", "partner", "mother", "father", "mom", "mum", "dad", "sister",
    "brother", "sibling", "aunt", "uncle", "niece", "nephew", "cousin", "grandson", "granddaughter", "grandmother",
    "grandfather", "grandma", "grandpa", "stepson", "stepdaughter", "stepmother", "stepfather", "guardian",
    "caregiver", "friend", "neighbor", "neighbour", "fiance", "fiancee", "boyfriend", "girlfriend", "roommate",
    "sponsor",
)


# Names of two letters, a capital and a small letter or two capitals,
# written here (Codex's item 6 of lane CZ-E's review: `wife Jo notified`).
TWO_LETTER_NAMES = ("Jo", "Li", "Al", "Ed", "Bo", "Ty", "Vi", "Lu", "Mo", "Ky", "JO", "LI")


def relative_spellings() -> "list[str]":
    """A word of `RELATIVES_CLOSED` (small letters or title case) before a made-up name or a name of two letters (`TWO_LETTER_NAMES`), a space, two, three or an odd space between, inside a remark."""
    found: "list[str]" = []
    draw = random.Random(SEED + 5)
    names = forms._distinct(draw, 8, lambda d: made_up_word(d, 2))
    for word in RELATIVES_CLOSED:
        for spelled in (word, word.capitalize()):
            for space in (" ", "  ", "   ", "\xa0", "\u202f"):
                for name in names + list(TWO_LETTER_NAMES[::3]):
                    found += [f"{spelled}{space}{name} at bedside", f"per {spelled}{space}{name} {names[0]}",
                              f"{spelled}:{space}{name}"]
            for name in TWO_LETTER_NAMES:
                found += [f"{spelled} {name} notified", f"per {spelled} {name} today"]
    return found


def _coordinates(draw: random.Random, places: int) -> "tuple[str, str, float, float]":
    north = round(draw.uniform(-89.0, 89.0), places)
    east = round(draw.uniform(-179.0, 179.0), places)
    if abs(north) <= 1.0 and abs(east) <= 1.0:
        east = 45.0 + east
    return f"{north:.{places}f}", f"{east:.{places}f}", north, east


# The marks that may part a latitude and a longitude in one cell.
PAIR_MARKS = (",", ", ", " ,", ";", " ", "  ", "\t", "/", "|", "\xa0")


def coordinate_pair_spellings() -> "list[str]":
    """A latitude and a longitude in one cell: three to seven places, every sign, the latitude first or the longitude first, parted by a mark of `PAIR_MARKS`, in brackets or `POINT( )` or neither; a degree's mark and a hemisphere's letter after each, or the hemisphere's letter before each."""
    found: "list[str]" = []
    draw = random.Random(SEED + 6)
    for places in range(3, 8):
        for _point in range(6):
            first, second, north, east = _coordinates(draw, places)
            for left, right in ((first, second), (second, first)):
                for mark in PAIR_MARKS:
                    pair = f"{left}{mark}{right}"
                    found += [pair, f"({pair})", f"[{pair}]", f"POINT({pair})", f"POINT ({pair})"]
            bare_north, bare_east = f"{abs(north):.{places}f}", f"{abs(east):.{places}f}"
            north_side, east_side = ("N" if north >= 0 else "S"), ("E" if east >= 0 else "W")
            found += [f"{bare_north}\xb0 {north_side}, {bare_east}\xb0 {east_side}",
                      f"{north_side}{bare_north} {east_side}{bare_east}", f"{north_side}{bare_north}, {east_side}{bare_east}"]
    return found


def coordinate_pair_in_words_spellings() -> "list[str]":
    """A latitude and a longitude standing among words, in EVERY spelling a cell of its own admits (`coordinate_pair_spellings`: a degree's mark and a hemisphere's letter after each, `POINT( )`, brackets; Codex's item 5 of lane CZ-E's review, the orchestrator's LANE CZ-E RULINGS 6 (5)): after a word or inside a remark, punctuation around them or not (`home 41.66123,-91.53210`, `at 41.66123, -91.53210 now`, `pt at N41.66123 W91.53210.`, `home 41.66123\xb0 N, 91.53210\xb0 W`), each number after a label glued by `=` or `:` (`lat=41.66123, lon=-91.53210`), the hemisphere's letter after each number apart (`home 41.66123 N, 91.53210 W`), or with a longitude's word between them (`lat 41.66123 lon -91.53210`)."""
    found: "list[str]" = []
    for pair in coordinate_pair_spellings():
        for template in ("home {x}", "at {x} now", "seen near ({x}) today", "loc: {x}.", "GPS {x}, ok"):
            found += [template.format(x=pair)]
    draw = random.Random(SEED + 11)
    for places in range(3, 8):
        for _point in range(20):
            first, second, north, east = _coordinates(draw, places)
            for between in ("lon", "lon:", "long", "lng", "LON"):
                found += [f"lat {first} {between} {second}", f"seen at lat: {first}, {between} {second} today"]
            for one, two in (("lat", "lon"), ("latitude", "longitude"), ("LAT", "LNG"), ("pt_lat", "pt_lon2")):
                for glue in ("=", ":"):
                    found += [f"{one}{glue}{first}, {two}{glue}{second}", f"at {one}{glue}{first} {two}{glue}{second} now"]
            bare_north, bare_east = f"{abs(north):.{places}f}", f"{abs(east):.{places}f}"
            north_side, east_side = ("N" if north >= 0 else "S"), ("E" if east >= 0 else "W")
            found += [f"home {bare_north} {north_side}, {bare_east} {east_side}",
                      f"home {bare_north}{north_side}, {bare_east}{east_side} today"]
    return found


def network_address_spellings() -> "list[str]":
    """Dotted addresses (four groups of 0 to 255, a port or a prefix after them or not), colon addresses (eight groups, or fewer around one `::`, a dotted address last or not, in brackets with a port, a zone after `%`) and hardware addresses (six groups of two by colons, hyphens or odd dashes, three of four by points)."""
    found: "list[str]" = []
    draw = random.Random(SEED + 7)
    for _address in range(400):
        groups = [draw.randint(0, 255) for _place in range(4)]
        dotted = ".".join(f"{group}" for group in groups)
        found += [dotted, f"{dotted}:{draw.randint(1, 65535)}", f"{dotted}/{draw.randint(8, 32)}"]
        hexes = [f"{draw.randint(0, 65535):x}" for _place in range(8)]
        cut = draw.randint(1, 6)
        found += [":".join(hexes), ":".join(hexes).upper(), ":".join(hexes[:cut]) + "::" + ":".join(hexes[cut + 1:]),
                  "::" + ":".join(hexes[cut:]), ":".join(hexes[:cut]) + "::", f"[{':'.join(hexes[:cut])}::1]:443",
                  f"fe80::{hexes[0]}%eth0", f"::ffff:{dotted}"]
        pairs = [f"{draw.randint(0, 255):02x}" for _place in range(6)]
        found += [":".join(pairs), "-".join(pairs).upper(), draw.choice(ODD_DASHES).join(pairs)]
        dotted_pairs = ".".join("".join(pairs[at:at + 2]) for at in (0, 2, 4))
        if any(character.isalpha() for character in dotted_pairs):
            # ...three groups of four parted by points hold a letter: twelve
            # figures so parted are read as no address (a number in groups).
            found += [dotted_pairs]
    return found


def network_address_in_words_spellings() -> "list[str]":
    """A network address standing among words: after a label (`IP `, `IP: `, `IP:`, `ip=`), inside a remark, in a link, punctuation around it or not -- every form the address reader admits among them, letters alone too (`network_address_forms`; Codex's item 4 of lane CZ-E's review)."""
    found: "list[str]" = []
    for address in network_address_spellings()[::3] + network_address_forms()[::5]:
        for template in ("IP {x}", "IP: {x}", "IP:{x}", "ip={x}", "login from {x} today", "seen ({x}), ok",
                         "host {x}.", "via http://{x}/path", "client_ip={x}", "src_ip2:{x} ok"):
            if "[" in address and "http" in template:
                continue
            found += [template.format(x=address)]
    return found


# THE STATES' TWO-FIGURE CODES A CENSUS WRITES, frozen here letter by letter
# (Codex's item 9 of lane CZ-E's review, the orchestrator's LANE CZ-E
# RULINGS 6 (7): the sweep read the reader's own list, so a state taken
# from it took its forty cases with it): 01 to 56 with the census's gaps
# (03, 07, 14, 43 and 52 name no state), and five territories.
STATE_CODES_WRITTEN = (
    "01", "02", "04", "05", "06", "08", "09", "10", "11", "12", "13", "15", "16", "17", "18", "19", "20", "21", "22",
    "23", "24", "25", "26", "27", "28", "29", "30", "31", "32", "33", "34", "35", "36", "37", "38", "39", "40", "41",
    "42", "44", "45", "46", "47", "48", "49", "50", "51", "53", "54", "55", "56", "60", "66", "69", "72", "78",
)


def provider_check_passes(figures: str) -> bool:
    """The KPI's own check of a provider's ten-figure number (Luhn's sum over the card issuer's prefix 80840 and the ten figures, a multiple of ten), written here apart from the product's (RULINGS 6 (7))."""
    written = "80840" + figures
    total = 0
    for place, character in enumerate(reversed(written)):
        figure = int(character)
        if place % 2 == 1:
            figure = figure * 2 - (9 if figure * 2 > 9 else 0)
        total += figure
    return total % 10 == 0


def area_code_spellings() -> "list[str]":
    """Codes of an area smaller than a state for every state's two-figure code (`STATE_CODES_WRITTEN`, frozen here): a tract's eleven figures, a block group's twelve, and, for a state of one figure from 2 to 9, the ten left when the nought is lost where the KPI's own check (`provider_check_passes`) says they are no provider's number."""
    found: "list[str]" = []
    draw = random.Random(SEED + 8)
    for state in STATE_CODES_WRITTEN:
        for _code in range(20):
            tract = f"{state}{draw.randrange(1, 840, 2):03d}{draw.randint(100, 999999):06d}"
            found += [tract, tract + f"{draw.randint(1, 9)}"]
            if state[0] == "0" and state[1] in "23456789" and not provider_check_passes(tract[1:]):
                found += [tract[1:]]
    return found


def provider_numbers_like_areas() -> "list[str]":
    """Ten figures opening as a state of one figure that lost its nought would, which ARE a provider's number by the KPI's own check: read as no area's code (red where the product's check passes them)."""
    found: "list[str]" = []
    draw = random.Random(SEED + 12)
    while len(found) < 200:
        figures = f"{draw.choice('2456789')}{draw.randint(0, 999999999):09d}"
        if provider_check_passes(figures) and ("0" + figures[0]) in STATE_CODES_WRITTEN:
            found += [figures]
    return found


def serial_number_spellings() -> "list[str]":
    """Device serial numbers in many makers' layouts: one to four capitals and six to twelve figures, figures and a check capital, capitals between figure groups, and two to four groups joined by dashes or odd dashes."""
    found: "list[str]" = []
    draw = random.Random(SEED + 9)
    for _serial_place in range(300):
        figures = "".join(f"{draw.randint(0, 9)}" for _place in range(draw.randint(6, 12)))
        letters = "".join(draw.choice(CAPITALS) for _place in range(draw.randint(1, 4)))
        dash = draw.choice(("-",) + ODD_DASHES)
        found += [letters + figures, figures + letters[:1], figures[:3] + letters + figures[3:],
                  f"{letters}{dash}{figures}", f"{letters[:1]}{figures[:1]}-{figures[1:5]}-{figures[5:]}",
                  f"{figures[:4]}-{letters}-{figures[4:]}", f"SN{figures}"]
    return found


# The words and marks a band of ages is written with, written here.
BAND_JOINS = ("-", "\u2013", " - ", " to ", "\u2011", "\u2212")
BAND_UNITS = ("", " yrs", " years", "y", " y/o", " yo", " years old")
BAND_UPWARD_AFTER = ("+", " +", " and over", " and older", " or older", " or more", " and up", " & over", " & older",
                     " & above", " or above", " or greater", " and greater", "up")


def age_band_spellings() -> "list[tuple[str, int, int]]":
    """Bands of ages from 0 to 120 with their first and last age (-1 open upward): closed five- and ten-year bands joined by a mark or a word of `BAND_JOINS`, a unit word of `BAND_UNITS` after them or not, `age` before them or not; intervals in brackets (`[90, 95)`, `(89, 94]`, `[90-95)`); and bands open upward after `>=`, `>`, `\u2265` or `over`, or before a mark or a word of `BAND_UPWARD_AFTER`."""
    found: "list[tuple[str, int, int]]" = []
    for start in range(0, 121, 5):
        for width in (4, 9):
            end = start + width
            if end > 125:
                continue
            for join in BAND_JOINS:
                for unit in BAND_UNITS:
                    for opening in ("", "age ", "Ages "):
                        found += [(f"{opening}{start}{join}{end}{unit}", start, end)]
            if end + 1 <= 125:
                found += [(f"[{start}, {end + 1})", start, end), (f"[{start}-{end + 1})", start, end)]
            if start >= 1:
                found += [(f"({start - 1}, {end}]", start, end)]
        for unit in ("", " yrs", " years"):
            found += [(f">= {start}{unit}", start, -1), (f">={start}{unit}", start, -1), (f"≥{start}{unit}", start, -1),
                      (f"over {start}{unit}", start + 1, -1), (f"> {start}{unit}", start + 1, -1)]
        for after in BAND_UPWARD_AFTER:
            found += [(f"{start}{after}", start, -1)]
    return found + downward_band_spellings()


# A band open downward: a strict bound (it ends one below its age) and an
# inclusive one (it holds its age), written here (Codex's item 1 of lane
# CZ-E's review, the orchestrator's LANE CZ-E RULINGS 6 (1)).
BAND_DOWN_STRICT = ("<", "< ", "under ", "Under ", "UNDER ", "below ", "Below ", "less than ", "Less than ")
BAND_DOWN_INCLUSIVE = ("<=", "<= ", "=<", "≤", "≤ ")


def downward_band_spellings() -> "list[tuple[str, int, int]]":
    """Bands open downward from every age of 1 to 125, each with its first and last age: after a strict bound of `BAND_DOWN_STRICT` (`<90` holds 0 to 89) or an inclusive one of `BAND_DOWN_INCLUSIVE` (`<= 90` holds 0 to 90), a unit word of years after it or not, `age` before it or not."""
    found: "list[tuple[str, int, int]]" = []
    for age in range(1, 126):
        for unit in ("", " yrs", " years"):
            for opening in ("", "age "):
                for mark in BAND_DOWN_STRICT:
                    found += [(f"{opening}{mark}{age}{unit}", 0, age - 1)]
                for mark in BAND_DOWN_INCLUSIVE:
                    found += [(f"{opening}{mark}{age}{unit}", 0, age)]
    return found


def odd_mark_spellings() -> "list[str]":
    """Every word form's remark with the odd marks in every position (the orchestrator's LANE CZ-E RULINGS 3 (4)): each odd space for each space between words, alone, doubled and beside a plain space, and all at once, leading and trailing; each odd dash for each hyphen of a telephone number or a date, alone and all at once."""
    bases = (
        "per Dr Gapesam today", "Mrs Lomo notified", "son Kukun at bedside", "wife Mara notified",
        "seen by Lanezon, A today", "consent by K. T. today", "seen Mar 14 in clinic", "call 319-555-0123 if rash",
        "moved to 3-14-31 today", "resume 2031-03-14 ok", "login from 192.0.2.17 today", "home 41.66123,-91.53210 now",
        "son 319-555-0123", "ref 76030298 on file",
    )
    found: "list[str]" = []
    for base in bases:
        spaces = [place for place, character in enumerate(base) if character == " "]
        dashes = [place for place, character in enumerate(base) if character == "-"]
        for odd in ODD_SPACES:
            for place in spaces:
                for written in (odd, odd + odd, odd + " ", " " + odd):
                    found += [base[:place] + written + base[place + 1:]]
            found += [base.replace(" ", odd), odd + base, base + odd, odd + base.replace(" ", odd) + odd]
        for odd in ODD_DASHES:
            for place in dashes:
                found += [base[:place] + odd + base[place + 1:]]
            if dashes:
                found += [base.replace("-", odd)]
    return found


def score_columns() -> "list[list[str]]":
    """Columns of scores out of four, five, six or ten written after a word (`pain 7/10`, `motor 3/5`, `murmur grade 2/6`), every score of the scale (the statistics check's generated family, written here)."""
    return [[f"{word} {over}/{under}" for over in range(0, under + 1)]
            for word in ("pain", "Pain score", "strength", "motor", "murmur grade", "reflexes", "effort")
            for under in (4, 5, 6, 10)]


# The common clinical abbreviations written with points (the statistics
# check's generated family), each before a word: those of three letters or
# more the closed list holds, and those of two, a person's two initials'
# form, which stay read (plan P4-D472 (c)).
CLINICAL_ABBREVIATIONS = (
    "I.C.U.", "A.M.A.", "U.T.I.", "D.O.A.", "C.H.F.", "E.M.S.", "S.L.P.", "A.D.L.", "R.O.M.", "B.M.I.", "C.P.R.",
    "D.V.T.", "H.T.N.", "I.V.F.", "L.O.C.", "M.V.A.", "N.K.A.", "P.C.P.", "R.L.E.", "R.O.S.", "S.O.B.", "T.K.A.",
    "T.H.A.", "U.R.I.", "W.N.L.", "C.B.C.", "B.M.P.", "E.E.G.", "E.M.G.", "P.F.T.", "T.P.N.", "P.E.G.", "A.B.G.",
)
TWO_LETTER_ABBREVIATIONS = ("P.T.", "O.T.", "P.E.", "R.T.", "N.G.", "O.G.", "G.T.")


def abbreviation_capitals(codes: "tuple[str, ...]" = CLINICAL_ABBREVIATIONS) -> "frozenset[str]":
    """Each clinical abbreviation of ``codes`` as the closed list holds it, its capitals alone."""
    return frozenset(code.replace(".", "") for code in codes)


def dotted_abbreviation_spellings(codes: "tuple[str, ...]" = CLINICAL_ABBREVIATIONS) -> "list[str]":
    """Each clinical abbreviation of ``codes``, written with its points, before a word."""
    return [code + " " + word for code in codes for word in ("eval", "consult", "ordered", "done")]


# THE FAMILIES THE READERS DO NOT READ (stated in plan P4-D472, never
# asserted read): each written from its own grammar, so its misses are
# counted by family.
def open_families() -> "dict[str, list[str]]":
    """Each family of a form the readers leave open, its spellings inside remarks (a pair, an address or a band alone in its cell), keyed by the family's name; `OPEN_READERS` names the reader each is read by."""
    found: "dict[str, list[str]]" = {}
    draw = random.Random(SEED + 10)
    names = forms._distinct(draw, 10, lambda d: made_up_word(d, 3))
    dates: "list[str]" = []
    for month in range(1, 13):
        for day in _valid_days(month):
            dates += [f"{day:02d}.{month:02d}.", f"{MONTH_NAMES[month - 1]} the {day}th", f"{day} de {MONTH_NAMES[month - 1].lower()}"]
    found["a day and a month with a trailing point, `the`, `de`"] = [f"seen {one} in clinic" for one in dates]
    found["titles outside the closed list"] = [
        f"per {title} {name} today" for title in ("Dra.", "Sra.", "Pastor", "Rabbi", "Sgt", "Lt", "Hon", "RN")
        for name in names
    ]
    found["initials with no points or in small letters"] = [
        f"consent by {written} today" for written in ("KT", "K T", "k.t.", "kt", "K.-T.", "K/T") for _name in names
    ]
    found["a family and a given name, no middle initial"] = [f"seen by {name}, {names[0]} today" for name in names]
    found["a local number beside no word of a telephone"] = [f"son 555-01{place:02d}" for place in range(20)]
    found["a coordinate pair of two places"] = [f"{40 + place / 7:.2f},{-91 - place / 3:.2f}" for place in range(20)]
    found["a pair with a decimal comma"] = [f"{40 + place},{place}1234 -91,{place}5678" for place in range(10)]
    found["a hardware address of twelve figures, no marks"] = [f"{draw.randint(0, 2 ** 48):012x}" for _place in range(20)]
    found["an address glued to a word"] = [f"IP192.0.2.{place}" for place in range(1, 21)]
    found["bands in another language"] = [f"{start}-{start + 4} {word}" for start in range(90, 105, 5)
                                          for word in ("a\xf1os", "ans", "Jahre", "anos")]
    found["bands joined by `a` or `bis`"] = [f"{start} {word} {start + 4}" for start in range(90, 105, 5) for word in ("a", "bis")]
    return found


# The reader each open family is read by: the identifier words of a
# remark, or the cell form of a pair, an address or a band.
OPEN_READERS = {
    "a coordinate pair of two places": "pair", "a pair with a decimal comma": "pair",
    "a hardware address of twelve figures, no marks": "address", "an address glued to a word": "address",
    "bands in another language": "band", "bands joined by `a` or `bis`": "band",
}


# What no reader may read (the price, at the unit level): remarks and
# labels a health table writes that hold no identifier.
PLAIN_LEVELS = PLAIN_REMARKS + PLAIN_TEMPLATES + PROCEDURES + (
    "Black or African American", "Cancelled by Patient", "Transfer to Other Facility", "consult Cardiology",
    "seen by Cardiology", "Pain, chest", "takes 1-2 tabs", "range 500-1000 mg", "BP 120/80 noted", "ver 3.14 ok",
    "pt N.P.O. since midnight", "given P.O. B.I.D.", "e.g. later", "seen at 9 A.M.", "U.S. citizen",
    "dose 2.5 mg", "Grade 3 of 4", "ward day 12", "follow up in 2 weeks", "Stage IIB", "sent to Radiology",
    "room 1204", "call back tomorrow", "Dr on call", "lab 12345-6 pending",
)


# -- THE SECOND REPAIR'S GENERATED FORMS (the orchestrator's LANE CZ-E RULINGS 6 and 7) --


def date_remark_columns() -> "list[tuple[list[str], list[str]]]":
    """Columns of date remarks whose dates share days, as a column of visits writes them (the combined verify's item 1, its own shapes widened), each (its levels, its date remarks): the 48 dates of four days in every month, month first and day first; 200 columns of 30 dates drawn at random, each in a remark of `SWEEP_TEMPLATES` and a mark of its own; every spelling of `month_and_day_spellings` in one column a template; and dates beside every score of `score_columns` that shares their figures (the scores themselves no date remark)."""
    columns: "list[list[str]]" = [
        [f"seen {month}/{day}" for month in range(1, 13) for day in (3, 8, 14, 21)],
        [f"seen {day}/{month}" for month in range(1, 13) for day in (13, 18, 24, 28)],
    ]
    draw = random.Random(SEED + 13)
    for _column in range(200):
        template = draw.choice(SWEEP_TEMPLATES)
        mark = draw.choice(("/", " / ", "/ "))
        columns += [sorted({template.format(x=f"{draw.randint(1, 12)}{mark}{draw.randint(1, 28)}")
                            for _date in range(30)})]
    spelled = month_and_day_spellings()
    for template in SWEEP_TEMPLATES:
        head, tail = template.split("{x}")
        columns += [[text for text in spelled if text.startswith(head) and text.endswith(tail)][:8000]]
    found = [(column, column) for column in columns]
    for scale in score_columns()[:8]:
        under = scale[-1].split("/")[-1]
        dates = [f"seen {over}/{under} in clinic" for over in range(1, min(int(under), 12) + 1)]
        found += [(scale + dates, dates)]
    return found


# The prefixes of an international number (a country's code of one to three
# figures after `+`), its bracketed groups (a trunk nought, an area code)
# and the marks between its groups, written here (Codex's item 6 of lane
# CZ-E's review: `call +44 (0)20 7946 0958`, `contact +44 (20) 7946 0958`).
INTERNATIONAL_CODES = ("+44", "+33", "+49", "+353", "+61", "+7", "+972", "+81", "+52")
INTERNATIONAL_MARKS = (" ", "-", ".")


def international_telephone_spellings() -> "list[str]":
    """International numbers with a bracketed group: a country's code of `INTERNATIONAL_CODES`, a space or none, a trunk nought `(0)` with the next group glued to it or after a mark, or an area code of two to four figures in brackets, then two groups of three or four figures parted by a mark of `INTERNATIONAL_MARKS`, inside a remark."""
    found: "list[str]" = []
    draw = random.Random(SEED + 14)
    for code in INTERNATIONAL_CODES:
        for after_code in (" ", ""):
            for mark in INTERNATIONAL_MARKS:
                area = f"{draw.randint(1, 9)}{draw.randint(0, 9)}"
                first, second = f"{draw.randint(100, 9999)}", f"{draw.randint(1000, 9999)}"
                for bracket in (f"(0){area}", f"(0){mark}{area}", f"({area})", f"(0{area})", f"({area}{draw.randint(0, 9)})"):
                    number = f"{code}{after_code}{bracket}{mark}{first}{mark}{second}"
                    for template in ("call {x}", "contact {x}", "{x} (mobile)", "son abroad {x} today"):
                        found += [template.format(x=number)]
    return found


def network_address_forms() -> "list[str]":
    """Every form the address reader admits, as its grammar writes it (Codex's item 4 of lane CZ-E's review, the orchestrator's LANE CZ-E RULINGS 6 (4)): hardware addresses of six groups of two by colons, hyphens or odd dashes and of three groups of four by points, in letters alone, figures alone where the marks are colons or hyphens, or both; colon addresses of eight groups and around `::` (first, inside, last), in letters alone or with figures, a dotted address last or not; and dotted addresses."""
    found: "list[str]" = []
    draw = random.Random(SEED + 15)
    for _address in range(60):
        for pool in ("abcdef", "0123456789", "0123456789abcdef", "ABCDEF"):
            def group(size: int) -> str:
                return "".join(draw.choice(pool) for _place in range(size))

            for mark in (":", "-", "–"):
                found += [mark.join(group(2) for _place in range(6))]
            if pool != "0123456789":
                found += [".".join(group(4) for _place in range(3))]
                eight = [group(draw.randint(1, 4)) for _place in range(8)]
                cut = draw.randint(1, 6)
                found += [":".join(eight), ":".join(eight[:cut]) + "::" + ":".join(eight[cut + 1:]),
                          "::" + ":".join(eight[cut:]), ":".join(eight[:cut]) + "::",
                          ":".join(eight[:6]) + f":{draw.randint(0, 255)}.{draw.randint(0, 255)}.0.{draw.randint(1, 254)}"]
        found += [f"{draw.randint(0, 255)}.{draw.randint(0, 255)}.{draw.randint(0, 255)}.{draw.randint(0, 255)}"]
    return found


# The marks of a column's unit an age band may stand in (`AGE_MARKS`: 90
# years in years, months, weeks and days), written here.
UNIT_MARKS = {"years": 90, "months": 1080, "weeks": 4695, "days": 32871}


def unit_band_columns() -> "list[tuple[list[str], int, bool]]":
    """Columns of bands in each unit (Codex's item 2 of lane CZ-E's review, the orchestrator's LANE CZ-E RULINGS 6 (2)), each with its unit's mark and whether a band of it is past 89 years: five- and ten-year bands of every age to 125 and bands opening at 80 topped `105+`, with no unit word (in the column's unit: past 89 only in years) or with a unit word of years (past 89 whatever the column's unit)."""
    found: "list[tuple[list[str], int, bool]]" = []
    for mark in UNIT_MARKS.values():
        for width in (5, 10):
            for unit in ("", " yrs", " years"):
                cells = [f"{start}-{start + width - 1}{unit}" for start in range(0, 120, width)] + [f"120+{unit}"]
                found += [(cells, mark, mark == 90 or bool(unit))]
        for unit in ("", " y"):
            cells = ["80-89", "90-94", "95-99", "100-104", "105+"]
            found += [([cell + unit for cell in cells], mark, mark == 90 or bool(unit))]
    return found


# The adult groups of the combined verify's item 2 (groups of unequal widths
# opening at 16, 18 or 21 under no unit word, and `75-99` beside `100+`),
# each with the one band it pools from (RULINGS 7 (3)).
ADULT_SCHEMES = (
    (["18-44", "45-64", "65-89", "90-94", "95-99", "100+"], 90),
    (["21-39", "40-59", "60-74", "75-89", "90-94", "95-99", "100+"], 90),
    (["16-24", "25-44", "45-64", "65-89", "90-94", "95-99", "100+"], 90),
    (["18-44", "45-59", "60-74", "75-99", "100+"], 75),
    (["18-24", "25-34", "35-44", "45-54", "55-64", "65-74", "75-84", "85-89", "90-94", "95-99", "100-104", "105+"], 90),
    (["20-29", "30-49", "50-69", "70-89", "90-99", "100+"], 90),
)


# THE OLD DESCRIPTION OF CODEX'S ITEM 3 (lane CZ-E's review; the orchestrator's
# LANE CZ-E RULINGS 6 (3)): the description the base wrote -- the public
# head's tree, before the band reading -- of a column of ages declared a
# code, 50, 60, 70 and 95 each on 4,950 rows and 95-99 on 200
# (`old_ages_cells`): top-coded, its band published as written beside its
# 90. Kept whole, so a description made before the band reading is shown
# to load and validate as it did; `top_coded_bands` stands in no block of it.
OLD_AGES_DESCRIPTION = "".join((
    '{\n'
    '  "columns": [\n'
    '    {\n'
    '      "detection_evidence": "there are 5 different values, which is within the 1000 a set of categories may have in a table of 20000 rows, so this column is a set of categories",\n'
    '      "level_ceiling": 1000,\n'
    '      "levels": [\n'
    '        {\n'
    '          "count": 4950,\n'
    '          "label": "50",\n'
    '          "shape_form_cells": 0,\n'
    '          "variants": {\n'
    '            "50": 4950\n'
    '          },\n'
    '          "variants_withheld": {}\n'
    '        },\n'
    '        {\n'
    '          "count": 4950,\n'
    '          "label": "60",\n'
    '          "shape_form_cells": 0,\n'
    '          "variants": {\n'
    '            "60": 4950\n'
    '          },\n'
    '          "variants_withheld": {}\n'
    '        },\n'
    '        {\n'
    '          "count": 4950,\n'
    '          "label": "70",\n'
    '          "shape_form_cells": 0,\n'
    '          "variants": {\n'
    '            "70": 4950\n'
    '          },\n'
    '          "variants_withheld": {}\n'
    '        },\n'
    '        {\n'
    '          "count": 4950,\n'
    '          "label": "90",\n'
    '          "shape_form_cells": 0,\n'
    '          "variants": {\n'
    '            "90": 4950\n'
    '          },\n'
    '          "variants_withheld": {}\n'
    '        },\n'
    '        {\n'
    '          "count": 200,\n'
    '          "label": "95-99",\n'
    '          "shape_form_cells": 200,\n'
    '          "variants": {\n'
    '            "95-99": 200\n'
    '          },\n'
    '          "variants_withheld": {}\n'
    '        }\n'
    '      ],\n'
    '      "missing_by_class": {\n'
    '        "(blank)": 0,\n'
    '        "(date-sentinel)": 0,\n'
    '        "(declared-missing)": 0,\n'
    '        "(numeric-sentinel)": 0,\n'
    '        "(text-code)": 0,\n'
    '        "(withheld)": 0\n'
    '      },\n'
    '      "missing_by_source": {},\n'
    '      "n_contradictory": 0,\n'
    '      "n_distinct": 5,\n'
    '      "n_distinct_folded": 5,\n'
    '      "n_missing": 0,\n'
    '      "n_missing_blank": 0,\n'
    '      "n_missing_withheld": 0,\n'
    '      "n_not_numeric": 200,\n'
    '      "n_numeric": 19800,\n'
    '      "n_out_of_range": 0,\n'
    '      "n_present": 20000,\n'
    '      "n_sentinel_candidates_unpublished": 0,\n'
    '      "name": "age",\n'
    '      "position": 1,\n'
    '      "quality_state": "ok",\n'
    '      "remarks": [],\n'
    '      "role": "categorical",\n'
    '      "sentinel_verdicts": [],\n'
    '      "shape_forms": {\n'
    '        "%%-%%": 200\n'
    '      },\n'
    '      "statistical_type": "categorical",\n'
    '      "structural_role": "data",\n'
    '      "suppressed_levels": 0,\n'
    '      "suppressed_numbers": {\n'
    '        "mean": null,\n'
    '        "n_cells": 0\n'
    '      },\n'
    '      "suppressed_rows": 0,\n'
    '      "top_category_pooled": 11,\n'
    '      "top_coded": 90\n'
    '    }\n'
    '  ],\n'
    '  "created_with": "0.1.0.dev0",\n'
    '  "n_columns": 1,\n'
    '  "n_rows": 20000,\n'
    '  "profile_version": 6,\n'
    '  "publication_notes": [],\n'
    '  "relationships": {\n'
    '    "deterministic": null,\n'
    '    "grain": null,\n'
    '    "hierarchy": null,\n'
    '    "keys": null,\n'
    '    "missing_data_process": null,\n'
    '    "statistical": null,\n'
    '    "temporal": null,\n'
    '    "validation_targets": null\n'
    '  },\n'
    '  "settings": {\n'
    '    "categorical_ceiling": 1000,\n'
    '    "categorical_floor": 2,\n'
    '    "categorical_share": 0.1,\n'
    '    "century_windows": [],\n'
    '    "day_first": false,\n'
    '    "declaration_matching": "exact_number_when_it_reads_as_one_else_spelling",\n'
    '    "declaration_publication": "settings_counts_only_columns_unchanged",\n'
    '    "declared_missing_values": {\n'
    '      "built_in_dates": [],\n'
    '      "built_in_numbers": [],\n'
    '      "built_in_texts": [],\n'
    '      "n_declared": 0,\n'
    '      "values_recorded": false\n'
    '    },\n'
    '    "forced_codes": [\n'
    '      "age"\n'
    '    ],\n'
    '    "forced_date_columns": [],\n'
    '    "forced_date_counts": [],\n'
    '    "forced_decimal_commas": [],\n'
    '    "forced_delimiter": "",\n'
    '    "forced_identifiers": [],\n'
    '    "forced_measurements": [],\n'
    '    "forced_metadata_rows": 0,\n'
    '    "forced_twelve_hour_clocks": [],\n'
    '    "identifier_minimum_rows": 20,\n'
    '    "identifier_uniqueness": 0.95,\n'
    '    "kept_values": {\n'
    '      "built_in_dates": [],\n'
    '      "built_in_numbers": [],\n'
    '      "built_in_texts": [],\n'
    '      "n_declared": 0,\n'
    '      "values_recorded": false\n'
    '    },\n'
    '    "long_tail_minimum_level": 11,\n'
    '    "minimum_parse_rate": 0.99,\n'
    '    "near_threshold_slack": 1,\n'
    '    "person_columns": [],\n'
    '    "sentinel_minimum_share": 0.005,\n'
    '    "sentinel_outlier_iqr_multiple": 4.0,\n'
    '    "small_cell_floor": 11\n'
    '  },\n'
    '  "source": {\n'
    '    "dialect": {\n'
    '      "blank_lines": [],\n'
    '      "blank_lines_spread": null,\n'
    '      "byte_order_mark": false,\n'
    '      "columns": [\n'
    '        {\n'
    '          "pad": null,\n'
    '          "quoting": {\n'
    '            "absent": "needed",\n'
    '            "empty": "needed",\n'
    '            "number": "needed",\n'
    '            "text": "needed"\n'
    '          },\n'
    '          "sequence_start": null\n'
    '        }\n'
    '      ],\n'
    '      "delimiter": ",",\n'
    '      "empty_rows": {\n'
    '        "interior": 0,\n'
    '        "leading": 0,\n'
    '        "trailing": 0\n'
    '      },\n'
    '      "end_of_file_mark": false,\n'
    '      "escape": "doubled",\n'
    '      "final_line_ending": true,\n'
    '      "header_quoting": "needed",\n'
    '      "header_rows": [],\n'
    '      "header_rows_quoting": "needed",\n'
    '      "initial_space": false,\n'
    '      "line_endings": [\n'
    '        {\n'
    '          "ending": "lf",\n'
    '          "lines": 20001\n'
    '        }\n'
    '      ],\n'
    '      "line_endings_spread": [],\n'
    '      "preamble": [],\n'
    '      "preamble_withheld": false,\n'
    '      "row_order": null,\n'
    '      "separator_line": false,\n'
    '      "short_rows": false,\n'
    '      "trailing_delimiter": {\n'
    '        "header": false,\n'
    '        "rows": false\n'
    '      },\n'
    '      "written_names": []\n'
    '    },\n'
    '    "encoding": "utf-8-sig",\n'
    '    "header_by_convention": true,\n'
    '    "header_evidence": "The first row was read as the column names by convention, not by evidence: a CSV file is normally written with its column names first, and nothing in this file contradicted that -- no value in the first row belongs among the values of the column below it. synthtwin did not check that those values ARE names, because no such check exists. If that row is really the first record, run the command again with --first-row data: the columns are then named column_1, column_2, and so on and every record is kept.",\n'
    '    "header_source": "file",\n'
    '    "used_fallback_encoding": false,\n'
    '    "workbook": null\n'
    '  }\n'
    '}\n',
))
OLD_AGES_SEED = 20261111


def old_ages_cells() -> "list[str]":
    """The cells the old description (`OLD_AGES_DESCRIPTION`) was made from, in their order."""
    draw = random.Random(OLD_AGES_SEED)
    cells = ["50", "60", "70", "95"] * 4950 + ["95-99"] * 200
    draw.shuffle(cells)
    return cells
