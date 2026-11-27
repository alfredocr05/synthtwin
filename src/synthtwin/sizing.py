"""What a run needs, read from the table's size before any hour of work (lane SCALE).

WHY THIS MODULE EXISTS. A table of tens of millions of rows takes hours
to describe and, held as synthtwin holds it today, more memory than an
ordinary computer has. A run that starts anyway either fails after hours
-- out of memory, the computer swapping to a standstill -- or finishes
on a computer nobody could use meanwhile. So before any hour of work the
command weighs what this table will need against this computer's
installed memory (`computer.installed_memory`) and says it in plain
words; where the memory cannot hold the run, it STOPS before starting
and says why and what to do. It never quietly does less work to fit:
nothing here changes what a run describes, builds or checks.

WHAT IS PREDICTED. For each step a person runs -- describing the table
(`profile`, one round; a later round of answers takes about as long
again, its relations fit kept: `answered_round_of`), building the twin
(`generate`), checking it (`validate`) and the five twin-versus-real
checks -- the seconds and the peak memory, from the table's rows and
columns:

- seconds: a fixed part, and a part a cell (a row of a column) taken at
  the LARGEST size measured, grown past it by the growth measured between
  the largest sizes (`Step.growth`), so a step that grows faster than its
  rows is predicted to keep doing so, and grown with the columns by the
  power measured from 50 to 150 columns (`Step.column_power`: a wider
  table's cell costs more, its columns being read against one another);
  and, for the description, the relations fit's part, a part a fitted row
  (at most `FIT_SAMPLE_ROWS`, the fit's own sample) a cube of the columns:
  MEASURED, the fit grew as the columns to the power 3.2 from 50 to 150
  (every column screened against every other, and each label target's
  design widening with its parents' levels);
- peak memory: a fixed part and a part a column, beside the larger of a
  part a cell and, for the description, the fit's part a fitted row a
  column (the two peaks fall at different moments of the step), and,
  for a step whose peak a cell costs more at middling sizes than at the
  largest (validate and the checks read a whole table of text until the
  reader's own bound reads it in groups of columns; the twin's columns
  are worked on whole beside the finished ones), that part, capped
  (`Step.whole_mebibytes_most`; MEASURED: about 40 to 60 bytes a cell at
  100,000 to 200,000 rows, falling to 20 to 30 at 2,000,000); with
  `MEMORY_MARGIN_PERCENT` more.

The constants are measured on the lane's laptop (an Apple M4, one
process a step, the invented dense table of
`tools/measurements/kpi_inside_scale.py` from 20,000 to 2,000,000 rows
at 50 columns and at 150 columns at 20,000 rows; lane SCALE's report
gives every point) and written beside each. Past the sizes measured the
figures are EXTRAPOLATIONS, wider ones the more so, and the words say
"expected", never "measured". A computer whose one
core is slower takes proportionally longer (a typical office or virtual
Windows desktop is about one and a half to two and a half times slower a
core: an assumption, not measured here), which the words say.

WHAT IS NOT PREDICTED. A workbook's or another system's file's size on
disk does not say how large its table is, so `reading.glance` gives
nothing for one and no check is made before it is read. The figures are
for the shipped route (the inside record on); they hold no reading of
how many people the table holds or of its columns' kinds, which move
both figures by a factor the measurements bound but do not fix: the
memory is therefore taken at the measured peak with a margin, the side
the check errs on.

THE LIMIT. A step whose predicted peak passes `BUDGET_SHARE_NUMERATOR`
/ `BUDGET_SHARE_DENOMINATOR` of the installed memory is over this
computer's limit (the rest is for the system and the programs beside
it). Where the memory cannot be read (Windows: `computer.installed_memory`
says None), no limit is decided; the words give the need and the person
compares it.

Guarantees: every function is a fixed function of its arguments; no
file, no clock, no network, no process. Raises TypeError for a row or
column count that is not a whole number of nought or more.
"""

import dataclasses

# The measured size every part a cell is taken at: the largest table the
# proof runs described end to end (2,000,000 rows by 50 columns).
MEASURED_ROWS = 2_000_000
MEASURED_COLUMNS = 50

# The relations fit's sample, its rows at most (`inside_relations.SAMPLE_CAP`,
# repeated here so this module imports nothing).
FIT_SAMPLE_ROWS = 200_000

# The share of the installed memory one step may take before the check
# calls the run over this computer's limit: the rest is the system's and
# the other programs'.
BUDGET_SHARE_NUMERATOR = 3
BUDGET_SHARE_DENOMINATOR = 4

# What is added to each predicted peak: the peaks measured move with the
# table's kinds of columns and with what else the computer holds.
MEMORY_MARGIN_PERCENT = 25

MEBIBYTE = 1024 * 1024


@dataclasses.dataclass(frozen=True)
class Step:
    """One step's measured cost: its seconds and its peak memory, a fixed part and the parts that grow.

    ``seconds_fixed`` and ``mebibytes_fixed`` are what the step takes on a
    table of no rows; ``microseconds_a_cell`` and ``bytes_a_cell`` its part
    a cell at `MEASURED_ROWS` rows and `MEASURED_COLUMNS` columns;
    ``growth`` the exponent by which its part a cell grows with the rows
    past `MEASURED_ROWS` (0 where it grew as the rows did);
    ``column_power`` the exponent by which its part a cell's seconds grow
    with the columns; ``mebibytes_a_column`` its memory a column;
    ``fit_microseconds`` the relations fit's seconds, in millionths, a
    fitted row a cube of the columns, and ``fit_bytes`` its memory a fitted
    row a column (both nought for a step that fits nothing);
    ``whole_bytes_a_cell`` the memory a cell of a table read whole holds as
    text, and ``whole_mebibytes_most`` the most it holds read in groups.
    """

    name: str
    words: str
    seconds_fixed: float
    microseconds_a_cell: float
    growth: float
    mebibytes_fixed: float
    bytes_a_cell: float
    column_power: float = 0.0
    mebibytes_a_column: float = 0.0
    fit_microseconds: float = 0.0
    fit_bytes: float = 0.0
    whole_bytes_a_cell: float = 0.0
    whole_mebibytes_most: float = 0.0


