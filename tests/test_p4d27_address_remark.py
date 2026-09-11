"""The address decline speaks (contract NF50, residual R-P4-39).

Plan decision P4-D27 built the rule that stops `user12345@example.org`
being read as a number wearing the affix pair `user` / `@example.org`.
That rule is right and nothing here touches it: reading the column that
way published a mean of 53,574.055 over 400 rows, which is the average
of real identifiers.

**WHAT WAS WRONG IS THAT THE DECLINE WAS SILENT.** A column that had
been described as numbers stopped being described as numbers, and no
enumerated sentence anywhere said so -- `taxonomy.NOTE_ARITY` carried no
address form at all, so the profile, the summary beside it and the
twin's own report had nothing to print. Principle 5 does not say a
column is either handled or declined; it says a column is either
handled or **declined with a plain-language explanation**.

WHAT IS PINNED HERE:

- the address column CARRIES the sentence;
- the sentence NAMES THE SHAPE it declined for, and names all three
  declarations -- `--identifier`, `--code`, `--measurement` -- with
  what each one does, because a list of flags with no consequence
  beside them is a list nobody can choose from;
- **the sentence ROUTES NOTHING**, measured rather than asserted: with
  the decline's own question answered False the block is identical key
  for key except that the sentence is gone;
- it carries NO VALUE of the column -- no address, and no count;
- **the columns that must stay quiet**, which is most of this file. A
  quantity wearing a unit, a currency amount, a dose, and the two
  shapes review item P1-R6-F8 pins together (`1mg` and `code1`) each
  keep their reading and hear nothing about addresses;
- and a column the person declared a MEASUREMENT keeps its affixed
  reading, so there is no decline to explain and no sentence is
  written.
"""

import pathlib
import random
import tempfile

import fixtures
from synthtwin import profile, reading, taxonomy

# The sentence's own opening, which is fixed text of the form and not an
# argument. Every test below finds the remark by it rather than by a
# position in the list, because the order remarks are raised in is not
# what this file is about.
OPENING = "the values in this column are a number wrapped in an electronic"


def _described(
    values: "list[str]",
    name: str = "email",
    identifiers: "list[str] | None" = None,
    codes: "list[str] | None" = None,
    measurements: "list[str] | None" = None,
) -> dict:
    """One column, described the way `synthtwin profile` describes it."""
    folder = pathlib.Path(tempfile.mkdtemp())
    table = fixtures.write(
        folder, "thing.csv", fixtures.single_column_table(name, values)
    )
    return profile.build_document(
        reading.read_table(f"{table}"),
        taxonomy.Settings(),
        [] if identifiers is None else identifiers,
        forced_codes=codes,
        forced_measurements=measurements,
    )


def _address_remark(document: dict) -> "str | None":
    for remark in document["columns"][0]["remarks"]:
        if OPENING in remark:
            return remark
    return None


def _identifiers(count: int = 400, seed: int = 11) -> "list[int]":
    """Distinct whole numbers, as a record-number column holds them."""
    return random.Random(seed).sample(range(10000, 99999), count)


def _addresses() -> "list[str]":
    return [f"user{number}@example.org" for number in _identifiers()]


# -- the column this form exists for ----------------------------------


def test_the_address_column_is_told_why_it_stopped_being_numbers() -> None:
    """THE WHOLE OF WHAT THIS BUYS, on the column R-P4-39 was opened for."""
    document = _described(_addresses())
    said = _address_remark(document)
    assert said is not None, document["columns"][0]["remarks"]


def test_the_sentence_names_the_shape_it_declined_for() -> None:
    """A person recognizes their own column by the shape, not by a flag.

    The rule makes a POSITIVE identification -- an at sign, a host, a
    dot, a letter label -- and the sentence describes that same shape,
    so somebody reading it can tell whether it is talking about their
    column.
    """
    said = _address_remark(_described(_addresses()))
    assert said is not None
    assert "electronic address" in said
    assert "at sign" in said
    assert "host" in said
    assert "dot label" in said


