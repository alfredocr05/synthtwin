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

- `TALLY` is `taxonomy._tally` as 66bca69 shipped it, holding every
  folded label's map of spellings, the oracle of lane S4d's plain labels
  (`tests/test_stage4_describe_memory.py`, plan P4-D390): every label's
  map, as `taxonomy._label_spellings` answers it, must be the map this
  held.

`READ_THE_COLUMN`, `taxonomy._read_the_column` with its level pass as
668f276 shipped it, stood here too until plan P4-D390 deleted that pass.

- `RECORD_OF_TEN`, `EXACT_MAPS`, `MOMENTS_KEYED`, `DAYS_A_ROW` and
  `SPLIT_A_CHARACTER_AT_A_TIME` are, as 4682d6ad shipped them, the
  record of ten fields `taxonomy._classify` built, `_distinct_numbers`
  and `_mode_of` over a map keyed by every exact number,
  `ordered_moments` keying every moment, `_census_days` holding a day
  number a row and `splits_into_numbers` building each part a
  character at a time: the oracles of lane H3
  (`tests/test_stage4_describe_memory.py`, plan P4-D423), whose answers
  the product's must be wherever both answer.
- `AFFIX_PAIRS`, `STAMP_CLOCK`, `LABEL_READERS`, `CENSUS_RANKED` and
  `FEW_UNITS` (`calendar_rules.few_units` over a set of every pair) are,
  as 4682d6ad shipped them, the affix reading's pair walk and reach over a map of
  every pair, the slashed stamps' one written clock over a tuple of
  halves, parts and pairs a stamp, and four rules reading the tally's
  labels by their folded text: the oracles of lane H3's repair (the
  same file and plan), asked of a tally carrying `taxonomy._label_maps`'s
  two maps under their old names.

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


TALLY = r'''
def _tally(
    classified: list[_Cell],
    n_rows: int,
    settings: Settings,
    decimal_comma: bool = False,
) -> _Cells:
    """Count the one classification of each cell, in one pass.

    This function reads the records and never the text: it is arithmetic
    over `_classify`'s answers. That is what lets a numeric sentinel be
    dropped by filtering the records and counting again, instead of
    reading the whole column a second time and hoping the second reading
    agrees with the first (review item P1-R6-F10).
    """
    present: list[str] = []
    numbers: list[float] = []
    out_of_range = 0
    contradictory = 0
    not_a_number = 0
    negative = 0
    positive = 0
    sign_unknown = 0
    sign_unsettled_numeric = 0
    whole = 0
    fraction = 0
    whole_unknown = 0
    negative_unrepresentable = 0
    all_digits = 0
    code_alphabet = 0
    folded_counts: dict[str, int] = {}
    spellings_by_folded: dict[str, dict[str, int]] = {}
    for cell in classified:
        present += [cell.text]
        if cell.kind == parsing.NUMBER:
            if cell.value is not None:
                numbers += [cell.value]
        elif cell.kind == parsing.NUMBER_OUT_OF_RANGE:
            out_of_range = out_of_range + 1
        elif cell.kind == parsing.NUMBER_CONTRADICTORY:
            contradictory = contradictory + 1
        else:
            not_a_number = not_a_number + 1
        # EVERY present cell is counted here, ordinary text included.
        # The sign and whole-number families are two MARGINS over the
        # present cells, and the contract states them that way: U1 and
        # U2 both sum to `n_present`, and the three key meanings all
        # read "present cells whose notation settles ..." (contract v4
        # section 6.2). A cell of ordinary text settles neither
        # question, so it answers for `n_whole_unknown` and
        # `n_sign_unknown` -- which is exactly what the generation
        # method's construction table ties it to (generation method
        # G10.5 step 1, the "ordinary text" row), and exactly what
        # `_classify` already gives it: SIGN_UNKNOWN and WHOLE_UNKNOWN.
        #
        # This line used to read `if cell.kind != parsing.NOT_A_NUMBER`,
        # which left a text cell out of both families while `n_present`
        # counted it. The producer then wrote a description its own
        # loader refused, and the refusal told the reader their file had
        # been changed since it was written -- blaming a person who had
        # done nothing. Found while transcribing this rule for the
        # version 6 contract, reproduced end to end, and fixed here
        # rather than in the invariant, because the contract, the sealed
        # generation method and the shipped loader all three agree with
        # each other and against this line.
        if cell.sign == parsing.SIGN_NEGATIVE:
            negative = negative + 1
            if cell.kind != parsing.NUMBER:
                negative_unrepresentable = negative_unrepresentable + 1
        elif (
            cell.sign == parsing.SIGN_POSITIVE
            or cell.sign == parsing.SIGN_ZERO
        ):
            positive = positive + 1
        else:
            sign_unknown = sign_unknown + 1
            if cell.kind != parsing.NOT_A_NUMBER:
                sign_unsettled_numeric = sign_unsettled_numeric + 1
        if cell.whole == parsing.WHOLE_YES:
            whole = whole + 1
        elif cell.whole == parsing.WHOLE_NO:
            fraction = fraction + 1
        else:
            whole_unknown = whole_unknown + 1
        if cell.all_digits:
            all_digits = all_digits + 1
        if cell.code_alphabet:
            code_alphabet = code_alphabet + 1
        if cell.folded in folded_counts:
            folded_counts[cell.folded] = folded_counts[cell.folded] + 1
        else:
            folded_counts[cell.folded] = 1
            spellings_by_folded[cell.folded] = {}
        spellings = spellings_by_folded[cell.folded]
        if cell.text in spellings:
            spellings[cell.text] = spellings[cell.text] + 1
        else:
            spellings[cell.text] = 1
    return _Cells(
        decimal_comma=decimal_comma,
        classified=classified,
        present=present,
        n_rows=n_rows,
        settings=settings,
        numbers=numbers,
        n_out_of_range=out_of_range,
        n_contradictory=contradictory,
        n_not_numeric=not_a_number,
        n_negative=negative,
        n_positive=positive,
        n_sign_unknown=sign_unknown,
        n_whole=whole,
        n_fraction=fraction,
        n_whole_unknown=whole_unknown,
        n_sign_unsettled_numeric=sign_unsettled_numeric,
        n_negative_unrepresentable=negative_unrepresentable,
        raw_distinct=len(set(present)),
        folded_counts=folded_counts,
        spellings_by_folded=spellings_by_folded,
        all_digits=all_digits,
        code_alphabet=code_alphabet,
    )
'''


