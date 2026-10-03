"""A description written before plan P4-D375 loads, generates and validates.

THE DEFECT (review of landing 3b.G1, item 1, HIGH). Plan P4-D375 kept the
readers of a withheld tail pair "so a description written before still
loads and says why a side is silent". None did. 668f276, the last pushed
tree whose producer withholds a pair, wrote neither the twelve keys stage 3b
reserves (plan P4-D364: seven on a `datetime` block, five on a
`time_of_day` block) nor the settings key landing T1 added
(`forced_twelve_hour_clocks`, plan P4-D370), and the strict key rule
refused such a document by its first missing key -- `generate` and
`validate` both stopped on "The description has no entry called
'forced_twelve_hour_clocks'", and with that key supplied, on
`hour_census` and `clock_census`. The helper that held the promise,
`kpi_shapes.written_before_p4d375`, starts from a CURRENT document and
clears only its distances, so it carried every newer key and could not
see it.

THE DOCUMENTS HERE ARE THE REAL ONES. `WRITTEN_BY_668F276` is, byte for
byte, the description 668f276's own `synthtwin profile` writes for the
table `three_columns()` builds -- 100 consecutive dates from 2020-01-01,
100 clocks at minute 13*i of the day, and the whole numbers 1 to 100 --
at the default floor of 11: `git archive 668f276 src`, then
`synthtwin profile three.csv` run on that source
(sha256 below, the file's own). Its date and number tails withhold both
distances, each with the remark 668f276 wrote. `written_by_fa00321()`
is the same document with the twelve reserves added empty, which is
byte for byte what fa00321 (3b.K merged, before T1) writes for that
table -- a description that carries the reserves and still lacks the
settings key -- and its digest is that file's, so it is not a current
document with fields cleared either.

WHAT IS HELD: each document loads; each absent key reads as the empty
value every producer since writes where nothing is published; the
withheld sides stay withheld and their remarks stay; `synthtwin
generate` writes a twin of it, whose report says why each withheld side
is silent in the remark the earlier producer wrote, and `synthtwin
validate` measures that twin, both with exit code 0, and nothing is
MISSED; and the relief is exactly the keys added since 668f276 -- any
other key absent is still refused, and a reserve present is still read
by its own reader.

Mutation: dropping the `_absent_read_as_empty` call in `_settings`
turns every loading test here red on `forced_twelve_hour_clocks`;
dropping it in `_column` turns 668f276's red on `hour_census` (the date
column is read first), and fa00321's, which carries the reserves, stays
green.
"""

from __future__ import annotations

import contextlib
import datetime
import hashlib
import io
import json

import pytest

import fixtures
from synthtwin import canonical, cli, contract, errors, validation

# -- the documents ---------------------------------------------------------

DIGEST_668F276 = "16903c66f0d1fb7c5179ab238907122401d41fcf39cd4b0b4db52e684af5f678"
DIGEST_FA00321 = "c1581e3ebc70f15866aab7e34da74634235697eaacba5863cc6f06a3d8537b56"

# THE KEYS ADDED SINCE 668f276, as the two later trees wrote them.
RESERVED_ON_DATES = (
    "day_of_month_census",
    "heavy_dates",
    "hour_census",
    "minute_census",
    "minute_heaps",
    "second_census",
    "second_heaps",
)
RESERVED_ON_CLOCKS = ("clock_census", "clock_codes", "clock_heaps", "clock_step", "minute_census")


def three_columns() -> str:
    """The table both documents describe: dates, clocks and whole numbers, 100 rows."""
    start = datetime.date(2020, 1, 1)
    lines = ["visit_day,visit_time,count_value"]
    for row in range(100):
        minute = 13 * row
        lines += [f"{(start + datetime.timedelta(days=row)).isoformat()},{(minute // 60) % 24:02d}:{minute % 60:02d},{row + 1}"]
    return "\n".join(lines) + "\n"


