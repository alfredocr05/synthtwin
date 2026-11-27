"""P4-D445 (lane CZ-A): the identifier forms' gate, its second file -- the held walk over the tokens and the rule away.

SPLIT FROM `tests/test_zoo_safe_harbor_forms.py` (lane CZ-A's repair 2): the
gate file read 181.6 CPU seconds with repair 2's cases and variant
columns, past the 180 a gate file may take, so the cases that run the
tokens' form apart from its 600-row items -- the held walk's pass-over and
the rule-away mutant -- stand here, every case kept, none moved to a slow
driver.

THE HELD WALK PASSES OVER A LAYOUT OF ANOTHER BAND (`generation._fillings_
outside_the_band`): a column of opaque tokens held with no person column
names a layout for each token, and a slot of the code alphabet read every
filling up to 4,096 of each layout holding a `+` or a `/`, and a wide slot
of each code one; the walk now moves such a layout's step as the search
would have moved it, so the twin is the same bytes and the form's 20,000
rows are written in minutes, not hours. AND THE RULE AWAY: with the
identifier forms not read, a token column answered `keep` is put no Safe
Harbor question.
"""

from __future__ import annotations

import pathlib

import pytest

import safe_harbor_forms as forms
from synthtwin import generation, parsing, taxonomy


def _questions_put(seen: "dict", column: str) -> "list[list[str]]":
    return seen["columns"][column]["asked"]  # type: ignore[no-any-return]


def _check(seen: "dict") -> None:
    """0 real values written, 0 twin cells equal to or carrying one, a question put to each identifier column."""
    assert seen["profile"] == 0 and seen["generate"] == 0, seen.get("screen")
    for column in forms.IDENTIFIERS[seen["kind"]]:
        counted = seen["columns"][column]
        what = f"{seen['kind']}.{column} at {seen['rows']} rows, {seen['mode']}: {counted}"
        assert counted["description_values"] == 0, what
        assert counted["twin_cells_equal"] == 0, what
        assert counted["twin_cells"] == 0, what
        offered = _questions_put(seen, column)
        assert any("identifier" in one or one == ["no", "yes"] for one in offered), what
        if seen["mode"] == "coded":
            assert counted["role"] == "identifier", what