def test_the_sentence_names_all_three_routes_and_what_each_one_does() -> None:
    """THE PART THE CLOSE PLAN ASKED FOR.

    `--identifier` alone was what the free-text remark beside this one
    already said, and it is the WRONG answer for a column somebody
    wants the distribution of. All three declarations are named, each
    with its consequence, and each consequence is measured in
    `test_each_named_route_does_what_the_sentence_says` below.
    """
    said = _address_remark(_described(_addresses()))
    assert said is not None
    for flag in ("--identifier", "--code", "--measurement"):
        assert flag in said, flag
    assert "no value of this column is published at all" in said
    assert "each spelling is published with how many rows carried it" in said
    assert "described as numbers wearing that address" in said


def test_each_named_route_does_what_the_sentence_says() -> None:
    """A route named in a sentence is a promise, so it is measured.

    Three declarations, three roles, three different published shapes.
    A wording that named a flag doing something else would be a
    sentence sending somebody to the wrong command.
    """
    values = _addresses()
    declared = _described(values, identifiers=["email"])["columns"][0]
    assert declared["role"] == taxonomy.ROLE_IDENTIFIER
    assert "levels" not in declared and "mean" not in declared

    coded = _described(values, codes=["email"])["columns"][0]
    assert coded["role"] == taxonomy.ROLE_LONG_TAIL
    assert coded["levels"], "the --code route must publish the spellings"

    measured = _described(values, measurements=["email"])["columns"][0]
    assert measured["role"] == taxonomy.ROLE_AFFIXED
    assert "mean" in measured and "percentiles" in measured


def test_the_sentence_says_it_decides_nothing() -> None:
    """The README's ratified rule, kept in the sentence itself.

    No rule of this package may decide the identifier role from a
    column's values (P1-R6-F8). This sentence proposes and says so.
    """
    said = _address_remark(_described(_addresses()))
    assert said is not None
    assert "THIS SENTENCE DECIDES NOTHING" in said


# -- it routes nothing, measured -------------------------------------


def test_the_sentence_moves_no_role_and_no_published_fact(monkeypatch) -> None:
    """WITH THE SENTENCE AND WITHOUT IT, ONE BLOCK.

    `_declined_as_an_address` is consulted for exactly one purpose --
    raising this remark -- so answering it False rebuilds the document
    as it was before this landing. Everything except `remarks` must be
    identical, and `remarks` must differ by this one sentence and
    nothing else. An edit that let the remark reach a role, a key or a
    count turns this red.
    """
    values = _addresses()
    with_it = _described(values)["columns"][0]
    monkeypatch.setattr(taxonomy, "_declined_as_an_address", lambda _cells: False)
    without = _described(values)["columns"][0]

    said = _address_remark({"columns": [with_it]})
    assert said is not None
    assert _address_remark({"columns": [without]}) is None

    assert with_it["role"] == without["role"]
    for key in sorted(set(with_it) | set(without)):
        if key == "remarks":
            continue
        assert with_it[key] == without[key], key
    kept = [line for line in with_it["remarks"] if line != said]
    assert kept == list(without["remarks"])


def test_the_sentence_carries_no_value_of_the_column() -> None:
    """A sentence of this format carries counts, never a cell.

    This one carries no count either: arity 0, so the whole text is the
    form's own words. Neither an address of the column nor the affix
    pair the decline was about may appear in it.
    """
    values = _addresses()
    said = _address_remark(_described(values))
    assert said is not None
    assert said == taxonomy.rendered(taxonomy.REMARK_ADDRESS_NOT_A_QUANTITY, ())
    assert taxonomy.NOTE_ARITY[taxonomy.REMARK_ADDRESS_NOT_A_QUANTITY] == 0
    for value in set(values):
        assert value not in said, value
    assert "@example.org" not in said
    for figure in "0123456789":
        assert figure not in said, figure


# -- and where it must stay quiet -------------------------------------


