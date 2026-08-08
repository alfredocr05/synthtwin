"""The written summary, and properties that must hold for any table.

Plan P1-D6 (the disclosure the reader sees before moving anything) and
P1-D8 (the property battery). The properties are the part that scales:
they hold for tables nobody wrote a case for, which is where a
statistical defect usually hides.
"""

import pathlib
import random

import fixtures
from synthtwin import profile, reading, summary, taxonomy

SETTINGS = taxonomy.Settings()


def _profile_of(tmp_path: pathlib.Path, text: str, name: str = "t.csv"):
    table = reading.read_table(str(fixtures.write(tmp_path, name, text)))
    document = profile.build_document(table, SETTINGS, [])
    return table, document, summary.render(document, "read as UTF-8.")


# -- the summary ------------------------------------------------------


def test_the_summary_names_every_column_once(tmp_path: pathlib.Path) -> None:
    table, _document, text = _profile_of(tmp_path, fixtures.every_role_table())
    for name in table.column_names:
        assert text.count(f"  {name}\n") == 1, name


def test_each_role_is_named_in_plain_language(
    tmp_path: pathlib.Path,
) -> None:
    _table, document, text = _profile_of(tmp_path, fixtures.every_role_table())
    for column in document["columns"]:
        assert "read as:" in text
    # No role name leaks through as jargon: the reader sees words.
    assert "free_text" not in text
    assert "record numbers or codes" in text
    assert "free text" in text


def test_the_disclosure_section_is_always_present(
    tmp_path: pathlib.Path,
) -> None:
    _table, _document, text = _profile_of(tmp_path, "a,b\n1,x\n2,y\n3,x\n")
    assert "WHAT THIS PROFILE CARRIES FROM YOUR TABLE" in text
    assert "real-derived material" in text


def test_the_summary_says_when_nothing_is_visible(
    tmp_path: pathlib.Path,
) -> None:
    values = [f"code{index}" for index in range(40)]
    _table, _document, text = _profile_of(
        tmp_path, fixtures.single_column_table("token", values)
    )
    assert "No column has labels visible" in text


def test_the_summary_lists_what_was_withheld(tmp_path: pathlib.Path) -> None:
    _table, _document, text = _profile_of(tmp_path, fixtures.every_role_table())
    assert "What was left out, column by column:" in text
    assert "record_code" in text


def test_the_summary_and_the_document_cannot_disagree(
    tmp_path: pathlib.Path,
) -> None:
    # The summary is rendered from the document alone, so a number in
    # the words is a number in the record.
    _table, document, text = _profile_of(tmp_path, fixtures.every_role_table())
    assert f"{document['n_rows']} rows" in text
    for column in document["columns"]:
        if column["role"] in (taxonomy.ROLE_COUNT, taxonomy.ROLE_CONTINUOUS):
            assert f"{column['percentiles']['max']}" in text


# -- properties that must hold for any table --------------------------


def _random_table(seed: int) -> str:
    """A neutral table of mixed column kinds, built from one seed."""
    rng = random.Random(seed)
    n_rows = rng.randint(20, 300)
    header = ["code", "group", "count_of", "measure", "day", "flag", "note"]
    rows = []
    for index in range(n_rows):
        rows.append(
            [
                f"K{index:06d}",
                fixtures.LABELS[rng.randrange(len(fixtures.LABELS))],
                "" if rng.random() < 0.1 else str(rng.randint(0, 50)),
                f"{rng.gauss(10, 3):.3f}",
                f"2024-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}",
                "yes" if rng.random() < 0.4 else "no",
                "" if rng.random() < 0.5 else f"note {index} in words",
            ]
        )
    return fixtures.rows_to_csv(header, rows)


def test_counts_add_up_for_many_random_tables(tmp_path: pathlib.Path) -> None:
    for seed in range(12):
        table, document, _text = _profile_of(
            tmp_path, _random_table(seed), f"t{seed}.csv"
        )
        assert document["n_rows"] == table.n_rows
        assert document["n_columns"] == len(table.column_names)
        for column in document["columns"]:
            assert column["n_present"] + column["n_missing"] == table.n_rows
            assert column["n_missing"] == sum(
                column["missing_by_class"].values()
            ), (
                f"the missing values of {column['name']} do not add up to "
                "the counts reported for each class"
            )


def test_percentiles_never_go_down_for_many_random_tables(
    tmp_path: pathlib.Path,
) -> None:
    for seed in range(12):
        _table, document, _text = _profile_of(
            tmp_path, _random_table(seed), f"t{seed}.csv"
        )
        for column in document["columns"]:
            if "percentiles" not in column:
                continue
            ladder = column["percentiles"]
            values = [ladder[label] for label, _num, _den in taxonomy.LADDER]
            assert values == sorted(values), column["name"]


def test_counted_values_match_an_independent_count(
    tmp_path: pathlib.Path,
) -> None:
    # Recomputed here from the raw column rather than trusting the
    # profiler's own bookkeeping.
    for seed in range(6):
        table, document, _text = _profile_of(
            tmp_path, _random_table(seed), f"t{seed}.csv"
        )
        for column in document["columns"]:
            values = table.columns[column["position"] - 1]
            blanks = len([value for value in values if not value.strip()])
            classes = column["missing_by_class"]
            # A blank is counted under its own class unless the class
            # itself falls below the small-cell floor, in which case it
            # joins the withheld total. Either way the two must account
            # for every blank cell.
            assert classes.get("(blank)", 0) + classes.get("(withheld)", 0) >= blanks


def test_no_withheld_value_survives_into_either_output(
    tmp_path: pathlib.Path,
) -> None:
    for seed in range(6):
        table, document, text = _profile_of(
            tmp_path, _random_table(seed), f"t{seed}.csv"
        )
        serialized = profile.serialize(document)
        for value in table.columns[0][:15]:
            assert value not in serialized, "an identifier reached the profile"
            assert value not in text, "an identifier reached the summary"
        for value in table.columns[6][:15]:
            if value:
                assert value not in serialized
                assert value not in text


def test_every_column_of_every_random_table_gets_a_role(
    tmp_path: pathlib.Path,
) -> None:
    for seed in range(12):
        _table, document, _text = _profile_of(
            tmp_path, _random_table(seed), f"t{seed}.csv"
        )
        for column in document["columns"]:
            assert column["role"] in taxonomy.ROLES
            assert column["detection_evidence"]
