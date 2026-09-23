"""P4-D27: the contract's note grammar and the producer's are one grammar.

WHY THIS FILE EXISTS, AND WHAT IT COST TO NOT HAVE IT. Contract 4.5.1
is the authority on every sentence a profile may carry: each form's
name, how many arguments it takes and what class each argument is.
`taxonomy.NOTE_ARITY` is what the producer actually emits. Section 14.8
summarises the same thing a third time as an appendix table. **Nothing
compared them**, and residual R-P4-29 recorded five mismatches found
by hand while building the date readings.

Measured when this guard was written, the real number was TEN, and four
of them were worse in kind than the five recorded:

* `evidence_long_tail_of_labels`, `evidence_clock_times`,
  `evidence_numbers_joined_in_one_cell` and
  `evidence_numbers_wearing_one_affix` -- the detection-evidence
  sentences of ALL FOUR roles Phase 4 added -- were emitted by the
  shipped producer and appeared in NO contract clause and NO appendix
  row. A second implementer reading the contract could not have
  reproduced a sentence this tool writes on any table carrying a clock,
  an affixed number, a joined reading or a long tail of labels.
* The package-word vocabulary was stated as nineteen and the producer
  carried twenty-one: the two clock words NF46 names a form by were
  missing, so a producer written to the contract would have REFUSED
  the clock evidence sentence outright.

Both are closed by the landing that adds this file. The remaining five
were the arity mismatches R-P4-29 named, held below as NAMED
EXCEPTIONS, and every one of them was the same thing: **four advisory
remarks that amendment A-P4-30 withdrew from this phase's scope,
transcribed into the contract before the withdrawal.** They close when
those remarks are built, and the exception list is how this guard says
so out loud instead of being weakened to accommodate them.

**THREE OF THE FIVE ARE NOW CLOSED (residual R-P4-24).** The advisory
remarks landed and their rows left this table because the contract and
the producer agree again, not because the table was relaxed. Two rows
remain, both of the code-shaped family, and the reason each one cannot
be reconciled by arity alone is written on it.

THE GUARD RUNS IN BOTH DIRECTIONS, and the direction that was missing
is the one that mattered. A one-way check ("every contract form is in
the producer") is satisfied by a producer that emits forms nobody
wrote down, which is exactly the state four roles were in.
"""

import re

from synthtwin import parsing, taxonomy

import fixtures

# Derived, never named: review item P4-A1-R3-F2.
CONTRACT = fixtures.GOVERNING_CONTRACT

# WHAT AMENDMENT A-P4-30 ACCOUNTS FOR AND HAS NOT YET GIVEN BACK, each
# with the arity the contract states, the arity the producer emits, and
# the landing that closes it. A form leaving this table must leave
# because it was RECONCILED, and a form joining it is a decision
# somebody records -- which is why the reason is written per row rather
# than as a comment over the whole table.
#
# **IT HELD FIVE ROWS UNTIL THE ADVISORY-REMARK LANDING (residual
# R-P4-24) AND HOLDS TWO.** Three were reconciled by building the form
# the contract had already written down, and the rows went with them:
# `remark_dates_also_read_as_numbers` states both counts (NF25),
# `remark_no_reading_fits` carries the clock clause and the
# recoverable-distribution advice at arguments 8 and 9 (NF29), and
# `remark_a_label_is_a_built_in_stand_in` is emitted (NF37).
KNOWN_MISMATCHES = {
    # THE CODE-SHAPED REMARKS, AND THEY ARE A SCOPE DECISION RATHER
    # THAN AN ARITY TO RECONCILE -- which is why they stayed here when
    # the other three left (residual R-P4-72). The contract's argument
    # 1 counts the present cells that share a value with another row,
    # and its second rendering exists for REPEATING code columns; the
    # producer raises these two only where every value differs, so the
    # argument would be zero at every call site and the second
    # rendering could not be reached. Adding the argument alone would
    # therefore build a rendering nothing can ever write, which is the
    # "a check that cannot fail" shape this repository refuses.
    #
    # AND THE WIDENING ITSELF IS NOT A TRANSCRIPTION. P4-D4.7 gives
    # the code-shape test as "all-whole, nearly-never-repeating, or
    # fixed-width leading-zero digit strings", and EVERY `count`
    # column is all-whole by that role's own definition
    # (`whole_everywhere` in `taxonomy._numeric_verdict`), so the
    # plan's first test would put this sentence on every count column
    # in every profile. Which columns carry a sentence is a published
    # fact of the document, so that is an owner-sized decision and not
    # this landing's to take.
    "remark_every_number_is_different": (1, 0),
    "remark_every_value_is_different": (1, 0),
}

