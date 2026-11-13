"""Every identifier shape the twin writes, and whether a twin cell equals a real one (plan P4-D432).

Shared by `tests/test_identifier_room.py` (the gate) and `tools/measurements/kpi_identifier_room.py`
(K-HZ-06's driver), so the gate and the ledger measure the same tables the same way.

THE SHAPES (`SHAPES`), each one column `target` beside a modality and a value, one shape a table:
lane CODES-3's verify 3's table of UIDs (a country branch, a vendor's product arcs, an
organisation root and none, one-figure and two-figure arcs before the instance number, series
of instances, repeated UIDs, pydicom and `2.25.` UIDs of random arcs), record numbers written
as decimals (Cerner's `31000000.00`, three widths, one place, grouped, a person's rows),
record numbers of figures alone (sequential from 1, a person on 3 and on 20 rows, random of 7,
8 and 10 figures, zero-filled, exported as `100000.0`, CSN-like strides, NPI-like numbers with
their Luhn check digit), prefixed ids of several lengths (`PT` and seven figures on one and on
three rows a person, `E` and nine, `P` and five, `QRV` and eight random, two systems, `ABC-`
and four, UUIDs), rsIDs (with and without `.`), and keys beside words and placeholders held
until answered and answered `identifier` (`R1000` to `R1039` alone, beside `Unknown` on two
cells in five, `N/A` on one in five, record numbers beside `-99` or `UNKNOWN`). `CODES3` adds
CODES-3's own gate tables: its PACS study UIDs, its Cerner export's two record numbers, its
flattened VCF's rsIDs and its plain keys beside one word.

WHAT IS COUNTED (`equal_cells`): twin cells of the column, present, whose text is exactly the
text of a present real cell of the same column. Nothing else: a twin cell holding a real
value inside it is a different defect, counted by `unanswered_identifier_shapes.count_real`.
"""

from __future__ import annotations

import contextlib
import csv
import io
import json
import pathlib
import random
import uuid

from synthtwin import cli

import unanswered_identifier_shapes as held_shapes

GE = "1.2.840.113619.2.55.3."
STUDY = "1.2.840.113619.2.55.3.2831164355.311.1593607063.464"
PYDICOM = "1.2.826.0.1.3680043.8.498."
SIEMENS = "1.3.12.2.1107.5.2.32."
KEYS = [f"R{1000 + place}" for place in range(40)]


def _luhn(figures: str) -> int:
    total = 0
    for place, character in enumerate(reversed(figures)):
        value = int(character)
        if place % 2 == 0:
            value = value * 2
            if value > 9:
                value = value - 9
        total = total + value
    return (10 - total % 10) % 10


class _Draw:
    """One table's draw: a seeded generator and the whole numbers it has handed out."""

    def __init__(self, seed: int) -> None:
        self.random = random.Random(seed)
        self.used: "set[int]" = set()

    def unique(self, low: int, high: int) -> int:
        while True:
            value = self.random.randint(low, high)
            if value not in self.used:
                self.used.add(value)
                return value

    def rsid(self) -> str:
        width = self.random.choices([3, 4, 5, 6, 7, 8, 9], [1, 2, 4, 10, 23, 30, 30])[0]
        return f"rs{self.unique(10 ** (width - 1), 10 ** width - 1)}"

    def npi(self) -> str:
        body = f"{self.random.choice('12')}{self.unique(10 ** 7, 10 ** 8 - 1)}"
        return body + str(_luhn("80840" + body))