# THE DESCRIPTION 668f276 WRITES for `three_columns()`, byte for byte.
WRITTEN_BY_668F276 = r'''{
  "columns": [
    {
      "all_at_midnight": false,
      "date_field_widths": {},
      "date_percentiles": {
        "max": null,
        "min": null,
        "p01": null,
        "p05": null,
        "p10": null,
        "p25": "2020-01-25",
        "p50": "2020-02-19",
        "p75": "2020-03-15",
        "p90": null,
        "p95": null,
        "p99": null
      },
      "datetime_separators": {},
      "datetimes_read_at": "local",
      "detection_evidence": "100 of the 100 values are dates written as 2024-03-17",
      "format": "iso-date",
      "high_tail": {
        "boundary": "2020-03-29",
        "mean_distance": null,
        "rms_distance": null,
        "rows": 11,
        "values": null
      },
      "low_tail": {
        "boundary": "2020-01-12",
        "mean_distance": null,
        "rms_distance": null,
        "rows": 11,
        "values": null
      },
      "missing_by_class": {
        "(blank)": 0,
        "(date-sentinel)": 0,
        "(declared-missing)": 0,
        "(numeric-sentinel)": 0,
        "(text-code)": 0,
        "(withheld)": 0
      },
      "missing_by_source": {},
      "month_name_styles": {},
      "n_at_midnight": null,
      "n_contradictory": 0,
      "n_distinct": 100,
      "n_distinct_folded": 100,
      "n_missing": 0,
      "n_missing_blank": 0,
      "n_missing_withheld": 0,
      "n_not_numeric": 100,
      "n_numeric": 0,
      "n_out_of_range": 0,
      "n_present": 100,
      "n_sentinel_candidates_unpublished": 0,
      "n_unparsed": 0,
      "name": "visit_day",
      "position": 1,
      "quality_state": "ok",
      "quarter_marker_case": {},
      "remarks": [
        "the two distances of the values beyond this column's lower tail boundary are not published because together they would give every one of those values back",
        "the two distances of the values beyond this column's upper tail boundary are not published because together they would give every one of those values back"
      ],
      "resolution": "date",
      "resolution_mix": {
        "iso-date": 100
      },
      "role": "datetime",
      "sentinel_verdicts": [],
      "statistical_type": "datetime",
      "structural_role": "data",
      "subsecond_digits": 0,
      "tail_unit": "day",
      "time_precision": "date",
      "utc_offsets": {
        "(none)": 100
      },
      "weekday_census": [],
      "zulu_case": {}
    },
    {
      "clock_form": "hh-mm",
      "clock_percentiles": {
        "max": null,
        "min": null,
        "p01": null,
        "p05": null,
        "p10": null,
        "p25": "05:12",
        "p50": "10:37",
        "p75": "16:02",
        "p90": null,
        "p95": null,
        "p99": null
      },
      "detection_evidence": "100 value(s) are clock times written as hours and minutes, `09:30`, and 0 value(s) are not",
      "high_tail": {
        "boundary": "19:04",
        "mean_distance": 78.0,
        "rms_distance": 88.17028978062848,
        "rows": 11,
        "values": null
      },
      "low_tail": {
        "boundary": "02:23",
        "mean_distance": 78.0,
        "rms_distance": 88.17028978062848,
        "rows": 11,
        "values": null
      },
      "missing_by_class": {
        "(blank)": 0,
        "(date-sentinel)": 0,
        "(declared-missing)": 0,
        "(numeric-sentinel)": 0,
        "(text-code)": 0,
        "(withheld)": 0
      },
      "missing_by_source": {},
      "n_contradictory": 0,
      "n_distinct": 100,
      "n_distinct_folded": 100,
      "n_missing": 0,
      "n_missing_blank": 0,
      "n_missing_withheld": 0,
      "n_not_numeric": 100,
      "n_numeric": 0,
      "n_out_of_range": 0,
      "n_present": 100,
      "n_sentinel_candidates_unpublished": 0,
      "n_unparsed": 0,
      "name": "visit_time",
      "position": 2,
      "quality_state": "ok",
      "remarks": [
        "every value in this column is different. That is not treated as evidence of anything: the column is described as numbers, which keeps its distribution. If it is really a record number, run the command again with --identifier NAME, where NAME is this column's name, and its values will be left out of the profile altogether"
      ],
      "role": "time_of_day",
      "sentinel_verdicts": [],
      "statistical_type": "time_of_day",
      "structural_role": "data"
    },
    {
      "bin_groups": [
        {
          "count": 12,
          "first": 0,
          "last": 4
        },
        {
          "count": 12,
          "first": 5,
          "last": 9
        },
        {
          "count": 12,
          "first": 10,
          "last": 14
        },
        {
          "count": 11,
          "first": 15,
          "last": 19
        },
        {
          "count": 12,
          "first": 20,
          "last": 24
        },
        {
          "count": 17,
          "first": 25,
          "last": 31
        }
      ],
      "decimal_plus": {},
      "detection_evidence": "all 100 numeric values are whole and none is negative, so this column counts things",
      "empty_bins": [],
      "empty_edges": [],
      "field_widths": {
        "2": 100
      },
      "fraction_widths": {},
      "group_separator": "",
      "integer_valued": true,
      "kurtosis": 1.7997599759975997,
      "mean": 50.5,
      "missing_by_class": {
        "(blank)": 0,
        "(date-sentinel)": 0,
        "(declared-missing)": 0,
        "(numeric-sentinel)": 0,
        "(text-code)": 0,
        "(withheld)": 0
      },
      "missing_by_source": {},
      "mode": null,
      "mode_count": 0,
      "n_contradictory": 0,
      "n_distinct": 100,
      "n_distinct_folded": 100,
      "n_distinct_values": 100,
      "n_left_out_of_statistics": 0,
      "n_missing": 0,
      "n_missing_blank": 0,
      "n_missing_withheld": 0,
      "n_negative": 0,
      "n_negative_unrepresentable": 0,
      "n_not_numeric": 0,
      "n_numeric": 100,
      "n_out_of_range": 0,
      "n_present": 100,
      "n_rows": 100,
      "n_sentinel_candidates_unpublished": 0,
      "n_used_in_statistics": 100,
      "n_zero": 0,
      "name": "count_value",
      "negative_form": "minus",
      "negative_notations": {},
      "number_spellings": {},
      "numeric_share": 1.0,
      "numeric_styles": {
        "plain": 100
      },
      "pad_widths": {},
      "percentiles": {
        "max": null,
        "min": null,
        "p01": null,
        "p05": null,
        "p10": null,
        "p25": 25.75,
        "p50": 50.5,
        "p75": 75.25,
        "p90": null,
        "p95": null,
        "p99": null
      },
      "percentiles_between": {
        "p02": null,
        "p03": null,
        "p04": null,
        "p06": null,
        "p07": null,
        "p08": null,
        "p09": null,
        "p11": null,
        "p12": 12.88,
        "p13": 13.87,
        "p14": 14.86,
        "p15": 15.85,
        "p16": 16.84,
        "p17": 17.83,
        "p18": 18.82,
        "p19": 19.81,
        "p20": 20.8,
        "p21": 21.79,
        "p22": 22.78,
        "p23": 23.77,
        "p24": 24.76,
        "p26": 26.74,
        "p27": 27.73,
        "p28": 28.72,
        "p29": 29.71,
        "p30": 30.7,
        "p31": 31.69,
        "p32": 32.68,
        "p33": 33.67,
        "p34": 34.66,
        "p35": 35.65,
        "p36": 36.64,
        "p37": 37.63,
        "p38": 38.62,
        "p39": 39.61,
        "p40": 40.6,
        "p41": 41.59,
        "p42": 42.58,
        "p43": 43.57,
        "p44": 44.56,
        "p45": 45.55,
        "p46": 46.54,
        "p47": 47.53,
        "p48": 48.52,
        "p49": 49.51,
        "p51": 51.49,
        "p52": 52.48,
        "p53": 53.47,
        "p54": 54.46,
        "p55": 55.45,
        "p56": 56.44,
        "p57": 57.43,
        "p58": 58.42,
        "p59": 59.41,
        "p60": 60.4,
        "p61": 61.39,
        "p62": 62.38,
        "p63": 63.37,
        "p64": 64.36,
        "p65": 65.35,
        "p66": 66.34,
        "p67": 67.33,
        "p68": 68.32,
        "p69": 69.31,
        "p70": 70.3,
        "p71": 71.29,
        "p72": 72.28,
        "p73": 73.27,
        "p74": 74.26,
        "p76": 76.24,
        "p77": 77.23,
        "p78": 78.22,
        "p79": 79.21,
        "p80": 80.2,
        "p81": 81.19,
        "p82": 82.18,
        "p83": 83.17,
        "p84": 84.16,
        "p85": 85.15,
        "p86": 86.14,
        "p87": 87.13,
        "p88": 88.12,
        "p89": null,
        "p91": null,
        "p92": null,
        "p93": null,
        "p94": null,
        "p96": null,
        "p97": null,
        "p98": null
      },
      "position": 3,
      "quality_state": "ok",
      "remarks": [
        "every value in this column is different. That is not treated as evidence of anything: the column is described as numbers, which keeps its distribution. If it is really a record number, run the command again with --identifier NAME, where NAME is this column's name, and its values will be left out of the profile altogether",
        "the two distances of the values beyond this column's lower tail boundary are not published because together they would give every one of those values back",
        "the two distances of the values beyond this column's upper tail boundary are not published because together they would give every one of those values back"
      ],
      "role": "count",
      "sentinel_verdicts": [],
      "skew": 0.0,
      "statistical_type": "count",
      "std": 29.011491975882016,
      "std_unrepresentable": false,
      "structural_role": "data",
      "tails": {
        "high": {
          "mean_distance": null,
          "percent": 88,
          "rms_distance": null,
          "rows": 12,
          "values": []
        },
        "low": {
          "mean_distance": null,
          "percent": 12,
          "rms_distance": null,
          "rows": 12,
          "values": []
        }
      },
      "thousands_marks": {},
      "value_histogram": {},
      "wide_runs": "none"
    }
  ],
  "created_with": "0.1.0.dev0",
  "n_columns": 3,
  "n_rows": 100,
  "profile_version": 6,
  "publication_notes": [
    {
      "column": "",
      "note": "this description was made from a table of 100 rows, which is fewer than a thousand. Every count here is a count of ROWS over that population -- where your table holds several rows per person, a value only one person has is published with the number of their rows -- so each count narrows who a row could be further than the same count would in a large table. Nothing in this description is excused by the size: the same rules produced it, the smallest group size is the same number, and every obligation it states is the same obligation"
    },
    {
      "column": "visit_day",
      "note": "the days of the week this column's values fall on are not counted: its dates repeat too little for any date to hold 11 rows"
    }
  ],
  "relationships": {
    "deterministic": null,
    "grain": null,
    "hierarchy": null,
    "keys": null,
    "missing_data_process": null,
    "statistical": null,
    "temporal": null,
    "validation_targets": null
  },
  "settings": {
    "categorical_ceiling": 1000,
    "categorical_floor": 2,
    "categorical_share": 0.1,
    "day_first": false,
    "declaration_matching": "exact_number_when_it_reads_as_one_else_spelling",
    "declaration_publication": "settings_counts_only_columns_unchanged",
    "declared_missing_values": {
      "built_in_dates": [],
      "built_in_numbers": [],
      "built_in_texts": [],
      "n_declared": 0,
      "values_recorded": false
    },
    "forced_codes": [],
    "forced_decimal_commas": [],
    "forced_delimiter": "",
    "forced_identifiers": [],
    "forced_measurements": [],
    "forced_metadata_rows": 0,
    "identifier_minimum_rows": 20,
    "identifier_uniqueness": 0.95,
    "kept_values": {
      "built_in_dates": [],
      "built_in_numbers": [],
      "built_in_texts": [],
      "n_declared": 0,
      "values_recorded": false
    },
    "long_tail_minimum_level": 11,
    "minimum_parse_rate": 0.99,
    "near_threshold_slack": 1,
    "person_columns": [],
    "sentinel_minimum_share": 0.005,
    "sentinel_outlier_iqr_multiple": 4.0,
    "small_cell_floor": 11
  },
  "source": {
    "dialect": {
      "blank_lines": [],
      "blank_lines_spread": null,
      "byte_order_mark": false,
      "columns": [
        {
          "pad": null,
          "quoting": {
            "absent": "needed",
            "empty": "needed",
            "number": "needed",
            "text": "needed"
          },
          "sequence_start": null
        },
        {
          "pad": null,
          "quoting": {
            "absent": "needed",
            "empty": "needed",
            "number": "needed",
            "text": "needed"
          },
          "sequence_start": null
        },
        {
          "pad": null,
          "quoting": {
            "absent": "needed",
            "empty": "needed",
            "number": "needed",
            "text": "needed"
          },
          "sequence_start": null
        }
      ],
      "delimiter": ",",
      "empty_rows": {
        "interior": 0,
        "leading": 0,
        "trailing": 0
      },
      "end_of_file_mark": false,
      "escape": "doubled",
      "final_line_ending": true,
      "header_quoting": "needed",
      "header_rows": [],
      "header_rows_quoting": "needed",
      "initial_space": false,
      "line_endings": [
        {
          "ending": "lf",
          "lines": 101
        }
      ],
      "line_endings_spread": [],
      "preamble": [],
      "preamble_withheld": false,
      "row_order": {
        "collation": "text",
        "column": 1,
        "direction": "ascending"
      },
      "separator_line": false,
      "short_rows": false,
      "trailing_delimiter": {
        "header": false,
        "rows": false
      },
      "written_names": []
    },
    "encoding": "utf-8-sig",
    "header_by_convention": false,
    "header_evidence": "column 3 holds a number in every row below it, and its first-row value is not a number",
    "header_source": "file",
    "used_fallback_encoding": false,
    "workbook": null
  }
}
'''