RECORD_OF_TEN = r'''
@dataclasses.dataclass(frozen=True, slots=True)
class _Cell:
    """One present cell, decided once and never read from the text again.

    This is the record STRUCTURAL RULE A is about. It is built by
    `_classify`, once per cell, and it is frozen: what a cell is
    numerically, the number it parsed to, that same number exactly, its
    sign, whether it is a whole number, and the lexical facts the role
    rules ask about.

    It carried two more lexical facts until review item P1-R6-F8 --
    whether the cell was one word, and whether it held a letter -- and
    they existed for one purpose: guessing which all-different columns
    were record numbers. That guess is withdrawn, so the facts that fed
    it are gone rather than left lying about for a later rule to pick
    up again.

    Everything below consults this record. Round 5's code asked the
    parser three separate questions per cell -- classify, sign,
    whole-number -- and the last two classified the cell again from its
    text, so "classified exactly once" was a comment rather than a
    property of the code (review item P1-R6-F10).
    """

    text: str
    # THE SPELLING THE NUMBER RULES READ, which is `text` itself on
    # every undeclared column and the swapped spelling on one declared
    # `--decimal-comma` (plan P4-D26). The two are separate fields
    # because they answer different questions and a single field got
    # one of them wrong: `text` is what the FILE holds, and the label
    # roles publish it, so a declaration about numbers must never
    # rewrite a level, a code or a note; this is how the NUMBER is
    # written, and every census of numeric spelling reads it.
    #
    # Reading the censuses off `text` on a declared column made the
    # twin lose the fraction altogether. `1,5` carries no point, so its
    # style counted as `plain`, the whole column published `plain` and
    # `integer_valued: false` together, and the twin wrote `222` for a
    # column running from 2.89 to 300.23 -- the defect P4-D26 exists to
    # prevent, arriving through the census rather than through the
    # reading.
    numeric_text: str
    # One of parsing.NUMBER, NUMBER_OUT_OF_RANGE, NUMBER_CONTRADICTORY,
    # NOT_A_NUMBER.
    kind: str
    # The number the cell holds, and None whenever no number was held.
    value: "float | None"
    # The same number EXACTLY, as the canonical triple above, and None
    # whenever no number was held. `value` is what the profile publishes
    # and what the statistics are computed from; this is what a declared
    # value is compared with, and what the numeric-sentinel rule decides
    # a candidate's own cells by, because a comparison of rounded values
    # makes one number out of two (review items P1-R7-F3 and P1-R8-F2).
    exact: "tuple[int, tuple[str, ...], int] | None"
    sign: str
    whole: str
    # The cell after trimming and case folding: the key the levels, the
    # binary rule and the categorical rule all count with.
    folded: str
    # Both of these are published as COUNTS on a free-text column, which
    # is what a generator needs to build text of the same shape. Neither
    # decides a role.
    all_digits: bool
    code_alphabet: bool


def _classify(text: str, decimal_comma: bool = False) -> _Cell:
    """Classify one present cell, once, into the record every rule reads.

    ``decimal_comma`` says this column was DECLARED as writing its
    numbers with a comma for the point (plan P4-D26). Only the NUMERIC
    reading is taken from the swapped text; `text`, `folded` and the
    two alphabet tests keep the cell exactly as the file wrote it,
    because a declaration about numbers must not rewrite a level, a
    code or a note. Undeclared columns pass `False` and nothing about
    them moves.

    The parser is asked what the cell is exactly once. Everything else
    is derived from that answer:

    * a cell this format can hold has its sign and its whole-number
      status settled by the NUMBER it parsed to -- a parsed zero is
      exactly a cell whose digits are all zeros, because a value that
      collapses to zero from something larger is refused by the reader
      and comes back as out-of-range instead -- and it carries the exact
      number its spelling denotes beside the rounded one, so that a
      declared value is compared with the number and not with a rounding
      of it;
    * a cell too large or too small to hold has no value to read, so its
      whole-number status comes from which end of the range it fell off
      (too large is whole, too small lies strictly between zero and one)
      and its sign from the notation;
    * contradictory notation and ordinary text settle neither, and
      "unknown" is a real answer here, never guessed at.

    Guarantees: accepts text; returns a frozen `_Cell`; raises TypeError
    if handed anything that is not a string instance. The record depends
    on the text and nothing else. No I/O of any kind.
    """
    # THE TEXT THE NUMBER RULES READ, which is the cell itself on every
    # undeclared column and the swapped spelling on a declared one.
    read = parsing.written_with_a_decimal_comma(text) if decimal_comma else text
    kind = parsing.classify_number(read)
    value: float | None = None
    exact: tuple[int, tuple[str, ...], int] | None = None
    sign = parsing.SIGN_UNKNOWN
    whole = parsing.WHOLE_UNKNOWN
    if kind == parsing.NUMBER:
        value = parsing.parse_number(read)
        exact = parsing.exact_of_accepted_number(read)
        if value is not None:
            if value < 0.0:
                sign = parsing.SIGN_NEGATIVE
            elif value == 0.0:
                sign = parsing.SIGN_ZERO
            else:
                sign = parsing.SIGN_POSITIVE
            if parsing.is_whole_number(value):
                whole = parsing.WHOLE_YES
            else:
                whole = parsing.WHOLE_NO
    elif kind == parsing.NUMBER_OUT_OF_RANGE:
        if parsing.overflowed(read):
            whole = parsing.WHOLE_YES
        else:
            whole = parsing.WHOLE_NO
        if _written_negative(read):
            sign = parsing.SIGN_NEGATIVE
        else:
            sign = parsing.SIGN_POSITIVE
    trimmed = parsing.trimmed(text)
    # THE FOLDED LABEL IS THE CELL'S OWN TEXT WHERE FOLDING CHANGES
    # NOTHING (lane S4d, plan P4-D390): the same characters, held once
    # rather than copied beside every cell that is already folded.
    folded = parsing.folded(text)
    if folded == text:
        folded = text
    return _Cell(
        text=text,
        numeric_text=read,
        kind=kind,
        value=value,
        exact=exact,
        sign=sign,
        whole=whole,
        folded=folded,
        all_digits=parsing.is_digit_text(trimmed),
        code_alphabet=parsing.is_code_text(trimmed),
    )
'''