def test_a_weight_with_a_unit_says_nothing() -> None:
    """`72.4 kg` keeps its reading, so there is nothing to explain."""
    rng = random.Random(3)
    values = [f"{rng.uniform(45, 120):.1f} kg" for _each in range(400)]
    document = _described(values, name="weight")
    assert document["columns"][0]["role"] == taxonomy.ROLE_AFFIXED
    assert _address_remark(document) is None


def test_a_currency_amount_says_nothing() -> None:
    """`$52000`, all different and whole, is a salary column."""
    values = [f"${number}" for number in _identifiers()]
    document = _described(values, name="salary")
    assert document["columns"][0]["role"] == taxonomy.ROLE_AFFIXED
    assert _address_remark(document) is None


def test_a_repeating_dose_says_nothing() -> None:
    """`450 mg` is a dose whatever else is true of it.

    THE COLUMN IS BUILT PAST THE CATEGORICAL CEILING ON PURPOSE. Four
    amounts over four hundred rows is a set of CATEGORIES -- the
    ceiling is a tenth of the rows -- and rule 9 is never reached, so
    such a column would be quiet without this rule being asked anything
    at all. Sixty of them reach the affixed rule while still repeating,
    which is the shape this test means: a quantity whose values are
    whole and shared, wearing a unit.
    """
    rng = random.Random(4)
    amounts = list(range(50, 3050, 50))
    assert 450 in amounts and len(amounts) == 60
    values = [f"{rng.choice(amounts)} mg" for _each in range(400)]
    document = _described(values, name="dose")
    assert document["columns"][0]["role"] == taxonomy.ROLE_AFFIXED
    assert _address_remark(document) is None


def test_the_two_shapes_no_value_can_separate_are_both_quiet() -> None:
    """`1mg` and `code1` are one shape of string (P1-R6-F8).

    Any rule that told them apart is the defect review deleted four
    times. Neither hears about addresses, and they are asserted
    together so that a rule reaching one of them fails here.
    """
    amounts = [f"{index}mg" for index in range(1, 31)]
    codes = [f"code{index}" for index in range(1, 31)]
    assert _address_remark(_described(amounts, name="dose")) is None
    assert _address_remark(_described(codes, name="thing")) is None


def test_a_letter_prefixed_currency_says_nothing() -> None:
    """`USD100` and `Rs52000` are quantities and keep their reading."""
    for prefix, name in (("USD", "fee"), ("Rs", "salary")):
        values = [f"{prefix}{number}" for number in _identifiers()]
        document = _described(values, name=name)
        assert document["columns"][0]["role"] == taxonomy.ROLE_AFFIXED
        assert _address_remark(document) is None, prefix


def test_a_quantity_measured_at_a_condition_says_nothing() -> None:
    """`100 ms @ ambient` carries an at sign and is not an address.

    The rule behind this sentence identifies an address POSITIVELY --
    a host and a dot label after the at sign -- rather than declining
    on the character. A sentence raised here would be this project's
    second version of that rule speaking through a remark.
    """
    values = [f"{number} ms @ ambient" for number in range(100, 500)]
    document = _described(values, name="settling")
    assert document["columns"][0]["role"] == taxonomy.ROLE_AFFIXED
    assert _address_remark(document) is None


def test_a_column_of_addresses_at_MANY_HOSTS_says_nothing() -> None:
    """THE ONE QUIET CASE THAT IS NOT QUIET BY THE CONTROL FLOW.

    Every other silent column above keeps its affixed reading, so the
    decline question is never even asked of it. This one is different:
    the affixed rule DOES decline, and it declines for a reason of its
    own -- no single pair reaches the parse line, because the hosts
    differ -- and NOT because the winning pair is an address. NF50 is
    carried on the second reason only.

    A rule that asked "does any cell here look like an address?"
    instead of "is the WINNING PAIR an address?" would speak here, and
    the sentence it wrote would name a decline that did not happen and
    send its reader to three declarations for the wrong reason. This
    test is where such a rule meets its counterexample.
    """
    hosts = ("example.org", "example.net", "example.com", "example.edu")
    values = [
        f"user{number}@{hosts[index % len(hosts)]}"
        for index, number in enumerate(_identifiers())
    ]
    document = _described(values)
    assert document["columns"][0]["role"] == taxonomy.ROLE_TEXT
    assert _address_remark(document) is None


