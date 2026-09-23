"""P4-D333/D334/D335: no sentence carries a count a key withholds.

WHAT THIS LANDING CLOSED, AND WHAT IT COST TO NOT HAVE IT. Every
published count of a column block is held to the smallest group size.
A count written into a SENTENCE was held to nothing, and the two are
the same disclosure: "1 of this column's values are written with a
comma inside the number" names one row exactly as a key holding 1
would. Measured over 56 descriptions at a floor of eleven before the
binding table existed: 252 sentences, 145 of them carrying whole
numbers, and 29 arguments restating a count or a complement no key of
the block beside them could have printed.

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
`said_fewer_than_the_line` in the number's place.

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
reached the reader through `n_missing`. `K-S3-01` holds the number of
such leaves so it cannot rise unseen.
"""

import pathlib
import random

import pytest

import fixtures
import stage3_battery as battery
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
        if nested and argument[0] != taxonomy.SAID_FEWER_THAN_THE_LINE:
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
    """NF59's whole rendering, pinned character for character."""
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


def test_where_the_line_is_two_the_remark_is_withdrawn(
    tmp_path: pathlib.Path,
) -> None:
    """"fewer than 2" beside "such cells exist" is a count of one.

    At `--smallest-group 1` or 2 the census line is two, so the
    fragment cannot say anything the digit did not. A remark whose
    floored count falls there is not written at all.
    """
    document = battery.described(tmp_path, "numeric_one_grouped_comma", 1)
    remarks = " ".join(document["columns"][0]["remarks"])
    assert "comma inside the number" not in remarks
    assert "fewer than 2" not in remarks


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
    tmp_path: pathlib.Path, monkeypatch
) -> None:
    """The third clause of the floored rule, asked of a binding that names one.

    A floored count that REACHES the line still may not leave a group
    below it against a population a reader can subtract from. No
    binding names a population today -- every floored position's
    complement is the count of cells a competing reading did not reach,
    which P4-D332 leaves published -- so the clause is exercised here
    by binding one, which is what the date and clock tail landing will
    do when it moves NF51's arguments onto the published boundaries.

    MUTATION: take the population back out of the binding and this
    turns green, which is what says the clause is what refuses.
    """
    document = _documented(tmp_path, "numeric_one_out_of_range")
    block = document["columns"][0]
    bound = dict(taxonomy.ARGUMENT_BINDINGS)
    bound[(taxonomy.REMARK_TWO_READINGS_FIT, 0)] = (
        taxonomy.BIND_FLOORED,
        ("n_present",),
    )
    monkeypatch.setattr(taxonomy, "ARGUMENT_BINDINGS", bound)
    monkeypatch.setattr(
        taxonomy,
        "argument_binding",
        lambda form, place: bound[(form, place)]
        if (form, place) in bound
        else (),
    )
    block["remarks"] = list(block["remarks"]) + [
        taxonomy.note(
            taxonomy.REMARK_TWO_READINGS_FIT, (block["n_present"] - 3,)
        )
    ]
    with pytest.raises(errors.ProfileError):
        profile.check_publication(document)


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
    owner; `K-S3-01` is what stops it drifting wider.
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


@pytest.mark.skip(
    reason=(
        "the date and clock tail landing owns NF51's arguments 2 to 7: "
        "they restate the exact minimum and maximum this stage stops "
        "publishing, and there is nothing to compare them with until "
        "that landing moves them onto the tail's own boundaries"
    )
)
def test_the_epoch_band_remark_reads_the_published_tail_boundaries(
    tmp_path: pathlib.Path,
) -> None:
    """NF51 arguments 2 to 7 are bound to `value (tail rule)`.

    THE DEPENDENCY, NAMED RATHER THAN LEFT OUT. The binding is in the
    table now, so the guard knows these six positions are values and
    not counts and will not judge them by a count rule. What it cannot
    yet do is CHECK them: the two ends the remark reads as calendar
    days are today the block's exact `min` and `max`, which stage 3's
    tail landing replaces. When it lands, this test says the remark's
    days are the days of whatever the block publishes in their place,
    and the `BIND_VALUE` branch of `profile._one_argument_is_bound`
    stops returning early.
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
