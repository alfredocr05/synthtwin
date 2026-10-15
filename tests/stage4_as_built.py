"""Functions of the product as they stood before stage 4 changed them, frozen as text.

The review of landing S1 (item 5) found the references
`tests/test_stage4_linear_work.py` compared two rewritten functions
with were rebuilt from the CURRENT source with the landing's edits
reversed, so a change of meaning made to the product reached the
reference as well and the comparison still passed: with the held-back
groups' size written `sizes[place] + 1`, both label columns gained a
cell per group and stayed equal. These are fixed texts instead, and
nothing reads the product's source to build them:

- `LABEL_CONTENT` is `generation._label_content` exactly as 668f276
  shipped it, the column copied once per level.
- `ALLOTTED_OVER` is the packing walk of method G9.5 as 493f6f8
  shipped it, `generation._allotted_over` and every function it calls
  down to `_cell_walk`, the oracle of the bounded walk of plan P4-D389
  (`tests/test_stage4_allocator_walk.py`): the answers must be its
  answers wherever it finishes.
- `PUSHED_APART`, `IDENTITY_WALK`, `POOLED_PLACED` and `QUALITY_REPORT`
  are G6.5a's push, G6.6's identity walk, G8.3c's pooled placement and
  the quality report as 3434682 shipped them, the oracles of lane
  S4b-num (`tests/test_stage4_numbers_and_codes.py`, plans P4-D377,
  P4-D387 and P4-D390). `POOLED_PLACED`'s `_pooled_spelling` is lane
  L1's (07a38f6, which merged it beside 3434682's): L1 added three
  rules to its stepping -- `figures_cap`, no value a published number
  holds, the published codes' width -- and the lane's search must
  answer as that stepping does (batch 4a's merge).

`READ_THE_COLUMN`, `taxonomy._read_the_column` with its level pass as
668f276 shipped it, stood here too until plan P4-D390 deleted that pass.

Each is compiled into a copy of its module's own names, so the helpers
it does not define are today's, and the tests that use it require a
change of meaning made to the product function to break the
comparison. Nothing here is imported by the product.
"""

from __future__ import annotations

import types


def compiled(module: types.ModuleType, source: str, name: str) -> "tuple[object, dict]":
    """The function ``name`` defined by ``source``, run among a copy of ``module``'s names.

    Returns the function and the copy of the names it runs in, so a
    measure can replace one of them without touching the module.
    """
    names = dict(vars(module))
    exec(compile(source, f"<{name} as built>", "exec"), names)
    return names[name], names


