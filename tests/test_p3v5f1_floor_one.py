"""A floor of one holds nothing back, and every page says only that.

THE TWO DEFECTS THIS FILE EXISTS TO KEEP CLOSED (review round 6, item
P3-V5-F1; repaired under plan amendment A-P3-16).

1. AMENDMENT A-P3-11 PROMISED AN INVARIANT THE LOADER DID NOT ENFORCE.
   Its clause 1, and the contract's own section 4.4 with it, say that at
   a floor of one the "below the floor" half is the empty range, so
   nothing may be held back at all and a document that fills a held-back
   field is refused. Three of those fields were refused. Five were not:
   a producer-derived floor-one description stayed accepted after
   `(withheld)` was put into `missing_by_class`, `missing_by_source`,
   `utc_offsets` or `numeric_styles`, and after
   `n_sentinel_candidates_unpublished` was made nonzero.

2. THE QUALITY REPORT SAID SOMETHING FALSE ON ITS OWN FACE. At a floor
   of one it printed "At 1 nothing is withheld at all ... every line
   below that would have read WITHHELD carries its number instead", and
   then printed eighty-three obligation lines reading WITHHELD, with the
   count of them in its own verdict summary. Two rules put a line there;
   only one of them is the floor's.

HOW THE FIELD SET IS DERIVED, WHICH IS THE POINT OF THE FIRST HALF. The
repair was asked for "everywhere the floor governs, not at the fields
the reviewer listed", and a list of five field names would have been
exactly the mistake that left them unenforced. So no list is written
down here. `test_the_floor_governs_only_positions_the_loader_refuses`
DESCRIBES ONE TABLE TWICE with the real producer -- at a floor of eleven
and at a floor of one -- and reads the floor-governed positions off the
difference between the two documents. Every position that moves is then
grafted back into the floor-one document and the loader must refuse it.
A field added to the format later is covered on the commit that adds it,
as long as the fixture exercises it: `fixtures.every_withholding_table`
is built to exercise every way version 4 has of holding something back,
and its docstring says which column buys which.

THE SECOND HALF OF THE DERIVATION IS LEAF-BY-LEAF, because a field that
records what it held back in its own NAME -- as
`n_sentinel_candidates_unpublished` does -- is invisible to any walk for
the pooled-remainder word.
`test_every_tally_the_floor_zeroes_is_refused_when_it_is_not_zero` reads
that class off the same two documents by measurement: a count the
producer writes nonzero at eleven and zero at one is a tally of what the
floor held back, whatever it is called, and every member of the class
must make the loader refuse.

WHAT THAT DERIVATION DOES NOT COVER, said here rather than left to be
discovered. It sees a field only if a table can be built that makes the
floor move it, so a floor-governed field no fixture exercises is a field
this file cannot see. That is the residual, and the tests below narrow
it two ways: the loader's own rule finds a pooled remainder by WALKING
for the format's one word for "held back" rather than by naming fields,
so a new pooled field is covered whether or not a fixture reaches it;
and the prose positions are pinned, so a new COUNT cannot arrive
disguised as one.
"""

import copy
import json
import pathlib

import pytest

import fixtures
from synthtwin import (
    contract,
    errors,
    generation,
    profile,
    quality,
    reading,
    rendering,
    summary,
    taxonomy,
    validation,
)

# THE STRICT FLOOR THIS FILE MEASURES AGAINST, named here rather than
# read off `taxonomy.Settings()`. The owner lowered the default
# smallest group size to 1 (plan amendment A-P4-37), so the default
# floor now holds nothing back at all -- and a derivation that
# describes one table "at the default floor and at one" would be
# describing it twice the same way and reading an empty difference.
# Eleven is the floor every derivation below was measured on, which
# is why the prose reads "floor-eleven" throughout, so eleven is
# what this file asks for. It must stay above one for any of it to
# mean anything.
_STRICT = 11
assert _STRICT > 1


# -- describing one table at two floors -------------------------------


def _described(folder: pathlib.Path, floor: int) -> dict:
    """The real producer's description of the witness table at ``floor``."""
    folder.mkdir(parents=True, exist_ok=True)
    table = fixtures.write(
        folder, "witness.csv", fixtures.every_withholding_table()
    )
    document = profile.build_document(
        reading.read_table(f"{table}"),
        taxonomy.Settings(small_cell_floor=floor),
        [],
    )
    assert isinstance(document, dict)
    return document