# -- and the declaration silences it ----------------------------------


def test_a_declared_measurement_keeps_its_reading_and_hears_nothing() -> None:
    """THE PERSON WHO OWNS THE TABLE HAS THE LAST WORD.

    `--measurement` carries the address column past the decline, so it
    takes the affixed role and its numbers are described. There is then
    no decline to explain, and a sentence saying synthtwin did NOT read
    the column as numbers would be false of the document it sits in.
    """
    document = _described(_addresses(), measurements=["email"])
    block = document["columns"][0]
    assert block["role"] == taxonomy.ROLE_AFFIXED
    assert _address_remark(document) is None


def test_a_declared_code_column_hears_nothing_either() -> None:
    """`--code` is one of the three routes, already taken.

    The affix rule is not run under that declaration at all, so there
    is no decline of its making to report, and proposing three
    declarations to somebody who has just made one of them is noise.
    """
    document = _described(_addresses(), codes=["email"])
    assert document["columns"][0]["role"] == taxonomy.ROLE_LONG_TAIL
    assert _address_remark(document) is None


def test_a_declared_identifier_hears_nothing_either() -> None:
    """The declared identifier returns before any rule reads a value."""
    document = _described(_addresses(), identifiers=["email"])
    assert document["columns"][0]["role"] == taxonomy.ROLE_IDENTIFIER
    assert _address_remark(document) is None


# -- the sibling this landing found by looking ------------------------


def _with_a_stand_in(prefix: str, suffix: str) -> "list[str]":
    """189 cores between 50 and 70, and eleven spelled `-999`."""
    rng = random.Random(7)
    cores = [rng.randint(50, 70) for _each in range(189)] + [-999] * 11
    rng.shuffle(cores)
    return [f"{prefix}{core}{suffix}" for core in cores]


def test_a_declared_address_column_judges_its_stand_ins_over_the_cores() -> None:
    """THE CORE PASS ASKED A DIFFERENT QUESTION THAN ITS OWN CALLER.

    `_cores_judged` runs where the role was decided as `affixed_number`
    -- and the role is decided WITH the person's declarations, while
    the pass re-derived the reading WITHOUT them. On an address column
    carried past the decline by `--measurement` the two disagreed: the
    caller saw the affixed role, the pass saw the decline, and every
    cell went unjudged.

    Measured before the repair, and the numbers are why this is not a
    tidy-up: no verdict was published at all, `-999` stood as the
    column's smallest reading, and the mean came out **1.785** where
    the same column wearing an ordinary pair reads **60.03**. That is
    the silent statistical wrongness C6-5's core pass exists to
    prevent, reached through the one declaration whose whole meaning is
    that these numbers are real.

    The two columns are asserted AGAINST EACH OTHER rather than against
    written numbers, because what was wrong is that they disagreed.
    """
    declared = _described(
        _with_a_stand_in("user", "@example.org"),
        name="email",
        measurements=["email"],
    )["columns"][0]
    ordinary = _described(
        _with_a_stand_in("user", "_mg"), name="dose"
    )["columns"][0]

    assert declared["role"] == taxonomy.ROLE_AFFIXED
    assert ordinary["role"] == taxonomy.ROLE_AFFIXED
    assert declared["sentinel_verdicts"], (
        "the declared column published no stand-in verdict, so the core "
        "pass never ran on it"
    )
    assert declared["sentinel_verdicts"] == ordinary["sentinel_verdicts"]
    assert declared["n_present"] == ordinary["n_present"] == 189
    assert declared["n_missing"] == ordinary["n_missing"] == 11
    assert declared["mean"] == ordinary["mean"]
    assert declared["percentiles"]["min"] == ordinary["percentiles"]["min"]