def written_by_fa00321() -> str:
    """668f276's document with the twelve reserves added empty: fa00321's file for the table."""
    document = json.loads(WRITTEN_BY_668F276)
    for block in document["columns"]:
        if block["role"] == contract.ROLE_DATETIME:
            for key in RESERVED_ON_DATES:
                block[key] = []
        if block["role"] == contract.ROLE_CLOCK:
            for key in RESERVED_ON_CLOCKS:
                block[key] = None if key == "clock_step" else []
    return canonical.serialize(document)


def _digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _written(folder, text: str):
    """An earlier tree's description, written through `fixtures.write_profile`.

    The one place that decides a description's bytes
    (`tests/test_description_line_endings.py`) writes
    `canonical.serialize` of the parsed document, and the earlier
    producers wrote through that serializer too, so the file on disk is
    the embedded text byte for byte, which is asserted here: the loader
    is handed the earlier tree's own file and nothing rewritten.
    """
    path = fixtures.write_profile(folder, "three-profile.json", json.loads(text))
    assert path.read_bytes() == text.encode("utf-8")
    return path


def _run(arguments: "list[str]") -> "tuple[int, str]":
    said = io.StringIO()
    with contextlib.redirect_stdout(said), contextlib.redirect_stderr(said):
        code = cli.main(arguments)
    return code, said.getvalue()