def _walked(node: object, path: tuple) -> "dict[tuple, object]":
    """Every position of a document, as path -> value."""
    seen: dict[tuple, object] = {path: node}
    if isinstance(node, dict):
        for key in sorted(node):
            seen.update(_walked(node[key], path + (key,)))
    elif isinstance(node, list):
        place = 0
        for item in node:
            seen.update(_walked(item, path + (place,)))
            place = place + 1
    return seen


def _moved(strict: dict, loose: dict) -> "list[tuple]":
    """Every position where the two descriptions of one table differ."""
    left = _walked(strict, ())
    right = _walked(loose, ())
    moved: list[tuple] = []
    for path in sorted(set(left) | set(right), key=lambda one: [f"{step}" for step in one]):
        if path not in left or path not in right:
            moved = moved + [path]
        elif isinstance(left[path], (dict, list)):
            continue
        elif left[path] != right[path]:
            moved = moved + [path]
    return moved


# THE THREE KINDS OF POSITION THE FLOOR MOVES THAT ARE NOT COUNTS, each
# named with the reason it is not one. Everything else the floor moves
# must be a position the loader refuses to see filled at a floor of one.
#
# `settings.small_cell_floor` is the floor itself: the input the other
# positions are a function of, and a document carrying a different one
# is a different, entirely valid description.
#
# The other two are PROSE. A note and a remark are sentences written for
# a person, and the loader reads neither for numbers -- which is a
# bounded truth and not a good one: a hand-edited remark can still carry
# a sentence about a group nothing in the document holds back. That is
# recorded in amendment A-P3-16 rather than claimed closed.
_THE_FLOOR_ITSELF = ("settings", "small_cell_floor")


def _is_prose(path: tuple) -> bool:
    """Whether this position holds a sentence rather than a count."""
    if path[:1] == ("publication_notes",):
        return True
    return path[:1] == ("columns",) and "remarks" in path


def _whole_field(path: tuple) -> tuple:
    """The smallest whole field of a block that contains ``path``.

    The graft below moves a FIELD and not a leaf -- a whole
    `missing_by_source`, a whole `levels` list, a whole `utc_offsets` --
    so what lands in the floor-one document is a thing the producer
    really wrote at the strict floor, with its own arithmetic intact.
    A refusal is then about the invariant and not about a total the test
    broke while building its witness.
    """
    if path[0] == "columns":
        return path[:3]
    return path[:2]


def _graft(strict: dict, loose: dict, where: tuple) -> dict:
    """The floor-one document carrying the floor-eleven field at ``where``."""
    made = json.loads(json.dumps(loose))
    source: object = strict
    for step in where:
        assert isinstance(source, (dict, list))
        source = source[step]  # type: ignore[index]
    target: object = made
    for step in where[:-1]:
        assert isinstance(target, (dict, list))
        target = target[step]  # type: ignore[index]
    assert isinstance(target, (dict, list))
    target[where[-1]] = json.loads(json.dumps(source))  # type: ignore[index]
    return made


def _grafted_alive(strict: dict, loose: dict, where: tuple) -> dict:
    """The same graft, in the form the PRODUCER's own guard reads.

    `_graft` sends the document through JSON, which is what the loader
    takes and is exactly wrong for the other half: the publication guard
    runs BEFORE serialization, on a document whose sentences are still
    `taxonomy.Note` objects, and a JSON round trip turns each of them
    into text the guard refuses at `columns[].detection_evidence`. Every
    graft would then be "refused" for a reason that has nothing to do
    with the floor, and the derivation would report the guard enforcing
    an invariant it had never been asked about.

    THAT IS WHY THE PRODUCER'S HALF WAS NEVER ASKED (review item
    P3-V7-F6). The derivation was total over the fields the floor moves
    and was run against the loader alone, so a field the loader refused
    and the guard accepted -- `missing_by_class`'s pooled remainder --
    sat inside the derived class and outside its reach.
    """
    made = copy.deepcopy(loose)
    source: object = strict
    for step in where:
        assert isinstance(source, (dict, list))
        source = source[step]  # type: ignore[index]
    target: object = made
    for step in where[:-1]:
        assert isinstance(target, (dict, list))
        target = target[step]  # type: ignore[index]
    assert isinstance(target, (dict, list))
    target[where[-1]] = copy.deepcopy(source)  # type: ignore[index]
    return made


