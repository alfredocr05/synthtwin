"""P4-D333/D334/D335: no sentence carries a count a key withholds.

WHAT THIS LANDING CLOSED, AND WHAT IT COST TO NOT HAVE IT. Every
published count of a column block is held to the smallest group size.
A count written into a SENTENCE was held to nothing, and the two are
the same disclosure: "1 of this column's values are written with a
comma inside the number" names one row exactly as a key holding 1
would. Measured over 56 descriptions at a floor of eleven before the
binding table existed (the design's own `guard_measure.txt`): 252
sentences and 145 of them carrying whole numbers, of which NINE printed
a count no key of the block beside them published at all and 38 more
restated a count the key itself published below the line. The nine are
what the fragment replaces; the 38 are P4-D332's keys, left standing
and held at a ceiling by K-S3-12 and by
`test_the_keys_a_sentence_restates_below_the_line_are_held_at_a_ceiling`
below. THE SECOND NUMBER READ 29 UNTIL THE REPAIR PASS: that same run
records 29 only under a rule-M prototype this landing did not build,
and 38 is what it records for the tool as shipped.

THE RULE, AND WHY IT IS A TABLE. `taxonomy.ARGUMENT_BINDINGS` binds
every argument position of every form to what it IS -- a key of the
block, a sum or a difference of keys, a key of the document, the main
wrapper's cells, a setting, the levels at the line, a place in one of
this package's own lists, a column number, a value of the column said
a second way, or one of the THIRTEEN counts no key carries. A bound
position must equal what it is bound to, so the key's own floor rule
governs the sentence and nothing more has to be asked. A floored one
is nought, or reaches `parsing.census_floor` with no group left over
against the populations its binding names, or carries the fragment
`said_fewer_than_the_line` in the number's place -- or, where it
reaches the line and the population leaves a group below it,
`said_some_but_not_all`, which names no number at all.

FOUR OF THE THIRTEEN NAME A POPULATION (the repair pass). The two
counts of the comma remark, the affix reading's reach and the date
reading's reach are counts of cells bearing one SPELLING, so what each
does not count is a spelling or affix census group that
`parsing.census_nameable` withholds in the same block -- and the
sentence handed it back by subtraction: 1,199 beside a published
`n_present` of 1,200, 390 beside 400, 59 beside 60. The other nine's
complement is the count of cells a competing reading did not reach,
which the block publishes as a key of its own and P4-D332 leaves
standing.

THE CHECK HERE IS A SECOND IMPLEMENTATION, not a call into the one it
checks. `profile._arguments_are_bound` refuses a document; this file
walks the same sentences from the same table and says what it found,
so a fault in either is a disagreement rather than a shared silence.

WHAT THIS LANDING DELIBERATELY DID NOT CLOSE (P4-D332, the
orchestrator's call of 2026-09-22, reversible and to be put to the
owner). The odd-kind counts -- `n_not_numeric`, `n_out_of_range`,
`n_contradictory`, `n_negative_unrepresentable`, the clock and joined
`n_unparsed`, the affixed complement -- and the sign and pair counts
-- `n_zero`, `n_negative`, `part_above` -- stay published. Flooring
them broke goal 1 in 7 of 7 probed shapes: the owner's program runs
clean on the twin and raises on the real table, and the count still
reached the reader through `n_missing`. `K-S3-12` holds the number of
such leaves so it cannot rise unseen.
"""

import pathlib
import random

import pytest

import fixtures
import stage3_battery as battery
import tail_rule
from synthtwin import contract, errors, parsing, profile, reading, taxonomy

FLOORS = (1, 5, 11)


# -- walking the sentences of a finished document ----------------------


def _blocks_by_name(document: "dict") -> "dict[str, dict]":
    named: "dict[str, dict]" = {}
    for block in document["columns"]:
        named[block["name"]] = block
    return named


def _sentences(document: "dict") -> "list[tuple[str, taxonomy.Note, object]]":
    """(where, sentence, block) for all four sentence paths."""
    named = _blocks_by_name(document)
    found: "list[tuple[str, taxonomy.Note, object]]" = []
    head = document["source"]["header_evidence"]
    if isinstance(head, taxonomy.Note):
        found += [("source.header_evidence", head, None)]
    for entry in document["publication_notes"]:
        note = entry["note"]
        if isinstance(note, taxonomy.Note):
            block = named[entry["column"]] if entry["column"] in named else None
            found += [("publication_notes[].note", note, block)]
    for block in document["columns"]:
        said = block["detection_evidence"]
        if isinstance(said, taxonomy.Note):
            found += [("columns[].detection_evidence", said, block)]
        for remark in block["remarks"]:
            if isinstance(remark, taxonomy.Note):
                found += [("columns[].remarks[]", remark, block)]
    return found


def _positions(
    form: str, arguments: "tuple[object, ...]", line: int
) -> "list[tuple[str, int, object]]":
    """(form, place, argument) for every position, nested forms walked."""
    found: "list[tuple[str, int, object]]" = []
    for place in range(len(arguments)):
        argument = arguments[place]
        nested = (
            isinstance(argument, tuple)
            and len(argument) == 2
            and isinstance(argument[0], str)
            and isinstance(argument[1], tuple)
        )
        # THE TWO FRAGMENTS ARE POSITIONS, NOT SENTENCES TO WALK INTO.
        # Each stands in the place of a count, so what this walk has to
        # report is the position it stands AT. Walking into
        # `said_fewer_than_the_line` would ask about the line, which is
        # a setting and exempt; walking into `said_some_but_not_all`
        # would ask about nothing at all, because its arity is nought
        # -- and the position would then go unreported, which is how a
        # second implementation comes to agree by looking away.
        if nested and argument[0] not in (
            taxonomy.SAID_FEWER_THAN_THE_LINE,
            taxonomy.SAID_SOME_BUT_NOT_ALL,
        ):
            found += _positions(argument[0], argument[1], line)
            continue
        found += [(form, place, argument)]
    return found


