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
are the arity mismatches R-P4-29 named, they are held below as
NAMED EXCEPTIONS, and every one of them is the same thing: **four
advisory remarks that amendment A-P4-30 withdrew from this phase's
scope, transcribed into the contract before the withdrawal.** They
close when those remarks are built, and the exception list is how this
guard says so out loud instead of being weakened to accommodate them.

THE GUARD RUNS IN BOTH DIRECTIONS, and the direction that was missing
is the one that mattered. A one-way check ("every contract form is in
the producer") is satisfied by a producer that emits forms nobody
wrote down, which is exactly the state four roles were in.
"""

import pathlib
import re

from synthtwin import parsing, taxonomy

CONTRACT = (
    pathlib.Path(__file__).resolve().parents[1]
    / "docs"
    / "spec"
    / "profile-contract-v6.md"
)

# THE FIVE THAT AMENDMENT A-P4-30 ACCOUNTS FOR, each with the arity the
# contract states, the arity the producer emits, and the landing that
# closes it. A form leaving this table must leave because it was
# RECONCILED, and a form joining it is a decision somebody records --
# which is why the reason is written per row rather than as a comment
# over the whole table.
KNOWN_MISMATCHES = {
    # The compact-date-versus-number remark states both counts in the
    # contract and neither in the producer. A-P4-30 item 1 withdrew the
    # widening; the counts are already computed where it fires.
    "remark_dates_also_read_as_numbers": (2, 0),
    # Arguments 8 and 9 -- the clock clause's count and the
    # recoverable-distribution advice's count -- are specified as "0
    # where no such clause is written" and the producer emits neither.
    "remark_no_reading_fits": (9, 7),
    # The code-shaped remarks gained an argument when A-P4-1 widened
    # them to fire on REPEATING code columns too, which A-P4-30 item 1
    # then withdrew. The producer still writes only the all-different
    # rendering, which needs no argument.
    "remark_every_number_is_different": (1, 0),
    "remark_every_value_is_different": (1, 0),
    # The label column publishing a built-in stand-in number as a
    # level. A-P4-30 item 1 withdrew it; the producer has no such form.
    "remark_a_label_is_a_built_in_stand_in": (1, None),
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
    )
    stated = re.search(r"\*\*The package-word vocabulary — (\d+)\*\*", _contract())
    assert stated is not None, "the contract no longer states the count"
    assert int(stated.group(1)) == len(words), (
        f"the contract states {stated.group(1)} package words and the "
        f"producer carries {len(words)}"
    )
    # The clock words are named, and named as NOT being format members:
    # a reader who took them for `format` values would write them into
    # a key the loader refuses.
    for word in taxonomy.NOTE_CLOCK_WORDS:
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
