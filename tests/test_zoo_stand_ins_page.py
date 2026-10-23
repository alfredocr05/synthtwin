"""The zoo-fix stand-ins page holds what it computes (plan P4-D422).

WHY A FILE OF ITS OWN. The zoo-fix stand-ins page in
`docs/plans/phase-4-columns.md` is written before the code of lanes
CODES-1, CODES-2, CODES-3 and GG: nothing in the product reads it yet.
The disposition seal turns red on any edit of a sealed passage and is
re-sealed by whoever makes the edit, so it cannot tell a correction from
its undoing. This file can, for the figures the page computes, for its
reading of the product it describes, and for the one sentence of each
rule that carries the rule.

WHAT IS COMPUTED HERE, NOT READ. Rule A3's debt of the measured row 44
from the published block the page quotes; rule A2's positional census on
cells shaped like the measured i2b2 ones, its vocabulary prefix kept in
rows and gone when the same cells are counted in ten people; A2's three
stages of stand-ins on the zoo's own tumour registry, 0 of 81 cells out of
the TNM grammar where every place falling to the alphabet put 7 out, and
on a form under the floor whose vocabulary marks stage (3) keeps; A2's
forced case, refused; path (ii)'s shape screen over a shape of each class
it can refuse, item by item against the page's own list, and over the
result words it must let through, with its named residual; path (iii)'s
hold of a label column with a figure in every present cell, and the ZIP
column half written ZIP+4 that this base describes with no question; the
golden fixture's `region` holding back `outlying`, its `note` naming
nothing and its few-valued numbers outside GG's class, so no golden
moves; a lone held-back level printing its own row count (the owner's B);
the code-look test the page's `code` offer reads; the categories ceiling
GG's class reads at 600 rows and `days_supply` inside the class; the mark
set today; the twelve zoo kinds whose `OWNERS` lines name the four lanes,
each in the page's table of the kinds the lanes turn; and the holding
questions of plan P4-D401 that rule U reads, from that decision's own
sentences.

WHAT IS NOT HERE. No lane's code exists, so nothing here says a twin
meets anything. The functions below are the page's rules written once as
the test reads them, not the product's: each lane builds its own and its
gate holds the cases.
"""
import collections
import contextlib
import csv
import inspect
import io
import itertools
import json
import pathlib
import random
import re

import pytest

from synthtwin import asking
from synthtwin import cli
from synthtwin import parsing
from synthtwin import taxonomy

import fixtures
import health_zoo

REPOSITORY = pathlib.Path(__file__).resolve().parents[1]
PLAN = REPOSITORY / "docs" / "plans" / "phase-4-columns.md"
PAGE_HEADING = "## The zoo-fix stand-ins page"
DECISION_HEADING = "## Decision P4-D422"
FLOOR = 11


def _page() -> str:
    text = PLAN.read_text(encoding="utf-8")
    start = text.index(PAGE_HEADING)
    stop = text.index(DECISION_HEADING, start)
    return text[start:stop]


def _flat(text: str) -> str:
    return " ".join(text.split())


def _form(text: str) -> str:
    """A value's form as the page writes it: figures `%`, letters `@`, every other character itself."""
    return "".join("%" if mark.isdigit() else "@" if mark.isalpha() else mark for mark in text)


def _profiled(folder: pathlib.Path, name: str, text: str) -> "dict":
    path = fixtures.write(folder, name, text)
    sink = io.StringIO()
    with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
        code = cli.main(["profile", f"{path}", "--replace"])
    assert code == 0, sink.getvalue()[-400:]
    stem = name.rsplit(".", 1)[0]
    return json.loads((folder / f"{stem}-profile.json").read_text(encoding="utf-8"))


def _column(document: "dict", name: str) -> "dict":
    return next(column for column in document["columns"] if column["name"] == name)


def test_the_page_stands_once_and_its_decision_follows_it() -> None:
    text = PLAN.read_text(encoding="utf-8")
    assert text.count(PAGE_HEADING) == 1
    assert text.count(DECISION_HEADING) == 1
    assert text.index(PAGE_HEADING) < text.index(DECISION_HEADING)
    page = _page()
    for section in range(12):
        assert f"### ZS.{section} " in page, section


