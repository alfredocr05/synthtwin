"""The contract must describe every document the producer writes.

WHY THIS FILE EXISTS. On 2026-08-26 an adversarial re-check of an
unrelated residual found that the producer wrote NINETEEN settings keys
while the contract's membership rule said seventeen and its key list
said eighteen, and that the fourteenth role -- `joined_numbers` -- and
three of its keys appeared ZERO times in the governing contract. So
every description the tool wrote was a document that contract does not
describe, which is precisely what C6-20 exists to make impossible.

Two landings caused it and neither was careless in an obvious way:
`--code` corrected the key list and not the membership clause, and
`--measurement` corrected neither. What let both through is that
NOTHING COMPARED THE TWO. The suite held the contract to itself and the
code to itself; no test asked whether the code writes what the contract
describes.

These are those tests. They are deliberately about NAMES and COUNTS
rather than about meaning: a name the producer emits and the contract
never mentions is a defect whatever it means, and it is exactly the
defect that got through.
"""

import pathlib
import re

from synthtwin import contract

REPO = pathlib.Path(__file__).resolve().parent.parent
CONTRACT = REPO / "docs" / "spec" / "profile-contract-v6.md"

_WORDS = {
    13: "thirteen",
    14: "fourteen",
    15: "fifteen",
    16: "sixteen",
    17: "seventeen",
    18: "eighteen",
    19: "nineteen",
    20: "twenty",
}


def _said() -> str:
    return CONTRACT.read_text(encoding="utf-8")


def test_every_settings_key_the_producer_writes_is_in_the_contract() -> None:
    """A key the producer emits that the contract never names."""
    said = _said()
    missing = sorted(
        key for key in contract.SETTINGS_KEYS if f"`{key}`" not in said
    )
    assert missing == [], (
        "these settings keys are written into every description and are "
        f"named nowhere in the contract that governs it: {missing}"
    )


def test_the_membership_rule_counts_the_keys_the_producer_writes() -> None:
    """C6-20 states the count in words, and it must be the real one.

    It said seventeen while the producer wrote nineteen, and a loader
    written from the contract would have refused two keys every
    description carries.
    """
    said = _said()
    total = len(contract.SETTINGS_KEYS)
    word = _WORDS[total]
    pattern = re.compile(r"\*\*C6-20 \(membership\)\.\*\* All ([A-Z]+) keys")
    found = pattern.search(said)
    assert found is not None, "C6-20's membership sentence is not there"
    assert found.group(1).lower() == word, (
        f"C6-20 says {found.group(1)} settings keys and the producer "
        f"writes {total} ({word})"
    )


def test_the_key_list_names_every_settings_key() -> None:
    """Section 14's list is the other place the count is stated."""
    said = _said()
    total = len(contract.SETTINGS_KEYS)
    found = re.search(r"\*\*`settings` keys — (\d+)\*\*", said)
    assert found is not None, "the settings key list is not there"
    assert int(found.group(1)) == total, (
        f"the key list says {found.group(1)} and the producer writes "
        f"{total}"
    )
    start = said.index("**`settings` keys —")
    listing = said[start : start + 1200]
    absent = sorted(
        key for key in contract.SETTINGS_KEYS if f"`{key}`" not in listing
    )
    assert absent == [], f"the key list omits {absent}"


def test_every_role_the_producer_can_give_is_in_the_contract() -> None:
    """A role the contract never mentions is a role nobody can consume.

    `joined_numbers` shipped in the code and appeared nowhere in the
    contract at all -- not in the role list, not in the axis table, not
    in the forbidden-key matrix -- so a consumer written to the
    contract would meet a role it had never been told about.
    """
    said = _said()
    missing = sorted(role for role in contract.ROLES if f"`{role}`" not in said)
    assert missing == [], (
        f"these roles can be given to a column and the contract that "
        f"governs the document never names them: {missing}"
    )


def test_every_role_key_the_producer_can_write_is_in_the_contract() -> None:
    """Every key of every role, by name.

    `part_agreements`, `part_above` and `part_min_widths` were written
    into descriptions while appearing nowhere in the contract.
    """
    said = _said()
    missing: "list[str]" = []
    for role in contract.ROLES:
        for key in contract._role_keys(role):
            if f"`{key}`" not in said and key not in missing:
                missing = missing + [key]
    assert sorted(missing) == [], (
        f"these role keys are published and the contract never names "
        f"them: {sorted(missing)}"
    )


def test_the_role_count_stated_in_words_is_the_real_one() -> None:
    """The contract says the count in prose, in several places."""
    said = _said()
    total = len(contract.ROLES)
    word = _WORDS[total]
    stale = _WORDS[total - 1]
    for phrase in (
        f"one of the {word} role names",
        f"one of the {word} statistical types",
        f"total over the {word} roles",
    ):
        assert phrase in said, f"the contract does not say {phrase!r}"
        assert phrase.replace(word, stale) not in said, (
            f"the contract still says {stale} where it means {word}"
        )
