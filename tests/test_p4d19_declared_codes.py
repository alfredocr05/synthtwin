"""`--code`: the second declaration, and the questions that offer it.

WHAT THIS FILE IS FOR (plan P4-D19). A coding system written in digits
is written exactly like a measurement, and `taxonomy._decide` RULE 5
has recorded since review item P1-R6-F7 that the values cannot settle
which it is. Before this landing the tool had one declaration,
`--identifier`, which publishes NOTHING -- right for a record number
and wrong for a vaccine code, whose distribution is the whole point of
the column. `--code` is the second declaration, and `asking` is how the
tool offers it to somebody who has not thought about the question.

THE OWNER'S EIGHTEEN SYSTEMS are swept at the foot of this file: NDC,
CVX, MVX, UDI, MS-DRG, APC, UB-04, NPI, the clinical grouper codes, Elixhauser, Charlson,
CMS-HCC, CDPS, HGNC ID, HGVS, OMIM, ClinVar and GA4GH. Two of them --
a padded vaccine code and a padded revenue code -- came back from the
twin with their leading zeros gone before this landing, and the sweep
is what keeps them from going back.
"""

import pathlib
import random
import tempfile

import fixtures
import pytest

from synthtwin import (
    asking,
    contract,
    errors,
    generation,
    profile,
    reading,
    taxonomy,
)


def _described(
    values: "list[str]",
    name: str = "col",
    codes: "list[str] | None" = None,
    floor: int = 1,
) -> "dict[str, object]":
    """Describe a one-column table, optionally declaring it a code."""
    folder = pathlib.Path(tempfile.mkdtemp())
    table = fixtures.write(
        folder, "t.csv", fixtures.single_column_table(name, values)
    )
    read = reading.read_table(f"{table}")
    settings = taxonomy.Settings(small_cell_floor=floor)
    return profile.build_document(read, settings, [], codes or [])


def _loaded(document: "dict[str, object]") -> "contract.Profile":
    """The same document, read back through the strict loader."""
    folder = pathlib.Path(tempfile.mkdtemp())
    written = fixtures.write_profile(folder, "t.json", document)
    return contract.load_profile(f"{written}")


def _block(document: "dict[str, object]", name: str) -> "dict[str, object]":
    for block in document["columns"]:
        if block["name"] == name:
            return block
    raise AssertionError(f"no column {name!r}")


# -- what the declaration does ----------------------------------------


def test_a_padded_code_column_is_read_as_a_number_without_the_word() -> None:
    """The defect this landing closes, stated as a test.

    `08` is a vaccine code. Undeclared, the column reads as a quantity,
    so the profile publishes a ladder of real codes and the twin loses
    the padding.
    """
    values = ["08", "20", "213", "141", "03"] * 20
    block = _block(_described(values), "col")
    assert block["role"] == taxonomy.ROLE_COUNT
    assert "percentiles" in block


def test_the_same_column_declared_is_read_as_labels() -> None:
    """With the word, every spelling is kept and counted."""
    values = ["08", "20", "213", "141", "03"] * 20
    block = _block(_described(values, codes=["col"]), "col")
    assert block["role"] in taxonomy.ROLES_PUBLISHING_LABELS
    assert "percentiles" not in block


def test_a_declared_code_column_keeps_its_leading_zeros() -> None:
    """The twin's cells are the published spellings, padding and all."""
    values = ["08", "20", "213", "141", "03"] * 20
    document = _described(values, codes=["col"])
    twin = generation.generate(_loaded(document), 5)
    written = {cell for cell in twin.columns[0]}
    assert any(cell[0] == "0" and len(cell) > 1 for cell in written), (
        "every leading zero was lost, which is the defect --code closes"
    )
    assert written <= set(values)


def test_a_declared_code_publishes_no_numeric_ladder() -> None:
    """No mean, no smallest, no largest -- those are real codes."""
    values = [f"{number:03d}" for number in range(100, 340)]
    block = _block(_described(values, codes=["col"]), "col")
    for field in ("mean", "minimum", "maximum", "percentiles", "std_dev"):
        assert field not in block, f"{field} was published for a code"


def test_a_declared_code_still_publishes_its_distribution() -> None:
    """Unlike `--identifier`, the counts are kept: they are the point."""
    values = ["01"] * 100 + ["02"] * 60 + ["03"] * 20
    block = _block(_described(values, codes=["col"]), "col")
    counted = {
        level["label"]: level["count"] for level in block["levels"]
    }
    assert counted == {"01": 100, "02": 60, "03": 20}


def test_declaring_a_column_of_dates_stops_it_being_a_date() -> None:
    """A declaration beats the date rule, as it beats the numeric one."""
    values = [f"2024-01-{day:02d}" for day in range(1, 29)] * 8
    plain = _block(_described(values), "col")
    declared = _block(_described(values, codes=["col"]), "col")
    assert plain["role"] == taxonomy.ROLE_DATETIME
    assert declared["role"] != taxonomy.ROLE_DATETIME