LABEL_CONTENT = r'''
def _label_content(
    plan: "_ColumnPlan",
    short: "list[int] | None" = None,
) -> "tuple[list[str], list[Deviation]]":
    """Every present cell of a column of labels (method G8).

    ``short``, where given, is told how many held-back groups owed a
    numeric class and found no spelling of it (method G8.3a), which is
    how the twin's report tells a supply that ran out from a partition
    that did not exist.

    A column of labels consumes no words: everything is fixed by
    published counts, which is why a fully determined one produces the
    same bytes whatever the seed is. The published levels come first in
    the description's own order, each level's spellings in the order
    method G8.1 fixes, then the levels the smallest-group-size rule held
    back.
    """
    column = plan.column
    facts = column.facts
    if not isinstance(facts, contract.LabelFacts):
        raise _wrong_facts(column.name)
    used: dict[str, int] = {}
    owners: dict[str, str] = {}
    cells: list[str] = []
    notes: list[Deviation] = []
    made_up = 0
    for entry in facts.levels:
        covered = 0
        # ...AND HOW MANY OF THOSE CELLS ALREADY WEAR THE LABEL'S OWN
        # WRITTEN FORM. The published spellings are written byte for
        # byte, so what they wear is read rather than reasoned about --
        # the same rule `_forms_owed` follows for the column census.
        covered_in_form = 0
        for spelling in sorted(entry.variants):
            cells = cells + [spelling for _each in range(entry.variants[spelling])]
            covered = covered + entry.variants[spelling]
            if parsing.shape_form(spelling):
                covered_in_form = covered_in_form + entry.variants[spelling]
            used[spelling] = 1
            owners[parsing.folded(spelling)] = entry.label
        # WHICH HELD-BACK GROUPS KEEP THE LABEL'S WRITTEN FORM (method
        # G8.1a, plan amendment A-P4-47). The level publishes how many
        # of its cells wore that form; the published spellings written
        # just above pay what they can, and the rest is a DEBT that
        # whole held-back groups have to cover between them. Before
        # this fact existed the walk guessed -- it handed the scarce
        # form-keeping spelling to the LARGEST held-back group -- and
        # missed in both directions, which is residual R-P4-34.
        own_form = parsing.shape_form(entry.label)
        keeping = _form_keeping_groups(entry, covered_in_form)
        # WHETHER THE LABEL'S OWN SPELLING IS SPOKEN FOR. A level whose
        # published and held-back spellings do not reach its count is
        # finished below by writing the label itself, so that spelling
        # is reserved and a variant may not take it. Where they DO
        # reach the count nothing is left to write and the label's own
        # spelling is free -- and it is worth having, because it is the
        # one further spelling that folds onto the label while KEEPING
        # ITS WRITTEN FORM, where a trailing space does not (P4-D18).
        #
        # It goes to the LARGEST group whose target form it wears --
        # which is the largest form-keeping group where the label has a
        # form of its own, and the largest group of all where it has
        # none, because then every group's target is "no form" and so
        # is the label's. Where the label has a form and NO group keeps
        # it, the spelling is not spent at all: spending it there is
        # exactly the overshoot this amendment repairs.
        spare = _spare_variant_group(entry, keeping)
        left: "dict[str, int]" = {}
        for key in keeping:
            left[key] = keeping[key]
        for key in _withheld_keys(entry.variants_withheld):
            rows = int(key)
            for _each in range(entry.variants_withheld[key]):
                wanted = ""
                if key in left and left[key] > 0:
                    wanted = own_form
                    left[key] = left[key] - 1
                take = key == spare
                variant = _variant_spelling(
                    entry.label, used, owners, wanted, take
                )
                if take:
                    spare = ""
                made_up = made_up + 1
                cells = cells + [variant for _row in range(rows)]
                covered = covered + rows
        if covered < entry.count:
            cells = cells + [
                entry.label for _row in range(entry.count - covered)
            ]
            used[entry.label] = 1
            owners[parsing.folded(entry.label)] = entry.label
    if made_up:
        notes += [
            _deviation(
                column.name,
                "levels -> variants_withheld",
                f"{made_up} spellings that were held back",
                f"{made_up} neutral spellings made up in their place",
                "Those spellings were written by too few rows to publish, "
                "so the twin keeps the count and the values distinct; "
                "below the floor the spellings themselves are in no "
                "file synthtwin writes.",
            )
        ]
    number = 0
    # THE FORMS THIS COLUMN WAS WRITTEN IN, IF IT PUBLISHED ANY (plan
    # P4-D18). A long tail publishes a census of them, and it is the
    # role whose twin is mostly stand-ins; the sibling label roles
    # publish none, so the debt is empty for them and the neutral
    # `group-N` spelling stands as before.
    owing = _forms_owed(facts, cells)
    # THE CLASSES THE HELD-BACK GROUPS OWE (method G8.3a). The published
    # spellings pay what they read as; what is left of `n_numeric`,
    # `n_out_of_range` and `n_contradictory` is owed by the held-back
    # groups, which before this rule were all written as words -- so a
    # column of readings beside two labels lost every held-back reading
    # and code parsing its numbers crashed on the twin.
    # THE SIZES ARE READ OFF THE POOL (owner ruling of 2026-09-17, item
    # 2, option A; plan P4-D201), because no size of any one held-back
    # label is published any more.
    # EVERY ABSENT SPELLING OF THE TABLE, not only this column's
    # (integration repair of landing 2b.4). A made-up number is refused on
    # a spelling the profiler reads as absent, and `--missing-value 5`
    # declared for another column is absent here too: a column of labels
    # beside that one wrote `5` four times, and its twin was described
    # again with four present cells fewer and eight checks missed.
    holes = _all_holes_of(plan)
    comma = plan.decimal_comma
    debts = _classes_owed(column, cells, comma)
    numbers_owed, words_owed = _held_back_debts(
        owing, debts, facts.suppressed_rows, comma
    )
    sizes = held_back_sizes(
        facts.suppressed_levels,
        facts.suppressed_rows,
        plan.small_cell_floor,
        numbers_owed,
        words_owed,
    )
    # ASKED WHILE `cells` HOLDS THE PUBLISHED SPELLINGS ALONE, before any
    # stand-in joins them, so the answer is about what the DESCRIPTION
    # published and not about what the twin went on to write.
    unspellable = _published_an_unspellable_number(cells, comma)
    classes: "dict[int, str]" = {}
    written_as: "dict[int, str]" = {}
    asked: "dict[int, str]" = {}
    numbers_made = 0
    unplaced = False
    scaled = 0
    if sizes and max([debts[name] for name in _OWED_CLASSES]) > 0:
        (
            classes, written_as, asked, numbers_made, unplaced, scaled,
        ) = _class_stand_ins(
            column, cells, sizes, owing, debts, used, owners, holes, comma,
            short, plan.small_cell_floor,
        )
        # WHAT IS LEFT FOR WORDS, and only the forms words can wear: a
        # number-reading form is paid inside the number class or not at
        # all.
        for form in sorted(owing):
            if _form_reading(form, comma) != parsing.NOT_A_NUMBER:
                owing[form] = 0
    # NAMED FOR ITSELF rather than reusing `wanted`, which this module
    # already binds to a COUNT and to a STYLE NAME elsewhere: the strict
    # type check reads one name as one type per scope, and three
    # meanings under one spelling is a reading nobody should have to
    # hold in their head either.
    shared: "list[str]" = []
    if not classes:
        shared = _shared_out(sizes, owing, used, owners, holes)
    else:
        wordy = [place for place in range(len(sizes)) if place not in classes]
        settled = _shared_out(
            tuple([sizes[place] for place in wordy]), owing, used, owners,
            holes,
        )
        shared = ["" for _each in sizes]
        for step in range(len(wordy)):
            shared[wordy[step]] = settled[step]
    # THE SHAPE A STAND-IN TAKES WHERE THE CENSUS OWES IT NONE (landing
    # 2b.18 part 2, plan P4-D122; the carried item of landing 2b.12),
    # and the rows it is spent on.
    level_shape = _published_level_shape(facts, comma)
    shaped_places: "dict[int, int]" = {}
    if level_shape:
        shared, shaped_places = _level_shape_spent(
            sizes, shared, level_shape, written_as, used, owners, holes
        )
    # Each form's place in its own supply, carried across the whole
    # column so no spelling is walked twice.
    walked: "dict[str, int]" = {}
    shaped = 0
    kept = 0
    for place in range(len(sizes)):
        size = sizes[place]
        form = shared[place]
        if place in written_as:
            label = written_as[place]
            form = asked[place]
        else:
            number, label = _made_up_label(
                number, used, owners, form, plan.all_holes, walked,
                level_shape if place in shaped_places else "",
            )
            if not form and level_shape and _level_key(label) == level_shape:
                kept = kept + 1
        # WHAT THE LABEL ACTUALLY WEARS, not what it was asked to wear
        # (review round 2 finding 12). The walk gives a form up when
        # its supply is spent or every spelling of it is refused, and
        # this counted the ASKING -- so a report said thirty-three
        # stand-ins were written in a published form when five of them
        # were `group-N`.
        if form and parsing.census_form(label, facts.shape_forms) == form:
            shaped = shaped + 1
        cells = cells + [label for _row in range(size)]
    if facts.suppressed_levels:
        # WHAT THE STAND-INS WERE WRITTEN IN IS PART OF THE NOTE (plan
        # P4-D18). A column publishing a census of written forms has
        # its stand-ins written in them, and a column publishing none
        # has the neutral spelling as before -- and a column can have
        # both, where the forms the held-back cells wore were
        # themselves too rare to name, so the count is given rather
        # than the reader left to guess which happened.
        made = (
            f"{facts.suppressed_levels} neutral labels made up in their place"
        )
        if shaped:
            made = (
                f"{facts.suppressed_levels} labels made up in their place, "
                f"{shaped} of them written in a form this column published"
            )
        if kept and not shaped:
            made = (
                f"{facts.suppressed_levels} labels made up in their place, "
                f"{kept} of them written in the shape of a label this "
                f"column published"
            )
        elif kept:
            made = (
                f"{made}, and {kept} more in the shape of a label this "
                f"column published"
            )
        reason = _HELD_BACK_REASON
        if numbers_made:
            made = (
                f"{facts.suppressed_levels} labels made up in their place, "
                f"{numbers_made} of them numbers"
            )
            if shaped:
                made = (
                    f"{made}, and {shaped} of them written in a form this "
                    f"column published"
                )
            if kept:
                made = (
                    f"{made}, and {kept} in the shape of a label this "
                    f"column published"
                )
            reason = _HELD_BACK_NUMBERS_REASON
            if scaled >= numbers_made:
                # EVERY made-up number placed on the published scale,
                # and not merely some of them: a column where the
                # placement ran short still has numbers this version
                # chose the location of, so the older sentence is the
                # true one there.
                reason = _HELD_BACK_SCALED_REASON
            elif unplaced:
                reason = _HELD_BACK_UNPLACED_REASON
                if unspellable:
                    reason = _HELD_BACK_UNSPELLED_REASON
        notes += [
            _deviation(
                column.name,
                "suppressed_levels",
                f"{facts.suppressed_levels} labels that were held back",
                made,
                reason,
            )
        ]
    return cells, notes

'''


