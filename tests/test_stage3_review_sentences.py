"""Six sentences stage 3 left behind, each measured against the run.

WHAT THIS FILE IS. The adversarial review of 2026-09-23 returned REJECT
on stage 3 and the items it raised, 5 to 10, are all of one kind: a page
telling a researcher something the code does not do. Nothing crashed,
every one of the 7,469 tests passed, and the claim inventory passed
too -- because
what those checks ask is whether a page's ARITHMETIC adds up, and what
these six sentences got wrong is what the arithmetic is ABOUT.

This repository's charter puts such a sentence level with a crash: "a
twin that misstates what it carries fails the product's one job even when
nothing crashes -- and a sentence claiming more than the built phase
carries fails it the same way, because the reader acts on the sentence."
So each finding gets a test here, and each test is built the same way:

1. MEASURE the thing the sentence is about, by running the real command
   on a table built in the test's own folder. The expectation is then
   derived from the rule, never copied off the new output.
2. ASSERT that the page says what the measurement supports, and does NOT
   say the wording the review found. Both halves matter: deleting a
   sentence passes a ban and leaves a reader with nothing, which this
   repository treats as the worse of the two failures.

WHAT EACH ONE FAILS ON. Every test below is red on the exact wording that
shipped, and the docstring names it, so a later change that puts the old
promise back turns this file red rather than passing quietly:

  finding 5   README promised "every rollup of that column reproduces
              exactly" of a `--code` column, unqualified by the floor.
  finding 6   the population notice said "Every count here is a count
              over that population" where the population is people and
              the counts are rows.
  finding 7   the summary announced "Real smallest and largest values",
              the quality report promised "the smallest and largest
              exactly", the twin's report said all "nine steps between
              its smallest and its largest value" were measured, three
              answer choices promised "a smallest and a largest", and a
              bounded tail said its values "are not published" two lines
              above listing them.
  finding 8   the summary, README and SECURITY called a folded spelling
              count an original spelling count -- "only where 11 rows or
              more wrote it that way".
  finding 9   the quality report said "a group fewer than 11 rows carry
              is named in no description written under it", beside an
              accepted exception that publishes exactly such a count.
  finding 10  the handling notices, README and the quality report counted
              five files where a full run leaves six. The guard for that
              one is in `tests/test_claim_inventory.py`, whose derived
              totals now read the four forms that got past them; what is
              here is the run-driven half.

WHY THE TEXT CHECKS ARE PHRASES AND NOT DIGESTS. A digest over a page
turns red when anybody rewraps a paragraph and says nothing about what
changed. What is asserted here is the load-bearing CLAUSE -- the words
that make the claim true or false -- so the message names the claim a
maintainer has to keep rather than a hash they have to re-bless.
"""

import csv
import io
import contextlib
import json
import pathlib

import fixtures
from synthtwin import asking, cli, contract, parsing, taxonomy


def _table(folder: pathlib.Path, header: "list[str]", rows: "list[list[str]]") -> str:
    """One table written into this test's own folder, as a path string."""
    return f"{fixtures.write(folder, 'table.csv', fixtures.rows_to_csv(header, rows))}"


def _run(*words: str) -> "tuple[int, str]":
    """One command, with its screen captured.

    `capsys` would do as well; a local capture keeps a test that runs
    three commands from interleaving three screens into one fixture.
    """
    spoken = io.StringIO()
    with contextlib.redirect_stdout(spoken), contextlib.redirect_stderr(spoken):
        code = cli.main(list(words))
    return code, spoken.getvalue()


def _flat(text: str) -> str:
    """One page as its sentences read, lowercased and unwrapped."""
    return " ".join(text.lower().split())


def _says(page: str, phrase: str) -> bool:
    """Whether one page carries one clause, however it was wrapped."""
    return _flat(phrase) in _flat(page)


