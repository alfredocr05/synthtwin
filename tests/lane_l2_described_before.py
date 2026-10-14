"""A description written before lane L2, frozen as 6a248e7 wrote it (plan P4-D392).

`NARROW_BESIDE_WORDS` is what `synthtwin profile` on 6a248e7 wrote for the
200-row column `tests/test_lane_l2_spaced_meridiem.py` builds
(`_narrow_beside_words`): clock times written with U+202F before their
marker, one cell in 33 a rare text. Before L2 such a cell had no form, so
the description publishes none (`shape_forms` is empty). It is held here to
show that a description written before L2 still loads, generates the twin
6a248e7 generated and validates against its source. No value of any table
is in it: it is free text, and free text publishes no value.
"""

NARROW_BESIDE_WORDS = r"""{
  "columns": [
    {
      "detection_evidence": "none of the 200 values is written as a number, none of them reads as a date in any form synthtwin knows, and there are 184 different values where a set of categories may have at most 20 in a table of 200 rows",
      "length": {
        "max": 18,
        "mean": 7.495,
        "min": 7,
        "p50": 7.0
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
      "n_all_digits": 0,
      "n_code_alphabet": 0,
      "n_contradictory": 0,
      "n_distinct": 184,
      "n_distinct_by_occurrences": {
        "1": 169,
        "2": 14,
        "3": 1
      },
      "n_distinct_folded": 184,
      "n_missing": 0,
      "n_missing_blank": 0,
      "n_missing_withheld": 0,
      "n_not_numeric": 200,
      "n_numeric": 0,
      "n_out_of_range": 0,
      "n_present": 200,
      "n_sentinel_candidates_unpublished": 0,
      "name": "seen_at",
      "position": 1,
      "quality_state": "ok",
      "remarks": [
        "synthtwin could not settle what this column holds, so none of its values is published. Here is why: none of the 200 values is written as a number and none of them reads as a date in any form synthtwin knows; a column is described as numbers, or as dates, only when at least 198 of them read that way. It holds 184 different values, where a set of categories may hold at most 20. Describing it from the part that does read would publish an average, a spread and points along a range that the rest of the column contradicts, so synthtwin describes it as free text and publishes no value of it at all. If these are measurements written with a currency sign, a per-cent sign, a unit such as mg, or a clock time, write them as plain numbers -- one column for the number, and the unit in the column name -- and run the command again. 16 of its values are numbers wearing one shared piece of text, which is the reading that came closest"
      ],
      "role": "free_text",
      "sentinel_verdicts": [],
      "shape_forms": {},
      "statistical_type": "text",
      "structural_role": "data",
      "words": {
        "max": 3,
        "mean": 2.03,
        "min": 2
      }
    }
  ],
  "created_with": "0.1.0.dev0",
  "n_columns": 1,
  "n_rows": 200,
  "profile_version": 6,
  "publication_notes": [
    {
      "column": "",
      "note": "this description was made from a table of 200 rows, which is fewer than a thousand. Every count here is a count of ROWS over that population -- where your table holds several rows per person, a value only one person has is published with the number of their rows -- so each count narrows who a row could be further than the same count would in a large table. Nothing in this description is excused by the size: the same rules produced it, the smallest group size is the same number, and every obligation it states is the same obligation"
    },
    {
      "column": "seen_at",
      "note": "this column is described as free text, so none of its values are published: only how long they are, how many words they hold, how often they repeat, and -- where enough of them were written the same way -- the shape of that writing, which carries no letter and no figure of any value"
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
    "century_windows": [],
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
    "forced_date_columns": [],
    "forced_date_counts": [],
    "forced_decimal_commas": [],
    "forced_delimiter": "",
    "forced_identifiers": [],
    "forced_measurements": [],
    "forced_metadata_rows": 0,
    "forced_twelve_hour_clocks": [],
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
          "lines": 201
        }
      ],
      "line_endings_spread": [],
      "preamble": [],
      "preamble_withheld": false,
      "row_order": null,
      "separator_line": false,
      "short_rows": false,
      "trailing_delimiter": {
        "header": false,
        "rows": false
      },
      "written_names": []
    },
    "encoding": "utf-8-sig",
    "header_by_convention": true,
    "header_evidence": "The first row was read as the column names by convention, not by evidence: a CSV file is normally written with its column names first, and nothing in this file contradicted that -- no value in the first row belongs among the values of the column below it. synthtwin did not check that those values ARE names, because no such check exists. If that row is really the first record, run the command again with --first-row data: the columns are then named column_1, column_2, and so on and every record is kept.",
    "header_source": "file",
    "used_fallback_encoding": false,
    "workbook": null
  }
}
"""

NARROW_BESIDE_WORDS_SHA256 = "7881f59b5cd805c5c1e75bfe4f7734523b917945d02c2d8bec9ef0c9cf95e3fa"
NARROW_BESIDE_WORDS_TWIN_SHA256 = "b91c5993bdad4b70949431168d093343dc375fde32f556606fe051dcac627017"
