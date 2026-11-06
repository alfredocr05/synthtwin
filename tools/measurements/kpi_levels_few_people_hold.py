"""K-HZ-19: levels few people hold, at 600 and 20,000 rows (lane PL, plan P4-D453).

Runs the invented form of `tests/levels_few_people_hold.py` end to end, the way
the zoo runs its catalogue (profile, the general answers round by round,
generate, validate), at each size, and reads what P4-D453 promises:

- `levels_shown`: levels 1 to 10 people hold named in a description, a summary,
  a report or a questions file (target 0);
- `counts_named`: a count of 1 to 10 printed for a column too few people fill
  (target 0);
- `kept_filter_faults`, `flag_blank_share_faults`: == and isin on the kept
  levels, and a flag's blank share, past `health_zoo.SHARE_TOLERANCE` (target 0);
- `dtype_mismatches`, `thin_words_read_as_numbers`: pandas' reading of the twin
  against the real's (target 0): a column of words too few people fill stays a
  column of words (`thin_word_str_runs` 1);
- `kept_share_gap_max`, `isin_gap_max`, `blank_share_gap_max`,
  `pool_share_gap_max`: the largest gap, real to twin, of a kept level's `==`,
  the kept levels' `isin`, a column's blank share and a pool's share (at most
  0.001);
- `identifying_levels_published` (target 0), and the same columns under names
  that say nothing (`neutral_identifier_spellings_published`,
  `neutral_identifier_columns_not_asked`, target 0);
- at 20,000 rows, one row a person: `rows_boundary_faults` (10 rows counted
  absent, 11 described, a declared record number of 5 counted absent) and
  `declared_identifier_counts_printed` (target 0); a logistic model of the
  pooled 0/1 indicator fitted on the twin (`indicator_model_refused` 0) and its
  mean (`indicator_mean_gap`, at most 0.001);
- `columns_still_held`, by name with its reason; recorded apart:
  `stand_in_cells`, the price, the cells a reader could take for a level;
  `stand_ins_equal_a_real_value`, a stand-in that a function of the published
  levels makes equal to a real value (the orchestrator's LANE PL RULINGS 2 (1));
  each pooled number column's mean, real and twin (`mean_<column>_real`,
  `mean_<column>_twin`); the thin word's twin cells and people.

Every count is linear in the cells. The times are the product's own, apart from
the counting. About four minutes on the reference machine.

    .venv/bin/python tools/measurements/kpi_levels_few_people_hold.py --kpi
"""

import pathlib
import sys
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
import health_zoo  # noqa: E402
import kpi_rules  # noqa: E402
import levels_few_people_hold as form  # noqa: E402

kpi_rules.guard_this_tree()

COUNTS = (
    "levels_shown", "counts_named", "kept_filter_faults", "flag_blank_share_faults", "dtype_mismatches",
    "stand_ins_equal_a_real_value", "identifying_levels_published", "validate_misses", "leaks",
    "thin_words_read_as_numbers", "stand_in_cells", "birth_dates_equal_by_chance", "birth_date_points_at_a_grain",
    "kept_share_gap_max", "isin_gap_max", "blank_share_gap_max", "pool_share_gap_max",
    "thin_word_str_runs", "thin_word_twin_cells", "thin_word_twin_people",
)


def main() -> None:
    value: "dict[str, object]" = {}
    said: "list[str]" = []
    with tempfile.TemporaryDirectory(prefix="synthtwin-levels-") as scratch:
        for rows in (health_zoo.SMOKE_ROWS, health_zoo.KPI_ROWS):
            started = time.perf_counter()
            folder = pathlib.Path(scratch) / f"run-{rows}"
            found = form.measure(rows, form.SEED, folder)
            for key in COUNTS:
                value[f"{key}_{rows}_rows"] = found[key]
            for name, pair in sorted(found["pooled_means"].items()):  # type: ignore[attr-defined]
                value[f"mean_{name}_real_{rows}_rows"] = pair[0]
                value[f"mean_{name}_twin_{rows}_rows"] = pair[1]
            held = found["columns_still_held"]
            value[f"columns_still_held_{rows}_rows"] = len(held)  # type: ignore[arg-type]
            value[f"steps_failing_{rows}_rows"] = sum(1 for code in found["steps"].values() if code)  # type: ignore[attr-defined]
            neutral = form.neutral_identifiers(rows, pathlib.Path(scratch) / f"neutral-{rows}")
            value[f"neutral_identifier_spellings_published_{rows}_rows"] = neutral["spellings_published"]
            value[f"neutral_identifier_columns_not_asked_{rows}_rows"] = neutral["not_asked"]
            if rows >= health_zoo.KPI_ROWS:
                boundary = form.rows_boundary(rows, pathlib.Path(scratch) / f"rows-{rows}")
                value[f"rows_boundary_faults_{rows}_rows"] = boundary["faults"]
                value[f"declared_identifier_counts_printed_{rows}_rows"] = boundary["counts_printed"]
                fitted = form.indicator_model(folder)
                value[f"indicator_model_refused_{rows}_rows"] = fitted["refused"]
                value[f"indicator_mean_gap_{rows}_rows"] = fitted["mean_gap"]
            said += [f"{rows} rows: held {held}, steps {found['steps']}, {round(time.perf_counter() - started, 1)} s"]
    kpi_rules.emit("K-HZ-19", value, "; ".join(said))


if __name__ == "__main__":
    main()
