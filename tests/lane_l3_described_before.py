"""Descriptions written before lane L3, frozen as 7d27335 wrote them (plan P4-D393).

Before L3 a cell holding the space between a stamp's date and its clock --
`2024-01-05 9:15 AM`, `1/5/2024 09:15` -- had no form, nor had a stamp
longer than 24 characters, so each description below publishes no form
for its stamps, and every level whose label is such a stamp carries
`shape_form_cells` 0 whatever its named spellings wear. Each is held here
to show that a description written before L3 still loads, generates the
twin 7d27335 generated and validates against its source. They are what
`synthtwin profile` on 7d27335 wrote for the tables `stamp_tables` builds,
at a floor of eleven: free text beside rare words, a set of labels and a
column declared codes. Free text publishes no value; the labels and the
codes publish the stamps of their commonest levels, which are made up
here and are no one's.
"""

from __future__ import annotations

import random

NARROW = " "


def _stamp(draw: random.Random, spelling: str) -> str:
    """One made-up stamp in one of the spellings the tables use."""
    month = draw.randrange(1, 13)
    day = draw.randrange(1, 29)
    hour = draw.randrange(1, 13)
    minute = draw.randrange(60)
    word = ("AM", "PM")[draw.randrange(2)]
    if spelling == "iso-space-am":
        return f"2024-{month:02d}-{day:02d} {hour}:{minute:02d} {word}"
    if spelling == "us-narrow":
        return f"{month}/{day}/2024 {hour}:{minute:02d}{NARROW}{word}"
    if spelling == "dmy-seconds":
        return f"{day:02d}/{month:02d}/2024 {hour + 9:02d}:{minute:02d}:{draw.randrange(60):02d}"
    return f"2024-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:{draw.randrange(60):02d}.{draw.randrange(10 ** 6):06d}"


def stamp_tables() -> "dict[str, list[str]]":
    """The cells of each frozen description's column, by name."""
    tables: "dict[str, list[str]]" = {}
    draw = random.Random(393)
    free: "list[str]" = []
    for row in range(330):
        if row % 33 == 7:
            free += [("pending", "unknown")[row % 2]]
            continue
        free += [_stamp(draw, ("iso-space-am", "us-narrow", "dmy-seconds", "iso-fraction")[row % 4])]
    tables["free"] = free
    draw = random.Random(394)
    pool = [_stamp(draw, ("iso-space-am", "us-narrow")[number % 2]) for number in range(40)]
    labels: "list[str]" = []
    for row in range(600):
        if row % 33 == 7:
            labels += [("pending", "unknown")[row % 2]]
            continue
        labels += [pool[min(int(draw.paretovariate(1.0)) - 1, 39)]]
    tables["labels"] = labels
    draw = random.Random(395)
    codes: "list[str]" = []
    for row in range(400):
        if row % 33 == 7:
            codes += ["unknown"]
            continue
        codes += [_stamp(draw, ("dmy-seconds", "iso-fraction")[row % 2]) if row % 5 else "2024-01-05 9:15 AM"]
    tables["codes"] = codes
    return tables


# Filled in by the lane's scratch tool from 7d27335's own output: each
# entry is (the description's text, its sha256, its twin's sha256 at seed
# 0, whether the column is declared codes).