def _key(block: object, dotted: str) -> "int | None":
    node: object = block
    for step in dotted.split("."):
        if not isinstance(node, dict) or step not in node:
            return None
        node = node[step]
    return node if isinstance(node, int) and not isinstance(node, bool) else None


def _unaccounted(
    document: "dict", floor: int
) -> "list[str]":
    """Every argument this second implementation cannot account for."""
    line = parsing.census_floor(floor)
    found: "list[str]" = []
    for where, sentence, block in _sentences(document):
        for form, place, argument in _positions(
            sentence.form, sentence.arguments, line
        ):
            binding = taxonomy.argument_binding(form, place)
            said = f"{where} {form} argument {place + 1} = {argument!r}"
            if not binding:
                found += [f"{said}: NO BINDING"]
                continue
            kind = binding[0]
            if kind == taxonomy.BIND_FLOORED:
                if isinstance(argument, tuple):
                    if argument == (taxonomy.SAID_SOME_BUT_NOT_ALL, ()):
                        # NOTHING TO CHECK, and that is the point of
                        # it: a form with no argument carries no count,
                        # so there is no line it could contradict and
                        # no key it could disagree with.
                        continue
                    if argument != (
                        taxonomy.SAID_FEWER_THAN_THE_LINE,
                        (line,),
                    ):
                        found += [f"{said}: fragment does not carry the line"]
                    continue
                if 0 < argument < line:
                    found += [f"{said}: a count below the line {line}"]
                    continue
                for population in binding[1] if len(binding) > 1 else ():
                    total = _key(block, population)
                    if total is None:
                        found += [f"{said}: {population} not published"]
                    elif 0 < total - argument < line:
                        found += [
                            f"{said}: {total - argument} left of {population}"
                        ]
                continue
            if kind in (
                taxonomy.BIND_SETTING,
                taxonomy.BIND_VOCABULARY,
                taxonomy.BIND_STRUCTURAL,
                taxonomy.BIND_LEVELS_AT_THE_LINE,
                taxonomy.BIND_VALUE,
                taxonomy.BIND_WORD,
                taxonomy.BIND_NESTED,
                taxonomy.BIND_AFFIX,
            ):
                continue
            if kind == taxonomy.BIND_DOCUMENT:
                if document[binding[1]] != argument:
                    found += [f"{said}: != document {binding[1]}"]
                continue
            if kind == taxonomy.BIND_KEY:
                if _key(block, binding[1]) != argument:
                    found += [f"{said}: != key {binding[1]}"]
                continue
            if kind == taxonomy.BIND_SUM:
                parts = [_key(block, name) for name in binding[1]]
                if None in parts or sum(parts) != argument:
                    found += [f"{said}: != sum of {binding[1]}"]
                continue
            if kind == taxonomy.BIND_DIFFERENCE:
                left, right = _key(block, binding[1]), _key(block, binding[2])
                if left is None or right is None or left - right != argument:
                    found += [f"{said}: != {binding[1]} less {binding[2]}"]
                continue
            if kind == taxonomy.BIND_MAIN_WRAPPER:
                affixed = _key(block, "n_affixed")
                named = 0
                for wrapper in block["affix_variants"]:
                    named = named + wrapper["count"]
                if affixed is None or affixed - named != argument:
                    found += [f"{said}: != the main wrapper's cells"]
                continue
            found += [f"{said}: unknown binding kind {kind}"]
    return found


# -- the gate ----------------------------------------------------------


@pytest.mark.parametrize("floor", FLOORS)
def test_no_sentence_of_the_battery_carries_a_count_a_key_withholds(
    tmp_path: pathlib.Path, floor: int
) -> None:
    """THE GATE, over all 43 seeded shapes at three floors.

    Every argument of every sentence is accounted for by the binding
    table: it equals the key it restates, or it is a count no key
    carries that is nought, a group, or the fragment.
    """
    folder = tmp_path / f"floor-{floor}"
    folder.mkdir()
    unaccounted: "list[str]" = []
    for name in sorted(battery.SHAPES):
        document = battery.described(folder, name, floor)
        for finding in _unaccounted(document, floor):
            unaccounted += [f"{name}: {finding}"]
    assert not unaccounted, "\n".join(unaccounted)


@pytest.mark.parametrize("floor", FLOORS)
def test_the_producers_own_documents_pass_its_own_guard(
    tmp_path: pathlib.Path, floor: int
) -> None:
    """A guard that refused this producer's output would stop the tool.

    Written separately from the check above because they fail for
    different reasons: this one says the SHIPPED guard accepts what the
    shipped producer writes, and that is the claim that keeps `profile`
    usable at all.
    """
    folder = tmp_path / f"guard-{floor}"
    folder.mkdir()
    for name in sorted(battery.SHAPES):
        document = battery.described(folder, name, floor)
        profile.check_publication(document)


def test_the_binding_table_is_closed_over_every_form() -> None:
    """A position nobody bound is a number no rule governs."""
    assert taxonomy.unbound_argument_positions() == []
    assert len(taxonomy.FLOORED_POSITIONS) == 13


# -- the fragment ------------------------------------------------------


def test_the_fragment_says_the_line_and_nothing_else() -> None:
    """NF60's whole rendering, pinned character for character."""
    assert taxonomy.NOTE_ARITY[taxonomy.SAID_FEWER_THAN_THE_LINE] == 1
    assert (
        taxonomy.rendered(taxonomy.SAID_FEWER_THAN_THE_LINE, (11,))
        == "fewer than 11"
    )