# THE STEPS, MEASURED (lane SCALE's ladder and the 2,000,000 x 50 proof
# run of lane SPEED-2M, report 2; each constant is the lane report's):
STEPS = (
    Step("profile", "describing the table (one round of questions)", 60.0, 120.0, 0.08, 250.0, 24.0,
         column_power=0.45, mebibytes_a_column=1.2, fit_microseconds=0.04, fit_bytes=150.0),
    Step("generate", "building the twin", 10.0, 125.0, 0.28, 70.0, 39.0, column_power=0.15, mebibytes_a_column=0.75,
         whole_bytes_a_cell=40.0, whole_mebibytes_most=600.0),
    Step("validate", "checking the twin", 10.0, 90.0, 0.05, 145.0, 27.0, column_power=0.30, mebibytes_a_column=1.4,
         whole_bytes_a_cell=60.0, whole_mebibytes_most=600.0),
    Step("checks", "the five twin-versus-real checks", 10.0, 11.5, 0.15, 150.0, 21.0, column_power=0.30,
         mebibytes_a_column=1.0, whole_bytes_a_cell=60.0, whole_mebibytes_most=600.0),
)


@dataclasses.dataclass(frozen=True)
class Need:
    """What one step needs: its predicted seconds and peak memory in bytes."""

    step: Step
    seconds: float
    peak_bytes: int


def _whole(value: object, what: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise TypeError(f"{what} is a whole number of nought or more")
    return value


def need_of(step: Step, rows: int, columns: int, fitted: bool = True) -> Need:
    """``step``'s predicted seconds and peak memory on a table of ``rows`` by ``columns``.

    The part a cell is the measured one up to `MEASURED_ROWS` rows and
    grows by ``step.growth`` past it; the relations fit's part is counted
    where ``fitted`` (False: a round of answers whose fits are kept); the
    peak carries `MEMORY_MARGIN_PERCENT` more. Raises TypeError for a
    count that is not a whole number of nought or more.
    """
    rows = _whole(rows, "a row count")
    columns = _whole(columns, "a column count")
    cells = float(rows) * float(columns)
    sampled = float(min(rows, FIT_SAMPLE_ROWS))
    grown = 1.0
    if rows > MEASURED_ROWS and step.growth > 0.0:
        grown = (float(rows) / float(MEASURED_ROWS)) ** step.growth
    if columns > MEASURED_COLUMNS and step.column_power > 0.0:
        grown = grown * (float(columns) / float(MEASURED_COLUMNS)) ** step.column_power
    seconds = step.seconds_fixed + cells * step.microseconds_a_cell * grown / 1_000_000.0
    if fitted:
        width = float(columns)
        seconds = seconds + sampled * width * width * width * step.fit_microseconds / 1_000_000.0
    held = max(cells * step.bytes_a_cell, sampled * float(columns) * step.fit_bytes)
    held = held + min(cells * step.whole_bytes_a_cell, step.whole_mebibytes_most * MEBIBYTE)
    fixed = (step.mebibytes_fixed + step.mebibytes_a_column * float(columns)) * MEBIBYTE
    peak = (fixed + held) * (100 + MEMORY_MARGIN_PERCENT) / 100.0
    return Need(step, seconds, int(peak))


def needs_of(rows: int, columns: int) -> "tuple[Need, ...]":
    """Every step's need on a table of ``rows`` by ``columns``, in the order a person runs them."""
    return tuple(need_of(step, rows, columns) for step in STEPS)


def answered_round_of(rows: int, columns: int) -> Need:
    """A later round of the description (its answers), its relations fit kept: the description's need less the fit's time."""
    return need_of(STEPS[0], rows, columns, fitted=False)


def budget_of(installed: "int | None") -> "int | None":
    """The memory one step may take on a computer of ``installed`` bytes, or None where the memory was not read."""
    if installed is None:
        return None
    return _whole(installed, "an installed memory") * BUDGET_SHARE_NUMERATOR // BUDGET_SHARE_DENOMINATOR


def first_over(needs: "tuple[Need, ...]", installed: "int | None") -> "Need | None":
    """The step of the largest peak among those passing this computer's budget (`budget_of`), or None (none does, or the memory was not read).

    The largest, so the words name the memory the whole run needs, not the
    first step's alone; the first such step in ``needs``' order on a tie.
    """
    budget = budget_of(installed)
    if budget is None:
        return None
    worst: "Need | None" = None
    for one in needs:
        if one.peak_bytes > budget and (worst is None or one.peak_bytes > worst.peak_bytes):
            worst = one
    return worst


def gigabytes(size: int) -> str:
    """A size in bytes as a person reads a memory: '3.4 GB', '0.6 GB' (binary gigabytes, as a computer's memory is sold)."""
    return f"{_whole(size, 'a size') / (1024.0 * MEBIBYTE):.1f} GB"


def hours(seconds: float) -> str:
    """A duration as a person reads it: 'under a minute', 'about 25 minutes', 'about 3.5 hours'."""
    if seconds < 60.0:
        return "under a minute"
    if seconds < 3600.0:
        return f"about {int(round(seconds / 60.0))} minutes"
    return f"about {seconds / 3600.0:.1f} hours"
