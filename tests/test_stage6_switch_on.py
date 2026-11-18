"""The switch on: the landing that ships stage 6 (lane CHON, plan P4-D464).

The shipped command is switched: `synthtwin profile` describes between
columns behind the installation's key, record and lock (contract 4.6b.4),
`generate` loads the chain and `validate` measures it; a description whose
`statistical` and `grain` are null generates and validates exactly as
before. Every table here is invented and small (a test device: the owner's
floor of 20,000 rows governs what is judged, and the checks at that size run in
`tools/measurements/kpi_chain_shipped.py` under `kpi_run --slow`). The data
folder is each test's own (tests/conftest.py's `installation_folder`),
holding the fixed test key.

Each case names its mutant; each mutant was run red once (P4-D464):
- the switch off by default (`main` unswitched where no chain is given);
- generate loading without the chain;
- a writer splicing `statistical` alone with the rules on;
- a hold dropped (the subject question unanswered and a chain drawn);
- a refusal's words written into a file;
- the private report beside the twin;
- a new key left by a refused run;
- the size guard removed;
- the degraded chain dropped (no chain above the guard) or the whole chain drawn above it;
- the degraded chain's pairs taken from the weakest up;
- the base's abbreviations of `--replace` left to argparse;
- the null path's twin graded on every load;
- the summary page reading an empty tail's boundary (a computed date column);
- the zoo's engine leaving the subject question open, or ending its walk at
  the record's refusal, or walking in its caller's data folder; the
  drivers' guard leaving the data folder where it was; a named driver's
  profile run without a data folder of its own (repair 2).
"""

import hashlib
import json
import os
import pathlib
import random
import sys

import pytest

import fixtures
from synthtwin import asking, chain, cli, contract, installation, profile, results

FLOOR = 11


# -- the invented tables ----------------------------------------------------


def _clinic_text(rows: int, seed: int = 7) -> str:
    """An invented clinic: an age, a gender, a group that follows age, a pressure that follows age, an event."""
    draw = random.Random(seed)
    lines = ["age,gender,group,pressure,event"]
    for _row in range(rows):
        age = draw.randint(18, 88)
        gender = draw.choice(["f", "m"])
        group = draw.choice(["a", "b", "c"]) if age < 50 else draw.choice(["c", "d"])
        pressure = f"{round(100 + age * 0.5 + draw.gauss(0, 8), 1)}"
        event = "1" if draw.random() < 0.05 + age / 120 else "0"
        lines += [f"{age},{gender},{group},{pressure},{event}"]
    return "\n".join(lines) + "\n"


def _clinic(folder: pathlib.Path, rows: int = 1200, name: str = "clinic", seed: int = 7) -> pathlib.Path:
    folder.mkdir(parents=True, exist_ok=True)
    return fixtures.write(folder, f"{name}.csv", _clinic_text(rows, seed))


def _ran(argv: "list[str]", **named: object) -> "tuple[results.Result, str]":
    """One command line through `cli.run`, and every character its screen showed."""
    screen: "list[tuple[str, str]]" = []
    made = cli.run(argv, screen=screen, **named)  # type: ignore[arg-type]
    return made, "".join(text for _stream, text in screen)


def _answered(questions: pathlib.Path, answer: str = asking.ANSWER_ONE_ROW_EACH) -> pathlib.Path:
    """The questions file with the subject question answered."""
    document = json.loads(questions.read_text(encoding="utf-8"))
    document[asking.BETWEEN_COLUMNS][asking.ROWS_PER_PERSON]["your_answer"] = answer
    questions.write_text(json.dumps(document, indent=1) + "\n", encoding="utf-8", newline="\n")
    return questions


def _chained(folder: pathlib.Path, rows: int = 1200, extra: "tuple[str, ...]" = ()) -> "tuple[pathlib.Path, pathlib.Path]":
    """The clinic described by the shipped command over two rounds, the second with the subject question answered."""
    table = _clinic(folder, rows)
    first, said = _ran(["profile", str(table)])
    assert first.verdict == results.NO_MISS, said[-2000:]
    _answered(folder / "clinic-questions.json")
    second, said = _ran(
        ["profile", str(table), "--answers", str(folder / "clinic-questions.json"), "--replace-description", *extra]
    )
    assert second.verdict == results.NO_MISS, said[-2000:]
    return table, folder / "clinic-profile.json"


def _statistical(path: pathlib.Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))["relationships"]["statistical"]


# -- (i) THE SHIPPED COMMAND IS SWITCHED -------------------------------------


def test_the_shipped_profile_holds_the_chain_until_the_subject_question_is_answered(tmp_path: pathlib.Path) -> None:
    """Round 1 publishes nothing between columns and names the question and its file; round 2 draws the chain.

    MUTANTS: the switch off by default (no `between_columns` entry, no
    record); a hold dropped (a chain drawn in round 1).
    """
    table = _clinic(tmp_path)
    first, said = _ran(["profile", str(table)])
    assert first.verdict == results.NO_MISS, said[-2000:]
    assert _statistical(tmp_path / "clinic-profile.json") is None
    questions = tmp_path / "clinic-questions.json"
    asked = json.loads(questions.read_text(encoding="utf-8"))
    assert asking.ROWS_PER_PERSON in asked[asking.BETWEEN_COLUMNS]
    assert cli._hold_paragraph(cli._WAITS_FOR_SUBJECT, cli._shown(questions)).strip() in said
    assert "Between columns: 0 of the" not in said and "no family table is published" not in said
    # The record holds the run's entry, nothing between columns.
    record = json.loads((installation.data_folder() / installation.LEDGER_FILE).read_text(encoding="utf-8"))
    assert [entry["between"] for entry in record["tables"]] == [False]
    _answered(questions)
    second, said = _ran(["profile", str(table), "--answers", str(questions), "--replace-description"])
    assert second.verdict == results.NO_MISS, said[-2000:]
    statistical = _statistical(tmp_path / "clinic-profile.json")
    assert isinstance(statistical, dict) and statistical["chain"], said[-2000:]
    assert "share a family table and are carried exactly" in said


def test_the_shipped_questions_file_offers_the_record_answer(tmp_path: pathlib.Path) -> None:
    """GRa's hold shipped: a repeating record number's question offers `record` beside `identifier`.

    MUTANT: the record answer behind the switch alone (`asking.with_the_record_answer` not called).
    """
    draw = random.Random(5)
    lines = ["pid,weight,ward"]
    for row in range(1600):
        lines += [f"P{1000 + row % 400},{round(draw.gauss(70, 9), 1)},{draw.choice(['north', 'south'])}"]
    folder = tmp_path / "visits"
    folder.mkdir()
    table = fixtures.write(folder, "visits.csv", "\n".join(lines) + "\n")
    made, said = _ran(["profile", str(table)])
    assert made.verdict == results.NO_MISS, said[-2000:]
    asked = json.loads((folder / "visits-questions.json").read_text(encoding="utf-8"))["asked"]
    offered = [answer["answer"] for entry in asked if entry["column"] == "pid" for answer in entry["answers_you_can_give"]]
    assert asking.ANSWER_RECORD in offered and asking.ANSWER_IDENTIFIER in offered, offered
    assert _statistical(folder / "visits-profile.json") is None


def test_generate_and_validate_read_the_chain_the_shipped_profile_wrote(tmp_path: pathlib.Path) -> None:
    """The twin of a chained description is dealt by its chain and measured with V12's lines.

    MUTANT: generate loading without the chain (S12 refuses the
    description: exit 1 and no twin).
    """
    _table, described = _chained(tmp_path)
    made, said = _ran(["generate", str(described)])
    assert made.verdict in (results.NO_MISS, results.MISSED), said[-2000:]
    report = (tmp_path / "clinic-twin-report.txt").read_text(encoding="utf-8")
    from synthtwin import chain_grades, rendering

    assert rendering.CHAINED_HEADING in report and "THREE THINGS THAT ARE TRUE" not in report
    assert chain_grades.HEADING in report
    assert [one.reason for one in made.carried if one.subject == ()] == []
    checked, said = _ran(["validate", str(described)])
    assert checked.verdict in (results.NO_MISS, results.MISSED), said[-2000:]
    quality = (tmp_path / "clinic-twin-quality.txt").read_text(encoding="utf-8")
    assert "V12" in quality or "between columns" in quality.lower()


# -- (ii) THE NULL PATH ------------------------------------------------------


def test_a_description_publishing_nothing_between_columns_generates_and_validates_as_before(tmp_path: pathlib.Path) -> None:
    """A description the base wrote (statistical null): the switched generate and validate write its bytes as the unswitched ones.

    The base's path is the internal `unswitched` setting (the loader of S12
    word for word, no installation). MUTANT: the twin's report graded every
    family N on such a description (`switched` read on every load).
    """
    table = _clinic(tmp_path / "in")
    made, said = _ran(["profile", str(table), "--out-dir", str(tmp_path / "in")], unswitched=True)
    assert made.verdict == results.NO_MISS, said[-2000:]
    described = tmp_path / "in" / "clinic-profile.json"
    assert _statistical(described) is None
    outputs = {}
    for label, setting in (("on", False), ("off", True)):
        folder = tmp_path / label
        folder.mkdir()
        built, said = _ran(["generate", str(described), "--out-dir", str(folder)], unswitched=setting)
        assert built.verdict in (results.NO_MISS, results.MISSED), said[-2000:]
        checked, said = _ran(
            ["validate", str(described), "--twin", str(folder / "clinic-twin.csv"), "--out-dir", str(folder)],
            unswitched=setting,
        )
        outputs[label] = (
            (folder / "clinic-twin.csv").read_bytes(),
            (folder / "clinic-twin-report.txt").read_bytes(),
            (folder / "clinic-twin-quality.txt").read_bytes(),
            results.exit_code(checked),
            [(one.subject, one.reason) for one in built.carried],
        )
    assert outputs["on"] == outputs["off"]
    assert b"THREE THINGS THAT ARE TRUE OF EVERY TWIN THIS VERSION BUILDS" in outputs["on"][1]


# -- (iii) ONE PATH ----------------------------------------------------------