def test_a_count_below_the_line_is_written_as_the_fragment(
    tmp_path: pathlib.Path,
) -> None:
    """One grouped cell among 400 says "fewer than 11", not "1".

    The shape is the inventory's own: `numeric_one_grouped_comma`
    writes one `1,234` in among 400 three-figure counts, and the
    decimal-comma remark carried that 1 into a sentence at every floor
    until this landing.
    """
    document = battery.described(tmp_path, "numeric_one_grouped_comma", 11)
    remarks = " ".join(document["columns"][0]["remarks"])
    assert "fewer than 11 of this column's values" in remarks
    for remark in document["columns"][0]["remarks"]:
        assert not f"{remark}".startswith("1 of this column's values")


def test_the_fragment_is_capitalised_where_it_opens_a_sentence(
    tmp_path: pathlib.Path,
) -> None:
    """NF29 argument 6 stands after a full stop, so the fragment does too."""
    document = battery.described(tmp_path, "free_text_affix_reach", 11)
    remarks = " ".join(document["columns"][0]["remarks"])
    assert "again. Fewer than 11 of its values are numbers wearing" in remarks


def test_where_the_line_is_two_the_remark_keeps_its_warning_and_no_count(
    tmp_path: pathlib.Path,
) -> None:
    """"fewer than 2" beside "such cells exist" is a count of one.

    At `--smallest-group 1` or 2 the census line is two, so NF60 cannot
    say anything the digit did not. The remark used to be withdrawn
    there; since the owner's ruling of 2026-09-23 (plan P4-D347) it
    keeps its warning and drops the number, so NF61 stands instead --
    true of the same cells, and carrying no argument to read.
    """
    document = battery.described(tmp_path, "numeric_one_grouped_comma", 1)
    remarks = " ".join(document["columns"][0]["remarks"])
    assert "comma inside the number" in remarks, (
        "the decimal-comma warning is withdrawn again at a line of two"
    )
    assert "fewer than 2" not in remarks, (
        "'fewer than 2' is the count of one said in other words"
    )
    assert "some but not all" in remarks


# -- the complement, and the fragment that names no number -------------


def test_the_second_fragment_says_some_but_not_all_and_nothing_else() -> None:
    """NF61's whole rendering, pinned character for character.

    Nought arguments, because an argument here would be a count and a
    count is what it exists not to say.
    """
    assert taxonomy.NOTE_ARITY[taxonomy.SAID_SOME_BUT_NOT_ALL] == 0
    assert (
        taxonomy.rendered(taxonomy.SAID_SOME_BUT_NOT_ALL, ())
        == "some but not all"
    )
    # AND CAPITALISED WHERE IT OPENS A SENTENCE, on NF60's rule. NF29
    # argument 6 stands immediately after a full stop. The producer
    # withdraws that remark rather than writing the fragment there --
    # a remark CAN be withdrawn -- so the branch is asked of the
    # grammar directly, which is the only way to ask it at all.
    opened = taxonomy.rendered(
        taxonomy.REMARK_NO_READING_FITS,
        (
            (taxonomy.SAID_WRITTEN_AS_NUMBERS, (0, 400)),
            (taxonomy.SAID_READ_AS_DATES, (0, "iso-date")),
            99,
            400,
            40,
            (taxonomy.SAID_SOME_BUT_NOT_ALL, ()),
            0,
            0,
            0,
        ),
    )
    assert "again. Some but not all of its values are numbers wearing" in opened


def test_neither_fragment_stands_at_a_position_that_is_not_floored(
    tmp_path: pathlib.Path,
) -> None:
    """MUTATION: put a fragment where a whole sentence belongs.

    Both fragments RENDER at a nested position -- `_said` asks the
    grammar for the text and gets it -- so nothing upstream refuses
    them and the guard has to. A sentence that used one anywhere but a
    floored position would be saying "fewer than eleven", or "some but
    not all", about something that is not a count.
    """
    document = _documented(tmp_path, "numeric_one_out_of_range")
    block = document["columns"][0]
    kept = list(block["remarks"])
    dates = (taxonomy.SAID_READ_AS_DATES, (0, "iso-date"))
    numbers = (
        taxonomy.SAID_WRITTEN_AS_NUMBERS,
        (
            block["n_numeric"]
            + block["n_out_of_range"]
            + block["n_contradictory"],
            block["n_present"],
        ),
    )
    folded = block["n_distinct_folded"]

    def remark_carrying(first: object) -> object:
        """NF29 with every other argument legal, so only `first` can refuse it."""
        return taxonomy.note(
            taxonomy.REMARK_NO_READING_FITS,
            (first, dates, 99, folded, 40, 0, 0, 0, 0),
        )

    # THE CONTROL: the same remark carrying a real nested sentence at
    # argument 1 is published, so what refuses below is the fragment
    # standing there and not some other argument of this remark.
    block["remarks"] = kept + [remark_carrying(numbers)]
    profile.check_publication(document)
    for fragment in (
        (taxonomy.SAID_FEWER_THAN_THE_LINE, (11,)),
        (taxonomy.SAID_SOME_BUT_NOT_ALL, ()),
    ):
        assert taxonomy.rendered(fragment[0], fragment[1])
        block["remarks"] = kept + [remark_carrying(fragment)]
        with pytest.raises(errors.ProfileError):
            profile.check_publication(document)


def test_the_second_implementation_reports_the_place_a_fragment_stands_at(
    tmp_path: pathlib.Path,
) -> None:
    """A walk that steps INTO a fragment reports nothing about it.

    `_positions` is this file's own walk, and the whole of its value is
    that it reports the position a count would have stood at. NF61
    takes no argument, so a walk that recursed into it would yield
    nothing at all for that position -- and the gate above, and
    `K-S3-12`, would both go quiet about exactly the case the repair
    pass added. MUTATION: recurse into either fragment and this turns
    red while every other test here stays green.
    """
    document = battery.described(tmp_path, "dates_beside_ten_words", 11)
    evidence = document["columns"][0]["detection_evidence"]
    walked = _positions(evidence.form, evidence.arguments, 11)
    assert (
        taxonomy.SAID_READ_AS_DATES,
        0,
        (taxonomy.SAID_SOME_BUT_NOT_ALL, ()),
    ) in walked
    below = battery.described(tmp_path, "free_text_affix_reach", 11)
    remark = [
        note
        for note in below["columns"][0]["remarks"]
        if note.form == taxonomy.REMARK_NO_READING_FITS
    ][0]
    assert (
        taxonomy.REMARK_NO_READING_FITS,
        5,
        (taxonomy.SAID_FEWER_THAN_THE_LINE, (11,)),
    ) in _positions(remark.form, remark.arguments, 11)