def test_the_rule_away_no_safe_harbor_question_is_put(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The gate's mutant: with the identifier forms not read, a token column answered `keep` is put no Safe Harbor question."""
    held = forms.measure(tmp_path / "rule", forms.KIND_TOKENS, 600, "coded", small_tables_refused=False)
    assert ["no", "yes"] in _questions_put(held, "record_token")
    monkeypatch.setattr(taxonomy, "identifier_form_hold", lambda name, cells, absent: "")
    away = forms.measure(tmp_path / "away", forms.KIND_TOKENS, 600, "coded", small_tables_refused=False)
    assert ["no", "yes"] not in _questions_put(away, "record_token")



# -- the held walk passes over a layout of another band ---------------------------------


@pytest.mark.parametrize(("layout", "bands"), [
    ("%%%%%%%", ("digits",)),
    ("!!%%%%%", ("digits",)),
    ("@&%&@%&%@@&&%%@&@%&%@&", ("code",)),
    ("@&%&@%-&%@_&&%%@&@%&%@", ("code",)),
    ("%%%-%%-%%%%", ("code",)),
    ("@&%+&@%/&%@@&&%%@&@%&%", ("wide",)),
    ("%%% %%% %%%%", ("wide",)),
    ("%%%%.%%", ("wide",)),
    ("~~~~~~~~", ("digits", "code")),
    ("^^^^-^^^^", ("code",)),
])
def test_a_layout_fills_its_own_bands_alone(layout: str, bands: "tuple[str, ...]") -> None:
    """`_bands_a_layout_fills` names every band a filling of the layout recounts into, and no other.

    Each named band is the shipped `_reads_in_band`'s reading of 2,000
    fillings at steps spread over the room; a band not named is the one no
    filling reads. Mutant: a `+` or `/` read as the code alphabet's (the
    base64 token's layouts named code, so a code slot reads their ceiling).
    """
    assert generation._bands_a_layout_fills(layout) == bands
    room = parsing.layout_room(layout)
    seen = set()
    for step in range(2000):
        filling = generation._filled_layout(layout, 1 + step * 7919)
        read = [band for band in ("digits", "code", "wide") if generation._reads_in_band(filling, band)]
        assert len(read) == 1 and read[0] in bands, (layout, filling, read)
        seen.add(read[0])
    assert seen == set(bands) or room < 2000 or bands == ("digits", "code"), (layout, seen)


@pytest.mark.parametrize(("band", "layout", "passed"), [
    ("code", "@&%+&@%/&%@@&&%%@&@%&%", True),
    ("wide", "@&%+&@%/&%@@&&%%@&@%&%", False),
    ("wide", "@&%&@%&%@@&&%%@&@%&%@&", True),
    ("digits", "@&%&@%&%@@&&%%@&@%&%@&", True),
    ("code", "~~~~~~~~", False),
    ("wide", "~~~~~~~~", True),
    ("code", "+&%&@%&%@@&&%%@&@%&%@&", False),
    ("digits", "-%%%%%%", True),
    ("code", "%%%%%%%", True),
])
def test_a_slot_passes_over_a_layout_of_another_band(band: str, layout: str, passed: bool) -> None:
    """A slot passes over a layout no filling of which reads its band, save one opening a formula, given up at once."""
    assert generation._fillings_outside_the_band(band, layout) is passed


def test_the_token_walk_reads_no_ceiling_and_moves_no_byte(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Fifteen tokens on twenty rows each, held with no person column: each base64 token a layout of its own.

    A code slot read the whole ceiling of every wide layout (a `+` or a
    `/`) it was offered and a wide slot every code one, up to 4,096
    fillings a layout: 64,346 fillings asked for 13 named layouts at 300
    rows, and the twin of the form's 20,000 rows (836 named layouts) was not
    written in three hours. With the pass-over 2,906 are asked, and the twin
    is byte for byte the one the full search writes. With the keys of 24, 43
    and 44 base64 characters beside them (lane CZ-A's repair 1), 9,887
    fillings are asked against the full search's 83,615; with the UUIDs and
    the 64 capitals of repair 2 too, 11,074 against 88,898. Mutants: the
    pass-over withdrawn (the calls), and the pass-over not moving the
    layout's walk (the bytes).
    """
    asked = [0]
    fits = generation._fits_its_slot

    def counted(*arguments: object) -> bool:
        asked[0] += 1
        return fits(*arguments)  # type: ignore[arg-type]

    monkeypatch.setattr(generation, "_fits_its_slot", counted)
    seen = forms.measure(tmp_path, forms.KIND_TOKENS, 300, "coded", people=15, small_tables_refused=False)
    _check(seen)
    passed = asked[0]
    monkeypatch.setattr(generation, "_fillings_outside_the_band", lambda *_a: False)
    asked[0] = 0
    full = tmp_path / "full"
    full.mkdir()
    import contextlib
    import io

    import unanswered_identifier_shapes as shapes
    from synthtwin import cli

    with shapes.nobody_at_the_keyboard(), contextlib.redirect_stdout(io.StringIO()), \
            contextlib.redirect_stderr(io.StringIO()):
        assert cli.main(["generate", f"{tmp_path / 'issued_tokens-profile.json'}", "--out-dir", f"{full}",
                         "--seed", "0", "--replace"], small_tables_refused=False) == 0
    assert (full / "issued_tokens-twin.csv").read_bytes() == (tmp_path / "issued_tokens-twin.csv").read_bytes()
    assert passed * 5 < asked[0] and passed < 40 * 300, (passed, asked[0])
