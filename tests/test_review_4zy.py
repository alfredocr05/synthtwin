"""Batch 4zy's landing: the fix round of its one outside review (release 36).

WHAT IT HOLDS (each clause red on its mutant):

* Item 1 (HIPAA): an SPSS age column the description top-codes at 90 writes no value label into the twin's
  dictionary, whether its cells read `95.00` (codes counted by value) or `95` (counted by spelling): the label
  `95: "Senior"` named an age past 89 (mutant: the top-coded guard withdrawn).
* Item 2: the text zone's record numbers of one lettered class keep their class -- `L` and six figures stay `L` and six
  figures beside a `K` class of four figures -- because a key's nought mark is withdrawn only where the key is its
  figures ALONE, read off the whole template (mutant: one slot read as figures alone, letters or not).
* Item 9: a key of figures alone, rewritten by the text zone, holds no real key, neither by its spelling nor read as a
  number, and no value opening with a nought (mutant: the nought mark kept).
"""

from __future__ import annotations

import json
import pathlib
import random

import pytest

from synthtwin import cli, inside_text


# -- item 1: no value label of a top-coded column (`profile._published_native`) ---------------------------------------


def _age_file(tmp_path: pathlib.Path, display: str) -> pathlib.Path:
    pandas = pytest.importorskip("pandas")
    pyreadstat = pytest.importorskip("pyreadstat")
    rows = 2000
    ages = [95.0] * 1000 + [float(20 + index % 70) for index in range(rows - 1000)]
    bands = [1.0, 1.5, 2.25] * (rows // 3) + [1.0] * (rows % 3)
    frame = pandas.DataFrame({"age": ages, "dose_band": bands,
                              "sbp": [round(100 + ((index * 37) % 600) / 10, 1) for index in range(rows)]})
    source = tmp_path / "visits.sav"
    pyreadstat.write_sav(frame, str(source),
                         variable_value_labels={"age": {95.0: "Senior", 40.0: "Forty"},
                                                "dose_band": {1.0: "Low", 1.5: "Middle", 2.25: "High"}},
                         variable_format={"age": display, "dose_band": "F8.2"})
    return source


@pytest.mark.parametrize("display", ["F8.2", "F8.0"])
def test_a_top_coded_columns_value_labels_never_reach_the_twin(tmp_path: pathlib.Path, display: str) -> None:
    pyreadstat = pytest.importorskip("pyreadstat")
    source = _age_file(tmp_path, display)
    assert cli.main(["profile", str(source)]) == 0
    document = json.loads((tmp_path / "visits-profile.json").read_text(encoding="utf-8"))
    age = [block for block in document["columns"] if block["name"] == "age"][0]
    # The precondition: the description top-codes the age column (else the case proves nothing).
    assert any(key.startswith("top_coded") for key in age), sorted(age)
    native_columns = json.dumps(document["source"]["native"]["columns"])
    assert "Senior" not in native_columns and "Forty" not in native_columns
    # A column the description does not top-code keeps its labels, each code counted by its value.
    for text in ("Low", "Middle", "High"):
        assert text in native_columns, native_columns[:600]
    assert cli.main(["generate", str(tmp_path / "visits-profile.json"), "--seed", "3"]) == 0
    data, meta = pyreadstat.read_sav(str(tmp_path / "visits-twin.sav"))
    age_labels = meta.variable_value_labels.get("age", {})
    assert not age_labels, age_labels
    assert float(data["age"].max()) <= 90.0
    assert meta.variable_value_labels.get("dose_band"), meta.variable_value_labels


# -- items 2 and 9: the text zone's key templates (`inside_text._key_template`) ---------------------------------------


def _stand_in(cells: "list[str]", head: str, width: int) -> "list[str]":
    """A stand-in for the description's twin of a key column that wears NO real template (a letter no real key holds,
    then figures), so the zone must write every value anew -- the output the cases read. Same counts per value."""
    names: "dict[str, str]" = {}
    for cell in cells:
        if cell not in names:
            names[cell] = f"{head}{len(names) + 1:0{width}d}"
    return [names[cell] for cell in cells]


def _written(real: "list[str]", stand_in: "list[str]", persons: "list[int] | None", seed: int) -> "list[str]":
    entry = inside_text.entry_of(real, inside_text.MODE_IDENTIFIER, [], persons, 11)
    assert entry is not None
    written = inside_text.write_column(inside_text.zone_of({"c": entry}), "c", stand_in, seed)
    assert written is not None, "the zone left the column as the description's twin wrote it: nothing was read"
    return written


def test_a_lettered_key_class_keeps_its_letter() -> None:
    feed = random.Random(4)
    real = [f"K{1000 + index}" for index in range(400)] + [f"L{feed.randrange(10 ** 5, 10 ** 6):06d}" for _ in range(19600)]
    written = _written(real, _stand_in(real, "Z", 6), None, 7)
    real_l = sum(1 for cell in real if cell.startswith("L"))
    twin_l = sum(1 for cell in written if cell.startswith("L") and len(cell) == 7 and cell[1:].isdigit())
    twin_k = sum(1 for cell in written if cell.startswith("K") and len(cell) == 5 and cell[1:].isdigit())
    # Every `L` key stays an `L` key of six figures (mutant: none left), and every `K` key a `K` key; none is real.
    assert (twin_l, twin_k) == (real_l, len(real) - real_l), (twin_l, twin_k)
    assert not set(written) & set(real)


def test_a_key_of_figures_alone_holds_no_real_key_by_spelling_or_number() -> None:
    draw = random.Random(4)
    # Keys of one to five figures: every opening figure of the widths 2 to 4 is a real key's (only a nought was
    # free there -- the zoo's encounter numbers), the five-figure ones open with 1 to 4 (5 to 9 free).
    real = [f"{draw.randint(1, 45000)}" for _ in range(20000)]
    written = _written(real, _stand_in(real, "Z", 4), [row // 3 for row in range(20000)], 7)
    numbers = {int(cell) for cell in real}
    assert len(set(written)) == len(set(real))
    assert not set(written) & set(real)
    assert not [cell for cell in written if cell.isdigit() and int(cell) in numbers]
    assert not [cell for cell in written if len(cell) > 1 and cell.startswith("0")]