def test_declaring_a_column_of_clock_times_stops_it_being_a_clock() -> None:
    """Rule 8 is silenced too, for the same reason."""
    values = [f"{hour:02d}:{minute:02d}" for hour in range(8, 20)
              for minute in (0, 15, 30, 45)] * 5
    plain = _block(_described(values), "col")
    declared = _block(_described(values, codes=["col"]), "col")
    assert plain["role"] == taxonomy.ROLE_CLOCK
    assert declared["role"] != taxonomy.ROLE_CLOCK


def test_declaring_an_affixed_column_stops_the_core_being_a_number() -> None:
    """`HCC19` publishes percentiles of `19` until it is declared."""
    values = [f"HCC{number}" for number in range(1, 190)]
    plain = _block(_described(values), "col")
    declared = _block(_described(values, codes=["col"]), "col")
    assert plain["role"] == taxonomy.ROLE_AFFIXED
    assert declared["role"] != taxonomy.ROLE_AFFIXED


def test_the_declaration_is_recorded_in_the_profile() -> None:
    """A rerun needs no typing because the answers are in the file."""
    document = _described(["01", "02", "03"] * 40, codes=["col"])
    assert document["settings"]["forced_codes"] == ["col"]


def test_a_declared_name_the_table_lacks_is_refused_by_the_contract() -> None:
    """S8 covers the second declaration as it covers the first."""
    document = _described(["01", "02", "03"] * 40, codes=["col"])
    document["settings"]["forced_codes"] = ["not_a_column"]
    with pytest.raises(errors.ProfileError):
        _loaded(document)


# -- which columns are worth asking about ------------------------------


@pytest.mark.parametrize(
    "values,expected",
    [
        (["08", "20", "213"], asking.BECAUSE_PADDED),
        (["450", "300", "220"], asking.BECAUSE_FIXED_WIDTH),
        (["1", "2", "3"], None),
        (["20", "7", "113"], None),
        (["1.5", "2.7"], None),
        (["-3", "4"], None),
        (["1e3", "2e3"], None),
        (["", ""], None),
        (["12", "34"], None),
    ],
)
def test_the_signal_fires_only_where_it_should(
    values: "list[str]", expected: "str | None"
) -> None:
    """Padding and fixed width ask; a plain count does not.

    A two-digit fixed width does NOT ask: `12`, `34` is far more often
    a count than a code, and asking about it is the noise that makes
    somebody stop reading the questions.
    """
    assert asking.why_worth_asking(values) == expected


def test_a_measurement_column_is_never_asked_about() -> None:
    """Ages spread across widths and carry no padding."""
    rng = random.Random(4)
    ages = [f"{rng.randrange(1, 99)}" for _ in range(240)]
    assert asking.why_worth_asking(ages) is None


def test_an_already_declared_column_is_not_asked_about() -> None:
    """Asking again would say the answer had not been heard."""
    values = ["08", "20", "213", "141", "03"] * 20
    folder = pathlib.Path(tempfile.mkdtemp())
    table = fixtures.write(
        folder, "t.csv", fixtures.single_column_table("col", values)
    )
    read = reading.read_table(str(table))
    settings = taxonomy.Settings(small_cell_floor=1)
    document = profile.build_document(read, settings, [], ["col"])
    assert asking.questions_for(document, read.columns, settings, ["col"]) == []


def test_a_question_carries_examples_and_never_a_whole_column() -> None:
    """The person needs values to answer; four of them is enough."""
    values = ["08", "20", "213", "141", "03"] * 20
    folder = pathlib.Path(tempfile.mkdtemp())
    table = fixtures.write(
        folder, "t.csv", fixtures.single_column_table("col", values)
    )
    read = reading.read_table(str(table))
    settings = taxonomy.Settings(small_cell_floor=1)
    document = profile.build_document(read, settings, [], [])
    asked = asking.questions_for(document, read.columns, settings, [])
    assert len(asked) == 1
    assert asked[0].name == "col"
    assert len(asked[0].examples) == 4
    assert len(set(asked[0].examples)) == 4


# -- the owner's eighteen coding systems -------------------------------

_SYSTEMS: "dict[str, list[str]]" = {}


