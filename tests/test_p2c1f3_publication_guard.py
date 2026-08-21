"""The publication guard over the FINISHED profile (review P2-C1-F3).

Plan P2-D2 requires one control the earlier rounds kept asking for and
the code did not have: every string in the finished document is either a
value the disposition matrix authorizes or a SENTENCE built by a named
first-party constructor from an enumerated grammar, and the check runs
recursively over the finished tree -- the top-level publication notes
included, because `build_document` lifts those out of the column blocks
after each block is complete.

Why a path-and-type whitelist could not do this job, in one sentence: a
source spelling formatted into an existing note stands at the same path
with the same type as the prose it replaced. So acceptance here is by
ORIGIN. A sentence is accepted only when `taxonomy.rendered` can write
the identical text again from the form and the arguments the sentence
carries, and no value of a table is an argument the grammar allows.

The four mutations the plan names each have a test below, and each one
must FAIL the guard: a source spelling formatted into an existing note
path with an unchanged type; a concatenation assembling the same text
from fragments; a nested container smuggling one; and a note lifted to
the top level.
"""

import pathlib

import pytest

import fixtures
from synthtwin import cli, errors, profile, reading, taxonomy

SETTINGS = taxonomy.Settings()

# A spelling that stands for a value of somebody's table. Nothing in
# this package writes it, so finding it in a document means it came
# from the mutation that put it there.
SPELLING = "source-note-marker-271"

# The label `every_role_table` gives to too few rows to publish: the
# small-cell floor withholds it, so it is the exact value a note must
# never carry.
WITHHELD_LABEL = "outlying"


def _document(
    tmp_path: pathlib.Path, text: str = "", forced: "list[str] | None" = None
) -> dict:
    table = reading.read_table(
        str(fixtures.write(tmp_path, "t.csv", text or fixtures.every_role_table()))
    )
    return profile.build_document(table, SETTINGS, forced or [])


def _note_places(document: dict) -> list[dict]:
    return list(document["publication_notes"])


def _first_column_with_notes(document: dict) -> str:
    return f"{document['publication_notes'][0]['column']}"


# -- the guard accepts what the shipped producer builds ---------------


def test_a_genuine_profile_passes_the_guard(tmp_path: pathlib.Path) -> None:
    # The base of every mutation below: without this the red tests
    # would prove only that the guard refuses everything.
    profile.check_publication(_document(tmp_path))


@pytest.mark.parametrize(
    "rows",
    [
        [["2024-01-01T00:15:30.500+05:30", "2024-Q1", "+1.50"]] * 30,
        [["1e999", "(-5)", "-999"]] * 30,
        [["aa" if index < 30 else "AA", "x", "1"] for index in range(33)],
        [["", "one", ""]] * 12,
    ],
)
def test_the_guard_passes_on_every_shape_the_producer_writes(
    tmp_path: pathlib.Path, rows: "list[list[str]]"
) -> None:
    text = fixtures.rows_to_csv(["a", "b", "c"], rows)
    profile.check_publication(_document(tmp_path, text))
    # And again with a declared record-number column, which publishes
    # nothing and takes a different note.
    profile.check_publication(_document(tmp_path, text, ["a"]))


def test_the_guard_passes_where_a_block_withholds_its_own_candidate(
    tmp_path: pathlib.Path,
) -> None:
    # A declared record-number column that also holds a numeric stand-in
    # for "no value": the verdict survives and the spelling of the
    # candidate reads `(withheld)`, which is a leaf the rules authorize
    # and a shape no other case above reaches.
    rows = [["-999" if index < 20 else f"{index}", "x"] for index in range(120)]
    document = _document(
        tmp_path, fixtures.rows_to_csv(["code", "b"], rows), ["code"]
    )
    verdicts = document["columns"][0]["sentinel_verdicts"]
    assert verdicts and verdicts[0]["candidate"] == taxonomy.SUPPRESSED_LABEL
    profile.check_publication(document)