OPERATIVE = {
    "U": "A column is UNANSWERED for this page where",
    "U-table": "also (c) where any question of the table offering `identifier` is open, on any column",
    "U-reach": "**And for every NAME (ZS.3), every RARE VALUE (ZS.4) and every positional census (A2)**, also (c)",
    "U-stand-ins": "no stand-in made of a character read from its held-back cells: its stand-ins read only what the "
    "description prints -- the form's own marks, the characters its published levels wear, ruling 1's published "
    "prefix -- and the alphabet (A2)",
    "A1": "is not published apart: its cells are counted in the column's commonest published form or layout, "
    "and the twin writes them there. The producer and the validator absorb alike",
    "A1-none": "has no destination, and A1 moves nothing on it: the `(withheld)` entry stays as today, with its total, "
    "and the twin writes its cells as today's held-pool writer does",
    "A1-clock": "On a column whose stand-ins G8.3's clock line reads as clock times (plans P4-D373 and P4-D393) nothing "
    "moves: the clock and stamp fills keep priority and their bytes.",
    "A1-people": "that fewer than the floor's cells wear -- fewer than the floor's different subjects beside a "
    "subject column -- is not published apart",
    "A2": "the description lists at each place the characters at least the floor's cells hold there -- at least "
    "the floor's different subjects beside a subject column (P4-D406) -- and publishes no count",
    "A2-after-no": "and it does so only once the column's Safe Harbor question is answered `no` and rule U clears (ZS.1)",
    "A2-unanswered": "Unanswered, it lists nothing and reads no held-back cell: its stand-ins read only what the "
    "description prints",
    "A2-empty-place": "A place whose list is empty where no published level wears the form takes the form's alphabet "
    "at that place from stage (1) on",
    "A2-balanced": "while a listed character at some place holds fewer than the floor's stand-in cells (the floor's "
    "different subjects beside a subject column), the next stand-in takes at each place the listed character with the "
    "fewest stand-in cells so far",
    "A2-validate": "every listed character at each place held by at least the floor's cells of that form outside the "
    "published levels -- the floor's different subjects beside a subject column -- in the real file and the twin alike",
    "A2-H-rows": "H is read in rows beside a subject column too, the stricter reading.",
    "A2-W1": "A2 adds no own-fact group to RULE W1's list.",
    "A2-forced": "neither does a form with a place whose list is empty while its held-back cells H exceed (a-1)(f-1)",
    "A2-stages": "(1) each place's list, a place with an empty list taking the characters the form's published levels "
    "wear there; (2) each place's list together with the characters the form's published levels wear there; (3) the "
    "places widened to the form's alphabet one at a time from the last",
    "A2-label": "A2 fills the LABEL class only: a held-back level G8.3a owes the number class is written by A3 alone.",
    "A2-codes": "A zoo `codes` check (every twin value one the real writes) is met only by names (CODES-2) or by A2 "
    "reproducing every held-back level (TNM, GCS), never by a made-up stand-in.",
    "A2-floor": "An unlisted character's count lies in 0 to f-1, a bound that contains 0 -- nothing published forces "
    "any one character to appear",
    "A3": "the pool's level SIZES (G8.3c; not published) are drawn after the class and form debts, so every "
    "published form's debt inside the number class is a sum of whole levels",
    "A3-widths": "each number stand-in is written at its form's integer and fraction widths (`%%%.%`: three and one), "
    "inside the published range, off every published level",
    "C1": "A HELD column's twin meets every layout and form census its held block publishes, exactly, from "
    "made-up values",
    "C2": "each placeholder is written in its own spelling and each constant figure after the point as the source's",
    "C3": "that question carries the kind answers in its own entry",
    "CODES-3-root": "the figures-and-points root every cell shares is kept",
    "CODES-3-scope": "`parsing.is_a_literal_prefix` no longer asks for a letter only on a column whose every cell has "
    "the UID shape (a first arc of `0`, `1` or `2` and two points or more)",
    "yes-no-root": "A column held by the Safe Harbor question's `yes` keeps ruling 1's prefix only where it holds a "
    "letter, as today: no figure root is kept on it",
    "path-i": "So on path (i) the question is put whatever the column's levels, and until it is answered `no` the "
    "column is held as P4-D401 holds a column (its common ZIPs included)",
    "path-ii": "(1) at most two words; (2) no run of five figures or more, and at most six figures in the word",
    "path-iii": "Any other label column (`categorical`, or `long_tail_labels` answered `code`) answered `no` to "
    "the Safe Harbor question",
    "path-iii-every": "The question is put to EVERY label column (`categorical` or `long_tail_labels`, whatever its "
    "levels, answered `code` or not), in the first round, in ONE entry of the questions file",
    "path-iii-hold": "Unanswered, a label column every present cell of which holds a figure -- a ZIP, a ZIP+4, a "
    "postcode, a record, account or device number, a code -- is held as path (i) holds a column (P4-D401's held "
    "block), whatever its levels",
    "acted-on": "**`yes` is acted on at once**: it only withholds, so no other open question can delay it; `no`, which "
    "widens what is published, is acted on only once rule U (c) clears",
    "blank": "on path (i) and on a label column with a figure in every present cell, the column held (above); on any "
    "other label column, its word levels only, every level holding a figure pooled, no name",
    "path-iii-levels": "and on every other label column the hold is read LEVEL BY LEVEL: no level that holds a figure is "
    "published while the question is open -- it is pooled with the held-back levels",
    "majority-not": "A majority reading (held where half the present cells or more hold a figure) is NOT adopted: "
    "enough filler words still defeat it.",
    "names-joint": "The twin allocates the held-back sizes jointly, before any split",
    "names-reserve": "together with a reservation of at least one cell for each unnamed level",
    "names-validate": "each published form's count met with the named and unnamed levels' cells inside it",
    "top-code": "while that question is open every value above 89 is read as 90 for the whole description",
    "top-code-asked": "it is put the Safe Harbor question whatever its count of values",
    "top-code-reach": "its word cells and its PLACEHOLDERS set aside whatever their share -- an all-nines value of "
    "either sign (`999` and `9999` beside `-9`, `-99` and `-999`), a minus sign with one figure (`-1`), and ANY single "
    "value outside 0 to 125 that at least the floor's rows repeat (`888`, `-1` or `130` on 11 rows or more) -- AT LEAST "
    "TWO THIRDS of its remaining numbers lie within 0 to 125 and one of them is above 89",
    "top-code-placeholder-written": "and each placeholder set aside as the source wrote it (a code, not an age)",
    "top-code-gate3": "lane SH's gate cases (its LANE SH ADDENDUM 2, case (1)), and CODES-2's, `K-S3-64`'s held shape "
    "`agesbulk`",
    "top-code-limit": "Only an age column more than a third of whose numbers lie outside 0 to 125 on values that fewer "
    "than the floor's rows each hold -- the values outside 0 to 125 that the floor's rows repeat, the all-nines values "
    "and `-1` being set aside as placeholders, whatever their share -- is not reached",
    "top-code-months": "and an age counted in months or days is not protected: its values above 125 are set aside as "
    "placeholders where the floor's rows repeat them, and keep it out of reach where they are spread thin",
    "top-code-pounds": "or a weight in pounds whose values above 125 each hold the floor's rows, is top-coded too",
    "top-code-floor": "save a placeholder set aside -- an all-nines value, or a value above 125 that at least the floor's "
    "rows repeat -- a code written as the source wrote it",
    "top-code-bulk": "the reach is decided on the bulk of the values, never on all of them, so neither one outlier "
    "(`130`) nor a placeholder share past one present cell in three switches it off",
    "top-code-roles": "EVERY ROLE THAT PRINTS A VALUE is in its reach: `binary`, `constant`, `count` and `continuous`, "
    "and the number part of `numbers_with_labels` and of `affixed_number` (`95 years` read 95)",
    "top-code-other-question": "and whatever other question it is put, in the same round -- an answer to another "
    "question (the person question's `keep`, `code` or `measurement`) never answers this one",
    "top-code-outlier-read": "every value above 89 is read as 90 for the whole description, an outlier above 125 that "
    "fewer than the floor's rows hold included",
    "top-code-levels": "every level of a `binary` or `constant` column above 89 is printed as 90",
    "label-ages": "AGES IN LABEL ROLES ARE IN ITS REACH NOW, built by lane SH, not left to CODES-2 (the orchestrator's "
    "LANE SH ADDENDUM 2, case (2))",
    "label-ages-reach": "a `categorical` or `long_tail_labels` column whose levels -- placeholders set aside whatever their "
    "share (the number placeholders above, and any single word that at least the floor's rows repeat, such as `UNK`), "
    "and other words on at most one present cell in three -- are whole or decimal numbers with an optional unit word "
    "(`95`, `95 years`), at least two thirds of them within 0 to 125 and one above 89, is put the same Safe Harbor question",
    "label-ages-pool": "while it is open every level above 89 is pooled into one level written as 90 in the source's own "
    "form (`90 years`), printed, as every level is, only at the floor's rows or more; the twin writes no level above 89 "
    "but that one",
    "label-ages-codes-2": "CODES-2's path (iii) later holds such a column wider -- whole where every present cell holds a "
    "figure, level by level beside words (ZS.3) -- which publishes less, under the same question, never a second one",
    "label-ages-gate": "lane SH's gate cases (its LANE SH ADDENDUM 2, case (2)), and CODES-2's, `K-S3-64`'s held shape "
    "`ageslabel`",
    "label-ages-blank": "and on a label column of ages its levels above 89 pooled into one written as 90 until path (iii) "
    "holds it wider (ZS.1)",
    "label-ages-validate": "on a label column of ages, no level above 89 but the pooled 90",
    "label-ages-live": "beside a placeholder share (`-1` or `888` x 7,000: 95 printed; 8,000 `-1` beside 12,000 ages: 90 to "
    "104 printed) and in label roles (ages written `NN years`: the levels `90 years` to `104 years`; `95` beside `UNK` x "
    "7,000)",
    "label-ages-point-9": "its reach in label roles (ages written `NN years`, `95` beside `UNK`: the LANE SH ADDENDUM 2)",
    "label-ages-kpi": "`ageslabel`: the levels `90 years` to `104 years`, and `95` beside `UNK` x 7,000",
    "top-code-gate2": "lane SH's gate cases (1) and (2), and CODES-2's, `K-S3-64`'s held shapes `agesrole` and `agesbulk`",
    "top-code-ages999": "the `ages999` shapes (`999` once and twenty times) are reached and print 0 ages over 89 "
    "(CODES-2's gate cases and `K-S3-64`'s held shapes `ages999`)",
    "top-code-live": "TODAY'S product prints ages over 89 for ANY age column, a live exposure",
    "top-code-sh": "Lane SH (P4-D427, launched 2026-10-23, the orchestrator's LANE SH NOTE) builds this top-code in the "
    "product now; CODES-2 extends the same Safe Harbor question to the columns this page names later, never a second "
    "question.",
    "five-figure": "A column of a role the top-code reaches (`binary`, `constant`, `count`, `continuous`, and the "
    "number part of `numbers_with_labels` and of `affixed_number`) whose whole numbers, read as the source wrote them, "
    "are AT LEAST TWO THIRDS of four or five figures and one at least of five",
    "five-figure-zeros": "and a ZIP whose leading zero was lost read in its five-figure reading (`2100` beside `52240`: "
    "mixed widths are in reach, Codex's second outside round, item 4)",
    "five-figure-aside": "a lone `0` and a minus sign with one figure set aside whatever their share, may hold ZIP codes",
    "five-figure-gate2": "lane SH's gate cases (1) and (3), and CODES-2's, `K-S3-64`'s held shapes `ziprole` and "
    "`zipwidth`",
    "five-figure-four": "A column whose ZIPs ALL lost their zero (four figures alone, `2100` to `2583`) is held today by "
    "P4-D401's fixed-width question",
    "sh-agree": "So the page and SH agree once SH's addenda land; SH's verify reads its code against these "
    "paragraphs, and a difference is settled there, never by a second question.",
    "sh-head": "Read read-only at SH's head 0e3a65d4 (2026-10-23 07:53), SH's code already takes this page's words",
    "sh-addendum-2": "Its LANE SH ADDENDUM 2 (2026-10-23 08:44) adds the third verify's five shapes to that gate at 0 "
    "ages over 89 in any file",
    "sh-family": "its answers `no` and `yes` sit in their own AQ family `safe-harbor`",
    "sh-reach-still": "Its reach there is still repair 3's -- `taxonomy.TOP_CODE_ROLES` (`count`, `continuous`, "
    "`numbers_with_labels`)",
    "sh-goldens": "at 0e3a65d4 it is the `profile` command's rule, as P4-D401's hold is applied -- "
    "`profile.build_document` top-codes only where it is told to (its `top_code`, which `synthtwin profile` passes) -- so "
    "the goldens, built through `profile.build_document`, keep their bytes",
    "goldens-zs7": "The top-code reaches the fixtures' `amount` (0.5 to 99.5), but it is the `profile` command's rule "
    "(SH's 0e3a65d4: `profile.build_document` top-codes only where it is told to), and the goldens are built through "
    "`profile.build_document`, so they keep their bytes",
    "five-figure-other-question": "it is put the Safe Harbor question (ZS.3's first-round entry), whatever other question "
    "it is put, and the column is held whole until `no`",
    "five-figure-one-word": "One word cell cannot lift it (the orchestrator's rulings for HX4 of 2026-10-22 18:23 and "
    "21:32",
    "five-figure-blank": "on a number column the five-figure hold reaches, the column held (ZS.1)",
    "five-figure-floor": "**The five-figure hold** publishes less: the column takes P4-D401's held block until `no`",
    "when-put-all": "every column path (ii) reaches with a held-back word holding a figure, and every column the "
    "top-code or the five-figure hold reaches in the one entry that lists them",
    "five-figure-held": "and the column is held whole until `no` -- P4-D401's held block",
    "five-figure-nwl": "On the number part of `numbers_with_labels` the labels half is the words set aside, whatever "
    "its share",
    "five-figure-gate": "the `zip5word` shapes (`UNKNOWN` once, `HOMELESS` three times, with and without a leading "
    "zero) are CODES-2's gate cases at 0 ZIPs printed and `K-S3-64`'s held shapes `zip5word`",
    "five-figure-live": "TODAY'S product prints 9 real ZIPs on each of the four shapes",
    "five-figure-sh": "Lane SH (P4-D427) builds this hold in the product now, beside the top-code",
    "row-45": "Row 45 is CLOSED by lane HX only where every present cell is a key, a ZIP or a UDI",
    "screen-record": "A WORD HOLDING A FIGURE IS NAMED ONLY AFTER `no` (Codex's second outside round, item 2, "
    "superseding repair 3's named residual)",
    "screen-record-asked": "it is put, in the first round's one entry, to every column with a held-back word that holds "
    "a figure and passes the screen, and while it is open no such word is named",
    "screen-record-blank": "on a column path (ii) reaches, no held-back word holding a figure named",
    "screen-record-when": "every column path (ii) reaches with a held-back word holding a figure",
    "screen-letters": "Words of letters and marks alone (`TNP`, `HI`, `N/A`, `Not done`) are named by the screen",
    "screen-hash-not": "refusing `#` before figures is NOT adopted",
    "top-code-validate": "no twin cell above 90 save a placeholder set aside; the real file, read with every value above "
    "89 as 90, meets the description",
    "top-code-answers": "`no` lifts it (today's description, GG where its class holds); `yes` holds the column "
    "(P4-D401's held block)",
    "top-code-twin": "the twin writes the column so read, never a value above 90",
    "GG-a-waits": "**GG (a) waits for `no`**, though every value it would add clears the floor",
    "no-figure-run": "a constant run of figures is kept on no `yes` column, bracketed or not",
    "NP-ratio": "one value a subject, at most one repeated row in ten differing",
    "yes": "no value of this column is published, and the twin writes made-up values in its layouts",
    "no": "never the rows that hold them; where only one value is named, how many rows hold it can be read",
    "code-offer": "offer HX3's `code`, in HX3's words and with its declaration, between `keep` and `identifier`",
    "NP": "a held-back name is published only where its column is NOT ATTACHED to that subject",
    "NP-attached": "A name in an ATTACHED column (an ancestry or a birth city beside each patient's rows) is a value "
    "one to ten subjects hold whatever its rows and is not published",
    "GG": "the twin's present cells take exactly those values -- never a value inside a published empty gap",
    "GG-99": "never a value inside a published empty gap, never `-99` re-spelled `-99.0`, never a level dropped",
    "GG-blanks": "its blank cells keeping the column's published missing share, as today",
    "GG-validate": "every present twin cell a listed value; every listed value present; the blank cells within the "
    "column's published missing window",
    "GG-scale-limit": "Likewise a scale with a missing code left unanswered loses a level and writes values in the "
    "published gap",
    "GG-class": "whose values are NOT every whole number from the least to the greatest each held by at least the "
    "floor's rows",
    "GG-no": "**GG acts only after `no` to the Safe Harbor question**",
    "GG-b": "`few_values` lists every value, the rare ones included, without counts, and the twin's present cells "
    "take exactly those values",
    "GG-unanswered": "**Unanswered**, a column of the class keeps today's description and twin byte for byte",
    "GG-yes": "**`yes`** holds the column's ladder, mode and tail values (P4-D401's held block)",
    "GG-NP": "Beside a subject column, rule NP applies to the rare values as to names.",
    "GG-W1": "Every value the block prints -- in `few_values`, the ladder, the mode or a tail -- that the floored "
    "histogram does not count at f or more is an own-fact group for RULE W1",
    "W1": "contract 4.6b's RULE W1 reads every named level as an OWN-FACT GROUP",
    "W1-pooled": ", and the pooled total printed below f as one too",
    "validate-names": "where every held-back level is named, no cell outside the published and named levels",
    "vectors-4": "`pooled_level_sizes` (`-4`) moves on purpose under B",
    "vectors-27": "the clock cases (`clock_stand_ins_past_route_one`, `-27`) must not move",
    "goldens": "So the profile golden (`tests/test_profile_document.py`, `GOLDEN_SHA256`) and the digests of "
    "`tests/test_twin_golden.py` (`GOLDEN_DESCRIPTION_SHA256`, `GOLDEN_REPORT_SHA256`, `GOLDEN_TWIN_SHA256`) do not move",
    "tests-move": "the 20 lines in 13 test files that count the questions asked (`len(asked)`) and the 18 test files "
    "that declare `--code`",
    "words-limit": "A column of WORDS of a Safe Harbor class -- a city, a name -- whose Safe Harbor question is "
    "unanswered publishes its common word levels as today, and only its word levels, every level holding a figure pooled",
    "zoo-yes": "`yes` for `zip5` and `zip4`, the two path (i) columns of places, for `immunizations.udi`, a device number",
    "udi-reread": "\"a UDI column answered `yes` writes no real UDI, in its published layouts\"",
    "loinc": "`labs`' `codes loinc` (today under CODES-1's `loinc` line) moves likewise",
    "unowned": "So `diagnoses`' checks `levels icd10_dotted`, `levels icd10_plain`, `codes icd10_dotted` and "
    "`codes icd10_plain` have no owner that can turn them",
    "hx3": "Lane HX3 (P4-D420, READY, not on this base; CODES-2 stacks on it)",
    "i2b2-people": "counted in `patient_num`'s people, 13 levels on 90 cells are held back and three forms publish a "
    "census (adding the procedure codes' prefix and `NDC:00`); either way 0 stand-in cells fall outside the six vocabularies",
    "icd10-111": "`diagnoses.icd10_dotted` 3 forms and 111 `ICD-10-CM with the dot` cells",
    "see-note": "`mixed_results.result_value` 6 (moot once CODES-2 names `SEE NOTE`)",
    "gg-kpi-no": "values off the real list on the few-valued cases, stamped with `no` answered",
    "PS": "this page writes no date or time stand-in and names that rule wherever one is meant",
    "table-floor": "every rule here holds at every size, the Safe Harbor question, the top-code and rule U being "
    "identifier rules the floor never excuses",
}


@pytest.mark.parametrize("rule", sorted(OPERATIVE))
def test_each_rule_keeps_its_operative_sentence(rule: str) -> None:
    assert _flat(OPERATIVE[rule]) in _flat(_page()), rule


