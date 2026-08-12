"""Stage 1 of the Phase 3 claim migration: no private-mode claim survives.

The Phase 3 plan (P3-D7, migration table) retires every sentence that
describes the repository as private or describes a control as deferred
because the repository is private. The claim inventory cannot police
this: its surface list deliberately excludes ``.github/`` and
``tools/``, and the retired forms lived exactly there too. So this test
walks the ENTIRE tracked tree.

Scope, stated per the plan: historical records are excluded by name --
``CHANGELOG.md`` and everything under ``docs/plans/`` record what was
true on their own dates, and this file's own pattern table would
otherwise match itself. Everything else tracked must be free of every
retired stage-1 form, and the five governance surfaces must carry the
flip vocabulary that replaced them.
"""

from __future__ import annotations

import pathlib
import subprocess

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]

# The retired stage-1 forms, matched on lowercased text with whitespace
# runs collapsed -- the claim inventory's own normalization, reused so
# a line wrap cannot hide a form.
RETIRED_PRIVATE_MODE_FORMS = (
    "temporarily private",
    "private for now",
    "private today",
    "while the repository is private",
    "while the repo is private",
    "deferred while the repository is private",
    "until the repository becomes public",
    "deferred until the repository becomes public",
    "not allowed for private repositories",  # quoting the API is fine ONLY
    # in SECURITY.md's structural-refusal explanations; see the allowance
    # below.
)

# Exactly one file may still quote the two API refusal strings, because
# SECURITY.md states WHY the controls could not exist earlier by
# quoting the API's own errors. Nothing else may.
API_QUOTE_ALLOWANCE = {"SECURITY.md": ("not allowed for private repositories",)}

# The surfaces that must now carry the flip vocabulary.
FLIP_BEARING = (
    "AGENTS.md",
    "CLAUDE.md",
    "README.md",
    "SECURITY.md",
    "CONTRIBUTING.md",
)
FLIP_MARK = "visibility flip"

# Historical records: excluded because they state what was true on
# their own dates, and rewriting history is exactly what this project
# refuses to do.
EXCLUDED = ("CHANGELOG.md",)
EXCLUDED_PREFIXES = ("docs/plans/",)
SELF = "tests/test_p3_flip_migration.py"


def _tracked_files() -> list[str]:
    listing = subprocess.run(
        ["git", "ls-files"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return [line for line in listing.stdout.splitlines() if line]


def _normalized(path: pathlib.Path) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    return " ".join(text.lower().split())


def test_no_retired_private_mode_form_survives_outside_the_records() -> None:
    """Every tracked file outside the named records scans clean."""
    offenders: list[str] = []
    for relative in _tracked_files():
        if relative in EXCLUDED or relative == SELF:
            continue
        if any(relative.startswith(prefix) for prefix in EXCLUDED_PREFIXES):
            continue
        text = _normalized(REPO_ROOT / relative)
        for form in RETIRED_PRIVATE_MODE_FORMS:
            if form in text:
                allowed = API_QUOTE_ALLOWANCE.get(relative, ())
                if form in allowed:
                    continue
                offenders.append(f"{relative}: {form!r}")
    assert offenders == [], (
        "A retired private-mode sentence survives on a live surface. "
        "Stage 1 of the Phase 3 migration (plan P3-D7) retires these "
        "forms everywhere outside the historical records: "
        + "; ".join(offenders)
    )


def test_the_governance_surfaces_carry_the_flip_vocabulary() -> None:
    """The five governance surfaces name the flip and its record."""
    for relative in FLIP_BEARING:
        text = _normalized(REPO_ROOT / relative)
        assert FLIP_MARK in text, (
            f"{relative} no longer names the visibility flip; the "
            "repository-status story must live on every governance "
            "surface (plan P3-D7, stage 1)."
        )
    assert "activation record" in _normalized(REPO_ROOT / "SECURITY.md"), (
        "SECURITY.md must name the activation record that carries the "
        "flip's API confirmations (plan P3-D8.0)."
    )


def test_this_battery_can_fail() -> None:
    """Vacuity check: the matcher finds a seeded retired form."""
    seeded = "the repository is TEMPORARILY   private for now"
    normalized = " ".join(seeded.lower().split())
    assert any(
        form in normalized for form in RETIRED_PRIVATE_MODE_FORMS
    ), "the matcher no longer recognizes its own retired forms"
