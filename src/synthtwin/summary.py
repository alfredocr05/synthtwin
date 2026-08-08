"""The plain-language summary of a profile (plan P1-D5, P1-D6).

The same text is printed to the screen and written beside the profile.
It is written for a researcher who has never programmed: no jargon that
is not explained in the sentence that uses it, no statistical notation,
and every number said in words a person can act on.

It has one job beyond being readable. The profile is computed FROM real
data, so it is real-derived material, and the person running the tool
has to be able to see -- before they move the file anywhere -- exactly
which of their real values it carries and which it does not. That is
what the disclosure section is for, and it is printed every run,
whether or not anything was withheld.

The summary is built from the profile document, never from the table.
That is deliberate: the machine-readable record and the words a person
reads are then two views of the same thing and cannot disagree.

Imports here stay within the allowlist (plan D6.2): this module imports
only from this package.
"""

from synthtwin import parsing, taxonomy

_ROLE_WORDS = {
    taxonomy.ROLE_EMPTY: "no values at all",
    taxonomy.ROLE_CONSTANT: "one repeated value",
    taxonomy.ROLE_IDENTIFIER: "record numbers or codes",
    taxonomy.ROLE_BINARY: "two possible values",
    taxonomy.ROLE_DATETIME: "dates or times",
    taxonomy.ROLE_COUNT: "whole numbers that count things",
    taxonomy.ROLE_CONTINUOUS: "measured numbers",
    taxonomy.ROLE_CATEGORICAL: "a set of categories",
    taxonomy.ROLE_TEXT: "free text",
    taxonomy.ROLE_UNREPRESENTABLE: (
        "numbers this file format cannot hold"
    ),
}

# Roles whose real labels can appear in the profile, and roles whose
# values never appear in it at all.
_ROLES_WITH_LABELS = (
    taxonomy.ROLE_CONSTANT,
    taxonomy.ROLE_BINARY,
    taxonomy.ROLE_CATEGORICAL,
)
_ROLES_WITHOUT_VALUES = (
    taxonomy.ROLE_IDENTIFIER,
    taxonomy.ROLE_TEXT,
    taxonomy.ROLE_UNREPRESENTABLE,
)
_ROLES_WITH_RANGES = (
    taxonomy.ROLE_COUNT,
    taxonomy.ROLE_CONTINUOUS,
    taxonomy.ROLE_DATETIME,
)

_RULE = "=" * 66


def _text_of(value: object) -> str:
    """Any value as text, for a message, with display controls shown."""
    return parsing.visible(f"{value}")


def _list_of(value: object) -> list[object]:
    """``value`` when it is a list, an empty list otherwise."""
    if isinstance(value, list):
        return value
    return []


def _map_of(value: object) -> dict[str, object]:
    """``value`` when it is a mapping, an empty mapping otherwise."""
    if isinstance(value, dict):
        return value
    return {}


def _count_of(value: object) -> int:
    """``value`` when it is a whole number, zero otherwise."""
    if isinstance(value, int):
        return value
    return 0


def _listed(items: list[str]) -> str:
    """Join names with commas, without handing a list to a text method."""
    text = ""
    for item in items:
        text = item if not text else f"{text}, {item}"
    return text


def _role_words(role: str) -> str:
    """The plain-language name of a role."""
    if role not in _ROLE_WORDS:
        return role
    return _ROLE_WORDS[role]


def _column_lines(column: dict[str, object]) -> list[str]:
    """The block of lines describing one column."""
    role = _text_of(column["role"])
    lines = [
        f"  {_text_of(column['name'])}",
        f"    read as: {_role_words(role)}",
        f"    why: {_text_of(column['detection_evidence'])}",
        (
            f"    values present: {_count_of(column['n_present'])};   "
            f"missing: {_count_of(column['n_missing'])}"
        ),
    ]
    sources = _map_of(column["missing_by_source"])
    if sources:
        spellings = [
            f"{spelling} ({_count_of(sources[spelling])})"
            for spelling in sorted(sources)
        ]
        lines = lines + [f"    counted as missing: {_listed(spellings)}"]
    if role in _ROLES_WITH_LABELS:
        levels = _list_of(column["levels"])
        shown = [
            f"{_text_of(_map_of(level)['label'])} "
            f"({_count_of(_map_of(level)['count'])})"
            for level in levels
        ]
        if shown:
            lines = lines + [f"    values in the profile: {_listed(shown)}"]
        withheld = _count_of(column["suppressed_levels"])
        if withheld:
            lines = lines + [
                (
                    f"    values left out because too few rows share them: "
                    f"{withheld} (covering "
                    f"{_count_of(column['suppressed_rows'])} rows)"
                )
            ]
    if role in (taxonomy.ROLE_COUNT, taxonomy.ROLE_CONTINUOUS):
        ladder = _map_of(column["percentiles"])
        lines = lines + [
            (
                f"    smallest: {_text_of(ladder['min'])};   "
                f"middle: {_text_of(ladder['p50'])};   "
                f"largest: {_text_of(ladder['max'])}"
            ),
            (
                f"    average: {_text_of(column['mean'])};   "
                f"spread (standard deviation): {_text_of(column['std'])}"
            ),
        ]
    if role == taxonomy.ROLE_DATETIME:
        # A column written on two clocks is published on one, and this
        # line has to say which, or a reader compares a UTC time with
        # the wall clock they remember writing down.
        clock = ""
        if _text_of(column["datetimes_read_at"]) == "utc":
            clock = (
                "  (written in more than one time zone, so these are "
                "given at UTC)"
            )
        lines = lines + [
            (
                f"    earliest: {_text_of(column['earliest'])};   "
                f"latest: {_text_of(column['latest'])}{clock}"
            )
        ]
    if role == taxonomy.ROLE_IDENTIFIER:
        lines = lines + [
            (
                f"    {_count_of(column['n_distinct'])} different values, "
                f"between {_count_of(column['min_length'])} and "
                f"{_count_of(column['max_length'])} characters long. The "
                f"values themselves are not in the profile."
            )
        ]
    if role == taxonomy.ROLE_TEXT:
        length = _map_of(column["length"])
        lines = lines + [
            (
                f"    text between {_count_of(length['min'])} and "
                f"{_count_of(length['max'])} characters long. The text "
                f"itself is not in the profile."
            )
        ]
    for remark in _list_of(column["remarks"]):
        lines = lines + [f"    worth knowing: {_text_of(remark)}"]
    return lines