_DEFINING = re.compile(
    r"\*\*NF(\d+)\.\s*`([a-z0-9_]+)`"
    r"(?:(?!\*\*NF)[\s\S]){0,300}?arity\s+(\d+)"
)
_APPENDIX = re.compile(r"^\|\s*NG(\d+)\s*\|\s*`([a-z0-9_]+)`\s*\|\s*(\d+)\s*\|", re.MULTILINE)


def _contract() -> str:
    return CONTRACT.read_text(encoding="utf-8")


def _defining() -> "dict[str, int]":
    """Every form the contract DEFINES, by name, with its stated arity."""
    text = _contract()
    found: dict[str, int] = {}
    for match in _DEFINING.finditer(text):
        # A clause may carry a dash-title between the name and the
        # arity ("NF29. `x` -- the competing-readings remark -- arity
        # 9"), so the pattern spans to the arity rather than requiring
        # them adjacent.
        # A SECOND CLAUSE FOR ONE NAME IS A DEFECT, not something to
        # resolve. `setdefault` let an added clause with a different
        # arity lose silently to the first, which is the failure this
        # whole file exists to refuse one level up.
        name, arity = match.group(2), int(match.group(3))
        if name in found and found[name] != arity:
            raise AssertionError(
                f"contract 4.5.1 defines {name} twice, with arity "
                f"{found[name]} and {arity}"
            )
        found[name] = arity
    return found


def _banners() -> "list[str]":
    """Every `**NFnn. `name`**` banner, whether or not it parsed."""
    return re.findall(r"\*\*NF\d+\.\s*`([a-z0-9_]+)`", _contract())


def test_every_clause_the_contract_writes_is_one_this_guard_can_read() -> None:
    """A clause the parser cannot read is a clause it cannot check.

    ROUND 2 ITEM 9. `_defining` matches "arity N". A clause written
    "takes 1 argument" is not matched at all, and the guard then
    compares a map that silently lacks it and reports green -- the
    exact shape of the drift it was built to catch. Counting banners
    against parsed clauses closes that: an unreadable clause is now a
    failure rather than an omission.
    """
    banners = _banners()
    parsed = _defining()
    unreadable = sorted(set(banners) - set(parsed))
    assert not unreadable, (
        "these clauses are written in a shape `_defining` cannot read, "
        f"so the guard was not checking them: {unreadable}"
    )
    assert len(banners) == len(set(banners)), (
        "a form name carries two banners: "
        + repr(sorted({n for n in banners if banners.count(n) > 1}))
    )
    assert len(parsed) == len(banners)


def _appendix_rows() -> "list[tuple[str, int]]":
    """Every appendix row as written, duplicates included."""
    return [
        (m.group(2), int(m.group(3))) for m in _APPENDIX.finditer(_contract())
    ]


def _appendix() -> "dict[str, int]":
    """Every form the 14.8 appendix table lists, with its arity.

    ROUND 4 ITEM 2: a duplicate row used to collapse into this
    dictionary and change nothing, so the appendix could grow a
    forty-ninth row and every count derived from it stay put. A repeat
    is a defect and stops the read.
    """
    rows = _appendix_rows()
    found: dict[str, int] = {}
    for name, arity in rows:
        if name in found:
            raise AssertionError(
                f"the 14.8 appendix lists {name} twice; a repeated row "
                "is invisible to every count taken from this table"
            )
        found[name] = arity
    return found