EXACT_MAPS = r'''
def _distinct_numbers(cells: _Cells) -> int:
    """How many different NUMBERS this column's numeric cells hold.

    Guarantees: accepts a tally of one column; returns a count of at
    least zero, never more than the count of different spellings.
    Determinism: the answer depends only on the multiset of cells.
    Raises nothing. No I/O of any kind.
    """
    # READ OFF THE RECORD, never asked of the text again. Every cell
    # already carries the exact number it denotes -- `_classify`
    # computed it once, which is structural rule A's whole point -- so
    # calling `exact_of_spelling` here would classify all over again.
    # A test counts how often a numeric column is read that way, and
    # it is right to: the first draft of this asked twice per cell.
    seen: "dict[tuple[int, tuple[str, ...], int], int]" = {}
    for cell in cells.classified:
        if cell.kind != parsing.NUMBER:
            continue
        if cell.exact is None:
            continue
        seen[cell.exact] = 1
    return len(seen)


def _mode_of(cells: _Cells) -> "tuple[float | None, int]":
    """The number this column held most often, and how many cells held it.

    THE VALUE IS AN IDENTITY QUESTION AND THE ANSWER IS THE EXACT ONE.
    Cells are grouped by the canonical triple each already carries --
    the same key `_distinct_numbers` counts with, and the same one the
    declared-value and sentinel rules compare by -- so two spellings of
    one number are one value here, and two numbers that round to one
    binary64 are two. Grouping by the rounded `value` would make one
    mode out of two different numbers.

    THE TIE RULE IS THE SMALLEST, and it is written down rather than
    left to whatever a mapping iterates in. Where several numbers share
    the largest count the smallest of them is the mode: it is
    deterministic, it names no value the ladder does not already
    publish one of, and it gives an independent implementer one answer
    (plan P4-D4.11).

    Guarantees: accepts a tally of one column; returns the mode's own
    published value and its count, or `(None, 0)` where the column
    holds no number at all. The floor is NOT applied here -- this
    answers what the column held, and `_numeric_details` decides what
    may be published. Determinism: the answer depends only on the
    multiset of cells. Raises nothing. No I/O of any kind.
    """
    counts: "dict[tuple[int, tuple[str, ...], int], int]" = {}
    for cell in cells.classified:
        if cell.kind != parsing.NUMBER:
            continue
        if cell.exact is None or cell.value is None:
            continue
        if cell.exact in counts:
            counts[cell.exact] = counts[cell.exact] + 1
        else:
            counts[cell.exact] = 1
    if not counts:
        return None, 0
    most = 0
    for key in counts:
        if counts[key] > most:
            most = counts[key]
    # THE VALUES ARE READ OFF THE CELLS OF THE COMMONEST NUMBERS, in a
    # second walk, rather than held in a map beside the counts (lane S4d,
    # plan P4-D390): on a column whose numbers never repeat that map was
    # one entry a row. Every cell of one exact number holds one value
    # but exact zero's, which is 0.0 or -0.0 as the cell wrote it ("0",
    # "-0"), and the two compare equal: the map kept the LAST cell's
    # value per exact number, so the walk keeps the first exact number
    # it meets among equal values and then each later cell of that same
    # number, and the published zero carries the sign 66bca69 wrote.
    smallest: "float | None" = None
    chosen: "tuple[int, tuple[str, ...], int] | None" = None
    for cell in cells.classified:
        if cell.kind != parsing.NUMBER:
            continue
        if cell.exact is None or cell.value is None:
            continue
        if counts[cell.exact] != most:
            continue
        found = cell.value
        if smallest is None or found < smallest or cell.exact == chosen:
            smallest = found
            chosen = cell.exact
    return smallest, most
'''


MOMENTS_KEYED = r'''
def ordered_moments(
    pairs: "list[tuple[str, str]]", reading: str
) -> "tuple[list[str], str, str, str, str]":
    """These parsed moments in the order a description publishes them.

    THE ONE STATEMENT OF THE ORDER AND OF ITS TIE RULE (plan P4-D255).
    The cells are ordered by the INSTANT each names -- not by its local
    text, which sorted two offsets the wrong way round (review item
    P1-R1-F9) -- then by the text published for it, then by the offset
    it wears. So where several cells share an end's instant, the offset
    published for that end is the LARGEST of theirs at the latest and
    the SMALLEST at the earliest, and that is a rule the generator has
    to meet rather than guess at: `generation._endpoint_offset_notes`
    recounts the twin through this same function, and
    `generation._endpoint_tie_offsets` holds every tied rank to it.

    Guarantees: accepts the parsed (canonical, offset) pairs -- at least
    one -- and the clock they are published on; returns the canonical
    texts in order, the first and last of them, and the offsets those
    two wear. Determinism: a function of the two. Raises nothing. No I/O
    of any kind.
    """
    keyed: list[tuple[int, str, str]] = []
    unkeyed: list[str] = []
    # ONE KEY PER WRITTEN MOMENT (lane S4d, `parsing.SPELLING_MEMO_TEXTS`): the
    # rows that write one moment share its key, a moment met again past
    # the bound from its second sighting (`parsing.SPELLING_MEMO_NOTED`).
    known: "dict[tuple[str, str], tuple[int, str, str]]" = {}
    noted: "dict[tuple[str, str], tuple[int, str, str]]" = {}
    older: "dict[tuple[str, str], tuple[int, str, str]]" = {}
    answered = 0
    for canonical, offset in pairs:
        moment = (canonical, offset)
        if moment in known:
            answered = answered + 1
            keyed += [known[moment]]
            continue
        if moment in noted or moment in older:
            entry = noted[moment] if moment in noted else older[moment]
            known[moment] = entry
            answered = answered + 1
            keyed += [entry]
            continue
        instant = parsing.instant_key(canonical, offset)
        shown = canonical
        if reading == READ_AT_UTC:
            # ...AND A CONVERSION THE CALENDAR CANNOT SPELL IS CLAMPED TO
            # ITS EDGE, never left as the LOCAL text (`parsing.utc_moment`,
            # the dates pass of the stage-3 review, item 7). The sequence
            # this function returns is compared as plain text by
            # everything that reads it, so one local text among the
            # instants made the order and the texts disagree and published
            # a tail whose own loader refused it. -- 3b.7 repair (item 5):
            # spelled from the key just computed (`_utc_text_of`), the same
            # text, so each pair is keyed once.
            at_utc = (
                _utc_text_of(canonical, instant, offset)
                if instant is not None
                else parsing.utc_moment(canonical, offset)
            )
            if at_utc is not None:
                shown = at_utc
        if instant is None:
            unkeyed += [shown]
        else:
            entry = (instant, shown, offset)
            if parsing.memo_takes(len(known), answered):
                known[moment] = entry
            elif parsing.memo_notes(len(noted)):
                noted[moment] = entry
            else:
                older = noted
                noted = {}
            keyed += [entry]
    if keyed:
        ordered = sorted(keyed)
        canonical_order = [entry[1] for entry in ordered]
        return (
            canonical_order,
            ordered[0][1],
            ordered[len(ordered) - 1][1],
            ordered[0][2],
            ordered[len(ordered) - 1][2],
        )
    canonical_order = sorted(unkeyed)
    return (
        canonical_order,
        canonical_order[0],
        canonical_order[len(canonical_order) - 1],
        "",
        "",
    )
'''


DAYS_A_ROW = r'''
def _census_days(
    details: "dict[str, object]",
    pairs: "list[tuple[str, str]]",
    ranked: "list[int] | None" = None,
) -> "tuple[int, ...]":
    """The day of every parsed (canonical, offset) pair, ascending, where
    a weekday census may stand: a column of whole dates or of moments
    (landing 3b.1, plan P4-D355; moments since landing 3b.D2, plan
    P4-D367, whose instants `_census_moments` gives beside; every clock
    and member since landing 3b.7). Empty elsewhere.

    Each is the day the cell is WRITTEN on (`calendar_rules.written_day`),
    never its instant's: a sixtieth second, `23:59:60`, is its own day's
    (Codex's review of landing 3b.D2, item 1). Ascending, they are also
    the written days of the cells in the order of their instants, ties
    broken by the written day -- the order the tails cut -- since a cell's
    instant lies from its written day's first second to the next day's
    first, so a later instant is never on an earlier written day.

    ON EACH CELL'S OWN CLOCK (landing 3b.7, plan P4-D378): on a column of
    two offsets or of the joint member (`_on_own_clocks`) the days are the
    written days IN RANK ORDER (`_census_ranked`), which on such a column
    need not ascend -- `23:30-06:00` is written a day before the
    `05:00+05:30` its instant follows -- so the tails' rows cut them where
    they cut the column. Every other column is counted as before.

    Guarantees: accepts the published details, the parsed pairs and their
    ranking where the caller has it; returns the days. Determinism: a
    function of the three. Raises nothing. No I/O of any kind.
    """
    if not calendar_rules.census_scope(
        calendar_rules.SCOPE_DAYS,
        str(details["resolution"]),
        details["all_at_midnight"] is True,
    ):
        return ()
    if _on_own_clocks(details):
        order = ranked if ranked is not None else _census_ranked(details, pairs)
        if order is None:
            return ()
        return tuple(calendar_rules.written_day(pairs[place][0]) for place in order)
    days: "list[int]" = []
    # ONE DAY NUMBER PER WRITTEN DATE (lane S4d, `parsing.SPELLING_MEMO_TEXTS`;
    # past the bound from a date's second sighting, `parsing.SPELLING_MEMO_NOTED`).
    known: "dict[str, int]" = {}
    noted: "dict[str, int]" = {}
    older: "dict[str, int]" = {}
    answered = 0
    for canonical, _offset in pairs:
        if canonical in known:
            answered = answered + 1
            days += [known[canonical]]
            continue
        if canonical in noted or canonical in older:
            day = noted[canonical] if canonical in noted else older[canonical]
            known[canonical] = day
            answered = answered + 1
            days += [day]
            continue
        day = calendar_rules.written_day(canonical)
        if parsing.memo_takes(len(known), answered):
            known[canonical] = day
        elif parsing.memo_notes(len(noted)):
            noted[canonical] = day
        else:
            older = noted
            noted = {}
        days += [day]
    return tuple(sorted(days))
'''