def _the_guard_refuses(document: dict, where: tuple) -> None:
    """The producer's own guard must refuse to WRITE this document."""
    try:
        profile.check_publication(document)
    except errors.ProfileError as refused:
        said = f"{refused}"
        assert "before writing anything" in said, (
            f"the guard refused {where} in words that do not say the run "
            f"stopped before publishing: {said}"
        )
        return
    raise AssertionError(
        f"the profiler's own publication guard would WRITE a floor-one "
        f"description holding something back at {where}, which its own "
        f"strict loader refuses. The two halves of the product disagree "
        f"about what a floor of one means (amendment A-P3-16 clause 2, "
        f"review item P3-V7-F6)"
    )


def test_the_floor_governs_only_positions_the_loader_refuses(
    tmp_path: pathlib.Path,
) -> None:
    """The derivation, run rather than written down.

    Describe one table at a floor of eleven and at one; every position
    that moves is a position the floor governs; put the floor-eleven
    writing of it back into the floor-one document and the loader must
    refuse it. Nothing here names a field.

    BOTH UNTOUCHED DESCRIPTIONS ARE LOADED FIRST, so that a refusal
    below can only be about the one field that was moved. Without that,
    a graft that happened to break some unrelated total would report the
    invariant enforced when it was not.
    """
    strict = _described(tmp_path / "strict", _STRICT)
    loose = _described(tmp_path / "loose", 1)
    for name, document in (("strict", strict), ("loose", loose)):
        written = fixtures.write_profile(tmp_path, f"{name}.json", document)
        contract.load_profile(f"{written}")

    moved = _moved(strict, loose)
    assert len(moved) > 20, (
        "the witness table stopped making the floor hold things back, so "
        "this derivation is measuring nothing"
    )

    fields: list[tuple] = []
    for path in moved:
        if path == _THE_FLOOR_ITSELF or _is_prose(path):
            continue
        where = _whole_field(path)
        if where not in fields:
            fields = fields + [where]
    assert len(fields) >= 8, (
        "almost every moved position was excused as prose or as the "
        "floor itself, so this test grafted nothing worth grafting"
    )

    rules: list[str] = []
    silent: list[tuple] = []
    for where in fields:
        made = _graft(strict, loose, where)
        written = fixtures.write_profile(tmp_path, "grafted.json", made)
        try:
            contract.load_profile(f"{written}")
        except errors.ProfileError as refused:
            said = f"{refused}"
            assert "make the description again" in said, (
                f"the floor-eleven writing of {where} was refused at a "
                f"floor of one, but not in the words a person can act "
                f"on: {said}"
            )
            if "it is called " in said:
                rules = rules + [
                    said.split("it is called ")[1].split(" in synthtwin")[0]
                ]
            else:
                # An out-of-range refusal (R16) names the entry and the
                # range rather than a rule; the words it uses at a floor
                # of one are the ones amendment A-P3-11 clause 4 wrote.
                rules = rules + ["out-of-range"]
                assert "smallest group size of 1" in said, (
                    f"an out-of-range refusal at a floor of one that does "
                    f"not say so: {said}"
                )
            continue
        silent = silent + [where]
    assert "C5-S13" in rules, (
        "not one of the grafted fields was refused by the rule that says "
        "a floor of one holds nothing back, so this derivation is "
        "passing on rules that were already there"
    )

    # WHAT A FIELD CAN MOVE WITHOUT SAYING SO, measured rather than
    # excused. `sentinel_verdicts` is a LIST, and the floor changes it by
    # leaving an entry out; a shorter list is not a claim about anything,
    # and no invariant of the contract ties its length to a number the
    # document publishes. What records the omission is the tally beside
    # it, `n_sentinel_candidates_unpublished` -- which is one of the five
    # this repair closed. So the whole block is grafted for these, and
    # the block carries its own tally.
    assert silent == [("columns", 3, "sentinel_verdicts")], (
        f"a position the floor moves has stopped being recorded by the "
        f"document: {silent}"
    )
    for where in silent:
        made = _graft(strict, loose, where[:2])
        written = fixtures.write_profile(tmp_path, "block.json", made)
        with pytest.raises(errors.ProfileError):
            contract.load_profile(f"{written}")