def _stand_ins(
    cells: "list[str]", census_of: "dict[str, list[str]]", widen: bool, balanced: bool = True,
) -> "list[str]":
    """Rule A2's stand-ins, one a held-back level, commonest first.

    widen=True is the page as repaired: (1) each place's list, an empty list taking the characters the
    form's published levels wear there, or the form's alphabet where no published level wears the form;
    (2) each list with those characters; (3) the places widened to the form's alphabet one at a time from
    the last. balanced=True walks stage (1) in balanced order while a listed character holds fewer than
    the floor's stand-in cells: at each place the listed character with the fewest cells so far, the
    stage's order where that combination is taken. widen=False is the page as first written: the lists,
    an empty list taking the alphabet, then the alphabet at every place. An empty `census_of` is A2
    unanswered: nothing listed, nothing read from the held-back cells.
    """
    tally = collections.Counter(cells)
    published = {value for value, n in tally.items() if n >= FLOOR}
    held = sorted((value for value in tally if value not in published), key=lambda value: (-tally[value], value))

    def alphabet(form: str, place: int) -> "list[str]":
        return list("0123456789") if form[place] == "%" else (
            list("ABCDEFGHIJKLMNOPQRSTUVWXYZ") if form[place] == "@" else [form[place]])

    used = set(published)
    iterators: "dict[tuple[str, str], object]" = {}
    support: "dict[tuple[str, int], collections.Counter[str]]" = collections.defaultdict(collections.Counter)
    written = []
    for value in held:
        form = _form(value)
        lists = census_of.get(form) or ["" for _ in form]
        worn = ["".join(sorted({level[place] for level in published if _form(level) == form})) for place in range(len(form))]
        if widen:
            first = [list(lists[place] or worn[place]) or alphabet(form, place) for place in range(len(form))]
            second = [sorted(set(first[place]) | set(worn[place])) for place in range(len(form))]
            stages = [("1", first), ("2", second)] + [
                (f"3-{k}", second[:k] + [alphabet(form, place) for place in range(k, len(form))])
                for k in range(len(form) - 1, -1, -1)
            ]
        else:
            stages = [("1", [list(lists[place]) or alphabet(form, place) for place in range(len(form))]),
                      ("a", [alphabet(form, place) for place in range(len(form))])]
        found = ""
        short = any(support[(form, place)][mark] < FLOOR for place in range(len(form)) for mark in lists[place])
        if widen and balanced and short:
            pick = "".join(
                min(first[place], key=lambda mark: (support[(form, place)][mark], first[place].index(mark)))
                for place in range(len(form))
            )
            found = "" if pick in used else pick
        for name, choices in stages if not found else []:
            walk = iterators.setdefault((form, name), itertools.product(*choices))
            for combination in walk:  # type: ignore[attr-defined]
                if "".join(combination) not in used:
                    found = "".join(combination)
                    break
            if found:
                break
        used |= {found}
        written += [found] * tally[value]
        for place, mark in enumerate(found):
            support[(form, place)][mark] += tally[value]
    return written


def test_a2_stages_keep_the_tumour_registrys_grammar_where_the_alphabet_broke_it(tmp_path: pathlib.Path) -> None:
    place = [table.name for table in health_zoo.TABLES].index("tumor_registry")
    source = health_zoo.write_table(health_zoo.TABLES[place], tmp_path, 600, 20261016 + place)
    rows = list(csv.DictReader(io.StringIO(source.read_text(encoding="utf-8-sig"))))
    cells = [row["tnm"] for row in rows if row["tnm"]]
    tally = collections.Counter(cells)
    held = [(value, "") for value in cells if tally[value] < FLOOR]
    assert (len({value for value, _ in held}), len(held)) == (11, 81)
    census = {form: places for form, places in _census(held, FLOOR, in_people=False).items()}
    assert census == {"@%@%@%": ["T", "234", "N", "0123", "M", "1"]}
    grammar = re.compile(r"T[0-4]N[0-3]M[01]")
    real_held = {value for value, _ in held}
    first = _stand_ins(cells, census, widen=False)
    repaired = _stand_ins(cells, census, widen=True)
    assert (sum(not grammar.fullmatch(cell) for cell in first), len(set(first) & real_held)) == (7, 9)
    assert (sum(not grammar.fullmatch(cell) for cell in repaired), len(set(repaired) & real_held)) == (0, 11)
    page = _flat(_page())
    assert "0 of 81 cells outside `T[0-4]N[0-3]M[01]` and 11 of 11 stand-ins real levels" in page
    assert "7 of 81 cells outside and 9 of 11 real" in page


def test_a2_stage_three_keeps_the_vocabulary_marks_of_a_form_under_the_floor() -> None:
    cells = ["DEM|LANG:F"] * 30 + ["DEM|LANG:M"] * 30 + ["DEM|LANG:U"] * 5 + ["DEM|LANG:X"] * 3
    assert _stand_ins(cells, {}, widen=True)[-8:] == ["DEM|LANG:A"] * 5 + ["DEM|LANG:B"] * 3
    assert _stand_ins(cells, {}, widen=False)[-8:] == ["AAA|AAAA:A"] * 5 + ["AAA|AAAA:B"] * 3
    assert "the demographic form `@@@|@@@:@` is written with its published `DEM|` prefix and a drawn last letter" in _flat(_page())


def test_a2_refuses_the_forced_case_where_an_empty_place_bounds_every_character() -> None:
    """95 held-back cells of one figure place, each digit on at most 10: every digit is forced into 5..10."""
    held, alphabet_size, floor = 95, 10, FLOOR
    spread = [10, 10, 10, 10, 10, 10, 10, 10, 10, 5]
    assert sum(spread) == held and max(spread) <= floor - 1
    least = held - (alphabet_size - 1) * (floor - 1)
    assert least == 5 and least >= 1
    for spread_case in ([10] * 9 + [5], [5] + [10] * 9):
        for count in spread_case:
            assert least <= count <= floor - 1
    assert held > (alphabet_size - 1) * (floor - 1)
    assert 90 == (alphabet_size - 1) * (floor - 1)  # at H = 90 one digit may hold none: no bound inside 1..f-1
    assert "`K-S6-08` gains H = 95 on figures, a = 10: every digit forced into 5..10" in _flat(_page())


def _held_while_unanswered(cells: "list[str]") -> bool:
    """Path (iii)'s hold: a label column every present cell of which holds a figure."""
    present = [cell for cell in cells if cell.strip()]
    return bool(present) and all(any(mark.isdigit() for mark in cell) for cell in present)


def test_path_iii_holds_figure_columns_and_leaves_words_as_the_stated_limit() -> None:
    assert _held_while_unanswered(["02139", "02139-1234", "10027"])
    assert _held_while_unanswered(["K1A 0B1", "M5V 2T6"])  # letters too: the figures-and-marks reading misses it
    assert _held_while_unanswered(["E11.9", "I10", "T2N0M1"])
    assert not _held_while_unanswered(["Boston", "São Paulo", "Hà Nội"])
    assert not _held_while_unanswered(["DEM|LANG:F", "ICD10CM:E11.9"])
    page = _flat(_page())
    assert "measured, the zoo's `patients.birth_city`, 7 cities on 600 of 600 rows" in page
    assert "holding only columns of figures and marks alone leaves the postcode column's 5 of 40 printed" in page


def test_a_zip_column_half_written_zip_plus_four_is_asked_nothing_on_this_base(tmp_path: pathlib.Path) -> None:
    """The first review's case: today no question reaches it and real five-figure ZIPs print with their counts."""
    draw = random.Random(11)
    zips = [f"0{2100 + 7 * k:04d}" for k in range(70)]
    weights = [1.0 / (k + 1) ** 1.1 for k in range(70)]
    lines = ["pid,zip"]
    for k in range(600):
        code = draw.choices(zips, weights)[0]
        lines += [f"P{k:06d},{code}-{draw.randint(1000, 9999)}" if k % 2 else f"P{k:06d},{code}"]
    document = _profiled(tmp_path, "zipmix.csv", "\n".join(lines) + "\n")
    zip_column = _column(document, "zip")
    assert zip_column["role"] in ("categorical", "long_tail_labels")
    printed = [level["label"] for level in zip_column.get("levels") or []]
    assert printed and all(re.fullmatch(r"\d{5}", label) for label in printed)
    asked = json.loads((tmp_path / "zipmix-questions.json").read_text(encoding="utf-8"))["asked"]
    assert not [entry for entry in asked if entry.get("column") == "zip"]
    assert _held_while_unanswered([line.split(",")[1] for line in lines[1:]])
    assert "0 of 363 and 0 of 40 real values printed" in _flat(_page())


def _consecutive_and_floored(values: "list[str]") -> bool:
    """Outside GG's class: every whole number from the least to the greatest, each on the floor's rows."""
    tally = collections.Counter(values)
    numbers = sorted({float(value) for value in tally})
    if any(number != int(number) for number in numbers):
        return False
    whole = [int(number) for number in numbers]
    return whole == list(range(whole[0], whole[-1] + 1)) and min(tally.values()) >= FLOOR


@pytest.mark.parametrize("fixture", ["every_role_table", "every_role_and_joined_table"])
def test_the_golden_fixtures_few_valued_numbers_stand_outside_ggs_class(fixture: str, tmp_path: pathlib.Path) -> None:
    text = getattr(fixtures, fixture)()
    document = _profiled(tmp_path, f"{fixture}.csv", text)
    rows = list(csv.DictReader(io.StringIO(text)))
    ceiling = taxonomy.categories_ceiling(len(rows), taxonomy.Settings())
    few = [
        column["name"] for column in document["columns"]
        if column["role"] in ("count", "continuous") and (column.get("n_distinct") or 0) <= ceiling
    ]
    assert few == ["visits"]
    visits = [row["visits"] for row in rows if row["visits"]]
    assert sorted({int(value) for value in visits}) == list(range(10))
    assert _consecutive_and_floored(visits)
    assert "`visits` (a `count` column of the ten values 0 to 9, each on 15 to 28 rows) is outside GG's class" in _flat(_page())
    assert min(collections.Counter(visits).values()) >= 15 and max(collections.Counter(visits).values()) <= 28


def test_days_supply_is_inside_ggs_class() -> None:
    days_supply = {"5": 5, "7": 25, "10": 6, "14": 14, "21": 8, "28": 11, "30": 349, "84": 8, "90": 174}
    cells = [value for value, n in days_supply.items() for _ in range(n)]
    assert not _consecutive_and_floored(cells)
    assert _consecutive_and_floored([str(k % 4) for k in range(600)])


def test_the_kinds_table_holds_the_twelve_kinds_once_each() -> None:
    page = _page()
    table = page[page.index("**The kinds each lane turns, at 600 rows**"):page.index("### ZS.9")]
    named = re.findall(r"^\| ([^|]+) \|", table, flags=re.MULTILINE)
    kinds = [kind.strip("` ") for cell in named for kind in cell.split(",") if kind.strip("` ") not in ("kind", "---")]
    assert sorted(kinds) == sorted(TWELVE)
    assert "Best case 22 of 40 kinds; 18 without rule NP; 21 if the `udi` check is not re-read." in _flat(page)


def test_pcornet_dx_held_back_cells_are_the_label_level_and_seven_number_levels() -> None:
    number_levels = {"272.4": 4, "585.3": 3, "486": 8, "311": 4, "38341003": 5, "233604007": 4, "431855005": 1}
    assert (len(number_levels), sum(number_levels.values())) == (7, 29)
    assert 10 + sum(number_levels.values()) == 39
    assert len({_form(value) for value in number_levels} | {_form("R07.9")}) == 5
    assert "holds back 39 cells in five shapes" in _flat(_page())


def test_the_safe_harbor_question_is_the_owners_sentence() -> None:
    owners = (
        "Could a value of this column name a person, a place smaller than a state, a birth date, "
        "or a record, account or device number?"
    )
    page = _flat(_page())
    assert owners in page
    assert "> Could a value of '<column>' name a person, a place smaller than a state, a birth date, or a record, account or device number?" in _page()
    assert "45 CFR 164.514(b)(2)(i)" in page


SAFE_HARBOR_CLASSES = (
    "a person is a patient or a patient's relative, employer or household member, by name, initials or any mark",
    "a place smaller than a state is a street address, city, county, precinct, or a ZIP code, or its first three "
    "figures where that area holds 20,000 people or fewer",
    "a birth date includes any date of a person other than its year, and an age over 89 years, or any date that "
    "shows one",
    "the numbers include medical record, health-plan, account, certificate or licence, vehicle, device and serial "
    "numbers, telephone, fax and social security numbers, e-mail, web and internet addresses, and any other number "
    "or code given to one person",
)


@pytest.mark.parametrize("covered", SAFE_HARBOR_CLASSES)
def test_the_safe_harbor_explanation_names_each_class_the_page_relies_on(covered: str) -> None:
    """The question's `what_synthtwin_saw` covers 45 CFR 164.514(b)(2)(i)'s (B), (C) and (R) as GG and path (iii) read them."""
    assert _flat(covered) in _flat(_page())