@pytest.mark.parametrize("floor", FLOORS)
def test_no_floored_count_of_the_battery_hands_back_its_complement(
    tmp_path: pathlib.Path, floor: int
) -> None:
    """THE OTHER HALF OF THE GATE, over all 46 shapes at three floors.

    The gate above asks whether a floored count is itself too small to
    print. This asks the question the other way round: whether the
    cells it does NOT count are too few to name, because a reader
    holding the sentence and the block subtracts one from the other.
    Three of the shapes plant that remainder at one to ten -- 1,199
    grouped prices beside one bare cell, 390 dates beside ten words,
    59 cells wearing ` mg` beside one wearing ` MG` -- and each
    reproduces a real exposure: the first is the repository's own
    precedent, recorded in `parsing.census_nameable`'s docstring.

    IT ASKS ALL THIRTEEN POSITIONS, not only the four the rule arms.
    At the other nine the complement is a count the block publishes in
    a key beside the sentence, so a shape that raises this number is a
    P4-D332 decision somebody takes and records -- which is exactly
    what a number nobody can reach silently is for.
    """
    folder = tmp_path / f"complement-{floor}"
    folder.mkdir()
    line = parsing.census_floor(floor)
    handed_back: "list[str]" = []
    for name in sorted(battery.SHAPES):
        document = battery.described(folder, name, floor)
        for where, sentence, block in _sentences(document):
            total = _key(block, "n_present")
            if total is None:
                continue
            for form, place, argument in _positions(
                sentence.form, sentence.arguments, line
            ):
                if taxonomy.argument_binding(form, place)[:1] != (
                    taxonomy.BIND_FLOORED,
                ):
                    continue
                if isinstance(argument, tuple):
                    continue
                if 0 < total - argument < line:
                    handed_back += [
                        f"{name}: {where} {form} argument {place + 1} = "
                        f"{argument} beside n_present {total} hands back "
                        f"{total - argument}"
                    ]
    assert not handed_back, "\n".join(handed_back)


def test_the_sentence_a_block_cannot_lose_says_less_instead_of_the_digits(
    tmp_path: pathlib.Path,
) -> None:
    """The producer and the guard agree about the undroppable sentence.

    390 dates beside ten free-text cells. The column is described as
    free text, so its evidence nests `said_read_as_dates`, whose count
    is a floored position bound to `n_present`: 390 beside 400 hands
    back the ten. The evidence cannot be withdrawn -- a block must say
    how it was read -- and NF60 cannot stand there either, because
    "fewer than 11" is false of 390. So NF61 stands there, and the
    shipped guard accepts the shipped producer's own document.

    MUTATION: make `taxonomy._arguments_at_the_line` write the digits
    at a `_STANDS_NOWHERE` position that reaches the line -- which is
    what it did before the repair pass -- and
    `profile.check_publication` raises ProfileError on this ordinary
    table, reporting "a fault in synthtwin itself".
    """
    document = battery.described(tmp_path, "dates_beside_ten_words", 11)
    profile.check_publication(document)
    block = document["columns"][0]
    said = f"{block['detection_evidence']}"
    assert "some but not all read as dates" in said
    assert "390" not in said
    nested = block["detection_evidence"].arguments[1]
    assert nested[0] == taxonomy.SAID_READ_AS_DATES
    assert nested[1][0] == (taxonomy.SAID_SOME_BUT_NOT_ALL, ())


def test_a_remark_whose_complement_falls_below_the_line_keeps_its_warning(
    tmp_path: pathlib.Path,
) -> None:
    """1,199 grouped prices beside one bare cell: the warning stays, the count goes.

    THE OWNER'S RULING OF 2026-09-23 (plan P4-D347). The remark was
    withdrawn whole until this pass, and the cost was a load-bearing
    warning about 1,199 cells that may be a thousand times their real
    size, bought with the single ungrouped cell a reader would take off
    the published `n_present`. The warning comes back with no number in
    it, which costs nothing: NF61 carries no argument at all.

    AND NOTHING CAN BE SUBTRACTED FROM IT, which is what the withdrawal
    was for and is asserted here rather than assumed: no figure of the
    remark's own text is 1,199 or 1,200, and the only numbers on the
    line are the ones this repository's fixed prose carries.
    """
    document = battery.described(
        tmp_path, "numeric_all_but_one_grouped_comma", 11
    )
    profile.check_publication(document)
    block = document["columns"][0]
    assert block["n_present"] == 1200
    said = [
        remark
        for remark in block["remarks"]
        if remark.form == taxonomy.REMARK_GROUP_COMMAS
    ]
    assert len(said) == 1, (
        "the decimal-comma warning is withdrawn again on the shape the "
        "owner ruled on"
    )
    text = f"{said[0]}"
    assert "some but not all" in text
    # NOTHING TO SUBTRACT, asserted twice over. First on the ARGUMENTS:
    # every floored position either carries the fragment or carries a
    # count whose complement against `n_present` is nought or reaches
    # the line, which is `profile._floored_argument_is_bound`'s own
    # test and the one the guard above just ran.
    line = parsing.census_floor(11)
    for place in range(taxonomy.NOTE_ARITY[taxonomy.REMARK_GROUP_COMMAS]):
        argument = said[0].arguments[place]
        if not isinstance(argument, int) or isinstance(argument, bool):
            continue
        rest = block["n_present"] - argument
        assert rest == 0 or rest >= line, (
            f"argument {place} of the warning is {argument}, and "
            f"{block['n_present']} less it is {rest} -- the group the "
            f"floor holds back, handed back in prose"
        )
    # And then on the TEXT: the same warning built from a DIFFERENT
    # count in the same case -- 899 grouped cells of 900 beside one bare
    # -- renders character for character alike. A sentence carrying a
    # count of its column could not.
    settings = taxonomy.Settings(small_cell_floor=11)
    written = []
    for grouped, present in ((1199, 1200), (899, 900)):
        _evidence, kept = taxonomy.sentences_at_the_line(
            taxonomy.note(taxonomy.EVIDENCE_NUMBERS, (present, present)),
            [taxonomy.note(taxonomy.REMARK_GROUP_COMMAS, (grouped, 0))],
            present,
            settings,
        )
        written += [f"{kept[0]}"]
    assert written[0] == written[1] == text, (
        "the warning differs between 1,199 grouped cells of 1,200 and "
        "899 of 900, so it is carrying a count of its column"
    )


