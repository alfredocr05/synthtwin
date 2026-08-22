"""The profile document: shape, canonical bytes, and what it withholds.

Plan P1-D5 (the contract), P1-D6 (automatic suppression), P1-D11 and
D12 (canonical, byte-stable serialization).
"""

import dataclasses
import hashlib
import json
import pathlib

import pytest

import fixtures
from synthtwin import errors, profile, reading, taxonomy

SETTINGS = taxonomy.Settings()


def _document(tmp_path: pathlib.Path, text: str) -> dict:
    table = reading.read_table(str(fixtures.write(tmp_path, "t.csv", text)))
    return profile.build_document(table, SETTINGS, [])


def _demo_document(tmp_path: pathlib.Path) -> dict:
    return _document(tmp_path, fixtures.every_role_table())


# -- the contract ----------------------------------------------------


def test_top_level_fields_are_exactly_the_contract(
    tmp_path: pathlib.Path,
) -> None:
    document = _demo_document(tmp_path)
    assert sorted(document) == [
        "columns",
        "created_with",
        "n_columns",
        "n_rows",
        "profile_version",
        "publication_notes",
        "relationships",
        "settings",
        "source",
    ]
    assert document["profile_version"] == profile.PROFILE_VERSION


def test_columns_keep_the_order_they_had_in_the_file(
    tmp_path: pathlib.Path,
) -> None:
    document = _demo_document(tmp_path)
    positions = [column["position"] for column in document["columns"]]
    assert positions == list(range(1, len(positions) + 1))
    names = [column["name"] for column in document["columns"]]
    assert names[0] == "record_code"
    assert names[-1] == "note"


def test_every_column_carries_its_evidence_and_counts(
    tmp_path: pathlib.Path,
) -> None:
    document = _demo_document(tmp_path)
    for column in document["columns"]:
        assert column["detection_evidence"]
        assert column["role"] in taxonomy.ROLES
        assert column["n_present"] + column["n_missing"] == document["n_rows"]


def test_the_settings_that_produced_the_roles_travel_with_them(
    tmp_path: pathlib.Path,
) -> None:
    # A profile whose rules are not recorded cannot be checked later.
    document = _demo_document(tmp_path)
    recorded = document["settings"]
    declared = {field.name for field in dataclasses.fields(taxonomy.Settings)}
    assert declared <= set(recorded), (
        "every setting must be written into the profile; a setting added "
        "to Settings and forgotten in the settings block would leave "
        "profiles that cannot be reproduced"
    )
    assert recorded["small_cell_floor"] == SETTINGS.small_cell_floor


def test_notes_and_columns_cannot_disagree(tmp_path: pathlib.Path) -> None:
    document = _demo_document(tmp_path)
    named = {note["column"] for note in document["publication_notes"]}
    known = {column["name"] for column in document["columns"]}
    assert named <= known


# -- canonical bytes --------------------------------------------------


def test_serialization_is_canonical(tmp_path: pathlib.Path) -> None:
    text = profile.serialize(_demo_document(tmp_path))
    assert text.endswith("\n")
    assert "\r" not in text
    parsed = json.loads(text)
    assert profile.serialize(parsed) == text, "serializing is idempotent"
    keys = [line for line in text.splitlines() if line.startswith('  "')]
    assert keys == sorted(keys), "top-level keys are written in order"


def test_the_same_table_always_produces_the_same_bytes(
    tmp_path: pathlib.Path,
) -> None:
    first = profile.serialize(_demo_document(tmp_path))
    second = profile.serialize(_demo_document(tmp_path))
    assert first == second


def test_nothing_that_varies_between_runs_is_written(
    tmp_path: pathlib.Path,
) -> None:
    # No timestamp, no path, no machine name: that is what makes the
    # hash below mean something.
    text = profile.serialize(_demo_document(tmp_path))
    assert str(tmp_path) not in text
    assert "t.csv" not in text
    for word in ("timestamp", "created_at", "generated_at", "hostname"):
        assert word not in text