def _disclosure_lines(document: dict[str, object]) -> list[str]:
    """What of the real table this profile carries, and what it does not."""
    with_labels: list[str] = []
    without_values: list[str] = []
    with_ranges: list[str] = []
    for entry in _list_of(document["columns"]):
        column = _map_of(entry)
        name = _text_of(column["name"])
        role = _text_of(column["role"])
        if role in _ROLES_WITH_LABELS and _list_of(column["levels"]):
            with_labels = with_labels + [name]
        if role in _ROLES_WITHOUT_VALUES:
            without_values = without_values + [name]
        if role in _ROLES_WITH_RANGES:
            with_ranges = with_ranges + [name]
    floor = _count_of(_map_of(document["settings"])["small_cell_floor"])
    lines = [
        "WHAT THIS PROFILE CARRIES FROM YOUR TABLE",
        "",
        "  The profile was computed from your real data, so your",
        "  institution's rules for real-derived material apply to it.",
        "  It contains no rows of your table, but it is not anonymous",
        "  either. Here is exactly what is in it.",
        "",
    ]
    if with_labels:
        lines = lines + [
            "  Real labels you will see in the profile, with how often each",
            f"  appears (only labels shared by at least {floor} rows):",
            f"    {_listed(with_labels)}",
            "",
        ]
    else:
        lines = lines + [
            "  No column has labels visible in the profile.",
            "",
        ]
    if with_ranges:
        lines = lines + [
            "  Real smallest and largest values, and the points in between",
            "  that describe the shape of the column:",
            f"    {_listed(with_ranges)}",
            "",
        ]
    if without_values:
        lines = lines + [
            "  Nothing at all of the values, only how many there are and how",
            "  long they are:",
            f"    {_listed(without_values)}",
            "",
        ]
    notes = _list_of(document["publication_notes"])
    if notes:
        lines = lines + ["  What was left out, column by column:"]
        for entry in notes:
            note = _map_of(entry)
            lines = lines + [
                f"    {_text_of(note['column'])}: {_text_of(note['note'])}"
            ]
        lines = lines + [""]
    return lines


def render(document: dict[str, object], encoding_note: str) -> str:
    """The whole summary, as the text printed and written to disk.

    Guarantees:

    - Inputs: a profile document as built by `profile.build_document`,
      and one sentence describing how the file was read.
    - Determinism: the text depends only on the document and that
      sentence; every list it prints is in the document's own order or
      sorted, and nothing consults a clock or the environment.
    - Errors raised: none for a document this package built.
    - Boundary: no file is opened, and nothing appears here that is not
      already in the document -- which is what keeps the words and the
      machine-readable record from ever disagreeing.
    """
    n_rows = _count_of(document["n_rows"])
    n_columns = _count_of(document["n_columns"])
    lines = [
        _RULE,
        "synthtwin: what your table looks like",
        _RULE,
        "",
        f"Your table has {n_rows} rows and {n_columns} columns.",
        encoding_note,
        "",
        "This is a description of your table, not a copy of it. Next, the",
        "same description will be used to build a synthetic twin: a table",
        "with the same columns, the same kinds of values and the same",
        "patterns, and none of your real rows. Numbers computed on a twin",
        "are not research results -- develop your analysis on the twin, then",
        "run the finished analysis on your real table.",
        "",
        _RULE,
        "COLUMNS, ONE BY ONE",
        _RULE,
        "",
    ]
    for entry in _list_of(document["columns"]):
        lines = lines + _column_lines(_map_of(entry)) + [""]
    lines = lines + [_RULE] + _disclosure_lines(document)
    # The lines are joined by hand: the offline policy accepts a text
    # method only with arguments it has resolved, and a list built at
    # run time is not one (plan D6.2).
    text = ""
    for line in lines:
        text = text + line + "\n"
    return text