def test_the_code_promise_is_bounded_by_what_survives_the_floor(
    tmp_path: pathlib.Path,
) -> None:
    """`--code` may not promise a rollup the floor does not leave named.

    THE SENTENCE (finding 5). "because it holds the same codes the same
    number of times, **every rollup of that column reproduces exactly**
    -- the prefix a hierarchy groups by, the segment a reader splits on,
    the length." That is true of the codes a description PUBLISHES and of
    no others, and the default floor is where the difference lives: the
    columns `--code` exists for are the ones whose codes repeat least.

    MEASURED HERE rather than asserted: a column of 100 codes, one row
    each, at the default floor. Every level is pooled, so the description
    names no code at all and the twin's prefixes are its own invention.
    The test does not hard-code either number -- it reads the published
    levels and counts the twin's rows -- so a later landing that makes
    pooling keep a prefix moves this test's own evidence with it.
    """
    codes = [[f"{1000 + index}"] for index in range(parsing.POPULATION_FLOOR)]
    table = _table(tmp_path, ["proc_code"], codes)
    assert _run("profile", table, "--code", "proc_code")[0] == 0
    document = json.loads(
        (tmp_path / "table-profile.json").read_text(encoding="utf-8")
    )
    published = document["columns"][0].get("levels") or []
    assert not published, (
        "this shape no longer pools every code, so the measurement this "
        "test rests on has moved: re-measure the README's rollup claim "
        f"against what a floor of {document['settings']['small_cell_floor']} "
        f"leaves named ({len(published)} level(s) published)."
    )
    assert _run("generate", f"{tmp_path / 'table-profile.json'}", "--seed", "4")[0] == 0
    with (tmp_path / "table-twin.csv").open(encoding="utf-8") as handle:
        twin = list(csv.reader(handle))[1:]
    source_prefix = sum(1 for row in codes if row[0].startswith("10"))
    twin_prefix = sum(1 for row in twin if row[0].startswith("10"))
    assert twin_prefix != source_prefix, (
        "the twin now reproduces the prefix rollup of a column whose "
        "codes were all pooled, which would make the unqualified README "
        "promise true again. Re-read it before changing this test: "
        f"{twin_prefix} twin rows carry '10' against {source_prefix}."
    )
    readme = (fixtures.REPO_ROOT / "README.md").read_text(encoding="utf-8")
    assert not _says(readme, "every rollup of that column reproduces exactly"), (
        "README.md promises that EVERY rollup of a --code column "
        f"reproduces exactly. Measured on {len(codes)} codes of one row "
        f"each at the default floor: no code is published and {twin_prefix} "
        f"twin rows carry the prefix '10' against {source_prefix} in the "
        "source. Qualify the promise by the codes the floor leaves named."
    )
    for clause in (
        "a rollup over the codes the description PUBLISHES reproduces exactly",
        "a code fewer than `--smallest-group` rows share is counted into a "
        "pooled remainder",
    ):
        assert _says(readme, clause), (
            f"README.md no longer says {clause!r}. The rollup promise is "
            "only true of the published codes, and a reader who is not "
            "told where it stops will count on the twin and be wrong."
        )