def test_the_page_cites_no_method_section_this_base_lacks() -> None:
    text = PLAN.read_text(encoding="utf-8")
    start = text.index(PAGE_HEADING)
    assert "G7.13" not in text[start:]
    assert "(the G1 floor, contract NF128 and NF129, plan P4-D417)" in _flat(text[start:])


def test_a3_settles_row_44_where_today_overpays_its_published_form() -> None:
    published_forms = {"%%%.%": 21, "%%%.%%": 27, "@%%": 87, "@%%.%": 414, "@%%.%%": 11}
    number_levels = {"401.9": 14, "250.00": 27, "44054006": 12}
    n_numeric = 82
    owed = n_numeric - sum(number_levels.values())
    form_debt = published_forms["%%%.%"] - sum(n for v, n in number_levels.items() if _form(v) == "%%%.%")
    assert (owed, form_debt) == (29, 7)
    today = {"250.1": 10, "251": 9, "44054005": 6, "252": 4}
    assert sum(today.values()) == owed
    written = sum(n for v, n in today.items() if _form(v) == "%%%.%")
    assert number_levels["401.9"] + written == 24
    # A3: the sizes are drawn after the debt -- here 4 and 3, as the source held them,
    # each at most f - 1 -- so the published form reads its own count again.
    sizes = [4, 3]
    assert sum(sizes) == form_debt and all(1 <= size <= FLOOR - 1 for size in sizes)
    assert number_levels["401.9"] + sum(sizes) == published_forms["%%%.%"]
    page = _flat(_page())
    assert "so the held-back numbers owe 29 cells, 7 of them in `%%%.%`" in page
    assert "`%%%.%` reads 24 against 21 and validate exits 3" in page


def _census(cells: "list[tuple[str, str]]", floor: int, in_people: bool) -> "dict[str, list[str]]":
    """Rule A2 as the page writes it: per form, the characters the floor's cells (or people) hold at each place."""
    by_form: "dict[str, list[tuple[str, str]]]" = collections.defaultdict(list)
    for value, subject in cells:
        by_form[_form(value)] += [(value, subject)]
    lists: "dict[str, list[str]]" = {}
    for form, held in by_form.items():
        if len(held) < floor:
            continue
        places = []
        for place in range(len(form)):
            rows = collections.Counter(value[place] for value, _ in held)
            people: "dict[str, set[str]]" = collections.defaultdict(set)
            for value, subject in held:
                people[value[place]] |= {subject}
            places += ["".join(sorted(
                mark for mark, n in rows.items()
                if n >= floor and (not in_people or len(people[mark]) >= floor)
            ))]
        lists[form] = places
    return lists


def _prefix(places: "list[str]") -> str:
    prefix = ""
    for listed in places:
        if len(listed) != 1:
            break
        prefix += listed
    return prefix


def test_a2_keeps_the_vocabulary_prefix_in_rows_and_counts_it_in_people() -> None:
    letters = "ABCDEFGHJKLM"
    values = [f"ICD10CM:{letters[k % 12]}{k % 10}{(k * 7) % 10}.9" for k in range(36)]
    apart = [(value, f"P{k}") for k, value in enumerate(values)]
    lists = _census(apart, FLOOR, in_people=True)
    places = lists["@@@%%@@:@%%.%"]
    assert _prefix(places) == "ICD10CM:"
    assert places[-2:] == [".", "9"]
    assert places[8] == ""  # no letter of the code on the floor's cells: the form's own alphabet
    ten = [(value, f"P{k % 10}") for k, value in enumerate(values)]
    assert _prefix(_census(ten, FLOOR, in_people=True)["@@@%%@@:@%%.%"]) == ""
    assert _prefix(_census(ten, FLOOR, in_people=False)["@@@%%@@:@%%.%"]) == "ICD10CM:"
    few = [(f"ICD10CM:Z{k}.1", f"Q{k}") for k in range(FLOOR - 1)]
    assert "@@@%%@@:@%.%" not in _census(few, FLOOR, in_people=False)
    assert "listing `ICD10CM:` at its first eight places and `.9` at its last two" in _flat(_page())


SCREEN = {
    "(1) at most two words": lambda word: len(word.split()) > 2,
    "(2) no run of five figures or more, and at most six figures in the word": lambda word: bool(
        re.search(r"\d{5}", word)) or sum(mark.isdigit() for mark in word) > 6,
    "(3) no `@`, no `://`, no `www.`": lambda word: "@" in word or "://" in word or "www." in word,
    "(4) no date shape": lambda word: bool(re.search(r"\d{1,4}[/.-]\d{1,2}[/.-]\d{1,4}", word)),
    "and no clock shape (a two-figure hour 00 to 23, a colon and minutes 00 to 59, with or without seconds or a "
    "marker; a titer, `1:` and figures, is not one)": lambda word: bool(re.search(r"(?<!\d)(?:[01]\d|2[0-3]):[0-5]\d", word)),
    "(5) no dotted quad": lambda word: bool(re.search(r"\d{1,3}(?:\.\d{1,3}){3}", word)),
    "(6) no word holding both a letter and a figure": lambda word: any(mark.isalpha() for mark in word) and any(
        mark.isdigit() for mark in word),
    "(7) no single letter followed by a point": lambda word: bool(re.search(r"(?<![A-Za-z])[A-Za-z]\.", word)),
}
"""Path (ii)'s shape screen, one refusal a clause of the page's own list, the clause as the page writes it."""


def _passes_screen(word: str, without: str = "") -> bool:
    """Path (ii)'s shape screen as the page writes it; `without` leaves one clause out."""
    return not any(refuses(word) for clause, refuses in SCREEN.items() if clause != without)


REFUSED = (
    "Called to J. Smith RN at 14:32", "555-1234", "123-45-6789", "02139-1234", "02139",
    "a.b@c.org", "2024-01-05", "01/05/2024", "10.0.0.12", "http://x.org", "www.example",
    "14:32", "REC 0012345", "(319) 555-0100", "REC 4521", "E1234", "K1A 0B1", "J.S.", "J. Smith",
    "SN12", "SW1A 1AA",
)
PASSED = ("TNP", "HI", "LO", "1:40", "1:1280", "N/A", ".", "Not done", ">60", "<0.5", "QNS")


@pytest.mark.parametrize("word", REFUSED)
def test_the_shape_screen_refuses_each_shaped_class(word: str) -> None:
    assert not _passes_screen(word)


@pytest.mark.parametrize("word", PASSED)
def test_the_shape_screen_lets_the_result_words_through(word: str) -> None:
    assert _passes_screen(word)


def test_every_clause_of_the_screen_stands_on_the_page() -> None:
    page = _flat(_page())
    for clause in SCREEN:
        assert _flat(clause) in page, clause


# Each clause of the screen, a word only that clause refuses: the page's list is the screen. Clause (5)
# is the one no word reaches alone: a dotted quad of six figures or fewer always holds a date shape.
ONLY_THIS_CLAUSE = {
    "(1) at most two words": "seen by nurse",
    "(2) no run of five figures or more, and at most six figures in the word": "02139",
    "(3) no `@`, no `://`, no `www.`": "a@b",
    "(4) no date shape": "1/2/24",
    "and no clock shape (a two-figure hour 00 to 23, a colon and minutes 00 to 59, with or without seconds or a "
    "marker; a titer, `1:` and figures, is not one)": "14:32",
    "(6) no word holding both a letter and a figure": "SN12",
    "(7) no single letter followed by a point": "J.S.",
}


@pytest.mark.parametrize("clause", sorted(ONLY_THIS_CLAUSE))
def test_each_clause_of_the_screen_is_the_pages_and_refuses_its_own_class(clause: str) -> None:
    word = ONLY_THIS_CLAUSE[clause]
    assert _flat(clause) in _flat(_page()), clause
    assert not _passes_screen(word)
    assert _passes_screen(word, without=clause), (clause, word)


def test_the_screens_residual_is_the_one_the_page_names() -> None:
    assert _passes_screen("Smith") and _passes_screen("John Smith") and _passes_screen("JS")
    assert not _passes_screen("pH 7.35") and not _passes_screen("10E3/uL")
    page = _flat(_page())
    assert _passes_screen("ABCD") and not _passes_screen("SN12") and not _passes_screen("SW1A 1AA")
    assert _passes_screen("SN12", without="(6) no word holding both a letter and a figure")
    assert _passes_screen("SW1A 1AA", without="(6) no word holding both a letter and a figure")
    assert ("A lone one- or two-word name typed into a measurement column (`Smith`, `John Smith`, initials without "
            "points such as `JS`), or a serial written in letters alone, cannot be told from a result word by its "
            "shape") in page
    assert "a result word such as `pH 7.35` or `10E3/uL` is refused too" in page


def test_the_golden_region_holds_back_outlying_and_note_names_nothing(tmp_path: pathlib.Path) -> None:
    text = fixtures.every_role_table()
    document = _profiled(tmp_path, "every_role_table.csv", text)
    rows = list(csv.DictReader(io.StringIO(text)))
    region = _column(document, "region")
    assert region["role"] == "categorical"
    assert (region["suppressed_levels"], region["suppressed_rows"]) == (1, 7)
    assert collections.Counter(row["region"] for row in rows)["outlying"] == 7 and len(rows) == 240
    assert "outlying" not in json.dumps(region)
    note = _column(document, "note")
    assert note["role"] == "long_tail_labels"
    assert (note["suppressed_levels"], note["suppressed_rows"]) == (182, 217)
    for column in document["columns"]:
        assert "(withheld)" not in json.dumps(column.get("shape_forms", {}))
        assert "(withheld)" not in json.dumps(column.get("layout_forms", {}))
    published = [f"{level['label']}" for name in ("region", "note") for level in _column(document, name).get("levels") or []]
    assert published and not _figure_levels(published)  # path (iii)'s level-wise hold pools no golden level
    assert "`region` holds back `outlying` (7 of 240)" in _flat(_page())


def test_a_lone_held_back_level_prints_its_own_row_count(tmp_path: pathlib.Path) -> None:
    draw = random.Random(7)
    lines = ["gender,unit,value"]
    for k in range(600):
        gender = "X" if k < 4 else ("F" if draw.random() < 0.5 else "M")
        unit = "U" if k == 10 else ("A" if draw.random() < 0.5 else "B")
        lines += [f"{gender},{unit},{draw.gauss(50, 10):.1f}"]
    document = _profiled(tmp_path, "lone.csv", "\n".join(lines) + "\n")
    gender = _column(document, "gender")
    unit = _column(document, "unit")
    assert (gender["suppressed_levels"], gender["suppressed_rows"]) == (1, 4)
    assert (unit["suppressed_levels"], unit["suppressed_rows"]) == (1, 1)
    assert "a lone `U` prints `suppressed_rows 1`, measured again on this base" in _flat(_page())


def test_the_code_look_reaches_code_form_tails_and_not_words() -> None:
    assert asking._looks_like_a_code(["E11.9", "C50.911", "I10", "Z79.4"])
    assert asking._looks_like_a_code(["0JH60DZ", "J1885", "99213"])
    assert not asking._looks_like_a_code(["E11.9", "chest pain"])
    assert not asking._looks_like_a_code(["Penicillin", "Sulfa"])
    assert not asking._looks_like_a_code(["E11.9;I10"])
    assert not asking._looks_like_a_code(["X" * 21 + "1"])
    assert "a figure in every cell, no space, at most 20 characters" in _flat(_page())


def test_gg_reads_the_categories_ceiling_and_days_supply_falls_inside_it() -> None:
    ceiling = taxonomy.categories_ceiling(600, taxonomy.Settings())
    days_supply = {"5": 5, "7": 25, "10": 6, "14": 14, "21": 8, "28": 11, "30": 349, "84": 8, "90": 174}
    assert sum(days_supply.values()) == 600
    assert len(days_supply) <= ceiling
    assert sorted(value for value, n in days_supply.items() if n < FLOOR) == ["10", "21", "5", "84"]
    page = _flat(_page())
    assert "(`5` 5, `7` 25, `10` 6, `14` 14, `21` 8, `28` 11, `30` 349, `84` 8, `90` 174)" in page
    assert "`taxonomy.categories_ceiling`" in page


def test_the_mark_set_today_is_the_thirteen_the_page_widens() -> None:
    assert parsing.SHAPE_MARKS == "-./_:#*()[]+,"
    assert len(parsing.SHAPE_MARKS) == 13
    for mark in "=|;^~":
        assert mark not in parsing.SHAPE_MARKS
    assert "today the thirteen `-./_:#*()[]+,`) gains `=`, `|`, `;`, `^` and `~`" in _flat(_page())


