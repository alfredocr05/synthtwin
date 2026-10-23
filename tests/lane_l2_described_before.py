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


# -- Codex's review of lane L2, item 2: label and code descriptions --------
#
# Four more descriptions 6a248e7's `synthtwin profile` wrote at a floor of
# eleven, of tables `label_tables` below builds: 100 rows of `9:15 AM`
# beside 100 of `10:30 PM`, read as labels and declared `--code`; 3,000
# rows of 60 times written `9:15 am`, one row in seven its letters turned
# over at random (`9:15 aM`); and 3,000 rows of 400 times to the
# millisecond written with U+202F before `am` or `pm`, a long tail. Before L2 none of their labels had
# a form, so every level carries `shape_form_cells` 0 while its named
# spellings now wear `%:%% @@` or its U+202F twin -- which the loader
# refused under W8 at 824c7a4. Each loads, generates the twin 6a248e7
# generated (its digest beside it, from a fresh process) and validates. The
# values are made-up times; no value of any table is in them. U+202F is
# written `\u202f` so this file stays ASCII; the text is the file's bytes.

TWO_LABELS = """{
  "columns": [
    {
      "detection_evidence": "there are exactly two different values, ignoring upper and lower case",
      "levels": [
        {
          "count": 100,
          "label": "10:30 pm",
          "shape_form_cells": 0,
          "variants": {
            "10:30 PM": 100
          },
          "variants_withheld": {}
        },
        {
          "count": 100,
          "label": "9:15 am",
          "shape_form_cells": 0,
          "variants": {
            "9:15 AM": 100
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
      "n_distinct": 2,
      "n_distinct_folded": 2,
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
      "remarks": [],
      "role": "binary",
      "sentinel_verdicts": [],
      "shape_forms": {},
      "statistical_type": "binary",
      "structural_role": "data",
      "suppressed_levels": 0,
      "suppressed_numbers": {
        "mean": null,
        "n_cells": 0
      },
      "suppressed_rows": 0
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
      "row_order": {
        "collation": "text",
        "column": 1,
        "direction": "descending"
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
    "header_by_convention": true,
    "header_evidence": "The first row was read as the column names by convention, not by evidence: a CSV file is normally written with its column names first, and nothing in this file contradicted that -- no value in the first row belongs among the values of the column below it. synthtwin did not check that those values ARE names, because no such check exists. If that row is really the first record, run the command again with --first-row data: the columns are then named column_1, column_2, and so on and every record is kept.",
    "header_source": "file",
    "used_fallback_encoding": false,
    "workbook": null
  }
}
"""
TWO_LABELS_SHA256 = "b9461a326296384401e85079f5d0013ebe81445f95a7f883f88594da75d9ee78"
TWO_LABELS_TWIN_SHA256 = "6e5de59618d69f693f67b20439a167a63d8ab345425f7bfb6fe2456b67725e88"

TWO_CODES = """{
  "columns": [
    {
      "detection_evidence": "there are exactly two different values, ignoring upper and lower case",
      "levels": [
        {
          "count": 100,
          "label": "10:30 pm",
          "shape_form_cells": 0,
          "variants": {
            "10:30 PM": 100
          },
          "variants_withheld": {}
        },
        {
          "count": 100,
          "label": "9:15 am",
          "shape_form_cells": 0,
          "variants": {
            "9:15 AM": 100
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
      "n_distinct": 2,
      "n_distinct_folded": 2,
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
      "remarks": [],
      "role": "binary",
      "sentinel_verdicts": [],
      "shape_forms": {},
      "statistical_type": "binary",
      "structural_role": "data",
      "suppressed_levels": 0,
      "suppressed_numbers": {
        "mean": null,
        "n_cells": 0
      },
      "suppressed_rows": 0
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
          "lines": 201
        }
      ],
      "line_endings_spread": [],
      "preamble": [],
      "preamble_withheld": false,
      "row_order": {
        "collation": "text",
        "column": 1,
        "direction": "descending"
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
    "header_by_convention": true,
    "header_evidence": "The first row was read as the column names by convention, not by evidence: a CSV file is normally written with its column names first, and nothing in this file contradicted that -- no value in the first row belongs among the values of the column below it. synthtwin did not check that those values ARE names, because no such check exists. If that row is really the first record, run the command again with --first-row data: the columns are then named column_1, column_2, and so on and every record is kept.",
    "header_source": "file",
    "used_fallback_encoding": false,
    "workbook": null
  }
}
"""
TWO_CODES_SHA256 = "bc370faaf1b895c4b86d75f99f0c41bafca29da53f549fa2d031b01972d099e3"
TWO_CODES_TWIN_SHA256 = "6e5de59618d69f693f67b20439a167a63d8ab345425f7bfb6fe2456b67725e88"