def test_every_page_explaining_the_floor_names_the_unit_each_one_counts(
    tmp_path: pathlib.Path,
) -> None:
    """The size is counted in people; the disclosure floor counts rows.

    THE SENTENCES (finding 6). The population notice said "Every count
    here is a count over that population" -- where the population is
    people and every count is rows. Beside it, three pages said the usual
    eleven keeps a group from pointing at one person. Plan P4-D348
    accepts the opposite, and the owner accepted it knowingly, so the
    repair is to state the unit of each floor wherever either is
    explained.

    MEASURED HERE: a hundred declared people of twelve visits each, one
    of whom holds a value nobody else does. The value is published with
    the count of that person's ROWS at the default floor -- the test
    reads the count off the description and checks it against the visits
    per person rather than against the number 12 -- while the population
    notice above it counts the table in people.
    """
    visits = 12
    people = 100
    rows = [
        [f"P{person:03d}", f"{visit}", "lone" if person == 0 else "common"]
        for person in range(people)
        for visit in range(visits)
    ]
    table = _table(tmp_path, ["patient", "visit", "grade"], rows)
    assert _run("profile", table, "--identifier", "patient")[0] == 0
    document = json.loads(
        (tmp_path / "table-profile.json").read_text(encoding="utf-8")
    )
    assert document["settings"]["person_columns"] == ["patient"], (
        "the population is no longer counted in people on this shape, so "
        "the two units this test is about are not both in play."
    )
    counts = {
        level["label"]: level["count"]
        for column in document["columns"]
        for level in (column.get("levels") or [])
    }
    assert counts.get("lone") == visits, (
        "one person's own value is no longer published with the count of "
        f"their rows ({counts.get('lone')!r} against {visits} visits), so "
        "re-measure P4-D348 before trusting the sentences below."
    )
    # AND THE COUNT CLEARS THE FLOOR, which is the whole of P4-D348: the
    # floor counts rows, one person holds this many of them, so nothing
    # holds the value back.
    floor = document["settings"]["small_cell_floor"]
    assert counts["lone"] >= floor, (
        f"one person's {visits} visits no longer clear a floor of {floor}, "
        "so this shape does not exercise the limit the sentences below "
        "have to state."
    )
    summary = (tmp_path / "table-profile.txt").read_text(encoding="utf-8")
    assert not _says(summary, "every count here is a count over that population"), (
        "the population notice still says every count is a count over the "
        f"population, which this description counts in people ({people}) "
        f"while its counts are rows: 'lone' publishes {counts['lone']}. Say "
        "which unit each number is in."
    )
    assert _says(summary, "every count here is a count of ROWS over that population"), (
        "the population notice no longer names the unit of its counts. A "
        "reader who takes them for people reads one patient's twelve "
        "visits as twelve patients."
    )
    assert _says(summary, f"a table of {people} people"), (
        "the notice no longer says the size is counted in people, which is "
        "the other half of the same sentence."
    )
    assert _run("generate", f"{tmp_path / 'table-profile.json'}")[0] == 0
    assert _run("validate", f"{tmp_path / 'table-profile.json'}")[0] in (0, 3)
    quality = (tmp_path / "table-twin-quality.txt").read_text(encoding="utf-8")
    assert _says(quality, "the floor counts ROWS, not"), (
        "the quality report's floor section no longer says the floor "
        "counts rows, so the blanket person protection it used to imply is "
        "back by omission."
    )
    assert _says(
        quality, "The size of the table is the one number counted in people"
    ), "the quality report no longer names the floor that IS counted in people."


def test_no_page_promises_an_end_or_a_check_stage_3_took_away(
    tmp_path: pathlib.Path,
) -> None:
    """Four pages and three answer choices, measured against the ladder.

    THE SENTENCES (finding 7). On a continuous column the description
    withholds both ends and the rungs nearest them. The pages went on
    announcing "Real smallest and largest values" (the summary),
    promising "the smallest and largest exactly" (the quality report's
    expectations section), reporting that all "nine steps between its
    smallest and its largest value" were measured (the twin's report),
    and offering "a smallest and a largest" as what an answer would
    publish (the measurement, joined-number and decimal-comma choices).

    AND THE INVERSE ERROR sat beside them: a bounded tail opened "the 12
    smallest values are not published" and then, two lines down, named
    which values they are.

    MEASURED HERE: the withheld rungs are read off the description, so
    the claim "both ends and some interior rungs are withheld" is this
    run's own measurement and not a number copied from the review.
    """
    rows = [[f"{index + 0.125}"] for index in range(parsing.POPULATION_FLOOR)]
    table = _table(tmp_path, ["reading"], rows)
    assert _run("profile", table, "--measurement", "reading")[0] == 0
    document = json.loads(
        (tmp_path / "table-profile.json").read_text(encoding="utf-8")
    )
    rungs = document["columns"][0]["percentiles"]
    withheld = sorted(name for name in rungs if rungs[name] is None)
    assert {"min", "max"} <= set(withheld), (
        "this column now publishes an end, so the pages below may say so. "
        f"Withheld: {withheld}."
    )
    interior = [name for name in withheld if name not in ("min", "max")]
    assert interior, (
        "no interior rung is withheld on this column any more, so the "
        "twin's report may again say all nine steps were measured."
    )
    assert _run("generate", f"{tmp_path / 'table-profile.json'}")[0] == 0
    assert _run("validate", f"{tmp_path / 'table-profile.json'}")[0] in (0, 3)
    pages = {
        "the plain-language summary": tmp_path / "table-profile.txt",
        "the twin's report": tmp_path / "table-twin-report.txt",
        "the quality report": tmp_path / "table-twin-quality.txt",
    }
    retired = (
        "real smallest and largest values",
        "the smallest and largest exactly",
        "the nine steps between its smallest and its largest value",
    )
    standing = [
        f"{what}: {clause!r}"
        for what, path in pages.items()
        for clause in retired
        if _says(path.read_text(encoding="utf-8"), clause)
    ]
    assert not standing, (
        "these pages promise an end or a ladder check the description "
        f"does not carry -- it withholds {withheld} on this column:\n  "
        + "\n  ".join(standing)
    )
    for answer in (
        asking.ANSWER_MEASUREMENT,
        asking.ANSWER_JOINED,
        asking.ANSWER_DECIMAL_COMMA,
    ):
        shown = asking._publishes_under(
            answer, taxonomy.ROLE_CONTINUOUS, contract.DEFAULT_SMALL_CELL_FLOOR
        )
        assert "a smallest and a largest" not in shown, (
            f"the {answer!r} choice still offers a smallest and a largest, "
            "which a description written after stage 3 does not publish. "
            "The person answering the question is deciding on this "
            f"sentence: {shown!r}"
        )
        assert "end" in shown, (
            f"the {answer!r} choice no longer says anything about the ends "
            f"at all, which tells the person less than the old promise: "
            f"{shown!r}"
        )
    # THE INVERSE ERROR, on a bounded scale whose tail names its values.
    bounded = tmp_path / "bounded"
    bounded.mkdir()
    scale = [[f"{index % 7}"] for index in range(parsing.POPULATION_FLOOR + 20)]
    assert _run("profile", _table(bounded, ["pain"], scale))[0] == 0
    described = json.loads(
        (bounded / "table-profile.json").read_text(encoding="utf-8")
    )
    tails = described["columns"][0]["tails"]
    assert tails and tails["low"]["values"], (
        "this bounded scale's tail no longer names its values, so the "
        "sentence pair this half of the test is about cannot arise."
    )
    lines = (bounded / "table-profile.txt").read_text(encoding="utf-8").splitlines()
    opening = [one for one in lines if "smallest values are not published" in one]
    listing = [one for one in lines if "the values that end lies on" in one]
    assert listing, "the tail no longer lists the values it holds on this page."
    assert not [one for one in opening if "one by one" not in one], (
        "the summary says this tail's values 'are not published' and then "
        f"lists them:\n  {opening}\n  {listing}"
    )