def test_the_keys_a_sentence_restates_below_the_line_are_held_at_a_ceiling(
    tmp_path: pathlib.Path,
) -> None:
    """P4-D332's own class, re-measurable rather than quoted.

    The measurement that asked for the binding table counted three
    quantities over 56 descriptions at a floor of eleven, and only one
    of them -- the NINE this guard closes -- can be re-run from
    anything in the repository. The 38 beside it is a count of
    sentences restating a key the block published BELOW the line, and
    P4-D332 leaves those keys standing, so nothing here would ever
    turn red if that class doubled.

    This counts the same class over the committed battery: an argument
    bound to a key, a sum or a difference of keys whose value is one to
    ten. It is a CEILING and not a target, on exactly K-S3-12's
    reasoning -- the keys are published on purpose, and what may not
    happen is the number growing while nobody is looking.
    """
    line = parsing.census_floor(11)
    keys = (taxonomy.BIND_KEY, taxonomy.BIND_SUM, taxonomy.BIND_DIFFERENCE)
    restating = 0
    for name in sorted(battery.SHAPES):
        document = battery.described(tmp_path, name, 11)
        for _where, sentence, _block in _sentences(document):
            for form, place, argument in _positions(
                sentence.form, sentence.arguments, line
            ):
                if isinstance(argument, bool) or not isinstance(argument, int):
                    continue
                bound = taxonomy.argument_binding(form, place)[:1]
                if bound and bound[0] in keys and 0 < argument < line:
                    restating = restating + 1
    assert restating <= 20, (
        "more sentences now restate a key the block published below the "
        f"line than the {restating} this landing measured; P4-D332 leaves "
        "those keys standing, so a rise is a decision to record rather "
        "than a defect to hide"
    )


# -- the mutations -----------------------------------------------------


def _documented(tmp_path: pathlib.Path, name: str, floor: int = 11) -> "dict":
    return battery.described(tmp_path, name, floor)


def test_a_sentence_count_unequal_to_its_key_is_refused(
    tmp_path: pathlib.Path,
) -> None:
    """MUTATION: move one argument away from the key it restates.

    `remark_values_out_of_range` argument 1 is `n_out_of_range`. A
    remark saying 3 beside a key saying 1 is a count the block never
    published, which is the whole class this guard exists for.
    """
    document = _documented(tmp_path, "numeric_one_out_of_range")
    block = document["columns"][0]
    remarks = list(block["remarks"])
    for index in range(len(remarks)):
        if remarks[index].form == taxonomy.REMARK_OUT_OF_RANGE:
            remarks[index] = taxonomy.note(
                taxonomy.REMARK_OUT_OF_RANGE, (block["n_out_of_range"] + 2,)
            )
    block["remarks"] = remarks
    with pytest.raises(errors.ProfileError):
        profile.check_publication(document)


def test_a_floored_count_below_the_line_is_refused(
    tmp_path: pathlib.Path,
) -> None:
    """MUTATION: put the digit back where the fragment stands.

    This is the landing's own repair, undone: the comma remark carrying
    1 instead of `said_fewer_than_the_line`.
    """
    document = _documented(tmp_path, "numeric_one_grouped_comma")
    block = document["columns"][0]
    remarks = list(block["remarks"])
    found = False
    for index in range(len(remarks)):
        if remarks[index].form == taxonomy.REMARK_GROUP_COMMAS:
            remarks[index] = taxonomy.note(taxonomy.REMARK_GROUP_COMMAS, (1, 0))
            found = True
    block["remarks"] = remarks
    assert found, "the shape no longer carries the comma remark"
    with pytest.raises(errors.ProfileError):
        profile.check_publication(document)


def test_a_fragment_carrying_another_number_is_refused(
    tmp_path: pathlib.Path,
) -> None:
    """MUTATION: "fewer than 3" under a run whose smallest group is 11.

    A fragment built with a smaller line is a narrower claim than the
    floor allows, and a reader cannot tell it from the truth.
    """
    document = _documented(tmp_path, "numeric_one_grouped_comma")
    block = document["columns"][0]
    remarks = list(block["remarks"])
    for index in range(len(remarks)):
        if remarks[index].form == taxonomy.REMARK_GROUP_COMMAS:
            remarks[index] = taxonomy.note(
                taxonomy.REMARK_GROUP_COMMAS,
                ((taxonomy.SAID_FEWER_THAN_THE_LINE, (3,)), 0),
            )
    block["remarks"] = remarks
    with pytest.raises(errors.ProfileError):
        profile.check_publication(document)