ALLOTTED_OVER = r'''
def _allotted_over(
    groups: "tuple[int, ...]",
    margins: "list[tuple[list[int], list[int]]]",
    allowed: "list[int]",
) -> "list[int] | None":
    """Give every group to one cell, meeting EVERY margin exactly.

    THE GRID CARRIES THE DESCRIPTION'S OWN COUNTS AND NOTHING ELSE
    (review item P2-C3-F1). A margin is a family of published counts
    that divides the cells between them: ``(quotas, part_of)``, where
    ``part_of[cell]`` says which count of that family the cell answers
    for. A column of numbers too large to hold publishes THREE such
    families over one set of cells -- what the notation classifies as,
    whether the value is a whole number, and what sign it settles -- and
    publishes no cross-tabulation of them at all. Packing over two
    margins invented from them, rather than over the three the
    description carries, is how an earlier revision asked the walk to
    solve a question the real column never answered and then reported
    six exact counts as missed.

    ``allowed[i]`` names the cells group ``i`` may take. The answer is
    one cell index per group, in group order, or None where no
    assignment of whole groups meets every count of every margin.

    THE ORDER IS PART OF THE RULE, so two implementations pack the same
    way. Inside each margin the counts are ranked in ascending order of
    their own published values, ties by the description's own order, so
    the count that absorbs whatever is left over is answered for last.
    Cells are then filled in ascending order of the ranks they carry,
    margin by margin, ties by the cell's own number -- which for two
    margins is exactly the row-major order over ranked rows and columns
    that `_allotted_pairs` states. Within a cell the different group
    SIZES are offered in ascending order and each offers as many copies
    as the cell can still hold, falling back to fewer; a fill that
    leaves a later cell unable to finish is undone and the next is
    tried; and groups are handed to their cells in group order.
    """
    counted = 0
    for size in groups:
        counted = counted + size
    for margin in margins:
        total = 0
        for quota in margin[0]:
            total = total + quota
        if total != counted:
            return None
    cells = len(margins[0][1])
    # THE SMALLEST COUNT IS ANSWERED FOR FIRST, and the largest last.
    # The order is fixed by the published values themselves, ascending,
    # ties by the contract's own order, so it is a function of the
    # description and of nothing else. It is chosen rather than inherited
    # for a reason a ceiling used to hide: the largest count is the one
    # that absorbs whatever is left over, so filling it first spends the
    # small group sizes on it and leaves the small counts to be made out
    # of the large sizes, which is the shape a packing walk can spend an
    # unbounded amount of time undoing. Answering the small counts first
    # is what keeps a genuine description answered at once now that no
    # ceiling stops the walk (review items P2-C2-F1 and P2-C3-F1).
    order = _cell_order(margins, cells)
    ranked = [-1 for _each in range(cells)]
    for step in range(cells):
        ranked[order[step]] = step
    part_at = [
        [margin[1][order[step]] for step in range(cells)]
        for margin in margins
    ]
    last_of = [_last_cells(places, cells) for places in part_at]
    masks = [
        _ranked_mask(allowed[place], ranked) for place in range(len(groups))
    ]
    keys = sorted({
        (groups[place], masks[place]) for place in range(len(groups))
    })
    place_of = {keys[index]: index for index in range(len(keys))}
    counts = [0 for _each in keys]
    for place in range(len(groups)):
        counts[place_of[(groups[place], masks[place])]] = (
            counts[place_of[(groups[place], masks[place])]] + 1
        )
    taken = _cell_walk(
        keys,
        counts,
        [[quota for quota in margin[0]] for margin in margins],
        part_at,
        last_of,
    )
    if taken is None:
        return None
    chosen = [-1 for _each in groups]
    for cell in range(cells):
        for place in range(len(groups)):
            if chosen[place] >= 0:
                continue
            found = place_of[(groups[place], masks[place])]
            if taken[cell][found] < 1:
                continue
            chosen[place] = order[cell]
            taken[cell][found] = taken[cell][found] - 1
    for cell in chosen:
        if cell < 0:
            return None
    return chosen


def _cell_order(
    margins: "list[tuple[list[int], list[int]]]", cells: int
) -> "list[int]":
    """The order the cells are filled in, as cell numbers.

    Each margin ranks its own counts ascending, ties by the order the
    description states them in; a cell then carries one rank per margin,
    and the cells are filled in ascending order of those ranks read left
    to right, ties by the cell's own number. Over two margins this is
    the row-major order over ranked rows and ranked columns exactly.
    """
    ranks: list[list[int]] = []
    for margin in margins:
        quotas = margin[0]
        placed = [
            pair[1]
            for pair in sorted(
                [(quotas[place], place) for place in range(len(quotas))]
            )
        ]
        rank = [0 for _each in quotas]
        for step in range(len(placed)):
            rank[placed[step]] = step
        ranks += [rank]
    keyed = sorted([
        (
            tuple(
                ranks[place][margins[place][1][cell]]
                for place in range(len(margins))
            ),
            cell,
        )
        for cell in range(cells)
    ])
    return [pair[1] for pair in keyed]


def _last_cells(places: "list[int]", cells: int) -> "list[bool]":
    """Which cells are the last of their own count, in the fill order.

    A count has nothing after that cell to answer for it, so the cell
    takes exactly what the count still owes rather than choosing.
    """
    seen: dict[int, int] = {}
    flags = [False for _each in range(cells)]
    for step in range(cells - 1, -1, -1):
        if places[step] not in seen:
            flags[step] = True
            seen[places[step]] = 1
    return flags


def _ranked_mask(mask: int, ranked: "list[int]") -> int:
    """One permission set written over the cells in the order they fill."""
    built = 0
    for cell in range(len(ranked)):
        if (mask >> cell) & 1:
            built = built | (1 << ranked[cell])
    return built


def _cell_room(
    owed: "list[list[int]]",
    part_at: "list[list[int]]",
    last_of: "list[list[bool]]",
    cell: int,
) -> "tuple[int, int]":
    """The smallest and largest total one cell of the grid may hold.

    A cell may never hold more than what ANY of the counts it answers
    for still owes. It holds EXACTLY what one of them still owes when it
    is that count's last cell, because nothing after it can answer for
    that count. Where those demands cross, the pair returned has its
    ends the wrong way round and the caller reads that as "no fill".
    """
    lowest = 0
    highest = -1
    for margin in range(len(owed)):
        left = owed[margin][part_at[margin][cell]]
        if last_of[margin][cell] and left > lowest:
            lowest = left
        if highest < 0 or left < highest:
            highest = left
    return lowest, highest


def _reach_bits(
    keys: "list[tuple[int, int]]",
    left: "list[int]",
    cell: int,
    ceiling: int,
) -> "list[int]":
    """Which totals the sizes from each place onward can still make.

    Entry ``k`` is a whole number whose bit ``t`` is set when the group
    sizes at places ``k`` and after, in the copies still unplaced, can be
    chosen to total exactly ``t``. It is built from the last place
    backward, one size at a time, by the halving rule -- one copy, then
    two, then four, then what is left -- so a size with a thousand
    copies costs ten shifts rather than a thousand. Bits above
    ``ceiling`` are dropped, because no fill of this cell may reach
    them.

    This is what makes the walk of `_cell_walk` enter only branches that
    can finish the cell they are filling, which is what let the state
    and depth ceilings of the earlier revision be removed (review item
    P2-C2-F1).
    """
    total = len(keys)
    limit = (1 << (ceiling + 1)) - 1
    bits = [0 for _each in range(total + 1)]
    bits[total] = 1
    for place in range(total - 1, -1, -1):
        reach = bits[place + 1]
        if (keys[place][1] >> cell) & 1:
            copies = left[place]
            step = 1
            while copies > 0:
                take = min(step, copies)
                reach = (reach | (reach << (take * keys[place][0]))) & limit
                copies = copies - take
                step = step * 2
        bits[place] = reach
    return bits


def _reach_any(
    keys: "list[tuple[int, int]]",
    left: "list[int]",
    cells: int,
    target: int,
) -> bool:
    """Whether the groups allowed in ANY of ``cells`` can total ``target``.

    The same halving walk as `_reach_bits`, over the union of a set of
    cells rather than one cell, and answering one question instead of
    building a table.
    """
    if target < 1:
        return True
    limit = (1 << (target + 1)) - 1
    reach = 1
    for place in range(len(keys)):
        if keys[place][1] & cells == 0:
            continue
        copies = left[place]
        step = 1
        while copies > 0:
            take = min(step, copies)
            reach = (reach | (reach << (take * keys[place][0]))) & limit
            copies = copies - take
            step = step * 2
        if (reach >> target) & 1:
            return True
    return (reach >> target) & 1 == 1


def _margins_left(
    keys: "list[tuple[int, int]]",
    left: "list[int]",
    owed: "list[list[int]]",
    part_at: "list[list[int]]",
    cell: int,
    cells: int,
) -> bool:
    """Whether every count still owed can be made from what is unplaced.

    A NECESSARY CONDITION, checked once per state rather than discovered
    at the bottom of a walk. Every count of every margin that still owes
    something must be able to total exactly that from the group sizes
    still unplaced that its own remaining cells permit. It says nothing
    about whether the margins can be satisfied TOGETHER -- that is the
    question the walk itself answers -- but it cuts the branch where one
    of them cannot be satisfied at all, which is where a walk with no
    ceiling would otherwise spend an unbounded amount of time (review
    items P2-C2-F1 and P2-C3-F1).
    """
    for margin in range(len(owed)):
        for part in range(len(owed[margin])):
            if owed[margin][part] < 1:
                continue
            reachable = 0
            for step in range(cell, cells):
                if part_at[margin][step] == part:
                    reachable = reachable | (1 << step)
            if not _reach_any(keys, left, reachable, owed[margin][part]):
                return False
    return True


def _within(bits: int, lowest: int, highest: int) -> bool:
    """True when some total between the two ends is still reachable."""
    if highest < 0:
        return False
    low = max(lowest, 0)
    if low > highest:
        return False
    return bits & (((1 << (highest - low + 1)) - 1) << low) != 0


def _cell_next(
    keys: "list[tuple[int, int]]",
    left: "list[int]",
    state: "list[int]",
    reach: "list[int]",
    room: "tuple[int, int]",
    cell: int,
) -> "tuple[list[int], list[int] | None]":
    """The next fill of one cell in the fixed order, and the walk after it.

    ``state`` is how many groups of each size this cell is taking, as far
    as the walk has decided. An empty ``state`` asks for the first fill;
    a complete one asks for the fill after it, which is what lets the
    caller resume this cell after a later one failed. Sizes are decided
    in ascending order and each offers as many copies as the cell can
    still hold, falling back to fewer -- the order method G9.5 fixes.

    Returns the walk to hand back on the next call and the fill, or None
    for the fill where this cell's walk is spent.

    Every branch entered can still reach a total the cell accepts,
    because `reach` is consulted before descending, so a complete state
    is always a fill and no fill is ever visited twice.
    """
    total = len(keys)
    lowest, highest = room
    walk = [number for number in state]
    if total == 0:
        if walk or not (lowest <= 0 <= highest):
            return walk, None
        return walk, []
    used = 0
    for place in range(len(walk)):
        used = used + walk[place] * keys[place][0]
    if len(walk) == total:
        while walk and walk[len(walk) - 1] == 0:
            walk = walk[:len(walk) - 1]
        if not walk:
            return walk, None
        place = len(walk) - 1
        walk[place] = walk[place] - 1
        used = used - keys[place][0]
    while True:
        place = len(walk) - 1
        if place >= 0 and walk[place] < 0:
            used = used + keys[place][0]
            walk = walk[:place]
            if not walk:
                return walk, None
            walk[place - 1] = walk[place - 1] - 1
            used = used - keys[place - 1][0]
            continue
        if place >= 0 and not _within(
            reach[place + 1], lowest - used, highest - used
        ):
            walk[place] = walk[place] - 1
            used = used - keys[place][0]
            continue
        if len(walk) == total:
            return walk, [number for number in walk]
        ahead = len(walk)
        most = 0
        if (keys[ahead][1] >> cell) & 1:
            most = min(left[ahead], (highest - used) // keys[ahead][0])
        walk += [most]
        used = used + most * keys[ahead][0]


def _moved_by(
    fill: "list[int]",
    keys: "list[tuple[int, int]]",
    left: "list[int]",
    owed: "list[list[int]]",
    part_at: "list[list[int]]",
    cell: int,
    way: int,
) -> None:
    """Apply one cell's fill to the running tallies, or take it back.

    ``way`` is -1 to place the fill and 1 to undo it, which is what lets
    the walk of `_cell_walk` step back over a cell it has already tried.
    """
    moved = 0
    for place in range(len(fill)):
        left[place] = left[place] + way * fill[place]
        moved = moved + fill[place] * keys[place][0]
    for margin in range(len(owed)):
        owed[margin][part_at[margin][cell]] = (
            owed[margin][part_at[margin][cell]] + way * moved
        )


def _cell_walk(
    keys: "list[tuple[int, int]]",
    counts: "list[int]",
    owed: "list[list[int]]",
    part_at: "list[list[int]]",
    last_of: "list[list[bool]]",
) -> "list[list[int]] | None":
    """Fill every cell of the grid exactly, or say no filling does.

    Written as a loop over an explicit list of walks rather than as
    nested calls, so that a description publishing many different group
    sizes cannot grow a call chain without end -- which is the shape the
    removed depth ceiling was guarding against, now handled rather than
    refused (review item P2-C2-F1).

    A cell whose walk is spent is written down as having no answer under
    the state it was entered in -- which sizes were still unplaced and
    what every count of every margin still owed -- so the same state is
    never explored twice, and the number of different states is finite
    and fixed by the description before the walk begins. That is the
    whole termination argument, and it is the only thing that ends this
    walk now: NOTHING counts trips and stops (review item P2-C3-F1).
    """
    cells = len(part_at[0])
    left = [count for count in counts]
    walks: list[list[int]] = []
    reaches: list[list[int]] = []
    rooms: list[tuple[int, int]] = []
    placed: list[list[int]] = []
    marks: list[tuple[int, tuple[int, ...], tuple[tuple[int, ...], ...]]]
    marks = []
    failed: dict[
        tuple[int, tuple[int, ...], tuple[tuple[int, ...], ...]], int
    ] = {}
    cell = 0
    while True:
        if cell == cells:
            return placed
        if len(walks) == cell:
            mark = (
                cell,
                tuple(left),
                tuple(tuple(margin) for margin in owed),
            )
            room = _cell_room(owed, part_at, last_of, cell)
            if mark in failed or room[0] > room[1] or not _margins_left(
                keys, left, owed, part_at, cell, cells
            ):
                failed[mark] = 1
                cell = cell - 1
                if cell < 0:
                    return None
                continue
            marks += [mark]
            rooms += [room]
            reaches += [_reach_bits(keys, left, cell, room[1])]
            walks += [[]]
            placed += [[]]
        else:
            _moved_by(
                placed[cell], keys, left, owed, part_at, cell, 1,
            )
        walk, found = _cell_next(
            keys, left, walks[cell], reaches[cell], rooms[cell], cell
        )
        walks[cell] = walk
        if found is None:
            failed[marks[cell]] = 1
            walks = walks[:cell]
            reaches = reaches[:cell]
            rooms = rooms[:cell]
            placed = placed[:cell]
            marks = marks[:cell]
            cell = cell - 1
            if cell < 0:
                return None
            continue
        _moved_by(found, keys, left, owed, part_at, cell, -1)
        placed[cell] = found
        cell = cell + 1

'''


