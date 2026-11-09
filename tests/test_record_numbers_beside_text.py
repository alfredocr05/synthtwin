"""Codex's review of batch 4q, item 1: a record number standing as its own word beside text is kept off the real.

Lane CZ-A's hold of a name beside a record number (plan P4-D445) read a column of `Cedar, Abc [1000000]` as record
numbers where it had been free text, and its excluded template wrote one letter out (`Z&&&&, @&& [%%%%%%%]`): no
twin cell was a real one, but on Codex's table -- 20,000 rows, 1,000 people of 20 records each, the record
numbers 1000000 to 1019999, nothing declared or answered, seed 0 -- 46 twin cells held a complete real record
number, where as free text (f0ce1e06) the column's runs wore `figure_openings` and none did. The same letter alone
kept a blood unit's sequence beside its facility code off nothing, on the public line too. A run of five figures
or more inside a wider value now opens, in the layout's exclusion, as no real run of its width opens
(`taxonomy.inner_runs`, `_exclusion_with_openings`), so no twin cell holds one.

HOWEVER IT IS GLUED (the fix round's verify, blocker 1): the first round reached a run standing as its own word
only, and a record number glued to its label or before a letter inside a name (`Cedar, Abc [MR1000000]`, `Cedar,
Abc #MR1000000`, `Cedar, Abc [1000000A]`) kept the one-letter exclusion: 46, 46 and 47 twin cells of Codex's
construction held a complete real record number on 037d4fcd, none on f0ce1e06. A run is now reached in every
layout of two words or more, whatever stands beside it inside its word; a layout of one word is one key, as before.

Each case runs the command at the owner's table floor (20,000 rows, 1,000 people) with nobody at the keyboard,
generates at seed 0, validates, and counts with the forms' own linear counter (`safe_harbor_forms.complete_tokens`:
the real runs in a set, each different twin cell read once).
"""

from __future__ import annotations

import contextlib
import csv
import io
import json
import pathlib

import pytest

from synthtwin import cli, parsing, taxonomy

import safe_harbor_forms as forms
import unanswered_identifier_shapes as held_shapes

ROWS = 20_000