def test_every_tally_the_floor_zeroes_is_refused_when_it_is_not_zero(
    tmp_path: pathlib.Path,
) -> None:
    """The shape the pooled-remainder walk cannot see, derived on its own.

    A count that the producer writes NONZERO at a floor of eleven and
    ZERO at a floor of one is a tally of what the floor held back, and
    it says so in its own field name rather than under the pooled
    remainder's word -- so no walk for that word finds it. That class is
    read off the two documents here, leaf by leaf, and every member of
    it must make the loader refuse a floor-one description.

    `n_sentinel_candidates_unpublished` is the member that was accepted
    at any value, at any floor, before amendment A-P3-16. The others
    were already tied to something: a suppressed count with no sizes
    beside it breaks B4.
    """
    strict = _described(tmp_path / "strict", _STRICT)
    loose = _described(tmp_path / "loose", 1)
    left = _walked(strict, ())
    right = _walked(loose, ())
    tallies: list[tuple] = []
    for path in sorted(left, key=lambda one: [f"{step}" for step in one]):
        if path not in right or _is_prose(path):
            continue
        was = left[path]
        now = right[path]
        if isinstance(was, bool) or isinstance(now, bool):
            continue
        if not isinstance(was, int) or not isinstance(now, int):
            continue
        if was > 0 and now == 0:
            tallies = tallies + [path]
    assert len(tallies) >= 3, (
        f"the witness table no longer makes the floor zero a tally, so "
        f"this test is measuring nothing: {tallies}"
    )
    for path in tallies:
        made = _graft(strict, loose, path)
        assert _moved(loose, made) == [path], (
            f"the graft of {path} moved more than that one leaf, so a "
            f"refusal below would not be about it"
        )
        written = fixtures.write_profile(tmp_path, "tally.json", made)
        with pytest.raises(errors.ProfileError):
            contract.load_profile(f"{written}")
        # AND THE OTHER HALF OF THE PRODUCT (review item P3-V7-F6).
        # A tally the reading half refuses and the writing half would
        # publish is the disagreement amendment A-P3-16 clause 2 was
        # written to end, and asking only the reader is how one member
        # of this derived class stayed open through two rounds.
        _the_guard_refuses(_grafted_alive(strict, loose, path), path)


def test_every_pooled_remainder_is_refused_by_the_half_that_writes(
    tmp_path: pathlib.Path,
) -> None:
    """The pooled-remainder walk, run against the PRODUCER'S guard.

    REVIEW ITEM P3-V7-F6, and the derivation rather than the field. The
    class is read off the floor-eleven document by the format's own word
    for "held back" -- every positive count standing under `(withheld)`,
    wherever a field puts it -- and each member is grafted into the
    floor-one document, where the guard that decides what may be WRITTEN
    must refuse it. No field is named here, so a fifth field putting a
    count under that word is in this derivation on the commit that adds
    it, exactly as it is in the loader's.

    WHAT WAS OPEN, AND WHY THE DERIVATION DID NOT SEE IT. Amendment
    A-P3-16 clause 1 built this walk for the loader and clause 2 wrote
    the producer's half as five leaf assertions naming three rule kinds.
    A `missing_by_class` count carries the generic `_COUNT` kind, so it
    sat under none of the three, and the derivation that would have
    caught it was only ever asked of the reading half. The two halves
    are now asked the same question from the same walk.

    AND FROM CONTRACT VERSION 5 THE WALK HAS A SECOND HALF, because one
    remainder stopped standing under the word (that contract's C5-N5 and
    C5-S13). `missing_by_source` now holds one key space -- spellings
    the table wrote -- so a key reading `(withheld)` there is the
    table's own text and not a pool, and the remainder that used to
    stand there is the named field `n_missing_withheld`. The derivation
    therefore reads BOTH: every positive count under the word, and every
    positive count in the one field that says "held back" in its name
    where a spelling map used to say it. Neither half names a field it
    does not have to.
    """
    strict = _described(tmp_path / "strict", _STRICT)
    loose = _described(tmp_path / "loose", 1)
    profile.check_publication(loose)
    remainders = [
        path
        for path, value in _walked(strict, ()).items()
        if path
        and path[-1] in (contract.WITHHELD, "n_missing_withheld")
        and not isinstance(value, bool)
        and isinstance(value, int)
        and value > 0
    ]
    assert len(remainders) >= 4, (
        f"the witness table stopped pooling a remainder anywhere, so "
        f"this derivation is measuring nothing: {remainders}"
    )
    fields = {
        path[-2] if path[-1] == contract.WITHHELD else path[-1]
        for path in remainders
    }
    assert len(fields) >= 4, (
        f"every pooled remainder the witness makes now stands in the "
        f"same field, so this derivation cannot show the walk reaching "
        f"more than one: {sorted(fields)}"
    )
    for path in remainders:
        _the_guard_refuses(_grafted_alive(strict, loose, path), path)