# -- stage 4 lane S4b-num (the million-row costs of numbers and codes) -------
#
# Each text below is the function as 3434682 shipped it, read off that
# tree with its docstrings and comments left out (`ast.unparse`), except
# IDENTITY_WALK: 3434682 ran the identity walk inside `_number_cells`,
# and the text is that loop with the names it read from the enclosing
# function made its parameters, exactly the parameters the lane's
# `_identity_walk` takes.

PUSHED_APART = r'''
def _pushed_apart(facts: contract.NumericFacts, layout: '_NumericLayout', rungs: 'tuple[float, ...] | None', moved: 'list[float]', texts: 'list[str]', held: 'dict[str, int]', figures: int, keep_whole: bool) -> 'tuple[list[float], list[str], dict[str, int]]':
    wanted = facts.n_distinct_values
    total = len(moved)
    if wanted is None or rungs is None or figures < 0 or (total != wanted):
        return (moved, texts, held)
    if len(held) >= wanted:
        return (moved, texts, held)
    bottom = _grid_units(_grid_text(rungs[0], figures), figures)
    top = _grid_units(_grid_text(rungs[-1], figures), figures)
    if bottom is None or top is None or top <= bottom:
        return (moved, texts, held)
    gaps: 'tuple[tuple[float, float], ...]' = tuple(((edges[0], edges[1]) for edges in facts.empty_edges))
    point_free = _whole_demand(facts) > 0
    immovable: 'dict[str, int]' = {}
    while len(held) < wanted:
        target = -1
        target_units = 0
        for place in range(total):
            text = texts[place]
            if held[text] < 2 or text in immovable:
                continue
            if layout.bands[place] == _BAND_ZERO:
                continue
            units = _grid_units(text, figures)
            if units is None:
                continue
            if target < 0 or units < target_units:
                target = place
                target_units = units
        if target < 0:
            break
        collision = texts[target]
        band = layout.bands[target]
        lowest = bottom
        highest = top
        if band == _BAND_NEGATIVE and highest > -1:
            highest = -1
        if band == _BAND_POSITIVE and lowest < 1:
            lowest = 1
        holders: 'list[int]' = []
        for place in range(total):
            if texts[place] != collision:
                continue
            if layout.bands[place] == _BAND_ZERO:
                continue
            if place == 0 or place == total - 1:
                continue
            holders += [place]
        ways: 'list[tuple[int, int, list[tuple[int, int]]]]' = []
        for step in (-1, 1):
            order = range(len(holders))
            if step > 0:
                order = range(len(holders) - 1, -1, -1)
            for index in order:
                mover = holders[index]
                kind: 'bool | None' = None
                if keep_whole:
                    kind = _whole_valued(moved[mover]) == moved[mover]
                plan = _push_plan(texts, held, collision, target_units, step, lowest, highest, figures, gaps, kind, kept=facts.kept_stand_ins)
                if plan is None:
                    continue
                pairs = plan[0] + [(mover, plan[1])]
                refused = False
                for pair in pairs:
                    if not _push_allowed(facts, moved, pair[0], pair[1], figures, keep_whole, point_free):
                        refused = True
                        break
                if refused:
                    continue
                ways += [(len(pairs), step, pairs)]
                break
        if not ways:
            immovable[collision] = 1
            continue
        chosen = ways[0]
        for way in ways:
            if way[0] < chosen[0]:
                chosen = way
        for pair in chosen[2]:
            place = pair[0]
            fresh_text = _grid_at(pair[1], figures)
            fresh = float(fresh_text)
            old = texts[place]
            held[old] = held[old] - 1
            if held[old] == 0:
                del held[old]
            seen = 0
            if fresh_text in held:
                seen = held[fresh_text]
            held[fresh_text] = seen + 1
            texts[place] = fresh_text
            moved[place] = fresh
    return (moved, texts, held)

def _push_plan(texts: 'list[str]', held: 'dict[str, int]', collision: str, start: int, step: int, lowest: int, highest: int, figures: int, gaps: 'tuple[tuple[float, float], ...]', whole: 'bool | None', kept: 'tuple[float, ...]'=()) -> 'tuple[list[tuple[int, int]], int] | None':
    passed: 'dict[int, int]' = {}
    unit = start
    while True:
        after = _band_step(unit, step, lowest, highest, figures, gaps, whole, kept=kept)
        if after is None:
            return None
        passed[unit] = after
        if _grid_at(after, figures) not in held:
            break
        unit = after
    run: 'list[tuple[int, int]]' = []
    for place in range(len(texts)):
        text = texts[place]
        if text == collision:
            continue
        units = _grid_units(text, figures)
        if units is None or units not in passed:
            continue
        run += [(place, passed[units])]
    return (run, passed[start])
'''