def test_a_folded_spelling_count_is_not_described_as_an_original_count(
    tmp_path: pathlib.Path,
) -> None:
    """The number beside a spelling covers the rows folded into it.

    THE SENTENCES (finding 8). The summary said the profile records "the
    exact spellings your file uses for it -- capitals and spacing
    included -- again only where 11 rows or more wrote it that way", and
    README and SECURITY promised the same. Ruling 6 of 2026-09-17 counts
    a sub-floor spelling into the label's COMMONEST spelling instead, so
    the number beside a named spelling is not a count of that spelling
    and `variants_withheld` comes back empty at every floor above one.

    MEASURED HERE: four labels, each written three ways, none of the
    three often enough to be named on its own. The test reads the biggest
    original spelling count off its own table and checks it against the
    floor, so the evidence is the rule's and not the review's.
    """
    rows: "list[list[str]]" = []
    ways = {"lower": 9, "upper": 8, "spaced": 8}
    for label in ("alpha", "beta", "gamma", "delta"):
        rows += [[label] for _ in range(ways["lower"])]
        rows += [[label.upper()] for _ in range(ways["upper"])]
        rows += [[f" {label}"] for _ in range(ways["spaced"])]
    assert len(rows) >= parsing.POPULATION_FLOOR, (
        "the table this test builds fell under the population floor, so "
        "`synthtwin profile` would write nothing to read."
    )
    assert _run("profile", _table(tmp_path, ["grade"], rows))[0] == 0
    document = json.loads(
        (tmp_path / "table-profile.json").read_text(encoding="utf-8")
    )
    floor = document["settings"]["small_cell_floor"]
    assert max(ways.values()) < floor, (
        "no original spelling of this table is under the floor any more, "
        "so the folding this test is about does not happen."
    )
    folded: "list[int]" = []
    for column in document["columns"]:
        for level in column.get("levels") or []:
            assert not level["variants_withheld"], (
                "`variants_withheld` carries an entry again, so the "
                "absorption rule has changed and SECURITY's corrected "
                f"paragraph has to be re-measured: {level}"
            )
            for spelling in level["variants"]:
                folded += [level["variants"][spelling]]
    assert folded and max(folded) > max(ways.values()), (
        "no published spelling carries more rows than any one spelling of "
        f"the file wrote ({folded} against {ways}), so the count beside a "
        "spelling is not a folded count on this shape."
    )
    summary = (tmp_path / "table-profile.txt").read_text(encoding="utf-8")
    assert not _says(summary, f"only where {floor} rows or more wrote it that way"), (
        "the summary still says a named spelling is one that the floor's "
        f"own number of rows wrote that way. Measured: a spelling counted "
        f"{max(folded)} where the commonest spelling of the file was "
        f"written {max(ways.values())} times."
    )
    assert _says(summary, "with how many rows are counted into"), (
        "the summary no longer says what the number beside a spelling "
        "counts, which is the whole of the repair."
    )
    for relative, retired, kept in (
        (
            "README.md",
            "the exact spellings your file used for it together with how "
            "many rows wrote it that way",
            "That number is not a count of that spelling",
        ),
        (
            "SECURITY.md",
            "a spelling fewer rows than the floor wrote is withheld and "
            "counted into `variants_withheld`",
            "the number beside a named spelling is not a count of that "
            "spelling",
        ),
    ):
        page = (fixtures.REPO_ROOT / relative).read_text(encoding="utf-8")
        assert not _says(page, retired), (
            f"{relative} still says {retired!r}, and the producer folds "
            "a sub-floor spelling into the commonest instead."
        )
        assert _says(page, kept), (
            f"{relative} no longer says {kept!r}, so a reader is left with "
            "a count they will read as a count of one spelling."
        )