def test_the_prose_positions_really_are_prose(
    tmp_path: pathlib.Path,
) -> None:
    """The excused positions hold sentences, and no number of rows.

    Without this the excuse list above is a way to hide a count: a
    position named prose that carried a count would leave the derivation
    silently narrower than it reads.
    """
    loose = _described(tmp_path, 1)
    strict = _described(tmp_path / "strict", _STRICT)
    for document in (strict, loose):
        for path, value in _walked(document, ()).items():
            if not _is_prose(path):
                continue
            assert not isinstance(value, bool)
            assert not isinstance(value, (int, float)), (
                f"{path} is excused from the derivation as prose, and it "
                f"holds a number"
            )


# -- the five the loader used to accept ------------------------------


def _column(document: dict, name: str) -> dict:
    """One column block of a description, by name."""
    for block in document["columns"]:
        if block["name"] == name:
            assert isinstance(block, dict)
            return block
    raise AssertionError(f"no column called {name!r}")


# THE FIFTH ENTRY MOVED WITH THE FORMAT, and the field it moved to is
# the field the count moved to. Round 6 measured this one on
# `missing_by_source`, whose `(withheld)` key carried the pooled
# remainder; contract version 5 gives that map one key space and puts
# the remainder in `n_missing_withheld` (its C5-N5, C5-S13). The witness
# is the same witness -- a floor-one description that still holds
# something back where the floor pooled it -- read at the field that
# now holds it. Grafting the old field instead would now break a total
# and be refused by the accounting rule, which would say this one is
# enforced when it is not.
_WITNESSES = (
    ("missing_by_class", "visits"),
    ("n_missing_withheld", "visits"),
    ("n_sentinel_candidates_unpublished", "reading"),
    ("utc_offsets", "stamped_at"),
    ("numeric_styles", "amount"),
)


@pytest.mark.parametrize(
    "field,column", _WITNESSES, ids=[one[0] for one in _WITNESSES]
)
def test_each_field_round_six_got_past_the_loader_is_refused(
    tmp_path: pathlib.Path, field: str, column: str
) -> None:
    """The five exact mutations, one test each, naming the rule.

    These are pinned separately from the derivation above because a
    derivation that stops seeing one of them must not go quietly green:
    the reviewer measured these five on the shipped loader and they are
    the record of what was open.
    """
    strict = _described(tmp_path / "strict", _STRICT)
    loose = _described(tmp_path / "loose", 1)
    held = _column(strict, column)[field]
    assert held != _column(loose, column)[field], (
        f"{column}.{field} no longer differs between the two floors, so "
        f"this witness has stopped witnessing"
    )
    made = json.loads(json.dumps(loose))
    _column(made, column)[field] = held
    written = fixtures.write_profile(tmp_path, "held.json", made)
    with pytest.raises(errors.ProfileError) as refused:
        contract.load_profile(f"{written}")
    said = f"{refused.value}"
    assert "S13" in said, (
        f"a floor-one description holding something back in {field} was "
        f"refused, but not by the rule that says it may not: {said}"
    )
    assert "the smallest group size is 1" in said, (
        "the refusal does not end with the floor it is measured against, "
        "which is how every other floor-governed refusal reads"
    )
    assert column in said, "the refusal does not say which column"


def test_the_pooled_remainder_is_found_by_walking_not_by_a_field_list(
) -> None:
    """The rule reaches a field version 4 does not have.

    THIS IS THE CLAIM THE REPAIR RESTS ON. Five fields were unenforced
    because each was checked where it was written, so a sixth would have
    been unenforced too. The loader now looks for the format's one word
    for "held back" wherever it stands, and this hands it a shape no
    version-4 document has to prove that it does.
    """
    made_up = {
        "columns": [
            {
                "name": "a",
                "a_block_nobody_has_written_yet": {
                    "deeper": {contract.WITHHELD: 4},
                },
            }
        ]
    }
    found = contract._held_back_in(made_up, ())
    assert [(path, count) for path, count, _kind in found] == [
        (
            (
                "columns",
                0,
                "a_block_nobody_has_written_yet",
                "deeper",
                contract.WITHHELD,
            ),
            4,
        )
    ]