SPLIT_A_CHARACTER_AT_A_TIME = r'''
def splits_into_numbers(text: str, separator: str) -> "list[str] | None":
    """The parts of one cell under one separator, or None.

    ``separator`` is the WHOLE separator, mark and any spaces around
    it, so `120 / 80` splits on `" / "` and its twin is written back
    the same way (plan P4-D24).

    A part may carry a decimal point, which an I:E ratio of `1:1.5`
    needs and which the first build of this role refused, sending the
    column to free text where it published nothing. **This function was
    called `splits_into_wholes` until 2026-08-26**, and the name was
    the origin of a false sentence on six surfaces: a reader who
    trusted it wrote "whole numbers" into the profile, the front page,
    the changelog and the contract, of a reading that accepts `1:1.5`.

    The type gate is the offline audit's: it accepts no method call on
    a value it cannot trace, and a cell arrives here from a list this
    function did not build.
    """
    if not isinstance(text, str):
        raise TypeError("a cell must be text")
    if not separator:
        return None
    parts: "list[str]" = []
    current = ""
    at = 0
    while at < len(text):
        matched = True
        for step in range(len(separator)):
            if at + step >= len(text) or text[at + step] != separator[step]:
                matched = False
                break
        if matched:
            parts += [current]
            current = ""
            at = at + len(separator)
            continue
        current = current + text[at]
        at = at + 1
    parts += [current]
    if len(parts) < 2:
        return None
    for part in parts:
        if not _reads_as_one_number(part):
            return None
    return parts
'''


# -- lane H3's repair (plan P4-D423): 4682d6ad's own functions, frozen as text --
#
# `AFFIX_PAIRS` is the affix reading's pair walk and its reach as 4682d6ad
# shipped them, a map of every pair; `STAMP_CLOCK` the slashed stamps' one
# written clock, a tuple of halves, parts and pairs a stamp; `LABEL_READERS`
# four rules that read the tally's labels by their folded text
# (`folded_counts`, `spellings_by_folded`), asked of a tally that carries the
# maps `taxonomy._label_maps` gives.


