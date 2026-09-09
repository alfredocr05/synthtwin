"""How often do two strata round onto one spelling? (R-P4-56)

Real CSV, real reader, producer, loader, generator. For each column:
how many strata the layout builds, how many DIFFERENT numbers those
strata hold, and how many different spellings come out once the
published fraction width is applied. Also whether the twin then writes
a cell wearing a leading zero no source cell wore.
"""
import pathlib
import random
import sys
import tempfile
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
import fixtures
from synthtwin import generation, profile, taxonomy, contract, reading

grab = {}
inner = generation._number_cells
def spy(column, facts, layout, values):
    grab["values"] = list(values)
    grab["width"] = dict(facts.fraction_widths)
    return inner(column, facts, layout, values)
generation._number_cells = spy

def build(folder, stem, rows):
    fixtures.write(folder, f"{stem}.csv", "reading\n" + "\n".join(rows) + "\n")
    table = reading.read_table(str(folder / f"{stem}.csv"),
                               first_row=reading.FIRST_ROW_AUTOMATIC)
    doc = profile.build_document(table, taxonomy.Settings(), [])
    return doc, contract.load_profile(
        str(fixtures.write_profile(folder, f"{stem}-p.json", doc)))

# Columns on a fixed decimal grid, which is what a code-like or a
# rounded measurement column looks like: one or two figures after the
# point, values spaced far wider than that grid.
# A CONTROL FAMILY BESIDE THE ONE UNDER TEST. The grid columns below
# are chosen because that is the shape the collision bites; a rate
# measured over them alone is a rate for them alone. So half the corpus
# is ordinary continuous readings at full precision, where no fraction
# width is pinned and the collision has nothing to round together.
random.seed(20260830)
shapes = []
control = []
for _trial in range(80):
    control.append([repr(random.uniform(0, 1000))
                    for _each in range(random.choice([120, 240]))])
for _trial in range(80):
    figures = random.choice([1, 1, 2])
    step = random.choice([1, 1.1, 0.5, 2.5, 10])
    start = random.choice([0.0, 250.0, 1000.0, -50.0])
    count = random.choice([40, 60, 99, 150])
    grid = [round(start + step * n, figures) for n in range(count)]
    rows = [f"%.{figures}f" % grid[n % len(grid)]
            for n in range(random.choice([120, 240, 300]))]
    shapes.append(rows)

FAMILIES = (("grid", shapes), ("ordinary", control))

collided = odd_cells = built = 0
misses = []
with tempfile.TemporaryDirectory() as folder:
    home = pathlib.Path(folder)
    for family, corpus in FAMILIES:
     built = collided = odd_cells = 0
     misses = []
     for index, rows in enumerate(corpus):
         try:
             doc, loaded = build(home, f"c{index}", rows)
         except Exception:
             continue
         built += 1
         column = doc["columns"][0]
         twin = generation.generate(loaded, 7)
         vals = grab["values"]
         width = grab["width"]
         if not width:
             continue
         figures = max(int(key) for key in width)
         texts = [("%." + str(figures) + "f") % value for value in vals]
         if len(set(texts)) < len(set(vals)):
             collided += 1
             named = [d for d in twin.deviations
                      if getattr(d, "fact", "") == "n_distinct_values"]
             cells = [c for c in twin.columns[0] if c]
             widest = max(len(c.split(".")[0].lstrip("-")) for c in cells)
             source = max(len(r.split(".")[0].lstrip("-")) for r in rows)
             if widest > source:
                 odd_cells += 1
             misses.append((index, len(set(vals)), len(set(texts)),
                            bool(named), widest, source))

     print("=== family:", family, "===")
     print(" columns built:", built)
     print(" two strata round onto one spelling on:", collided)
     print("   and of those, the twin writes a wider integer part on:", odd_cells)
     for row in misses[:6]:
      print("    column %d: %d stratum values -> %d spellings, "
           "value miss reported=%s, widest written %d vs source %d" % row)