DESCRIBED = {
    "free": (
        r"""{
  "columns": [
    {
      "detection_evidence": "none of the 330 values is written as a number, 80 read as dates written as 17/03/2024 14:05 (day first), and there are 322 different values where a set of categories may have at most 33 in a table of 330 rows",
      "length": {
        "max": 26,
        "mean": 19.669696969696968,
        "min": 7,
        "p50": 19.0
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
      "n_distinct": 322,
      "n_distinct_by_occurrences": {
        "1": 320,
        "5": 2
      },
      "n_distinct_folded": 322,
      "n_missing": 0,
      "n_missing_blank": 0,
      "n_missing_withheld": 0,
      "n_not_numeric": 330,
      "n_numeric": 0,
      "n_out_of_range": 0,
      "n_present": 330,
      "n_sentinel_candidates_unpublished": 0,
      "name": "seen_at",
      "position": 1,
      "quality_state": "ok",
      "remarks": [
        "synthtwin could not settle what this column holds, so none of its values is published. Here is why: none of the 330 values is written as a number and 80 read as dates written as 17/03/2024 14:05 (day first); a column is described as numbers, or as dates, only when at least 327 of them read that way. It holds 322 different values, where a set of categories may hold at most 33. Describing it from the part that does read would publish an average, a spread and points along a range that the rest of the column contradicts, so synthtwin describes it as free text and publishes no value of it at all. If these are measurements written with a currency sign, a per-cent sign, a unit such as mg, or a clock time, write them as plain numbers -- one column for the number, and the unit in the column name -- and run the command again. Fewer than 11 of its values are numbers wearing one shared piece of text, which is the reading that came closest",
        "nearly every value in this column is different, some are shared with another row, and none of the forms synthtwin can read fits them. synthtwin did NOT assume they are record numbers: it cannot tell from the values alone whether these are record numbers or measurements written in a form it does not read yet, and a wrong guess would throw away the whole distribution. Nothing from this column is published either way -- no value of it, and no distribution. If these ARE record numbers, run the command again with --identifier NAME, where NAME is this column's name, and the profile will say so. If they are measurements written with a currency sign, a per-cent sign, a unit such as mg, or a clock time, write them as plain numbers -- one column for the number, and the unit in the column name -- and their distribution will be described. Do not use --identifier on a measurement: it withholds the column entirely"
      ],
      "role": "free_text",
      "sentinel_verdicts": [],
      "shape_forms": {},
      "statistical_type": "text",
      "structural_role": "data",
      "words": {
        "max": 3,
        "mean": 2.2181818181818183,
        "min": 1
      }
    }
  ],
  "created_with": "0.1.0.dev0",
  "n_columns": 1,
  "n_rows": 330,
  "profile_version": 6,
  "publication_notes": [
    {
      "column": "",
      "note": "this description was made from a table of 330 rows, which is fewer than a thousand. Every count here is a count of ROWS over that population -- where your table holds several rows per person, a value only one person has is published with the number of their rows -- so each count narrows who a row could be further than the same count would in a large table. Nothing in this description is excused by the size: the same rules produced it, the smallest group size is the same number, and every obligation it states is the same obligation"
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
          "lines": 331
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
""",
        "d167ca8344eca4d811fd7ea91f3774040bf8c0d9607af8cc4ddb39234715e013",
        "b78d5d88d2ecd66bfa60d6086e0fae20742a2869d348608639a628dcb0e34e37",
        False,
    ),
    "labels": (
        r"""{
  "columns": [
    {
      "detection_evidence": "there are 29 different values, which is within the 60 a set of categories may have in a table of 600 rows, so this column is a set of categories",
      "level_ceiling": 60,
      "levels": [
        {
          "count": 282,
          "label": "2024-04-08 6:44 am",
          "shape_form_cells": 0,
          "variants": {
            "2024-04-08 6:44 AM": 282
          },
          "variants_withheld": {}
        },
        {
          "count": 94,
          "label": "8/3/2024 6:23 am",
          "shape_form_cells": 0,
          "variants": {
            "8/3/2024 6:23 AM": 94
          },
          "variants_withheld": {}
        },
        {
          "count": 48,
          "label": "2024-03-21 12:25 am",
          "shape_form_cells": 0,
          "variants": {
            "2024-03-21 12:25 AM": 48
          },
          "variants_withheld": {}
        },
        {
          "count": 43,
          "label": "12/28/2024 8:26 am",
          "shape_form_cells": 0,
          "variants": {
            "12/28/2024 8:26 AM": 43
          },
          "variants_withheld": {}
        },
        {
          "count": 20,
          "label": "2024-08-24 9:23 am",
          "shape_form_cells": 0,
          "variants": {
            "2024-08-24 9:23 AM": 20
          },
          "variants_withheld": {}
        },
        {
          "count": 17,
          "label": "3/3/2024 3:36 am",
          "shape_form_cells": 0,
          "variants": {
            "3/3/2024 3:36 AM": 17
          },
          "variants_withheld": {}
        },
        {
          "count": 11,
          "label": "2/8/2024 10:03 am",
          "shape_form_cells": 0,
          "variants": {
            "2/8/2024 10:03 AM": 11
          },
          "variants_withheld": {}
        }
      ],
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
      "n_distinct": 29,
      "n_distinct_folded": 29,
      "n_missing": 0,
      "n_missing_blank": 0,
      "n_missing_withheld": 0,
      "n_not_numeric": 600,
      "n_numeric": 0,
      "n_out_of_range": 0,
      "n_present": 600,
      "n_sentinel_candidates_unpublished": 0,
      "name": "seen_at",
      "position": 1,
      "quality_state": "ok",
      "remarks": [],
      "role": "categorical",
      "sentinel_verdicts": [],
      "shape_forms": {},
      "statistical_type": "categorical",
      "structural_role": "data",
      "suppressed_levels": 22,
      "suppressed_numbers": {
        "mean": null,
        "n_cells": 0
      },
      "suppressed_rows": 85
    }
  ],
  "created_with": "0.1.0.dev0",
  "n_columns": 1,
  "n_rows": 600,
  "profile_version": 6,
  "publication_notes": [
    {
      "column": "",
      "note": "this description was made from a table of 600 rows, which is fewer than a thousand. Every count here is a count of ROWS over that population -- where your table holds several rows per person, a value only one person has is published with the number of their rows -- so each count narrows who a row could be further than the same count would in a large table. Nothing in this description is excused by the size: the same rules produced it, the smallest group size is the same number, and every obligation it states is the same obligation"
    },
    {
      "column": "seen_at",
      "note": "22 value(s) of this column are each shared by fewer than 11 rows, so they are counted together instead of being published (85 rows in total)"
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
          "lines": 601
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
""",
        "73092fdd0fca656c3da542299eef64236e56e58a4d222407b9660e449e1f3c0b",
        "a9a811ea7446295bf2c582a027813b29885f7617ac2596180271d5284b196e97",
        False,
    ),
    "codes": (
        r"""{
  "columns": [
    {
      "detection_evidence": "there are 313 different values, more than the 40 a set of categories may have in a table of 400 rows -- but 2 level(s) of it are shared by at least 11 rows each, so this column is a long tail of labels rather than free text",
      "levels": [
        {
          "count": 77,
          "label": "2024-01-05 9:15 am",
          "shape_form_cells": 0,
          "variants": {
            "2024-01-05 9:15 AM": 77
          },
          "variants_withheld": {}
        },
        {
          "count": 12,
          "label": "unknown",
          "shape_form_cells": 0,
          "variants": {
            "unknown": 12
          },
          "variants_withheld": {}
        }
      ],
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
      "n_distinct": 313,
      "n_distinct_folded": 313,
      "n_missing": 0,
      "n_missing_blank": 0,
      "n_missing_withheld": 0,
      "n_not_numeric": 400,
      "n_numeric": 0,
      "n_out_of_range": 0,
      "n_present": 400,
      "n_sentinel_candidates_unpublished": 0,
      "name": "seen_at",
      "position": 1,
      "quality_state": "ok",
      "remarks": [],
      "role": "long_tail_labels",
      "sentinel_verdicts": [],
      "shape_forms": {},
      "statistical_type": "long_tail_labels",
      "structural_role": "data",
      "suppressed_levels": 311,
      "suppressed_numbers": {
        "mean": null,
        "n_cells": 0
      },
      "suppressed_rows": 311
    }
  ],
  "created_with": "0.1.0.dev0",
  "n_columns": 1,
  "n_rows": 400,
  "profile_version": 6,
  "publication_notes": [
    {
      "column": "",
      "note": "this description was made from a table of 400 rows, which is fewer than a thousand. Every count here is a count of ROWS over that population -- where your table holds several rows per person, a value only one person has is published with the number of their rows -- so each count narrows who a row could be further than the same count would in a large table. Nothing in this description is excused by the size: the same rules produced it, the smallest group size is the same number, and every obligation it states is the same obligation"
    },
    {
      "column": "seen_at",
      "note": "311 value(s) of this column are each shared by fewer than 11 rows, so they are counted together instead of being published (311 rows in total)"
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
    "forced_codes": [
      "seen_at"
    ],
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
          "lines": 401
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
""",
        "5da23fd8373d675747a8704af554d53529fb3ee7409dca6e2e2cb84ed4086c7b",
        "b38659ee7bbf6ad42b1ed93212209212afe4f3116a1780ba3c620527e7dbc512",
        True,
    ),
}