FOUR = ("CODES-1", "CODES-2", "CODES-3", "GG")
TWELVE = (
    "demographics", "diagnoses", "medication_orders", "imaging", "genomics", "perioperative", "labs",
    "mixed_results", "tumor_registry", "immunizations_providers", "surveys_pro", "dicom_metadata",
)


def test_the_twelve_kinds_are_the_ones_the_zoo_owns_to_the_four_lanes() -> None:
    owned = sorted(
        kind for kind, lines in health_zoo.OWNERS.items()
        if any(owner in FOUR for owner, _gap, _covers in lines)
    )
    assert owned == sorted(TWELVE)
    page = _flat(_page())
    assert ", ".join(f"`{kind}`" for kind in TWELVE[:-1]) + f" and `{TWELVE[-1]}`" in page


def test_rule_u_reads_the_holding_questions_p4_d401_names() -> None:
    text = _flat(PLAN.read_text(encoding="utf-8"))
    p4d401 = text[text.index("## Decision P4-D401"):text.index("## Decision P4-D402")]
    assert (
        "the person question, the two-numbers question, or the question answered by a measurement, a code "
        "or a record number (padded figures, figures all one width or grouped in threes, and a date count "
        "whose values are also one width)"
    ) in p4d401
    assert "the point-between-thousands question and the checklist of columns read as numbers" in p4d401
    page = _flat(_page())
    for named in (
        "the person question (routes one to four)", "the two-numbers question",
        "the question answered by a measurement, a code or a record number put to padded figures",
        "the point-between-thousands question, the checklist of columns read as numbers",
    ):
        assert named in page, named


# The second repair (2026-10-22): the combined review of 0ebcdd08 and the one outside review.


def _figure_levels(levels: "list[str]") -> "list[str]":
    """Path (iii) read level by level: the published levels holding a figure, pooled while the question is open."""
    return [level for level in levels if any(mark.isdigit() for mark in level)]


@pytest.mark.parametrize("token, times", [("UNKNOWN", 1), ("HOMELESS", 3), ("FOREIGN", 2)])
def test_one_word_cell_defeats_the_column_wise_hold_and_not_the_level_wise_one(
    token: str, times: int, tmp_path: pathlib.Path,
) -> None:
    """The combined review's `zipword` shapes: today 6 real ZIPs print and nothing is asked."""
    draw = random.Random(11)
    zips = [f"0{2100 + 7 * k:04d}" for k in range(70)]
    weights = [1.0 / (k + 1) ** 1.1 for k in range(70)]
    lines = ["pid,zip"]
    for k in range(600):
        code = draw.choices(zips, weights)[0]
        cell = f"{code}-{draw.randint(1000, 9999)}" if k % 2 else code
        lines += [f"P{k:06d},{token if k < times else cell}"]
    document = _profiled(tmp_path, "zipword.csv", "\n".join(lines) + "\n")
    column = _column(document, "zip")
    assert (column["role"], column.get("n_missing")) == ("long_tail_labels", 0)
    printed = [f"{level['label']}" for level in column.get("levels") or []]
    assert len([label for label in printed if re.fullmatch(r"\d{5}", label)]) == 6
    asked = json.loads((tmp_path / "zipword-questions.json").read_text(encoding="utf-8"))["asked"]
    assert not [entry for entry in asked if entry.get("column") == "zip"]
    assert not _held_while_unanswered([line.split(",")[1] for line in lines[1:]])
    assert [level for level in printed if level not in _figure_levels(printed)] == []
    page = _flat(_page())
    assert "6 real five-figure ZIPs print with their counts (`02100`, `02107`, `02114`, `02121`, ...)" in page
    assert "`K-S3-64`'s held shapes `zipword`" in page


def test_the_level_wise_hold_leaves_word_levels_and_its_price_is_named() -> None:
    assert _figure_levels(["Boston", "Hà Nội", "spo2", "q6h", "1"]) == ["spo2", "q6h", "1"]
    assert _figure_levels(["DEM|LANG:F", "UNKNOWN"]) == []
    page = _flat(_page())
    assert "The level-by-level reading adds" in page and "5 columns and 15 levels, unanswered" in page
    assert "the majority reading would add 2 columns and 17 levels" in page


PLACEHOLDER = re.compile(r"(?:-9+|9{3,})(\.0+)?")
NEGATIVE_PLACEHOLDER = re.compile(r"-9+(\.0+)?")


def _top_coded(cells: "list[str]", placeholder: "re.Pattern[str]" = PLACEHOLDER) -> bool:
    """The Safe Harbor top-code's reach: present values within 0..125, one above 89, all-nines placeholders of
    either sign (`999`, `9999`, `-9`, `-99`, `-999`) set aside on at most one present cell in three."""
    present = [cell for cell in (cell.strip() for cell in cells) if cell]
    aside = [cell for cell in present if placeholder.fullmatch(cell)]
    if 3 * len(aside) > len(present):
        return False
    values: "list[float]" = []
    for cell in present:
        if placeholder.fullmatch(cell):
            continue
        try:
            values += [float(cell)]
        except ValueError:
            return False
    return bool(values) and min(values) >= 0 and max(values) <= 125 and max(values) > 89


def _printed_values(column: "dict") -> "set[float]":
    printed = set(((column.get("tails") or {}).get("high") or {}).get("values") or [])
    printed |= {value for value in (column.get("percentiles") or {}).values() if value is not None}
    return printed | ({column["mode"]} if column.get("mode") is not None else set())


def test_ages_over_89_print_today_and_the_top_code_reaches_them(tmp_path: pathlib.Path) -> None:
    """The combined review's `ages2000` shape: nobody answering, three ages over 89 print and nothing is asked."""
    draw = random.Random(7)
    ages = [min(104, max(18, int(draw.gauss(70, 14)))) for _ in range(2000)]
    lines = ["pid,age"] + [f"P{k:06d},{age}" for k, age in enumerate(ages)]
    document = _profiled(tmp_path, "ages2000.csv", "\n".join(lines) + "\n")
    age = _column(document, "age")
    assert (age["role"], age.get("n_distinct")) == ("count", 75)
    assert sorted(value for value in _printed_values(age) if value > 89) == [93.0, 103.0, 104.0]
    asked = json.loads((tmp_path / "ages2000-questions.json").read_text(encoding="utf-8"))["asked"]
    assert not [entry for entry in asked if entry.get("column") == "age"]
    assert _top_coded([f"{value}" for value in ages])
    read = ["pid,age"] + [f"P{k:06d},{min(age, 90)}" for k, age in enumerate(ages)]
    top = _column(_profiled(tmp_path, "ages2000top.csv", "\n".join(read) + "\n"), "age")
    assert max(_printed_values(top)) == 90.0
    page = _flat(_page())
    assert "it prints the high tail `values [103.0, 104.0]` and the rung 93, three ages over 89" in page
    assert "Under the top-code the `ages2000` shape prints 0 values above 89" in page


def test_the_top_codes_reach_spares_the_golden_reading_and_names_its_limits() -> None:
    rows = list(csv.DictReader(io.StringIO(fixtures.every_role_table())))
    assert not _top_coded([row["reading"] for row in rows])  # -999 to 394: the goldens keep their bytes
    assert not _top_coded([row["visits"] for row in rows])
    assert _top_coded([f"{value}" for value in range(50, 121)])  # a pulse: a false alarm, asked once
    assert _top_coded(["-99", "45", "91"]) and _top_coded(["-99.0", "88.5", "92.25"])
    assert not _top_coded(["45", "91", "130"]) and not _top_coded(["-1", "45", "91"])  # repair 3's reach
    assert _top_code_reach(["45", "91", "130"]) and _top_code_reach(["-1", "45", "91"])  # the bulk reach (close 2)
    assert not _top_code_reach([row["reading"] for row in rows]) and not _top_code_reach([row["visits"] for row in rows])
    assert _top_code_reach([row["amount"] for row in rows]) and _top_coded([row["amount"] for row in rows])
    page = _flat(_page())
    assert "one column, `vitals.pulse` (50 to 120, 71 values; today it prints 103, 113, 117, 119 and 120)" in page
    assert "the fixtures' `amount` (0.5 to 99.5) was in repair 3's reach already" in page


def test_rule_np_reads_the_products_attachment_ratio() -> None:
    from synthtwin import profile

    assert profile.ATTACHED_DIFFERENT_AT_MOST == 10
    assert "different * ATTACHED_DIFFERENT_AT_MOST <= again" in inspect.getsource(profile._attached)
    subjects = [f"S{k}" for k in range(10)] * 2
    first = [f"v{k}" for k in range(10)]
    assert profile._attached(first + first[:9] + ["other"], subjects)  # one repeated row in ten differs
    assert not profile._attached(first + first[:8] + ["other", "else"], subjects)  # two in ten
    assert "(P4-D406's test: one value a subject, at most one repeated row in ten differing)" in _flat(_page())


def _constant_marks(cells: "list[str]") -> "dict[str, list[str]]":
    """The rule the second repair withdrew: unanswered, the characters every cell of a form holds."""
    by_form: "dict[str, list[str]]" = collections.defaultdict(list)
    for cell in cells:
        by_form[_form(cell)] += [cell]
    return {
        form: [held[0][place] if len({cell[place] for cell in held}) == 1 else "" for place in range(len(form))]
        for form, held in by_form.items()
    }


def test_a2_unanswered_reads_no_held_back_cell() -> None:
    """The outside review's item 1: the form's constant characters rebuilt the real held-back levels."""
    cells = ["UNASSIGNED"] * 584 + ["ZX-A"] * 8 + ["ZX-B"] * 8
    withdrawn = _stand_ins(cells, {"@@-@": _constant_marks(cells)["@@-@"]}, widen=True)
    repaired = _stand_ins(cells, {}, widen=True)
    assert sorted(set(withdrawn) - {"UNASSIGNED"}) == ["ZX-A", "ZX-B"]
    assert sorted(set(repaired) - {"UNASSIGNED"}) == ["AA-A", "AA-B"]
    assert ("584 cells `UNASSIGNED` beside `ZX-A` and `ZX-B` on 8 cells each are written `AA-A` and `AA-B`"
            in _flat(_page()))


def test_a2_stage_one_takes_the_alphabet_where_no_published_level_wears_the_form() -> None:
    """The outside review's item 6: the page and this file's helper now read the same rule."""
    cells = [f"{letter}-Z" for letter in "ABCDEFGHIJKL" for _ in range(2)] + ["OPEN"] * 76
    tally = collections.Counter(cells)
    census = _census([(value, "") for value in cells if tally[value] < FLOOR], FLOOR, in_people=False)
    assert census == {"@-@": ["", "-", "Z"]}
    assert _stand_ins(cells, census, widen=True)[0] == "A-Z"
    assert "the census lists nothing, `-` and `Z`, and stage (1) writes `A-Z` first" in _flat(_page())


def _support(written: "list[str]", places: int) -> "list[collections.Counter[str]]":
    return [collections.Counter(cell[place] for cell in written) for place in range(places)]


def test_a2_balanced_walk_keeps_the_censuss_floor_in_the_twin() -> None:
    """The outside review's item 5: 61 levels of `@%@` on 4 cells each; the stage's own order puts `Y` on 4."""
    cells: "list[str]" = []
    for k, (figure, letter) in enumerate(itertools.product("01234", "ABCDEFGHIJKL")):
        cells += [("X" if k % 2 == 0 else "Y") + figure + letter] * 4
    cells += ["Y0A"] * 4
    tally = collections.Counter(cells)
    assert (len(tally), len(cells)) == (61, 244)
    census = _census([(value, "") for value in cells if tally[value] < FLOOR], FLOOR, in_people=False)
    assert census == {"@%@": ["XY", "01234", "ABCDEFGHIJKL"]}
    plain = _stand_ins(cells, census, widen=True, balanced=False)
    walked = _stand_ins(cells, census, widen=True)
    assert [cell[0] for cell in dict.fromkeys(plain)][:61] == ["X"] * 60 + ["Y"]
    assert _support(plain, 3)[0]["Y"] == 4
    listed = [(place, mark) for place, marks in enumerate(census["@%@"]) for mark in marks]
    assert min(_support(walked, 3)[place][mark] for place, mark in listed) == 16
    page = _flat(_page())
    assert "the stage's own order writes 60 `X` levels before the first `Y`, `Y` on 4 cells against the census's 11" in page
    assert "the balanced order puts every listed character on 16 cells or more" in page