EARLIER = {"668f276": WRITTEN_BY_668F276, "fa00321": written_by_fa00321()}


def test_the_documents_are_the_files_the_earlier_trees_wrote() -> None:
    """Each document here is its tree's own file, by digest, and the table is the one it describes."""
    assert _digest(WRITTEN_BY_668F276) == DIGEST_668F276
    assert _digest(EARLIER["fa00321"]) == DIGEST_FA00321
    document = json.loads(WRITTEN_BY_668F276)
    assert "forced_twelve_hour_clocks" not in document["settings"]
    for block in document["columns"]:
        for key in RESERVED_ON_DATES + RESERVED_ON_CLOCKS:
            assert key not in block, (block["name"], key)
    assert [block["role"] for block in document["columns"]] == [
        contract.ROLE_DATETIME, contract.ROLE_CLOCK, contract.ROLE_COUNT,
    ]
    assert document["columns"][0]["low_tail"]["mean_distance"] is None
    assert document["columns"][2]["tails"]["high"]["rms_distance"] is None


def test_the_relief_is_exactly_the_keys_added_since() -> None:
    """The keys read as empty are the keys the current tuples hold and 668f276's blocks lack, no more."""
    document = json.loads(WRITTEN_BY_668F276)
    assert tuple(sorted(set(contract.SETTINGS_KEYS) - set(document["settings"]))) == tuple(
        sorted(contract.SETTINGS_READ_AS_EMPTY_WHEN_ABSENT)
    )
    dates, clocks = document["columns"][0], document["columns"][1]
    assert sorted(set(contract.DATETIME_KEYS) - set(dates)) == sorted(contract.DATETIME_READ_AS_EMPTY_WHEN_ABSENT)
    assert sorted(set(contract.CLOCK_KEYS) - set(clocks)) == sorted(contract.CLOCK_READ_AS_EMPTY_WHEN_ABSENT)