def test_the_contract_defines_every_form_the_producer_emits() -> None:
    """No shipped sentence is one the contract never wrote down.

    THE DIRECTION THAT WAS MISSING. Four roles' evidence sentences
    shipped with no clause and no appendix row, so a second implementer
    had nothing to reproduce them from.
    """
    defining = _defining()
    appendix = _appendix()
    undefined = sorted(set(taxonomy.NOTE_ARITY) - set(defining))
    unlisted = sorted(set(taxonomy.NOTE_ARITY) - set(appendix))
    assert not undefined, (
        "the producer emits sentences that contract 4.5.1 does not "
        f"define: {undefined}"
    )
    assert not unlisted, (
        "the producer emits sentences the 14.8 appendix does not list: "
        f"{unlisted}"
    )


def test_the_producer_emits_every_form_the_contract_defines() -> None:
    """No contract form is one no producer could ever write.

    A form specified and never emitted is a loader that would refuse a
    conforming document, which is how residual R-P4-37 was found on the
    role topology.
    """
    missing = sorted(set(_defining()) - set(taxonomy.NOTE_ARITY))
    unexplained = [
        name
        for name in missing
        if KNOWN_MISMATCHES.get(name, (None, 0))[1] is not None
    ]
    assert not unexplained, (
        "the contract defines sentences no producer can write, and no "
        f"amendment accounts for them: {unexplained}"
    )


def test_the_three_statements_of_every_arity_agree() -> None:
    """Defining clause, appendix row and producer state one number.

    The three disagreed about five forms with nothing comparing them
    (residual R-P4-29). Any mismatch not in `KNOWN_MISMATCHES`
    fails here.
    """
    defining = _defining()
    appendix = _appendix()
    offenders: list[str] = []
    for name in sorted(set(defining) | set(appendix) | set(taxonomy.NOTE_ARITY)):
        stated = defining.get(name)
        listed = appendix.get(name)
        emitted = taxonomy.NOTE_ARITY.get(name)
        if stated == listed == emitted:
            continue
        if KNOWN_MISMATCHES.get(name) == (stated, emitted) and stated == listed:
            continue
        offenders.append(
            f"{name}: clause {stated}, appendix {listed}, producer {emitted}"
        )
    assert not offenders, "the note grammar has drifted:\n" + "\n".join(offenders)


def test_every_named_disagreement_is_still_real() -> None:
    """The exception list may not outlive the drift it excuses.

    A guard whose exceptions are never re-checked becomes a list of
    things nobody looks at. When a remark of A-P4-30 is built, its row
    here stops matching and this turns red, which is the reminder to
    delete the row.
    """
    defining = _defining()
    stale = [
        name
        for name, (stated, emitted) in KNOWN_MISMATCHES.items()
        if defining.get(name) == taxonomy.NOTE_ARITY.get(name)
        or (defining.get(name), taxonomy.NOTE_ARITY.get(name)) != (stated, emitted)
    ]
    assert not stale, (
        "these forms no longer disagree the way KNOWN_MISMATCHES "
        f"says, so their rows are stale and should be deleted: {stale}"
    )


# The binding column of contract 4.5.1's C6-143 table, one row per
# argument position: | `form` | argument (1-based) | bound to |.
_BINDING_ROW = re.compile(
    r"^\|\s*`([a-z0-9_]+)`\s*\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|$", re.MULTILINE
)