def _joint_sizes(debts: "dict[str, int]", named: "dict[str, str]", unnamed: "list[str]") -> "dict[str, int]":
    """The names' joint allocation: each level 1..f-1, each form's debt met, a cell reserved per unnamed level.

    `named` maps a named level to its form; `unnamed` holds the form each unnamed level is reserved in.
    What remains of a form's debt goes to its named levels by an even split, past f-1 to its unnamed ones.
    """
    sizes = {level: 1 for level in named} | {f"unnamed-{k}": 1 for k in range(len(unnamed))}
    for form, debt in sorted(debts.items()):
        members = sorted(level for level, worn in named.items() if worn == form)
        spare = [f"unnamed-{k}" for k, worn in enumerate(unnamed) if worn == form]
        remains = debt - len(members) - len(spare)
        assert remains >= 0, form
        share, extra = divmod(remains, len(members)) if members else (0, 0)
        for place, level in enumerate(members):
            sizes[level] += share + (1 if place < extra else 0)
        overflow = sum(max(0, sizes[level] - (FLOOR - 1)) for level in members) + (0 if members else remains)
        for level in members:
            sizes[level] = min(sizes[level], FLOOR - 1)
        for level in spare:
            moved = min(overflow, FLOOR - 1 - sizes[level])
            sizes[level] += moved
            overflow -= moved
        assert overflow == 0, form
    return sizes


def test_named_levels_share_the_form_debts_not_the_pool() -> None:
    """The outside review's item 4: `AA` 39, `B-B` 39, `CC` 1, `DD` 1, `E-E` 10, `F-F` 10, the rare four named."""
    cells = ["AA"] * 39 + ["B-B"] * 39 + ["CC"] + ["DD"] + ["E-E"] * 10 + ["F-F"] * 10
    forms = collections.Counter(_form(cell) for cell in cells)
    assert forms == {"@@": 41, "@-@": 59}
    named = {"CC": "@@", "DD": "@@", "E-E": "@-@", "F-F": "@-@"}
    debts = {"@@": 41 - 39, "@-@": 59 - 39}
    readings = set()
    for extra in itertools.combinations(sorted(named), 2):  # the even split of the pooled 22: 6, 6, 5 and 5, seeded
        split = {level: 5 + (level in extra) for level in named}
        readings |= {39 + split["E-E"] + split["F-F"]}
    assert readings == {49, 50, 51}
    joint = _joint_sizes(debts, named, [])
    assert joint == {"CC": 1, "DD": 1, "E-E": 10, "F-F": 10}
    assert 39 + joint["E-E"] + joint["F-F"] == forms["@-@"]
    reserved = _joint_sizes({"@@": 15}, {"QQ": "@@"}, ["@@"])
    assert reserved == {"QQ": 10, "unnamed-0": 5}  # the whole pool to the name would leave the unnamed level none
    page = _flat(_page())
    assert "so form `@-@` reads 49 to 51 against its published 59" in page
    assert "the joint allocation gives `E-E` and `F-F` the 20 cells `@-@` owes and `CC` and `DD` the 2 `@@` owes" in page


def _absorbed(census: "dict[str, int]") -> "dict[str, int]":
    """Rule A1: forms under the floor counted in the commonest published one; none published, nothing moves."""
    published = {form: n for form, n in census.items() if form != "(withheld)" and n >= FLOOR}
    if not published:
        return dict(census)
    top = max(published, key=lambda form: (published[form], form))
    return published | {top: published[top] + sum(n for form, n in census.items() if form not in published)}


def test_a1_absorbs_into_a_published_layout_and_moves_nothing_where_none_is_published() -> None:
    row_43 = {"&&%%%%%%%%": 58, "&&%%%%%%%%%": 533, "(withheld)": 9}
    assert _absorbed(row_43) == {"&&%%%%%%%%%": 542, "&&%%%%%%%%": 58}
    ten_layouts = {"(withheld)": 100}  # 100 values in ten layouts of ten cells each, none published
    assert _absorbed(ten_layouts) == {"(withheld)": 100}
    assert 'A column none of whose forms or layouts is published' in _flat(_page())


def test_ggs_membership_reads_present_cells_and_keeps_the_blanks() -> None:
    """The outside review's item 8: `1` on 200 rows, `3` on 200 and 200 blanks, after `no`."""
    few_values = {"1", "3"}
    twin = ["1"] * 200 + ["3"] * 200 + [""] * 200
    assert all(cell in few_values for cell in twin if cell)
    assert not all(cell in few_values for cell in twin)  # "every twin cell" would fail the column's own blanks
    assert "(a column of `1` on 200 rows, `3` on 200 and 200 blanks keeps its 200 blanks)" in _flat(_page())


def test_the_zoo_knows_its_udi_as_a_code_and_answers_it_yes() -> None:
    """The combined review's item 3: answered `no`, the zoo's own answer would publish its 20 GS1 UDIs."""
    table = next(table for table in health_zoo.TABLES if table.name == "immunizations")
    assert table.knows["udi"] == "code"
    pattern = re.compile(r"\(01\)\d{14}\(17\)\d{6}\(10\)[A-Z0-9]+")
    assert pattern.fullmatch("(01)69944697887698(17)252216(10)LOT862")
    assert not pattern.fullmatch("(37)69944697887698(52)252216(84)LOT862")  # every figure drawn, as `yes` writes
    page = _flat(_page())
    assert "answered `no` it would publish the 20 GS1 UDIs it prints today" in page
    assert "| `immunizations_providers` | CODES-2's names (`npi`) beside a repeating person column, and `udi` answered `yes`" in page


# The third repair (2026-10-23): the second verify of 37e028c7, its three new items.


def _five_figure_held(cells: "list[str]", every: bool = False) -> bool:
    """ZS.1's five-figure hold: whole numbers all of five figures, padded or not, at most one present cell in three
    set aside as words; `every` is the all-or-nothing reading no word cell may sit beside."""
    present = [cell for cell in (cell.strip() for cell in cells) if cell]
    numbers = [cell for cell in present if re.fullmatch(r"\d+", cell)]
    words = [cell for cell in present if not re.fullmatch(r"[-+]?\d+(\.\d*)?", cell)]
    if every and words:
        return False
    if 3 * len(words) > len(present) or len(numbers) + len(words) != len(present) or not numbers:
        return False
    return all(len(cell) == 5 for cell in numbers)


def _zip5word(lead: bool, token: str, times: int) -> "tuple[list[str], list[str]]":
    draw = random.Random(11)
    zips = [f"0{2100 + 7 * k:04d}" if lead else f"{52240 + 7 * k}" for k in range(70)]
    weights = [1.0 / (k + 1) ** 1.1 for k in range(70)]
    return zips, [token if k < times else draw.choices(zips, weights)[0] for k in range(600)]


@pytest.mark.parametrize("lead", [True, False])
@pytest.mark.parametrize("token, times", [("UNKNOWN", 1), ("HOMELESS", 3)])
def test_one_word_cell_beside_five_figure_zips_read_as_numbers_prints_them_today(
    lead: bool, token: str, times: int, tmp_path: pathlib.Path,
) -> None:
    """The second verify's item 1, `zip5word`: today 9 real ZIPs print; the five-figure hold reaches the column."""
    zips, cells = _zip5word(lead, token, times)
    lines = ["pid,zip"] + [f"P{k:06d},{cell}" for k, cell in enumerate(cells)]
    column = _column(_profiled(tmp_path, "zip5word.csv", "\n".join(lines) + "\n"), "zip")
    assert column["role"] == "count"
    printed = [value for value in _printed_values(column) if float(value).is_integer()]
    assert len([value for value in printed if f"{int(value):05d}" in zips]) == 9
    assert _five_figure_held(cells)
    assert not _five_figure_held(cells, every=True)  # the all-or-nothing reading: one word lifts it
    assert not _five_figure_held(["HOMELESS"] * 201 + cells[201:])  # repair 3's cap: past it, not reached
    assert _zip_reach(cells) and _zip_reach(["HOMELESS"] * 201 + cells[201:])  # close 2: words aside whatever their share
    page = _flat(_page())
    assert "TODAY'S product prints 9 real ZIPs on each of the four shapes" in page
    assert "a tenth rung within one of a real ZIP (`2478.7`, `52618.7`; the second verify counted it, 10)" in page


def test_the_five_figure_hold_spares_other_number_columns() -> None:
    assert not _five_figure_held(["2100", "52240", "UNKNOWN"])  # repair 3's reach missed the lost zeros
    assert _zip_reach(["2100", "52240", "UNKNOWN"])  # close 2: in reach
    for cells in (["45", "91", "UNKNOWN"], ["12345.5", "23456"], ["2100", "2107"], ["1998", "2003", "2011"]):
        assert not _five_figure_held(cells) and not _zip_reach(cells), cells
    assert _five_figure_held(["02100", "52240", "", "UNKNOWN"]) and _zip_reach(["02100", "52240", "", "UNKNOWN"])
    page = _flat(_page())
    assert "a ZIP column whose leading zeros were lost (`2100` beside `52240`) is in reach" in page
    assert "With 150 or 250 `HOMELESS` cells of 600 and a leading zero the column is read `numbers_with_labels`" in page


@pytest.mark.parametrize("times, over", [(1, [93.0, 103.0]), (20, [94.0, 112.95])])
def test_a_999_cell_beside_ages_prints_ages_over_89_today_and_both_signs_are_set_aside(
    times: int, over: "list[float]", tmp_path: pathlib.Path,
) -> None:
    """The second verify's item 2, `ages999`: one `999` defeated a reach setting aside negative placeholders only."""
    draw = random.Random(7)
    ages = [min(104, max(18, int(draw.gauss(70, 14)))) for _ in range(2000)]
    cells = ["999" if k < times else f"{age}" for k, age in enumerate(ages)]
    lines = ["pid,age"] + [f"P{k:06d},{cell}" for k, cell in enumerate(cells)]
    document = _profiled(tmp_path, "ages999.csv", "\n".join(lines) + "\n")
    age = _column(document, "age")
    assert age["role"] == "count"
    assert sorted(value for value in _printed_values(age) if 89 < value <= 125) == over
    asked = json.loads((tmp_path / "ages999-questions.json").read_text(encoding="utf-8"))["asked"]
    assert not [entry for entry in asked if entry.get("column") == "age"]
    assert _top_coded(cells)
    assert not _top_coded(cells, placeholder=NEGATIVE_PLACEHOLDER)  # "negative all-nines placeholders aside"
    assert _top_coded(["9999", "45", "91"]) and not _top_coded(["99", "45", "91", "130"])
    assert not _top_coded(["999", "999", "45", "91"])  # more than one present cell in three: not reached
    assert "beside one `999` the same column prints 93 and 103, beside twenty 94 and 112.95" in _flat(_page())


def test_the_screen_passes_short_record_numbers_in_figures_and_marks_as_its_named_residual() -> None:
    """The second verify's item 3: `#4521` and `12-345` pass the screen beside the result words that must."""
    for word in ("#4521", "12-345", "4521/7", "#45-21", "120/80", "2-3", "1:40"):
        assert _passes_screen(word), word
    page = _flat(_page())
    assert "`#4521`, `12-345`, `4521/7` and `#45-21` pass, as the result words `120/80`, `2-3` and `1:40` must" in page
    assert ("a short record or accession number written in figures and marks (`#4521`, `12-345`) passes it too, but is "
            "named only after `no` (ZS.3 (ii)), no residual") in page


# Close 2 (2026-10-23): Codex's second outside round (`codex-w3/verdict-ZRb2.md`). The owner: "Fix 4 privacy, carry
# 5". Items 1 to 4 are fixed on the page, each case computed here and its product reading measured at 20,000 rows;
# items 5 to 9 are carried to their lanes (ZS.11), each with Codex's case and an "open until" mark on the page.

NINES = re.compile(r"(?:-9+|9{3,})(?:\.0+)?")
ONE_NUMBER = re.compile(r"[^\d.+-]*([-+]?\d+(?:\.\d+)?)[^\d]*")
REPAIR_3_ROLES = ("count", "continuous", "numbers_with_labels")


def _numbers_of(cells: "list[str]") -> "list[str]":
    """The present cells read as one number each, an affix taken off (`95 years` is 95); words and joined cells aside."""
    found: "list[str]" = []
    for cell in (cell.strip() for cell in cells):
        match = ONE_NUMBER.fullmatch(cell) if cell else None
        if match:
            found += [match.group(1)]
    return found