AFFIX_PAIRS = r'''
def _affixed_before_the_address_test(
    cells: _Cells, forced_measurement: bool = False
) -> "_Affixed | None":
    """The one affix pair this column wears, address or not.

    Every rule of the role except the address decline. Two callers ask
    it and each applies that last rule for itself, which is what keeps
    the reading and the reason for refusing it one computation.

    Guarantees:

    - Determinism: every cell is split by `affixed_split`, which is a
      function of the cell alone, and the winning pair is chosen by
      count with ties broken by the pair's own text. Nothing here reads
      a clock or a random source, and no dictionary order reaches the
      result.
    - The test, and both halves are the contract's: at least the
      parse-line COUNT of present cells wear ONE pair, and that pair's
      cell count is at least `small_cell_floor`. Both are counts and
      neither is a compared share, so no rounding of a division decides
      a role.
    - The floor is read HERE, at detection, deliberately. The pair is
      PUBLISHED, so being able to publish a floor-clearing spelling is
      constitutive of the role: a column that could not publish one
      under the recorded settings takes the next rule instead of taking
      this one and then withholding the thing that makes it this role.
    - A column whose cells wear more than one pair past the line's
      slack returns None -- a recorded decline, not a partial reading.
      Publishing a distribution over the `$` cells of a column that
      also holds `EUR` cells would describe part of a column and drop
      the rest.
    """
    present = cells.present
    if not present:
        return None
    settings = cells.settings
    needed = _needed(settings.minimum_parse_rate, len(present))
    # PASS ONE: which pair. Only cells whose core is a number this
    # format can hold propose a pair, because the role exists to
    # describe a distribution and a pair proposed by cells holding no
    # number would describe none.
    proposing: "dict[tuple[str, str], int]" = {}
    for text in present:
        split = _split_once(cells, text)
        if split is None:
            # THE BARE PAIR IS A MEMBER OF THE VOCABULARY (plan
            # P4-D36), proposed by a cell that reads as a number
            # wearing nothing at all. A laboratory column of `13.5`,
            # `4.2 H` and `9.8 L` wears three wrappers and one of them
            # is empty; without it the two flagged thirds could never
            # reach the line between them and the column was described
            # as free text.
            #
            # IT CANNOT SWALLOW A PLAIN NUMERIC COLUMN, because rule 6
            # is asked first: a column most of whose cells are bare
            # numbers is a column of numbers and never reaches here.
            if _reads_as_a_number(
                parsing.trimmed(text), cells.decimal_comma
            ):
                key = ("", "")
                proposing[key] = (
                    proposing[key] + 1 if key in proposing else 1
                )
            continue
        prefix, core, suffix = split
        key = (prefix, suffix)
        if key in proposing:
            proposing[key] = proposing[key] + 1
        else:
            proposing[key] = 1
    if not proposing:
        return None
    # WHICH PAIRS ARE PUBLISHABLE (plan P4-D36). A pair worn by fewer
    # cells than the smallest group size cannot be published, so its
    # cells are STRAGGLERS -- the population the parse line already
    # tolerates and the straggler construction already writes. That is
    # what keeps this rule from needing a held-back pool of its own.
    #
    # Walked over SORTED keys throughout, so nothing here depends on
    # the order a dictionary happened to fill.
    speaking: "list[tuple[str, str]]" = []
    for key in sorted(proposing):
        if proposing[key] >= settings.small_cell_floor:
            speaking += [key]
    if not speaking:
        return None
    # EVERY WRAPPER OF A SET STANDS APART FROM THE NUMBER (plan
    # P4-D36), and this guard is what keeps a set of CODE SCHEMES and
    # a set of markers from being read as a quantity.
    #
    # A LETTER WRITTEN FLUSH AGAINST A NUMBER IS NOT A UNIT. A unit or
    # an annotation is either separated from the number -- `13.5 H`,
    # `70 kg` -- or is a mark that is no letter at all -- `$98`, `45%`.
    # Two shapes were read as quantities without this and neither is
    # one: a diagnosis column of `E10.0`, `I11.2`, `J44.9` published a
    # LADDER over its code numbers, and a column of a hundred ages
    # beside twenty `refused3` markers put the marker's own digit into
    # the ladder with them.
    #
    # ASKING IT OF EVERY WRAPPER RATHER THAN OF ONE is what the second
    # of those settled: the bare wrapper stands apart by itself, so a
    # column of numbers beside ANY flush marker would have been
    # admitted on the numbers' own account.
    #
    # THE PRICE, and it is small: a column of `$98` beside `EUR99` --
    # a currency written flush -- is not read as a quantity. It was
    # free text before this landing and stays that way, so nothing is
    # lost that anybody had.
    #
    # ASKED OF A SET ONLY. A column wearing ONE wrapper is read exactly
    # as it was, so `D0140` is still whatever it was before.
    if len(speaking) > 1:
        # SOME CELL OF THIS COLUMN IS A PLAIN NUMBER, which is what
        # lets a flag be written flush against the digits (review round
        # 1, item 6). See `_stands_apart`: the front of the number is
        # where a code scheme puts its letter, and the back is where an
        # abnormal flag puts one -- but only a column that holds
        # unwrapped numbers is a column of numbers with annotations.
        # A LETTER FLUSH BEHIND THE DIGITS IS AMBIGUOUS AND THE PERSON
        # SETTLES IT (review round 3, item 2). Round 1 relaxed this
        # where the vocabulary held the bare wrapper, on the ground
        # that a column holding unwrapped numbers is a column of
        # numbers with annotations; round 2 then found a register of
        # procedure codes wearing exactly that shape, and round 3 found
        # that the width test written to separate them does neither
        # job. Measured, both ways:
        #
        #   100 bare two-digit readings beside 50 ending `H` and 50
        #   ending `L` -- an ordinary laboratory column -- was REFUSED,
        #   because its cores are all two digits;
        #
        #   50 bare four-digit codes beside 50 five-digit ones and 100
        #   ending `F` -- a register whose leading zeros a spreadsheet
        #   ate -- was ADMITTED, because its bare cores are of two
        #   widths.
        #
        # Nothing in the text tells a flagged measurement from a code
        # register: both are figures with a letter behind them. So the
        # question goes to whoever holds the table, which is this
        # project's own answer where a guess is not confident, and
        # `--measurement` is the flag that carries it. Undeclared, such
        # a column is what it was before this landing.
        for key in speaking:
            if not _stands_apart(key[0], key[1], forced_measurement):
                return None
        # AND EVERY WRAPPER OF A SET IS ONE WORD (plan P4-D36). A unit
        # or an annotation is a word -- `H`, `kg`, `months`, `EUR`,
        # `$` -- and a sentence is not. A column of `free comment
        # number 03 written out` beside its upper-case variants
        # proposes two wrappers of four words each; both clear the
        # floor, and the column published a LADDER over what is a
        # sequence number inside prose.
        #
        # ASKED OF A SET ONLY, so a column wearing ONE wrapper is read
        # exactly as it was: `note 3 of the batch` was this role
        # before this landing and still is.
        for key in speaking:
            if not _one_word(key[0]) or not _one_word(key[1]):
                return None
    # A SET OF WRAPPERS MAY NOT DIFFER BY ITS DIGITS (plan P4-D36),
    # and this guard was written against a false reading the set rule
    # created. A column of feet and inches, `4'5"`, `5'11"` proposes one pair per
    # inches value -- prefix nothing, suffix `'5"` -- and a dozen of
    # them clear the floor and the ceiling together. The column then
    # published a ladder over the FEET of some cells and the inches of
    # others: a description saying something false, where before it
    # said nothing at all.
    #
    # A WRAPPER IS SHARED TEXT. Where a column wears ONE, it may carry
    # digits -- `mL/min/1.73m2` is a real unit and this rule read it
    # before -- so the guard is asked only of a SET, where a digit is
    # the mark of a split that cut through a number.
    if len(speaking) > 1:
        for key in speaking:
            for side in key:
                for mark in side:
                    if mark in "0123456789":
                        return None
    # THE SET IS A VOCABULARY AND NOT PROSE, on the categorical rule's
    # own ceiling. A column proposing dozens of different pairs is a
    # column of text that happens to hold digits, and describing it as
    # a quantity in many wrappers would be describing something else.
    if len(speaking) > _categorical_ceiling(cells):
        return None
    # THE DETECTION LINE is over the cells wearing a PUBLISHABLE pair,
    # together. The contract's test is that at least the parse-line
    # count of present cells are affixed numbers; before plan P4-D36 it
    # asked that of ONE pair, so a laboratory column of `13.5`,
    # `4.2 H` and `9.8 L` -- where no pair carries a third of the
    # column -- reached no rule at all and was described as free text.
    covered = 0
    for key in speaking:
        covered = covered + proposing[key]
    if covered < needed:
        return None
    # THE COMMONEST PAIR IS THE ONE THE BLOCK NAMES, ties broken by the
    # pair's own text so two implementations pick the same one.
    pair = speaking[0]
    best = 0
    for key in speaking:
        if proposing[key] > best:
            pair = key
            best = proposing[key]
    if len(speaking) > 1:
        # AND EVERY WRAPPER'S CELLS ARE WRITTEN THE WAY THE COMMONEST
        # WRAPPER'S ARE (plan P4-D36). A unit or a flag does not change
        # how a value is SPELLED: a column of `13.5`, `4.2 H` and
        # `9.8 L` writes one figure after the point whichever wrapper a
        # cell wears. A NOUN in front of an index does: a column of 240
        # readings written to one figure beside sixty `note 3` cells
        # proposes two wrappers that both stand apart and are both one
        # word, and reading it as a quantity puts the notes' own
        # sequence numbers into the ladder with the readings.
        #
        # THE TEST IS AN OVERLAP AND NOT AN IDENTITY, because a real
        # flagged column may carry a whole value beside its fractional
        # ones: each wrapper's cells must share at least one fraction
        # width with the commonest wrapper's.
        if not _written_alike(present, speaking, pair, cells):
            return None

    # PASS TWO: which cells WEAR it. This is a different population and
    # a larger one, and keeping them apart is the whole of C6-7. A
    # column of `5 mg`, `7 mg` and `many mg` wears the pair three
    # times: `n_affixed` is 3 and one core is not numeric at all. The
    # first pass alone would have said 2, and the three non-holdable
    # core classes would have been unreachable -- no producer could
    # ever have written `n_core_not_numeric` above zero.
    prefix, suffix = pair
    cores: "list[str]" = []
    wrappers: "list[tuple[str, str]]" = []
    counts: "dict[tuple[str, str], int]" = {}
    for text in present:
        trimmed = parsing.trimmed(text)
        chosen = _pair_worn(trimmed, speaking, cells.decimal_comma)
        if chosen is None:
            continue
        core = trimmed[
            len(chosen[0]) : len(trimmed) - len(chosen[1])
        ]
        if not core:
            # `mg` on its own wears no pair: it IS the suffix, with
            # nothing between the two sides for a number to be.
            continue
        cores += [core]
        # ...AND WHICH WRAPPER IT WORE (plan P4-D37), kept beside it so
        # the blocks below can be read one wrapper at a time.
        wrappers += [chosen]
        counts[chosen] = counts[chosen] + 1 if chosen in counts else 1
    # A WRAPPER IS FILTERED ON WHAT WEARS IT, NOT ON WHAT PROPOSED IT
    # (found while building plan P4-D37). `speaking` holds the wrappers
    # that cleared the floor at PROPOSAL -- pass one, over the cells
    # that read as a number wearing them -- and the count published is
    # the count that WEARS them, which is a different population and
    # can be far smaller. A column of `$1` to `$99` beside eleven cells
    # spelled `1` and one spelled `7`, with `1` DECLARED a hole,
    # proposes the bare wrapper twelve times and is worn by it ONCE:
    # the eleven holes are not present cells. The bare wrapper was
    # published with the count 1, which is a group of one named in a
    # description under a floor of eleven.
    #
    # So the floor is applied again here, where the published count
    # exists, and a wrapper that fails it is not published at all: its
    # cells become STRAGGLERS, which is the population this role
    # already has and already writes.
    kept: "dict[tuple[str, str], int]" = {}
    for key in counts:
        if key == pair or counts[key] >= settings.small_cell_floor:
            kept[key] = counts[key]
    if len(kept) != len(counts):
        held: "list[str]" = []
        wearing: "list[tuple[str, str]]" = []
        for place in range(len(cores)):
            if wrappers[place] in kept:
                held += [cores[place]]
                wearing += [wrappers[place]]
        cores = held
        wrappers = wearing
        counts = kept
    n_affixed = len(cores)
    # THE COMMONEST WRAPPER IS CHOSEN FROM WHAT WEARS IT, and it was
    # chosen from what PROPOSED it (review round 5, item 1). The
    # proposal pass counts cells that read as a NUMBER wearing a
    # wrapper; the wear pass counts every cell that wears it, cores
    # that are no number included, and the two orders can differ. AF17
    # then refused what this function had just written: a hundred
    # distinct ` kg` numerals beside ninety-eight ` aa` numerals and
    # two `many aa` cells proposes ` kg` as commonest and WEARS both a
    # hundred times, so the loader's tie rule wants ` aa` -- and
    # `synthtwin profile` wrote a file `synthtwin generate` refused,
    # which is the defect amendment A-P3-11 exists to keep closed.
    #
    # THE TIE RULE IS THE LOADER'S, character for character: most cells
    # first, and where two wrappers wear the same number of cells the
    # pair that sorts first.
    for key in sorted(counts):
        if counts[key] > counts[pair] or (
            counts[key] == counts[pair] and key < pair
        ):
            pair = key
    prefix, suffix = pair
    variants: "list[tuple[str, str, int]]" = []
    for key in sorted(counts):
        if key == pair:
            continue
        variants += [(key[0], key[1], counts[key])]
    # The floor is read HERE, at detection, deliberately: the pair is
    # PUBLISHED, so being able to publish a floor-clearing spelling is
    # constitutive of the role.
    if n_affixed < settings.small_cell_floor:
        return None
    if pair not in counts:
        return None
    return _Affixed(
        prefix=prefix,
        suffix=suffix,
        variants=variants,
        cores=cores,
        wrappers=wrappers,
        n_affixed=n_affixed,
    )

def affixed_reach(cells: _Cells) -> int:
    """How many present cells the BEST affix reading accounted for.

    The count the winning pair reached, whether or not it cleared the
    detection line -- so a column that declined can still say how far
    this reading got. Zero where no cell proposed a pair at all.

    A COLUMN THAT PUBLISHES NOTHING OWES ITS OWNER THE REASON, and the
    reason is a set of counts (contract C6-5). The competing-readings
    remark already names how much of the column read as numbers and how
    much as dates; without this one it stayed silent about the reading
    that came closest on a column of prices, which is the reading its
    owner would recognize.

    Guarantees: accepts a tally of one column; returns a count of its
    present cells. No spelling of the column travels out through it.
    Determinism: a function of the cells alone. Raises nothing. No I/O
    of any kind.
    """
    proposing: "dict[tuple[str, str], int]" = {}
    for text in cells.present:
        split = _split_once(cells, text)
        if split is None:
            continue
        prefix, _core, suffix = split
        key = (prefix, suffix)
        if key in proposing:
            proposing[key] = proposing[key] + 1
            continue
        proposing[key] = 1
    best = 0
    for key in sorted(proposing):
        if proposing[key] > best:
            best = proposing[key]
    return best
'''


