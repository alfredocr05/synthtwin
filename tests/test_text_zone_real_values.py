"""Gate file of lane LEDGER: the inside record's text zone writes no real identifier into the twin (HIPAA first).

MEASURED on the merged head of batch 4zz (its tree the public head's) through the health data zoo on the shipped
route at 20,000 rows: 1,548 real street addresses (1,580 cells) and 72 real e-mail addresses of `phi_registry` stood in
the twin, written in their real templates as free text nobody was asked about (each word the floor's people write
kept, each number drawn inside the real ends), and 233 real encounter numbers of `i2b2_facts` (491 cells) stood in it
as numbers, written with a nought in front (`0456` is the real `456` read as a number) where every other opening
figure of their width was a real key's.

WHAT IT HOLDS (each clause red on its mutant):

* a key of figures alone takes no nought as its mark, so no value the zone writes reads, as a number, as a real key
  (mutant: the nought mark kept);
* a column named as an identifier element, or whose cells read as a person's details or as e-mail addresses, is not
  written in its real words (`cli._names_a_person`; mutants: the name not read; the e-mail reader withdrawn), while
  ordinary structured text still is;
* through the commands, the registry's addresses, telephone numbers and e-mail addresses read as such again, made up
  (lane TEXTZONE, `inside_text.MODE_DETAIL`; mutant: such a column left the description's filler).
"""

from __future__ import annotations

import contextlib
import csv
import io
import pathlib
import random
import re

import pytest

import health_zoo_wide
import reliability_battery as B
from synthtwin import cli, inside, inside_text, installation

ROWS = 6000


def _stand_in(cells: "list[str]") -> "list[str]":
    """A stand-in for the description's twin of a column of keys: a made-up key a real value, as long, all figures."""
    names: "dict[str, str]" = {}
    for cell in cells:
        if cell not in names:
            names[cell] = f"{len(names) + 1:0{len(cell)}d}"[-len(cell):]
    return [names[cell] for cell in cells]


def test_a_key_of_figures_alone_is_never_written_as_a_real_one_read_as_a_number() -> None:
    draw = random.Random(4)
    # Keys of one to five figures; the five-figure ones open with 1 to 4, every shorter width opens with 1 to 9.
    real = [f"{draw.randint(1, 45000)}" for _ in range(ROWS)]
    entry = inside_text.entry_of(real, inside_text.MODE_IDENTIFIER, [], [row // 3 for row in range(ROWS)], 11)
    assert entry is not None
    for template in entry["templates"].values():  # type: ignore[union-attr]
        mark = template["mark"]  # type: ignore[index]
        assert not mark or "0" not in mark[2], mark
    zone = inside_text.zone_of({"c": entry})
    written = inside_text.write_column(zone, "c", _stand_in(real), 7)
    numbers = {int(cell) for cell in real}
    if written is not None:
        assert not [cell for cell in written if cell and int(cell) in numbers]


def test_a_column_naming_a_person_keeps_the_descriptions_cells() -> None:
    draw = random.Random(5)
    streets = ("Oak", "Maple", "Cedar", "Pine", "Elm")
    addresses = [f"{draw.randint(1, 9999)} {draw.choice(streets)} St" for _ in range(500)]
    emails = [f"{draw.choice(('anna', 'ben'))}.{draw.choice(('lee', 'kim'))}{draw.randint(1, 999)}@example.org"
              for _ in range(500)]
    phones = [f"(312) 555-{draw.randint(0, 9999):04d}" for _ in range(500)]
    readings = [f"sys={draw.randint(90, 180)};dia={draw.randint(50, 110)}" for _ in range(500)]
    assert cli._names_a_person("street_address", addresses)
    assert cli._names_a_person("contact", emails)
    assert cli._names_a_person("callback", phones)
    assert not cli._names_a_person("bp_reading", readings)
    assert cli._an_email_address("anna.lee12@example.org")
    assert not cli._an_email_address("sys=141;dia=74")
    assert not cli._an_email_address("@example.org")


def test_the_registrys_addresses_and_e_mails_reach_the_twin_as_no_real_one(tmp_path: pathlib.Path) -> None:
    """THROUGH THE COMMANDS (the inside record written, the twin drawn from it), the zoo's `phi_registry` at 20,000
    rows: no street address and no e-mail address of the twin is a real one (mutant: the guard not called)."""
    header, rows = health_zoo_wide.phi_registry(20000, 1)
    source = tmp_path / "table" / "registry.csv"
    out = tmp_path / "out"
    source.parent.mkdir()
    out.mkdir()
    with open(source, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)
    places = inside.Places(pathlib.Path(tmp_path, "installation", "synthtwin", "inside"), (), (),
                           installation.system_name(), ())
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr("synthtwin.cli._INSIDE_RECORD_SHIPPED", True)
        patch.setattr(inside, "default_places", lambda: places)
        with B.installed(tmp_path), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            assert cli.main(["profile", str(source), "--out-dir", str(out)], small_tables_refused=False) == 0
            assert cli.main(["generate", str(out / "registry-profile.json"), "--out-dir", str(out), "--seed", "0"],
                            small_tables_refused=False) == 0
    report = (out / "registry-twin-report.txt").read_text(encoding="utf-8")
    assert report.startswith(cli._INSIDE_REPORT_HEAD)
    twin = list(csv.DictReader(open(out / "registry-twin.csv", encoding="utf-8", newline="")))
    for at, name in ((2, "street_address"), (3, "phone"), (4, "email")):
        real = {row[at] for row in rows}
        assert not [row[name] for row in twin if row[name] in real], name
    # ...AND THEY READ AS ADDRESSES, TELEPHONE NUMBERS AND E-MAIL ADDRESSES AGAIN (lane TEXTZONE): the analyst's own
    # patterns hold on every cell, the words made up, the area codes and exchanges none a real number holds (mutant:
    # the column left the description's filler, release 36's cost).
    layouts = {"street_address": r"\d{1,4} [A-Z][a-z]+ (St|Ave|Rd|Blvd|Ln)", "phone": r"\(\d{3}\) \d{3}-\d{4}",
               "email": r"[a-z]+\.[a-z]+\d*@example\.org"}
    for name, layout in layouts.items():
        misfits = [row[name] for row in twin if not re.fullmatch(layout, row[name])]
        assert not misfits, (name, len(misfits))
    streets = {row[2].split(" ")[1] for row in rows}
    assert not {row["street_address"].split(" ")[1] for row in twin} & streets
    assert not {row["phone"][1:4] for row in twin} & {row[3][1:4] for row in rows}
    assert not {row["phone"][6:9] for row in twin} & {row[3][6:9] for row in rows}