# name: (cell maker taking the row's index and the table's draw, declared with --identifier)
SHAPES: "dict[str, tuple[object, bool]]" = {
    # -- UIDs, declared (CODES-3 verify 3's table and its NEW SHAPES)
    "uid_752": (lambda k, d: f"1.2.752.24.7.1.{k + 1}", True),
    "uid_ge_product_two_figure_arcs": (lambda k, d: f"1.2.840.113619.2.40.10.12.{k + 1}", True),
    "uid_dcmtk_one_figure_arcs": (lambda k, d: f"1.2.276.0.7.1.2.{k + 1}", True),
    "uid_siemens_one_figure_arcs": (lambda k, d: f"{SIEMENS}1.2.{k + 1}", True),
    "uid_ge_one_figure_arcs": (lambda k, d: f"{GE}1.2.3.{k + 1}", True),
    "uid_ge_two_figure_arcs": (lambda k, d: f"{GE}12.34.56.{k + 1}", True),
    "uid_dcmtk_three_figure_arcs": (lambda k, d: f"1.2.276.0.123.456.789.{k + 1}", True),
    "uid_noorg_series": (lambda k, d: f"1.2.276.0.12.34.56.{k // 10 + 1}.{k % 10 + 1}", True),
    "uid_hl7_value_sets": (lambda k, d: f"2.16.840.1.113883.3.464.1003.{k + 1}", True),
    "uid_pydicom_repeated": (lambda k, d: f"{PYDICOM}{1000 + k // 20}.{k % 20 + 1}", True),
    "uid_short_arcs_no_organisation": (lambda k, d: f"1.2.276.0.12.34.56.{k + 1}", True),
    "uid_short_arcs_one_product_arc": (lambda k, d: f"1.2.840.113619.2.4021.1015.1230.{k + 1}", True),
    "uid_short_arcs_ge": (lambda k, d: f"{GE}4021.1015.1230.{k + 1}", True),
    "uid_sop_one_study": (lambda k, d: f"{STUDY}.{k // 50 + 1}.{k % 50 + 1}", True),
    "uid_siemens_short_arcs": (lambda k, d: f"{SIEMENS}4021.1015.1230.{k + 1}", True),
    "uid_siemens_serial": (lambda k, d: f"{SIEMENS}35162.2026101512301234.{k + 1}", True),
    "uid_pydicom_random": (lambda k, d: f"{PYDICOM}{d.random.randint(10**29, 10**30)}", True),
    "uid_2_25_random": (lambda k, d: f"2.25.{d.random.randint(10**36, 10**38)}", True),
    "uid_study_on_ten_rows": (
        lambda k, d: f"{GE}{2831164355 + (k // 10) * 7}.311.{1593607063 + k // 10}.{464 + (k // 10) % 100}",
        True,
    ),
    "uid_no_root_sequential": (lambda k, d: f"1.2.{k + 1}", True),
    # -- record numbers written as decimals
    "cerner_one_width": (lambda k, d: f"{31000000 + k}.00", True),
    "cerner_on_five_rows": (lambda k, d: f"{31000000 + k // 5}.00", True),
    "cerner_seven_and_eight_figures": (lambda k, d: f"{d.random.choice([9000000, 31000000]) + k}.00", True),
    "cerner_three_widths": (lambda k, d: f"{d.random.choice([1500, 150000, 15000000]) + k}.00", True),
    "cerner_two_widths": (lambda k, d: f"{d.random.choice([1500, 15000000]) + k}.00", True),
    "cerner_three_widths_one_place": (lambda k, d: f"{d.random.choice([1500, 150000, 15000000]) + k}.0", True),
    "cerner_three_widths_blank": (
        lambda k, d: "" if k % 10 == 0 else f"{d.random.choice([1500, 150000, 15000000]) + k}.00", True,
    ),
    "cerner_person_on_three_rows": (lambda k, d: f"{12000000 + k // 3}.00", True),
    "cerner_grouped": (lambda k, d: f"{31000000 + k:,}.00", True),
    "cerner_hundred_values": (lambda k, d: f"{k % 100:02d}.00", True),
    # -- record numbers of figures alone
    "sequential_from_one": (lambda k, d: f"{k + 1}", True),
    "sequential_person_on_twenty_rows": (lambda k, d: f"{k // 20 + 1}", True),
    "sequential_person_on_three_rows": (lambda k, d: f"{k // 3 + 1}", True),
    "random_seven_figures": (lambda k, d: f"{d.unique(10**6, 10**7 - 1)}", True),
    "random_eight_figures": (lambda k, d: f"{d.unique(10**7, 10**8 - 1)}", True),
    "random_ten_figures": (lambda k, d: f"{d.unique(10**9, 10**10 - 1)}", True),
    "sequential_seven_figures": (lambda k, d: f"{1000000 + k}", True),
    "zero_filled_eight": (lambda k, d: f"{k + 1:08d}", True),
    "zero_filled_person_on_four_rows": (lambda k, d: f"{k // 4 + 1:06d}", True),
    "float_record_number": (lambda k, d: f"{100000 + k}.0", True),
    "csn_stride": (lambda k, d: f"{8000000000 + 37 * k}", True),
    "npi_check_digit": (lambda k, d: d.npi(), True),
    # -- prefixed ids
    "pt_seven_sequential": (lambda k, d: f"PT{1000000 + k:07d}", True),
    "pt_seven_person_on_three_rows": (lambda k, d: f"PT{1000000 + k // 3:07d}", True),
    "e_nine_sequential": (lambda k, d: f"E{100000000 + k}", True),
    "p_five": (lambda k, d: f"P{k % 90000 + 10000}", True),
    "letters_eight_random": (lambda k, d: f"QRV{d.unique(10**7, 10**8 - 1)}", True),
    "two_systems": (lambda k, d: (f"ST{1000 + k % 9000}" if k % 2 else f"E{100000 + k}"), True),
    "abc_dash_four": (lambda k, d: f"ABC-{1000 + k % 9000}", True),
    "uuid": (lambda k, d: str(uuid.UUID(int=d.random.getrandbits(128))), True),
    # -- rsIDs
    "rsid": (lambda k, d: d.rsid(), True),
    "rsid_beside_dots": (lambda k, d: "." if k % 5 == 0 else d.rsid(), True),
    # -- keys beside words and placeholders, held until answered (and answered, in ANSWERED)
    "keys_alone": (lambda k, d: KEYS[k % 40], False),
    "keys_beside_unknown": (lambda k, d: "Unknown" if k % 5 < 2 else KEYS[k % 40], False),
    "keys_beside_na": (lambda k, d: "N/A" if k % 5 == 0 else KEYS[k % 40], False),
    "record_numbers_beside_minus_99": (lambda k, d: "-99" if k % 5 == 0 else f"{1000000 + k // 4}", False),
    "record_numbers_beside_unknown": (lambda k, d: "UNKNOWN" if k % 7 == 0 else f"{2000000 + k // 3}", False),
    "pt_held_person_on_three_rows": (lambda k, d: f"PT{1000000 + k // 3:07d}", False),
    "uid_study_held": (
        lambda k, d: f"{GE}{2831164355 + (k // 10) * 7}.311.{1593607063 + k // 10}.{464 + (k // 10) % 100}",
        False,
    ),
    # -- lane ID-ROOM's skeptic 1 (wave6/ID-ROOM-sk1.md): one stray cell beside a column of keys
    # (item 2), one key written two ways (item 3), UIDs of two roots (item 4), dense layouts a class
    # or a date can exhaust (item 5), the spill beside outliers rule A1 counts (item 6), case, spaces,
    # zero fill and a hyphen (item 8)
    "outlier_long": (lambda k, d: "123456789012" if k == 5 else f"{1000000 + k}", True),
    "outlier_short": (lambda k, d: "12" if k == 5 else f"{1000000 + k}", True),
    "outlier_word": (lambda k, d: "ERR" if k == 5 else f"{1000000 + k}", True),
    "outlier_person_on_three_rows": (lambda k, d: "99999999999" if k == 5 else f"{1000000 + k // 3}", True),
    "pt_two_outliers": (
        lambda k, d: "PT1234567890123" if k == 5 else ("PT98765432" if k == 9 else f"PT{1000000 + k:07d}"), True,
    ),
    "pad_mixed": (lambda k, d: f"{k + 1:08d}" if k % 2 else f"{k + 1}", True),
    "pad_split": (lambda k, d: (lambda v: f"{v:09d}" if d.random.random() < 0.5 else f"{v}")(
        d.unique(10**6, 10**7 - 1)), True),
    "case_split": (
        lambda k, d: f"REC{d.random.randint(8000000, 9999999)}" if k % 2 == 0
        else f"rec{d.random.randint(1000000, 7999999)}", True,
    ),
    "space_mixed": (lambda k, d: f" {1000000 + k}" if k % 4 == 0 else f"{1000000 + k}", True),
    "dash_split": (
        lambda k, d: f"P{d.random.randint(80000, 99999)}" if k % 2 == 0 else f"P-{d.random.randint(10000, 79999)}",
        True,
    ),
    "hex4_dense": (lambda k, d: f"{d.random.getrandbits(16):04x}", True),
    "uid_ge_and_siemens": (lambda k, d: f"{GE}{k + 1}" if k % 2 else f"{SIEMENS}{k + 1}", True),
    "uid_hl7_and_dicom": (
        lambda k, d: f"2.16.840.1.113883.3.464.{k + 1}" if k % 2 else f"1.2.840.10008.5.1.4.{k + 1}", True,
    ),
    "uid_one_arc_repeating": (lambda k, d: f"1.2.3.{k % 1000}", True),
    # -- Codex's review of the lane (codex-w3/verdict-ID-ROOM): identifiers past the layout limit
    # (item 1), a real cell spelled as an exclusion (item 2), a folded identity widened (item 3), two
    # long prefixes widened (item 4), identifiers of sixty-four characters (item 5)
    "over_the_layout_limit": (lambda k, d: str(10**64 + k % 100), True),
    "dense_beside_one_past_the_limit": (lambda k, d: str(10**64) if k % 600 == 599 else str(k % 600 + 1), True),
    "literal_marks": (
        lambda k, d: (lambda i: f"{1000 + i}" if i < 200 else ("9%%%" if i == 200 else f"x%0{i - 201}"))(k % 211),
        True,
    ),
    "folded_with_spaces": (
        lambda k, d: (lambda i: (" " if i % 2 else "") + "ABCDEFGHIJ"[(i // 2) // 10] + str((i // 2) % 10)
                      if i < 200 else "KLMNOPQRST"[(i - 200) // 10] + str((i - 200) % 10))((k // 2) % 300),
        True,
    ),
    # Letters a key's case splits: `N` to `Z` written in capitals, `a` to `m` in small letters, so only
    # the fold of the case says every letter is held at the first place.
    "letter_case_halves": (
        lambda k, d: (f"{chr(ord('N') + d.random.randrange(13))}" if k % 2 == 0
                      else f"{chr(ord('a') + d.random.randrange(13))}") + f"{d.random.randint(10000, 99999)}",
        True,
    ),
    "two_long_prefixes": (
        lambda k, d: ("A" + "-" * 59 if k % 800 < 400 else "B" + "_" * 59) + str(100 + k % 400), True,
    ),
    "sixty_four_characters": (lambda k, d: "Q" * 61 + str(100 + k % 800), True),
    # -- lane ID-ROOM's verify (wave6/ID-ROOM-verify.md, new item 1): two layouts whose excluded
    # templates write the same figures at the same merged places, so their fillings run in step and
    # the final pass, claiming by the fold alone, wrote two twin persons as one -- `97525937.0` beside
    # `97525937.00` (its `s_dec_mixed`), `100005` beside `100005.0` read as numbers (`s_float_int`),
    # `1234 5` beside `1234-5` (`x_space_inside`).
    "decimal_one_or_two_noughts": (
        lambda k, d: f"{31000000 + k}.0" if k % 2 else f"{31000000 + k}.00", True,
    ),
    "number_beside_its_decimal": (lambda k, d: f"{100000 + k}.0" if k % 2 else f"{100000 + k}", True),
    "space_or_dash_inside": (
        lambda k, d: f"{1000 + k % 9000} {k % 7}" if k % 2 else f"{1000 + k % 9000}-{k % 7}", True,
    ),
    # -- the orchestrator's ruling 2 of 2026-10-25 (lane SH's verify 3, 'New shapes'): a held ZIP
    # column's made-up values in its layouts -- every cell ZIP+4, and three in ten. Lane SH's ZIP hold
    # is not on this lane's base, where the unanswered column is read as free text, so these are
    # DECLARED, which writes them as the hold does: made-up values in the column's own layouts.
    "zip_plus_four": (lambda k, d: f"{52240 + 7 * d.random.randrange(40)}-{d.random.randint(1000, 9999)}", True),
    "zip_plus_four_thirty": (
        lambda k, d: (lambda z: f"{z}-{d.random.randint(1000, 9999)}" if d.random.random() < 0.3 else z)(
            f"{52240 + 7 * d.random.randrange(40)}"),
        True,
    ),
}

# Shapes the gate validates too, at 20,000 rows (exit 0): the twin keeps its own validation where
# the lane's base did (skeptic 1 of lane ID-ROOM, items 5 and 8). Two are held to equality alone, as
# their walk misses on the base too: `case_split`, whose walk writes one value as the stand-in
# `@---------` and misses `&&&%%%%%%%` by one cell (exit 3 on 2d25b07 and on the head alike), and
# `space_mixed`, whose walk writes no cell with an edge space (exit 3 on both).
VALIDATED = (
    "pad_mixed", "hex4_dense", "dash_split", "pad_split", "outlier_long",
    "outlier_short", "outlier_word", "outlier_person_on_three_rows", "pt_two_outliers",
    "two_long_prefixes",
)

# Shapes built at 600 rows alone: what they pin is a construction, not a density.
AT_600_ALONE = (
    "over_the_layout_limit", "literal_marks", "folded_with_spaces", "two_long_prefixes",
)

# The held shapes answered `identifier` on the questions file, as the person holding the table
# would, at the sizes whose people the population floor describes (P4-D341: 100 people or more; the
# forty keys of `keys_alone` are 40 people and are refused at every size, and the question put to
# `record_numbers_beside_unknown` offers no `identifier`).
ANSWERED = (
    ("record_numbers_beside_minus_99", (600, 20_000)),
    ("pt_held_person_on_three_rows", (600, 20_000)),
    ("uid_study_held", (20_000,)),
)

# Declared shapes the population floor refuses at 600 rows (fewer than 100 people: 60 studies, 30
# patients); profiled, nothing is written, so no twin cell can be real.
REFUSED_AT_600 = ("uid_study_on_ten_rows", "sequential_person_on_twenty_rows")

# Lane CODES-3's own gate tables (tests/test_zoo_identifiers.py): table, column, declared.
CODES3 = (
    ("codes3_pacs_study_uid", "study_uid", True),
    ("codes3_cerner_encounter", "ENCNTR_ID", True),
    ("codes3_cerner_person", "PERSON_ID", True),
    ("codes3_vcf_rsid", "ID", True),
    ("codes3_keys_r_one_word", "key", False),
    ("codes3_keys_ab_third_word", "key", False),
    ("codes3_keys_pad_pure", "key", False),
)


def rows_of(name: str, n: int) -> "tuple[list[str], list[list[str]], str, bool]":
    """One shape's table: its header, its rows, the column measured and whether it is declared."""
    if name.startswith("codes3_"):
        import test_zoo_identifiers as codes3

        for table, column, declared in CODES3:
            if table == name:
                if table == "codes3_pacs_study_uid":
                    header, rows = codes3.uid_rows(n, 20261016)
                elif table.startswith("codes3_cerner"):
                    header, rows = codes3.float_keys_rows(n, 4252)
                elif table == "codes3_vcf_rsid":
                    header, rows = codes3.vcf_rows(n, 4250)
                elif table == "codes3_keys_r_one_word":
                    header, rows = codes3.plain_rows("R", -1, n)
                elif table == "codes3_keys_ab_third_word":
                    header, rows = codes3.plain_rows("AB", 3, n)
                else:
                    header, rows = codes3.plain_rows("PAD", 0, n)
                return header, rows, column, declared
        raise KeyError(name)
    make, declared = SHAPES[name]
    draw = _Draw(7)
    rows = [
        [make(k, draw), draw.random.choice(("CT", "MR", "CR")), f"{draw.random.uniform(3, 150):.1f}"]  # type: ignore[operator]
        for k in range(n)
    ]
    return ["target", "mod", "value"], rows, "target", bool(declared)


def every_shape() -> "tuple[str, ...]":
    """Every shape's name, CODES-3's tables last."""
    return tuple(SHAPES) + tuple(table for table, _column, _declared in CODES3)


def walk_and_pass(folder: pathlib.Path, name: str, n: int) -> "dict[str, list[str]]":
    """One declared shape's real column, its twin, and the twin the walks write with the final pass withdrawn.

    Profiled once and generated twice at seed 0, the second time with `generation.
    _spelled_off_the_real` returning the walk's cells, so the two twins differ only by the pass
    (lane ID-ROOM's verify, new item 1).
    """
    from synthtwin import generation

    header, rows, column, declared = rows_of(name, n)
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "t.csv"
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)
    typed = ["--identifier", column] if declared else []
    found: "dict[str, list[str]]" = {"real": [row[header.index(column)] for row in rows]}
    screen = io.StringIO()
    final_pass = generation._spelled_off_the_real
    with held_shapes.nobody_at_the_keyboard():
        with contextlib.redirect_stdout(screen), contextlib.redirect_stderr(screen):
            assert cli.main(["profile", f"{path}", "--out-dir", f"{folder}", "--replace"] + typed) == 0
            for label in ("twin", "walk"):
                out = folder / label
                out.mkdir(exist_ok=True)
                try:
                    if label == "walk":
                        generation._spelled_off_the_real = lambda _c, _f, cells, _h: (cells, [])  # type: ignore[assignment]
                    assert cli.main(["generate", f"{folder / 't-profile.json'}", "--out-dir", f"{out}",
                                     "--seed", "0", "--replace"]) == 0
                finally:
                    generation._spelled_off_the_real = final_pass  # type: ignore[assignment]
                with open(out / "t-twin.csv", encoding="utf-8", newline="") as handle:
                    table = list(csv.reader(handle))
                place = table[0].index(column)
                found[label] = [row[place] for row in table[1:]]
    return found


def merged_equal_cells(
    real: "list[str]", twin: "list[str]", absent: "frozenset[str]" = frozenset()
) -> int:
    """Twin cells, present, whose MERGED KEY (`parsing.merged_key`) is a present real cell's.

    The form `profile.subject_keys` counts a person by (plan P4-D406): `P0013736` and `P13736`,
    `009297784` and `9297784`, `P-1` and `p1` are one key, so a twin cell merging with a real one
    names a real person written another way (skeptic 1 of lane ID-ROOM, item 3).
    """
    from synthtwin import parsing

    keys = {parsing.merged_key(cell) for cell in real if cell.strip() and cell not in absent}
    keys.discard("")
    return sum(
        1 for cell in twin if cell.strip() and cell not in absent and parsing.merged_key(cell) in keys
    )


# THE SAME DAY, ANY WIDTH OF YEAR (LANE ID-ROOM2 RULINGS 6 (5)): a twin date naming a day a real cell
# of its column names -- read in an ordinary form, a four-figure year as written, a two-figure year in
# the 1900s and in the 2000s, month first and day first both -- is a real date written another way.
_FOUR_FIGURE_DAYS = ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%d-%b-%Y", "%d %b %Y", "%Y%m%d")
_TWO_FIGURE_DAYS = ("%m/%d/%y", "%d/%m/%y", "%d-%b-%y", "%d %b %y")


def days_named(cell: str) -> "frozenset[tuple[int, int, int]]":
    """Every day a cell names in an ordinary date form, as (year, month, day); two-figure years in both centuries."""
    import datetime

    found: "set[tuple[int, int, int]]" = set()
    for form in _FOUR_FIGURE_DAYS:
        try:
            read = datetime.datetime.strptime(cell, form)
        except ValueError:
            continue
        found.add((read.year, read.month, read.day))
    for form in _TWO_FIGURE_DAYS:
        try:
            read = datetime.datetime.strptime(cell, form)
        except ValueError:
            continue
        for century in (1900, 2000):
            try:
                datetime.date(century + read.year % 100, read.month, read.day)
            except ValueError:
                continue
            found.add((century + read.year % 100, read.month, read.day))
    return frozenset(found)


def same_day_cells(real: "list[str]", twin: "list[str]", absent: "frozenset[str]" = frozenset()) -> int:
    """Twin cells, present, naming a day a present real cell of the same column names (`days_named`).

    Linear: the real cells' days in one set, each different cell read once.
    """
    days: "set[tuple[int, int, int]]" = set()
    for cell in set(real):
        if cell.strip() and cell not in absent:
            days |= days_named(cell.strip())
    hits: "dict[str, bool]" = {}
    count = 0
    for cell in twin:
        if not cell.strip() or cell in absent:
            continue
        if cell not in hits:
            hits[cell] = bool(days_named(cell.strip()) & days)
        count += hits[cell]
    return count


def equal_cells(real: "list[str]", twin: "list[str]", absent: "frozenset[str]" = frozenset()) -> int:
    """Twin cells, present, spelled exactly as a present real cell of the same column.

    ``absent`` are the spellings the description reads as no value (its `missing_by_source`: `.`,
    `N/A`), which the twin writes at their published counts and which are no identifier.
    """
    present = {cell for cell in real if cell.strip() and cell not in absent}
    return sum(1 for cell in twin if cell.strip() and cell not in absent and cell in present)


def run_shape(
    folder: pathlib.Path, name: str, n: int, answer: str = "", validate: bool = True
) -> "dict[str, object]":
    """Profile (nobody at the keyboard; ``answer`` put to the column's question), generate, validate.

    Returns the three exits, the column's block, the real and the twin cells, the twin cells
    equal to a real one, and every written file's text but the source's and the twin's.
    """
    header, rows, column, declared = rows_of(name, n)
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "t.csv"
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)
    typed = ["--identifier", column] if declared else []
    screen = io.StringIO()
    with held_shapes.nobody_at_the_keyboard():
        with contextlib.redirect_stdout(screen), contextlib.redirect_stderr(screen):
            profiled = cli.main(["profile", f"{path}", "--out-dir", f"{folder}", "--replace"] + typed)
            if answer and profiled == 0:
                questions = json.loads((folder / "t-questions.json").read_text(encoding="utf-8"))
                for entry in questions.get("asked", []):
                    if entry.get("column") == column:
                        entry["your_answer"] = answer
                answers = folder / "answers.json"
                answers.write_text(json.dumps(questions), encoding="utf-8", newline="\n")
                profiled = cli.main(["profile", f"{path}", "--out-dir", f"{folder}", "--replace",
                                     "--answers", f"{answers}"] + typed)
            generated = -1
            if profiled == 0:
                generated = cli.main(["generate", f"{folder / 't-profile.json'}", "--out-dir",
                                      f"{folder}", "--seed", "0", "--replace"])
            validated = -1
            if validate and generated == 0:
                validated = cli.main(["validate", f"{folder / 't-profile.json'}", "--twin",
                                      f"{folder / 't-twin.csv'}", "--out-dir", f"{folder}",
                                      "--replace"])
    real = [row[header.index(column)] for row in rows]
    twin: "list[str]" = []
    if (folder / "t-twin.csv").is_file():
        with open(folder / "t-twin.csv", encoding="utf-8", newline="") as handle:
            table = list(csv.reader(handle))
        place = table[0].index(column)
        twin = [row[place] for row in table[1:]]
    block: "dict[str, object]" = {}
    if (folder / "t-profile.json").is_file():
        document = json.loads((folder / "t-profile.json").read_text(encoding="utf-8"))
        block = [one for one in document["columns"] if one["name"] == column][0]
    texts: "dict[str, str]" = {"(screen)": screen.getvalue()}
    for written in sorted(folder.iterdir()):
        if written.is_file() and written.name not in ("t.csv", "t-twin.csv"):
            texts[written.name] = written.read_text(encoding="utf-8", errors="replace")
    absent = frozenset(block.get("missing_by_source") or {})  # type: ignore[arg-type]
    return {
        "exits": (profiled, generated, validated),
        "block": block,
        "real": real,
        "twin": twin,
        "equal": equal_cells(real, twin, absent),
        "merged": merged_equal_cells(real, twin, absent),
        "texts": texts,
    }


def _column_cells(path: pathlib.Path, name: str) -> "list[str] | None":
    """One column of a table, read by the product's own reader; None where it is not read.

    `reading.read_table` reads each table in its own dialect -- a byte-order mark, a `;` or a tab,
    a workbook -- as `synthtwin profile` does (skeptic 1 of lane ID-ROOM, item 8); a table it reads
    with made-up names, or whose header sits under rows of notes, is read by the csv module under
    the delimiter that splits its header, the mark aside.
    """
    from synthtwin import reading

    try:
        table = reading.read_table(f"{path}")
        if name in table.column_names:
            return list(table.columns[table.column_names.index(name)])
    except Exception:  # noqa: BLE001 -- a table the reader refuses is read below
        pass
    if path.suffix not in (".csv", ".tsv", ".txt", ".psv"):
        return None
    text = path.read_bytes().decode("utf-8-sig", errors="replace")
    for delimiter in (",", ";", "\t", "|"):
        rows = list(csv.reader(io.StringIO(text), delimiter=delimiter))
        for start in range(min(len(rows), 12)):
            if name in rows[start]:
                place = rows[start].index(name)
                return [row[place] for row in rows[start + 1:] if len(row) > place]
    return None


# THE DATE PASS'S HELD DIAGNOSIS DATES, KEPT (lane TR's repair 1; LANE TR RULINGS 3 (4)): the catalogue
# answers `tumor_registry.dx_date` as the dates it is since then, so its own run reads the column as dates.
# The tables `zoo_equal_cells` reads leave those two questions blank, as a person may, so the column is held
# as record numbers and its twin written by the date pass, as K-HZ-06's zoo leg has counted it since lane
# HB's merge -- its runs byte for byte as before.
ZOO_LEFT_UNANSWERED = {"tumor_registry": ("dx_date",)}


def zoo_tables() -> "tuple[object, ...]":
    """The zoo tables `zoo_equal_cells` reads: the WHOLE catalogue this machine can read.

    E0a's twenty-five exports and lane E0c's thirty-nine (`health_zoo.catalogue`), workbooks
    left out only where the cross-check reader is absent (`health_zoo.runnable_tables`). Batch
    4m's records (Codex's review of batch 4l, its second Medium, BATCH 4m OWES 2): the helper
    read `health_zoo.TABLES` alone, so an added export's identifier column -- the instrument
    magnitudes' `sample_id`, `S500000` beside a twin's `s0500000` -- was never counted. Each
    column `ZOO_LEFT_UNANSWERED` names is left unanswered (`zoo_left_unanswered`).
    """
    import health_zoo

    return tuple(zoo_left_unanswered(table) for table in health_zoo.runnable_tables(health_zoo.catalogue()))


def zoo_left_unanswered(table: object) -> object:
    """A zoo table whose answers leave out the columns `ZOO_LEFT_UNANSWERED` names for it; any other table as it is."""
    import dataclasses

    name = getattr(table, "name", "")
    if name not in ZOO_LEFT_UNANSWERED:
        return table
    knows = getattr(table, "knows")
    kept = {column: answer for column, answer in knows.items() if column not in ZOO_LEFT_UNANSWERED[name]}
    return dataclasses.replace(table, knows=kept)  # type: ignore[type-var]


# K-HZ-06's zoo leg, counted per named column (batch 4n's records, Codex's review of batch 4m, its
# first Medium, BATCH 4n OWES 1): the five birth-date columns lane SH2 holds as identifiers, whose
# twins match a real date of their column by chance, each counted under keys of its own with its own
# bound; every other zoo identifier column goes into the two totals, which must read 0. Pooled, a
# birth date gone would have offset a record number newly written as a real key. At lane HB's merge
# (batch 4n) the diagnosis dates of `tumor_registry.dx_date` join them: held as record numbers, their
# twin is written as valid dates from the constant range by lane HB's rule 10 (plan P4-D442), never
# reading a real value, and matches a real date of its column by chance as measured (LANE HB RULINGS
# 8 (4) and 11 (4)), so it too counts under keys of its own with its own bound. Since lane ID-ROOM2
# (plan P4-D457) the six draw their made-up dates from a block of years no real date of theirs takes,
# so each pair of keys reads 0, a column apart still, so no date can offset a key.
ZOO_HELD_DATES = (
    "patients.dob_iso",
    "patients.dob_us",
    "patients.dob_text",
    "phi_registry.birth_date",
    "registry_extract.dob_short",
    "tumor_registry.dx_date",
)
ZOO_EQUAL = "zoo_twin_cells_equal_to_a_real_identifier"
ZOO_MERGING = "zoo_twin_cells_merging_with_a_real_identifier"


def zoo_held_date_keys(column: str) -> "tuple[str, str]":
    """K-HZ-06's two keys for one of `ZOO_HELD_DATES`: patients.dob_iso -> zoo_patients_dob_iso_equal, ..._merging."""
    stem = "zoo_" + column.replace(".", "_")
    return f"{stem}_equal", f"{stem}_merging"


def zoo_held_date_same_day_key(column: str) -> str:
    """K-HZ-06's same-day key for one of `ZOO_HELD_DATES` (LANE ID-ROOM2 RULINGS 6 (5)): ..._same_day."""
    return "zoo_" + column.replace(".", "_") + "_same_day"


def tally_zoo(
    value: "dict", by_column: "dict[str, tuple[int, int]]", same_days: "dict[str, int] | None" = None
) -> None:
    """Add one zoo run's counts, `table.column` -> (equal, merging), to K-HZ-06's value.

    Each of `ZOO_HELD_DATES` under its own two keys (present, at 0, whether or not it was read);
    every other identifier column into `ZOO_EQUAL` and `ZOO_MERGING`, never into a date's keys.
    Where ``same_days`` is given (`zoo_equal_cells`), each of `ZOO_HELD_DATES` also under its
    same-day key: its twin cells naming a day a real cell of it names, either width of year.
    """
    for column in ZOO_HELD_DATES:
        for key in zoo_held_date_keys(column):
            value[key] = int(value.get(key, 0))
        if same_days is not None:
            key = zoo_held_date_same_day_key(column)
            value[key] = int(value.get(key, 0)) + int(same_days.get(column, 0))
    for column, (equal, merged) in sorted(by_column.items()):
        if column in ZOO_HELD_DATES:
            on_equal, on_merged = zoo_held_date_keys(column)
        else:
            on_equal, on_merged = ZOO_EQUAL, ZOO_MERGING
        value[on_equal] = int(value.get(on_equal, 0)) + equal
        value[on_merged] = int(value.get(on_merged, 0)) + merged


def refused_for_the_people_floor(result: object) -> bool:
    """Whether a `health_zoo.run_table` run stopped on the command's refusal for the people floor (LANE I4q RULINGS 15 (3)).

    Its profile or answers step exited 1 with the command's own words for a table of too few people
    (`errors.the_population_is_too_small`, counted in people: 'This table holds 40 people, and synthtwin
    describes a table of 100 people or more.'), read off the product's own sentence, never copied. Any other
    exit, any other words, or a run with no such step is no such refusal.
    """
    from synthtwin import errors

    marker = "987654321"
    said = errors.the_population_is_too_small(int(marker), "people", "")
    opening = said[: said.index(marker)]
    rest = said[said.index(marker) + len(marker):]
    rest = rest[: rest.index(".") + 1]
    steps = result.get("steps") if isinstance(result, dict) else None
    if not isinstance(steps, dict):
        return False
    for step in ("profile", "answers"):
        seen = steps.get(step)
        if isinstance(seen, dict) and seen.get("exit") == 1:
            error = f"{seen.get('error') or ''}"
            if error.startswith(opening) and rest in error:
                return True
    return False


def zoo_equal_cells(
    folder: pathlib.Path,
    n: int,
    tables: "tuple[object, ...] | None" = None,
    by_column: "dict[str, tuple[int, int]] | None" = None,
    same_days: "dict[str, int] | None" = None,
) -> "dict[str, int]":
    """The health data zoo's identifier columns: twin cells spelled as a real cell of their column.

    Every zoo table this machine runs (`zoo_tables`, or those named; each at its catalogue seed,
    `health_zoo.seed_of`, as `health_zoo.run_zoo` draws it), workbooks included where the
    cross-check reader is, run through `health_zoo.run_table` -- profiled scripted, answered with
    the zoo's general facts, generated at seed 0 -- and every column its description writes as an
    identifier, each read in its table's own dialect. Returns the equal cells, the cells whose
    merged key is a real cell's, the identifier columns read, those NOT read (a failure: no column
    goes uncounted), the tables whose twin was not written, those the command REFUSED for the people
    floor apart from them (`refused_by_floor`, `refused_for_the_people_floor`: the refusal is the
    command's, by design, where any other failure to write stays counted as not written) and the
    tables run. Where `by_column`
    is given, each column read adds its own (equal, merging) under `table.column` (`tally_zoo`);
    where `same_days` is, each of `ZOO_HELD_DATES` read adds its twin cells naming a real day
    (`same_day_cells`).
    """
    import health_zoo

    found = {"equal": 0, "merged": 0, "columns": 0, "unread": 0, "unwritten": 0, "refused_by_floor": 0, "tables": 0}
    for table in zoo_tables() if tables is None else tables:
        where = folder / table.name  # type: ignore[attr-defined]
        found["tables"] += 1
        done = health_zoo.run_table(table, where, n, health_zoo.seed_of(table))  # type: ignore[arg-type]
        profile = where / f"{table.name}-profile.json"
        twin = where / f"{table.name}-twin{table.suffix}"
        if not twin.is_file():
            # A text export (`.txt`: tab- or pipe-delimited, or Excel's Unicode text) is twinned as
            # `.csv` in the source's own dialect, where `health_zoo.run_table` reads it (batch 4m's
            # records, the orchestrator's LANE I4m RULINGS 5: the three `.txt` exports' twins were
            # counted as not written, their identifier columns never read).
            twin = where / f"{table.name}-twin.csv"
        if not profile.is_file() or not twin.is_file():
            # ...apart, a table the command refused for the people floor (LANE I4q RULINGS 15 (3): a
            # fixture of 40 people at 20,000 rows, which the command rightly refuses, read as a table
            # not written).
            found["refused_by_floor" if refused_for_the_people_floor(done) else "unwritten"] += 1
            continue
        document = json.loads(profile.read_text(encoding="utf-8"))
        absent: "frozenset[str]" = frozenset()
        for block in document["columns"]:
            if block.get("role") != "identifier":
                continue
            real = _column_cells(where / f"{table.name}{table.suffix}", block["name"])
            made = _column_cells(twin, block["name"])
            if real is None or made is None:
                found["unread"] += 1
                continue
            absent = frozenset(block.get("missing_by_source") or {})
            found["columns"] += 1
            equal = equal_cells(real, made, absent)
            merged = merged_equal_cells(real, made, absent)
            found["equal"] += equal
            found["merged"] += merged
            named = f"{table.name}.{block['name']}"  # type: ignore[attr-defined]
            if by_column is not None:
                before = by_column.get(named, (0, 0))
                by_column[named] = (before[0] + equal, before[1] + merged)
            if same_days is not None and named in ZOO_HELD_DATES:
                same_days[named] = same_days.get(named, 0) + same_day_cells(real, made, absent)
    return found
