"""K-S3-17, K-S3-18, K-S3-20, K-S3-21, K-S3-22 and K-S3-50: what publishing every tail pair does, measured.

Plan P4-D375 publishes every numeric tail pair binary64 can hold; the
cost rule of P4-D353, which published a withheld pair only where
withholding it cost the twin its mean or spread, went with the
withholding. Five numbers say what the pairs buy and what they give
back, each over its own seeded battery and each through the real
producer, and -- where a twin is asked -- the real generator and checker:

* `K-S3-17` (the owner's accepted limit, answer 1): on five columns whose
  two tails are dense and whose interior the rungs chain, how many outer
  tail values the exact skew and kurtosis rebuild beside both published
  pairs (`complement_reader.union`);
* `K-S3-18` (answers 3 and 4): the published sides from whose pair a
  reader names at least one cell DIRECTLY with the producer's own lattice,
  and how many cells (`complement_reader.named_directly`);
* `K-S3-20`: at a floor of 36, every obligation the twins at seeds 0, 4 and
  9 MISS and leave WITHHELD, the blocks whose own window misses, the pairs
  the moments need, and the published pairs the checker cannot check;
* `K-S3-21` (answer 5): the outer values a reader names BY SUBTRACTION
  from the column's exact mean and spread beside a published pair
  (`complement_reader.by_subtraction`), and the columns it gives up on;
* `K-S3-22`: where no published pair keeps a moment, the moments the twins
  still miss, and how many blocks keep neither or one of them in their
  own windows;
* `K-S3-50`: how far twins write past the real column's own range, which
  no check sees because no end is published -- over `K-S3-20`'s 37 shapes
  at floors 11, 20, 36 and 50, the numeric twins holding a cell outside
  the real minimum and maximum and how far, as thousandths of the real
  span; and over the two date columns of landing 3b.0's tie-group
  witnesses, the twins writing a day outside the real first and last.

Every column is built from a fixed seed string at run time; nothing is
read from disk but the tree's own code.

    .venv/bin/python tools/measurements/kpi_cost_rule.py --kpi [--only K-S3-18,K-S3-21]
"""

import pathlib
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT))
import complement_reader as reader  # noqa: E402
import cost_rule_window as window  # noqa: E402
import kpi_rules  # noqa: E402
import kpi_shapes  # noqa: E402
import test_stage3_gate as gate  # noqa: E402
from synthtwin import parsing, validation  # noqa: E402

kpi_rules.guard_this_tree()

SEEDS = (0, 4, 9)


def _text(cells):
    return "value\n" + "\n".join(cells) + "\n"


def _described(home, name, cells, floor):
    """One column described at ``floor``."""
    return kpi_shapes.describe(home / f"{name}-f{floor}", name, _text(cells), floor)


def _paired(block):
    """The sides of a numeric block publishing their pair and listing no value."""
    tails = block.get("tails")
    if not isinstance(tails, dict):
        return []
    return [
        side
        for side in ("low", "high")
        if isinstance(tails.get(side), dict)
        and tails[side]["mean_distance"] is not None
        and not tails[side]["values"]
    ]


def _twins(described):
    """Every twin verdict at the three seeds, as (subcheck, verdict)."""
    found = []
    for seed in SEEDS:
        text = kpi_shapes.twin_text(described, seed)
        outcome = kpi_shapes.measure(described, text, f"twin-{seed}.csv")
        found += [(check.subcheck, check.verdict) for check in outcome.checks]
    return found


def skew_and_kurtosis(home):
    """K-S3-17: the union reader over five both-dense columns at a floor of eleven."""
    value = {"values_rebuilt": 0, "minimum_named": 0, "maximum_named": 0, "withheld_values_asked": 0, "shapes": 0}
    for seed in range(1, 6):
        values, cells = reader.both_dense(40, 11, seed)
        described = _described(home / "k317", f"both_W40_s{seed}", cells, 11)
        block = described.document["columns"][0]
        read = reader.union(block, values)
        n = block["n_used_in_statistics"]
        low_rows = parsing.tail_rows(n, block["tails"]["low"]["percent"], "low")
        high_rows = parsing.tail_rows(n, block["tails"]["high"]["percent"], "high")
        value["values_rebuilt"] += read["values_rebuilt"]
        value["minimum_named"] += int(read["minimum_named"])
        value["maximum_named"] += int(read["maximum_named"])
        value["withheld_values_asked"] += (low_rows - 1) + (high_rows - 1)
        value["shapes"] += 1
        print(f"K-S3-17 seed {seed}: {read}", flush=True)
    return value