def _set_aside(numbers: "list[str]", repeated: bool = True) -> "set[float]":
    """ZS.1's placeholders, close 3: an all-nines value of either sign; a minus sign with one figure; and any single
    value outside 0 to 125 that at least the floor's rows repeat, whatever their share. `repeated=False` is close 2's
    all-nines alone, a mutant."""
    aside = {float(text) for text in numbers if NINES.fullmatch(text)}
    if repeated:
        tally = collections.Counter(float(text) for text in numbers)
        aside |= {float(text) for text in numbers if re.fullmatch(r"-\d(?:\.0+)?", text)}
        aside |= {value for value, n in tally.items() if not 0 <= value <= 125 and n >= FLOOR}
    return aside


def _top_code_reach(cells: "list[str]", bulk: bool = True, capped: bool = False, repeated: bool = True) -> bool:
    """ZS.1's top-code reach: words and placeholders set aside whatever their share; at least two thirds of the other
    numbers within 0 to 125; one above 89. `bulk=False` asks it of every number and `capped` sets the all-nines
    placeholders aside on at most one present cell in three: repair 3's reach, each a mutant; `repeated=False` is
    close 2's placeholders, a mutant."""
    present = [cell for cell in (cell.strip() for cell in cells) if cell]
    numbers = _numbers_of(cells)
    if capped and 3 * len([text for text in numbers if NINES.fullmatch(text)]) > len(present):
        return False
    aside = _set_aside(numbers, repeated)
    values = [float(text) for text in numbers if float(text) not in aside]
    inside = [value for value in values if 0 <= value <= 125]
    enough = 3 * len(inside) >= 2 * len(values) if bulk else len(inside) == len(values)
    return bool(values) and enough and max(values) > 89


LEVEL_NUMBER = re.compile(r"\s*([-+]?\d+(?:\.\d+)?)(?:\s*[A-Za-z]+)?\s*")


def _label_age_reach(cells: "list[str]", word_placeholders: bool = True) -> bool:
    """ZS.1's reach in label roles, close 3: levels that are a number with an optional unit word; placeholders set
    aside whatever their share (the number ones, and a word that at least the floor's rows repeat), other words on at
    most one present cell in three; then the numbers' reach. `word_placeholders=False` caps every word, a mutant."""
    present = [cell for cell in (cell.strip() for cell in cells) if cell]
    numbers: "list[str]" = []
    words: "list[str]" = []
    for cell in present:
        match = LEVEL_NUMBER.fullmatch(cell)
        if match:
            numbers += [match.group(1)]
        else:
            words += [cell]
    tally = collections.Counter(words)
    other = [word for word in words if tally[word] < FLOOR] if word_placeholders else words
    if 3 * len(other) > len(present):
        return False
    aside = _set_aside(numbers)
    values = [float(text) for text in numbers if float(text) not in aside]
    inside = [value for value in values if 0 <= value <= 125]
    return bool(values) and 3 * len(inside) >= 2 * len(values) and max(values) > 89


def _read_as_90(cells: "list[str]", label: bool = False) -> "list[str]":
    """The column read under the top-code: every number above 89 that is no placeholder written as 90, in the
    source's own form (`95 years` read `90 years`); placeholders as the source wrote them."""
    pattern = LEVEL_NUMBER if label else ONE_NUMBER
    numbers = [match.group(1) for match in (pattern.fullmatch(cell.strip()) for cell in cells if cell.strip()) if match]
    aside = _set_aside(numbers)
    read: "list[str]" = []
    for cell in cells:
        match = pattern.fullmatch(cell.strip()) if cell.strip() else None
        number = match.group(1) if match else ""
        if number and float(number) not in aside and float(number) > 89:
            read += [cell.replace(number, "90", 1)]
        else:
            read += [cell]
    return read


def _zip_reach(cells: "list[str]", widths: "tuple[int, ...]" = (4, 5)) -> bool:
    """ZS.1's five-figure hold, close 2: whole numbers as the source wrote them, at least two thirds of four or five
    figures, one of five; words, a lone `0` and a minus sign with one figure set aside whatever their share.
    `widths=(5,)` is repair 3's five figures only, a mutant."""
    numbers = [text for text in _numbers_of(cells) if text != "0" and not re.fullmatch(r"-\d", text)]
    whole = [text.split(".")[0] for text in numbers if re.fullmatch(r"\d+(\.0+)?", text)]
    shaped = [text for text in whole if len(text) in widths]
    return bool(numbers) and 3 * len(shaped) >= 2 * len(numbers) and any(len(text) == 5 for text in whole)


def _reach_roles() -> "set[str]":
    """The roles the page's top-code sentence names, read from the page itself."""
    page = _flat(_page())
    start = page.index("EVERY ROLE THAT PRINTS A VALUE is in its reach:")
    return set(re.findall(r"`([a-z_]+)`", page[start:page.index("whole numbers or not", start)]))


def _affixed_ages() -> "list[str]":
    draw = random.Random(5)
    return [f"{min(104.99, max(18.0, draw.gauss(70, 14))):.2f} years" for _ in range(20000)]


CODEX_AGES = {
    "binary": (["60"] * 10000 + ["95"] * 10000, "binary"),
    "constant": (["95"] * 20000, "constant"),
    "outlier": (["60"] * 10000 + ["95"] * 9999 + ["130"], "count"),
    "placeholders": (["60"] * 6500 + ["95"] * 6500 + ["999"] * 7000, "count"),
}
CODEX_ZIPS = {
    "binary": (["02100"] * 10000 + ["02107"] * 10000, "binary"),
    "constant": (["02100"] * 20000, "constant"),
    "zeros-lost": (["2100", "2107", "52240", "52247"] * 5000, "count"),
}


def _printed(column: "dict") -> "set[str]":
    """Every value a block prints: levels, rungs (`percentiles_between` too), mode, empty-gap edges and tail values."""
    shown: "set[str]" = set()
    for level in column.get("levels") or []:
        shown |= {f"{level['label']}"}
    rungs = list((column.get("percentiles") or {}).values()) + list((column.get("percentiles_between") or {}).values())
    for value in rungs + [column.get("mode")] + [edge for pair in column.get("empty_edges") or [] for edge in pair]:
        if value is not None:
            shown |= {f"{value}"}
    for side in ("high", "low"):
        shown |= {f"{value}" for value in ((column.get("tails") or {}).get(side) or {}).get("values") or []}
    return shown


@pytest.mark.parametrize("case", sorted(CODEX_AGES))
def test_codex_round_two_ages_print_today_and_the_widened_reach_takes_them(case: str, tmp_path: pathlib.Path) -> None:
    """Items 1 and 3: at 20,000 rows, nobody answering, each case prints 95 with no question; the page's reach takes it."""
    cells, role = CODEX_AGES[case]
    document = _profiled(tmp_path, "ages.csv", "age\n" + "\n".join(cells) + "\n")
    column = _column(document, "age")
    assert column["role"] == role and role in _reach_roles()
    assert any(89 < float(value) <= 125 for value in _printed(column)), _printed(column)
    asked = json.loads((tmp_path / "ages-questions.json").read_text(encoding="utf-8"))["asked"]
    assert not [entry for entry in asked if entry.get("column") == "age"]
    assert _top_code_reach(cells)
    if case == "outlier":
        assert not _top_code_reach(cells, bulk=False) and not _top_coded(cells)  # every value within 0..125: off
    if case == "placeholders":
        assert not _top_code_reach(cells, capped=True) and not _top_coded(cells)  # one-third cap: off
    if case in ("binary", "constant"):
        assert _top_coded(cells) and role not in REPAIR_3_ROLES  # repair 3 met the cells, not the role


def test_codex_round_two_affixed_ages_are_in_reach_after_keep() -> None:
    """Item 1: ages written ` years`, read `affixed_number` once the person question is answered `keep`
    (`r4-probe3.log`): the number part is in reach; repair 3's reach, reading whole cells, was not."""
    cells = _affixed_ages()
    assert _top_code_reach(cells) and not _top_coded(cells)
    assert "affixed_number" in _reach_roles() and "affixed_number" not in REPAIR_3_ROLES
    page = _flat(_page())
    assert ("once it is answered `keep` they read `affixed_number` and print `max` 104.99, `p99` 102.91 and `p95` "
            "92.83") in page
    assert "`60` x 6,500, `95` x 6,500 and `999` x 7,000 read `count` and print `p50` 95" in page
    assert "`60` x 10,000, `95` x 9,999 and one `130` read `count` and print 95 from `p75` to `p99`" in page


@pytest.mark.parametrize("case", sorted(CODEX_ZIPS))
def test_codex_round_two_zips_print_today_and_the_widened_hold_takes_them(case: str, tmp_path: pathlib.Path) -> None:
    """Items 1 and 4: binary and constant ZIPs and ZIPs that lost their leading zeros print real ZIPs today."""
    cells, role = CODEX_ZIPS[case]
    document = _profiled(tmp_path, "zips.csv", "zip\n" + "\n".join(cells) + "\n")
    column = _column(document, "zip")
    assert column["role"] == role and role in _reach_roles()
    real = {cell.lstrip("0") for cell in cells}
    shown = {value.split(".")[0].lstrip("0") for value in _printed(column)}
    assert real <= shown, (real, shown)
    asked = json.loads((tmp_path / "zips-questions.json").read_text(encoding="utf-8"))["asked"]
    assert not [entry for entry in asked if entry.get("column") == "zip"]
    assert _zip_reach(cells)
    if case == "zeros-lost":
        assert not _zip_reach(cells, widths=(5,)) and not _five_figure_held(cells)  # five figures only: missed
    else:
        assert _five_figure_held(cells) and role not in REPAIR_3_ROLES  # repair 3 met the cells, not the role
    page = _flat(_page())
    assert ("and prints `mode` 2100, `min` 2100, `max` 52247, `p90` 52247 and the tail values 2100 and 52247, and 2107 and "
            "52240 among `percentiles_between` and as the edges of its published empty gap") in page


def _named_by_path_ii(word: str, answer: str, screen_only: bool = False) -> bool:
    """ZS.3 (ii), close 2: a held-back word passing the screen is named; one holding a figure only after `no`.
    `screen_only` is repair 3's reading, its mutant."""
    if not _passes_screen(word):
        return False
    return screen_only or answer == "no" or not any(mark.isdigit() for mark in word)


def test_codex_round_two_hash_word_is_held_until_no(tmp_path: pathlib.Path) -> None:
    """Item 2: 16,000 numbers 1.00..16.99, 3,999 `HI` and one `#4521` at 20,000 rows: today `#4521` is held back
    unnamed and nothing is asked; the screen alone would name it; the page names it only after `no`."""
    cells = [f"{1 + (k % 1600) / 100:.2f}" for k in range(16000)] + ["HI"] * 3999 + ["#4521"]
    document = _profiled(tmp_path, "hash.csv", "result\n" + "\n".join(cells) + "\n")
    column = _column(document, "result")
    assert column["role"] == "numbers_with_labels" and "#4521" not in json.dumps(column)
    asked = json.loads((tmp_path / "hash-questions.json").read_text(encoding="utf-8"))["asked"]
    assert not [entry for entry in asked if entry.get("column") == "result"]
    assert _named_by_path_ii("#4521", "", screen_only=True)  # repair 3: named with no question
    assert not _named_by_path_ii("#4521", "") and _named_by_path_ii("#4521", "no")
    for word in ("12-345", "4521/7", "120/80", "1:40"):
        assert not _named_by_path_ii(word, "") and _named_by_path_ii(word, "no"), word
    for word in ("HI", "TNP", "N/A", "Not done"):
        assert _named_by_path_ii(word, ""), word
    assert "and `#4521` stays held unanswered (CODES-2's gate case `hashword`)" in _flat(_page())


def _carried() -> str:
    page = _page()
    return page[page.index("### ZS.11 Carried to lanes (the owner, 2026-10-23)"):]


CARRIED = {
    5: ("owner CODES-2", "open until CODES-2 (ZS.11 item 5)",
        ("ten ZIP+4 labels on 1,990 rows each beside `UNKNOWN` on 100 rows", "`suppressed_rows 19,900`",
         "at most 100 cells (10 levels of at most 10)", "contract B4", "A report that names a shortfall does not meet it.")),
    6: ("owner CODES-1", "open until CODES-1 (ZS.11 item 6)",
        ("a held form `@%` of 24 levels on 5 rows each", "the census lists [empty, `01`]", "[`ABX`, `01234`]")),
    7: ("owner CODES-2", "open until CODES-2 (ZS.11 item 7)",
        ("validate reads that profile and one CSV", "keeps the overlap with the source a measurement of its gate's "
         "fixtures")),
    8: ("owner lane SH now, CODES-2 extending it", "open until lane SH (P4-D427), CODES-2 extending it (ZS.11 item 8)",
        ("a pulse of 50 to 120", "\"none of these: the values are measurements, counts, codes or categories that name "
         "no person, place, date or record\"", "The question asks what the column holds, never the analysis.")),
    9: ("owner NOTES", "open until NOTES",
        ("20 common three-word descriptions on 11 rows each beside 19,780 different three-word descriptions",
         "BEFORE rule 9b's fallback and kept after it")),
}


