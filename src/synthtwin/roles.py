"""What a description says of each column's role, read by every command (lane S5a, plan P4-D437).

Two rules that the generator's report and the validator each read, and
that a run's result (`synthtwin.results`, plan P4-D395) reads for both
commands: which disposition-registry group a column's role publishes
under (`registry_group`, moved here from `validation._group_of`), and
which invention class a column's twin cells are in (`made_up_class`,
moved here from `rendering`, plan P4-D2). They live here because
`rendering` imports the generator, which a validate run may never reach,
and `validation` imports the reader, which a generate run may never
reach; this module imports `contract` alone.

Guarantees: pure functions of a loaded description's blocks. Raises
nothing. No I/O of any kind.
"""

from synthtwin import contract


# THE THREE INVENTION CLASSES (plan P4-D2). A column belongs to at most
# one of them, and the class decides which sentence its block carries.
#
# WHY THREE AND NOT ONE. A single sentence would be false at both edges.
# "Every value here is invented" is false of a category column that
# carries its published labels and made up only the withheld tail; and
# an invention sentence about an EMPTY column is false of a twin that
# holds no present cell of it at all. So the classes are drawn where the
# truth changes, and a column that belongs to none of them gets no
# sentence rather than a hedged one.
MADE_UP_NOTHING = ""
MADE_UP_EVERYTHING = "everything"
MADE_UP_HELD_BACK = "held-back"
MADE_UP_UNCARRIED = "uncarried"


def held_back_cells(facts: contract.LabelFacts) -> int:
    """How many cells of a label column's twin are neutral stand-ins.

    Two kinds, counted together because a reader meets them as one
    thing: the rows of every level the floor held back entirely, and
    the rows inside a published level whose SPELLING the floor held
    back. The second reads its counts through `contract.occurrence_size`
    because a repetition map's keys are row counts written as text, and
    that function is the one reader of them.
    """
    total = facts.suppressed_rows
    for level in facts.levels:
        for key in sorted(level.variants_withheld):
            size = contract.occurrence_size(key)
            if size is None:
                continue
            total = total + size * level.variants_withheld[key]
    return total


def made_up_class(column: contract.ColumnBlock) -> str:
    """Which invention class this column is in (plan P4-D2, A-P4-2).

    THE ROLE OPENS A CLASS; THE CELLS SETTLE IT (plan amendment A-P4-2,
    review item P4-C1-F3). Reading the role alone put a label column
    whose every level the floor held back into the partly-invented
    class -- and such a column has no published spelling at all, so
    every present cell of its twin is a neutral stand-in and the page
    told the reader there were values of theirs beside them when there
    were none. The count the plan asks for is a count of CELLS, so the
    edge is decided by cells: a column all of whose present cells are
    invented is in the everything class however its role publishes.
    """
    # A column with no present cell has no invented cell either, so it
    # is in no class whatever its role says -- the empty-column carve-out
    # the plan states, and the reason this test comes first.
    if not column.n_present:
        return MADE_UP_NOTHING
    if column.structural_role == "identifier" or column.role in (
        "free_text",
        "numeric_unrepresentable",
    ):
        return MADE_UP_EVERYTHING
    facts = column.facts
    if isinstance(facts, contract.LabelFacts):
        return _how_much_made_up(column, held_back_cells(facts), MADE_UP_HELD_BACK)
    return _how_much_made_up(column, uncarried_cells(column), MADE_UP_UNCARRIED)


def _how_much_made_up(
    column: contract.ColumnBlock, invented: int, partly: str
) -> str:
    """No invented cell, some of them, or the whole column (A-P4-2)."""
    if not invented:
        return MADE_UP_NOTHING
    if invented >= column.n_present:
        return MADE_UP_EVERYTHING
    return partly


def uncarried_cells(column: contract.ColumnBlock) -> int:
    """How many cells the description counts but carries no value for.

    On a numeric column these are the three classes beside the numbers
    themselves -- out of range, contradictory, and not a number at all --
    which the twin writes as counted stand-ins. On a datetime column it
    is the cells that did not read as dates. It is deliberately NOT the
    four universal counts on a datetime column: a written date is not a
    number, so those counts describe every cell of it and would name the
    whole column invented.
    """
    facts = column.facts
    if isinstance(facts, contract.DatetimeFacts):
        return facts.n_unparsed
    if isinstance(facts, contract.NumericFacts):
        return (
            column.n_out_of_range
            + column.n_contradictory
            + column.n_not_numeric
        )
    return 0


def registry_group(facts: contract.ColumnFacts) -> str:
    """Which disposition-registry group a column's role publishes under.

    The group a fact's `group.field` name opens with (`tests/dispositions.py`):
    `validation` names every check's fact under it, and a run's result
    names every generator deviation's fact under it (plan P4-D395 part 1),
    so the two read one rule; it moved here from `validation._group_of`
    with lane S5a (plan P4-D437): the generator may not import `validation`.
    Guarantees: a pure function of the facts' type. Raises nothing.
    """
    if isinstance(facts, contract.JoinedFacts):
        # THIS BRANCH WAS MISSING and the fall-through below answered
        # for it, so a joined column's two distinctness counts were
        # reported as `empty.n_distinct` -- the identity of a role that
        # publishes both as 0 and exactly observable. Found by
        # measuring a blood-pressure column rather than by any guard,
        # which is residual R-P4-62's own point.
        return "joined"
    if isinstance(facts, contract.CompoundFacts):
        # AND THIS ONE WAS WRITTEN WITH THE ROLE, not after it. The
        # branch above records what happens when a role reaches this
        # dispatch with no answer of its own: the fall-through at the
        # end returns `empty`, whose registry says both counts are 0
        # and exactly observable, so a real column's distinctness was
        # reported under another role's identity. The fifteenth role
        # publishes both counts over BOTH halves and has its own group.
        return "compound"
    if isinstance(facts, contract.ClockFacts):
        return "clock"
    if isinstance(facts, contract.AffixedFacts):
        # Its quantitative block IS the numeric block, read over the
        # cores, so it takes the numeric group's dispositions entire.
        return "numeric"
    if isinstance(facts, contract.NumericFacts):
        return "numeric"
    if isinstance(facts, contract.LabelFacts):
        return "label"
    if isinstance(facts, contract.DatetimeFacts):
        return "datetime"
    if isinstance(facts, contract.IdentifierFacts):
        return "identifier"
    if isinstance(facts, contract.TextFacts):
        return "free_text"
    if isinstance(facts, contract.UnrepresentableFacts):
        return "numeric_unrepresentable"
    return "empty"
