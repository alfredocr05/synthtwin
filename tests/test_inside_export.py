"""Gate file of lane IN-0 (plan P4-D495): what leaves the protected computer, and the repository's own rule.

THE EXPORT copies the twin and its report and nothing else: never a
description, a questions file or a record, whatever a record's file is
called; after copying, the destination is listed and a file carrying the
marker stops the export. THE REPOSITORY: CI's sensitive-paths job runs
`tools/hooks/check_inside_records.py` on every event, which fails on any
file starting with the marker (and prints its path, never its content);
the ignore file holds the record's suffix; the repository holds no
record today. Each clause is red on its mutant (lane IN-0's report).
"""

from __future__ import annotations

import importlib.util
import pathlib
import re

import pytest

from synthtwin import inside

REPO = pathlib.Path(__file__).resolve().parents[1]
CHECKER = pathlib.Path(REPO, "tools", "hooks", "check_inside_records.py")
WORKFLOW = pathlib.Path(REPO, ".github", "workflows", "ci.yml")
RECORD_TEXT = inside.MARKER + '\n{"format":"synthtwin-inside","mode":"inside","table":{},"version":1,"zones":{}}\n'


def _checker():  # noqa: ANN202 -- the tool module, loaded from its file
    spec = importlib.util.spec_from_file_location("check_inside_records", CHECKER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _a_run_s_folder(root: pathlib.Path) -> pathlib.Path:
    out = pathlib.Path(root, "out")
    out.mkdir(parents=True)
    for name, text in (("cohort-twin.csv", "person,age\nP1,40\n"), ("cohort-twin-report.txt", "report\n"),
                       ("cohort-twin.xlsx", "PK workbook bytes\n"), ("cohort-profile.json", '{"columns": []}\n'),
                       ("cohort-questions.json", "{}\n"), ("cohort-profile.txt", "screen\n"),
                       ("cohort" + inside.SUFFIX, RECORD_TEXT), ("renamed-twin.csv", RECORD_TEXT),
                       ("renamed-twin-report.txt", "﻿" + RECORD_TEXT)):
        pathlib.Path(out, name).write_text(text, encoding="utf-8", newline="\n")
    return out


def test_the_manifest_names_the_twin_and_its_report_alone(tmp_path: pathlib.Path) -> None:
    out = _a_run_s_folder(tmp_path)
    names = [path.name for path in inside.export_manifest(out)]
    assert names == ["cohort-twin-report.txt", "cohort-twin.csv", "cohort-twin.xlsx"]


def test_the_export_leaves_no_record_behind_and_stops_on_one(tmp_path: pathlib.Path) -> None:
    out = _a_run_s_folder(tmp_path)
    outbox = pathlib.Path(tmp_path, "outbox")
    copied = inside.export(out, outbox)
    assert sorted(path.name for path in copied) == ["cohort-twin-report.txt", "cohort-twin.csv", "cohort-twin.xlsx"]
    listed = sorted(path.name for path in outbox.iterdir())
    assert listed == ["cohort-twin-report.txt", "cohort-twin.csv", "cohort-twin.xlsx"]
    assert not any(inside.carries_marker(path) for path in outbox.iterdir())
    pathlib.Path(outbox, "left-over.txt").write_text(RECORD_TEXT, encoding="utf-8", newline="\n")
    with pytest.raises(inside.InsideError, match="holds an inside record"):
        inside.export(out, outbox)


def test_the_export_s_suffixes_are_the_command_s_own() -> None:
    from synthtwin import cli

    assert inside.EXPORT_SUFFIXES == (cli._TWIN_SUFFIX, cli._WORKBOOK_TWIN_SUFFIX, cli._REPORT_SUFFIX)


def test_the_repository_s_checker_finds_a_record_and_prints_its_path_alone(tmp_path: pathlib.Path,
                                                                            capsys: pytest.CaptureFixture[str]) -> None:
    checker = _checker()
    assert checker.MARKER == inside.MARKER
    assert inside.MARKER_BYTES == inside.MARKER.encode("utf-8")
    tree = pathlib.Path(tmp_path, "checkout")
    pathlib.Path(tree, "docs").mkdir(parents=True)
    pathlib.Path(tree, "docs", "notes.md").write_text("a page that names the marker later: " + inside.MARKER + "\n",
                                                      encoding="utf-8", newline="\n")
    pathlib.Path(tree, ".git").mkdir()
    pathlib.Path(tree, ".git", "a-record-git-keeps.txt").write_text(RECORD_TEXT, encoding="utf-8", newline="\n")
    assert checker.main([str(tree)]) == 0
    pathlib.Path(tree, "docs", "cohort.json").write_text(RECORD_TEXT.replace("zones", "Zq7-canary"), encoding="utf-8", newline="\n")
    pathlib.Path(tree, "with-a-byte-order-mark.txt").write_bytes(b"\xef\xbb\xbf" + RECORD_TEXT.encode("utf-8"))
    capsys.readouterr()
    assert checker.main([str(tree)]) == 1
    printed = capsys.readouterr().out
    assert "docs/cohort.json" in printed.replace("\\", "/") and "with-a-byte-order-mark.txt" in printed
    assert "Zq7-canary" not in printed


def test_the_repository_holds_no_record_and_ignores_the_record_s_suffix() -> None:
    assert _checker().records_under(str(REPO)) == []
    ignored = pathlib.Path(REPO, ".gitignore").read_text(encoding="utf-8").splitlines()
    assert "*" + inside.SUFFIX in ignored


def _sensitive_job(workflow: str) -> str:
    job = re.search(r"^  sensitive-paths:\n(?P<body>(?:(?!  \S).*\n?)*)", workflow, re.MULTILINE)
    return job.group("body") if job else ""


def _checker_step_problems(workflow: str) -> "list[str]":
    body = _sensitive_job(workflow)
    if not body:
        return ["ci.yml has no sensitive-paths job"]
    steps = re.split(r"^      - ", body, flags=re.MULTILINE)
    mine = [step for step in steps if "tools/hooks/check_inside_records.py" in step]
    if not mine:
        return ["the sensitive-paths job no longer runs tools/hooks/check_inside_records.py"]
    if re.search(r"^\s*if:", mine[0], re.MULTILINE) or re.search(r"^    if:", body, re.MULTILINE):
        return ["the inside-record step runs only under a condition"]
    if "continue-on-error" in mine[0]:
        return ["the inside-record step cannot fail the job"]
    return []


def test_ci_runs_the_checker_on_every_event() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert _checker_step_problems(text) == []
    step = "        run: python3 tools/hooks/check_inside_records.py .\n"
    assert step in text
    assert _checker_step_problems(text.replace(step, "        run: echo skipped\n")) == [
        "the sensitive-paths job no longer runs tools/hooks/check_inside_records.py"]
    assert _checker_step_problems(text.replace(step, "        if: false\n" + step)) == [
        "the inside-record step runs only under a condition"]