# Recorded from the fixed fixture in fixtures.py. This hash is a CHANGE
# DETECTOR, not an oracle: review round 1 correctly observed that a hash
# transcribed from the implementation cannot check it. The oracle is
# tests/test_numeric_reference.py, whose values are computed by exact
# rational arithmetic in a script that imports none of this code.
#
# Re-recorded once for review item P1-R6-F7 and P1-R6-F9. What moved is
# the `settings` block and nothing else: four thresholds that named
# deleted rules are gone (`numeric_majority`, `categorical_repetition`,
# `categorical_numeric_ceiling`, `code_minimum_width`), three that name
# the ratified ones are new (`categorical_share`, `categorical_floor`,
# `declaration_matching`), and the two pooled-beyond-the-cap counts left
# the level block with the cap that could no longer fill them. Every
# column of this fixture keeps the role, the counts and the statistics
# it had before, which is what the table above is checked for.
#
# Re-recorded a second time for review item P1-R8-F4. What moved here is
# ONE number and nothing else: `profile_version`, from 2 to 3, because a
# declared-identifier column now carries `n_distinct_by_occurrences`.
# That was checked rather than assumed -- writing 2 back into this
# document and serializing it again reproduces the previous digest
# character for character. It moves for a change no column of THIS
# fixture shows, because the fixture declares no identifier: every role
# it does exercise keeps the same bytes. The field itself is pinned in
# tests/test_p1r8f4_repetition_multiset.py, on a document that declares
# one.
#
# Re-recorded a third time for profile version 4 (plan P2-D3 to P2-D5
# and owner decisions 9, 10 and 11). The difference was read line by
# line against the previous document rather than accepted from the
# digest, and it is exactly the five additions, the version number and
# one sentence:
#
# * `profile_version` 3 -> 4;
# * three axes on every one of the ten column blocks --
#   `statistical_type`, `quality_state`, `structural_role`;
# * `n_distinct_by_occurrences` on the two free-text columns, which
#   holds `{"1": 240}` and `{"1": 80}`: every value of each is
#   different, which `n_distinct` already said;
# * `variants` and `variants_withheld` on each of the seven published
#   labels -- four in `region`, two in `answer`, one in `batch`; the
#   count is written out per column because "seven" alone is a number a
#   later reader cannot check, and the first recording of this comment
#   said eight. This fixture writes every label one way, so each variant
#   mapping names that one spelling at the label's own count and each
#   withheld mapping is empty -- the fold changes nothing here, which is
#   why the labels themselves are unmoved. `region`'s fifth label is
#   below the floor, so it is withheld and carries no variants at all;
# * `numeric_styles` on the three numeric columns: `{"plain": 229}`,
#   `{"plain": 227}` and `{"decimal": 240}`, the last being the measured
#   column, every cell of which is written with a decimal point;
# * the top-level `relationships` block, eight names and eight nulls;
# * the free-text publication note now also says "and how often they
#   repeat", because the block it describes now carries that.
#
# No count, no statistic, no label and no role of any column moved.
#
# AND IT MOVED AGAIN AT CONTRACT VERSION 5 (plan amendments A-P3-27 and
# A-P3-28). Four things changed in these bytes and no fifth:
#
# * `profile_version` reads 5;
# * every column block carries `n_missing_blank` and
#   `n_missing_withheld`, which are the two counts version 4 kept inside
#   `missing_by_source` under this package's own two words;
# * `missing_by_source` therefore holds one key space -- spellings the
#   table wrote -- and no `(blank)` or `(withheld)` key;
# * both declaration records carry `built_in_texts` and
#   `built_in_numbers`, empty here because this run declares nothing.
#
# No count, no statistic, no label, no role and no spelling of any
# column moved, and no cell of any twin moved with them: the twin's own
# golden is unchanged.
#
# RE-RECORDED 2026-08-21, and the cause is one change with one reach:
# the demonstration table's free-text column stopped being a template.
# It held `observation 0 written out in several plain words`,
# `observation 1 ...` and so on -- which the affixed-number rule of
# this phase reads as a number wearing shared text, because that is
# what those strings are. A fixture meant to stand for text NO rule
# reads had to become text no rule reads, so it is prose that varies
# at both ends and holds no digit.
#
# RE-RECORDED AGAIN THROUGH CODEX ROUNDS 2 AND 3 (2026-08-21), and the
# cause is NOT the one above: that free-text change is a round-1 record
# and the column has not moved since. What moved these digests is the
# `dose` column and the census beside it. `dose` was added to the
# shared table so the affixed role is walked by every battery, its
# spread was widened so a twin can carry its distinctness, and its
# cores were given a decimal point so the fraction-width census is
# exercised on THIS role rather than only on the plain numeric ones.
# The census itself is new in that range and publishes two more
# obligations on `dose` -- `widths.published.1` and
# `widths.published.2` -- so the quality report carries MORE than it
# did, which is the direction a re-recording must move in.
#
# All four digests moved together, which is what a change to the
# TABLE looks like: a different column of values makes a different
# description, a different twin, a different report and a different
# quality report. A change to the generator alone would have moved the
# last three and left the first.
GOLDEN_SHA256 = (
    "4d72d563f4bb4216766fce81bf67bcf5a3023cc88dd9ee6d138a9c88852616fa"
)


def test_golden_hash_of_the_demonstration_profile(
    tmp_path: pathlib.Path,
) -> None:
    """Pin the bytes of a fixed table's profile (plan D12).

    This hash is a change detector, not an oracle for the statistics
    themselves -- those are checked in test_numeric_reference.py against
    values computed by exact rational arithmetic outside this package.
    Its job is to turn any difference
    between platforms, interpreter versions or library versions into a
    visible failure instead of a silently different twin. The version
    string is normalized out, because the installed version is an input
    to the profile by design (D12) and would otherwise make every
    version bump look like a byte divergence.
    """
    document = _demo_document(tmp_path)
    document["created_with"] = "(version normalized for the golden test)"
    text = profile.serialize(document)
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    assert digest == GOLDEN_SHA256, (
        "the profile of the fixed demonstration table changed. If this "
        "was intended, update GOLDEN_SHA256; if it appeared only on one "
        "platform, it is a determinism defect and is release-blocking "
        f"(plan D12). New digest: {digest}"
    )