def test_the_shipped_description_is_the_library_s_under_the_fixed_key(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The bytes the shipped command writes are `chain.with_rules(document, chain.describe(...))` of what it handed the chain.

    MUTANT: a writer splicing `statistical` alone (the computed columns'
    blocks lost where a rule is carried): red on the rule table below.
    """
    handed: "list[tuple[object, ...]]" = []
    real = chain.describe

    def kept(*given: object, **named: object) -> chain.Chained:
        nonlocal handed
        handed += [(given, named)]
        return real(*given, **named)  # type: ignore[arg-type]

    monkeypatch.setattr(chain, "describe", kept)
    _table, described = _chained(tmp_path / "rule", 1500)
    given, named = handed[len(handed) - 1]
    switch = given[3]
    assert isinstance(switch, chain.ChainSwitch)
    assert switch.key == bytes(range(32)) and switch.rules and not switch.patient_layer
    document = json.loads(json.dumps(given[1]))
    library = chain.with_rules(document, real(given[0], document, given[2], switch, *given[4:], **named))  # type: ignore[arg-type]
    assert profile.serialize(library) == described.read_text(encoding="utf-8")


def test_a_rule_the_shipped_run_carries_writes_its_computed_column(tmp_path: pathlib.Path) -> None:
    """A table whose stay is its last day less its first: the shipped run carries the rule and writes the computed block.

    MUTANT: the shipped switch asking for no rule steps (`_shipped_chain`
    with rules False): no rule written.
    """
    draw = random.Random(11)
    lines = ["first_day,last_day,stay,ward"]
    for _row in range(1500):
        first = draw.randint(1, 300)
        stay = draw.randint(0, 20)
        lines += [f"{first},{first + stay},{stay},{draw.choice(['north', 'south', 'east'])}"]
    folder = tmp_path / "stays"
    folder.mkdir()
    table = fixtures.write(folder, "stays.csv", "\n".join(lines) + "\n")
    first, said = _ran(["profile", str(table)])
    assert first.verdict == results.NO_MISS, said[-2000:]
    _answered(folder / "stays-questions.json")
    second, said = _ran(["profile", str(table), "--answers", str(folder / "stays-questions.json"), "--replace-description"])
    assert second.verdict == results.NO_MISS, said[-2000:]
    statistical = _statistical(folder / "stays-profile.json")
    assert isinstance(statistical, dict)
    assert statistical["rules"], statistical["rules"]
    contract.load_profile(str(folder / "stays-profile.json"))


def test_a_date_column_a_carried_rule_computes_is_summarised_and_built(tmp_path: pathlib.Path) -> None:
    """A day out never before the day in: the rule computes the second date, and the run writes every file.

    The computed column's block publishes no value of its own (contract
    4.6b.7), so both its tails are empty; the summary page says so in
    place of the boundaries, and `generate` and `validate` read it. Found
    by the health data zoo's walk at 20,000 rows (two exports stopped on
    the summary page before this landing's repair).

    MUTANT: the summary page reading an empty tail's boundary (the run
    stops with a KeyError).
    """
    draw = random.Random(3)
    lines = ["admitted,went_home,ward"]
    for _row in range(400):
        day_in = 1 + draw.randint(0, 360)
        day_out = day_in + draw.randint(0, 9)
        lines += [f"2024-{_month_day(day_in)},2024-{_month_day(day_out)},{draw.choice(['north', 'south', 'east'])}"]
    folder = tmp_path / "days"
    folder.mkdir()
    table = fixtures.write(folder, "days.csv", "\n".join(lines) + "\n")
    first, said = _ran(["profile", str(table)])
    assert first.verdict == results.NO_MISS, said[-2000:]
    _answered(folder / "days-questions.json")
    second, said = _ran(["profile", str(table), "--answers", str(folder / "days-questions.json"), "--replace-description"])
    assert second.verdict == results.NO_MISS, said[-2000:]
    statistical = _statistical(folder / "days-profile.json")
    assert isinstance(statistical, dict)
    assert [(rule["kind"], rule["computed"]) for rule in statistical["rules"]] == [("order", "went_home")]
    summary = (folder / "days-profile.txt").read_text(encoding="utf-8")
    assert "written in the twin by a rule this description carries" in summary
    built, said = _ran(["generate", str(folder / "days-profile.json")])
    assert built.verdict in (results.NO_MISS, results.MISSED), said[-2000:]
    assert (folder / "days-twin.csv").is_file()
    checked, said = _ran(["validate", str(folder / "days-profile.json"), "--twin", str(folder / "days-twin.csv")])
    assert checked.verdict in (results.NO_MISS, results.MISSED), said[-2000:]


def _month_day(day: int) -> str:
    """The 2024 date of a day of the year 1 to 370, as MM-DD (days past the year's end kept in December)."""
    ends = (31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
    day = min(day, 366)
    month = 0
    while day > ends[month]:
        day = day - ends[month]
        month = month + 1
    return f"{month + 1:02d}-{day:02d}"


# -- (iv) 4.6b.4'S DECISIONS AND THE LOCK, THROUGH main ----------------------


def _quiet_files(folder: pathlib.Path) -> "dict[str, bytes]":
    return {f"{path.relative_to(folder)}": path.read_bytes() for path in sorted(folder.rglob("*")) if path.is_file()}


def test_the_record_s_decisions_and_the_lock_in_the_contract_s_words(tmp_path: pathlib.Path) -> None:
    """4.6b.4 through `cli.run`: each refusal in its words, exit 1, nothing written; the warning; the lock.

    MUTANT: a refusal's words written into a file (every file of the
    output and data folders is read for them).
    """
    data = installation.data_folder()
    table, described = _chained(tmp_path / "a")
    folder = tmp_path / "a"
    before = _quiet_files(folder)
    # The same table, name and key, another description: refused, nothing written.
    questions = folder / "clinic-questions.json"
    again, said = _ran(["profile", str(table), "--answers", str(questions), "--smallest-group", "12"])
    assert again.verdict == results.REFUSED and results.exit_code(again) == 1, said[-2000:]
    assert installation.words_changed("clinic") in said
    words_said = [installation.words_changed("clinic")]
    assert _quiet_files(folder) == before
    # The same content under another name: refused.
    renamed, said = _ran(["profile", str(table), "--answers", str(questions), "--name", "other"])
    assert renamed.verdict == results.REFUSED and results.exit_code(renamed) == 1
    assert installation.words_other_name("clinic") in said
    words_said += [installation.words_other_name("clinic")]
    # A different table under a name already used: one warning, and the run goes on.
    other = _clinic(tmp_path / "b", 1100, name="clinic", seed=9)
    warned, said = _ran(["profile", str(other)])
    assert warned.verdict == results.NO_MISS and installation.words_name_reused("clinic") in said
    words_said += [installation.words_name_reused("clinic")]
    # Another key: refused; with --replace-description, it proceeds.
    key = installation.key_path(data)
    kept = key.read_bytes()
    key.write_bytes(bytes(reversed(range(32))))
    keyed, said = _ran(["profile", str(table), "--answers", str(questions), "--replace"])
    assert keyed.verdict == results.REFUSED and results.exit_code(keyed) == 1
    assert installation.words_other_key(f"{key}") in said
    words_said += [installation.words_other_key(f"{key}")]
    key.write_bytes(kept)
    # The lock: another run holds it.
    lock = data / installation.LOCK_FILE
    lock.touch()
    locked, said = _ran(["profile", str(table), "--answers", str(questions), "--replace-description"])
    assert locked.verdict == results.REFUSED and results.exit_code(locked) == 1
    assert installation.words_locked(f"{lock}") in said
    words_said += [installation.words_locked(f"{lock}")]
    lock.unlink()
    # A record standing without its key: refused; --new-key makes one, and the table is refused until confirmed.
    key.unlink()
    missing, said = _ran(["profile", str(table), "--answers", str(questions), "--replace-description"])
    assert missing.verdict == results.REFUSED and installation.words_key_missing(f"{key}") in said
    words_said += [installation.words_key_missing(f"{key}")]
    made, said = _ran(["profile", str(table), "--answers", str(questions), "--new-key", "--replace-description"])
    assert made.verdict == results.NO_MISS, said[-2000:]
    assert installation.words_key_made(f"{key}") in said and key.read_bytes() != kept
    # No file of the output folders or the data folder holds a refusal's words.
    for place in (tmp_path, data):
        for path in place.rglob("*"):
            if path.is_file() and path.suffix != ".csv":
                text = path.read_text(encoding="utf-8", errors="replace")
                for words in words_said:
                    assert words not in text, (path, words[:40])


# -- (v) THE PRIVATE REPORT'S PLACE AND THE NAME -----------------------------


def test_the_private_report_is_written_in_the_data_folder_alone(tmp_path: pathlib.Path) -> None:
    """Its folder 0700 and its file 0600 beside the key; refused inside the output folder; never beside the twin.

    MUTANT: the private report beside the twin (the output folder holds it).
    """
    _table, described = _chained(tmp_path / "out")
    private = installation.data_folder() / "private-reports"
    written = sorted(private.iterdir())
    assert len(written) == 1
    if os.name != "nt":
        assert private.stat().st_mode & 0o777 == 0o700
        assert written[0].stat().st_mode & 0o777 == 0o600
    assert not [path for path in (tmp_path / "out").rglob("*") if "private" in path.name]
    table = _clinic(tmp_path / "beside", seed=9)
    refused, said = _ran(["profile", str(table), "--name", "beside", "--private-folder", str(tmp_path / "beside" / "mine")])
    assert refused.verdict == results.NO_MISS
    assert "The private report was not written" in said
    assert not (tmp_path / "beside" / "mine").exists()


@pytest.mark.parametrize("name", ["../up", "a/b", "a\\b", "..", "", "tab\there"])
def test_a_name_that_would_leave_its_folder_is_refused_before_any_work(tmp_path: pathlib.Path, name: str) -> None:
    """`--name` with a separator, '..', a control character or nothing: exit 2, nothing read or written."""
    table = _clinic(tmp_path)
    data = installation.data_folder()
    before = _quiet_files(data)
    made, said = _ran(["profile", str(table), "--name", name])
    assert made.verdict == results.UNUSABLE and results.exit_code(made) == 2
    assert "--name" in said
    assert not (tmp_path / "clinic-profile.json").exists()
    assert _quiet_files(data) == before


def test_the_four_options_parse_and_every_abbreviation_of_the_base_keeps_its_meaning() -> None:
    """argparse takes a word beginning one long option alone as that option: `--r` to `--replac` read `--replace` on the base and still do.

    `--replace-description` begins with each of them, so the parser writes
    them whole first (`cli._kept_abbreviations`); `--replace-` and longer
    begin the new option alone, and no long option of the base begins
    `--n` or `--p`. MUTANT: the abbreviations left to argparse (`--rep`
    refused as ambiguous).
    """
    for word in ("--r", "--re", "--rep", "--repl", "--repla", "--replac", "--replace"):
        read = cli._parse_arguments(["generate", "x.json", word], None)
        assert read.replace and not read.replace_description, word
    for word in ("--replace-", "--replace-d", "--replace-description"):
        read = cli._parse_arguments(["profile", "x.csv", word], None)
        assert read.replace_description and not read.replace, word
    read = cli._parse_arguments(["profile", "x.csv", "--na", "clinic", "--new", "--pri", "mine"], None)
    assert (read.name, read.new_key, read.private_folder) == ("clinic", True, "mine")
    refused = cli.run(["profile", "x.csv", "--n", "clinic"], screen=[])
    assert refused.verdict == results.UNUSABLE and "ambiguous option" in refused.refusal.words
    for word in ("--rep=x", "--replace=x"):
        bad = cli.run(["generate", "x.json", word], screen=[])
        assert bad.verdict == results.UNUSABLE and "--replace" in bad.refusal.words, word


# -- (vi) THE SIZE GUARD, SIZED BY THE WHOLE RUN (LANE CHON RULINGS 2) -------


def _oracle() -> object:
    """The chain's oracle, read from the page alone (`tools/reference/chain_oracle.py`)."""
    import importlib.util

    place = pathlib.Path(__file__).resolve().parents[1] / "tools" / "reference" / "chain_oracle.py"
    spec = importlib.util.spec_from_file_location("cho_chain_oracle_guard", place)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_the_size_guard_projects_the_whole_run_from_its_measured_costs() -> None:
    """The whole run, profile, generate and validate with the chain on, against 24 CPU hours and 8 GB a process.

    The page's constants (contract 4.6b.13, stated limit 4, amended
    2026-11-12: a line a + b n a column and a pair, fitted through the
    whole runs at 20,000 and 200,000 rows) project every measured run from
    above; the owner's 2,000,000 x 50 keeps its whole chain with EVERY
    partner; the first guard's 1,000,000 x 88 and 200,000 x 197 keep their
    whole chain with the 24 partners, while 2,000,000 x 62 and x 100 keep a
    degraded chain, never nothing, and a table whose run without the chain
    fills the time keeps none; and every decision of a GENERATED sweep
    equals the oracle's. MUTANT: the guard sized by the profile alone
    (2,000,000 x 62 drew no chain); the degraded chain dropped (none where
    some columns fit); the fixed terms dropped (a measured run projected
    from below).
    """
    co = _oracle()
    assert co.GUARD == {  # type: ignore[attr-defined]
        "run_seconds": chain.RUN_SECONDS_AT_MOST,
        "process_bytes": chain.PROCESS_BYTES_AT_MOST,
        "plain_ns_cell": chain.PLAIN_NANOSECONDS_A_CELL,
        "plain_ms_column": chain.PLAIN_MILLISECONDS_A_COLUMN,
        "chain_ns_pair": chain.CHAIN_NANOSECONDS_A_PAIR,
        "chain_ms_pair": chain.CHAIN_MILLISECONDS_A_PAIR,
        "every_ns_pair": chain.EVERY_PARTNER_NANOSECONDS_A_PAIR,
        "every_ms_pair": chain.EVERY_PARTNER_MILLISECONDS_A_PAIR,
        "describe_fixed": chain.DESCRIBE_BYTES_FIXED,
        "describe_cell": chain.DESCRIBE_BYTES_A_CELL,
        "describe_pair": chain.DESCRIBE_BYTES_A_PAIR,
    }
    # THE MEASURED WHOLE RUNS (CPU seconds, profile, generate and validate,
    # one process a step; plan P4-D464, repair 1, LANE CHON RULINGS 6 (2)):
    # lane CHs's three shapes of 50 columns at 20,000 and 200,000 rows, the
    # run without the chain, with the 24 partners and with every partner (the
    # numeric shape's 50 eligible columns, the code-heavy shape's 47; the mixed
    # shape draws none). Each constant is the largest of the shapes' fitted
    # slopes and intercepts, so the guard projects every measured run from above.
    measured = {
        ("codes", 20_000, "every"): 609.0,
        ("codes", 200_000, "every"): 3552.5,
        ("codes", 20_000, "off"): 156.1,
        ("codes", 200_000, "off"): 1462.9,
        ("codes", 20_000, "p24"): 571.9,
        ("codes", 200_000, "p24"): 3353.2,
        ("mixed", 20_000, "off"): 271.4,
        ("mixed", 200_000, "off"): 2547.0,
        ("numeric", 20_000, "every"): 1672.8,
        ("numeric", 200_000, "every"): 8877.8,
        ("numeric", 20_000, "off"): 351.9,
        ("numeric", 200_000, "off"): 3284.2,
        ("numeric", 20_000, "p24"): 1487.1,
        ("numeric", 200_000, "p24"): 7589.5,
    }
    eligible = {"numeric": 50, "codes": 47, "mixed": 0}
    for (shape, rows, setting), seconds in measured.items():
        drawn = 0 if setting == "off" else eligible[shape]
        assert chain.projected_seconds(rows, 50, drawn, setting == "every") >= seconds, (shape, rows, setting)
    whole = chain.size_decision(2_000_000, 50, 50)
    assert (whole.drawn, whole.every_partner, whole.degraded) == (50, True, False)
    assert whole.seconds == whole.seconds_every <= chain.RUN_SECONDS_AT_MOST
    for rows, columns in ((1_000_000, 88), (200_000, 197)):
        kept = chain.size_decision(rows, columns, columns)
        assert (kept.drawn, kept.every_partner) == (columns, False), (rows, columns, kept)
        assert kept.seconds <= chain.RUN_SECONDS_AT_MOST < kept.seconds_every
    for rows, columns in ((2_000_000, 62), (2_000_000, 100)):
        above = chain.size_decision(rows, columns, columns)
        assert above.degraded and 2 <= above.drawn < columns, (rows, columns, above)
        assert above.seconds <= chain.RUN_SECONDS_AT_MOST < above.seconds_whole
    none = chain.size_decision(2_000_000, 140, 140)
    assert none.drawn == 0 and none.seconds_plain > chain.RUN_SECONDS_AT_MOST
    assert chain.size_decision(20_000, 5, 5).drawn == 5 and chain.size_decision(20_000, 5, 1).drawn == 1
    drawn_before = 10**9
    for rows in (20_000, 200_000, 1_000_000, 2_000_000, 4_000_000):
        drawn = chain.size_decision(rows, 80, 80).drawn
        assert drawn <= drawn_before
        drawn_before = drawn
    draw = random.Random(464)
    for _case in range(1500):
        candidates = draw.randint(0, 400)
        columns = candidates + draw.randint(0, 60)
        rows = draw.choice([20_000, 50_000, 200_000, 1_000_000, 2_000_000, draw.randint(20_000, 5_000_000)])
        made = chain.size_decision(rows, columns, candidates)
        assert (made.drawn, made.every_partner) == co.guard_decision(rows, columns, candidates), (rows, columns, candidates)  # type: ignore[attr-defined]
        assert made.seconds == co.guard_seconds(rows, columns, made.drawn, made.every_partner)  # type: ignore[attr-defined]


def test_the_degraded_chain_keeps_the_columns_whose_pairs_carry_the_most_dependence() -> None:
    """THE DEGRADED CHAIN's choice (contract 4.6b.13, stated limit 4), on screen codes, against the oracle.

    A family of three dependent columns built among independent ones is
    kept whole at three; a derived family's input is kept first; and a
    GENERATED sweep of 300 tables of codes (2 to 12 columns, 2 to 10 codes,
    dependence built in at random) gives the oracle's places every time.
    MUTANT: the pairs taken from the weakest up, or ties read the other way.
    """
    import types

    co = _oracle()
    draw = random.Random(7)
    rows = 600
    base = [draw.randrange(4) for _row in range(rows)]
    built = [
        types.SimpleNamespace(screen=bytes(draw.randrange(4) for _row in range(rows)), screen_levels=4),
        types.SimpleNamespace(screen=bytes(base), screen_levels=4),
        types.SimpleNamespace(screen=bytes(draw.randrange(3) for _row in range(rows)), screen_levels=3),
        types.SimpleNamespace(screen=bytes(code if draw.random() < 0.8 else draw.randrange(4) for code in base), screen_levels=4),
        types.SimpleNamespace(screen=bytes(min(3, code + (draw.random() < 0.2)) for code in base), screen_levels=4),
        types.SimpleNamespace(screen=bytes(draw.randrange(5) for _row in range(rows)), screen_levels=5),
    ]
    assert chain.strongest_columns(built, 3, frozenset()) == [1, 3, 4]  # type: ignore[arg-type]
    assert chain.strongest_columns(built, 3, frozenset({0})) in ([0, 1, 4], [0, 1, 3], [0, 3, 4])  # type: ignore[arg-type]
    assert 0 in chain.strongest_columns(built, 3, frozenset({0}))  # type: ignore[arg-type]
    for _case in range(300):
        count = draw.randint(2, 12)
        size = draw.randint(20, 200)
        screens: "list[tuple[bytes, int]]" = []
        for place in range(count):
            levels = draw.randint(2, 10)
            if place and draw.random() < 0.5:
                source, source_levels = screens[draw.randrange(place)]
                codes = bytes(min(levels - 1, code * levels // source_levels) if draw.random() < 0.7 else draw.randrange(levels) for code in source)
            else:
                codes = bytes(draw.randrange(levels) for _row in range(size))
            screens += [(codes, levels)]
        at_most = draw.randint(2, count)
        forced = frozenset(draw.sample(range(count), draw.randint(0, 1)))
        fakes = [types.SimpleNamespace(screen=codes, screen_levels=levels) for codes, levels in screens]
        for first in range(count):
            for second in range(first):
                found = chain.pair_dependence(fakes[first], fakes[second])  # type: ignore[arg-type]
                expected = co.pair_dependence(screens[first][0], screens[first][1], screens[second][0], screens[second][1])  # type: ignore[attr-defined]
                assert found == float(expected)
        assert chain.strongest_columns(fakes, at_most, forced) == co.strongest(screens, at_most, forced)  # type: ignore[arg-type, attr-defined]


def _guarded_constants(monkeypatch: pytest.MonkeyPatch, allowed: int) -> None:
    """The guard's costs set so a table of 1,000 rows costs one second a pair of the columns drawn and nothing else."""
    monkeypatch.setattr(chain, "PLAIN_NANOSECONDS_A_CELL", 0)
    monkeypatch.setattr(chain, "CHAIN_NANOSECONDS_A_PAIR", 1_000_000)
    monkeypatch.setattr(chain, "EVERY_PARTNER_NANOSECONDS_A_PAIR", 2_000_000)
    for fixed in ("PLAIN_MILLISECONDS_A_COLUMN", "CHAIN_MILLISECONDS_A_PAIR", "EVERY_PARTNER_MILLISECONDS_A_PAIR"):
        monkeypatch.setattr(chain, fixed, 0)
    monkeypatch.setattr(chain, "RUN_SECONDS_AT_MOST", allowed)


def test_above_the_guard_the_chain_is_drawn_over_the_strongest_columns_and_says_so(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The guard's budget lowered by the test: three of the clinic's five columns, the rest set aside and named.

    The description lists the two others as ineligible for `size` and
    loads; the screen says how many columns are related and how many are
    carried on their own, with both projections; the private report names
    them; the twin's shared report names them as carried on their own.
    MUTANT: the degraded chain dropped (no chain above the guard, as the
    old guard did); the whole chain drawn above it.
    """
    _guarded_constants(monkeypatch, 3)
    table = _clinic(tmp_path, 1000)
    _ran(["profile", str(table), "--name", "wide"])
    _answered(tmp_path / "clinic-questions.json")
    made, said = _ran(
        ["profile", str(table), "--answers", str(tmp_path / "clinic-questions.json"), "--name", "wide", "--replace-description"]
    )
    assert made.verdict == results.NO_MISS, said[-2000:]
    statistical = _statistical(tmp_path / "clinic-profile.json")
    assert isinstance(statistical, dict), said[-2000:]
    kept = [entry["column"] for entry in statistical["ladder"]]
    aside = [entry["column"] for entry in statistical["ineligible"] if entry["reason"] == "size"]
    assert len(kept) == 3 and len(aside) == 2 and not set(kept) & set(aside), statistical["ineligible"]
    assert statistical["moments"] is None or statistical["moments"]["partners"] == 24
    assert "the relationships are kept among the 3 columns whose pairs carry the most dependence" in said
    assert "The other 2 columns are carried on their own" in said
    profile_described = contract.load_profile(str(tmp_path / "clinic-profile.json"))
    assert profile_described.relationships.set_aside == tuple(aside)
    reports = [path for path in (installation.data_folder() / "private-reports").iterdir() if "wide" in path.name]
    private = reports[0].read_text(encoding="utf-8")
    assert "the size guard drew the chain over 3 of the 5 eligible columns" in private
    assert "relating every column would take the projected run to about" in private
    built, said = _ran(["generate", str(tmp_path / "clinic-profile.json")])
    assert built.verdict in (results.NO_MISS, results.MISSED), said[-2000:]
    report = (tmp_path / "clinic-twin-report.txt").read_text(encoding="utf-8")
    from synthtwin import chain_grades

    assert chain_grades.SET_ASIDE in report and all(name in report.split(chain_grades.SET_ASIDE)[1] for name in aside)


def test_above_even_the_degraded_chains_budget_no_chain_is_drawn_and_the_screen_says_why(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Where not even two columns fit: no chain, the screen's line with the projections, the private note; no shared byte says why.

    MUTANT: the guard removed (a chain drawn above every budget).
    """
    _guarded_constants(monkeypatch, 0)
    monkeypatch.setattr(chain, "PLAIN_NANOSECONDS_A_CELL", 1_000_000)
    table = _clinic(tmp_path / "over", 1000, seed=8)
    _ran(["profile", str(table), "--name", "over"])
    _answered(tmp_path / "over" / "clinic-questions.json")
    made, said = _ran(
        ["profile", str(table), "--answers", str(tmp_path / "over" / "clinic-questions.json"), "--name", "over"]
    )
    assert made.verdict == results.NO_MISS, said[-2000:]
    assert _statistical(tmp_path / "over" / "clinic-profile.json") is None
    sized = chain.size_decision(1000, 5, 5)
    assert sized.drawn == 0 and cli._guard_line(sized).strip() in said
    reports = [path for path in (installation.data_folder() / "private-reports").iterdir() if "over" in path.name]
    assert reports and chain.size_note(sized) in reports[0].read_text(encoding="utf-8")
    shared = (tmp_path / "over" / "clinic-profile.json").read_text(encoding="utf-8") + (
        tmp_path / "over" / "clinic-profile.txt"
    ).read_text(encoding="utf-8")
    assert "larger than" not in shared and "hours" not in shared


# -- (vii) THE DATA FOLDER IS THE TEST'S OWN, AND A REFUSED RUN LEAVES NOTHING -


def test_each_test_has_a_data_folder_of_its_own_holding_the_fixed_key(installation_folder: pathlib.Path) -> None:
    """tests/conftest.py's fixture: the platform's data folder is this test's, its key the fixed one."""
    assert installation.data_folder() == installation_folder
    assert installation.key_path(installation_folder).read_bytes() == bytes(range(32))
    assert f"{installation_folder}".startswith(os.environ["XDG_DATA_HOME"])


def test_a_run_refused_before_the_chain_leaves_no_key_folder_or_entry(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A fresh installation: the table floor's refusal and a missing table make no folder, key or entry.

    MUTANT: a new key left by a refused run (the key made before the table is read).
    """
    fresh = tmp_path / "fresh"
    monkeypatch.setenv("XDG_DATA_HOME", str(fresh))
    monkeypatch.setenv("LOCALAPPDATA", str(fresh))
    small = _clinic(tmp_path / "small", 300)
    floored, said = _ran(["profile", str(small)], small_tables_refused=True)
    assert floored.verdict == results.REFUSED, said[-2000:]
    missing, said = _ran(["profile", str(tmp_path / "small" / "nowhere.csv")])
    assert missing.verdict == results.REFUSED
    assert not fresh.exists()
    reached, said = _ran(["profile", str(small)])
    assert reached.verdict == results.NO_MISS, said[-2000:]
    assert installation.key_path(fresh / installation.FOLDER).is_file()
    assert installation.words_key_made(f"{installation.key_path(fresh / installation.FOLDER)}") in said


# -- REPAIR 1: A CARRIED RULE'S COLUMNS SURVIVE THE DEGRADED CHAIN -----------
# (LANE CHON RULINGS 5 (1), skeptic 1's item 1: the degraded chain set aside a
# carried rule's input or its source carrier, so the profile wrote, with exit
# 0, a description its own loader and `generate` refused.)


def _rule_table(folder: pathlib.Path, source: bool, rows: int = 1500, seed: int = 5, second: bool = False) -> pathlib.Path:
    """An invented stay: a day in, a day out never before it (and the stay where `source`), a ward, a family of five on one factor.

    The days pair weakly with the family, so the degraded chain's strongest
    pairs are the family's: the columns the carried rule reads must be kept
    first or the loader refuses the description (S28). With `second`, a
    day seen and a day seen again never before it beside them.
    """
    draw = random.Random(seed)
    header = ["first_day", "last_day"] + (["stay"] if source else []) + (["seen_on", "seen_again"] if second else [])
    header += ["ward", "a", "b", "c", "d", "e"]
    lines = [",".join(header)]
    for _row in range(rows):
        first = draw.randint(1, 300)
        stay = draw.randint(0, 20)
        seen = draw.randint(1, 200) if second else 0
        a = draw.gauss(50, 10)
        b = a + draw.gauss(0, 2)
        c = "low" if a < 45 else ("mid" if a < 55 else "high")
        d = "1" if b > 52 else "0"
        e = round(a * 2 + draw.gauss(0, 3), 1)
        cells = [f"{first}", f"{first + stay}"] + ([f"{stay}"] if source else [])
        cells += [f"{seen}", f"{seen + draw.randint(0, 40)}"] if second else []
        cells += [draw.choice(["north", "south", "east"]), f"{a:.1f}", f"{b:.1f}", c, d, f"{e}"]
        lines += [",".join(cells)]
    folder.mkdir(parents=True, exist_ok=True)
    return fixtures.write(folder, "stays.csv", "\n".join(lines) + "\n")


def _two_rounds(table: pathlib.Path, extra: "tuple[str, ...]" = ()) -> "tuple[results.Result, str]":
    """The shipped walk: round 1, the subject question answered, round 2."""
    stem = table.name[: -len(".csv")]
    first, said = _ran(["profile", str(table), *extra])
    assert first.verdict == results.NO_MISS, said[-2000:]
    _answered(table.parent / f"{stem}-questions.json")
    return _ran(["profile", str(table), "--answers", str(table.parent / f"{stem}-questions.json"), "--replace-description", *extra])


def test_the_degraded_chain_keeps_every_column_a_carried_rule_reads() -> None:
    """THE CLASS, CLOSED BY A GENERATED RUN (LANE CHON RULINGS 5 (1)(a), (b) and (e); contract 4.6b.13, stated limit 4).

    3,000 generated cases: 3 to 14 eligible columns of screen codes, one
    to three carried rules, each reading an input and carried by a derived
    difference or by another eligible column, the guard's bound from 2 up.
    The places the product forces (`chain.rule_columns`) equal the oracle's
    from the rules as written (`rule_places`), every one is kept even where
    they alone pass the bound, and nothing past the bound is kept but
    them; the first 100 cases keep the oracle's places exactly. MUTANT: the
    forced places the derived families' parents alone (the build's rule):
    a source carrier set aside.
    """
    import types

    co = _oracle()
    draw = random.Random(1205)
    for case in range(3000):
        count = draw.randint(3, 14)
        size = draw.randint(30, 90)
        screens: "list[tuple[bytes, int]]" = []
        for place in range(count):
            levels = draw.randint(2, 6)
            if place and draw.random() < 0.6:
                source, source_levels = screens[draw.randrange(place)]
                codes = bytes(min(levels - 1, code * levels // source_levels) if draw.random() < 0.7 else draw.randrange(levels) for code in source)
            else:
                codes = bytes(draw.randrange(levels) for _row in range(size))
            screens += [(codes, levels)]
        names = [f"c{place}" for place in range(count)]
        carried = []
        for _rule in range(draw.randint(1, 3)):
            first = draw.choice(names)
            carrier = "derived" if draw.random() < 0.5 else draw.choice([name for name in names if name != first])
            carried += [(types.SimpleNamespace(inputs=(first,)), types.SimpleNamespace(carrier=carrier))]
        read = chain.rule_columns(carried)
        forced = frozenset(place for place in range(count) if names[place] in read)
        written = [{"inputs": list(rule.inputs), "carrier": option.carrier} for rule, option in carried]
        assert sorted(forced) == co.rule_places(names, written), case  # type: ignore[attr-defined]
        at_most = draw.randint(2, count - 1)
        fakes = [types.SimpleNamespace(screen=codes, screen_levels=levels) for codes, levels in screens]
        kept = chain.strongest_columns(fakes, at_most, forced)  # type: ignore[arg-type]
        assert forced <= set(kept), (case, sorted(forced), kept)
        assert len(kept) <= max(at_most, len(forced)), case
        if case < 100:
            assert kept == co.strongest(screens, at_most, forced), case  # type: ignore[attr-defined]


def test_a_rule_another_column_carries_keeps_its_input_and_carrier_under_the_guard_and_the_twin_is_built(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Skeptic 1's nine-column table through the shipped command, the guard lowered to four columns.

    The rule `last_day` on or after `first_day`, carried by `stay`: both
    columns it reads are kept with the two strongest of the family, the
    description loads and `generate` builds its twin. MUTANT: the forced
    places the derived families' parents alone (the build's rule): the
    loader refuses the chain, so no chain is written (red).
    """
    _guarded_constants(monkeypatch, 9)
    table = _rule_table(tmp_path / "source", True)
    made, said = _two_rounds(table)
    assert made.verdict == results.NO_MISS, said[-2000:]
    statistical = _statistical(table.parent / "stays-profile.json")
    assert isinstance(statistical, dict), said[-2000:]
    kept = [entry["column"] for entry in statistical["ladder"]]
    assert len(kept) == 4 and [entry["column"] for entry in statistical["ineligible"] if entry["reason"] == "size"], statistical["ineligible"]
    assert statistical["rules"], statistical["rules"]
    for rule in statistical["rules"]:
        assert set(rule["inputs"]) <= set(kept), (rule, kept)
        assert rule["carrier"] == "derived" or rule["carrier"] in kept, (rule, kept)
    contract.load_profile(str(table.parent / "stays-profile.json"))
    built, said = _ran(["generate", str(table.parent / "stays-profile.json")])
    assert built.verdict in (results.NO_MISS, results.MISSED), said[-2000:]
    assert (table.parent / "stays-twin.csv").is_file()


def test_a_derived_carried_rule_keeps_its_input_under_the_guard(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A day out never before a day in, no stay column: the rule carried by a derived difference keeps `first_day`.

    MUTANT: the forced places emptied: `first_day` set aside, the loader
    refuses the chain, so no chain is written (red).
    """
    _guarded_constants(monkeypatch, 9)
    table = _rule_table(tmp_path / "derived", False)
    made, said = _two_rounds(table)
    assert made.verdict == results.NO_MISS, said[-2000:]
    statistical = _statistical(table.parent / "stays-profile.json")
    assert isinstance(statistical, dict), said[-2000:]
    kept = [entry["column"] for entry in statistical["ladder"]]
    assert [(rule["computed"], rule["inputs"], rule["carrier"]) for rule in statistical["rules"]] == [("last_day", ["first_day"], "derived")]
    assert "first_day" in kept and len(kept) == 4, kept
    contract.load_profile(str(table.parent / "stays-profile.json"))


def test_the_rules_alone_past_the_bound_are_all_kept_and_the_note_says_so(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The bound lowered to two columns: the two carried rules read three, all kept and nothing else; the private note says so.

    A carried rule is never dropped silently (fidelity first): the note
    names the bound, the columns the rules read and the projected run.
    """
    _guarded_constants(monkeypatch, 2)
    table = _rule_table(tmp_path / "bound", True, second=True)
    made, said = _two_rounds(table, ("--name", "bound"))
    assert made.verdict == results.NO_MISS, said[-2000:]
    statistical = _statistical(table.parent / "stays-profile.json")
    assert isinstance(statistical, dict), said[-2000:]
    assert [(rule["computed"], rule["carrier"]) for rule in statistical["rules"]] == [("last_day", "stay"), ("seen_again", "derived")]
    assert sorted(entry["column"] for entry in statistical["ladder"]) == ["first_day", "seen_on", "stay"]
    reports = [path for path in (installation.data_folder() / "private-reports").iterdir() if "bound" in path.name]
    private = reports[0].read_text(encoding="utf-8")
    assert "the carried rules read more columns than the" in private and "a carried rule is never dropped" in private
    contract.load_profile(str(table.parent / "stays-profile.json"))


def _epoch_table(folder: pathlib.Path, rows: int = 1500) -> pathlib.Path:
    """Moments written as counts twice, in milliseconds and in seconds since 1970, beside a ward and a score (the zoo's time edges)."""
    import datetime

    draw = random.Random(5)
    lines = ["epoch_ms,epoch_s,ward,score"]
    for _row in range(rows):
        moment = datetime.datetime(2022, 1, 1) + datetime.timedelta(seconds=draw.randint(0, 3 * 365 * 86400))
        instant = int((moment - datetime.datetime(1970, 1, 1)).total_seconds())
        lines += [f"{instant * 1000 + draw.randint(0, 999)},{instant},{draw.choice(['north', 'south', 'east'])},{draw.randint(0, 40)}"]
    folder.mkdir(parents=True, exist_ok=True)
    return fixtures.write(folder, "edges.csv", "\n".join(lines) + "\n")


def test_the_command_never_writes_a_description_its_own_loader_refuses(tmp_path: pathlib.Path) -> None:
    """THE CHAIN'S FAIL-SAFE (LANE CHON RULINGS 5 (1)(c), 6 (3)): a carried rule computing a column of dates written as counts.

    The chain's own check passes the computed block, the loader's column
    rules refuse it (CD1): the description written is the PLAIN one, its
    columns as described and no chain, it loads and `generate` builds its
    twin, and the private report names the refusal. MUTANT: the refused
    chain written (the fail-safe read where the moments stand only, or
    by the chain's check alone): the loader refuses the file (red).
    """
    table = _epoch_table(tmp_path / "edges")
    first, said = _ran(["profile", str(table), "--name", "edges"])
    assert first.verdict == results.NO_MISS, said[-2000:]
    questions = table.parent / "edges-questions.json"
    document = json.loads(questions.read_text(encoding="utf-8"))
    for entry in document["asked"]:
        entry["your_answer"] = {"epoch_ms": "milliseconds-since-1970", "epoch_s": "seconds-since-1970"}.get(entry["column"], entry["your_answer"])
    document[asking.BETWEEN_COLUMNS][asking.ROWS_PER_PERSON]["your_answer"] = asking.ANSWER_ONE_ROW_EACH
    questions.write_text(json.dumps(document, indent=1) + "\n", encoding="utf-8", newline="\n")
    second, said = _ran(["profile", str(table), "--answers", str(questions), "--replace-description", "--name", "edges"])
    assert second.verdict == results.NO_MISS, said[-2000:]
    described = table.parent / "edges-profile.json"
    assert _statistical(described) is None
    loaded = contract.load_profile(str(described))
    assert {column.name for column in loaded.columns} >= {"epoch_ms", "epoch_s"}
    reports = [path for path in (installation.data_folder() / "private-reports").iterdir() if "edges" in path.name]
    assert reports and "the loader that reads the description refused the chain" in reports[0].read_text(encoding="utf-8")
    built, said = _ran(["generate", str(described)])
    assert built.verdict in (results.NO_MISS, results.MISSED), said[-2000:]


# -- REPAIR 1: A RUN THAT WRITES NO DESCRIPTION LEAVES NO KEY, FOLDER OR ENTRY -
# (LANE CHON RULINGS 5 (2), skeptic 1's items 2 and 3.)


def _fresh_data_folder(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> pathlib.Path:
    fresh = tmp_path / "fresh"
    monkeypatch.setenv("XDG_DATA_HOME", str(fresh))
    monkeypatch.setenv("LOCALAPPDATA", str(fresh))
    return fresh


def test_a_run_refused_for_its_outputs_leaves_no_key_folder_or_entry(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A network out-dir, the table as the out-dir, an out-dir that is not there: each refused before the key is made.

    The refusal comes before the run reaches the chain, so its screen never
    says a key was made (a run that wrote no description takes back what it
    made, so the folder alone cannot tell). MUTANT: the output's checks
    left after the chain (the screen says a key was made in a folder the
    run then takes back).
    """
    fresh = _fresh_data_folder(tmp_path, monkeypatch)
    table = _clinic(tmp_path / "t", 1000)
    made_words = installation.words_key_made(f"{installation.key_path(fresh / installation.FOLDER)}")
    for out_dir in ("//server/share/out", str(table), str(tmp_path / "no" / "such")):
        refused, said = _ran(["profile", str(table), "--out-dir", out_dir])
        assert refused.verdict in (results.REFUSED, results.UNUSABLE), (out_dir, said[-1500:])
        assert made_words not in said, out_dir
        assert not fresh.exists(), out_dir
        assert not (tmp_path / "t" / "clinic-profile.json").exists()
    reached, said = _ran(["profile", str(table)])
    assert reached.verdict == results.NO_MISS, said[-2000:]
    assert installation.key_path(fresh / installation.FOLDER).is_file()


def test_a_write_that_fails_after_the_record_takes_back_its_entry_key_and_folder(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The description's write fails after the ledger's entry is written: no entry, no key and no folder are left.

    In a data folder that holds a record already, the record is written
    back as the run read it and the key stays. MUTANT: the entry left
    (a later answered round meets the record's refusal for a description
    never written).
    """
    fresh = _fresh_data_folder(tmp_path, monkeypatch)
    table = _clinic(tmp_path / "t", 1000)
    real = profile.write_both_files

    def failing(*given: object, **named: object) -> object:
        raise OSError("the disk is full")

    monkeypatch.setattr(profile, "write_both_files", failing)
    with pytest.raises(OSError):
        cli.run(["profile", str(table)], screen=[])
    assert not fresh.exists()
    assert not (tmp_path / "t" / "clinic-profile.json").exists()
    monkeypatch.setattr(profile, "write_both_files", real)
    first, said = _ran(["profile", str(table)])
    assert first.verdict == results.NO_MISS, said[-2000:]
    data = fresh / installation.FOLDER
    key = installation.key_path(data).read_bytes()
    record = (data / installation.LEDGER_FILE).read_text(encoding="utf-8")
    monkeypatch.setattr(profile, "write_both_files", failing)
    other = _clinic(tmp_path / "u", 1100, name="other", seed=9)
    with pytest.raises(OSError):
        cli.run(["profile", str(other)], screen=[])
    assert installation.key_path(data).read_bytes() == key
    assert (data / installation.LEDGER_FILE).read_text(encoding="utf-8") == record


@pytest.mark.skipif(os.name == "nt", reason="a link needs a privilege on Windows; the case above holds the rule on every platform")
def test_a_dangling_link_at_the_description_s_name_leaves_nothing_behind(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Skeptic 1's own case: the write refused at a link that leads nowhere; no key, folder or entry is left."""
    fresh = _fresh_data_folder(tmp_path, monkeypatch)
    table = _clinic(tmp_path / "t", 1000)
    out = tmp_path / "out"
    out.mkdir()
    (out / "clinic-profile.json").symlink_to(tmp_path / "nowhere" / "x.json")
    refused, said = _ran(["profile", str(table), "--out-dir", str(out)])
    assert refused.verdict != results.NO_MISS, said[-2000:]
    assert not fresh.exists()


@pytest.mark.parametrize("where", ["out", "table", "inside"])
def test_a_data_folder_beside_the_output_is_refused_before_anything_is_made(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, where: str) -> None:
    """XDG_DATA_HOME (LOCALAPPDATA on Windows) at the output folder, the table's folder, or inside one: refused, exit 1, nothing written.

    The key and the record never travel beside the files that are shared
    (contract 4.6b.4). MUTANT: the test removed (the key and the record
    written inside the output folder).
    """
    table = _clinic(tmp_path / "in", 1000)
    out = tmp_path / "out"
    out.mkdir()
    place = {"out": out, "table": tmp_path / "in", "inside": out / "private"}[where]
    monkeypatch.setenv("XDG_DATA_HOME", str(place))
    monkeypatch.setenv("LOCALAPPDATA", str(place))
    argv = ["profile", str(table)] + (["--out-dir", str(out)] if where != "table" else [])
    refused, said = _ran(argv)
    assert refused.verdict == results.REFUSED and results.exit_code(refused) == 1, said[-2000:]
    assert "never travel beside the files that are shared" in said
    assert not (place / installation.FOLDER).exists()
    assert not list(out.glob("*-profile.json")) and not (tmp_path / "in" / "clinic-profile.json").exists()


def test_a_table_in_the_home_folder_uses_the_platform_s_own_data_folder(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The table, and the outputs beside it, in the account's home folder; the data folder the platform's own, deep inside it.

    The home folder holds the platform's place for an account's private
    data by design (~/Library/Application Support, ~/.local/share,
    AppData/Local), so the run is not refused there (lane CHON's repair 1:
    the rule as first built refused every table kept in the home folder),
    while a data folder standing directly in the home folder beside the
    table still is. MUTANTS: the home folder's exemption removed (refused);
    a data folder standing directly in the table's folder allowed (the key
    made beside the table in the home folder).
    """
    home = tmp_path / "home"
    table = _clinic(home, 1000)
    for name in ("HOME", "USERPROFILE"):
        monkeypatch.setenv(name, str(home))
    for name in ("XDG_DATA_HOME", "LOCALAPPDATA"):
        monkeypatch.delenv(name, raising=False)
    made, said = _ran(["profile", str(table)])
    assert made.verdict == results.NO_MISS, said[-2000:]
    default = installation.data_folder()
    assert home in default.parents and default.parent != home, default
    assert installation.key_path(default).is_file()
    monkeypatch.setenv("XDG_DATA_HOME", str(home))
    monkeypatch.setenv("LOCALAPPDATA", str(home))
    refused, said = _ran(["profile", str(table), "--replace"])
    assert refused.verdict == results.REFUSED and "never travel beside the files that are shared" in said, said[-2000:]
    assert not (home / installation.FOLDER).exists()


# -- REPAIR 1: F2, AN UNANSWERED RECORD-NUMBER QUESTION ON ANOTHER COLUMN -----
# (LANE CHON RULINGS 3 (1).)


def _ward_text(rows: int = 1500) -> str:
    """An invented ward table: a unit code of ten values beside an age, a weight that follows it, a group and an event."""
    draw = random.Random(3)
    units = ["H01", "H02", "C01", "C02", "W1", "W2", "W3", "N10", "N11", "S5"]
    lines = ["unit,age,weight,group,event"]
    for _row in range(rows):
        age = draw.randint(18, 90)
        group = draw.choice(["a", "b"]) if age < 50 else draw.choice(["b", "c"])
        event = "1" if draw.random() < 0.1 + age / 200 else "0"
        lines += [f"{draw.choice(units)},{age},{round(60 + age * 0.2 + draw.gauss(0, 8), 1)},{group},{event}"]
    return "\n".join(lines) + "\n"


def test_an_open_record_number_question_on_another_column_never_turns_the_chain_off(tmp_path: pathlib.Path) -> None:
    """F2 (LANE CHON RULINGS 3 (1)): the subject question answered `one row each`, the unit code's question left open.

    The library's switch with the answer (route C): the held code column
    is left out of the chain, held and named in the notes, and the chain
    is drawn over the rest. The shipped walk (route S) asks the person
    question first, as lane GRa's walk does; its screen names the column
    and the answers that turn the chain on. MUTANTS: the left-out rule
    removed (no chain: the held repeating column turns it off); the
    paragraph without the column's name and answers.
    """
    from synthtwin import reading, taxonomy

    folder = tmp_path / "ward"
    folder.mkdir()
    table = fixtures.write(folder, "ward.csv", _ward_text())
    made, said = _ran(["profile", str(table)])
    assert made.verdict == results.NO_MISS, said[-2000:]
    shown = cli._shown(folder / "ward-questions.json")
    assert cli._hold_paragraph(cli._WAITS_FOR_PERSON, shown, ("unit",)).strip() in said
    assert "Answer keep where its values are codes or a measurement" in said and ": unit." in said
    assert _statistical(folder / "ward-profile.json") is None
    # Route C: the switch handed in, the subject answered, the person question on `unit` open.
    document = json.loads((folder / "ward-profile.json").read_text(encoding="utf-8"))
    read = reading.read_table(str(table), small_cell_floor=FLOOR)
    settings = taxonomy.Settings(small_cell_floor=FLOOR)
    switch = chain.ChainSwitch("ward", bytes(range(32)), ("unit",), rows_per_person=chain.ROWS_ONE, held_by_person=("unit",))
    chained = chain.describe(read, document, settings, switch)
    assert chained.statistical is not None, chained.notes[-3:]
    assert chained.statistical["chain"]
    assert [entry["reason"] for entry in chained.statistical["ineligible"] if entry["column"] == "unit"] in (["held"], ["identifier"])
    assert "unit" not in [entry["column"] for entry in chained.statistical["ladder"]]
    assert any("left out of the chain while their question" in note and "unit" in note for note in chained.notes)


def _pressure_text(rows: int = 1500) -> str:
    """An invented cohort: an age, a pressure of three figures that follows it, a two-valued group, a death that follows age."""
    draw = random.Random(5)
    lines = ["age,sbp,group,died"]
    for _row in range(rows):
        age = draw.gauss(55, 12)
        lines += [f"{age:.0f},{100 + 0.8 * age + draw.gauss(0, 8):.0f},{draw.choice('FM')},{'yes' if draw.random() < (0.6 if age > 65 else 0.1) else 'no'}"]
    return "\n".join(lines) + "\n"


def test_a_held_column_its_own_open_question_leaves_out_of_the_chain_is_named_in_the_private_report(tmp_path: pathlib.Path) -> None:
    """LANE CHON RULINGS 6 (4), on the statistics check: a column left out of the chain by its own open question is named.

    The pressure's question offers `identifier` and stays open, so the
    description holds it as record numbers and the chain is drawn over the
    other columns, the subject question answered `one row each`; the private
    report's section on what the description left out names it (the screen
    names its open question already). MUTANT: the note removed (the section
    silent on the held column, as the build head was).
    """
    folder = tmp_path / "cohort"
    folder.mkdir()
    table = fixtures.write(folder, "cohort.csv", _pressure_text())
    made, said = _ran(["profile", str(table)])
    assert made.verdict == results.NO_MISS, said[-2000:]
    _answered(folder / "cohort-questions.json")
    second, said = _ran(["profile", str(table), "--answers", str(folder / "cohort-questions.json"), "--replace-description"])
    assert second.verdict == results.NO_MISS, said[-2000:]
    statistical = _statistical(folder / "cohort-profile.json")
    assert isinstance(statistical, dict) and statistical["chain"]
    assert "sbp" not in [entry["column"] for entry in statistical["ladder"]]
    assert [entry["reason"] for entry in statistical["ineligible"] if entry["column"] == "sbp"] in (["held"], ["identifier"])
    reports = [path for path in (installation.data_folder() / "private-reports").iterdir() if "cohort" in path.name]
    assert len(reports) == 1
    section = reports[0].read_text(encoding="utf-8").split("WHAT THE DESCRIPTION LEFT OUT, AND WHY", 1)[1].split("\n\n", 1)[0]
    assert "left out of the chain while their own question in the questions file stays open" in section
    assert "held: sbp" in section


# -- REPAIR 1: A FIXTURE OF A WIDER SCOPE NEVER MEETS THE ACCOUNT'S DATA FOLDER -


@pytest.fixture(scope="module")
def _seen_by_a_module_fixture() -> pathlib.Path:
    """The data folder a fixture of this module sees when pytest makes it (before any test's own autouse fixture)."""
    return installation.data_folder()


def test_a_fixture_of_a_module_meets_a_data_folder_of_its_own(
    _seen_by_a_module_fixture: pathlib.Path,
    _installation_folder_of_the_module: pathlib.Path,
    _installation_folder_of_the_session: pathlib.Path,
) -> None:
    """tests/conftest.py's module and session folders: a module's fixture runs its shipped command in a folder of its own.

    MUTANT: the module's autouse folder removed (the module fixture saw the
    session's folder, or with the session's removed too the account's own,
    where the whole suite of the build head wrote its keys and records).
    """
    assert _seen_by_a_module_fixture == _installation_folder_of_the_module
    assert _installation_folder_of_the_module != _installation_folder_of_the_session
    assert installation.key_path(_seen_by_a_module_fixture).read_bytes() == bytes(range(32))
    account = installation.data_folder(environ={})
    assert account not in (_seen_by_a_module_fixture, _installation_folder_of_the_session)


# -- REPAIR 1: PARAGRAPH 3 SAYS THE TWIN CAN SHOW A RELATIONSHIP THE TABLE DOES NOT HAVE --


def test_a_chained_twin_s_report_says_it_can_show_a_relationship_the_table_does_not_have(tmp_path: pathlib.Path) -> None:
    """LANE CHON RULINGS 6 (1)(B): paragraph 3 of a chained twin's report carries the measured words; every other twin keeps it word for word.

    The other twins: an unswitched twin, and a twin of a description made
    with the switch whose chain is off (lane ST's block, every family
    graded N), whose columns were built on their own and so show no
    relationship the table does not have. MUTANTS: the words on every twin
    (the unswitched twin's paragraph 3 moved); the words on every switched
    twin, its chain drawn or not (the chain-off twin's paragraph 3 moved)."""
    from synthtwin import generation, rendering

    _table, described = _chained(tmp_path / "chained")
    made, said = _ran(["generate", str(described)])
    assert made.verdict in (results.NO_MISS, results.MISSED), said[-2000:]
    report = (tmp_path / "chained" / "clinic-twin-report.txt").read_text(encoding="utf-8")
    assert "\n".join(rendering._INVENTED_RELATIONSHIPS) in report
    assert "about one pair of" in report and "14 to 16 in 100" in report
    document = json.loads(described.read_text(encoding="utf-8"))
    document["relationships"]["statistical"] = None
    off = fixtures.write_profile(tmp_path, "clinic-off-profile.json", document)
    loaded = contract.load_profile(str(off), chain=True)
    assert loaded.relationships.switched and not loaded.relationships.ladder
    chain_off = rendering.report(loaded, generation.generate(loaded, 1))
    standing = rendering._independence_lines()
    second = [line[:3] for line in standing].index("2. ")
    assert "\n".join(standing[second:]) in chain_off
    assert rendering._INVENTED_RELATIONSHIPS[0] not in chain_off
    plain = tmp_path / "plain"
    table = _clinic(plain)
    made, said = _ran(["profile", str(table)], unswitched=True)
    built, said = _ran(["generate", str(plain / "clinic-profile.json")], unswitched=True)
    assert built.verdict in (results.NO_MISS, results.MISSED), said[-2000:]
    unswitched = (plain / "clinic-twin-report.txt").read_text(encoding="utf-8")
    assert "\n".join(rendering._independence_lines()) in unswitched
    assert rendering._INVENTED_RELATIONSHIPS[0] not in unswitched


# -- REPAIR 2: THE ZOO'S ENGINE ANSWERS THE SUBJECT QUESTION; EVERY DRIVER'S
# RUNS IN A DATA FOLDER OF ITS OWN (LANE CHON RULINGS 7 (1)) -----------------


def test_the_zoo_answers_the_subject_question_as_each_export_is() -> None:
    """LANE CHON RULINGS 7 (1)(a): the subject question, where the file puts it, is answered as the export truly is.

    The person column's name where one names a person on several rows;
    'several rows, no column names the person' where an encounter's coded
    rows repeat a person no column names; 'one row each' where every row is
    another person's. Each answer is about the data, so the question is
    general. The zoo's engine asks for it (`subject=True`); the other walks
    that borrow the zoo's answers leave it open, as before. MUTANT: the
    subject question left open (`answer_generally` without its subject
    branch): every answer below reads ''.
    """
    import health_zoo as zoo

    for name, answer in (
        ("microbiology", asking.ANSWER_ONE_ROW_EACH),
        ("labs", zoo.table_named("labs").person),
        ("diagnoses_procedures", asking.ANSWER_NO_PERSON_COLUMN),
    ):
        assert answer
        document = {asking.BETWEEN_COLUMNS: {asking.ROWS_PER_PERSON: asking.rows_per_person_entry("")}}
        asked, general = zoo.answer_generally(zoo.table_named(name), document, subject=True)
        assert general, name
        assert document[asking.BETWEEN_COLUMNS][asking.ROWS_PER_PERSON]["your_answer"] == answer, name
        assert [entry["given"] for entry in asked if entry["column"] == zoo.SUBJECT_QUESTION] == [answer], name
    # A file that puts no subject question gets none; a borrowing walk leaves it open.
    asked, general = zoo.answer_generally(zoo.table_named("microbiology"), {"asked": []}, subject=True)
    assert asked == [] and general
    document = {asking.BETWEEN_COLUMNS: {asking.ROWS_PER_PERSON: asking.rows_per_person_entry("")}}
    asked, general = zoo.answer_generally(zoo.table_named("microbiology"), document)
    assert asked == [] and document[asking.BETWEEN_COLUMNS][asking.ROWS_PER_PERSON]["your_answer"] == ""


def test_the_zoo_s_engine_draws_a_chain_and_reads_it_for_leaks(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, installation_folder: pathlib.Path,
) -> None:
    """LANE CHON RULINGS 7 (1)(b) to (d): at the KPI size the zoo's engine walks an export to its chain and reads it.

    The microbiology export at 20,000 rows, the owner's floor on, through
    `health_zoo.run_table` -- the engine of the HIPAA drivers K-HZ-01, 02,
    03 and 05: its first round held by the subject question, the subject
    question answered 'one row each', the answered round refused by the
    record in its own words and run once more with --replace-description
    (counted), the chain drawn, and the leak counters reading the chained
    description and its twin (no isolate number in either). The walk ran in
    a data folder of its own: this test's folder still holds an empty record
    and no private report. MUTANTS: the subject question left open (no
    chain); the record's refusal left as the run's end (the answered round
    exits 1); the walk in the caller's data folder (this test's record
    written).
    """
    import health_zoo as zoo

    table = zoo.table_named("microbiology")
    read: "list[tuple[bool, bool]]" = []
    leaked = zoo.leaked

    def reading(*given: object, **named: object) -> "dict[str, dict]":
        described = json.loads(pathlib.Path(f"{given[3]}").read_text(encoding="utf-8"))
        statistical = described["relationships"]["statistical"]
        read.extend([(given[2] is not None, isinstance(statistical, dict) and bool(statistical["chain"]))])
        return leaked(*given, **named)  # type: ignore[arg-type]

    monkeypatch.setattr(zoo, "leaked", reading)
    empty = (installation_folder / installation.LEDGER_FILE).read_bytes()
    result = zoo.run_table(table, tmp_path / "zoo", zoo.KPI_ROWS, zoo.seed_of(table), small_tables_refused=True)
    steps = {step: done["exit"] for step, done in result["steps"].items()}
    assert steps == {"profile": 0, "answers": 0, "generate": 0, "validate": steps["validate"]}, result["steps"]
    assert steps["validate"] in (0, 3)
    asked = json.loads((tmp_path / "zoo" / "microbiology-questions.json").read_text(encoding="utf-8"))
    assert asked[asking.BETWEEN_COLUMNS][asking.ROWS_PER_PERSON]["your_answer"] == asking.ANSWER_ONE_ROW_EACH
    assert result["record_refused"] == [1] and result["answer_rounds"] == 1
    assert result["chained"] >= 1
    assert (False, False) in read and (False, True) in read and (True, True) in read, read
    assert result["leaks"] and all(
        entry.get("description", 0) == 0 and entry.get("twin", 0) == 0 for entry in result["leaks"].values()
    ), result["leaks"]
    assert (installation_folder / installation.LEDGER_FILE).read_bytes() == empty
    assert not (installation_folder / "private-reports").exists()
    assert os.environ["XDG_DATA_HOME"] == os.environ["LOCALAPPDATA"] == str(installation_folder.parent)


def test_a_driver_runs_in_a_data_folder_of_its_own(installation_folder: pathlib.Path) -> None:
    """LANE CHON RULINGS 7 (1)(c): every driver's process, and every block a driver names, gets a data folder of its own.

    `kpi_rules.guard_this_tree`, which every driver calls first, points
    XDG_DATA_HOME and LOCALAPPDATA at a new folder holding the fixed test key
    and an empty record; `kpi_rules.own_data_folder` names another for its
    block, puts the names back and removes it. MUTANT: the guard leaving the
    data folder where it was (a driver's runs in the account's folder).
    """
    import kpi_rules

    kpi_rules.guard_this_tree()
    place = pathlib.Path(os.environ["XDG_DATA_HOME"])
    assert os.environ["LOCALAPPDATA"] == str(place) and place != installation_folder.parent
    assert installation.data_folder() == place / installation.FOLDER
    assert installation.key_path(place / installation.FOLDER).read_bytes() == bytes(range(32))
    assert json.loads((place / installation.FOLDER / installation.LEDGER_FILE).read_text(encoding="utf-8")) == {"tables": [], "version": 1}
    with kpi_rules.own_data_folder() as data:
        assert installation.data_folder() == data and data.parent != place
        assert installation.key_path(data).read_bytes() == bytes(range(32))
    assert os.environ["XDG_DATA_HOME"] == os.environ["LOCALAPPDATA"] == str(place)
    assert not data.exists()


def _cli_calls_reaching_profile(tree: "object") -> "list[tuple[int, bool]]":
    """Each call of `cli.run(...)` and of `cli.main(...)` that may run `profile`: its line, and whether it names a data folder."""
    import ast

    found: "list[tuple[int, bool]]" = []

    def named(stack: "list[ast.AST]") -> bool:
        for node in stack:
            if isinstance(node, ast.With):
                for item in node.items:
                    call = item.context_expr
                    if isinstance(call, ast.Call):
                        function = call.func
                        name = function.attr if isinstance(function, ast.Attribute) else function.id if isinstance(function, ast.Name) else ""
                        if name in ("own_data_folder", "_installation"):
                            return True
        return False

    def walk(node: "ast.AST", stack: "list[ast.AST]") -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.Call):
                function = child.func
                if isinstance(function, ast.Attribute) and function.attr in ("main", "run") and isinstance(function.value, ast.Name) and function.value.id == "cli":
                    first = child.args[0] if child.args else None
                    word = first.elts[0].value if isinstance(first, ast.List) and first.elts and isinstance(first.elts[0], ast.Constant) else None
                    if word in (None, "profile") and not any(keyword.arg == "chain" for keyword in child.keywords):
                        found.extend([(child.lineno, named(stack))])
            walk(child, [*stack, child])

    walk(tree, [])  # type: ignore[arg-type]
    return found


def _guarded_at_module_level(tree: "object") -> bool:
    """Whether a module calls `kpi_rules.guard_this_tree()` as a statement of its own body, before any function runs."""
    import ast

    return any(
        isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)
        and isinstance(node.value.func, ast.Attribute) and node.value.func.attr == "guard_this_tree"
        for node in tree.body  # type: ignore[attr-defined]
    )


def test_every_driver_that_runs_the_shipped_profile_names_a_data_folder() -> None:
    """THE CLASS, SWEPT OVER EVERY DRIVER (LANE CHON RULINGS 7 (1)(c); plan P4-D464 limit (15)).

    Every call of `cli.run` and of `cli.main` in `tools/measurements` that may run
    `profile` hands in a chain naming its folder, sits inside a block that
    names a data folder of its own (`kpi_rules.own_data_folder`,
    `kpi_chain_shipped`'s `_installation`), or stands in a module that calls
    `kpi_rules.guard_this_tree()` among its own statements; and every driver
    that reaches such a call through a module of `tests` calls the guard
    there too -- save through `health_zoo`, whose engine names a folder for
    each walk (`run_table`). MUTANT: one of the five named drivers' blocks
    removed (`kpi_chain_rules.py`'s price run).
    """
    import ast

    root = pathlib.Path(__file__).resolve().parents[1]
    helpers = set()
    for path in sorted((root / "tests").glob("*.py")):
        if path.name.startswith("test_") or path.name == "conftest.py":
            continue
        if _cli_calls_reaching_profile(ast.parse(path.read_text(encoding="utf-8"))):
            helpers.add(path.stem)
    assert {"health_zoo", "unanswered_identifier_shapes"} <= helpers, sorted(helpers)
    open_calls: "list[str]" = []
    drivers = sorted((root / "tools" / "measurements").glob("*.py"))
    assert len(drivers) > 50
    for path in drivers:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        guarded = _guarded_at_module_level(tree)
        open_calls += [f"{path.name}:{line}" for line, named in _cli_calls_reaching_profile(tree) if not (named or guarded)]
        imported = {
            alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names
        } | {node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module}
        reached = sorted((imported & helpers) - {"health_zoo"})
        if reached and not guarded:
            open_calls += [f"{path.name} through {reached}"]
    assert open_calls == [], open_calls


# -- K-S6-16: THE GOLDEN TWIN OF ONE CHAINED FIXTURE, ON EVERY CI CELL --------

# The digests of the shipped command's description and twin of the clinic
# fixture below, under the fixed test key, seed 0 (`K-S6-16`, plan P4-D464).
# Re-recorded only with a reason a record names. THE TWIN RE-RECORDED by lane
# CHG (plan P4-D492): G16.3's grouping gate leaves the fixture's grouping
# moments that its published facts do not show beyond chance to the walk, so
# one column fewer is polished (138,556 words drawn and planned, against
# 174,556); the description is the same bytes, and with the gate off the twin
# is the earlier golden byte for byte (`GOLDEN_TWIN_UNGATED`,
# tests/test_polish_grouping_gate.py).
GOLDEN_DESCRIPTION = "c08571aa6b37aae4d52d458a5c68c319680be10d6439b762885da8ecdb305265"
GOLDEN_TWIN = "c25a9c62f98d9e36c37fbefe5c4a6f6d1e7555092521fdaaf72149a65050f72e"
GOLDEN_TWIN_UNGATED = "4638074c25d7ee13deba5506a981fd006a4aa49d277b1f6d81ab69c2e23f9f01"


def golden_record(folder: pathlib.Path) -> "tuple[str, str, int, int]":
    """The chained clinic fixture through the shipped command (`K-S6-16`).

    The description's and the twin's SHA-256, and the words the twin drew
    beside the words its plan states (generation method G4.3: the formula).
    """
    from synthtwin import generation

    _table, described = _chained(folder, 1500)
    made, said = _ran(["generate", str(described)])
    assert made.verdict in (results.NO_MISS, results.MISSED), said[-2000:]
    twin = folder / "clinic-twin.csv"
    loaded = contract.load_profile(str(described))
    drawn = generation.generate(loaded, 0).words_drawn
    planned = generation.plan_generation(loaded).words_planned
    return hashlib.sha256(described.read_bytes()).hexdigest(), hashlib.sha256(twin.read_bytes()).hexdigest(), drawn, planned


def test_k_s6_16_the_chained_fixture_s_golden_twin(tmp_path: pathlib.Path) -> None:
    """`K-S6-16`: the description and the twin of the chained fixture, byte for byte, on every cell of the CI matrix; the words its formula."""
    described, twin, drawn, planned = golden_record(tmp_path / "golden")
    assert (described, twin) == (GOLDEN_DESCRIPTION, GOLDEN_TWIN), sys.version_info
    assert drawn == planned


# -- batch 4u's merge of this lane with lane EZ-a's rounds of questions --------


def test_a_later_round_of_one_run_asks_no_second_new_key_once_the_key_stands(tmp_path: pathlib.Path) -> None:
    """--new-key is the run's, not each round's (batch 4u's merge of lane CHON with lane EZ-a, plan P4-D479).

    Every shipped run is switched, and each round of questions after the files
    opens the installation again (`cli._described_once`). Once an earlier round
    made the key, asking for a new one again would be refused (a key stands),
    so a later round's switch has `new_key` off; until the key stands it stays
    as typed, and every other setting is the run's. MUTANT:
    `_switch_of_a_later_round` handing the switch back unchanged.
    """
    folder = tmp_path / "data"
    folder.mkdir()
    typed = cli.ChainRun(folder=str(folder), new_key=True, replace_description=True)
    assert cli._switch_of_a_later_round(typed) == typed
    installation.key_path(folder).write_bytes(bytes(range(32)))
    assert cli._switch_of_a_later_round(typed) == cli.ChainRun(folder=str(folder), new_key=False, replace_description=True)
    assert cli._switch_of_a_later_round(None) is None
    plain = cli.ChainRun(folder=str(folder))
    assert cli._switch_of_a_later_round(plain) is plain


def test_a_person_said_in_a_handed_back_file_is_read_in_the_switched_words_too() -> None:
    """Lane EZ-a's reading of a person said in a questions file reads the switched person question's words (batch 4u's merge).

    On a switched run -- every shipped run since plan P4-D464 -- the person
    question's `identifier` reads `asking.PERSON_ANSWER_MEANS` (lane GRa,
    RULINGS 1 (1)); the unswitched opening and the kept answer's words still
    read as the person, and `record`'s words never do. MUTANT:
    `cli._says_the_person` reading the unswitched opening alone, the merge's
    code before this repair.
    """
    assert cli._says_the_person(asking.PERSON_ANSWER_MEANS)
    assert cli._says_the_person(cli._PERSON_KEPT_MEANS)
    assert cli._says_the_person(cli._PERSON_MEANS_OPENING + " -- rows sharing a value of it are one person")
    assert not cli._says_the_person(asking.RECORD_ANSWER_MEANS)
    assert not cli._says_the_person("record numbers: no value of the column is published")


# -- batch 4u's merge of lane GRb: the patient layer through the shipped commands
#
# With the patient layer's sub-switch set on (`cli._PATIENT_LAYER_SHIPPED`, which
# LANE MU RULINGS 1 (2) has lane GRb's merge flip; each case here sets it in its
# own process), a table where one person stands on several rows publishes
# `grain` and its chain over patients, `generate` makes the twin by the patient
# walk (lane GRb, plan P4-D465), and `validate` checks the blocks the loader
# reads counted in patients (the person column and each patient-fixed column) on
# the file's patients. Measured before the merge with the sub-switch on:
# `generate` raised IndexError at `generation.generate_held`'s written cells on
# the zoo's tables of several rows a person (the person column's block counts
# patients, its cells were placed over rows; lane BT3b's owed item, lane MU's
# finding F1); measured after the merge and before the validator's patient
# view: `validate` missed the person column's presence, forms and repetition
# on 14 of the zoo's 25 exports.


def test_a_table_of_several_rows_a_person_is_described_generated_and_checked_by_the_shipped_commands(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The zoo's prescriptions export at the table floor, the shipped commands with CHON's engine: grain, twin, no miss.

    20,000 rows, the person column answered as the subject; the owner's
    floor on; the patient layer's sub-switch set on. The description
    publishes `grain` with `patient_id` as the person, the patient walk
    makes the twin (several rows a person, at least 1,000 people),
    `validate` meets every check, and no real value of a person, place or
    record column stands in the description or the twin. MUTANTS: the
    patient walk's branch of `generate_held` removed (generate raises
    IndexError); the validator's patient view dropped (the person
    column's checks missed).
    """
    import csv

    import health_zoo as zoo

    monkeypatch.setattr(cli, "_PATIENT_LAYER_SHIPPED", True)

    table = zoo.table_named("prescriptions")
    folder = tmp_path / "zoo"
    result = zoo.run_table(table, folder, zoo.KPI_ROWS, zoo.seed_of(table), small_tables_refused=True)
    steps = {step: done["exit"] for step, done in result["steps"].items()}
    assert steps == {"profile": 0, "answers": 0, "generate": 0, "validate": 0}, result["steps"]
    described = json.loads((folder / "prescriptions-profile.json").read_text(encoding="utf-8"))
    grain = described["relationships"]["grain"]
    assert isinstance(grain, dict) and grain["person"] == "patient_id", grain
    assert result["misses"] == [], result["misses"]
    with open(folder / "prescriptions-twin.csv", newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    people = {row["patient_id"] for row in rows}
    assert len(rows) == zoo.KPI_ROWS and 1_000 <= len(people) < len(rows), (len(rows), len(people))
    assert result["leaks"] and all(
        entry.get("description", 0) == 0 and entry.get("twin", 0) == 0 for entry in result["leaks"].values()
    ), result["leaks"]


def _visits_text(people: int, seed: int) -> str:
    """An invented table of visits: a person on 2 to 12 rows, a ward and a group fixed for the person, a visit number, a reading."""
    draw = random.Random(seed)
    lines = ["pid,ward,group,visit,reading"]
    rows: "list[str]" = []
    for person in range(people):
        ward = draw.choice(["north", "south", "east"])
        group = draw.choice(["a", "b"])
        level = draw.gauss(100, 12)
        for visit in range(1, draw.randint(2, 12) + 1):
            rows += [f"P{person + 1:05d},{ward},{group},{visit},{round(level + 0.7 * visit + draw.gauss(0, 4), 1)}"]
    draw.shuffle(rows)
    return "\n".join(lines + rows) + "\n"


def _answered_as_the_person(questions: pathlib.Path, person: str) -> int:
    """The visits table's questions answered as the person who holds it; how many were left open and are answered now.

    The person column `identifier` (rows sharing a value are one person),
    the subject question with the person column's name, and every other
    question `no` where `no` is offered (the ward, group, visit and
    reading name no person, place, date or record).
    """
    document = json.loads(questions.read_text(encoding="utf-8"))
    answered = 0
    for entry in document["asked"]:
        if f"{entry.get('your_answer') or ''}":
            continue
        offered = [choice["answer"] for choice in entry["answers_you_can_give"]]
        if entry.get("column") == person and "identifier" in offered:
            entry["your_answer"] = "identifier"
            answered += 1
        elif "no" in offered:
            entry["your_answer"] = "no"
            answered += 1
    subject = document[asking.BETWEEN_COLUMNS].get(asking.ROWS_PER_PERSON)
    if isinstance(subject, dict) and not f"{subject.get('your_answer') or ''}":
        subject["your_answer"] = person
        answered += 1
    questions.write_text(json.dumps(document, indent=1) + "\n", encoding="utf-8", newline="\n")
    return answered


@pytest.mark.parametrize("seed", [1, 2, 3, 4])
def test_the_blocks_counted_in_patients_are_checked_on_the_twin_s_patients(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, seed: int
) -> None:
    """Generated tables of several rows a person through the shipped commands: grain stands, its blocks counted in patients are met.

    300 to 500 people of 2 to 12 rows in shuffled order, a ward and a group
    fixed for each person (two patient-fixed columns beside the person
    column), the person column answered as the person, the patient layer's
    sub-switch set on. Every column check
    of the person column and of each patient-fixed column is met: their
    blocks count patients, and the validator reads them on each patient's
    first row of the twin (`chain_validation.patients_first_rows`). The
    lines between columns are the patient walk's to meet and are not
    judged here: these tables are below the owner's floor, where a row
    family the walk's closes leave short reads MISSED (P4-D465's stated
    limits). And the patients so read are each tabled patient once, in
    the order they first stand. MUTANT: the validator's patient view
    dropped (the person column's and the fixed columns' checks missed).
    """
    from synthtwin import chain_validation, reading, validation

    monkeypatch.setattr(cli, "_PATIENT_LAYER_SHIPPED", True)
    outcomes: "list[validation.Outcome]" = []
    measure = validation.measure

    def kept(*given: object, **named: object) -> validation.Outcome:
        outcome = measure(*given, **named)  # type: ignore[arg-type]
        outcomes.extend([outcome])
        return outcome

    draw = random.Random(seed)
    tmp_path.mkdir(parents=True, exist_ok=True)
    table = fixtures.write(tmp_path, "visits.csv", _visits_text(draw.randint(300, 500), seed))
    first, said = _ran(["profile", str(table)])
    assert first.verdict == results.NO_MISS, said[-2000:]
    questions = tmp_path / "visits-questions.json"
    for _round in range(3):
        if not _answered_as_the_person(questions, "pid"):
            break
        again, said = _ran(["profile", str(table), "--answers", str(questions), "--replace-description"])
        assert again.verdict == results.NO_MISS, said[-2000:]
    described = json.loads((tmp_path / "visits-profile.json").read_text(encoding="utf-8"))
    grain = described["relationships"]["grain"]
    assert isinstance(grain, dict) and grain["person"] == "pid", said[-2000:]
    fixed = sorted(entry["column"] for entry in grain["classes"] if entry["class"] == "patient_fixed")
    assert fixed, grain["classes"]
    made, said = _ran(["generate", str(tmp_path / "visits-profile.json")])
    assert made.verdict in (results.NO_MISS, results.MISSED), said[-2000:]
    monkeypatch.setattr(validation, "measure", kept)
    checked, said = _ran(["validate", str(tmp_path / "visits-profile.json")])
    assert checked.verdict in (results.NO_MISS, results.MISSED), said[-3000:]
    assert len(outcomes) == 1
    counted = ["pid", *fixed]
    verdicts = [check.verdict for check in outcomes[0].checks if check.column in counted]
    missed = [(check.column, check.subcheck or check.fact) for check in outcomes[0].checks if check.column in counted and check.verdict == validation.MISSED]
    assert missed == [] and verdicts.count(validation.HELD) >= 10 * len(counted), (missed, len(verdicts))
    twin = reading.read_table(str(tmp_path / "visits-twin.csv"))
    keys = twin.columns[twin.column_names.index("pid")]
    found = chain_validation.patients_first_rows(twin, {}, "pid")
    assert found is not None
    seen: "dict[str, int]" = {}
    for row in range(twin.n_rows):
        if keys[row].strip(" \t") and keys[row] not in seen:
            seen[keys[row]] = row
    assert found == sorted(seen.values()) and len(found) < twin.n_rows
