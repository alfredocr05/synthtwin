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
here and are no one's. Beside them, at floors 11 and 36, two sets of
labels whose levels hold case variants (`PM`, `pm`, `Pm`): stamps written
straight on after the space and stamps of 25 characters (skeptic 1 of L3,
item 2), whose twins move wherever the generator reads their named
spellings as written since L3.

`MOVED` holds the descriptions written before L3 that do NOT generate
7d27335's twin: a stamp parted by a letter (`T`, or `t` where every letter
is lower case) and of 24 characters or fewer was already a form, which
7d27335 filled letter by letter and which is filled since L3 with `T` (or
`t`), the marker word and the zone's `Z` (skeptic 1 of L3, item 1; skeptic
2, items 1 and 2). Each still loads and validates with the exits 7d27335
gave.
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
    tables.update(flipped_tables())
    return tables



def _short_t_stamp(draw: random.Random, glued: bool) -> str:
    """One made-up stamp parted by `T`, of 24 characters or fewer."""
    month, day, hour, minute = draw.randrange(1, 13), draw.randrange(1, 29), draw.randrange(24), draw.randrange(60)
    draw.randrange(60)
    hour12 = draw.randrange(1, 13)
    word = ("AM", "PM")[draw.randrange(2)]
    if glued:
        return f"2024-{month:02d}-{day:02d}T{hour12}:{minute:02d}{word}"
    return f"2024-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}"


def moved_tables() -> "dict[str, list[str]]":
    """The cells of each frozen description whose twin moved at L3, by name.

    A stamp parted by `T` and of 24 characters or fewer was a form before
    L3, so its description publishes that form: free text written
    `2024-mm-ddTHH:MM` and labels written `2024-mm-ddTh:mmAM`, beside rare
    words. 7d27335 filled the `T` and the marker letter by letter
    (`7040-00-06C28:35`); since L3 the fill writes `T` and the marker word.
    """
    draw = random.Random(11)
    free = [("pending", "unknown")[row % 2] if row % 33 == 7 else _short_t_stamp(draw, False) for row in range(600)]
    draw = random.Random(11)
    pool = [_short_t_stamp(draw, True) for _ in range(200)]
    labels: "list[str]" = []
    for row in range(1500):
        if row % 33 == 7:
            labels += [("pending", "unknown")[row % 2]]
            continue
        labels += [pool[min(int(draw.paretovariate(1.0)) - 1, 199)]]
    tables = {"moved-free": free, "moved-labels": labels}
    tables.update(lettered_tables())
    return tables


def lettered_tables() -> "dict[str, list[str]]":
    """Free text of short stamps whose letters 7d27335 filled by the step (skeptic 2 of L3).

    `moved-lower-t` is written `2024-mm-ddtHH:MM`, parted by a lower-case
    `t` (item 1): its form's letter is `&`, which since L3 is written `t`.
    `moved-zone` is written `2024-mm-ddTHH:MM:SSZ` and `2024-mm-ddTHH:MM:SS.mmmZ`,
    as FHIR's `instant` and JavaScript's `toISOString` write them (item 2):
    since the zone is read its `T` and its `Z` are written as such. Each
    stamp is of 24 characters or fewer, a form before L3, beside rare words.
    """
    draw = random.Random(12)
    lower: "list[str]" = []
    zoned: "list[str]" = []
    for row in range(600):
        month, day, hour, minute, second = (
            draw.randrange(1, 13), draw.randrange(1, 29), draw.randrange(24), draw.randrange(60), draw.randrange(60)
        )
        if row % 33 == 7:
            lower += [("pending", "unknown")[row % 2]]
            zoned += [("pending", "unknown")[row % 2]]
            continue
        lower += [f"2024-{month:02d}-{day:02d}t{hour:02d}:{minute:02d}"]
        fraction = f".{draw.randrange(1000):03d}" if row % 2 else ""
        zoned += [f"2024-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:{second:02d}{fraction}Z"]
    return {"moved-lower-t": lower, "moved-zone": zoned}