STAMP_CLOCK = r'''
def _on_the_written_clock(
    present: "list[str]", parsed: "list[bool]", settings: Settings
) -> "list[bool]":
    """Which of the cells one stamp reading parsed its one written clock keeps.

    The cells on another face are dropped, as `_stamp_clocks` drops them
    once the reading is chosen (`_stamp_clock_places`, one rule).
    Determinism: a function of the three. Raises nothing. No I/O.
    """
    places = [place for place in range(len(present)) if parsed[place]]
    kept, _clock = _stamp_clock_places(
        [present[place] for place in places], settings
    )
    found = [False for _cell in present]
    for index, _cell in kept:
        found[places[index]] = True
    return found

def _stamp_clock_places(
    sources: "list[str]", settings: Settings
) -> "tuple[list[tuple[int, str]], _StampClock]":
    """Which stamps a column's one written clock keeps, and how each is written (landing T1).

    THE STYLE MOST CELLS WROTE (`parsing.clock_style_of_cells`), on the
    12-hour face where the column is declared one. A cell on another face
    is dropped -- counted unread by the caller, as the clock role counts
    it -- and a cell whose hour shows the other width is kept and
    REWRITTEN in the column's, its date half untouched, so no published
    fact tells it apart (plan P4-D250's rule, owner ruling 6 of
    2026-09-17). A column every cell of which writes today's two-figure
    24-hour clock comes back exactly as it went in. The width is the one
    that rewrites no cell into a value the person declared missing
    (`_width_clear_of_absences`, the T1 review's item 1).

    ONE RULE, TWO CALLERS: `_stamp_clocks` holds a reading's cells to it,
    and `_slashed_evidence` counts each reading of a slashed pair under
    it, so the reading that wins the comparison is the one that keeps
    the most cells on its face (the T1 review's item 3).

    Guarantees: accepts the cells a stamp member parsed and the settings;
    returns each kept cell's place among them with the cell as written,
    in order, and the clock. Determinism: a function of the two. Raises
    nothing. No I/O of any kind.
    """
    halves: "list[tuple[str, str]]" = []
    read: "list[tuple[int, int, int, bool, int, str, bool]]" = []
    plain = True
    for value in sources:
        day, clock = parsing.stamp_halves(value)
        parts = parsing.clock_parts(clock)
        # Every cell here parsed under a stamp member, whose clock half
        # this reader read; a face no style has keeps the types honest.
        if parts is None:
            parts = (0, 0, 0, False, 2, "?", False)
        if parts[5] or (parts[4] != 2 and parts[0] < 10):
            plain = False
        halves += [(day, clock)]
        read += [parts]
    if plain and not reads_twelve_hours(settings):
        return (
            [(place, sources[place]) for place in range(len(sources))],
            _StampClock(),
        )
    style = parsing.clock_style_of_cells(read, reads_twelve_hours(settings))
    style, absent = _width_clear_of_absences(
        style,
        [(halves[place][1], read[place]) for place in range(len(sources))],
        [halves[place][0] for place in range(len(sources))],
        settings,
    )
    face = parsing.clock_face(style)
    kept: "list[tuple[int, str]]" = []
    other_faces = False
    widths_in = False
    for place in range(len(sources)):
        parts = read[place]
        second = parsing.clock_second(parts, face)
        if second is None:
            other_faces = True
            continue
        day, clock = halves[place]
        spelled = parsing.written_clock(second, parts[3], style)
        cell = sources[place]
        if spelled != clock:
            cell = f"{day}{spelled}"
            if cell in absent:
                # Both widths spell a declared absence: counted unread.
                continue
            widths_in = True
        kept += [(place, cell)]
    return kept, _StampClock(style, other_faces, widths_in)

def _stamp_clocks(
    good: "list[tuple[str, str]]", sources: "list[str]", settings: Settings
) -> "tuple[list[tuple[str, str]], list[str], _StampClock]":
    """A column of stamps held to its one written clock (landing T1).

    `_stamp_clock_places` says which cells stay and how each is written;
    each kept pair's canonical text is put on the column's face.

    Guarantees: accepts the parsed pairs, their cells and the settings;
    returns the pairs and cells kept, in order, and the clock.
    Determinism: a function of the three. Raises nothing. No I/O.
    """
    places, clock = _stamp_clock_places(sources, settings)
    if clock.style == parsing.DEFAULT_CLOCK_STYLE and len(places) == len(sources):
        unchanged = True
        for place, cell in places:
            if cell != sources[place]:
                unchanged = False
                break
        if unchanged:
            return good, sources, clock
    kept: "list[tuple[str, str]]" = []
    written: "list[str]" = []
    for place, cell in places:
        canonical, offset = good[place]
        kept += [(parsing.stamp_canonical(canonical, clock.style), offset)]
        written += [cell]
    return kept, written, clock
'''


