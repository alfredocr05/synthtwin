"""Stage 2: three independent writings of thousands grouping agree.

WHY THREE. The generator writes a thousands separator with
`parsing.with_group_separator`. If the validator checked a twin with that
same function, a defect in it would be a defect in both, and the check
could never see it. So the validator groups with a function of its own,
`validation._grouped_text`, and the independent oracle that freezes the
reference vectors groups with a third, `_group_thousands` in
`tools/reference/make_generation_reference_vectors.py`, which imports
nothing it checks. The three walk the figures three different ways: the
generator counts the first group from the left, the validator walks from
the right, and the oracle reverses and cuts in threes. They can agree
only where all three are right.

WHY THE ZEROS. When a column needs more distinct spellings than its
values supply, a cell raises its leading-zero order, and the first
version of this repair grouped those zeros too: `+0,001,234` and
`001,234.5`, a padded field wearing a separator. Review of this landing
did not catch it; a probe did. The mark reaches a cell only at order
zero, and the oracle and the generator are held to agreeing on that.

Rule amendment A-P4-59 is why this file exists at all: any generator
rule that moves is mirrored in the independent oracle in the same
commit.
"""

import pathlib
import random
import runpy

from synthtwin import generation, parsing, validation

ORACLE = (
    pathlib.Path(__file__).resolve().parent.parent
    / "tools"
    / "reference"
    / "make_generation_reference_vectors.py"
)


def _oracle() -> "dict[str, object]":
    return runpy.run_path(str(ORACLE))


def _spellings(count: int) -> "list[str]":
    """Seeded written numbers: signed, unsigned, whole and fractional."""
    draw = random.Random(20260914)
    written: "list[str]" = []
    for _ in range(count):
        sign = draw.choice(["", "-", "+"])
        whole = str(draw.randrange(0, 10 ** draw.randrange(1, 11)))
        fraction = f".{draw.randrange(0, 1000)}" if draw.random() < 0.5 else ""
        written += [sign + whole + fraction]
    return written


def test_the_three_groupers_agree_on_every_spelling() -> None:
    """Generator, validator and oracle write the same grouped text."""
    group_in_oracle = _oracle()["_group_thousands"]
    for text in _spellings(5000):
        expected = parsing.with_group_separator(text, ",")
        assert validation._grouped_text(text, ",") == expected, (
            f"the validator groups {text!r} differently from the generator"
        )
        assert group_in_oracle(text, ",") == expected, (  # type: ignore[operator]
            f"the oracle groups {text!r} differently from the generator"
        )


def test_a_raised_cell_carries_no_mark_in_the_generator_or_the_oracle() -> None:
    """The mark reaches a cell only at leading-zero order zero."""
    styled = _oracle()["styled_spelling"]
    cases = (
        ("plain", 1234.0, 0, True),
        ("leading_plus", 1234.0, 0, True),
        ("leading_plus", 1234.0, 3, True),
        ("decimal", 1234.5, 0, False),
        ("decimal", 1234.5, 2, False),
        ("decimal", -98765.25, 0, False),
    )
    for style, value, order, whole in cases:
        written = generation._styled_number(value, style, order, whole, -1, -1, ",")
        assert styled(style, value, whole, order, ",") == written, (  # type: ignore[operator]
            f"oracle and generator disagree on {style} at order {order}"
        )
        if order > 0:
            assert "," not in written, (
                f"{style} at order {order} grouped the zeros it spent: {written!r}"
            )