def _binding_text(binding: "tuple[object, ...]") -> str:
    """How C6-143 writes one binding, from the code's own table.

    THE ONE TRANSLATION, so that the comparison below is between the
    contract's rows and the producer's table and not between two
    spellings of the same thing. Every branch is a fixed phrase of the
    contract; a binding kind with no branch stops the read, which is
    the same refusal `taxonomy.unbound_argument_positions` makes one
    level up.
    """
    kind = binding[0]
    if kind == taxonomy.BIND_KEY:
        return f"key `{binding[1]}`"
    if kind == taxonomy.BIND_SUM:
        return "sum " + " + ".join(f"`{name}`" for name in binding[1])
    if kind == taxonomy.BIND_DIFFERENCE:
        return f"difference `{binding[1]}` less `{binding[2]}`"
    if kind == taxonomy.BIND_DOCUMENT:
        return f"document key `{binding[1]}`"
    if kind == taxonomy.BIND_MAIN_WRAPPER:
        return "main wrapper"
    if kind == taxonomy.BIND_SETTING:
        return f"setting ({binding[1]})"
    if kind == taxonomy.BIND_LEVELS_AT_THE_LINE:
        return "levels at the line"
    if kind == taxonomy.BIND_VOCABULARY:
        return "vocabulary"
    if kind == taxonomy.BIND_STRUCTURAL:
        return "structural"
    if kind == taxonomy.BIND_VALUE:
        return "value (tail rule)"
    if kind == taxonomy.BIND_FLOORED:
        if len(binding) > 1:
            return "floored against " + ", ".join(
                f"`{name}`" for name in binding[1]
            )
        return "floored"
    if kind == taxonomy.BIND_WORD:
        return "package word"
    if kind == taxonomy.BIND_NESTED:
        return "nested form"
    if kind == taxonomy.BIND_AFFIX:
        return "bound affix"
    raise AssertionError(f"no contract wording for the binding kind {kind!r}")


def _contract_bindings() -> "dict[tuple[str, int], str]":
    """Every row of the C6-143 table, keyed by (form, zero-based position)."""
    found: "dict[tuple[str, int], str]" = {}
    for match in _BINDING_ROW.finditer(_contract()):
        key = (match.group(1), int(match.group(2)) - 1)
        if key in found:
            raise AssertionError(
                f"C6-143 binds {key[0]} argument {key[1] + 1} twice; a "
                "repeated row is invisible to every count taken from "
                "this table"
            )
        found[key] = match.group(3)
    return found


def _code_bindings() -> "dict[tuple[str, int], tuple[object, ...]]":
    """The producer's table, the two contract-only positions included."""
    bound = dict(taxonomy.ARGUMENT_BINDINGS)
    bound.update(taxonomy.ARGUMENT_BINDINGS_STATED_NOT_EMITTED)
    return bound


def test_the_producer_binds_every_argument_it_can_print() -> None:
    """THE THIRD DIRECTION, ASKED OF THE CODE ALONE.

    `NOTE_ARITY` says how many arguments a form takes and C6-143 says
    what each one IS. A position with no binding is a number a sentence
    may print that no rule governs -- which is the state every one of
    the 94 positions was in before stage 3 landing 3.5, and how nine
    sentence arguments came to print counts no key of the block beside
    them published at all.
    """
    assert taxonomy.unbound_argument_positions() == []
    kinds = {
        taxonomy.ARGUMENT_BINDINGS[place][0]
        for place in taxonomy.ARGUMENT_BINDINGS
    }
    assert kinds <= set(taxonomy.BINDING_KINDS)


def test_the_contract_binding_column_is_the_codes_binding_table() -> None:
    """The third direction of this file's guard: the BINDINGS agree.

    The two directions above compare how many arguments each form
    takes. They say nothing about what those arguments are, and a
    contract whose binding column drifted from the code would send a
    second implementer's guard looking at the wrong key -- which is
    the same silence that let four whole forms ship undefined.

    Both tables carry the two positions
    `tests/test_p4d27_note_grammar_matches_the_code.py` records as
    known arity mismatches, so the comparison is over exactly the
    contract's 97 positions.
    """
    stated = _contract_bindings()
    emitted = _code_bindings()
    missing = sorted(set(emitted) - set(stated))
    extra = sorted(set(stated) - set(emitted))
    assert not missing, (
        "the producer binds argument positions that contract 4.5.1's "
        f"C6-143 table does not list: {missing}"
    )
    assert not extra, (
        "C6-143 binds argument positions no form of this producer has: "
        f"{extra}"
    )
    drifted = [
        f"{form} argument {place + 1}: contract {stated[(form, place)]!r}, "
        f"code {_binding_text(emitted[(form, place)])!r}"
        for form, place in sorted(emitted)
        if stated[(form, place)] != _binding_text(emitted[(form, place)])
    ]
    assert not drifted, "the argument bindings have drifted:\n" + "\n".join(
        drifted
    )