LABEL_READERS = r'''
def _published_distinct(cells: _Cells) -> int:
    """How many different spellings a label column's own block says it holds.

    THE COUNT DERIVED FROM THE PROTECTED SPELLINGS AND NOT FROM THE RAW
    ONES (plan P4-D276, the repair of the extra review round of
    2026-09-18). `n_distinct` counted the column's different cells
    exactly, and a published level's `variants` census counts the
    spellings the floor let it name -- so the difference between them
    counted the spellings the absorption took away, and while the
    absorption reached one-row spellings alone that difference WAS a
    count of one. **Measured** at a floor of eleven on 490 `F`, 500 `M`
    and one `f`: the block published `variants {"F": 491}` and
    `{"M": 500}`, no withheld spelling anywhere, and `n_distinct 3` --
    three spellings, two of them named, and the one left over is the row
    that wrote `f`.

    So the count is taken over the spellings the block SPEAKS OF: for
    every level the floor publishes, the spellings that survive
    `_absorb_lone_spellings`, and for every level the floor holds back,
    its own spellings, which no key of this block names and which no
    reader can subtract a published census from.

    Guarantees: accepts the column's tally; returns a count between the
    number of folded identities and `raw_distinct`. Determinism: a fixed
    function of the tally, walked in sorted order. Raises nothing. No I/O
    of any kind.
    """
    counted = 0
    for label in sorted(cells.folded_counts):
        spellings = _label_spellings(
            cells.folded_counts, cells.spellings_by_folded, label
        )
        if cells.folded_counts[label] >= cells.settings.small_cell_floor:
            spellings = _absorb_lone_spellings(spellings, cells.settings)
        for _spelling in sorted(spellings):
            counted = counted + 1
    return counted

def _a_level_is_below_the_floor(cells: _Cells) -> bool:
    """Whether any folded value of this column covers fewer rows than the floor.

    Asked by the clock rule for cells a workbook stores as clock times
    (plan P4-D382): a level the floor would hold back is one the twin
    could only write as made-up text. At a floor of one there can be no
    such level, so the answer there is always no. It is also the cheap
    gate in front of `_read_the_column`'s clock pass (plan P4-D373),
    whose route counts out only levels below the floor.

    Guarantees: accepts the tally; returns a bool. Determinism: a fixed
    function of the tally and its settings. Raises nothing. No I/O.
    """
    floor = cells.settings.small_cell_floor
    if floor <= 1:
        return False
    counts = cells.folded_counts
    for label in sorted(counts):
        if counts[label] < floor:
            return True
    return False

def _rare_beside_clocks(
    cells: _Cells,
    classified: "list[_Cell]",
    n_rows: int,
    settings: Settings,
    decimal_comma: bool,
) -> "tuple[str, ...]":
    """The rare words a column of clock times holds, or nothing (P4-D373).

    The folded values below the floor no spelling of which a clock reader
    takes, where they hold at most one present cell in
    `RARE_WORDS_BESIDE_CLOCKS` and the column without exactly their cells
    has a clock reading (`_clock_reading`); nothing otherwise, and nothing
    where there are none. The clock pass counts these cells missing and
    lets every rule read the column again (`_read_the_column`), where
    every rule then reads it as clock times (`_read_as_clock_times`, the
    second repair round). It is
    asked of every first reading as labels or free text, not only where
    a level is counted out (the repair round of landing 3b.5):
    a column of `7:30 AM` beside 0.6 % `UNK` and 0.3 % `99:99` was free
    text at 300 and 1,000 rows, and its twin wrote every cell `group-N`.

    THE CELLS NO CLOCK READER TAKES ARE COUNTED FIRST, and the count
    stops as soon as they are more than the column could hold and still
    clear the clock line once its rare words were counted out -- so a
    column of words is answered after a few of its spellings, however
    many it has, and only a column almost all times is read further.

    Guarantees: a function of the arguments, in sorted order. Raises
    nothing. No I/O of any kind.
    """
    present = len(cells.present)
    if not present:
        return ()
    rate = settings.minimum_parse_rate
    allowed = present - clock_line(
        rate, present - present // RARE_WORDS_BESIDE_CLOCKS
    )
    unread = 0
    for folded in cells.folded_counts:
        spellings = _label_spellings(
            cells.folded_counts, cells.spellings_by_folded, folded
        )
        for spelling in spellings:
            if parsing.clock_parts(spelling) is None:
                unread = unread + spellings[spelling]
                if unread > allowed:
                    return ()
    floor = settings.small_cell_floor
    rare: "dict[str, bool]" = {}
    counted = 0
    for folded in sorted(cells.folded_counts):
        if cells.folded_counts[folded] >= floor:
            continue
        spellings = _label_spellings(
            cells.folded_counts, cells.spellings_by_folded, folded
        )
        if any(parsing.clock_parts(spelling) is not None for spelling in spellings):
            continue
        rare[folded] = True
        counted = counted + cells.folded_counts[folded]
    if not rare or counted * RARE_WORDS_BESIDE_CLOCKS > present:
        return ()
    # THE CELLS LEFT MUST CLEAR THE CLOCK LINE before any is tallied again.
    if present - unread < clock_line(rate, present - counted):
        return ()
    kept = [cell for cell in classified if cell.folded not in rare]
    if not kept:
        return ()
    reduced = _tally(kept, n_rows, settings, decimal_comma)
    if _clock_reading(reduced) is None:
        return ()
    return tuple(sorted(rare))

def _floor_clearing_non_numeric(cells: _Cells) -> "tuple[str, ...]":
    """Folded spellings that repeat often enough to name and hold no number.

    "Often enough to name" is the publication floor and not a rule of
    this remark's own: a spelling the floor would hold back is a
    spelling the advice may not describe, so the two lines are the same
    line. "Holds no number" is asked of the CELLS rather than of the
    folded key, because the key is a trimmed and case-folded string and
    asking it a second time would be a second reading of a cell this
    module reads once.

    TWO THINGS ARE NARROWER THAN THE FLOOR, and both are here so the
    contract's own sentence is TRUE of the column it is written on.
    NF29's clause 9 says the covered cells "are written one of a few
    ways that repeat often enough to name", and neither half of that
    survives the floor alone:

    * **A spelling has to REPEAT**, which at a floor of one it need
      not (amendment A-P4-37 lowered the default floor to 1, four
      amendments after A-P4-1 wrote this trigger against it; plan
      P4-D316 returned it to 11). Without
      this, a column of a hundred numbers beside a hundred ALL
      DIFFERENT words would have every word counted as a "way that
      repeats", and the sentence would call a hundred one-off
      spellings a few repeated ones.
    * **There have to be A FEW WAYS**, which is the categorical
      ceiling -- this document's own line for "a small set of values in
      this column", computed and not invented. Without it a column
      whose gaps wear fifty different spellings is told they are "a
      few".

    Both narrow the advice rather than widening it, so no column gains
    a sentence by them; some columns that would have been told
    something loosely true are told nothing, which is the direction an
    advisory remark should err in.

    Guarantees: accepts the tally of one column; returns the folded
    identities in sorted order, which is the order every walk over them
    is taken in, and returns none at all where there are more of them
    than the ceiling admits. Raises nothing. No I/O of any kind.
    """
    # A MAPPING RATHER THAN A SET, and the offline audit is why: a set
    # is filled by a METHOD CALL on a value that audit cannot trace to
    # an allowlisted API, and no method call on an untraced value is
    # accepted. Subscript assignment is what `_tally` above builds its
    # own folded map with, for the same reason.
    numeric_somewhere: "dict[str, bool]" = {}
    for cell in cells.classified:
        if cell.kind != parsing.NOT_A_NUMBER:
            numeric_somewhere[cell.folded] = True
    floor = cells.settings.small_cell_floor
    if floor < 2:
        floor = 2
    found = tuple(
        folded
        for folded in sorted(cells.folded_counts)
        if cells.folded_counts[folded] >= floor
        and folded not in numeric_somewhere
    )
    if len(found) > _categorical_ceiling(cells):
        return ()
    return found
'''