def _fill_systems() -> None:
    rng = random.Random(11)

    def tail(make: "object", distinct: int, rows: int = 240) -> "list[str]":
        pool = [make(index) for index in range(distinct)]
        weights = [max(1, int(60 / (index + 1))) for index in range(distinct)]
        return rng.choices(pool, weights=weights, k=rows)

    _SYSTEMS["ndc"] = tail(
        lambda i: f"{rng.randrange(10**4, 10**5):05d}"
        f"-{rng.randrange(10**3, 10**4):04d}-{rng.randrange(0, 99):02d}",
        30,
    )
    _SYSTEMS["cvx"] = tail(
        lambda i: rng.choice(
            [f"{rng.randrange(1, 99):02d}", f"{rng.randrange(100, 300)}"]
        ),
        18,
    )
    _SYSTEMS["mvx"] = tail(
        lambda i: "".join(
            rng.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") for _ in range(3)
        ),
        12,
    )
    _SYSTEMS["udi"] = tail(
        lambda i: f"(01){rng.randrange(10**13, 10**14)}"
        f"(17){rng.randrange(200000, 301231)}(10)LOT{rng.randrange(100, 999)}",
        20,
    )
    _SYSTEMS["ms_drg"] = tail(lambda i: f"{rng.randrange(1, 999):03d}", 25)
    _SYSTEMS["apc"] = tail(lambda i: f"{rng.randrange(1000, 9999)}", 22)
    _SYSTEMS["ub04_rev"] = tail(
        lambda i: f"{rng.randrange(1, 999) * 10:04d}", 15
    )
    _SYSTEMS["npi"] = tail(lambda i: f"{rng.randrange(10**9, 10**10)}", 40)
    _SYSTEMS["clinical_class"] = tail(lambda i: f"{rng.randrange(1, 259)}", 20)
    _SYSTEMS["elixhauser"] = tail(
        lambda i: rng.choice(
            [
                "CHF", "VALV", "PULMCIRC", "PERIVASC", "HTN", "PARA",
                "NRO", "CHRNLUNG", "DM", "HYPOTHY", "RENLFAIL", "LIVER",
            ]
        ),
        12,
    )
    _SYSTEMS["charlson"] = tail(lambda i: f"{rng.randrange(0, 13)}", 13)
    _SYSTEMS["cms_hcc"] = tail(lambda i: f"HCC{rng.randrange(1, 189)}", 30)
    _SYSTEMS["cdps"] = tail(
        lambda i: f"{rng.choice(['CAR', 'PSY', 'SKC', 'CNS', 'PUL', 'GI'])}"
        f"-{rng.choice(['L', 'M', 'H', 'VH'])}",
        14,
    )
    _SYSTEMS["hgnc_id"] = tail(lambda i: f"HGNC:{rng.randrange(1, 45000)}", 30)
    _SYSTEMS["hgvs"] = tail(
        lambda i: f"NM_{rng.randrange(10**5, 10**6):06d}"
        f".{rng.randrange(1, 9)}:c.{rng.randrange(1, 3000)}"
        f"{rng.choice('ACGT')}>{rng.choice('ACGT')}",
        35,
    )
    _SYSTEMS["omim"] = tail(lambda i: f"{rng.randrange(100000, 620000)}", 30)
    _SYSTEMS["clinvar"] = tail(
        lambda i: f"VCV{rng.randrange(1, 999999):09d}", 35
    )
    _SYSTEMS["ga4gh"] = tail(
        lambda i: "ga4gh:VA."
        + "".join(
            rng.choice(
                "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                "abcdefghijklmnopqrstuvwxyz0123456789_-"
            )
            for _ in range(32)
        ),
        35,
    )


_fill_systems()

# The systems written in digits and nothing else. These are the ones
# that need the word: everything else already lands on a label role
# because a letter or a mark keeps it off the numeric rules.
_DIGIT_ONLY = (
    "cvx", "ms_drg", "apc", "ub04_rev", "npi", "clinical_class", "omim",
)


def _shape(text: str) -> str:
    """The written shape of a cell: figures, letters, marks kept."""
    out = ""
    for character in text:
        if "0" <= character <= "9":
            out = out + "%"
        elif ("a" <= character <= "z") or ("A" <= character <= "Z"):
            out = out + "@"
        else:
            out = out + character
    return out


@pytest.mark.parametrize("system", sorted(_SYSTEMS))
def test_every_coding_system_round_trips_in_its_own_shapes(
    system: str,
) -> None:
    """Every twin cell wears a shape the real column wrote.

    The digit-only systems are declared with `--code`, which is what
    the person running the tool would do. The rest need no declaration:
    a letter or a mark already keeps them off the numeric rules.
    """
    values = _SYSTEMS[system]
    codes = [system] if system in _DIGIT_ONLY else []
    document = _described(values, name=system, codes=codes)
    twin = generation.generate(_loaded(document), 3)
    real = {_shape(value) for value in values}
    written = {_shape(cell) for cell in twin.columns[0]}
    assert written <= real, (
        f"{system}: the twin wrote shapes the real column never did: "
        f"{sorted(written - real)}"
    )


