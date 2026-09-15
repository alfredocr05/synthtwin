"""The shipped version 6 contract passes its own mechanical checks.

WHY THIS FILE EXISTS (residual R-P4-113). `tools/spec/check_assembly.py`
was written to settle what a reader cannot: that every identifier the
contract defines is defined once, and that every identifier it cites is
defined somewhere. It read the section files under `docs/spec/v6-build/`
by default -- a folder that stopped moving on 2026-08-26 and was deleted,
with its assembler, when R-P4-113 closed -- and nothing ran it on the
document that ships. On that document it reported seventeen items.
Seven were real -- C6-32, C6-33 and C6-96 each named two different
rules, and invariants Q16 to Q19 were cited and never written -- and ten
were the checker not knowing three shapes the document defines in: a
rule named in prose ("its identifier is Q20"), a rule opened as a bullet
or part way along a line, and a LANDING name (`landing L16`) that reads
as an invariant of the `L` family.

A checker that reports false items teaches its reader to ignore it, so
the three shapes were taught to the checker before the zero was
demanded, and the tests below hold each one to what it recognises.
"""

import importlib.util
import pathlib

CONTRACT = pathlib.Path("docs/spec/profile-contract-v6.md")
TOOL = pathlib.Path("tools/spec/check_assembly.py")

_spec = importlib.util.spec_from_file_location("check_assembly", TOOL)
assert _spec is not None and _spec.loader is not None
check_assembly = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check_assembly)


def _items(path: pathlib.Path) -> "list[str]":
    paths = check_assembly._sections(path)
    return check_assembly.check_identifiers(paths) + check_assembly.check_framing(
        paths
    )


def _copy(tmp_path: pathlib.Path, text: str) -> pathlib.Path:
    target = tmp_path / "profile-contract-v6.md"
    target.write_text(text, encoding="utf-8", newline="\n")
    return target


def test_the_shipped_contract_reports_zero_items() -> None:
    assert _items(CONTRACT) == []


def test_the_command_passes_on_the_shipped_contract(capsys) -> None:
    import sys

    before = sys.argv
    sys.argv = ["check_assembly.py", f"{CONTRACT}"]
    try:
        code = check_assembly.main()
    finally:
        sys.argv = before
    assert code == 0
    assert "1 sections, 0 items" in capsys.readouterr().out


def test_a_duplicated_identifier_is_reported(tmp_path: pathlib.Path) -> None:
    """The vacuity check: one identifier opened twice turns it red."""
    text = CONTRACT.read_text(encoding="utf-8")
    # Inside a section of its own: text past the last marker belongs to
    # the enumeration appendix, which restates rules by design.
    text += (
        "\n<!-- zz: a later section -->\n\n"
        "**C6-122 (a second rule under a used number).** Text.\n"
    )
    items = _items(_copy(tmp_path, text))
    assert any("DUPLICATE IDENTIFIER C6-122" in item for item in items), items


def test_a_second_prose_definition_is_reported(tmp_path: pathlib.Path) -> None:
    """A prose name counts as a definition, so naming it twice collides."""
    text = CONTRACT.read_text(encoding="utf-8")
    text += "\n<!-- zz: a later section -->\n\nOne binds, and its identifier is Q20.\n"
    items = _items(_copy(tmp_path, text))
    assert any("DUPLICATE IDENTIFIER Q20" in item for item in items), items


def test_a_cited_invariant_nobody_wrote_is_reported(tmp_path: pathlib.Path) -> None:
    text = CONTRACT.read_text(encoding="utf-8")
    opener = "**Invariant Q18 (`mode` and `mode_count` stand together).**"
    assert text.count(opener) == 1
    text = text.replace(opener, "The pair stands together.")
    items = _items(_copy(tmp_path, text))
    # The one-list table still restates Q18, so the checker names it
    # as restated but never stated; the citations resolve against that
    # row. Either sentence is the defect being caught.
    assert any(
        "Q18" in item and ("cites" in item or "NEVER STATED" in item)
        for item in items
    ), items


def test_the_three_definition_shapes_are_recognised(tmp_path: pathlib.Path) -> None:
    text = "\n".join(
        [
            "One binds, and its identifier is Q20. Conditions follow.",
            "",
            "- **P9c (the sum).** Bounded on both sides.",
            "",
            "The census binds the same thing. **P5b (the sum).** Let F be.",
            "",
            "This was repaired at landing L16, and again at landing",
            "L19, citing Q20, P9c and P5b.",
            "",
        ]
    )
    assert _items(_copy(tmp_path, text)) == []


def test_a_case_and_a_list_are_not_definitions(tmp_path: pathlib.Path) -> None:
    """`**P5b.a` is a case of P5b; `**P6c, P7c` discusses two rules."""
    text = "\n".join(
        [
            "**P5b (the sum).** Let F be.",
            "",
            "- **P5b.a — a key is published.** F equals it.",
            "",
            "- **P6c.** A floor.",
            "- **P7c.** A width.",
            "",
            "**P6c, P7c and P5b do not reach the producer**: they bound it.",
            "",
        ]
    )
    assert _items(_copy(tmp_path, text)) == []


def test_a_landing_name_is_struck_only_after_the_word_landing(
    tmp_path: pathlib.Path,
) -> None:
    """`L7` with no `landing` before it is still a citation to resolve."""
    text = "The ladder rule L7 binds here.\n"
    items = _items(_copy(tmp_path, text))
    assert any("cites L7" in item for item in items), items


def test_the_checker_reads_the_shipped_contract_by_default(
    monkeypatch, capsys
) -> None:
    """R-P4-113 closed with the assembled contract as the only source.

    The build folder the checker once read by default is deleted, so a
    default still naming it would stop the tool with "no such folder";
    run with no argument, it must check the document that ships and find
    nothing wrong there.
    """
    monkeypatch.setattr("sys.argv", ["check_assembly.py"])
    assert check_assembly.main() == 0
    assert "1 sections, 0 items" in capsys.readouterr().out