def test_the_floored_positions_are_the_ones_the_contract_marks_floored() -> None:
    """Thirteen positions carry a count no key of the block publishes.

    They are the only ones the census line is asked about directly, and
    the only ones `said_fewer_than_the_line` may stand at. Stating the
    number in the contract and deriving it here is what keeps a
    fourteenth from being added in the code alone.
    """
    stated = {
        place
        for place, text in _contract_bindings().items()
        if text.startswith("floored")
    }
    assert stated == set(taxonomy.FLOORED_POSITIONS)
    assert len(taxonomy.FLOORED_POSITIONS) == 13
    written = re.search(
        r"THE (\w+) POSITIONS WHERE THE SENTENCE IS THE\n  PUBLICATION",
        _contract(),
    )
    assert written is not None, "C6-143 no longer states how many are floored"
    assert written.group(1) == "THIRTEEN"


def test_the_package_word_vocabulary_is_the_one_the_contract_states() -> None:
    """The second argument class is one closed list, counted once.

    It read nineteen while the producer carried twenty-one: the two
    clock words were missing, so a producer written to the contract
    would refuse NF46. The count is asserted from the PARTS rather than
    against a literal, so a new format member moves it honestly.
    """
    words = taxonomy.NOTE_ARGUMENT_WORDS
    assert len(set(words)) == len(words), "a package word is listed twice"
    assert set(words) == (
        set(parsing.DATE_FORMATS)
        | set(taxonomy.NOTE_CLOCK_WORDS)
        | set(taxonomy.NOTE_READING_WORDS)
        # THE TWO UNITS A POPULATION IS COUNTED IN (plan P4-D341,
        # contract 14.4a). They join this class for the reason the
        # clock words did: NF59 names a form's second argument by one
        # of them, so a producer written to a contract that omitted
        # them would refuse the sentence the tool writes.
        | set(taxonomy.NOTE_UNIT_WORDS)
    )
    stated = re.search(r"\*\*The package-word vocabulary — (\d+)\*\*", _contract())
    assert stated is not None, "the contract no longer states the count"
    assert int(stated.group(1)) == len(words), (
        f"the contract states {stated.group(1)} package words and the "
        f"producer carries {len(words)}"
    )
    # The clock words are named, and named as NOT being format members:
    # a reader who took them for `format` values would write them into
    # a key the loader refuses. The two units are held to the same two
    # things, for the same reason.
    for word in taxonomy.NOTE_CLOCK_WORDS + taxonomy.NOTE_UNIT_WORDS:
        assert f"`{word}`" in _contract(), f"the contract never names {word}"
        assert word not in parsing.DATE_FORMATS



# Where the contract states the size of the note grammar, in any of the
# shapes it uses. Round 3 item 2 found a NINTH site still saying 44 --
# and there were two, not one. A count is not repaired by moving the
# copies somebody happens to find; it is repaired by making every copy
# answer to the same arithmetic.
_FORM_COUNT_SITES = (
    r"the form is one of the (\d+) in section 4\.5\.1",
    r"one of the (\d+) the note grammar enumerates",
    r"### 14\.8 The note grammar — (\d+) forms",
    r"The table holds (\d+) forms",
    r"sentences of the (\d+) closed forms",
)
_POSITION_COUNT_SITES = (
    r"holds \d+ forms and (\d+) argument positions",
    r"argument\. (\d+) argument positions:",
    r"closed forms: (\d+) argument positions",
)
# The four classes, wherever the contract breaks the positions down.
_BREAKDOWN = (
    (
        r"(\d+) are whole numbers, (\d+) are package words, (\d+) are "
        r"nested\s+forms, and (\d+) are bound affix strings"
    ),
    (
        r"(\d+) are whole numbers, (\d+) package words, (\d+) nested "
        r"forms and (\d+) bound affix strings"
    ),
    (
        r"(\d+) whole numbers, (\d+) package words, (\d+)\s+nested "
        r"forms, (\d+) bound affix strings"
    ),
)