IDENTITY_WALK = r'''
def _identity_walk(holds: 'list[float]', styles: 'list[str]', base: 'list[str]', widths: 'list[int]', pads: 'list[int]', marks: 'list[str]', notations: 'list[str]', plussed: 'list[bool]', whole_column: bool, owed: int) -> 'dict[int, str]':
    identities: dict[str, int] = {}
    spellings: dict[str, int] = {}
    written: dict[int, str] = {}
    visiting: list[int] = []
    for index in range(len(holds)):
        if not marks[index]:
            visiting += [index]
    for index in range(len(holds)):
        if marks[index]:
            visiting += [index]
    for index in visiting:
        style = styles[index]
        spelling = base[index]
        if style != 'plain' and owed > 0 and (pads[index] < 0) and (parsing.folded(spelling) in identities):
            order = 1 if style == 'leading_zero' else 0
            while parsing.folded(spelling) in identities:
                order = order + 1
                spelling = _styled_number(holds[index], style, order, whole_column, widths[index], pads[index], marks[index], notations[index], plussed[index])
            owed = owed - 1
        identities[parsing.folded(spelling)] = 1
        spellings[spelling] = 1
        written[index] = spelling
    return written
'''

POOLED_PLACED = r'''
def _pooled_spelling(ladder: '_Ladder', wanted: float, asked: str, named: 'dict[str, int]', used: 'dict[str, int]', owners: 'dict[str, str]', holes: 'tuple[str, ...]', decimal_comma: bool, needed: int, pool: 'list[int] | None', widest: int) -> str:
    if not math.isfinite(wanted):
        return ''
    tiers = ladder.tiers
    if asked:
        tiers = (_form_places(asked, decimal_comma),)
    for places in tiers:
        middle = wanted
        if places > 0:
            middle = wanted * float(_ten_to(places))
        if places < 0:
            middle = wanted / float(_ten_to(0 - places))
        if not math.isfinite(middle) or abs(middle) > _POOLED_REACH:
            continue
        anchor = int(round(middle))
        reach_figures = widest
        if not ladder.anchored and _whole_figures(anchor, places) > reach_figures:
            reach_figures = _whole_figures(anchor, places)
        for step in range(2 * _POOLED_STEPS):
            reach = (step + 1) // 2
            units = anchor + (reach if step % 2 == 0 else -reach)
            if not _sign_held(units, ladder.signs):
                continue
            if reach_figures > 0 and _whole_figures(units, places) > reach_figures:
                continue
            if not asked and ladder.figures_cap > 0 and (_whole_figures(units, places) > ladder.figures_cap):
                continue
            if _is_published_at(ladder, units, places):
                continue
            candidate = _units_spelled(units, places, decimal_comma)
            form = parsing.census_form(candidate, named)
            wearing = ''
            if asked:
                if form != asked:
                    candidate = _dressed_in_form(candidate, asked, named, decimal_comma)
                    if not candidate:
                        continue
                    wearing = asked
            elif form in named:
                continue
            elif pool is not None and form and (parsing.form_room(form) >= needed) and (pool[0] < 1):
                continue
            if not asked:
                candidate = _padded_to_the_source(candidate, ladder)
            if candidate in used or parsing.folded(candidate) in owners:
                continue
            if not _is_a_usable_stand_in(candidate, holes, parsing.NUMBER, decimal_comma, wearing):
                continue
            return candidate
    return ''

def _pooled_offered(ladder: '_Ladder', groups: 'list[tuple[int, int, str]]', positions: 'list[int]', centre: float, spacing: float, middle: float, shift: float, named: 'dict[str, int]', used: 'dict[str, int]', owners: 'dict[str, str]', holes: 'tuple[str, ...]', decimal_comma: bool, needed: int, pool: 'list[int] | None', widest: int) -> 'tuple[dict[int, str], float, int]':
    taken = dict(used)
    answered = dict(owners)
    written: 'dict[int, str]' = {}
    cells = 0
    weighted = 0.0
    for step in range(len(groups)):
        wanted = middle + shift + spacing * (positions[step] - centre)
        found = ''
        if math.isfinite(wanted):
            found = _pooled_spelling(ladder, wanted, groups[step][2], named, taken, answered, holes, decimal_comma, needed, pool, widest)
        if not found:
            continue
        taken[found] = 1
        answered[parsing.folded(found)] = found
        written[groups[step][1]] = found
        value = _pooled_value(found, decimal_comma)
        if value is None:
            continue
        cells = cells + groups[step][0]
        weighted = weighted + value * float(groups[step][0])
    reached = middle
    if cells > 0:
        reached = weighted / float(cells)
    return (written, reached, cells)

def _pooled_carried(ladder: '_Ladder', groups: 'list[tuple[int, int, str]]', positions: 'list[int]', centre: float, spacing: float, middle: float, named: 'dict[str, int]', used: 'dict[str, int]', owners: 'dict[str, str]', holes: 'tuple[str, ...]', decimal_comma: bool, needed: int, pool: 'list[int] | None', widest: int) -> 'tuple[dict[int, str], float, int]':
    order = _pooled_pushed_first(ladder, groups, positions, centre, spacing, middle, named, used, owners, holes, decimal_comma, needed, pool, widest)
    taken = dict(used)
    answered = dict(owners)
    written: 'dict[int, str]' = {}
    cells = 0
    weighted = 0.0
    owed = 0.0
    left = 0
    for step in range(len(groups)):
        owed = owed + middle * float(groups[step][0])
        left = left + groups[step][0]
    for turn in range(len(order)):
        step = order[turn]
        if left < 1:
            break
        rest_cells = 0
        rest_weighted = 0.0
        for after in range(turn, len(order)):
            rest_cells = rest_cells + groups[order[after]][0]
            rest_weighted = rest_weighted + float(groups[order[after]][0] * positions[order[after]])
        rest_centre = 0.0
        if rest_cells > 0:
            rest_centre = rest_weighted / float(rest_cells)
        share = owed / float(left)
        wanted = share + spacing * (positions[step] - rest_centre)
        found = ''
        if math.isfinite(wanted):
            found = _pooled_spelling(ladder, wanted, groups[step][2], named, taken, answered, holes, decimal_comma, needed, pool, widest)
        value: 'float | None' = None
        if found:
            taken[found] = 1
            answered[parsing.folded(found)] = found
            written[groups[step][1]] = found
            value = _pooled_value(found, decimal_comma)
        if value is None:
            owed = owed - share * float(groups[step][0])
        else:
            owed = owed - value * float(groups[step][0])
            cells = cells + groups[step][0]
            weighted = weighted + value * float(groups[step][0])
        left = left - groups[step][0]
    reached = middle
    if cells > 0:
        reached = weighted / float(cells)
    return (written, reached, cells)

def _pooled_pushed_first(ladder: '_Ladder', groups: 'list[tuple[int, int, str]]', positions: 'list[int]', centre: float, spacing: float, middle: float, named: 'dict[str, int]', used: 'dict[str, int]', owners: 'dict[str, str]', holes: 'tuple[str, ...]', decimal_comma: bool, needed: int, pool: 'list[int] | None', widest: int) -> 'list[int]':
    taken = dict(used)
    answered = dict(owners)
    pushed: 'list[float]' = []
    for step in range(len(groups)):
        wanted = middle + spacing * (positions[step] - centre)
        found = ''
        if math.isfinite(wanted):
            found = _pooled_spelling(ladder, wanted, groups[step][2], named, taken, answered, holes, decimal_comma, needed, pool, widest)
        value: 'float | None' = None
        if found:
            taken[found] = 1
            answered[parsing.folded(found)] = found
            value = _pooled_value(found, decimal_comma)
        if value is None:
            pushed += [-1.0]
            continue
        away = value - wanted
        if away < 0.0:
            away = 0.0 - away
        pushed += [away]
    order: 'list[int]' = []
    seated: 'dict[int, int]' = {}
    for _turn in range(len(groups)):
        best = -1
        for step in range(len(groups)):
            if step in seated:
                continue
            if best < 0:
                best = step
                continue
            if pushed[best] < 0.0:
                continue
            if pushed[step] < 0.0 or pushed[step] > pushed[best]:
                best = step
        seated[best] = 1
        order += [best]
    return order

def _pooled_best(ladder: '_Ladder', groups: 'list[tuple[int, int, str]]', positions: 'list[int]', centre: float, spacing: float, middle: float, named: 'dict[str, int]', used: 'dict[str, int]', owners: 'dict[str, str]', holes: 'tuple[str, ...]', decimal_comma: bool, needed: int, pool: 'list[int] | None', widest: int, window: float) -> 'tuple[dict[int, str], int]':
    best, reached, cells = _pooled_offered(ladder, groups, positions, centre, spacing, middle, 0.0, named, used, owners, holes, decimal_comma, needed, pool, widest)
    closest = reached - middle
    if closest < 0.0:
        closest = 0.0 - closest
    if cells < 1 or closest <= window:
        return (best, cells)
    shift = middle - reached
    for _again in range(_POOLED_SHIFTS):
        if closest <= window or not math.isfinite(shift):
            break
        moved, moved_at, moved_cells = _pooled_offered(ladder, groups, positions, centre, spacing, middle, shift, named, used, owners, holes, decimal_comma, needed, pool, widest)
        if moved_cells < 1:
            break
        gap = moved_at - middle
        if gap < 0.0:
            gap = 0.0 - gap
        if gap < closest:
            best, closest, cells = (moved, gap, moved_cells)
        shift = shift + (middle - moved_at)
    if closest <= window:
        return (best, cells)
    carried, carried_at, carried_cells = _pooled_carried(ladder, groups, positions, centre, spacing, middle, named, used, owners, holes, decimal_comma, needed, pool, widest)
    gap = carried_at - middle
    if gap < 0.0:
        gap = 0.0 - gap
    if carried_cells > 0 and gap < closest:
        best, closest, cells = (carried, gap, carried_cells)
    return (best, cells)

def _pooled_numbers_placed(ladder: '_Ladder', scale: 'contract.PooledNumbers', groups: 'list[tuple[int, int, str]]', named: 'dict[str, int]', used: 'dict[str, int]', owners: 'dict[str, str]', holes: 'tuple[str, ...]', decimal_comma: bool, needed: int, pool: 'list[int] | None', widest: int, window: float) -> 'dict[int, str]':
    placed: 'dict[int, str]' = {}
    middle = scale.mean
    if middle is None or not groups:
        return placed
    sizes = tuple([pair[0] for pair in groups])
    positions = _pooled_positions(len(groups))
    centre = _pooled_centre(sizes, positions)
    furthest = 0.0
    for step in range(len(positions)):
        away = positions[step] - centre
        if away < 0.0:
            away = 0.0 - away
        if away > furthest:
            furthest = away
    spacing = _pooled_step(ladder, middle, furthest)
    best, cells = _pooled_best(ladder, groups, positions, centre, spacing, middle, named, used, owners, holes, decimal_comma, needed, pool, widest, window)
    if cells < 1:
        return placed
    for step in range(len(groups)):
        place = groups[step][1]
        if place not in best:
            continue
        found = best[place]
        used[found] = 1
        owners[parsing.folded(found)] = found
        placed[place] = found
    return placed
'''