def _k318_battery():
    for floor in (11, 36):
        for name, cells in gate.RECONSTRUCTIONS + gate.COST_SHAPES:
            yield name, cells, floor
        for name, _values, cells in reader.attack_battery(floor):
            yield name, cells, floor
        for seed in range(10):
            yield f"pareto0_400_s{seed}", reader.pareto(400, seed), floor
        for far, rows in ((4000, 400), (2000, 150), (2000, 400)):
            yield f"neg{far}_{rows}", reader.far_low(far, rows), floor


def published_pairs(home):
    """K-S3-18: the published sides a reader names a cell from, and how many cells."""
    value = {"sides_naming_a_value": 0, "values_named_directly": 0, "shapes": 0}
    for name, cells, floor in _k318_battery():
        described = _described(home / "k318", name, cells, floor)
        value["shapes"] += 1
        block = described.document["columns"][0]
        try:
            values = sorted(float(cell) for cell in cells)
        except ValueError:
            values = None
        named = {}
        if values is not None:
            for side in _paired(block):
                read = reader.named_directly(block, side, values)
                named[side] = read
                value["values_named_directly"] += read["values"]
                value["sides_naming_a_value"] += int(read["values"] > 0)
        print(f"K-S3-18 {name} at {floor}: {named}", flush=True)
    return value


def _k320_battery():
    for kind in reader.KINDS:
        for rows in reader.SIZES:
            yield f"{kind}_{rows}", reader.ordinary(kind, rows)
    for kind in reader.DISTINCT_KINDS:
        for rows in reader.SIZES:
            yield f"{kind}_{rows}", reader.ordinary(kind, rows)
    for name, cells in gate.RECONSTRUCTIONS + gate.COST_SHAPES:
        # AT THIS FLOOR THE FAR NEGATIVE VALUE KEEPS ITS MEAN AND NOT ITS
        # SPREAD: no pair keeps both, which is K-S3-22's.
        if name != "far_negative_beside_a_run":
            yield name, cells
    yield "exp3d_150_s1", reader.shape("exp3d", 150, 1)
    yield "bigint_d_400_s1", reader.shape("bigint_d", 400, 1)


def floor_36(home):
    """K-S3-20: STATE's floor-36 battery, every obligation MISSED and WITHHELD."""
    floor = 36
    value = {
        "twin_misses": 0,
        "twin_withheld": 0,
        "blocks_missing_own_window": 0,
        "pairs_the_moments_need": 0,
        "pairs_the_checker_cannot_check": 0,
        "shapes": 0,
    }
    for name, cells in _k320_battery():
        described = _described(home / "k320", name, cells, floor)
        value["shapes"] += 1
        block = described.document["columns"][0]
        ruled = _paired(block)
        tails = block.get("tails")
        need = []
        short = False
        if isinstance(tails, dict) and isinstance(tails.get("low"), dict):
            for side in ("low", "high"):
                one = tails[side]
                if one["mean_distance"] is None or one["values"]:
                    continue
                if window.costs(window.withheld(block, (side,)), floor):
                    need += [side]
            short = window.costs(block, floor)
        verdicts = _twins(described)
        misses = len([1 for _subcheck, verdict in verdicts if verdict == validation.MISSED])
        held_back = len([1 for _subcheck, verdict in verdicts if verdict == validation.WITHHELD])
        unchecked = {
            side
            for side in ruled
            for subcheck, verdict in verdicts
            if verdict == validation.WITHHELD and subcheck.endswith(f"tails.{side}.mean_distance")
        }
        value["pairs_the_moments_need"] += len(need)
        value["blocks_missing_own_window"] += int(short)
        value["twin_misses"] += misses
        value["twin_withheld"] += held_back
        value["pairs_the_checker_cannot_check"] += len(unchecked)
        print(
            f"K-S3-20 {name}: need {need} paired {sorted(ruled)} short {short} "
            f"misses {misses} withheld {held_back} unchecked {sorted(unchecked)}",
            flush=True,
        )
    return value