def test_a_remainder_of_zero_is_not_a_remainder() -> None:
    """`missing_by_class` always carries the key, usually holding zero.

    A rule that refused the KEY rather than a count under it would
    refuse every description ever written, at every floor.
    """
    assert contract._held_back_in({contract.WITHHELD: 0}, ()) == []


@pytest.mark.parametrize("floor", (_STRICT, 2))
def test_a_remainder_above_a_floor_of_one_is_left_alone(
    tmp_path: pathlib.Path, floor: int
) -> None:
    """The new rule binds at one and says nothing above it.

    A remainder pools several groups that each fell below the floor, so
    at eleven a remainder of twelve is ordinary. A rule that bounded it
    anywhere but at the bottom would refuse descriptions the producer
    writes.
    """
    document = _described(tmp_path, floor)
    written = fixtures.write_profile(tmp_path, "ordinary.json", document)
    loaded = contract.load_profile(f"{written}")
    assert loaded.settings.small_cell_floor == floor
    pooled = 0
    for block in document["columns"]:
        for field in ("missing_by_class", "missing_by_source"):
            entry = block.get(field, {})
            if isinstance(entry, dict) and contract.WITHHELD in entry:
                pooled = pooled + entry[contract.WITHHELD]
    if floor == _STRICT:
        assert pooled > 0, (
            "the witness table pools nothing at the strict floor, so "
            "this test would pass on a loader that refused every pool"
        )


def test_the_producer_writes_a_floor_one_description_the_loader_takes(
    tmp_path: pathlib.Path,
) -> None:
    """The whole point of the ruling still works.

    A rule this strict has one obvious way to go wrong: refusing the
    producer's own output. The producer holds nothing back at a floor of
    one, so its description passes, and the whole workflow runs on it.
    """
    document = _described(tmp_path, 1)
    written = fixtures.write_profile(tmp_path, "one.json", document)
    loaded = contract.load_profile(f"{written}")
    built = generation.generate(loaded, 7)
    twin = fixtures.write(tmp_path, "twin.csv", rendering.twin_csv(built))
    outcome = validation.measure(loaded, f"{twin}")
    assert outcome.census.missed == 0, (
        "the twin of a floor-one description misses an obligation"
    )


def test_the_two_halves_of_the_floor_are_one_range() -> None:
    """`_below_the_floor` is the range every floor rule is written on.

    At one it is empty, which is the whole of invariant S13; at zero it
    is empty too, and zero is refused elsewhere for a different reason.
    """
    assert list(contract._below_the_floor(1)) == []
    assert list(contract._below_the_floor(2)) == [1]
    assert list(contract._below_the_floor(11)) == [
        1, 2, 3, 4, 5, 6, 7, 8, 9, 10
    ]


# -- the producer's own guard says the same thing ---------------------


def test_the_publication_guard_refuses_a_pool_at_a_floor_of_one() -> None:
    """The other writing of the rule, on the producer's side.

    The profiler checks its own finished document before it writes a
    byte, and its rule for a pooled entry accepted any count of one or
    more whatever the floor was -- so the two halves of the product
    disagreed about what a floor of one means. They agree now.
    """
    at_one = profile._Publication(floor=1, names=("a",))
    at_eleven = profile._Publication(floor=11, names=("a",))
    somewhere = ("columns", profile._EACH, "numeric_styles", profile._ANY_KEY)
    assert not profile._leaf_is_published(
        profile._FLOORED_ENTRY, 3, contract.WITHHELD, somewhere, at_one
    )
    assert profile._leaf_is_published(
        profile._FLOORED_ENTRY, 3, contract.WITHHELD, somewhere, at_eleven
    )
    assert not profile._leaf_is_published(
        profile._HELD_BACK, 1, "suppressed_levels", somewhere, at_one
    )
    assert profile._leaf_is_published(
        profile._HELD_BACK, 0, "suppressed_levels", somewhere, at_one
    )
    assert not profile._leaf_is_published(
        profile._BELOW_THE_FLOOR, 1, "", somewhere, at_one
    )
    assert profile._leaf_is_published(
        profile._BELOW_THE_FLOOR, "7", "", somewhere, at_eleven
    )
    # THE ONE MAP WHOSE KEYS ARE THE TABLE'S OWN TEXT (contract 5
    # C5-N5). A count standing under those ten characters there is a
    # count of cells that held them, not a pool, and refusing it at a
    # floor of one would refuse the very description version 5 exists to
    # make writable. The remainder that used to stand there is
    # `n_missing_withheld`, held to the rule under its own kind above.
    one_key_space = (
        "columns", profile._EACH, "missing_by_source", profile._ANY_KEY
    )
    assert profile._leaf_is_published(
        profile._FLOOR_COUNT, 3, contract.WITHHELD, one_key_space, at_one
    )
    assert not profile._leaf_is_published(
        profile._HELD_BACK, 3, "n_missing_withheld", somewhere, at_one
    )