def test_a_floored_count_leaving_a_group_below_the_line_is_refused(
    tmp_path: pathlib.Path,
) -> None:
    """The third clause of the floored rule, asked of a SHIPPED binding.

    A floored count that REACHES the line still may not leave a group
    below it against the population its binding names. Four positions
    name one since the repair pass, so the clause is asked of a real
    binding here rather than of one the test invents -- which is what
    it did while none was armed, and is why a battery of 43 shapes
    could report the class closed while a sixty-row affixed column
    reached the exposure in one call.

    MUTATION: take the population back out of
    `(REMARK_GROUP_COMMAS, 0)` and this turns green, which is what says
    the clause is what refuses.
    """
    document = _documented(tmp_path, "numeric_one_out_of_range")
    block = document["columns"][0]
    kept = list(block["remarks"])
    # THE CONTROL FIRST: the same count leaving NOTHING over is
    # published, so what the refusal below rests on is the remainder
    # and not the size of the count.
    block["remarks"] = kept + [
        taxonomy.note(taxonomy.REMARK_GROUP_COMMAS, (block["n_present"], 0))
    ]
    profile.check_publication(document)
    block["remarks"] = kept + [
        taxonomy.note(
            taxonomy.REMARK_GROUP_COMMAS, (block["n_present"] - 3, 0)
        )
    ]
    with pytest.raises(errors.ProfileError):
        profile.check_publication(document)


def test_the_population_is_the_one_the_binding_names_and_not_every_key(
    tmp_path: pathlib.Path,
) -> None:
    """The nine unarmed positions are unarmed, and that is a decision.

    A floored count whose binding names no population is NOT refused
    for leaving a group below the line, because at those nine the
    complement is the count of cells a competing reading did not reach
    -- which the block publishes as a key of its own, and which
    P4-D332's call leaves standing and holds at a ceiling. Written
    down so that arming a tenth is a change somebody makes on purpose
    rather than a rule that quietly already covered it.
    """
    document = _documented(tmp_path, "numeric_one_out_of_range")
    block = document["columns"][0]
    assert taxonomy.argument_binding(taxonomy.REMARK_TWO_READINGS_FIT, 0) == (
        taxonomy.BIND_FLOORED,
    )
    block["remarks"] = list(block["remarks"]) + [
        taxonomy.note(
            taxonomy.REMARK_TWO_READINGS_FIT, (block["n_present"] - 3,)
        )
    ]
    profile.check_publication(document)


def test_exactly_four_floored_positions_name_a_population() -> None:
    """Which four, and the reason is a fact about their complement.

    Each of the four counts cells bearing ONE SPELLING of a number or
    of an affix, so what it does not count is a spelling-census group
    `parsing.census_nameable` withholds in the same block. The other
    nine count how far a competing READING got, and the block
    publishes the cells it did not reach.
    """
    armed = {
        place
        for place in taxonomy.FLOORED_POSITIONS
        if len(taxonomy.ARGUMENT_BINDINGS[place]) > 1
    }
    assert armed == {
        (taxonomy.REMARK_GROUP_COMMAS, 0),
        (taxonomy.REMARK_GROUP_COMMAS, 1),
        (taxonomy.REMARK_NO_READING_FITS, 5),
        (taxonomy.SAID_READ_AS_DATES, 0),
    }
    for place in armed:
        assert taxonomy.ARGUMENT_BINDINGS[place][1] == ("n_present",)


def test_an_argument_position_nobody_bound_is_refused(
    tmp_path: pathlib.Path, monkeypatch
) -> None:
    """MUTATION: take one position out of the binding table.

    A form that grew an argument and no binding could print a number
    under no rule at all, which is the state every position was in
    before this landing.
    """
    document = _documented(tmp_path, "numeric_one_out_of_range")
    thinned = dict(taxonomy.ARGUMENT_BINDINGS)
    del thinned[(taxonomy.REMARK_OUT_OF_RANGE, 0)]
    monkeypatch.setattr(taxonomy, "ARGUMENT_BINDINGS", thinned)
    with pytest.raises(errors.ProfileError):
        profile.check_publication(document)


# -- rule W: the words a count moves -----------------------------------


def _one_column(
    folder: pathlib.Path, stem: str, cells: "list[str]", floor: int
) -> "dict":
    path = folder / f"{stem}.csv"
    path.write_text(
        battery.rows_text(["value"], [[cell] for cell in cells]),
        encoding="utf-8",
        newline="",
    )
    table = reading.read_table(str(path), small_cell_floor=floor)
    settings = taxonomy.Settings(small_cell_floor=floor)
    return profile.build_document(table, settings, [], [], [])["columns"][0]


def test_rule_w_one_bracketed_cell_does_not_move_the_negatives_word(
    tmp_path: pathlib.Path,
) -> None:
    """MUTATION VERIFIED: `_negative_form` reading `small_cell_floor`.

    One accounting bracket among 400 cells published `brackets` at a
    settings floor of one, and a reader who knew how every other
    negative was written read that cell's spelling off the word. With
    `census_floor` the word is `minus` at every floor. Put
    `cells.settings.small_cell_floor` back in `_negative_form` and this
    turns red: measured 2026-09-22, `negative_form` came back
    `brackets`.
    """
    rng = random.Random(4)
    cells = [f"{rng.randint(10, 99)}.5" for _ in range(399)]
    cells += ["(42.5)"]
    rng.shuffle(cells)
    block = _one_column(tmp_path, "brackets", cells, 1)
    assert block["n_negative"] == 1
    assert block["negative_form"] == parsing.NEGATIVE_MINUS


def test_rule_w_one_grouped_cell_does_not_move_the_thousands_mark(
    tmp_path: pathlib.Path,
) -> None:
    """MUTATION VERIFIED: `_group_separator` reading `small_cell_floor`.

    Put the settings floor back and this turns red: measured
    2026-09-22, `group_separator` came back `,` on a column where one
    cell of 400 proves the mark.
    """
    rng = random.Random(5)
    cells = [f"{rng.randint(100, 999)}" for _ in range(399)]
    cells += ["1,234"]
    rng.shuffle(cells)
    block = _one_column(tmp_path, "grouped", cells, 1)
    assert block["group_separator"] == ""