@pytest.mark.parametrize("tree", sorted(EARLIER))
def test_an_earlier_description_loads_with_its_absent_keys_empty(tmp_path, tree) -> None:
    """The document loads; every key it lacks reads empty; its withheld sides stay withheld."""
    path = _written(tmp_path, EARLIER[tree])
    loaded = contract.load_profile(str(path))
    assert loaded.settings.forced_twelve_hour_clocks == ()
    dates, clocks, counts = loaded.columns
    for key in RESERVED_ON_DATES:
        assert getattr(dates.facts, key) == (), key
    for key in RESERVED_ON_CLOCKS:
        assert getattr(clocks.facts, key) == (None if key == "clock_step" else ()), key
    for side in (dates.facts.low_tail, dates.facts.high_tail, counts.facts.tails.low, counts.facts.tails.high):
        assert (side.mean_distance, side.rms_distance) == (None, None)
    assert clocks.facts.low_tail.mean_distance == 78.0
    withheld = [remark for remark in dates.remarks if "are not published because" in remark]
    assert len(withheld) == 2, dates.remarks


@pytest.mark.parametrize("tree", sorted(EARLIER))
def test_an_earlier_description_generates_and_validates(tmp_path, tree) -> None:
    """`synthtwin generate` and `synthtwin validate` both finish on it, and nothing is MISSED."""
    path = _written(tmp_path, EARLIER[tree])
    code, said = _run(["generate", str(path), "--seed", "0", "--out-dir", str(tmp_path), "--replace"])
    assert code == 0, said
    twin = tmp_path / "three-twin.csv"
    assert twin.exists()
    # ...and the twin's report says why each withheld side is silent, in
    # the remark the earlier producer wrote: the kept reader is reached.
    report = (tmp_path / "three-twin-report.txt").read_text(encoding="utf-8")
    for edge in ("lower", "upper"):
        note = f"the two distances of the values beyond this column's {edge} tail boundary are not published"
        assert report.count(note) == 2, (edge, report)
    code, said = _run(["validate", str(path), "--twin", str(twin), "--out-dir", str(tmp_path), "--replace"])
    assert code == 0, said
    outcome = validation.measure(contract.load_profile(str(path)), str(twin))
    missed = [f"{check.column}:{check.subcheck}" for check in outcome.checks if check.verdict == validation.MISSED]
    assert missed == []
    # The withheld sides are not checked as though they published a pair.
    asked = {check.subcheck for check in outcome.checks if check.column == "visit_day"}
    assert "tails.low.mean_distance" not in asked and "tails.low.boundary" in asked