def test_every_floor_governed_rule_of_the_guard_has_a_path(
    tmp_path: pathlib.Path,
) -> None:
    """The new rule kinds are used, not merely defined.

    A vocabulary word nothing is filed under is a word that cannot
    fail.
    """
    used = set(profile.PUBLICATION_RULES.values())
    assert profile._HELD_BACK in used
    assert profile._BELOW_THE_FLOOR in used
    document = _described(tmp_path, 1)
    profile.check_publication(document)


# -- the report says only what is true --------------------------------


def _deviating(folder: pathlib.Path, floor: int) -> "tuple[str, int]":
    """A floor-``floor`` report whose type gate really fires.

    The checked file holds words where the description publishes
    numbers, so `synthtwin validate` withholds every measurement that
    describing THAT file would not publish. That is the second of the
    two rules that put WITHHELD on a line, and it is untouched by the
    floor -- which is exactly what the sentence this test guards used to
    deny.
    """
    folder.mkdir(parents=True, exist_ok=True)
    header = ["amount", "visits", "recorded_on"]
    rows = [
        [
            f"{(index * 7) % 97 + 0.5:.2f}",
            f"{index % 9}",
            f"2024-{(index % 12) + 1:02d}-{(index % 28) + 1:02d}",
        ]
        for index in range(60)
    ]
    table = fixtures.write(folder, "t.csv", fixtures.rows_to_csv(header, rows))
    document = profile.build_document(
        reading.read_table(f"{table}"),
        taxonomy.Settings(small_cell_floor=floor),
        [],
    )
    described = fixtures.write_profile(folder, "t-profile.json", document)
    loaded = contract.load_profile(f"{described}")
    words = fixtures.write(
        folder,
        "words.csv",
        fixtures.rows_to_csv(
            header, [["alpha", "beta", "gamma"] for _index in range(60)]
        ),
    )
    outcome = validation.measure(loaded, f"{words}")
    return quality.quality_report(loaded, outcome), outcome.census.withheld


# The absolute claims about withholding that no page may make. Each one
# says "nothing is withheld", full stop -- and the type gate makes every
# one of them false whenever it fires, whatever the floor is.
_ABSOLUTE = (
    "nothing is withheld at all",
    "nothing is withheld",
    "nothing at all is withheld",
    "no line below reads WITHHELD.",
)


def test_the_floor_one_report_does_not_claim_nothing_is_withheld(
    tmp_path: pathlib.Path,
) -> None:
    """The measured contradiction, pinned.

    The report printed the absolute sentence and then eighty-three
    WITHHELD lines. This asserts both halves: that the file really does
    withhold, and that the page no longer says it does not.

    WHERE THE BOUNDED SENTENCE IS READ, since amendment A-P4-37. The
    half of this test that reads what a floor of one DOES buy used to
    read it out of the "SMALLEST GROUP SIZE LOWERED TO 1" section, which
    `quality._lowered_floor_lines` prints only where the floor is below
    the default. The owner lowered the default to 1 (A-P4-37), so a
    floor of one is no longer a lowering and that section is rightly
    absent: it exists to warn a reader that THIS description publishes
    smaller groups than synthtwin usually does, which is no longer true
    of a floor of one. The same bounded promise is made in the
    withholding rule at the foot of every report, by
    `quality._floor_gate_lines`, and that is where it is read now: both
    halves of it, the "nothing is held back THIS WAY" and the naming of
    which way, so a report that dropped either still goes red here.
    """
    text, withheld = _deviating(tmp_path, 1)
    assert withheld > 0, (
        "the checked file no longer makes the type gate fire, so this "
        "test could pass on a report that still claimed too much"
    )
    assert f"{withheld}  WITHHELD" in text, (
        "the verdict summary does not print the withheld count, so the "
        "contradiction this test is about cannot be read off the page"
    )
    for absolute in _ABSOLUTE:
        assert absolute not in text, (
            f"the report says {absolute!r} on a page that withholds "
            f"{withheld} obligation(s)"
        )
    assert "held back this way at all" in text, (
        "the report no longer tells the reader what a floor of one does "
        "buy them"
    )
    assert "being a group too small to name" in text, (
        "the report says nothing is held back this way without saying "
        "which way, which is the absolute claim again in fewer words"
    )