def test_the_floor_is_described_with_its_scope_and_its_exceptions(
    tmp_path: pathlib.Path,
) -> None:
    """The floor governs naming a VALUE, and the pages say so.

    THE SENTENCE (finding 9). The quality report said "a group fewer than
    11 rows carry is named in no description written under it -- that is
    what a floor is for -- so a count of it is not something a
    description of this file carries either". The owner has accepted
    counts that break it, and the simplest is measured here: 99 decimal
    cells beside one word publish `n_not_numeric` 1 and a remark carrying
    that 1. A count of cells BY KIND names no value of anybody's, which
    is why it is allowed -- and a blanket assurance beside an accepted
    exception is what this repository treats as equal to a crash.

    MEASURED HERE: the count and the remark are read off the description,
    and the test asserts the count is under the floor rather than
    asserting it is 1.
    """
    rows = [[f"{index / 4:.2f}"] for index in range(parsing.POPULATION_FLOOR - 1)]
    rows += [["pending"]]
    assert _run("profile", _table(tmp_path, ["reading"], rows), "--measurement",
                "reading")[0] == 0
    document = json.loads(
        (tmp_path / "table-profile.json").read_text(encoding="utf-8")
    )
    floor = document["settings"]["small_cell_floor"]
    column = document["columns"][0]
    assert 0 < column["n_not_numeric"] < floor, (
        "this column no longer publishes a count of cells under the "
        f"floor ({column['n_not_numeric']} against {floor}), so the "
        "exception the pages have to name is not in play."
    )
    carrying = [
        remark for remark in column["remarks"]
        if f"{column['n_not_numeric']} value(s)" in remark
    ]
    assert carrying, (
        "no remark carries the sub-floor count any more, which is the "
        f"half of the exception a reader meets: {column['remarks']}"
    )
    assert _run("generate", f"{tmp_path / 'table-profile.json'}")[0] == 0
    assert _run("validate", f"{tmp_path / 'table-profile.json'}")[0] in (0, 3)
    quality = (tmp_path / "table-twin-quality.txt").read_text(encoding="utf-8")
    assert not _says(
        quality,
        f"a group fewer than {floor} rows carry is named in no description "
        f"written under it",
    ), (
        "the quality report states the floor as a universal, and this "
        f"very run publishes {column['n_not_numeric']} as a count of "
        f"cells and again inside {carrying[0]!r}."
    )
    assert _says(quality, f"What the floor of {floor} does NOT cover"), (
        "the quality report no longer names the scope of the floor, so "
        "the blanket reading is back by omission."
    )
    assert _says(
        quality,
        "A count of CELLS BY KIND names no value and is published whatever "
        "its size",
    ), "the quality report no longer names the exception this run publishes."
    readme = (fixtures.REPO_ROOT / "README.md").read_text(encoding="utf-8")
    assert not _says(
        readme, "no group named anywhere in the profile covers fewer than eleven rows"
    ), (
        "README.md states the floor as a universal over every group, and "
        "what it governs is the naming of a value."
    )
    assert _says(
        readme, "the floor governs the naming of a VALUE, which is narrower"
    ), "README.md no longer names the scope of the floor."