def test_rule_w_one_wide_run_does_not_move_the_canonical_word(
    tmp_path: pathlib.Path,
) -> None:
    """MUTATION VERIFIED: `_wide_runs` reading `small_cell_floor`.

    One wide key beside 399 ordinary amounts published `canonical` at a
    floor of one, beside a forms map that had pooled that cell's form
    into `(withheld)` precisely so that no reader could tell what form
    it wore. Put the settings floor back and this turns red: measured
    2026-09-22, `wide_runs` came back `canonical`.
    """
    rng = random.Random(6)
    cells = [f"{rng.randint(1000, 9999)}" for _ in range(399)]
    cells += ["90071992547409931"]
    rng.shuffle(cells)
    block = _one_column(tmp_path, "wide", cells, 1)
    # The forms map names one form for the whole column, so the wide
    # cell is not pooled out of the question before the floor is asked.
    assert block["numeric_styles"] == {parsing.STYLE_PLAIN: 400}
    assert block["wide_runs"] == parsing.WIDE_NONE


def test_rule_w_a_column_of_one_moment_says_nothing_about_midnight(
    tmp_path: pathlib.Path,
) -> None:
    """`_all_at_midnight` and `_midnight_count` read the census line.

    They read `parsing.census_floor` already -- rule W found this one
    line of the four already written -- and the loader's D14 now reads
    the same function rather than rebuilding it from
    `MIDNIGHT_DISCLOSURE_FLOOR`. The claim is the one the floor makes:
    a column of ONE moment says nothing about midnight at any floor.
    """
    block = battery.described(tmp_path, "moments_one_midnight", 1)["columns"][0]
    assert block["n_at_midnight"] is None
    assert not block["all_at_midnight"]


# -- the mode's complement ---------------------------------------------


def test_a_heap_of_395_withholds_the_mode_pair(tmp_path: pathlib.Path) -> None:
    """MUTATION VERIFIED: `_mode_published` without `census_nameable`.

    395 zeros among 400 numbers published `mode_count: 395` beside
    `n_used_in_statistics: 400`, and the five cells that are not the
    heap are a group no key of the block would be allowed to name.
    Take the `census_nameable` clause out of `_mode_published` and this
    turns red: measured 2026-09-22, mode 0.0 and mode_count 395.
    """
    rng = random.Random(3)
    cells = ["0"] * 395 + [f"{rng.randint(1, 9)}" for _ in range(5)]
    rng.shuffle(cells)
    block = _one_column(tmp_path, "heap", cells, 11)
    assert block["mode"] is None
    assert block["mode_count"] == 0


def test_a_mode_leaving_a_group_behind_is_still_published(
    tmp_path: pathlib.Path,
) -> None:
    """The clause withholds a HEAP and not every mode.

    A rule that withheld the pair wherever it was large would cost the
    generator its only bound on a stratum. 300 of 400 leaves 100, which
    is a group, so the pair stands.
    """
    rng = random.Random(3)
    cells = ["7"] * 300 + [f"{rng.randint(10, 99)}" for _ in range(100)]
    rng.shuffle(cells)
    block = _one_column(tmp_path, "mode-kept", cells, 11)
    assert block["mode"] == 7.0
    assert block["mode_count"] == 300


def test_the_loader_refuses_a_mode_that_leaves_a_group_behind(
    tmp_path: pathlib.Path,
) -> None:
    """Q18's mirror: a description this producer cannot write is refused.

    Written against the LOADER because the producer and the loader are
    two implementations of one rule, and a rule only one of them holds
    is a rule a second producer could break.
    """
    rng = random.Random(3)
    cells = ["7"] * 300 + [f"{rng.randint(10, 99)}" for _ in range(100)]
    rng.shuffle(cells)
    path = tmp_path / "q18.csv"
    path.write_text(
        battery.rows_text(["value"], [[cell] for cell in cells]),
        encoding="utf-8",
        newline="",
    )
    table = reading.read_table(str(path), small_cell_floor=11)
    document = profile.build_document(
        table, taxonomy.Settings(small_cell_floor=11), [], [], []
    )
    block = document["columns"][0]
    block["mode_count"] = block["n_used_in_statistics"] - 3
    target = fixtures.write_profile(tmp_path, "table-profile.json", document)
    with pytest.raises(errors.ProfileError):
        contract.load_profile(str(target))


# -- what this landing did NOT move ------------------------------------


def test_the_odd_kind_counts_are_still_published(
    tmp_path: pathlib.Path,
) -> None:
    """P4-D332: they stay, and the number of them is held at a ceiling.

    Flooring these broke goal 1 in 7 of 7 probed shapes -- the owner's
    program ran clean on the twin and raised on the real table -- and
    the count still reached the reader through `n_missing`. This is the
    orchestrator's call of 2026-09-22, reversible, to be put to the
    owner; `K-S3-12` is what stops it drifting wider.
    """
    for name, key, expected in (
        ("numeric_one_out_of_range", "n_out_of_range", 1),
        ("numeric_one_contradictory", "n_contradictory", 1),
        ("numeric_three_not_numbers", "n_not_numeric", 3),
        ("clock_two_not_clock", "n_unparsed", 2),
        ("numeric_one_zero", "n_zero", 1),
    ):
        document = battery.described(tmp_path, name, 11)
        block = document["columns"][0]
        assert block[key] == expected, f"{name}.{key}"


