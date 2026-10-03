"""Two functions of the product as they stood before stage 4's first tier, frozen as text.

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
- `READ_THE_COLUMN` is `taxonomy._read_the_column` as 668f276 shipped
  it -- its level pass walking the sorted tuple of the levels counted
  out, every role asked of `_decide` -- with the one argument plan
  P4-D382 added beside it (2026-10-02), `stored_as`, passed through as
  the merged tree passes it.

Each is compiled into a copy of its module's own names, so the helpers
it calls are today's, and the tests in that file require a change of
meaning made to either product function to break the comparison.
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


READ_THE_COLUMN = r'''
def _read_the_column(
    values: list[str],
    n_rows: int,
    settings: Settings,
    forced_identifier: bool = False,
    forced_code: bool = False,
    forced_measurement: bool = False,
    forced_decimal_comma: bool = False,
    described_as_pair: bool = False,
    kept_placeholder_days: "tuple[str, ...]" = (),
    judged_candidates: "tuple[str, ...]" = (),
    stored_as: str = "",
) -> _ColumnReading:
    """Apply every declaration and every judgement, and stop there.

    `profile_column`'s own first act, split out so that the command's
    population census asks the same question of the same cells (review
    of stage 3, floor item 3). Nothing here decides a role that is
    published, computes a statistic or writes a sentence: it reads the
    column to the end of the passes that decide WHICH CELLS ARE THERE,
    and `_ColumnReading` says at length why that is one answer.

    Guarantees:

    - Inputs: `profile_column`'s own, minus the column's name and place,
      which no pass here reads.
    - Determinism: a fixed function of the arguments.
    - Errors raised: ValueError where the settings name one value BOTH
      as data and as "no value", which is `profile_column`'s own refusal
      and is raised here because this is where the declarations are
      applied.
    - Boundary: opens no file and prints nothing.
    """
    clashes = contradictory_declarations(
        settings.kept_values,
        settings.declared_missing_values,
        forced_decimal_comma,
    )
    if clashes:
        raise ValueError(f"{CONTRADICTORY_DECLARATION}: {clashes[0]}")
    present, missing = split_missing(
        values, settings, forced_decimal_comma
    )
    # THE one classification of this column's cells. Everything below
    # reads these records; not one line of it reads the column again.
    classified = _classify_all(present, forced_decimal_comma)
    # The second half of what the person declared, and the half that has
    # to wait for the classification: a declared NUMBER is compared with
    # the number a cell holds, not with the way the file spells it
    # (review item P1-R6-F9). It runs before the cells are counted, so
    # no rule and no statistic ever sees a value the person called "no
    # value".
    classified, declared = _declared_numbers_removed(
        classified, settings, forced_decimal_comma
    )
    missing = missing + declared
    # WHICH JUDGED PASS TOOK WHICH SPELLING (repair pass of landing
    # 2b.6, contract V5). Gathered at each of the three places a pass
    # removes a cell, because that is the only place it is known: after
    # the removal the classes are counted and the spellings are
    # counted, and neither says which pass a spelling came from.
    # Everything above this line is a DECLARATION -- `split_missing`
    # and `_declared_numbers_removed` -- so nothing the person named
    # can reach this record.
    judged_spellings: "dict[str, dict[str, int]]" = {}
    cells = _tally(classified, n_rows, settings, forced_decimal_comma)
    # One list of what is present, rebuilt from the surviving records.
    # Keeping the pre-declaration list here would have counted values
    # the person removed towards every share below it.
    present = cells.present

    # The numeric sentinels are judged only for a column that can end up
    # in a numeric role, and that is the one line there is: the COMBINED
    # numeric-looking population against the plan's parse rate. Asking
    # about the representable numbers alone let three unrepresentable
    # cells stop the question being asked at all, and `-999` was then
    # published as the column's minimum (review item P1-R5-F1).
    verdicts: dict[float, tuple[bool, str, int]] = {}
    if _numeric_looking(cells) >= _needed(
        settings.minimum_parse_rate, len(present)
    ):
        verdicts = _sentinel_verdicts(
            cells, len(present), judged_candidates
        )
        withheld = sorted(
            candidate for candidate in verdicts if verdicts[candidate][0]
        )
        if withheld:
            # Removed by the EXACT number a cell holds, the same
            # question `_sentinel_verdicts` counted the candidate's
            # rows with. Removing by the rounded value instead took
            # out cells holding a different number that rounds to the
            # candidate -- including cells the person had named with
            # `--keep-value` (review item P1-R8-F2).
            removed = [exact_of_number(candidate) for candidate in withheld]
            kept: list[_Cell] = []
            for cell in classified:
                if cell.exact in removed:
                    missing += [
                        (cell.text, parsing.MISSING_NUMERIC_SENTINEL)
                    ]
                    # WHICH candidate took it, written the way the
                    # verdict will publish it, so the two cannot drift.
                    place = 0
                    for step in range(len(removed)):
                        if removed[step] == cell.exact:
                            place = step
                    _spelling_judged(
                        judged_spellings,
                        f"{withheld[place]:g}",
                        cell.text,
                    )
                else:
                    kept += [cell]
            classified = kept
            # Every population is counted again from the surviving
            # RECORDS; none is patched, and no cell is classified twice.
            # Reading the column a second time here was the last place
            # where two readings of one cell could have differed
            # (review item P1-R6-F10).
            cells = _tally(
                classified, n_rows, settings, forced_decimal_comma
            )
            present = cells.present
    # THE SAME JUDGEMENT, OVER THE PLACEHOLDER DAYS (plan amendment
    # A-P4-1 item 3). A column whose open-ended rows are filled with
    # `9999-12-31` publishes that day as its exact last value, drags
    # its whole ladder toward it, and seeds the twin with decades the
    # source never held -- the one audited shape where the ratified
    # plan published wrong numbers with no warning at all. It is the
    # calendar's `-999`, one space over.
    #
    # ITS ORDERING IS TIGHTER THAN THE AFFIX PASS'S, and the decision
    # says why: taking cells out changes every count, so a column no
    # rule has trouble with today might be claimed by a different one
    # afterwards. There are two conditions, and both must hold.
    #
    # The first is that rules 0 through 4 declined the UN-REMOVED
    # column, which is what the trial below asks. So a constant column
    # of one placeholder day keeps today's claim, and a two-valued
    # column whose one value is a placeholder stays binary.
    #
    # The second is that the NON-CANDIDATE REMAINDER itself clears the
    # datetime rule's line. Otherwise no cell is judged, no cell is
    # removed, and the column lands exactly where today's rules put
    # it -- so an existing datetime column can never fall out of the
    # role by this pass, and a column that was never a column of dates
    # cannot be turned into one by taking cells out of it.
    day_verdicts: dict[str, tuple[bool, str, int]] = {}
    removed_by_days = 0
    judged_over_days = False
    if present and not forced_identifier:
        trial = _decide(
            cells,
            forced_identifier,
            forced_code=forced_code,
            forced_measurement=forced_measurement,
            described_as_pair=described_as_pair,
            stored_as=stored_as,
        )
        if trial.role == ROLE_TEXT or trial.role == ROLE_DATETIME:
            reading = _remainder_reading(present, settings)
            if reading is not None:
                day_verdicts = _placeholder_verdicts(
                    present,
                    reading,
                    settings,
                    forced_decimal_comma,
                    kept_placeholder_days,
                    judged_candidates,
                )
                withheld_days = sorted(
                    candidate
                    for candidate in day_verdicts
                    if day_verdicts[candidate][0]
                )
                if withheld_days:
                    kept_cells: list[_Cell] = []
                    for cell in classified:
                        found = parsing.placeholder_day_of(
                            cell.text, reading
                        )
                        if found is not None and found in withheld_days:
                            missing += [
                                (cell.text, parsing.MISSING_DATE_SENTINEL)
                            ]
                            # The candidate is the canonical day, which
                            # is exactly what the verdict publishes.
                            _spelling_judged(
                                judged_spellings, found, cell.text
                            )
                            removed_by_days = removed_by_days + 1
                        else:
                            kept_cells += [cell]
                    classified = kept_cells
                    cells = _tally(
                classified, n_rows, settings, forced_decimal_comma
            )
                    present = cells.present
                    judged_over_days = True

    # THE SAME JUDGEMENT, OVER THE CORES. A column of `-999 mg` beside
    # real amounts is the shape a trial file actually has, and the pass
    # above never sees it: the CELLS are not numeric-looking, so the
    # question is never asked, and `-999` is published as the column's
    # smallest dose with nothing complaining. That is the silent
    # statistical wrongness this project treats as its worst failure,
    # and the contract says plainly that stand-ins are judged over the
    # CORES once the earlier rules decline (C6-5).
    #
    # It runs only where an affixed reading is what the column reaches,
    # which is why the role is decided first and then decided again:
    # removing cells changes every count, so nothing may be built from
    # the first answer.
    removed_by_cores = 0
    judged_over_cores = False
    if present and not forced_identifier:
        trial = _decide(
            cells,
            forced_identifier,
            forced_code=forced_code,
            forced_measurement=forced_measurement,
            described_as_pair=described_as_pair,
            stored_as=stored_as,
        )
        if trial.role == ROLE_AFFIXED:
            before = len(present)
            classified, missing, verdicts = _cores_judged(
                cells,
                classified,
                missing,
                verdicts,
                judged_spellings,
                forced_measurement,
                judged_candidates,
            )
            cells = _tally(
                classified, n_rows, settings, forced_decimal_comma
            )
            present = cells.present
            # HOW MANY THE CORE PASS TOOK, carried to the verdict below.
            # Removal can move a column across the detection line -- a
            # pair whose count is eaten below the floor lands on a later
            # rule -- and the remark of the role it lands on has to say
            # so, or the reader is told a count of a column that no
            # longer exists (contract C6-5).
            removed_by_cores = before - len(present)
            judged_over_cores = True

    # THE LEVEL PASS: a label column's lone row that a reader could read
    # by subtraction is counted as missing (the owner's ruling of
    # 2026-09-17, item 5; plan P4-D231). The three passes above take out
    # cells that stand for "no value"; this one takes out cells whose
    # VALUE the floor will not let the column name, and it takes them
    # out for the reason the floor exists. A pool of one level on one
    # row IS a count of one, whether or not a key prints it (B3), so a
    # column of 480 `F`, 519 `M` and one `U` at a floor of eleven told
    # every reader that one row holds a third value -- and its twin
    # wrote an invented label in exactly one row, which is that person's
    # row. The cells are counted as missing, spelled as nothing, so the
    # description is that of the table with those cells blank: no count
    # is left to be worked out, and the twin writes a blank there.
    #
    # ITS ORDERING IS THE OTHER PASSES' (C6-5, A-P4-1 item 3). The role
    # is decided first and then decided again, because taking cells out
    # changes every count; the trial reading below is what says whether
    # this column publishes a level list at all, and `_decide` is then
    # asked again with `after_levels`, which holds the second reading to
    # the label rules.
    #
    # THE GATE IS CHEAP. No level below the floor means no pool at all,
    # and at a floor of one there is no such level, so no run at that
    # floor is charged for a second reading.
    judged_over_levels = False
    if (
        present
        and not forced_identifier
        and _a_level_is_below_the_floor(cells)
    ):
        trial = _decide(
            cells,
            forced_identifier,
            removed_by_cores,
            after_removal=judged_over_cores,
            after_days=judged_over_days,
            forced_code=forced_code,
            forced_measurement=forced_measurement,
            described_as_pair=described_as_pair,
            stored_as=stored_as,
        )
        counted_out = _levels_read_by_subtraction(cells, trial.role)
        if counted_out:
            # AND WHETHER THE LABEL RULES ALONE MAY DECIDE AGAIN. On a
            # column of LABELS they must: the cells this pass removed
            # are the ones that were keeping the parse-rate rules out,
            # and re-asking those rules would let a removal claim a
            # column no rule would have given it (C6-5). On a column of
            # numbers BESIDE labels they must not: what the pass removes
            # there is the whole of a label half the floor would not
            # name, and the numbers left were numbers all along --
            # measured, 98 readings beside two `trace` cells became FREE
            # TEXT and published no number at all, where the honest
            # answer is a column of 98 numbers with two holes.
            labels_alone = trial.role in _LEVEL_ROLES
            level_kept: list[_Cell] = []
            for cell in classified:
                if cell.folded in counted_out:
                    # THE SPELLING IS NOT CARRIED OVER, and that is the
                    # whole point. A cell counted absent under its own
                    # spelling would put that spelling in
                    # `missing_by_source` or in the pool beside it, and
                    # a reader who can tell such a cell from an ordinary
                    # blank has been told the count this pass exists to
                    # withhold.
                    missing += [("", parsing.MISSING_BLANK)]
                else:
                    level_kept += [cell]
            classified = level_kept
            cells = _tally(
                classified, n_rows, settings, forced_decimal_comma
            )
            present = cells.present
            judged_over_levels = labels_alone
    return _ColumnReading(
        cells=cells,
        present=present,
        missing=missing,
        verdicts=verdicts,
        day_verdicts=day_verdicts,
        judged_spellings=judged_spellings,
        judged_over_days=judged_over_days,
        removed_by_cores=removed_by_cores,
        judged_over_cores=judged_over_cores,
        judged_over_levels=judged_over_levels,
    )

'''