def test_a_full_run_leaves_six_files_and_no_page_of_it_says_five(
    tmp_path: pathlib.Path,
) -> None:
    """The run's own count, and the pages that state it.

    THE SENTENCES (finding 10). The lowered-floor alarm said "All five
    files of a full run carry them", README opened "three commands
    produce five files", SECURITY said "so all five files carry them",
    and the quality report closed "everything above about keeping these
    five files applies to this one unchanged" -- on a product whose full
    run leaves six. Both claim-inventory guards passed, and the reading
    they rest on is repaired in `tests/test_claim_inventory.py`; this is
    the half that counts what lands on the disk and then reads the pages
    the run itself wrote.
    """
    rows = [
        [fixtures.REGIONS[index % 4], f"{index % 7}"]
        for index in range(parsing.POPULATION_FLOOR + 20)
    ]
    table = pathlib.Path(_table(tmp_path, ["region", "visits"], rows))
    assert _run("profile", f"{table}")[0] == 0
    assert _run("generate", f"{tmp_path / 'table-profile.json'}")[0] == 0
    assert _run("validate", f"{tmp_path / 'table-profile.json'}")[0] in (0, 3)
    left = sorted(
        path.name
        for path in tmp_path.iterdir()
        if path.is_file() and path.name != table.name
    )
    # THE SIX IS DERIVED, not written here: `test_claim_inventory` reads
    # the package's own output names and counts them, and every stale-total
    # sentence in the repository is measured against that number. Writing
    # it again here would be the second copy of a count this repository has
    # watched go stale more than once.
    from test_claim_inventory import FILE_TOTAL

    assert len(left) == FILE_TOTAL, (
        f"a full run leaves {len(left)} files ({left}) and the package's "
        f"own output names count {FILE_TOTAL}. One of the two is what "
        "every handling sentence here is measured against, and the "
        "message in test_claim_inventory says which."
    )
    # THE ALARM, on a run that lowered the floor -- it is the one notice
    # the count was wrong in, and it is shown before any file exists.
    lowered = tmp_path / "lowered"
    lowered.mkdir()
    code, screen = _run(
        "profile", _table(lowered, ["region", "visits"], rows),
        "--smallest-group", "2",
    )
    assert code == 0
    assert not _says(screen, "all five files of a full run carry them"), (
        f"the lowered-floor alarm counts five files where a run leaves "
        f"{len(left)}: {left}"
    )
    assert _says(screen, "All six files of a full run carry them"), (
        "the lowered-floor alarm no longer says where the counts go, "
        "which is the paragraph a person acts on."
    )
    assert _says(
        screen,
        "the summary, the twin's report and the quality report each say on "
        "their own face",
    ), (
        "the alarm no longer names the pages that stamp themselves. It "
        "used to count four of them, and three say it in words."
    )
    quality = (tmp_path / "table-twin-quality.txt").read_text(encoding="utf-8")
    assert not _says(quality, "these five files applies to this one unchanged"), (
        "the quality report's withholding section still counts five files."
    )
    assert _says(quality, "the six files a full run leaves applies to this one"), (
        "the quality report no longer says the handling rule covers this "
        "page too, which is the claim the sentence exists to make."
    )


def test_the_charter_and_the_front_page_agree_on_the_file_count() -> None:
    """One fact, one place: the two documents a reader starts from.

    CLAUDE.md already counted six when the review ran; README counted
    five on its own opening line, which is the first sentence anybody
    reads. This holds them to each other rather than to a number written
    here, so the pair cannot drift again in one direction only.
    """
    charter = (fixtures.REPO_ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    readme = (fixtures.REPO_ROOT / "README.md").read_text(encoding="utf-8")
    assert _says(charter, "All six files a full run leaves behind"), (
        "CLAUDE.md no longer states the file count it is the source of."
    )
    assert not _says(readme, "three commands produce five files"), (
        "README.md's opening line counts five files where the charter "
        "counts six."
    )
    assert _says(
        readme, "three commands produce the six files a full run leaves behind"
    ), "README.md's opening line no longer states the count at all."
