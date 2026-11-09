"""The analysis families' STRUCTURAL GRADES, as both reports print them (contract 4.6b.8; lane ST, plan P4-D458).

NOT IN FORCE. Invariant S12 stands: only a description loaded with the
chain's switch reaches these lines, and no shipped command loads one.

A structural grade is a function of the description alone: it is what
the people the twin is shared with see. The SHARED report (the twin's
report, `rendering`) prints one line for each family F1 to F10 in these
grades, and one line for each pair with the word the description's
`words` holds, never recomputed; the PRIVATE report (`chain_selftest`)
prints the same grade beside the self-test's judged word. The grades are
the constants 4.6b.8 states, worded as BC-ARCH 4.2's example lines: `E`
exact at the published bands, `P` pinned on the code scale where the
description's `words` reads `pinned`, `A` approximate (as the chain
implies), `N` not carried. No line here holds a value, a rate, a gap, a
sample size or a reason a pair was left out. Standard library only; no
I/O of any kind.
"""

HEADING = "What you can analyse on this twin"

FAMILIES = (
    ("F1", "subgroup rates and cross-tables"),
    ("F2", "correlations"),
    ("F3", "linear regression"),
    ("F4", "logistic regression"),
    ("F5", "count regression"),
    ("F6", "time to event"),
    ("F7", "several rows per person"),
    ("F8", "trained models"),
    ("F9", "missing data by other columns"),
    ("F10", "code run unchanged"),
)

PAIRS_HEADING = (
    "Pairs of columns, each with its word in the description (exact: at the published bands of the one family "
    "that holds both; pinned: a published correlation; implied: as the chain implies):"
)

ONCE_LINE = (
    "Describe each table once, on one installation, under one name, with the same columns under the same "
    "names, and give a different table its own name."
)

MOVED = "moved in this twin"

_APPROXIMATE = "A (approximate: as the chain implies)"

# THE ONE FAMILY WITHIN COLUMNS, WHERE A COLUMN'S TWIN IS NOT ITS KIND
# (Codex's review of batch 4q, item 3): a column of dates held as record
# numbers that found no room for the made-up dates of some layout of it
# (its `made_up_years` published with no run of that layout's kind of
# year, empty or beside remark NF137) has those values written as record
# numbers, so code reading it as dates does not run there; F10 names it
# and reads N for it. The callers name the columns from the description's
# own facts (`generation.dates_written_as_record_numbers`).
NOT_DATES = "whose twin writes record numbers where the table holds dates"


def _within_columns(not_dates: "tuple[str, ...]") -> str:
    """F10's grade within columns: E, but N inside each column ``not_dates`` names."""
    if not not_dates:
        return "E (exact) within columns"
    named = ""
    for at in range(len(not_dates)):
        named += (", " if at else "") + f"{not_dates[at]}"
    return f"E (exact) within columns, except within {named}, {NOT_DATES}, which read N (not carried)"


def family_grades(
    pinned: bool, patient_layer: bool, moved: "tuple[str, ...]" = (), not_dates: "tuple[str, ...]" = ()
) -> "list[tuple[str, str, str]]":
    """Each family's code, name and structural grade, read from the description's words and its patient layer.

    `moved` names the children of the families a twin dealt against a moved
    target: inside them the E of F1, F4 and F9 reads A, as their pairs do
    (LANE ST RULINGS 5 (3), Codex's item 6), so no line claims more than the
    twin holds. Empty on the private report (written before any twin).
    `not_dates` names the columns of dates whose twin writes record numbers
    (`NOT_DATES`): inside them F10 reads N (Codex's review of batch 4q,
    item 3).
    """
    numbers = (
        "P (pinned on the twin's number scale) for the pairs reading pinned; A (approximate) elsewhere and on "
        "the raw or log scale of a skewed column"
        if pinned
        else _APPROXIMATE + "; no pair of this description reads pinned"
    )
    patients = (
        "E for patient-level rates inside a family; P for the trends over visits a published trend carries; "
        "A for mixed models and every other trend; N between two repeated columns at one visit"
        if patient_layer
        else "N (not in the description): this description says nothing about several rows a person"
    )
    grades = {
        "F1": (
            "E (exact at the published bands) inside each family of columns; A (approximate) across families; "
            "N for three or more columns across families"
        ),
        "F2": numbers,
        "F3": numbers,
        "F4": "E (exact) on banded predictors in the outcome's family; A (approximate) otherwise",
        "F5": _APPROXIMATE,
        "F6": _APPROXIMATE,
        "F7": patients,
        "F8": _APPROXIMATE,
        "F9": "E (exact) inside a family, where an empty cell is a band; A (approximate) otherwise",
        "F10": _within_columns(not_dates) + "; A (approximate) between columns, where no rule is published",
    }
    if moved:
        named = ""
        for at in range(len(moved)):
            named += (", " if at else "") + f"{moved[at]}"
        held = f"except in the families of {named}, {MOVED}, which read A (approximate)"
        grades["F1"] = (
            f"E (exact at the published bands) inside each family of columns, {held}; A (approximate) across "
            "families; N for three or more columns across families"
        )
        grades["F4"] = f"E (exact) on banded predictors in the outcome's family, {held}; A (approximate) otherwise"
        grades["F9"] = f"E (exact) inside a family, where an empty cell is a band, {held}; A (approximate) otherwise"
    return [(code, name, grades[code]) for code, name in FAMILIES]


def off_grades(not_dates: "tuple[str, ...]" = ()) -> "list[tuple[str, str, str]]":
    """Each family's grade on a twin of a description made with the chain's switch that publishes no chain.

    Every family between columns reads `N`, with no reason (LANE ST
    RULINGS 1 (9) and 3 (6); contract 4.6c.11 limit 2): code run unchanged
    keeps `E` within columns, which holds on every twin but inside a column
    ``not_dates`` names (`NOT_DATES`, N there: Codex's review of batch 4q,
    item 3), and `N` between.
    """
    return [
        (
            code, name,
            _within_columns(not_dates) + "; N (not carried) between columns" if code == "F10" else "N (not carried)",
        )
        for code, name in FAMILIES
    ]


def pair_words(words: "list[dict[str, object]] | tuple[tuple[str, str, str], ...]") -> "list[tuple[str, str, str]]":
    """The description's `words`, each `(first, second, word)`, in its own order, as published."""
    out: "list[tuple[str, str, str]]" = []
    for entry in words:
        if isinstance(entry, tuple):
            out += [entry]
            continue
        names = entry["columns"] if "columns" in entry else None
        word = entry["word"] if "word" in entry else None
        if isinstance(names, list) and len(names) == 2 and isinstance(word, str):
            out += [(f"{names[0]}", f"{names[1]}", word)]
    return out