FLIPPED_LABELS = """{
  "columns": [
    {
      "detection_evidence": "there are 43 different values, which is within the 300 a set of categories may have in a table of 3000 rows, so this column is a set of categories",
      "level_ceiling": 300,
      "levels": [
        {
          "count": 1682,
          "label": "6:09 pm",
          "shape_form_cells": 0,
          "variants": {
            "6:09 PM": 52,
            "6:09 Pm": 47,
            "6:09 pM": 68,
            "6:09 pm": 1515
          },
          "variants_withheld": {}
        },
        {
          "count": 523,
          "label": "11:03 am",
          "shape_form_cells": 0,
          "variants": {
            "11:03 AM": 25,
            "11:03 Am": 19,
            "11:03 aM": 14,
            "11:03 am": 465
          },
          "variants_withheld": {}
        },
        {
          "count": 250,
          "label": "9:06 pm",
          "shape_form_cells": 0,
          "variants": {
            "9:06 Pm": 13,
            "9:06 pm": 237
          },
          "variants_withheld": {}
        },
        {
          "count": 126,
          "label": "10:03 am",
          "shape_form_cells": 0,
          "variants": {
            "10:03 am": 126
          },
          "variants_withheld": {}
        },
        {
          "count": 73,
          "label": "1:05 pm",
          "shape_form_cells": 0,
          "variants": {
            "1:05 pm": 73
          },
          "variants_withheld": {}
        },
        {
          "count": 64,
          "label": "7:04 am",
          "shape_form_cells": 0,
          "variants": {
            "7:04 am": 64
          },
          "variants_withheld": {}
        },
        {
          "count": 43,
          "label": "2:35 pm",
          "shape_form_cells": 0,
          "variants": {
            "2:35 pm": 43
          },
          "variants_withheld": {}
        },
        {
          "count": 35,
          "label": "1:52 am",
          "shape_form_cells": 0,
          "variants": {
            "1:52 am": 35
          },
          "variants_withheld": {}
        },
        {
          "count": 29,
          "label": "1:12 am",
          "shape_form_cells": 0,
          "variants": {
            "1:12 am": 29
          },
          "variants_withheld": {}
        },
        {
          "count": 26,
          "label": "4:40 am",
          "shape_form_cells": 0,
          "variants": {
            "4:40 am": 26
          },
          "variants_withheld": {}
        },
        {
          "count": 19,
          "label": "10:37 pm",
          "shape_form_cells": 0,
          "variants": {
            "10:37 pm": 19
          },
          "variants_withheld": {}
        },
        {
          "count": 19,
          "label": "5:26 am",
          "shape_form_cells": 0,
          "variants": {
            "5:26 am": 19
          },
          "variants_withheld": {}
        },
        {
          "count": 13,
          "label": "1:14 am",
          "shape_form_cells": 0,
          "variants": {
            "1:14 am": 13
          },
          "variants_withheld": {}
        },
        {
          "count": 11,
          "label": "9:54 am",
          "shape_form_cells": 0,
          "variants": {
            "9:54 am": 11
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
      "n_distinct": 58,
      "n_distinct_folded": 43,
      "n_missing": 0,
      "n_missing_blank": 0,
      "n_missing_withheld": 0,
      "n_not_numeric": 3000,
      "n_numeric": 0,
      "n_out_of_range": 0,
      "n_present": 3000,
      "n_sentinel_candidates_unpublished": 0,
      "name": "seen_at",
      "position": 1,
      "quality_state": "ok",
      "remarks": [
        "some values in this column differ only in upper and lower case; they are counted, and published, as one"
      ],
      "role": "categorical",
      "sentinel_verdicts": [],
      "shape_forms": {},
      "statistical_type": "categorical",
      "structural_role": "data",
      "suppressed_levels": 29,
      "suppressed_numbers": {
        "mean": null,
        "n_cells": 0
      },
      "suppressed_rows": 87
    }
  ],
  "created_with": "0.1.0.dev0",
  "n_columns": 1,
  "n_rows": 3000,
  "profile_version": 6,
  "publication_notes": [
    {
      "column": "seen_at",
      "note": "29 value(s) of this column are each shared by fewer than 11 rows, so they are counted together instead of being published (87 rows in total)"
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
          "lines": 3001
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
FLIPPED_LABELS_SHA256 = "d875cba549d080cc2e877ba89e9a6b0b9be9bf00660f6a82268795350eedba38"
FLIPPED_LABELS_TWIN_SHA256 = "34035b717b55cda6242a14d841ed0060abbca7a506d3561a91ddce0af7772971"

NARROW_TAIL = """{
  "columns": [
    {
      "detection_evidence": "there are 391 different values, more than the 300 a set of categories may have in a table of 3000 rows -- but 18 level(s) of it are shared by at least 11 rows each, so this column is a long tail of labels rather than free text",
      "levels": [
        {
          "count": 718,
          "label": "10:47:22.814\u202fam",
          "shape_form_cells": 0,
          "variants": {
            "10:47:22.814\u202fam": 718
          },
          "variants_withheld": {}
        },
        {
          "count": 254,
          "label": "08:15:41.053\u202fam",
          "shape_form_cells": 0,
          "variants": {
            "08:15:41.053\u202fam": 254
          },
          "variants_withheld": {}
        },
        {
          "count": 149,
          "label": "02:30:55.252\u202fpm",
          "shape_form_cells": 0,
          "variants": {
            "02:30:55.252\u202fpm": 149
          },
          "variants_withheld": {}
        },
        {
          "count": 67,
          "label": "09:36:15.013\u202fam",
          "shape_form_cells": 0,
          "variants": {
            "09:36:15.013\u202fam": 67
          },
          "variants_withheld": {}
        },
        {
          "count": 51,
          "label": "03:51:04.142\u202fpm",
          "shape_form_cells": 0,
          "variants": {
            "03:51:04.142\u202fpm": 51
          },
          "variants_withheld": {}
        },
        {
          "count": 46,
          "label": "07:11:58.888\u202fpm",
          "shape_form_cells": 0,
          "variants": {
            "07:11:58.888\u202fpm": 46
          },
          "variants_withheld": {}
        },
        {
          "count": 30,
          "label": "03:00:55.005\u202fam",
          "shape_form_cells": 0,
          "variants": {
            "03:00:55.005\u202fam": 30
          },
          "variants_withheld": {}
        },
        {
          "count": 30,
          "label": "04:55:10.296\u202fpm",
          "shape_form_cells": 0,
          "variants": {
            "04:55:10.296\u202fpm": 30
          },
          "variants_withheld": {}
        },
        {
          "count": 23,
          "label": "03:12:57.392\u202fpm",
          "shape_form_cells": 0,
          "variants": {
            "03:12:57.392\u202fpm": 23
          },
          "variants_withheld": {}
        },
        {
          "count": 20,
          "label": "06:19:30.713\u202fpm",
          "shape_form_cells": 0,
          "variants": {
            "06:19:30.713\u202fpm": 20
          },
          "variants_withheld": {}
        },
        {
          "count": 18,
          "label": "04:56:43.640\u202fam",
          "shape_form_cells": 0,
          "variants": {
            "04:56:43.640\u202fam": 18
          },
          "variants_withheld": {}
        },
        {
          "count": 17,
          "label": "01:26:10.958\u202fam",
          "shape_form_cells": 0,
          "variants": {
            "01:26:10.958\u202fam": 17
          },
          "variants_withheld": {}
        },
        {
          "count": 17,
          "label": "05:47:22.865\u202fpm",
          "shape_form_cells": 0,
          "variants": {
            "05:47:22.865\u202fpm": 17
          },
          "variants_withheld": {}
        },
        {
          "count": 14,
          "label": "05:21:19.837\u202fam",
          "shape_form_cells": 0,
          "variants": {
            "05:21:19.837\u202fam": 14
          },
          "variants_withheld": {}
        },
        {
          "count": 12,
          "label": "09:42:53.408\u202fam",
          "shape_form_cells": 0,
          "variants": {
            "09:42:53.408\u202fam": 12
          },
          "variants_withheld": {}
        },
        {
          "count": 12,
          "label": "10:00:28.047\u202fam",
          "shape_form_cells": 0,
          "variants": {
            "10:00:28.047\u202fam": 12
          },
          "variants_withheld": {}
        },
        {
          "count": 11,
          "label": "06:22:57.537\u202fpm",
          "shape_form_cells": 0,
          "variants": {
            "06:22:57.537\u202fpm": 11
          },
          "variants_withheld": {}
        },
        {
          "count": 11,
          "label": "10:45:21.067\u202fpm",
          "shape_form_cells": 0,
          "variants": {
            "10:45:21.067\u202fpm": 11
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
      "n_distinct": 391,
      "n_distinct_folded": 391,
      "n_missing": 0,
      "n_missing_blank": 0,
      "n_missing_withheld": 0,
      "n_not_numeric": 3000,
      "n_numeric": 0,
      "n_out_of_range": 0,
      "n_present": 3000,
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
      "suppressed_levels": 373,
      "suppressed_numbers": {
        "mean": null,
        "n_cells": 0
      },
      "suppressed_rows": 1500
    }
  ],
  "created_with": "0.1.0.dev0",
  "n_columns": 1,
  "n_rows": 3000,
  "profile_version": 6,
  "publication_notes": [
    {
      "column": "seen_at",
      "note": "373 value(s) of this column are each shared by fewer than 11 rows, so they are counted together instead of being published (1500 rows in total)"
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
          "lines": 3001
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
NARROW_TAIL_SHA256 = "8a05a01e9ff0303e6f5b6067fb1f6dfaf02215e37193f5cfd1e43c6c80b270e0"
NARROW_TAIL_TWIN_SHA256 = "7dca4f29e6ca710de6be6a2d65767bba8a473145600f8e91cdef8f01443a746d"


def label_tables() -> "dict[str, list[str]]":
    """The four tables 6a248e7 described above, rebuilt cell for cell."""
    import random

    narrow = "\u202f"
    pairs = ("am", "pm")

    def flipped(text: str, draw: random.Random) -> str:
        return "".join(c.swapcase() if c.isalpha() and draw.random() < 0.5 else c for c in text)

    two = ["9:15 AM"] * 100 + ["10:30 PM"] * 100  # written in capitals
    draw = random.Random(7)
    pool = [f"{draw.randrange(1, 13)}:{draw.randrange(60):02d} {pairs[draw.randrange(2)]}" for _ in range(60)]
    varied: "list[str]" = []
    for row in range(3000):
        cell = pool[min(int(draw.paretovariate(1.2)) - 1, 59)]
        varied += [flipped(cell, draw) if row % 7 == 0 else cell]
    draw = random.Random(5)
    tail_pool = []
    for _ in range(400):
        hour = draw.randrange(1, 13)
        draw.randrange(60)
        text = f"{hour:02d}:{draw.randrange(60):02d}:{draw.randrange(60):02d}.{draw.randrange(1000):03d}"
        tail_pool += [text + narrow + pairs[draw.randrange(2)]]
    tail = [
        tail_pool[min(int(draw.paretovariate(1.0)) - 1, 399)] if row % 2 else tail_pool[draw.randrange(400)]
        for row in range(3000)
    ]
    return {"TWO_LABELS": two, "TWO_CODES": two, "FLIPPED_LABELS": varied, "NARROW_TAIL": tail}


# Each description, its digest and its twin's, and whether it was declared --code.
LABELS_AND_CODES = {
    "TWO_LABELS": (TWO_LABELS, TWO_LABELS_SHA256, TWO_LABELS_TWIN_SHA256, False),
    "TWO_CODES": (TWO_CODES, TWO_CODES_SHA256, TWO_CODES_TWIN_SHA256, True),
    "FLIPPED_LABELS": (FLIPPED_LABELS, FLIPPED_LABELS_SHA256, FLIPPED_LABELS_TWIN_SHA256, False),
    "NARROW_TAIL": (NARROW_TAIL, NARROW_TAIL_SHA256, NARROW_TAIL_TWIN_SHA256, False),
}