def _run(folder: pathlib.Path, column: str, cells: "list[str]") -> "dict[str, object]":
    """Profile with nobody at the keyboard, generate at seed 0, validate; the column's block and the counts."""
    folder.mkdir(parents=True, exist_ok=True)
    table = folder / "t.csv"
    with open(table, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow([column])
        writer.writerows([[cell] for cell in cells])
    with held_shapes.nobody_at_the_keyboard(), contextlib.redirect_stdout(io.StringIO()), \
            contextlib.redirect_stderr(io.StringIO()):
        profiled = cli.main(["profile", f"{table}", "--out-dir", f"{folder}", "--replace"])
        generated = cli.main(["generate", f"{folder / 't-profile.json'}", "--out-dir", f"{folder}", "--seed", "0",
                              "--replace"]) if profiled == 0 else -1
        validated = cli.main(["validate", f"{folder / 't-profile.json'}", "--twin", f"{folder / 't-twin.csv'}",
                              "--out-dir", f"{folder}", "--replace"]) if generated == 0 else -1
    block = json.loads((folder / "t-profile.json").read_text(encoding="utf-8"))["columns"][0]
    with open(folder / "t-twin.csv", encoding="utf-8", newline="") as handle:
        twin = [row[0] if row else "" for row in list(csv.reader(handle))[1:]]
    real = sorted({cell for cell in cells if cell.strip()})
    merged = {parsing.merged_key(cell) for cell in real}
    return {
        "exits": (profiled, generated, validated),
        "block": block,
        "twin": twin,
        "tokens": forms.complete_tokens(real, twin),
        "equal": sum(1 for cell in twin if cell in set(real)),
        "merged": sum(1 for cell in twin if parsing.merged_key(cell) in merged),
    }


def test_codex_s_name_beside_a_record_number_of_its_own_writes_no_real_record_number(tmp_path: pathlib.Path) -> None:
    """Codex's table: 46 twin cells held a complete real record number on 29fdf3aa, none on f0ce1e06 (free text).

    The layout's exclusion writes the record number's opening beside its letter, no real record number of
    seven figures opening so; no twin cell is or merges with a real one, and the twin validates. MUTANT:
    `taxonomy.inner_runs` naming no run (the letter alone, as on 29fdf3aa): 46.
    """
    cells = [f"Cedar, {forms.given_of(row // 20)} [{1000000 + row}]" for row in range(ROWS)]
    seen = _run(tmp_path, "label", cells)
    assert seen["exits"] == (0, 0, 0)
    block = seen["block"]
    assert block["role"] == taxonomy.ROLE_IDENTIFIER  # type: ignore[index]
    assert seen["tokens"] == 0 and seen["equal"] == 0 and seen["merged"] == 0, seen["tokens"]
    excluded = block["layout_exclusions"]["@&&&&, @&& [%%%%%%%]"]  # type: ignore[index]
    opening = excluded[excluded.index("[") + 1]
    assert "1" <= opening <= "9" and opening != "1", excluded


def test_a_blood_unit_s_sequence_beside_its_facility_code_is_kept_off_the_real(tmp_path: pathlib.Path) -> None:
    """The sibling the sweep found on f0ce1e06 and 29fdf3aa alike: a unit number a row (ISBT 128's layout, the
    sequences running on from 100000), whose exclusion wrote its first letter alone, carried complete real
    sequences into twin cells (40 cells of the forms' own units at 20,000 rows). Now none. MUTANT: as above.
    """
    cells = [f"W1234 26 {100000 + row:06d} 00" for row in range(ROWS)]
    seen = _run(tmp_path, "unit", cells)
    assert seen["exits"] == (0, 0, 0)
    assert seen["block"]["role"] == taxonomy.ROLE_IDENTIFIER  # type: ignore[index]
    assert seen["tokens"] == 0 and seen["equal"] == 0 and seen["merged"] == 0, seen["tokens"]


# The verify's three tables of blocker 1 (Codex's construction, the record number glued): the cell and the layout
# lane CZ-A's route holds it in, with the complete real record numbers 037d4fcd's twin held inside wider cells.
GLUED = {
    "label_glued": (lambda row: f"Cedar, {forms.given_of(row // 20)} [MR{1000000 + row}]", "@&&&&, @&& [@@%%%%%%%]"),
    "sign_and_label_glued": (lambda row: f"Cedar, {forms.given_of(row // 20)} #MR{1000000 + row}",
                             "@&&&&, @&& #@@%%%%%%%"),
    "letter_after": (lambda row: f"Cedar, {forms.given_of(row // 20)} [{1000000 + row}A]", "@&&&&, @&& [%%%%%%%@]"),
}


@pytest.mark.parametrize("name", sorted(GLUED))
def test_a_record_number_glued_inside_a_name_writes_no_real_record_number(tmp_path: pathlib.Path, name: str) -> None:
    """The verify's blocker 1: 46 (label glued), 46 (`#` and label glued) and 47 (a letter after) twin cells held a
    complete real record number on 037d4fcd and on 29fdf3aa, none on f0ce1e06 (free text).

    Lane CZ-A's route holds each column as a name beside a record number; the layout's exclusion now writes the
    number's opening beside its label or before its letter, no real record number of seven figures opening so;
    no twin cell is or merges with a real one, and the twin validates. MUTANT: `taxonomy.inner_runs` reading a run
    standing as its own word only (the first round's rule): 46, 46 and 47.
    """
    make, layout = GLUED[name]
    cells = [make(row) for row in range(ROWS)]
    seen = _run(tmp_path, "label", cells)
    assert seen["exits"] == (0, 0, 0)
    block = seen["block"]
    assert block["role"] == taxonomy.ROLE_IDENTIFIER  # type: ignore[index]
    assert seen["tokens"] == 0 and seen["equal"] == 0 and seen["merged"] == 0, seen["tokens"]
    excluded = block["layout_exclusions"][layout]  # type: ignore[index]
    place = layout.index("%")
    for spelling in excluded if isinstance(excluded, list) else [excluded]:
        assert "2" <= spelling[place] <= "9", excluded


def test_the_runs_a_layout_writes_inside_a_wider_value() -> None:
    """`inner_runs`: five figures or more in a layout of two words or more, however glued in their word."""
    assert taxonomy.inner_runs("@&&&&, @&& [%%%%%%%]") == [(12, 7)]
    assert taxonomy.inner_runs("@%%%% %% %%%%%% %%") == [(9, 6)]
    assert taxonomy.inner_runs("@&&&& #%%%%%%%") == [(7, 7)]
    assert taxonomy.inner_runs("@&&&, @&& (@@@: %%%%%%%)") == [(16, 7)]
    # ...glued to its label, before a letter, joined by a code's mark, two runs in one value, figures alone.
    assert taxonomy.inner_runs("@&&&&, @&& [@@%%%%%%%]") == [(14, 7)]
    assert taxonomy.inner_runs("@&&&&, @&& #@@%%%%%%%") == [(14, 7)]
    assert taxonomy.inner_runs("@&&&&, @&& [%%%%%%%@]") == [(12, 7)]
    assert taxonomy.inner_runs("@&&&&, @&& [@@@-%%%%%%%]") == [(16, 7)]
    assert taxonomy.inner_runs("[%%]%%%%%%%%%%%%%%[%%]@@%%%%%%") == [(4, 14), (24, 6)]
    assert taxonomy.inner_runs("%% %%%%%% %%") == [(3, 6)]
    # ...a layout of one word is one key: glued to letters, after a sign, joined by a code's marks; four figures
    # are no key.
    assert taxonomy.inner_runs("@@@%%%%%%%") == []
    assert taxonomy.inner_runs("#@@%%%%%%%") == []
    assert taxonomy.inner_runs("[%%%%%%%@]") == []
    assert taxonomy.inner_runs("@@@-%%%%%") == []
    assert taxonomy.inner_runs("%%@-%%%%%%") == []
    assert taxonomy.inner_runs("%%%%%-%%%%%") == []
    assert taxonomy.inner_runs("@&&&&, @&& [%%%%]") == []
    # ...the marks that part words are a space and every layout mark that joins no code's parts.
    assert set(taxonomy._WORD_PARTS) == {" "} | (set(parsing.LAYOUT_MARKS) - set(taxonomy.OWN_WORD_JOINS))


def test_an_exclusion_already_opening_its_runs_off_the_real_stands() -> None:
    """`_openings_kept`: a spelling whose run opens with a figure no real run of its width opens with stands as
    it was; one opening with a figure a real run holds, or writing the run's place out not at all, does not."""
    held = {7: {"1": 20000, "10": 20000, "101": 20000}}
    runs = [(12, 7)]
    assert taxonomy._openings_kept(["Z&&&&, @&& [9%%%%%%]"], runs, held)
    assert not taxonomy._openings_kept(["Z&&&&, @&& [1%%%%%%]"], runs, held)
    assert not taxonomy._openings_kept(["Z&&&&, @&& [%%%%%%%]"], runs, held)