def test_no_count_moved_so_the_twin_report_still_reads_the_partition(
    tmp_path: pathlib.Path,
) -> None:
    """The skeptic's site 1: `rendering` reads three published counts.

    `_uncarried_cells` and `_made_up_lines` read `n_not_numeric`,
    `n_out_of_range` and `n_contradictory` to tell the reader how much
    of the column the twin invented. A rule that counted those cells
    out would have made all three nought and the report would have said
    nothing was made up while the twin wrote an invented cell. This
    landing moves no count, and this is what says so.
    """
    document = battery.described(tmp_path, "numeric_three_not_numbers", 11)
    block = document["columns"][0]
    partition = (
        block["n_numeric"]
        + block["n_out_of_range"]
        + block["n_contradictory"]
        + block["n_not_numeric"]
    )
    assert partition == block["n_present"]
    assert block["n_not_numeric"] == 3


def test_the_epoch_band_remark_reads_the_published_tail_boundaries(
    tmp_path: pathlib.Path,
) -> None:
    """NF51 arguments 2 to 7 are the two edges the block publishes.

    THE MERGE OBLIGATION, BUILT (plan P4-D345, contract NF51). This
    test was SKIPPED on the date and clock tail branch, with its reason
    naming the dependency: the remark's two ends restated
    `percentiles.min` and `percentiles.max`, and there was nothing to
    compare them with until the NUMERIC tail landing withdrew those two
    keys. Both landings now stand in one tree, so the check is made.

    THE DAYS ARE WORKED OUT HERE, from the rule and not from the
    producer. `tests/tail_rule.py` says which percent each boundary
    stands at, the rung is read off the ladder the description
    publishes, and the day is that rung divided by the band's units --
    which is the arithmetic contract NF51 states, done a second time.
    """
    document = battery.described(tmp_path, "epoch_seconds", 11)
    block = document["columns"][0]
    remarks = [
        remark
        for remark in block["remarks"]
        if remark.form == taxonomy.REMARK_EPOCH_BAND
    ]
    assert remarks, "the epoch-band shape no longer carries its remark"
    assert block["percentiles"]["min"] is None
    assert block["percentiles"]["max"] is None

    cells, _flags = battery.SHAPES["epoch_seconds"](
        random.Random(battery.BATTERY_SEED)
    )
    numbers = [float(cell) for cell in cells]
    low_percent = tail_rule.percent_of(len(numbers), 11)
    assert low_percent is not None
    edges = (
        tail_rule.rung_of(block, low_percent),
        tail_rule.rung_of(block, 100 - low_percent),
    )
    a_day = 24 * 60 * 60
    owed = (taxonomy.EPOCH_BAND_SECONDS,)
    for edge in edges:
        owed = owed + parsing.civil_from_days(int(edge) // a_day)
    assert remarks[0].arguments == owed, remarks[0].arguments

    # ...AND THEY ARE NOT THE COLUMN'S OWN ENDS, which is the leak the
    # rule closes rather than a detail of it.
    ends = (taxonomy.EPOCH_BAND_SECONDS,)
    for edge in (min(numbers), max(numbers)):
        ends = ends + parsing.civil_from_days(int(edge) // a_day)
    assert remarks[0].arguments != ends


def test_a_remark_naming_ends_the_block_withholds_is_refused(
    tmp_path: pathlib.Path,
) -> None:
    """The guard, mutated: prose may not outlive the facts it quotes.

    A description whose ladder stops short of both ends and whose
    time-band remark still names the column's real smallest and largest
    values would publish, in prose, the two numbers the whole tail rule
    exists to withhold. `profile.check_publication` refuses it.

    THE MUTATION IS OF THE DOCUMENT, not of the producer, so this stays
    a statement about the LOADER: a second implementer writing those
    two days into a conforming-looking description is stopped by the
    same rule that stops this one.
    """
    document = battery.described(tmp_path, "epoch_seconds", 11)
    block = document["columns"][0]
    profile.check_publication(document)

    cells, _flags = battery.SHAPES["epoch_seconds"](
        random.Random(battery.BATTERY_SEED)
    )
    numbers = [float(cell) for cell in cells]
    a_day = 24 * 60 * 60
    ends = (taxonomy.EPOCH_BAND_SECONDS,)
    for edge in (min(numbers), max(numbers)):
        ends = ends + parsing.civil_from_days(int(edge) // a_day)
    block["remarks"] = [
        taxonomy.note(taxonomy.REMARK_EPOCH_BAND, ends)
        if remark.form == taxonomy.REMARK_EPOCH_BAND
        else remark
        for remark in block["remarks"]
    ]
    with pytest.raises(errors.ProfileError):
        profile.check_publication(document)


def test_a_block_with_no_end_and_no_boundary_carries_no_band_remark(
    tmp_path: pathlib.Path,
) -> None:
    """A column too small for a tail says nothing about a band.

    Contract NF51 and plan P4-D345: both of the sentence's days would
    then be values nothing else in the description holds, which is the
    one thing a sentence argument may never be (4.5.1). The shape is a
    column of epoch seconds at a floor high enough that no percent
    leaves a tail's rows outside on both sides at once (contract TL3),
    so the block publishes its moments and no rung at all. At 120 cells
    the widest boundary, 50 per cent, leaves 59 rows outside and the
    floor asks for 61, so there is no percent to stand at.
    """
    base = 1_600_000_000
    draw = random.Random(11)
    cells = [f"{base + draw.randint(0, 50_000_000)}" for _ in range(120)]
    path = tmp_path / "band.csv"
    path.write_text(
        battery.rows_text(["value"], [[cell] for cell in cells]),
        encoding="utf-8",
        newline="",
    )
    floor = 61
    document = profile.build_document(
        reading.read_table(f"{path}", small_cell_floor=floor),
        taxonomy.Settings(small_cell_floor=floor),
        [],
        [],
        [],
    )
    block = document["columns"][0]
    assert tail_rule.percent_of(len(cells), floor) is None
    assert block["percentiles"]["min"] is None
    assert block["percentiles"]["max"] is None
    assert taxonomy.published_ends(block) is None
    assert not [
        remark
        for remark in block["remarks"]
        if remark.form == taxonomy.REMARK_EPOCH_BAND
    ]
    profile.check_publication(document)