def test_every_sentence_in_a_finished_profile_carries_its_origin(
    tmp_path: pathlib.Path,
) -> None:
    # The property the guard rests on, stated directly: the sentences a
    # genuine profile carries are `taxonomy.Note`s, not strings that
    # happen to match something.
    document = _document(tmp_path)
    sentences = [f"{document['source']['header_evidence']}"]
    carried: list[object] = [document["source"]["header_evidence"]]
    for entry in _note_places(document):
        carried += [entry["note"]]
    for block in document["columns"]:
        carried += [block["detection_evidence"]]
        carried += list(block["remarks"])
    assert len(carried) > 10, "this table should produce many sentences"
    for sentence in carried:
        assert isinstance(sentence, taxonomy.Note)
        assert sentence.form in taxonomy.NOTE_ARITY
        assert f"{sentence}" == taxonomy.rendered(
            sentence.form, sentence.arguments
        )
    assert sentences  # the header verdict is one of them


# -- mutation 1: a source spelling formatted into an existing note ----


def _seam_that_names_a_withheld_label(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Make the pooled-label note name the label it is withholding.

    This is the review's own scenario: an edit to an existing
    note-producing seam that interpolates a source spelling into the
    sentence. The path does not move and the type does not change --
    it is a string under `publication_notes[].note`, exactly as before.
    """
    real = taxonomy._pooled_note

    def leaking(levels: object, settings: object) -> str:
        return f"{real(levels, settings)}: {WITHHELD_LABEL}"

    monkeypatch.setattr(taxonomy, "_pooled_note", leaking)


def test_a_source_spelling_in_an_existing_note_path_is_refused(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _seam_that_names_a_withheld_label(monkeypatch)
    with pytest.raises(errors.ProfileError) as refusal:
        _document(tmp_path)
    assert "publication_notes[].note" in f"{refusal.value}"


def test_that_mutation_really_would_have_published_the_spelling(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # A mutation that changed nothing would make the test above pass for
    # the wrong reason. The seam is asked directly, without the guard in
    # the way, and the withheld label is there.
    _seam_that_names_a_withheld_label(monkeypatch)
    text = fixtures.every_role_table()
    table = reading.read_table(str(fixtures.write(tmp_path, "t.csv", text)))
    described = taxonomy.profile_column(
        "region", 2, table.columns[1], table.n_rows, SETTINGS, False
    )
    assert any(
        WITHHELD_LABEL in f"{note}" for note in described.publication_notes
    ), "the mutated seam must really carry the spelling"


def test_the_refusal_never_repeats_the_text_it_is_refusing(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # A message quoting the offending text would publish to a screen
    # what the guard is refusing to publish to a file.
    _seam_that_names_a_withheld_label(monkeypatch)
    with pytest.raises(errors.ProfileError) as refusal:
        _document(tmp_path)
    assert WITHHELD_LABEL not in f"{refusal.value}"


def test_the_same_mutation_stops_the_command_before_it_writes(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    # The guard runs during construction, before serialization: the
    # command stops with a sentence a person can act on and leaves no
    # file behind.
    _seam_that_names_a_withheld_label(monkeypatch)
    table = fixtures.write(tmp_path, "clinic.csv", fixtures.every_role_table())
    assert cli.main(["profile", str(table)]) == 1
    spoken = capsys.readouterr().err
    assert "synthtwin stopped before writing anything" in spoken
    assert "report it to the synthtwin maintainers" in spoken
    assert WITHHELD_LABEL not in spoken
    left = sorted(place.name for place in tmp_path.iterdir())
    assert left == ["clinic.csv"]


def test_a_finished_note_edited_in_place_is_refused(
    tmp_path: pathlib.Path,
) -> None:
    document = _document(tmp_path)
    entry = _note_places(document)[0]
    entry["note"] = f"{entry['note']} ({SPELLING})"
    with pytest.raises(errors.ProfileError):
        profile.check_publication(document)


def test_a_note_that_keeps_its_form_but_not_its_words_is_refused(
    tmp_path: pathlib.Path,
) -> None:
    # The origin is not a password: a Note whose text no longer matches
    # what its own form writes is refused, so tagging a smuggled
    # sentence with a real form does not get it published.
    document = _document(tmp_path)
    entry = _note_places(document)[0]
    forged = taxonomy.Note(f"{entry['note']} {SPELLING}")
    forged.form = f"{entry['note'].form}"
    forged.arguments = entry["note"].arguments
    entry["note"] = forged
    with pytest.raises(errors.ProfileError):
        profile.check_publication(document)


def test_a_note_whose_arguments_carry_a_spelling_is_refused(
    tmp_path: pathlib.Path,
) -> None:
    document = _document(tmp_path)
    entry = _note_places(document)[0]
    forged = taxonomy.Note(f"{entry['note']}")
    forged.form = f"{entry['note'].form}"
    forged.arguments = (SPELLING,)
    entry["note"] = forged
    with pytest.raises(errors.ProfileError):
        profile.check_publication(document)


def test_a_spelling_cannot_even_be_built_into_a_sentence() -> None:
    # The plan's requirement that such a note fails at CONSTRUCTION
    # rather than at pattern matching.
    with pytest.raises(ValueError):
        taxonomy.note(taxonomy.NOTE_ONE_VALUE_BELOW_FLOOR, (SPELLING,))
    with pytest.raises(ValueError):
        taxonomy.note("a_form_nobody_enumerated")
    with pytest.raises(ValueError):
        taxonomy.note(taxonomy.NOTE_LABELS_POOLED, (1, 2))
    with pytest.raises(ValueError):
        taxonomy.note(taxonomy.NOTE_ONE_VALUE_BELOW_FLOOR, (True,))


# -- mutation 2: a concatenation that assembles the same text ---------


def test_a_sentence_assembled_from_fragments_is_refused(
    tmp_path: pathlib.Path,
) -> None:
    document = _document(tmp_path)
    entry = _note_places(document)[0]
    fragments = [
        "this column is described as free text, so none of its values ",
        "are published: only how long they are, how many words they ",
        "hold, and how often they repeat",
        f" -- for instance {SPELLING}",
    ]
    assembled = ""
    for fragment in fragments:
        assembled = assembled + fragment
    entry["note"] = assembled
    with pytest.raises(errors.ProfileError):
        profile.check_publication(document)


def test_even_an_exact_copy_assembled_from_fragments_is_refused(
    tmp_path: pathlib.Path,
) -> None:
    # Acceptance is by origin, not by resemblance. The same words,
    # assembled rather than written by a constructor, are refused --
    # which is what makes the check unable to be fooled by a sentence
    # that merely LOOKS like prose this package writes.
    document = _document(tmp_path)
    entry = _note_places(document)[0]
    copied = ""
    for fragment in [f"{entry['note']}"[:10], f"{entry['note']}"[10:]]:
        copied = copied + fragment
    assert copied == f"{entry['note']}"
    entry["note"] = copied
    with pytest.raises(errors.ProfileError):
        profile.check_publication(document)


def test_joining_anything_to_a_note_loses_its_origin() -> None:
    # The property of Python that the guard rests on, pinned here so a
    # future change of representation cannot quietly remove it.
    written = taxonomy.note(taxonomy.NOTE_FREE_TEXT_WITHHELD)
    assert isinstance(written, taxonomy.Note)
    for grown in (written + SPELLING, f"{written}{SPELLING}", f"{written}"):
        assert not isinstance(grown, taxonomy.Note)


def test_a_bare_note_without_a_form_is_refused(
    tmp_path: pathlib.Path,
) -> None:
    document = _document(tmp_path)
    entry = _note_places(document)[0]
    entry["note"] = taxonomy.Note(f"{entry['note']}")
    with pytest.raises(errors.ProfileError):
        profile.check_publication(document)


# -- mutation 3: a nested container smuggling a spelling -------------


def test_a_nested_container_carrying_a_spelling_is_refused(
    tmp_path: pathlib.Path,
) -> None:
    document = _document(tmp_path)
    block = document["columns"][0]
    block["examples"] = [{"cell": SPELLING}]
    with pytest.raises(errors.ProfileError):
        profile.check_publication(document)


def test_a_spelling_inside_an_existing_container_is_refused(
    tmp_path: pathlib.Path,
) -> None:
    # Not a new key this time: the spelling is smuggled into a mapping
    # the profile already has, whose keys are words of this package.
    document = _document(tmp_path)
    for block in document["columns"]:
        block["missing_by_class"][SPELLING] = 1
    with pytest.raises(errors.ProfileError):
        profile.check_publication(document)


def test_a_spelling_as_a_key_of_a_shape_summary_is_refused(
    tmp_path: pathlib.Path,
) -> None:
    document = _document(tmp_path)
    smuggled = False
    for block in document["columns"]:
        if "length" in block:
            block["length"][SPELLING] = 3
            smuggled = True
    assert smuggled, "this table should hold a free-text column"
    with pytest.raises(errors.ProfileError):
        profile.check_publication(document)


def test_a_spelling_published_below_the_floor_is_refused(
    tmp_path: pathlib.Path,
) -> None:
    # The guard is not only about sentences: a spelling at a path the
    # matrix authorizes is still refused when the count beside it never
    # cleared the small-cell floor.
    document = _document(tmp_path)
    smuggled = False
    for block in document["columns"]:
        if block.get("levels"):
            block["levels"][0]["variants"][SPELLING] = 1
            smuggled = True
    assert smuggled, "this table should hold a published label"
    with pytest.raises(errors.ProfileError):
        profile.check_publication(document)


def test_a_spelling_at_or_above_the_floor_is_what_the_matrix_allows(
    tmp_path: pathlib.Path,
) -> None:
    # The other side of the same rule, so the test above cannot pass
    # because the guard refuses every spelling everywhere.
    document = _document(tmp_path)
    for block in document["columns"]:
        if block.get("levels"):
            floor = SETTINGS.small_cell_floor
            block["levels"][0]["variants"][SPELLING] = floor
            block["levels"][0]["count"] = block["levels"][0]["count"] + floor
            break
    profile.check_publication(document)


# -- mutation 4: a note lifted to the top level ----------------------


def test_a_note_added_at_the_top_level_is_refused(
    tmp_path: pathlib.Path,
) -> None:
    document = _document(tmp_path)
    document["publication_notes"] = _note_places(document) + [
        {"column": _first_column_with_notes(document), "note": SPELLING}
    ]
    with pytest.raises(errors.ProfileError) as refusal:
        profile.check_publication(document)
    assert "publication_notes[].note" in f"{refusal.value}"


def test_a_top_level_note_about_a_column_that_is_not_there_is_refused(
    tmp_path: pathlib.Path,
) -> None:
    document = _document(tmp_path)
    document["publication_notes"] = _note_places(document) + [
        {
            "column": SPELLING,
            "note": taxonomy.note(taxonomy.NOTE_FREE_TEXT_WITHHELD),
        }
    ]
    with pytest.raises(errors.ProfileError) as refusal:
        profile.check_publication(document)
    assert "publication_notes[].column" in f"{refusal.value}"


def test_a_top_level_key_of_its_own_is_refused(
    tmp_path: pathlib.Path,
) -> None:
    document = _document(tmp_path)
    document["notes_about_the_table"] = [SPELLING]
    with pytest.raises(errors.ProfileError):
        profile.check_publication(document)


# -- fail closed -----------------------------------------------------


def test_a_key_no_rule_names_stops_the_run(tmp_path: pathlib.Path) -> None:
    document = _document(tmp_path)
    document["columns"][0]["a_new_fact"] = 3
    with pytest.raises(errors.ProfileError) as refusal:
        profile.check_publication(document)
    assert "columns[].a_new_fact" in f"{refusal.value}"


def test_a_leaf_of_the_wrong_kind_stops_the_run(
    tmp_path: pathlib.Path,
) -> None:
    document = _document(tmp_path)
    document["columns"][0]["n_present"] = SPELLING
    with pytest.raises(errors.ProfileError):
        profile.check_publication(document)


def test_a_word_outside_its_own_vocabulary_stops_the_run(
    tmp_path: pathlib.Path,
) -> None:
    document = _document(tmp_path)
    document["columns"][0]["role"] = SPELLING
    with pytest.raises(errors.ProfileError):
        profile.check_publication(document)


def test_a_version_that_is_not_this_one_stops_the_run(
    tmp_path: pathlib.Path,
) -> None:
    document = _document(tmp_path)
    document["created_with"] = SPELLING
    with pytest.raises(errors.ProfileError):
        profile.check_publication(document)


def test_a_datetime_endpoint_that_is_a_spelling_stops_the_run(
    tmp_path: pathlib.Path,
) -> None:
    document = _document(tmp_path)
    found = False
    for block in document["columns"]:
        if "earliest" in block:
            block["earliest"] = SPELLING
            found = True
    assert found, "this table should hold a date column"
    with pytest.raises(errors.ProfileError):
        profile.check_publication(document)


def test_a_declared_spelling_cannot_reach_the_settings_block(
    tmp_path: pathlib.Path,
) -> None:
    document = _document(tmp_path)
    document["settings"]["kept_values"] = [SPELLING]
    with pytest.raises(errors.ProfileError):
        profile.check_publication(document)


def test_a_relationship_slot_that_carries_anything_stops_the_run(
    tmp_path: pathlib.Path,
) -> None:
    document = _document(tmp_path)
    document["relationships"]["grain"] = SPELLING
    with pytest.raises(errors.ProfileError):
        profile.check_publication(document)


def test_a_missing_floor_stops_the_run(tmp_path: pathlib.Path) -> None:
    # The guard's own context is read from the document, so it refuses
    # a document that cannot supply it rather than checking against a
    # floor it invented.
    document = _document(tmp_path)
    settings = dict(document["settings"])
    del settings["small_cell_floor"]
    document["settings"] = settings
    with pytest.raises(errors.ProfileError):
        profile.check_publication(document)


# -- the grammar itself ----------------------------------------------


def test_every_enumerated_form_writes_and_rewrites_the_same_words() -> None:
    for form in taxonomy.NOTE_FORMS:
        arguments = _plausible_arguments(form)
        written = taxonomy.note(form, arguments)
        assert f"{written}" == taxonomy.rendered(form, arguments)
        assert len(f"{written}") > 20, f"{form} writes nothing readable"


def test_the_enumeration_and_the_arity_table_are_one_thing() -> None:
    assert sorted(taxonomy.NOTE_FORMS) == sorted(taxonomy.NOTE_ARITY)


def test_rendering_a_form_nobody_enumerated_raises() -> None:
    with pytest.raises(ValueError):
        taxonomy.rendered("a_form_nobody_enumerated", ())


def test_only_enumerated_parts_are_accepted_as_arguments() -> None:
    assert taxonomy.argument_is_enumerated(0)
    assert taxonomy.argument_is_enumerated(11)
    assert taxonomy.argument_is_enumerated(taxonomy.NOTE_ARGUMENT_WORDS[0])
    assert taxonomy.argument_is_enumerated(
        (taxonomy.NOTE_ONE_VALUE_BELOW_FLOOR, (11,))
    )
    for refused in (
        SPELLING,
        -1,
        True,
        1.5,
        None,
        (SPELLING, ()),
        (taxonomy.NOTE_ONE_VALUE_BELOW_FLOOR, (SPELLING,)),
        (taxonomy.NOTE_ONE_VALUE_BELOW_FLOOR, ()),
    ):
        assert not taxonomy.argument_is_enumerated(refused)


def test_the_axis_vocabularies_cover_every_role() -> None:
    # The guard checks each axis against these tuples, so a role added
    # with a shape word nobody listed would be refused at publication.
    for role in taxonomy.ROLES:
        statistical_type, quality_state = taxonomy.ROLE_AXES[role]
        assert statistical_type in taxonomy.STATISTICAL_TYPES
        assert quality_state in taxonomy.QUALITY_STATES
    assert taxonomy.STRUCTURAL_ROLES == ("data", "identifier")


def _plausible_arguments(form: str) -> "tuple[object, ...]":
    """One acceptable set of arguments for any enumerated form."""
    fragment = (taxonomy.SAID_WRITTEN_AS_NUMBERS, (3, 9))
    dates = (taxonomy.SAID_READ_AS_DATES, (2, taxonomy.NOTE_ARGUMENT_WORDS[0]))
    if form == taxonomy.EVIDENCE_NO_READING_FITS:
        return (fragment, dates, 4, 5, 60)
    if form == taxonomy.REMARK_NO_READING_FITS:
        # Seven since the affixed role shipped: how far the affix
        # reading got, and how many cells stand-in judging removed.
        return (fragment, dates, 9, 4, 5, 6, 7)
    if form == taxonomy.EVIDENCE_DATES:
        return (9, 10, taxonomy.NOTE_ARGUMENT_WORDS[0])
    if form == taxonomy.SAID_READ_AS_DATES:
        return (2, taxonomy.NOTE_ARGUMENT_WORDS[0])
    # The two affixed forms take the fourth argument class at two of
    # their positions: an affix spelling, which the grammar admits only
    # there and only under the binding the guard checks. Every other
    # position of every form is a whole number.
    built: list[object] = []
    for place in range(taxonomy.NOTE_ARITY[form]):
        if taxonomy.takes_a_bound_affix(form, place):
            built = built + ["mg"]
        else:
            built = built + [1 + place]
    return tuple(built)