QUALITY_REPORT = r'''
def _missed_lines(outcome: validation.Outcome) -> 'list[str]':
    missed = [check for check in outcome.checks if check.verdict == validation.MISSED]
    if not missed:
        return ['Nothing was missed, so this part of the section is empty. Every', 'obligation and its outcome is listed under it, column by column.', '']
    lines = ['WHAT THIS FILE DOES NOT CARRY. Each line names one obligation the', 'description sets, what it asks for, and what the file holds --', 'or, where what the file holds may not be printed here, why.', '']
    for check in missed:
        lines = lines + [f'{_where(check)}'] + _detail_of(check) + ['']
    return lines

def _column_order(outcome: validation.Outcome) -> 'list[str]':
    seen: list[str] = []
    for check in outcome.checks:
        if check.column not in seen:
            seen += [check.column]
    return seen

def _detail_lines(outcome: validation.Outcome) -> 'list[str]':
    lines = [_RULE, 'FACT BY FACT', _RULE, '']
    lines = lines + _missed_lines(outcome)
    lines += ["EVERY OBLIGATION, IN THE DESCRIPTION'S OWN ORDER.", '']
    for column in _column_order(outcome):
        heading = 'the file as a whole'
        if column:
            heading = f"'{_shown(column)}'"
        lines += [heading]
        for check in outcome.checks:
            if check.column != column:
                continue
            lines = lines + _detail_of(check)
        lines += ['']
    return lines

def quality_report(description: contract.Profile, outcome: validation.Outcome) -> str:
    lines = _opening_lines(description, outcome.measured_name) + ['']
    lowered = _lowered_floor_lines(description)
    if lowered:
        lines = lines + lowered + ['']
    population = _small_population_lines(description)
    if population:
        lines = lines + population + ['']
    lines = lines + _summary_lines(outcome.census) + ['']
    lines = lines + _bounds_lines() + ['']
    lines = lines + _detail_lines(outcome)
    lines = lines + _not_checkable_lines(outcome) + ['']
    lines = lines + _expectations_lines() + ['']
    lines = lines + _handling_lines(description, outcome.census.withheld)
    text = ''
    for line in lines:
        text = text + line + _NEWLINE
    return text
'''
