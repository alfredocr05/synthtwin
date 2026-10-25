"""Every identifier shape the twin writes, and whether a twin cell equals a real one (plan P4-D432).

Shared by `tests/test_identifier_room.py` (the gate) and `tests/test_kpi_ledger.py::test_k_hz_06`
(K-HZ-06), so the gate and the ledger measure the same tables the same way.

THE SHAPES (`SHAPES`), each one column `target` beside a modality and a value, one shape a table:
lane CODES-3's verify 3's table of UIDs (a country branch, a vendor's product arcs, an
organisation root and none, one-figure and two-figure arcs before the instance number, series
of instances, repeated UIDs, pydicom and `2.25.` UIDs of random arcs), record numbers written
as decimals (Cerner's `31000000.00`, three widths, one place, grouped, a person's rows),
record numbers of figures alone (sequential from 1, a person on 3 and on 20 rows, random of 7,
8 and 10 figures, zero-filled, exported as `100000.0`, CSN-like strides, NPI-like numbers with
their Luhn check digit), prefixed ids of several lengths (`PT` and seven figures on one and on
three rows a person, `E` and nine, `P` and five, `MRN` and eight random, two systems, `ABC-`
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
    "mrn_eight_random": (lambda k, d: f"MRN{d.unique(10**7, 10**8 - 1)}", True),
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
}

# The held shapes answered `identifier` on the questions file, as the person holding the table would.
ANSWERED = (
    "keys_alone",
    "keys_beside_unknown",
    "keys_beside_na",
    "record_numbers_beside_minus_99",
    "record_numbers_beside_unknown",
    "pt_held_person_on_three_rows",
    "uid_study_held",
)

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
                    header, rows = codes3.cerner_rows(n, 4252)
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


def equal_cells(real: "list[str]", twin: "list[str]") -> int:
    """Twin cells, present, spelled exactly as a present real cell of the same column."""
    present = {cell for cell in real if cell.strip()}
    return sum(1 for cell in twin if cell.strip() and cell in present)


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
    return {
        "exits": (profiled, generated, validated),
        "block": block,
        "real": real,
        "twin": twin,
        "equal": equal_cells(real, twin),
        "texts": texts,
    }