def test_published_numbers_are_exact_not_rounded_to_a_fixed_width(
    tmp_path: pathlib.Path,
) -> None:
    # Revision 0 rounded every number to twelve significant digits. On
    # values around 1e15 that published a range of zero beside a spread
    # of three (review finding P1-R1-F6). Numbers now reach the file
    # exactly as computed.
    text = profile.serialize(_demo_document(tmp_path))
    assert "1e+15" not in text
    values = [str(1000000000000000 + step) for step in range(10)]
    table = reading.read_table(
        str(fixtures.write(tmp_path, "big.csv", fixtures.single_column_table("v", values)))
    )
    document = profile.build_document(table, SETTINGS, [])
    ladder = document["columns"][0]["percentiles"]
    assert ladder["min"] == 1000000000000000.0
    assert ladder["max"] == 1000000000000009.0


def test_no_not_a_number_can_reach_the_file(tmp_path: pathlib.Path) -> None:
    # json.dumps would happily write NaN, which is not valid JSON and
    # which no other tool would read back.
    text = profile.serialize(_demo_document(tmp_path))
    assert "NaN" not in text
    assert "Infinity" not in text


# -- what the profile withholds ---------------------------------------


def test_no_identifier_or_free_text_value_appears_anywhere(
    tmp_path: pathlib.Path,
) -> None:
    table = reading.read_table(
        str(fixtures.write(tmp_path, "t.csv", fixtures.every_role_table()))
    )
    text = profile.serialize(profile.build_document(table, SETTINGS, []))
    identifiers = table.columns[0]
    comments = [value for value in table.columns[7] if value]
    for value in identifiers[:20]:
        assert value not in text, f"identifier {value!r} leaked into the profile"
    for value in comments[:20]:
        assert value not in text, "free text leaked into the profile"


def test_a_label_below_the_floor_never_appears(tmp_path: pathlib.Path) -> None:
    document = _demo_document(tmp_path)
    text = profile.serialize(document)
    region = next(
        c for c in document["columns"] if c["name"] == "region"
    )
    assert region["suppressed_levels"] == 1
    assert "outlying" not in text, (
        "a label shared by fewer rows than the floor must not appear, in "
        "any field, including the evidence sentences"
    )


def test_raising_the_floor_withholds_more(tmp_path: pathlib.Path) -> None:
    table = reading.read_table(
        str(fixtures.write(tmp_path, "t.csv", fixtures.every_role_table()))
    )
    strict = taxonomy.Settings(small_cell_floor=1000)
    text = profile.serialize(profile.build_document(table, strict, []))
    assert "north" not in text
    assert "yes" not in text


def test_a_forced_identifier_column_publishes_nothing(
    tmp_path: pathlib.Path,
) -> None:
    table = reading.read_table(
        str(fixtures.write(tmp_path, "t.csv", fixtures.every_role_table()))
    )
    document = profile.build_document(table, SETTINGS, ["amount"])
    amount = next(
        c for c in document["columns"] if c["name"] == "amount"
    )
    assert amount["role"] == taxonomy.ROLE_IDENTIFIER
    assert "percentiles" not in amount
    assert document["settings"]["forced_identifiers"] == ["amount"]


# -- writing the files ------------------------------------------------


def test_files_are_written_beside_the_table_by_default(
    tmp_path: pathlib.Path,
) -> None:
    table_path = fixtures.write(tmp_path, "readings.csv", "a,b\n1,2\n3,4\n")
    profile_path, summary_path = profile.default_output_paths(table_path, None)
    assert profile_path == tmp_path / "readings-profile.json"
    assert summary_path == tmp_path / "readings-profile.txt"


def test_an_output_folder_that_does_not_exist_is_refused(
    tmp_path: pathlib.Path,
) -> None:
    table_path = fixtures.write(tmp_path, "readings.csv", "a,b\n1,2\n")
    with pytest.raises(errors.ProfileError) as caught:
        profile.default_output_paths(table_path, str(tmp_path / "nowhere"))
    assert "does not exist" in f"{caught.value}"


def test_written_files_use_newline_endings_on_every_platform(
    tmp_path: pathlib.Path,
) -> None:
    target = tmp_path / "out.txt"
    profile.write_text_file(target, "one\ntwo\n")
    assert target.read_bytes() == b"one\ntwo\n"


def test_writing_where_writing_is_impossible_says_so(
    tmp_path: pathlib.Path,
) -> None:
    with pytest.raises(errors.ProfileError) as caught:
        profile.write_text_file(tmp_path / "no-such-folder" / "x.txt", "x")
    assert "could not be written" in f"{caught.value}"
