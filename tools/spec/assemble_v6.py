'''Assemble the version 6 contract from its section files.

The sections are written and checked independently -- that is what lets
each be verified against source without its checker holding the whole
document in mind -- and this script is where they become one document.
It is kept because the assembly is not a one-time act: a repair lands in
a section and the document is rebuilt, so that no fix ever exists only
in the assembled copy.

Run  over the result. It must report zero
items before the document is called finished.
'''
from pathlib import Path

B = Path("docs/spec/v6-build")
ORDER = [
    ("s1", "scope, authority, completeness; terms"),
    ("s3", "encoding and canonical serialization"),
    ("s4", "the document: top level and settings"),
    ("s45", "publication notes, the note grammar, relationships"),
    ("s5", "the column block: universal keys and the axes"),
    ("a7a_53", "the multiplicity map"),
    ("s5b", "the vocabulary, the absent cells, verdicts, the ladder"),
    ("r1", "the roles; empty; numeric_unrepresentable"),
    ("r2", "the label roles; constant; binary"),
    ("r3", "categorical and datetime"),
    ("r4a", "count and continuous"),
    ("r4b", "identifier and free_text"),
    ("r6", "the publication class and the forbidden-key matrix"),
    ("r5a", "affixed_number"),
    ("r5b", "time_of_day"),
    ("r5c", "long_tail_labels"),
    ("a7a_72", "multiplicity parity and the relationship manifest"),
    ("a7b1", "label spelling variants"),
    ("a7c", "numeric styles and fraction widths"),
    ("a7d", "the twin reproduces the recorded hole spellings"),
    ("a8a", "every invariant, part one"),
    ("a8b1", "every invariant: the value-bearing families"),
    ("a8b2", "every invariant: the new roles and the producer obligations"),
    ("a9", "the disposition matrix"),
    ("a10a", "the loader"),
    ("a10b", "the version rule, the refusals, the message"),
    ("a14", "capacity, the disclosure inventory, the decisions"),
    ("a14app", "appendix: every enumeration in one place"),
]

HEADER = """# Profile contract, version 6 — the normative specification

**Status:** revision 6, 2026-08-21 — the first COMPLETE statement of
this format. **Not ratified.** It is reviewed adversarially before the
implementation it anchors is written, under the standing process:
plans and specifications before the artifacts they anchor. It joins
the disposition seal at its own landing.

**This document is self-contained.** It carries nothing by reference
from version 4 or version 5, replaces nothing by name, and holds no
table of replacements. Every rule, key, enumeration, invariant,
disposition and loader obligation that governs a version 6 description
is written HERE, at its own wording, once. Section 1 states that rule
and what it cost.

**Authority.** The Phase 4 plan `docs/plans/phase-4-columns.md` is the
authority for every decision here; this document is the normative
statement of what a version 6 description may contain. Where the two
disagree the plan governs and this document is defective. The plan's
amendments A-P4-1 through A-P4-12 are part of the ratified text this
document transcribes.

**Versions 4 and 5 keep their sealed text** and keep governing the
descriptions written under them. Nothing here edits what they require.

---

"""


def build() -> int:
    missing = [n for n, _ in ORDER if not (B / f"{n}.md").exists()]
    assert not missing, f"missing sections: {missing}"
    parts = []
    for name, subject in ORDER:
        body = (B / f"{name}.md").read_text(encoding="utf-8").strip()
        parts.append(f"<!-- {name}: {subject} -->\n\n{body}")
    text = HEADER + "\n\n---\n\n".join(parts) + "\n"
    Path("docs/spec/profile-contract-v6.md").write_text(text, encoding="utf-8")
    return len(ORDER)


if __name__ == "__main__":
    print(f"assembled {build()} sections")