def test_the_table_itself_meets_the_earlier_description(tmp_path) -> None:
    """The validator measures the real table against 668f276's description, and it holds."""
    path = _written(tmp_path, WRITTEN_BY_668F276)
    table = fixtures.write(tmp_path, "three.csv", three_columns())
    outcome = validation.measure(contract.load_profile(str(path)), str(table))
    assert [check for check in outcome.checks if check.verdict == validation.MISSED] == []


@pytest.mark.parametrize(
    "where, key",
    [("settings", "small_cell_floor"), (0, "weekday_census"), (1, "clock_form"), (0, "low_tail")],
)
def test_any_other_absent_key_is_still_refused(tmp_path, where, key) -> None:
    """Only the keys added since 668f276 are relieved; every other absence is refused by name."""
    document = json.loads(WRITTEN_BY_668F276)
    block = document["settings"] if where == "settings" else document["columns"][where]
    del block[key]
    path = fixtures.write_profile(tmp_path, "three-profile.json", document)
    with pytest.raises(errors.ProfileError, match=f"no entry called '{key}'"):
        contract.load_profile(str(path))


def test_a_reserve_that_is_present_is_still_read_by_its_reader(tmp_path) -> None:
    """A reserve present and not empty is refused as before: absent is relieved, present is not."""
    document = json.loads(EARLIER["fa00321"])
    document["columns"][0]["hour_census"] = [{"count": 11, "first": 0, "last": 0}]
    path = fixtures.write_profile(tmp_path, "three-profile.json", document)
    with pytest.raises(errors.ProfileError, match="hour_census"):
        contract.load_profile(str(path))