def _k321_battery():
    for floor in (11, 36):
        for name, values, cells in reader.attack_columns(floor):
            yield name, values, cells, floor
        cells = [f"{value:05}" for value in range(1, 400)] + ["12345"]
        yield "padded_399_beside_one_far", sorted(int(cell) for cell in cells), cells, floor
        for far in (4000, 2000):
            for rows in (150, 400):
                cells = reader.far_low(far, rows)
                yield f"neg{far}_{rows}", sorted(int(cell) for cell in cells), cells, floor


def by_subtraction(home):
    """K-S3-21: what the exact mean and spread give back of the other tail beside a published pair."""
    value = {"values_by_subtraction": 0, "columns_the_reader_gives_up_on": 0, "shapes": 0}
    for name, values, cells, floor in _k321_battery():
        described = _described(home / "k321", name, cells, floor)
        value["shapes"] += 1
        read = reader.by_subtraction(described.document["columns"][0], values)
        value["values_by_subtraction"] += read["values_rebuilt"]
        if read["complement"].startswith("interior-too-free"):
            value["columns_the_reader_gives_up_on"] += 1
        print(f"K-S3-21 {name} at {floor}: {read}", flush=True)
    return value


def _k322_battery():
    for floor in (11, 36):
        for kind in ("pad99999", "cfh99999"):
            for rows in (150, 400):
                yield f"{kind}_{rows}", reader.shape(kind, rows, 1), floor
    for floor in (20, 36, 50):
        yield "par20d_150_s2", reader.shape("par20d", 150, 2), floor
    for floor in (36, 50):
        for seed in range(10):
            yield f"pareto0_400_s{seed}", reader.pareto(400, seed), floor
    for rows in (40, 60):
        yield f"small_lnd_{rows}", reader.small_distinct(rows), 36
    for rows in (100, 150):
        yield f"neg4000_{rows}", reader.far_low(4000, rows), 36
    yield "pad50000_150", reader.shape("pad50000", 150, 1), 36


def residual(home):
    """K-S3-22: the moments no published pair keeps, and how many each block's own windows keep."""
    value = {
        "moment_misses": 0,
        "blocks_no_candidate_keeps_either": 0,
        "blocks_one_moment_kept": 0,
        "blocks_with_no_pair_to_publish": 0,
        "shapes": 0,
    }
    for name, cells, floor in _k322_battery():
        described = _described(home / "k322", name, cells, floor)
        value["shapes"] += 1
        block = described.document["columns"][0]
        kept = None
        tails = block.get("tails")
        if isinstance(tails, dict) and isinstance(tails.get("low"), dict):
            # THE BLOCK'S OWN G12.3 WINDOWS, as the cost rule asked them of
            # the block it published (`cost_rule_window`).
            kept = 2 - len(window.missed(block, floor))
            if kept == 0:
                value["blocks_no_candidate_keeps_either"] += 1
            elif kept == 1:
                value["blocks_one_moment_kept"] += 1
        if isinstance(tails, dict) and not isinstance(tails.get("low"), dict):
            value["blocks_with_no_pair_to_publish"] += 1
        misses = len([
            1 for subcheck, verdict in _twins(described)
            if verdict == validation.MISSED and subcheck.endswith(("moments.mean", "moments.std"))
        ])
        value["moment_misses"] += misses
        print(f"K-S3-22 {name} at {floor}: kept {kept} moment misses {misses}", flush=True)
    return value


def _range_overshoot(real, twin):
    """Thousandths of the real span the twin's furthest cell stands past the real range, or None."""
    low, high = min(real), max(real)
    span = high - low
    beyond = max([low - one for one in twin if one < low] + [one - high for one in twin if one > high] + [0.0])
    if beyond <= 0.0 or span <= 0.0:
        return None
    return int(round(1000.0 * beyond / span))


def _numbers_of(text):
    found = []
    for line in text.split("\n")[1:]:
        number = parsing.parse_number(line) if line else None
        if number is not None:
            found += [number]
    return found