def flipped_tables() -> "dict[str, list[str]]":
    """Labels of stamps whose levels hold case variants (`PM`, `pm`, `Pm`), by name.

    `flip-short` is written straight on after a space (`2024-01-05 9:15PM`),
    `flip-long` runs to 25 characters (`2024-01-05T09:15:30.123PM`): neither
    was a form before L3, and each named spelling wears a stamp form now.
    Each is frozen at floors 11 and 36 (`flip-short-11` ... `flip-long-36`).
    """
    tables: "dict[str, list[str]]" = {}
    for kind in ("short", "long"):
        draw = random.Random(7)
        pool: "list[str]" = []
        for _ in range(40):
            month, day, hour, minute = draw.randrange(1, 13), draw.randrange(1, 29), draw.randrange(1, 13), draw.randrange(60)
            if kind == "short":
                pool += [f"2024-{month:02d}-{day:02d} {hour}:{minute:02d}PM"]
                continue
            second, part = draw.randrange(60), draw.randrange(1000)
            pool += [f"2024-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:{second:02d}.{part:03d}PM"]
        cells: "list[str]" = []
        for row in range(2000):
            if row % 33 == 7:
                cells += [("pending", "unknown")[row % 2]]
                continue
            stamp = pool[min(int(draw.paretovariate(1.0)) - 1, 39)]
            flip = draw.random()
            cells += [stamp if flip < 0.6 else (stamp[:-2] + "pm" if flip < 0.8 else stamp[:-2] + "Pm")]
        tables[f"flip-{kind}-11"] = cells
        tables[f"flip-{kind}-36"] = cells
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
    "flip-short-11": (
        r"""{
  "columns": [
    {
      "detection_evidence": "there are 42 different values, which is within the 200 a set of categories may have in a table of 2000 rows, so this column is a set of categories",
      "level_ceiling": 200,
      "levels": [
        {
          "count": 951,
          "label": "2024-06-05 7:41pm",
          "shape_form_cells": 0,
          "variants": {
            "2024-06-05 7:41PM": 561,
            "2024-06-05 7:41Pm": 179,
            "2024-06-05 7:41pm": 211
          },
          "variants_withheld": {}
        },
        {
          "count": 322,
          "label": "2024-01-03 9:06pm",
          "shape_form_cells": 0,
          "variants": {
            "2024-01-03 9:06PM": 193,
            "2024-01-03 9:06Pm": 64,
            "2024-01-03 9:06pm": 65
          },
          "variants_withheld": {}
        },
        {
          "count": 154,
          "label": "2024-06-19 1:58pm",
          "shape_form_cells": 0,
          "variants": {
            "2024-06-19 1:58PM": 92,
            "2024-06-19 1:58Pm": 30,
            "2024-06-19 1:58pm": 32
          },
          "variants_withheld": {}
        },
        {
          "count": 98,
          "label": "2024-09-07 1:05pm",
          "shape_form_cells": 0,
          "variants": {
            "2024-09-07 1:05PM": 62,
            "2024-09-07 1:05Pm": 15,
            "2024-09-07 1:05pm": 21
          },
          "variants_withheld": {}
        },
        {
          "count": 56,
          "label": "2024-07-14 2:15pm",
          "shape_form_cells": 0,
          "variants": {
            "2024-07-14 2:15PM": 42,
            "2024-07-14 2:15Pm": 14
          },
          "variants_withheld": {}
        },
        {
          "count": 52,
          "label": "2024-02-18 7:03pm",
          "shape_form_cells": 0,
          "variants": {
            "2024-02-18 7:03PM": 40,
            "2024-02-18 7:03pm": 12
          },
          "variants_withheld": {}
        },
        {
          "count": 50,
          "label": "2024-05-05 7:55pm",
          "shape_form_cells": 0,
          "variants": {
            "2024-05-05 7:55PM": 39,
            "2024-05-05 7:55pm": 11
          },
          "variants_withheld": {}
        },
        {
          "count": 34,
          "label": "2024-10-13 1:14pm",
          "shape_form_cells": 0,
          "variants": {
            "2024-10-13 1:14PM": 34
          },
          "variants_withheld": {}
        },
        {
          "count": 33,
          "label": "2024-10-04 4:40pm",
          "shape_form_cells": 0,
          "variants": {
            "2024-10-04 4:40PM": 33
          },
          "variants_withheld": {}
        },
        {
          "count": 32,
          "label": "2024-11-19 1:36pm",
          "shape_form_cells": 0,
          "variants": {
            "2024-11-19 1:36PM": 32
          },
          "variants_withheld": {}
        },
        {
          "count": 31,
          "label": "unknown",
          "shape_form_cells": 0,
          "variants": {
            "unknown": 31
          },
          "variants_withheld": {}
        },
        {
          "count": 30,
          "label": "pending",
          "shape_form_cells": 0,
          "variants": {
            "pending": 30
          },
          "variants_withheld": {}
        },
        {
          "count": 22,
          "label": "2024-07-05 9:07pm",
          "shape_form_cells": 0,
          "variants": {
            "2024-07-05 9:07PM": 22
          },
          "variants_withheld": {}
        },
        {
          "count": 16,
          "label": "2024-10-10 9:52pm",
          "shape_form_cells": 0,
          "variants": {
            "2024-10-10 9:52PM": 16
          },
          "variants_withheld": {}
        },
        {
          "count": 13,
          "label": "2024-01-18 3:18pm",
          "shape_form_cells": 0,
          "variants": {
            "2024-01-18 3:18PM": 13
          },
          "variants_withheld": {}
        },
        {
          "count": 13,
          "label": "2024-10-21 4:23pm",
          "shape_form_cells": 0,
          "variants": {
            "2024-10-21 4:23PM": 13
          },
          "variants_withheld": {}
        },
        {
          "count": 11,
          "label": "2024-11-06 2:37pm",
          "shape_form_cells": 0,
          "variants": {
            "2024-11-06 2:37PM": 11
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
      "n_distinct": 69,
      "n_distinct_folded": 42,
      "n_missing": 0,
      "n_missing_blank": 0,
      "n_missing_withheld": 0,
      "n_not_numeric": 2000,
      "n_numeric": 0,
      "n_out_of_range": 0,
      "n_present": 2000,
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
      "suppressed_levels": 25,
      "suppressed_numbers": {
        "mean": null,
        "n_cells": 0
      },
      "suppressed_rows": 82
    }
  ],
  "created_with": "0.1.0.dev0",
  "n_columns": 1,
  "n_rows": 2000,
  "profile_version": 6,
  "publication_notes": [
    {
      "column": "seen_at",
      "note": "25 value(s) of this column are each shared by fewer than 11 rows, so they are counted together instead of being published (82 rows in total)"
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
          "lines": 2001
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
        "648776a0400ab0d299e784d80f845d563610a8901a121763d7f3baeae35abc07",
        "bb8157880694343aed585e56c27f3fc7f9f073416797efed955004e5585afcf6",
        False,
    ),
    "flip-short-36": (
        r"""{
  "columns": [
    {
      "detection_evidence": "there are 42 different values, which is within the 200 a set of categories may have in a table of 2000 rows, so this column is a set of categories",
      "level_ceiling": 200,
      "levels": [
        {
          "count": 951,
          "label": "2024-06-05 7:41pm",
          "shape_form_cells": 0,
          "variants": {
            "2024-06-05 7:41PM": 561,
            "2024-06-05 7:41Pm": 179,
            "2024-06-05 7:41pm": 211
          },
          "variants_withheld": {}
        },
        {
          "count": 322,
          "label": "2024-01-03 9:06pm",
          "shape_form_cells": 0,
          "variants": {
            "2024-01-03 9:06PM": 193,
            "2024-01-03 9:06Pm": 64,
            "2024-01-03 9:06pm": 65
          },
          "variants_withheld": {}
        },
        {
          "count": 154,
          "label": "2024-06-19 1:58pm",
          "shape_form_cells": 0,
          "variants": {
            "2024-06-19 1:58PM": 154
          },
          "variants_withheld": {}
        },
        {
          "count": 98,
          "label": "2024-09-07 1:05pm",
          "shape_form_cells": 0,
          "variants": {
            "2024-09-07 1:05PM": 98
          },
          "variants_withheld": {}
        },
        {
          "count": 56,
          "label": "2024-07-14 2:15pm",
          "shape_form_cells": 0,
          "variants": {
            "2024-07-14 2:15PM": 56
          },
          "variants_withheld": {}
        },
        {
          "count": 52,
          "label": "2024-02-18 7:03pm",
          "shape_form_cells": 0,
          "variants": {
            "2024-02-18 7:03PM": 52
          },
          "variants_withheld": {}
        },
        {
          "count": 50,
          "label": "2024-05-05 7:55pm",
          "shape_form_cells": 0,
          "variants": {
            "2024-05-05 7:55PM": 50
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
      "n_distinct": 77,
      "n_distinct_folded": 42,
      "n_missing": 0,
      "n_missing_blank": 0,
      "n_missing_withheld": 0,
      "n_not_numeric": 2000,
      "n_numeric": 0,
      "n_out_of_range": 0,
      "n_present": 2000,
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
      "suppressed_levels": 35,
      "suppressed_numbers": {
        "mean": null,
        "n_cells": 0
      },
      "suppressed_rows": 317
    }
  ],
  "created_with": "0.1.0.dev0",
  "n_columns": 1,
  "n_rows": 2000,
  "profile_version": 6,
  "publication_notes": [
    {
      "column": "seen_at",
      "note": "35 value(s) of this column are each shared by fewer than 36 rows, so they are counted together instead of being published (317 rows in total)"
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
    "small_cell_floor": 36
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
          "lines": 2001
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
        "ed1912e2a56be71eb168a5e3fea831a838e24501d965c5ebcd0a4ce05635537f",
        "62f4827054c514f00ed14bfd8609ceaf0779994ee683ecf1cc903aace6707e09",
        False,
    ),
    "flip-long-11": (
        r"""{
  "columns": [
    {
      "detection_evidence": "there are 40 different values, which is within the 200 a set of categories may have in a table of 2000 rows, so this column is a set of categories",
      "level_ceiling": 200,
      "levels": [
        {
          "count": 975,
          "label": "2024-06-05t07:41:03.074pm",
          "shape_form_cells": 0,
          "variants": {
            "2024-06-05T07:41:03.074PM": 560,
            "2024-06-05T07:41:03.074Pm": 209,
            "2024-06-05T07:41:03.074pm": 206
          },
          "variants_withheld": {}
        },
        {
          "count": 334,
          "label": "2024-09-04t06:37:03.931pm",
          "shape_form_cells": 0,
          "variants": {
            "2024-09-04T06:37:03.931PM": 191,
            "2024-09-04T06:37:03.931Pm": 75,
            "2024-09-04T06:37:03.931pm": 68
          },
          "variants_withheld": {}
        },
        {
          "count": 166,
          "label": "2024-09-07t01:05:27.428pm",
          "shape_form_cells": 0,
          "variants": {
            "2024-09-07T01:05:27.428PM": 97,
            "2024-09-07T01:05:27.428Pm": 37,
            "2024-09-07T01:05:27.428pm": 32
          },
          "variants_withheld": {}
        },
        {
          "count": 98,
          "label": "2024-02-08t02:35:27.060pm",
          "shape_form_cells": 0,
          "variants": {
            "2024-02-08T02:35:27.060PM": 49,
            "2024-02-08T02:35:27.060Pm": 26,
            "2024-02-08T02:35:27.060pm": 23
          },
          "variants_withheld": {}
        },
        {
          "count": 58,
          "label": "2024-10-04t04:40:40.596pm",
          "shape_form_cells": 0,
          "variants": {
            "2024-10-04T04:40:40.596PM": 30,
            "2024-10-04T04:40:40.596Pm": 15,
            "2024-10-04T04:40:40.596pm": 13
          },
          "variants_withheld": {}
        },
        {
          "count": 49,
          "label": "2024-03-18t02:23:39.026pm",
          "shape_form_cells": 0,
          "variants": {
            "2024-03-18T02:23:39.026PM": 26,
            "2024-03-18T02:23:39.026Pm": 11,
            "2024-03-18T02:23:39.026pm": 12
          },
          "variants_withheld": {}
        },
        {
          "count": 46,
          "label": "2024-01-19t10:25:03.999pm",
          "shape_form_cells": 0,
          "variants": {
            "2024-01-19T10:25:03.999PM": 33,
            "2024-01-19T10:25:03.999pm": 13
          },
          "variants_withheld": {}
        },
        {
          "count": 31,
          "label": "unknown",
          "shape_form_cells": 0,
          "variants": {
            "unknown": 31
          },
          "variants_withheld": {}
        },
        {
          "count": 30,
          "label": "pending",
          "shape_form_cells": 0,
          "variants": {
            "pending": 30
          },
          "variants_withheld": {}
        },
        {
          "count": 26,
          "label": "2024-09-27t11:11:06.595pm",
          "shape_form_cells": 0,
          "variants": {
            "2024-09-27T11:11:06.595PM": 26
          },
          "variants_withheld": {}
        },
        {
          "count": 25,
          "label": "2024-07-05t09:07:36.315pm",
          "shape_form_cells": 0,
          "variants": {
            "2024-07-05T09:07:36.315PM": 25
          },
          "variants_withheld": {}
        },
        {
          "count": 24,
          "label": "2024-04-02t09:54:08.296pm",
          "shape_form_cells": 0,
          "variants": {
            "2024-04-02T09:54:08.296PM": 24
          },
          "variants_withheld": {}
        },
        {
          "count": 18,
          "label": "2024-12-03t10:03:39.210pm",
          "shape_form_cells": 0,
          "variants": {
            "2024-12-03T10:03:39.210PM": 18
          },
          "variants_withheld": {}
        },
        {
          "count": 16,
          "label": "2024-08-19t08:23:19.254pm",
          "shape_form_cells": 0,
          "variants": {
            "2024-08-19T08:23:19.254PM": 16
          },
          "variants_withheld": {}
        },
        {
          "count": 11,
          "label": "2024-10-21t04:23:06.560pm",
          "shape_form_cells": 0,
          "variants": {
            "2024-10-21T04:23:06.560PM": 11
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
      "n_distinct": 78,
      "n_distinct_folded": 40,
      "n_missing": 0,
      "n_missing_blank": 0,
      "n_missing_withheld": 0,
      "n_not_numeric": 2000,
      "n_numeric": 0,
      "n_out_of_range": 0,
      "n_present": 2000,
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
      "suppressed_levels": 25,
      "suppressed_numbers": {
        "mean": null,
        "n_cells": 0
      },
      "suppressed_rows": 93
    }
  ],
  "created_with": "0.1.0.dev0",
  "n_columns": 1,
  "n_rows": 2000,
  "profile_version": 6,
  "publication_notes": [
    {
      "column": "seen_at",
      "note": "25 value(s) of this column are each shared by fewer than 11 rows, so they are counted together instead of being published (93 rows in total)"
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
          "lines": 2001
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
        "d02c69b76886752878d9d26251e08ddb7b420e764d9fe3ee1ed3c14a10542d21",
        "5adb504fd6cd64a2e3f57f28a6a388d33fe8815d1033fe2ec85ac8718ca5ca7d",
        False,
    ),
    "flip-long-36": (
        r"""{
  "columns": [
    {
      "detection_evidence": "there are 40 different values, which is within the 200 a set of categories may have in a table of 2000 rows, so this column is a set of categories",
      "level_ceiling": 200,
      "levels": [
        {
          "count": 975,
          "label": "2024-06-05t07:41:03.074pm",
          "shape_form_cells": 0,
          "variants": {
            "2024-06-05T07:41:03.074PM": 560,
            "2024-06-05T07:41:03.074Pm": 209,
            "2024-06-05T07:41:03.074pm": 206
          },
          "variants_withheld": {}
        },
        {
          "count": 334,
          "label": "2024-09-04t06:37:03.931pm",
          "shape_form_cells": 0,
          "variants": {
            "2024-09-04T06:37:03.931PM": 191,
            "2024-09-04T06:37:03.931Pm": 75,
            "2024-09-04T06:37:03.931pm": 68
          },
          "variants_withheld": {}
        },
        {
          "count": 166,
          "label": "2024-09-07t01:05:27.428pm",
          "shape_form_cells": 0,
          "variants": {
            "2024-09-07T01:05:27.428PM": 129,
            "2024-09-07T01:05:27.428Pm": 37
          },
          "variants_withheld": {}
        },
        {
          "count": 98,
          "label": "2024-02-08t02:35:27.060pm",
          "shape_form_cells": 0,
          "variants": {
            "2024-02-08T02:35:27.060PM": 98
          },
          "variants_withheld": {}
        },
        {
          "count": 58,
          "label": "2024-10-04t04:40:40.596pm",
          "shape_form_cells": 0,
          "variants": {
            "2024-10-04T04:40:40.596PM": 58
          },
          "variants_withheld": {}
        },
        {
          "count": 49,
          "label": "2024-03-18t02:23:39.026pm",
          "shape_form_cells": 0,
          "variants": {
            "2024-03-18T02:23:39.026PM": 49
          },
          "variants_withheld": {}
        },
        {
          "count": 46,
          "label": "2024-01-19t10:25:03.999pm",
          "shape_form_cells": 0,
          "variants": {
            "2024-01-19T10:25:03.999PM": 46
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
      "n_distinct": 82,
      "n_distinct_folded": 40,
      "n_missing": 0,
      "n_missing_blank": 0,
      "n_missing_withheld": 0,
      "n_not_numeric": 2000,
      "n_numeric": 0,
      "n_out_of_range": 0,
      "n_present": 2000,
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
      "suppressed_levels": 33,
      "suppressed_numbers": {
        "mean": null,
        "n_cells": 0
      },
      "suppressed_rows": 274
    }
  ],
  "created_with": "0.1.0.dev0",
  "n_columns": 1,
  "n_rows": 2000,
  "profile_version": 6,
  "publication_notes": [
    {
      "column": "seen_at",
      "note": "33 value(s) of this column are each shared by fewer than 36 rows, so they are counted together instead of being published (274 rows in total)"
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
    "small_cell_floor": 36
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
          "lines": 2001
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
        "fbac3874a7d73d8ab4ee808bf9e5fc86e2f57925892de9cb3f04d3e6bfbc46d0",
        "879d13818192b9111007eaff8f5ee0f4b53a77b1003218ba95a8d17f225a4b10",
        False,
    ),
}

# Descriptions written before L3 whose twin moved at L3 (plan P4-D393, skeptic
# 1 of L3, item 1, and skeptic 2, items 1 and 2): each entry is (the
# description's text, its sha256, the twin 7d27335 generated at seed 0, the
# twin generated since L3, and the exits 7d27335's validation gave against
# its own twin and the table). `moved-zone`'s twin misses `length.mean` at
# 7d27335 and since alike (exit 3): the fill keeps every stamp's length,
# so that miss is no part of L3's.

MOVED = {
    "moved-free": (
        r"""{
  "columns": [
    {
      "detection_evidence": "none of the 600 values is written as a number, 582 read as dates written as 2024-03-17 14:05:00, and there are 584 different values where a set of categories may have at most 60 in a table of 600 rows",
      "length": {
        "max": 16,
        "mean": 15.73,
        "min": 7,
        "p50": 16.0
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
      "n_code_alphabet": 18,
      "n_contradictory": 0,
      "n_distinct": 584,
      "n_distinct_by_occurrences": {
        "1": 582,
        "9": 2
      },
      "n_distinct_folded": 584,
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
      "remarks": [
        "synthtwin could not settle what this column holds, so none of its values is published. Here is why: none of the 600 values is written as a number and 582 read as dates written as 2024-03-17 14:05:00; a column is described as numbers, or as dates, only when at least 594 of them read that way. It holds 584 different values, where a set of categories may hold at most 60. Describing it from the part that does read would publish an average, a spread and points along a range that the rest of the column contradicts, so synthtwin describes it as free text and publishes no value of it at all. If these are measurements written with a currency sign, a per-cent sign, a unit such as mg, or a clock time, write them as plain numbers -- one column for the number, and the unit in the column name -- and run the command again. Fewer than 11 of its values are numbers wearing one shared piece of text, which is the reading that came closest",
        "nearly every value in this column is different, some are shared with another row, and none of the forms synthtwin can read fits them. synthtwin did NOT assume they are record numbers: it cannot tell from the values alone whether these are record numbers or measurements written in a form it does not read yet, and a wrong guess would throw away the whole distribution. Nothing from this column is published either way -- no value of it, and no distribution. If these ARE record numbers, run the command again with --identifier NAME, where NAME is this column's name, and the profile will say so. If they are measurements written with a currency sign, a per-cent sign, a unit such as mg, or a clock time, write them as plain numbers -- one column for the number, and the unit in the column name -- and their distribution will be described. Do not use --identifier on a measurement: it withholds the column entirely"
      ],
      "role": "free_text",
      "sentinel_verdicts": [],
      "shape_forms": {
        "%%%%-%%-%%@%%:%%": 582
      },
      "statistical_type": "text",
      "structural_role": "data",
      "words": {
        "max": 1,
        "mean": 1.0,
        "min": 1
      }
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
        "20c38aed4ca490d33a1fafd421185c0be6f629aac6ebfff1e7e8e3135bdc1a3e",
        "eb69b02db9872af13f60524baa360e22c9a030eb880e8f69ea589858adeeaacc",
        "b07588cf04a2279c023f2515f8d7294f4d7c4960ef7f81d2f7d8179eeba1a40b",
        (0, 0),
    ),
    "moved-labels": (
        r"""{
  "columns": [
    {
      "detection_evidence": "there are 62 different values, which is within the 150 a set of categories may have in a table of 1500 rows, so this column is a set of categories",
      "level_ceiling": 150,
      "levels": [
        {
          "count": 738,
          "label": "2024-08-28t8:54pm",
          "shape_form_cells": 738,
          "variants": {
            "2024-08-28T8:54PM": 738
          },
          "variants_withheld": {}
        },
        {
          "count": 236,
          "label": "2024-09-28t9:12pm",
          "shape_form_cells": 236,
          "variants": {
            "2024-09-28T9:12PM": 236
          },
          "variants_withheld": {}
        },
        {
          "count": 117,
          "label": "2024-11-20t5:06am",
          "shape_form_cells": 117,
          "variants": {
            "2024-11-20T5:06AM": 117
          },
          "variants_withheld": {}
        },
        {
          "count": 66,
          "label": "2024-02-18t10:40pm",
          "shape_form_cells": 66,
          "variants": {
            "2024-02-18T10:40PM": 66
          },
          "variants_withheld": {}
        },
        {
          "count": 46,
          "label": "2024-08-21t3:39am",
          "shape_form_cells": 46,
          "variants": {
            "2024-08-21T3:39AM": 46
          },
          "variants_withheld": {}
        },
        {
          "count": 31,
          "label": "2024-09-03t4:02am",
          "shape_form_cells": 31,
          "variants": {
            "2024-09-03T4:02AM": 31
          },
          "variants_withheld": {}
        },
        {
          "count": 29,
          "label": "2024-11-10t2:00pm",
          "shape_form_cells": 29,
          "variants": {
            "2024-11-10T2:00PM": 29
          },
          "variants_withheld": {}
        },
        {
          "count": 23,
          "label": "pending",
          "shape_form_cells": 0,
          "variants": {
            "pending": 23
          },
          "variants_withheld": {}
        },
        {
          "count": 23,
          "label": "unknown",
          "shape_form_cells": 0,
          "variants": {
            "unknown": 23
          },
          "variants_withheld": {}
        },
        {
          "count": 22,
          "label": "2024-11-09t2:35pm",
          "shape_form_cells": 22,
          "variants": {
            "2024-11-09T2:35PM": 22
          },
          "variants_withheld": {}
        },
        {
          "count": 19,
          "label": "2024-08-11t4:37am",
          "shape_form_cells": 19,
          "variants": {
            "2024-08-11T4:37AM": 19
          },
          "variants_withheld": {}
        },
        {
          "count": 14,
          "label": "2024-10-25t5:25pm",
          "shape_form_cells": 14,
          "variants": {
            "2024-10-25T5:25PM": 14
          },
          "variants_withheld": {}
        },
        {
          "count": 12,
          "label": "2024-04-22t5:33pm",
          "shape_form_cells": 12,
          "variants": {
            "2024-04-22T5:33PM": 12
          },
          "variants_withheld": {}
        },
        {
          "count": 12,
          "label": "2024-08-13t2:25am",
          "shape_form_cells": 12,
          "variants": {
            "2024-08-13T2:25AM": 12
          },
          "variants_withheld": {}
        },
        {
          "count": 11,
          "label": "2024-06-25t1:32am",
          "shape_form_cells": 11,
          "variants": {
            "2024-06-25T1:32AM": 11
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
      "n_distinct": 62,
      "n_distinct_folded": 62,
      "n_missing": 0,
      "n_missing_blank": 0,
      "n_missing_withheld": 0,
      "n_not_numeric": 1500,
      "n_numeric": 0,
      "n_out_of_range": 0,
      "n_present": 1500,
      "n_sentinel_candidates_unpublished": 0,
      "name": "seen_at",
      "position": 1,
      "quality_state": "ok",
      "remarks": [],
      "role": "categorical",
      "sentinel_verdicts": [],
      "shape_forms": {
        "%%%%-%%-%%@%%:%%@@": 89,
        "%%%%-%%-%%@%:%%@@": 1365
      },
      "statistical_type": "categorical",
      "structural_role": "data",
      "suppressed_levels": 47,
      "suppressed_numbers": {
        "mean": null,
        "n_cells": 0
      },
      "suppressed_rows": 101
    }
  ],
  "created_with": "0.1.0.dev0",
  "n_columns": 1,
  "n_rows": 1500,
  "profile_version": 6,
  "publication_notes": [
    {
      "column": "seen_at",
      "note": "47 value(s) of this column are each shared by fewer than 11 rows, so they are counted together instead of being published (101 rows in total)"
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
          "lines": 1501
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
        "507113458c1e9328e28069ad0c0eb54e0bcd17c9db8be0a8445c8cbef9cea577",
        "29d218e6dc7d4e1dedbcaabd1116a94934c0d3731af888292d5919d58e89772a",
        "b0f25abd8f0941957e3ab5f5812f882e36b53da6d433967216a086665b947deb",
        (0, 0),
    ),
    "moved-lower-t": (
        r"""{
  "columns": [
    {
      "detection_evidence": "none of the 600 values is written as a number, 582 read as dates written as 2024-03-17 14:05:00, and there are 584 different values where a set of categories may have at most 60 in a table of 600 rows",
      "length": {
        "max": 16,
        "mean": 15.73,
        "min": 7,
        "p50": 16.0
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
      "n_code_alphabet": 18,
      "n_contradictory": 0,
      "n_distinct": 584,
      "n_distinct_by_occurrences": {
        "1": 582,
        "9": 2
      },
      "n_distinct_folded": 584,
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
      "remarks": [
        "synthtwin could not settle what this column holds, so none of its values is published. Here is why: none of the 600 values is written as a number and 582 read as dates written as 2024-03-17 14:05:00; a column is described as numbers, or as dates, only when at least 594 of them read that way. It holds 584 different values, where a set of categories may hold at most 60. Describing it from the part that does read would publish an average, a spread and points along a range that the rest of the column contradicts, so synthtwin describes it as free text and publishes no value of it at all. If these are measurements written with a currency sign, a per-cent sign, a unit such as mg, or a clock time, write them as plain numbers -- one column for the number, and the unit in the column name -- and run the command again. Fewer than 11 of its values are numbers wearing one shared piece of text, which is the reading that came closest",
        "nearly every value in this column is different, some are shared with another row, and none of the forms synthtwin can read fits them. synthtwin did NOT assume they are record numbers: it cannot tell from the values alone whether these are record numbers or measurements written in a form it does not read yet, and a wrong guess would throw away the whole distribution. Nothing from this column is published either way -- no value of it, and no distribution. If these ARE record numbers, run the command again with --identifier NAME, where NAME is this column's name, and the profile will say so. If they are measurements written with a currency sign, a per-cent sign, a unit such as mg, or a clock time, write them as plain numbers -- one column for the number, and the unit in the column name -- and their distribution will be described. Do not use --identifier on a measurement: it withholds the column entirely"
      ],
      "role": "free_text",
      "sentinel_verdicts": [],
      "shape_forms": {
        "%%%%-%%-%%&%%:%%": 582
      },
      "statistical_type": "text",
      "structural_role": "data",
      "words": {
        "max": 1,
        "mean": 1.0,
        "min": 1
      }
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
        "914e774533dd87b6e62585795bb8a33e890525bdcb765aed549d700bb3ad5762",
        "ea7bd92ecaae81864df5490add4f3ed9dbf18b4854ac7cfd5c00189f1c82cce9",
        "c3756af9b88dcba6ab9ab368502d1a7da177e6f7a015c89886fa6b18afd62e6a",
        (0, 0),
    ),
    "moved-zone": (
        r"""{
  "columns": [
    {
      "detection_evidence": "none of the 600 values is written as a number, 582 read as dates written as 2024-03-17 14:05:00, and there are 584 different values where a set of categories may have at most 60 in a table of 600 rows",
      "length": {
        "max": 24,
        "mean": 21.55,
        "min": 7,
        "p50": 20.0
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
      "n_code_alphabet": 18,
      "n_contradictory": 0,
      "n_distinct": 584,
      "n_distinct_by_occurrences": {
        "1": 582,
        "9": 2
      },
      "n_distinct_folded": 584,
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
      "remarks": [
        "synthtwin could not settle what this column holds, so none of its values is published. Here is why: none of the 600 values is written as a number and 582 read as dates written as 2024-03-17 14:05:00; a column is described as numbers, or as dates, only when at least 594 of them read that way. It holds 584 different values, where a set of categories may hold at most 60. Describing it from the part that does read would publish an average, a spread and points along a range that the rest of the column contradicts, so synthtwin describes it as free text and publishes no value of it at all. If these are measurements written with a currency sign, a per-cent sign, a unit such as mg, or a clock time, write them as plain numbers -- one column for the number, and the unit in the column name -- and run the command again. Fewer than 11 of its values are numbers wearing one shared piece of text, which is the reading that came closest",
        "nearly every value in this column is different, some are shared with another row, and none of the forms synthtwin can read fits them. synthtwin did NOT assume they are record numbers: it cannot tell from the values alone whether these are record numbers or measurements written in a form it does not read yet, and a wrong guess would throw away the whole distribution. Nothing from this column is published either way -- no value of it, and no distribution. If these ARE record numbers, run the command again with --identifier NAME, where NAME is this column's name, and the profile will say so. If they are measurements written with a currency sign, a per-cent sign, a unit such as mg, or a clock time, write them as plain numbers -- one column for the number, and the unit in the column name -- and their distribution will be described. Do not use --identifier on a measurement: it withholds the column entirely"
      ],
      "role": "free_text",
      "sentinel_verdicts": [],
      "shape_forms": {
        "%%%%-%%-%%@%%:%%:%%.%%%@": 291,
        "%%%%-%%-%%@%%:%%:%%@": 291
      },
      "statistical_type": "text",
      "structural_role": "data",
      "words": {
        "max": 1,
        "mean": 1.0,
        "min": 1
      }
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
        "ba1da5cbe5320cd3b12a048b6d055142dbe8b92bd4e531b262db9e48db3dcb10",
        "08ef60a9fc7dd436f732ce6b4d8069d1e8029ffdfac072b3ab86a069a18ac812",
        "2823a51587e53769c3d4f75fc6112b31088a75ef2b3f603eb7b68e24798bf127",
        (3, 0),
    ),
}
