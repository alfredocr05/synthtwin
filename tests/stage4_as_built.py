"""A function of the product as it stood before stage 4's first tier, frozen as text.

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

`READ_THE_COLUMN`, `taxonomy._read_the_column` with its level pass as
668f276 shipped it, stood here too until plan P4-D390 deleted that pass.

The text is compiled into a copy of its module's own names, so the
helpers it calls are today's, and the tests in that file require a
change of meaning made to the product function to break the comparison.
Nothing here is imported by the product.
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