@pytest.mark.parametrize("item", sorted(CARRIED))
def test_each_carried_item_names_codexs_case_its_condition_and_its_owner(item: int) -> None:
    owner, mark, case = CARRIED[item]
    carried = _flat(_carried())
    entry = carried[carried.index(f"{item}. **"):]
    entry = entry[:entry.index(f"{item + 1}. **")] if item < 9 else entry
    assert f"-- {owner}.**" in entry, item
    for fragment in case:
        assert _flat(fragment) in entry, (item, fragment)
    assert "The condition" in entry and "The gate" in entry
    page = _flat(_page())
    elsewhere = page[:page.index("### ZS.11 Carried to lanes")]
    assert mark in elsewhere, (item, mark)
    assert f"ZS.11 item {item}" in elsewhere


def test_the_carried_cases_add_up() -> None:
    """Codex's carried cases, computed: the pool, A2's census before and after, NOTES' rows."""
    assert 10 * 1990 == 19900 and 10 * (FLOOR - 1) == 100 and 10 * 1990 + 100 == 20000
    letters = [chr(code) for code in range(ord("A"), ord("W") + 1)] + ["Y"]
    real = [(f"{letter}{k % 2}", f"{letter}{k}") for k, letter in enumerate(letters) for _ in range(5)]
    assert len({value for value, _ in real}) <= 24 and len(real) == 120
    assert _census(real, FLOOR, in_people=False)["@%"] == ["", "01"]
    written = [f"X{k}" for k in range(9)] + [f"A{k}" for k in range(10)] + [f"B{k}" for k in range(5)]
    twin = [(value, value) for value in written for _ in range(5)]
    assert len(written) == 24 and len(twin) == 120
    assert _census(twin, FLOOR, in_people=False)["@%"] == ["ABX", "01234"]
    assert 20 * 11 + 19780 == 20000


def test_the_owners_decision_is_recorded_and_the_page_agrees_with_lane_sh() -> None:
    text = _flat(PLAN.read_text(encoding="utf-8"))
    decision = text[text.index(DECISION_HEADING):]
    assert "\"Fix 4 privacy, carry 5\"" in decision and "**Close 2 (2026-10-23).**" in decision
    assert "no third outside round" in decision and "The items carried to lanes are ZS.11." in decision
    page = _flat(_page())
    assert "\"Fix 4 privacy, carry 5\"" in page
    assert "`asking.safe_harbor_sentence`" in page and "`SAFE_HARBOR_CLASSES`" in page
    assert "its own AQ family `safe-harbor`" in page


# Close 3 (2026-10-23): the internal verify of close 2 (`wave6/ZRb-verify3.md`) and the orchestrator's LANE SH
# ADDENDUM 2: placeholders that are not all-nines, ages in label roles, the carried items' marks at their places, and
# SH's head.

MARKS = (
    ("### ZS.0 ", "(whether that question reaches a column rule 9b has already turned into `free_text` is open until "
     "NOTES, ZS.11 item 9)"),
    ("### ZS.3 ", "Where no allocation meets the debts, the twin's report names the shortfall, as G8.2a names one; a "
     "profile whose pool no allocation can meet at all is open until CODES-2 (ZS.11 item 5)."),
    ("### ZS.3 ", "(GG's columns join it, ZS.4); a column the reading page's rule 9b turns into `free_text` before this "
     "entry is written is open until NOTES (ZS.11 item 9)."),
    ("### ZS.3 ", "at most 100 cells allocable at floor 11): open until CODES-2 (ZS.11 item 5)."),
    ("### ZS.3 ", "and names nothing; whether a tail rule 9b has turned into `free_text` is put the question at all is "
     "open until NOTES, ZS.11 item 9);"),
    ("### ZS.3 ", "The wording of `no` is open until lane SH (P4-D427), CODES-2 extending it (ZS.11 item 8): as written "
     "it leaves a measurement, such as a pulse of 50 to 120, no truthful answer."),
    ("### ZS.5 ", "A2 adds no own-fact group to RULE W1's list. That the twin and the validator keep the unlisted "
     "characters' bound is open until CODES-1 (ZS.11 item 6)."),
    ("### ZS.6 ", "the upper bound on unlisted characters, in generation and validation, is open until CODES-1 (ZS.11 "
     "item 6) |"),
    ("### ZS.6 ", "the held block's checks, as `yes`; \"no twin cell a real value\" is not validate's to check from one "
     "profile and one CSV: open until CODES-2 (ZS.11 item 7) |"),
)


def _section(heading: str) -> str:
    page = _page()
    start = page.index(heading)
    stop = page.find("### ZS.", start + len(heading))
    return page[start:stop if stop >= 0 else len(page)]


@pytest.mark.parametrize("place, mark", MARKS, ids=[f"{place.strip()}-{k}" for k, (place, _) in enumerate(MARKS)])
def test_each_open_until_mark_stands_where_the_rule_is_stated(place: str, mark: str) -> None:
    """The verify's item 5: a carried item's mark pinned at its place, not as appearing somewhere on the page."""
    assert _flat(mark) in _flat(_section(place)), (place, mark)


def _spread_ages() -> "list[str]":
    """The verify's case: 12,000 ages drawn from N(70, 14) clipped to 18..104 (its seed, 23) beside 8,000 `-1`."""
    draw = random.Random(23)
    return [f"{min(104, max(18, int(draw.gauss(70, 14))))}" for _ in range(12000)] + ["-1"] * 8000


VERIFY_AGES = {
    "minus-one": (["60"] * 6500 + ["95"] * 6500 + ["-1"] * 7000, "continuous", [95.0]),
    "minus-one-spread": (_spread_ages(), "continuous", [90.0, 92.0, 95.0, 99.0, 100.0, 101.0, 102.0, 103.0, 104.0]),
    "eights": (["60"] * 6500 + ["95"] * 6500 + ["888"] * 7000, "count", [95.0]),
}


@pytest.mark.parametrize("case", sorted(VERIFY_AGES))
def test_placeholders_that_are_not_all_nines_print_ages_today_and_the_reach_takes_them(
    case: str, tmp_path: pathlib.Path,
) -> None:
    """The verify's item 3: at 20,000 rows, nobody answering, each prints ages over 89 with no question; close 2's reach,
    setting aside all-nines alone, missed each; with `-1` and every repeated value outside 0 to 125 aside, it is
    reached, and read as 90 prints 0 ages over 89."""
    cells, role, over = VERIFY_AGES[case]
    document = _profiled(tmp_path, "ages.csv", "age\n" + "\n".join(cells) + "\n")
    column = _column(document, "age")
    assert column["role"] == role and role in _reach_roles()
    assert sorted({float(value) for value in _printed(column) if 89 < float(value) <= 125}) == over
    asked = json.loads((tmp_path / "ages-questions.json").read_text(encoding="utf-8"))["asked"]
    assert not [entry for entry in asked if entry.get("column") == "age"]
    assert _top_code_reach(cells) and not _top_code_reach(cells, repeated=False)
    top = _column(_profiled(tmp_path, "agestop.csv", "age\n" + "\n".join(_read_as_90(cells)) + "\n"), "age")
    assert {float(value) for value in _printed(top) if 89 < float(value) <= 125} <= {90.0}
    page = _flat(_page())
    assert "`60` x 6,500, `95` x 6,500 and `-1` x 7,000 read `continuous` and print 95" in page
    assert ("12,000 ages drawn from N(70, 14) clipped to 18..104 beside 8,000 `-1` read `continuous` and print 90, 92, "
            "95, 99 and 100 to 104") in page
    assert "`60` x 6,500, `95` x 6,500 and `888` x 7,000 read `count` and print `p50` 95" in page


def test_the_placeholder_reach_spares_the_golden_reading_and_names_its_limits() -> None:
    """ZS.10 narrowed: repeated values outside 0 to 125 are set aside; spread thin they keep an age out of reach."""
    rows = list(csv.DictReader(io.StringIO(fixtures.every_role_table())))
    assert not _top_code_reach([row["reading"] for row in rows])  # `-999` set aside, still out of reach
    assert _top_code_reach(["-1", "45", "91", "300"]) and not _top_code_reach(["-1", "45", "91", "300"], bulk=False)
    months = [f"{month}" for month in range(1200)]
    assert not _top_code_reach(months)  # an age in months spread thin: out of reach
    assert _top_code_reach(months * FLOOR)  # repeated: its values above 125 set aside, the rest top-coded
    assert _top_code_reach([f"{pounds}" for pounds in range(100, 300)] * FLOOR)  # a weight in pounds: a false alarm
    page = _flat(_page())
    assert "it drops `labs.result_value` (no value from 90 to 125 left once its repeated values above 125 are set aside)" in page
    assert "on the analyst tables it adds `fu_days` of ST1 and ST6" in page


VERIFY_LABELS = {
    "years": ([f"{18 + (k * 37) % 87} years" for k in range(20000)], "categorical"),
    "unk": (["60"] * 6500 + ["95"] * 6500 + ["UNK"] * 7000, "categorical"),
}


@pytest.mark.parametrize("case", sorted(VERIFY_LABELS))
def test_ages_in_label_roles_print_today_and_the_label_reach_takes_them(case: str, tmp_path: pathlib.Path) -> None:
    """The verify's item 4: ages written `NN years`, and `95` beside `UNK` x 7,000, read `categorical` and print levels
    above 89 with no question; the label-role reach takes both, and pooled into 90 they print 0 ages over 89."""
    cells, role = VERIFY_LABELS[case]
    document = _profiled(tmp_path, "labels.csv", "age\n" + "\n".join(cells) + "\n")
    column = _column(document, "age")
    assert column["role"] == role
    shown = [f"{level['label']}" for level in column.get("levels") or []]
    numbers = [float(match.group(1)) for match in (LEVEL_NUMBER.fullmatch(label) for label in shown) if match]
    over = sorted(number for number in numbers if 89 < number <= 125)
    assert over == ([float(age) for age in range(90, 105)] if case == "years" else [95.0])
    asked = json.loads((tmp_path / "labels-questions.json").read_text(encoding="utf-8"))["asked"]
    assert not [entry for entry in asked if entry.get("column") == "age"]
    assert role not in _reach_roles()  # the number roles' reach never reads a label column
    assert _label_age_reach(cells)
    if case == "unk":
        assert not _label_age_reach(cells, word_placeholders=False)  # every word capped: `UNK` x 7,000 lifts it
    pooled = _read_as_90(cells, label=True)
    top = _column(_profiled(tmp_path, "labelstop.csv", "age\n" + "\n".join(pooled) + "\n"), "age")
    labels = [f"{level['label']}" for level in top.get("levels") or []]
    numbers = [float(match.group(1)) for match in (LEVEL_NUMBER.fullmatch(label) for label in labels) if match]
    assert not [number for number in numbers if 89 < number <= 125 and number != 90]
    page = _flat(_page())
    assert ("ages 18 to 104 written `NN years`, each on about 230 rows, read `categorical`, nothing is asked, and the "
            "levels `90 years` to `104 years` print with their counts") in page
    assert "`60` x 6,500, `95` x 6,500 and `UNK` x 7,000 read `categorical` and print the level `95`" in page


def test_the_page_cites_sh_at_its_head_and_closes_the_goldens_mark() -> None:
    """The verify's item 6: SH's 0e3a65d4 makes the top-code the `profile` command's rule, so the goldens keep their
    bytes; no "open until SH" mark is left on them."""
    page = _flat(_page())
    assert "0e3a65d4" in page and "b0dbd57c" not in page
    assert "open until SH" not in page
    assert "and the zoo answers `no` for `vitals.pulse` (ZS.7)" in page


def test_close_3_is_recorded_in_the_decision() -> None:
    text = _flat(PLAN.read_text(encoding="utf-8"))
    decision = text[text.index(DECISION_HEADING):]
    assert "**Close 3 (2026-10-23).** On the internal verify of close 2 (`wave6/ZRb-verify3.md`)" in decision
    assert ("`-1` and any single value outside 0 to 125 that the floor's rows repeat are set aside whatever their share "
            "(the orchestrator's LANE SH ADDENDUM 2, case (1))") in decision
    assert "ages in label roles are in the top-code's reach now, built by lane SH (its case (2)), not left to CODES-2" in decision