@pytest.mark.parametrize("floor", (_STRICT, 2, 1))
def test_no_page_claims_nothing_is_withheld_at_any_floor(
    tmp_path: pathlib.Path, floor: int
) -> None:
    """The same shape, looked for in all three written pages.

    Read at a strict floor and at lower ones, because the
    lowered-floor sections are the ones written most recently and least
    often read.
    """
    folder = tmp_path / f"floor-{floor}"
    document = _described(folder, floor)
    described = fixtures.write_profile(folder, "witness.json", document)
    loaded = contract.load_profile(f"{described}")
    built = generation.generate(loaded, 7)
    twin = fixtures.write(folder, "twin.csv", rendering.twin_csv(built))
    pages = {
        "the plain-language summary": summary.render(document, ""),
        "the generation report": rendering.report(loaded, built),
        "the quality report": quality.quality_report(
            loaded, validation.measure(loaded, f"{twin}")
        ),
    }
    for what in sorted(pages):
        for absolute in _ABSOLUTE:
            assert absolute not in pages[what], (
                f"{what} at a floor of {floor} says {absolute!r}, which "
                f"no page can promise: the type gate withholds lines for "
                f"a reason the floor does not decide"
            )


def test_the_narrower_wording_was_already_right_next_door() -> None:
    """The two sentences about the floor of one now agree.

    `_floor_gate_lines` has said the bounded thing all along -- nothing
    is held back THIS WAY -- while the section at the head of the report
    said the absolute one. This keeps them from drifting apart again.
    """
    gate = "\n".join(quality._floor_gate_lines(1))
    assert "held back this way at all" in gate
    assert "nothing is withheld at all" not in gate


# -- what an offset is, written twice ---------------------------------


def _offset_candidates() -> "list[str]":
    """Every string worth asking both writings about, built rather than listed."""
    made: list[str] = ["", "Z", "z", "(none)", "(withheld)", "+0200", "Q", "ZZ"]
    for hours in (0, 2, 5, 9, 10, 14, 23, 99):
        for minutes in (0, 15, 30, 45, 60):
            for sign in ("+", "-"):
                made = made + [f"{sign}{hours:02d}:{minutes:02d}"]
    return made


def test_the_two_writings_of_an_offset_accept_the_same_strings() -> None:
    """The profiler's guard and the strict loader agree, string by string.

    THEY DISAGREED ON EXACTLY ONE STRING AND IT WAS `Z` (found while
    repairing review item P3-V5-F1; plan amendment A-P3-16 clause 4).
    The producer writes `Z` for a cell whose time is stamped in UTC,
    the loader accepts it wherever an offset may stand, and the
    profiler's own publication guard did not -- so `synthtwin profile`
    refused every table of UTC-stamped times, telling the person it was
    a fault in synthtwin and giving them no way to describe their table.
    """
    for text in _offset_candidates():
        assert profile._is_offset(text) == contract._is_an_offset(text), (
            f"the two writings of what a UTC offset is disagree about "
            f"{text!r}"
        )


def test_a_table_stamped_in_utc_runs_the_whole_workflow(
    tmp_path: pathlib.Path,
) -> None:
    """The defect as a person met it: profile, generate, validate.

    The witness table's `stamped_at` column ends in `Z`, so this is the
    end-to-end form of the test above.
    """
    document = _described(tmp_path, _STRICT)
    offsets = _column(document, "stamped_at")["utc_offsets"]
    assert "Z" in offsets, (
        "the witness table's times are no longer stamped in UTC, so this "
        "test no longer covers the defect it is named for"
    )
    described = fixtures.write_profile(tmp_path, "utc.json", document)
    loaded = contract.load_profile(f"{described}")
    built = generation.generate(loaded, 7)
    twin = fixtures.write(tmp_path, "twin.csv", rendering.twin_csv(built))
    outcome = validation.measure(loaded, f"{twin}")
    for check in outcome.checks:
        if check.column == "stamped_at":
            assert check.verdict != validation.MISSED, (
                f"the twin of a UTC-stamped column misses "
                f"{check.subcheck}"
            )