# THE TWO DATE COLUMNS (tests/test_stage3b_gate.py): every_day_group's 105
# dates over 22 days from 2024-05-06, and the same with 2024-05-12 declared
# missing and twelve more cells written that way.
_TIE_COUNTS = (5, 4, 1, 6, 9, 2, 4, 7, 6, 2, 7, 7, 5, 5, 3, 2, 9, 7, 1, 1, 11, 1)


def out_of_range(home):
    """K-S3-50: twins past the real range, numeric over K-S3-20's battery, and the two date columns."""
    import datetime

    import fixtures
    from synthtwin import contract, profile, reading, taxonomy

    value = {
        "numeric_twins": 0,
        "numeric_twins_out_of_range": 0,
        "median_overshoot_permille": 0,
        "worst_overshoot_permille": 0,
        "date_twins": 0,
        "date_twins_out_of_range": 0,
        "date_days_out_most": 0,
    }
    found = []
    for floor in (11, 20, 36, 50):
        for name, cells in _k320_battery():
            real = _numbers_of(_text(cells))
            described = _described(home / "k350", name, cells, floor)
            if described.document["columns"][0]["role"] not in ("count", "continuous"):
                continue
            for seed in SEEDS:
                value["numeric_twins"] += 1
                past = _range_overshoot(real, _numbers_of(kpi_shapes.twin_text(described, seed)))
                if past is not None:
                    value["numeric_twins_out_of_range"] += 1
                    found += [past]
    found.sort()
    if found:
        value["median_overshoot_permille"] = found[len(found) // 2]
        value["worst_overshoot_permille"] = found[len(found) - 1]
    first = datetime.date(2024, 5, 6)
    days = []
    for step in range(len(_TIE_COUNTS)):
        days += [(first + datetime.timedelta(days=step)).isoformat()] * _TIE_COUNTS[step]
    for absent in (False, True):
        cells = days + (["2024-05-12"] * 12 if absent else [])
        folder = home / f"k350-dates-{absent}"
        folder.mkdir(parents=True, exist_ok=True)
        table = fixtures.write(folder, "dates.csv", "seen_on\n" + "".join(f"{cell}\n" for cell in cells))
        settings = taxonomy.Settings(small_cell_floor=11, declared_missing_values=("2024-05-12",) if absent else ())
        document = profile.build_document(reading.read_table(str(table), small_cell_floor=11), settings, [], [], [])
        written = fixtures.write_profile(folder, "dates-profile.json", document)
        described = kpi_shapes.Described(folder, table, document, contract.load_profile(str(written)))
        real = sorted(set(days) - ({"2024-05-12"} if absent else set()))
        for seed in (0, 1, 2, 3, 4):
            value["date_twins"] += 1
            held = [line for line in kpi_shapes.twin_text(described, seed).split("\n")[1:] if line and line != "2024-05-12"]
            out = [one for one in held if one < real[0] or one > real[len(real) - 1]]
            if out:
                value["date_twins_out_of_range"] += 1
                worst = max(
                    max((datetime.date.fromisoformat(real[0]) - datetime.date.fromisoformat(one)).days for one in out),
                    max((datetime.date.fromisoformat(one) - datetime.date.fromisoformat(real[len(real) - 1])).days for one in out),
                )
                value["date_days_out_most"] = max(value["date_days_out_most"], worst)
    print(f"K-S3-50 overshoots (thousandths of the span): {found}", flush=True)
    return value


MEASUREMENTS = (
    ("K-S3-17", skew_and_kurtosis),
    ("K-S3-18", published_pairs),
    ("K-S3-20", floor_36),
    ("K-S3-21", by_subtraction),
    ("K-S3-22", residual),
    ("K-S3-50", out_of_range),
)


def main():
    """Every measurement, or those `--only K-S3-18,K-S3-21` names."""
    wanted = None
    if "--only" in sys.argv:
        wanted = sys.argv[sys.argv.index("--only") + 1].split(",")
    with tempfile.TemporaryDirectory() as folder:
        home = pathlib.Path(folder)
        for entry_id, measure in MEASUREMENTS:
            if wanted is None or entry_id in wanted:
                kpi_rules.emit(entry_id, measure(home))


if __name__ == "__main__":
    main()