CENSUS_RANKED = r'''
def _census_ranked(
    details: "dict[str, object]",
    pairs: "list[tuple[str, str]]",
    instants: "list[int] | None" = None,
) -> "list[int] | None":
    """The places of the parsed pairs in the order the description RANKS
    them, on a column counted on its cells' own clocks (`_on_own_clocks`;
    landing 3b.7, plan P4-D378), or None elsewhere and where a pair names
    no instant.

    RANK BY THE INSTANT, COUNT BY THE TEXT. The order is `ordered_moments`'
    one tie rule (plan P4-D255): the instant each pair names, then the text
    published for it -- its conversion to the shared clock where the column
    is published there -- then its offset. The published tails' rows then
    cut this order exactly where they cut the column: sorting the written
    texts instead put two cells of one instant under two offsets apart,
    and every census would have counted a body the tails do not leave. A
    bare date of the joint member names its midnight with no offset, as
    `ordered_moments` ranks it. Each census then counts a cell at the day,
    hour, minute and second its own text is WRITTEN at (`_census_days`,
    `_census_hours`, `_census_clock_fields`).

    Computed once a column and handed to every census (the 3b.7 design
    skeptic's minor 7: one instant key a pair, about 2.5 seconds a million
    pairs). Guarantees: accepts the published details and the parsed
    pairs; returns a permutation of their places or None. Determinism: a
    function of the two. Raises nothing. No I/O of any kind.

    ONE INSTANT KEY A PAIR (the repair of landing 3b.7, skeptic 1's item
    5): the conversion to the shared clock is spelled from the key already
    computed (`_utc_text_of`), and where the caller hands ``instants`` it is
    filled, in rank order, with each pair's instant on the clock
    `_census_moments` reads, so that census computes none of its own. Three
    keys a pair before: `parsing.instant_key` ran 1,000,002 times in one
    describe of 200,000 pairs, against 400,000 before the landing.
    """
    if not _on_own_clocks(details):
        return None
    if details["resolution"] not in (RESOLUTION_DATE, RESOLUTION_DATETIME):
        return None
    shared = details["datetimes_read_at"] == READ_AT_UTC
    keyed: "list[tuple[int, str, str, int]]" = []
    place = 0
    for canonical, offset in pairs:
        instant = parsing.instant_key(canonical, offset)
        if instant is None:
            return None
        shown = canonical
        if shared:
            at_utc = _utc_text_of(canonical, instant, offset)
            if at_utc is not None:
                shown = at_utc
        keyed += [(instant, shown, offset, place)]
        place = place + 1
    ordered = sorted(keyed)
    if instants is not None:
        for instant, _shown, offset, at in ordered:
            if shared or offset == "":
                instants += [instant]
                continue
            # On the column's own clock `_census_moments` reads the wall
            # clock, with no offset: the one pair a second key is asked of.
            local = parsing.instant_key(pairs[at][0], "")
            instants += [instant if local is None else local]
    return [entry[3] for entry in ordered]
'''


FEW_UNITS = r'''
def few_units(
    groups: "tuple[tuple[int, int, int], ...]",
    body: "list[int]",
    units: "list[int]",
) -> bool:
    """Whether the census's groups hold too few different written units (P4-D367).

    THE PRODUCER'S FEW-UNITS RULE, on the REAL body: `body` is the day
    of every body cell and `units` its written unit (its instant in
    whole units of the column's precision, or its day where every value
    stands at midnight), in the same order. True where at least two
    groups are non-empty and they hold fewer than `FEWEST_MEAN_UNITS`
    different written units each on average. A CONSERVATIVE rule, set on
    the measured cases where a twin missed its count of different values
    (module text above), not a proof that no twin can meet the census;
    a rule of what the twin is sure to meet, never of what a reader
    could work out, so the loader cannot ask it, and need not.

    Guarantees: accepts the census, the body's days and its written
    units, one each a cell; returns the answer. Determinism: a function
    of the three. Raises nothing. No I/O of any kind.
    """
    where = where_of(groups)
    held = [0 for _group in groups]
    for index, _unit in {
        (where[weekday_of(day)], unit) for day, unit in zip(body, units)
    }:
        held[index] = held[index] + 1
    filled = [held[index] for index in range(len(groups)) if groups[index][2] > 0]
    return len(filled) >= 2 and sum(filled) < FEWEST_MEAN_UNITS * len(filled)
'''