@pytest.mark.parametrize("system", sorted(_DIGIT_ONLY))
def test_every_digit_only_system_is_offered_or_needs_no_offer(
    system: str,
) -> None:
    """A digit-only system either raises a question or is unambiguous.

    The grouper column is the honest gap: one to three digits with no
    padding is
    written exactly like a count, so nothing in the values can raise
    the question. It is named here rather than hidden, and `--code`
    still describes it correctly when somebody says the word.
    """
    values = _SYSTEMS[system]
    reason = asking.why_worth_asking(values)
    if system == "clinical_class":
        assert reason is None, "the grouper column is the documented gap; see the docstring"
    else:
        assert reason is not None, (
            f"{system} is written in digits and would be read as a "
            f"measurement, but nothing offers the question"
        )


# -- P4-D22: a declared code column always publishes its codes ---------


def _thin_tailed_codes(count: int = 240) -> "list[str]":
    """A laboratory-code column: many codes, none of them repeated much."""
    rng = random.Random(21)
    pool = [
        f"{rng.randrange(1000, 99999)}-{rng.randrange(0, 9)}"
        for _each in range(140)
    ]
    return [rng.choice(pool) for _each in range(count)]


def test_a_thin_tailed_code_column_published_nothing_until_p4d22() -> None:
    """The defect P4-D22 closes, stated as a test.

    Undeclared, such a column clears neither door to the label roles --
    too many different codes to be a set of categories, and no code
    repeated enough to be a long tail -- so it falls to free text, which
    publishes no value at all and whose twin holds not one real code.
    """
    values = _thin_tailed_codes()
    block = _block(_described(values), "col")
    assert block["role"] == taxonomy.ROLE_TEXT
    assert "levels" not in block


def test_the_same_column_declared_publishes_every_code() -> None:
    """Declared, the detection line does not apply and the codes are named."""
    values = _thin_tailed_codes()
    block = _block(_described(values, codes=["col"]), "col")
    assert block["role"] == taxonomy.ROLE_LONG_TAIL
    named = {level["label"]: level["count"] for level in block["levels"]}
    counted: "dict[str, int]" = {}
    for value in values:
        counted[value] = counted[value] + 1 if value in counted else 1
    assert named == counted, "the published counts are not the column's own"


def test_the_twin_of_a_declared_code_column_holds_the_same_codes() -> None:
    """Same codes, same counts -- which is what makes every rollup exact."""
    values = _thin_tailed_codes()
    document = _described(values, codes=["col"])
    twin = generation.generate(_loaded(document), 5)
    made: "dict[str, int]" = {}
    for cell in twin.columns[0]:
        made[cell] = made[cell] + 1 if cell in made else 1
    counted: "dict[str, int]" = {}
    for value in values:
        counted[value] = counted[value] + 1 if value in counted else 1
    assert made == counted


@pytest.mark.parametrize(
    "name,rollup",
    [
        ("the exact code", lambda v: v),
        ("the part before the mark", lambda v: v[: v.find("-")]),
        ("the part after it", lambda v: v[v.find("-") + 1 :]),
        ("how long the code is", lambda v: f"{len(v)}"),
    ],
)
def test_every_rollup_of_a_declared_code_column_reproduces(
    name: str, rollup: "object"
) -> None:
    """THE POINT OF P4-D22, and it is worth stating as its own test.

    synthtwin knows no coding system and models no hierarchy. It does
    not have to: a twin holding the same codes the same number of times
    reproduces EVERY function of those codes exactly -- the prefix a
    hierarchy groups by, the suffix a check digit sits in, the length a
    reader splits on. Hierarchy is not built here; it is a consequence
    of holding the right values the right number of times.
    """
    assert callable(rollup)
    values = _thin_tailed_codes()
    document = _described(values, codes=["col"])
    twin = generation.generate(_loaded(document), 5)

    def counted(cells: "list[str]") -> "dict[str, int]":
        out: "dict[str, int]" = {}
        for cell in cells:
            key = f"{rollup(cell)}"
            out[key] = out[key] + 1 if key in out else 1
        return out

    assert counted(values) == counted([cell for cell in twin.columns[0]]), (
        f"{name} does not come back the same"
    )


def test_the_line_is_lifted_by_the_declaration_and_nothing_else() -> None:
    """A column of prose is still free text, at every floor.

    The detection line's job is keeping names, addresses and free
    comments out of the label roles. P4-D22 lifts it for a DECLARED
    column and for no other, so that job is untouched.
    """
    rng = random.Random(8)
    words = "patient reports mild chest pain on exertion denies fever".split()
    prose = [
        " ".join(rng.choice(words) for _each in range(rng.randint(5, 10)))
        for _row in range(240)
    ]
    assert _block(_described(prose), "col")["role"] == taxonomy.ROLE_TEXT
    assert (
        _block(_described(prose, floor=11), "col")["role"]
        == taxonomy.ROLE_TEXT
    )
