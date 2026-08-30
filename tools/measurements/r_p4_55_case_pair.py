"""How wide is R-P4-55: how often did the packing charge the wrong ceiling?

Real CSV, real reader, real profiler, real loader, real generator. The
twin's RAW and FOLDED spelling counts are compared with the published
ones, with the guard as it shipped and as it is now.
"""
import pathlib, random, sys, tempfile
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
import fixtures
from synthtwin import generation, profile, taxonomy, contract, parsing, reading

OLD = generation._style_strata
def shipped(quotas, layout, values, whole_column, wanted, raw, styles):
    """The guard as it shipped: the RAW supply against the FOLDED ceiling."""
    return OLD(quotas, layout, values, whole_column, wanted, wanted, styles)

def counts(cells):
    live = [c for c in cells if c != ""]
    return len(set(live)), len(set(parsing.folded(c) for c in live))

def build(folder, stem, rows):
    text = "column_1\n" + "\n".join(rows) + "\n"
    path = fixtures.write(folder, f"{stem}.csv", text)
    table = reading.read_table(str(path), first_row=reading.FIRST_ROW_AUTOMATIC)
    document = profile.build_document(table, taxonomy.Settings(), [])
    loaded = contract.load_profile(
        str(fixtures.write_profile(folder, f"{stem}-profile.json", document))
    )
    return loaded

# THE SOURCE HAS TO ASK FOR THE PAIR. `n_distinct` rises above
# `n_distinct_folded` only where the real column wrote one number two
# ways that fold together, and in a numeric column the only such pair
# is the exponent's own case. A corpus of lowercase spellings alone
# publishes the two counts equal, never demands a case pair, and so
# never reaches the branch at all -- which is what the first run of
# this script measured, and it measured nothing.
random.seed(20260830)
shapes = []
for _trial in range(70):
    n = random.choice([25, 40, 60, 120])
    lo, hi = random.choice([(-6, 2), (-3, 16), (0, 17), (-8, 8), (12, 17)])
    rows = [repr(random.uniform(1, 10) * (10.0 ** random.randint(lo, hi)))
            for _each in range(n)]
    for _each in range(random.randint(0, 6)):
        rows.append("1e+15")
    # and the same column with some of its exponents in upper case
    pairs = random.randint(1, 4)
    mixed = list(rows)
    for _each in range(pairs):
        place = random.randrange(len(mixed))
        if "e" in mixed[place]:
            mixed.append(mixed[place].replace("e", "E"))
    shapes.append(rows)
    shapes.append(mixed)

refused, differ, closer, further = [], 0, [], []
flagged = []
tried = 0
with tempfile.TemporaryDirectory() as folder:
    home = pathlib.Path(folder)
    for index, rows in enumerate(shapes):
        try:
            loaded = build(home, f"s{index}", rows)
        except Exception as exc:
            refused.append((index, type(exc).__name__, str(exc)[:90]))
            continue
        column = loaded.columns[0]
        published = (column.n_distinct, column.n_distinct_folded)
        flagged.append(column.n_distinct > column.n_distinct_folded)
        for seed in (0, 1, 2):
            tried = tried + 1
            generation._style_strata = OLD
            now = counts([r[0] for r in generation.generate(loaded, seed).rows])
            generation._style_strata = shipped
            was = counts([r[0] for r in generation.generate(loaded, seed).rows])
            generation._style_strata = OLD
            if now == was:
                continue
            differ = differ + 1
            miss_now = abs(now[0] - published[0]) + abs(now[1] - published[1])
            miss_was = abs(was[0] - published[0]) + abs(was[1] - published[1])
            if miss_now < miss_was:
                closer.append((index, seed, published, was, now))
            elif miss_now > miss_was:
                further.append((index, seed, published, was, now))

print("published raw>folded on:", sum(1 for f in flagged if f), "of", len(flagged))
print("shapes built:", len(shapes) - len(refused), "of", len(shapes),
      "  refused:", len(refused))
for r in refused[:4]:
    print("    refused:", r)
print("column-seeds tried:", tried)
print("the two guards disagree on:", differ)
print("  now CLOSER to the published counts:", len(closer))
print("  now FURTHER:", len(further))
for row in closer[:10]:
    print("    shape %d seed %d published(raw,folded)=%s shipped=%s now=%s" % row)
for row in further[:10]:
    print("    WORSE shape %d seed %d published=%s shipped=%s now=%s" % row)