def test_every_stated_count_of_the_grammar_is_the_same_count() -> None:
    """One grammar, counted once, wherever the contract states its size.

    ROUND 3 ITEM 2. Four sites moved when NF45-NF48 landed and two did
    not, so the document said 48 forms in one place and 44 in another,
    and a consumer written to the second would refuse three sentences
    the producer writes. The guard read arities and never read the
    totals, so it stayed green straight through the contradiction.

    WHAT IS COMPUTED AND WHAT IS ONLY CHECKED FOR CONSISTENCY. The form
    count, the position count, the package-word count and the count of
    bound affix positions all come from the code or from the clauses
    themselves, so no number lives in this file. The four-way class
    breakdown cannot be derived without a second table of argument
    classes, which would be one more copy of the thing this test
    refuses -- so it is checked for SUMMING to the position count and
    for agreeing wherever it is repeated. That is exactly the defect
    4.5.1 carried at HEAD, where it said 56 whole numbers in one
    sentence and 53 in the next.

    WHAT THIS DOES NOT CATCH, and why that is accepted rather than
    hidden (residual R-P4-45). Changing every breakdown CONSISTENTLY --
    66 whole and 4 words becoming 65 and 5 in all three places at once
    -- still sums to the position count, still agrees with itself, and
    still names five bound positions, so this check passes. Two things
    bound it. The realistic failure is a site left behind when the
    others move, which is what happened when NF45-NF48 landed and is
    what this catches. And since 2026-08-26 the contract is INSIDE the
    disposition seal, so a coordinated edit of three breakdown
    sentences changes three sealed passages and cannot land without a
    counted re-seal that a reviewer reads. The class split is guarded
    by the seal where it cannot be guarded by arithmetic.
    """
    defining = _defining()
    forms, positions = len(defining), sum(defining.values())
    words = len(taxonomy.NOTE_ARGUMENT_WORDS)
    bound = sum(len(p) for p in taxonomy._BOUND_AFFIX_PLACES.values())
    text = _contract()
    wrong: list[str] = []

    for pattern, expected, what in (
        *((p, forms, "forms") for p in _FORM_COUNT_SITES),
        *((p, positions, "positions") for p in _POSITION_COUNT_SITES),
        (r"\*\*The package-word vocabulary — (\d+)\*\*", words, "package words"),
    ):
        seen = re.findall(pattern, text)
        if not seen:
            wrong.append(f"no site matches {pattern!r}; a count was reworded")
        for stated in seen:
            if int(stated) != expected:
                wrong.append(f"{what}: {stated} stated, {expected} counted")

    # ROUND 4 ITEM 2: a sentence saying "the note grammar contains 47
    # forms" matched none of the patterns above, and every pattern
    # still matched somewhere, so the non-vacuity assertion passed over
    # it. Any number standing immediately before the word `forms`
    # anywhere in the document is now held to the count, whatever
    # sentence it sits in.
    for found in re.finditer(r"(\d+)\s+(?:closed\s+)?forms\b", text):
        if int(found.group(1)) != forms:
            wrong.append(
                f"forms: {found.group(1)} stated at {found.group(0)!r}, "
                f"{forms} counted"
            )

    breakdowns = [
        tuple(int(n) for n in found)
        for pattern in _BREAKDOWN
        for found in re.findall(pattern, text)
    ]
    assert breakdowns, "the contract no longer breaks the positions down"
    for whole, packaged, nested, affixes in breakdowns:
        if whole + packaged + nested + affixes != positions:
            wrong.append(
                f"a breakdown sums to {whole + packaged + nested + affixes}, "
                f"not the {positions} positions the clauses hold"
            )
        if affixes != bound:
            wrong.append(f"bound affix positions: {affixes} stated, {bound} in code")
    if len(set(breakdowns)) > 1:
        wrong.append(f"the breakdowns disagree with each other: {set(breakdowns)}")

    assert not wrong, (
        "the contract states the grammar's size more than once and the "
        "copies disagree:\n" + "\n".join(wrong)
    )
