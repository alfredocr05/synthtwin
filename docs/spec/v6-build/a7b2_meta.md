VERDICT SOUND_WITH_CORRECTIONS errors=16

## ERRORS

1. ENUMERATION, both directions, PASSES. v4 7.4.3 states exactly seven W invariants: W1 (profile-contract-v4.md:1505), W2 (:1509), W3 (:1514), W4 (:1517), W5 (:1521), W6 (:1526), W7 (:1531). Seven in source, seven in the section, same identifiers, same subjects, none invented, none dropped. Wording of W3, W6 and W7 is verbatim. STATED REASONS in that range number FOUR, not seven: W2 (:1511-1512), W4 (:1519), W6 (:1527-1529), W7 (:1532-1534). W1 (:1505-1507), W3 (:1514-1515) and W5 (:1521-1524) are bare. The submission's provenance ("each with the reason stated there") and its gaps ("W3 ... the only one of the seven with a bare statement") both miscount: three are bare, not one.

2. ERROR — INVENTED REASON. W1's second sentence in the section ("a spelling of a label the description refuses to name may not appear beside its count under some other key") is in no source. v4:1505-1507 states W1 with no reason at all. A sourced ground for the same point exists at profile-contract-v4.md:1550-1551 — "The delta is bounded to the spelling forms of labels the profile ALREADY publishes" — and the corrected text uses that wording instead. Fixed in `corrected`.

3. ERROR — INTERNAL CONTRADICTION, and a false claim about the source. C6-114 says "None of them names a role." W1 names one, at profile-contract-v4.md:1507: "and on every non-label role". The section's own later paragraph then quotes it back — "W1's forbidden half — 'every non-label role'". The r2.md sentence this was modelled on (docs/spec/v6-build/r2.md:45-48) is true of B1-B8 and false of W1, because B1-B8 have no forbidden half. Corrected to: none names a PUBLISHING role, and W1 alone reaches outside the entry, to the complement — every block that publishes no `levels`.

4. ERROR — OVERSTATES THE LOADER, against shipped code, and contradicts the section's own next sentence. C6-115 says "a loader refuses on each by name" of six invariants. src/synthtwin/contract.py `_variants` (:3583-3628) raises exactly five by name: W5 (:3589), W2 (:3597), W3 (:3604), W7 (:3614), W4 (:3623). W1 is raised by NO name: contract.py:497-499 records it as "enforced by the key sets", and the actual refusal comes from `_keys(block, seat, LEVEL_KEYS, ...)` at contract.py:3494, naming the offending key. Corrected to name the five, and to say W1 is decided but not by name.

5. ERROR — SILENTLY REWORDED REASON. W5's ground in the section reads "because a spelling is held to the line a label is held to". The source clause is profile-contract-v4.md:1551-1553: "because each variant is governed by the same floor as any published label" — the same wording the shipped producer carries at src/synthtwin/taxonomy.py:3089-3092. Restored verbatim; the paraphrase drops the operative fact (same floor) for a metaphor.

6. ERROR — CITES IDENTIFIERS NO SECTION OF THIS BUILD DEFINES. The section cites "the multiplicity-map key form, M1 through M4 (section 5.3)". Section 5.3 as written (docs/spec/v6-build/a7a.md:7-20) folds key form, key range, value range and the empty map into `C6-90` as four unlettered bullets, and defines only M1 (:22-23) and M2 (:25-26). M3 and M4 survive only in summary tables — profile-contract-v4.md:1887-1888 and docs/spec/v6-build/a8a.md:114-115 — so citing them fails ASSEMBLY.md standing check 2 ("no rule referenced by identifier without being stated somewhere in this document"). Corrected to "the multiplicity-map form, and M1 and M2 as they bind `variants_withheld`". THE ASSEMBLER MUST STILL RECONCILE a8a.md:114-115 with a7a.md's C6-90.

7. ERROR — DUPLICATES A SIBLING. "the forbidden-key matrix, which admits `levels` on no other role" restates docs/spec/v6-build/r2.md:7 word for word. Corrected to a bare pointer at sections 6.3.1 and 6.11 (the matrix's home, docs/spec/v6-build/r6.md:165).

8. ERROR — DUPLICATES A SIBLING. "because writing the surviving value once gives shorter text" restates the round-trip table row at docs/spec/v6-build/a10a.md:135 ("the parse keeps one value; re-serializing writes the key once, so the text is shorter than the file"). Corrected to point at the check (R10) and stop.

9. ERROR — SELF-DUPLICATION. The section states the no-widening claim twice: C6-114 ("not one of them is restated, widened or excepted for any role") and again in the standalone paragraph ("Nothing in this family counts the roles, so no W invariant is widened, restated or excepted for the fourth one"). Merged into C6-114 in `corrected`; the `long_tail_labels` conclusion is kept there.

10. DISAGREEMENT WITH SHIPPED CODE (carried forward, not resolved). An out-of-range `variants_withheld` key is refused inside `_multiplicity`, whose docstring names the bound "W5" (src/synthtwin/contract.py:1965-1968) but whose raise goes through `_out_of_range` (:2015-2016) and whose own error list attributes it to R16 (:1978-1979). The refusal-code table maps R16 to "a value outside its range or enumeration" (docs/spec/v6-build/a10b.md:72). Section 5.3 as written also attributes the bound to W5 (docs/spec/v6-build/a7a.md:34). Two conforming loaders will refuse the same document and name different rules. The contract must say which identifier the refusal carries; no artifact settles it, so it is an owner call.

11. DISAGREEMENT WITH A WRITTEN SECTION (confirmed, both halves). docs/spec/v6-build/a8a.md:121 states W1 as "`variants` and `variants_withheld` appear on published level entries only", dropping W1's forbidden half over every non-label role, and its "loader? yes" column (:121, :126) marks W1 and W6 flatly decidable. contract.py:497-499 says both are enforced only by the key sets and the canonical round trip. a8a's two rows need repair against C6-115.

12. CONFLICT CONFIRMED, and it is WIDER than the submission reports. profile-contract-v4.md:1455 states the appearance rule over a ROLE LIST — "REQUIRED on every entry of `levels` on the three label roles and FORBIDDEN everywhere else" — and there are now FOUR label roles (profile-contract-v6.md:346-349; docs/plans/phase-4-columns.md:945-947). The submission cites this as v4:1442-1444, which is 7.4.1's heading and opening, not the sentence. The SAME defect sits a second time in v4's additions register at profile-contract-v4.md:2570 ("every published level entry on the three label roles"), which the submission does not name. Both belong to the shape/register authors and must be written over a block that carries `levels`, as r2.md:45-48 already does.

13. CONFLICT CONFIRMED. profile-contract-v4.md:1469 ("Values are integers >= the floor") restates W5's first clause in the wire-shape section. The shape author should point at W5. Line number in the submission (implied 7.4.2 bullet) is right; the exact line is :1469.

14. GAP CONFIRMED, and it bears on an enumeration elsewhere. The producer obligation this section states — that a `variants` key is the spelling the file held byte for byte — is the exact twin of N7, which docs/spec/v6-build/a14.md:555-561 counts as one of TWO producer obligations stated as invariants a loader cannot check (N7 and K5). The `variants` obligation is stated as a wire rule at 7.4.2 (a14.md:398-407, 13.5) and carries no invariant identifier. The corrected text points at 7.4.2 rather than restating the rule; if the owner wants it as an invariant, a14's count of two must change with it.

15. GAPS 2 AND 3 VERIFIED AS STATED. src/synthtwin/canonical.py:110-131 applies no Unicode normalization (`sort_keys`, `indent=2`, fixed separators, `ensure_ascii=False`, `allow_nan=False`), so W6's "a character the canonical form does not distinguish" names an empty producer-side case under the shipped writer; v4's wording is left intact and the question referred to the owner. src/synthtwin/parsing.py:364-375 is `text.strip().casefold()`, and docs/spec/v6-build/s1.md:169 says only "trimming and a Unicode `casefold()`" — the character set trimming removes is fixed nowhere, and W2 and B1 both ride on it. Section 2.3 owns the repair.

16. NUMBERING (noted, not an error in this section). C6-114 and C6-115 are free today — docs/spec/v6-build/a10a.md:200 reaches C6-113 — but independently written sections restart their own numbering, so both need the single assembly renumbering pass (ASSEMBLY.md section 2). No `C6-` letter identifier, no delta framing, and none of the scanned words ("supersedes", "carried", "unchanged from version 5") appears in the corrected text; verified by grep.

## GAPS

- Version 4 states no REASON for W3 — it is the only one of the seven with a bare statement (v4 line 1517-1518). I transcribed it bare rather than making up one. The shipped loader does check W3 separately and before W4, so its refusal names the offending spelling rather than the closure sum, but that is an implementation fact, not a stated reason; if the contract wants a reason it has to come from the owner.
- What 'a character the canonical form does not distinguish' names in W6 is fixed by no artifact I read. The shipped canonical serializer applies NO Unicode normalization (src/synthtwin/canonical.py `serialize`, lines 110-131: sorted keys, indent 2, fixed separators, `ensure_ascii=False`, `allow_nan=False`), so under that writer no two byte-different spellings collapse into one key and W6's producer-side case is empty. Either the clause means something a second implementation could reproduce, or it should be dropped to the plain statement that keys are distinct. I left v4's wording intact.
- The character set 'trimming' removes is not fixed anywhere I found. s1.md line 169 says 'trimming and a Unicode `casefold()`'; the shipped fold is `str.strip().casefold()`, which removes Python's whitespace set including U+00A0 — a second implementation using an ASCII-only trim would compute a different folded identity and could accept or refuse a `variants` key W2 decides the other way. W2 and B1 both ride on it; the terms section owns the fix, not this one.
- The numbers C6-114 and C6-115 are provisional. Independently written sections restart their own numbering (a10a already reaches C6-113, a7a C6-92, r4b C6-82), so both need renumbering in the single assembly sequence. If the assembler prefers the r2.md precedent — unnumbered framing prose beside a family of lettered invariants — both paragraphs can lose their identifiers without losing content.

## CONFLICTS NOTED

- THE PREMISE IS TRUE OF THE INVARIANTS AND FALSE OF THE SHAPE. Version 4 section 7.4.3 states W1-W7 over a level entry, so all seven reach `long_tail_labels` with no widening — the brief's claim holds. But version 4 section 7.4.2 (lines 1442-1444) states where the keys may appear over a ROLE LIST: 'REQUIRED on every entry of `levels` on the three label roles and FORBIDDEN everywhere else'. With `long_tail_labels` there are FOUR. Transcribing that sentence as written would forbid the two keys on the very role v6's C6-16 requires them on (profile-contract-v6.md lines 346-349; phase-4-columns.md lines 946-947). The shape author owns the sentence and must write it over a block carrying `levels`, as r2.md already does for B1-B8.
- SHAPE RESTATES W5's FIRST HALF. Version 4 7.4.2's `variants` bullet says 'Values are integers >= the floor', which is exactly W5's first clause stated a second time in a second place — the duplication this rewrite exists to end. The shape should point at W5 and stop.
- SHIPPED LOADER CITES A DIFFERENT RULE THAN THE ONE THAT OWNS IT. An out-of-range `variants_withheld` key is refused inside `_multiplicity` under R16, not W5 (src/synthtwin/contract.py: docstring at lines 1965-1968 says the bound is 'W5', the raise at 2015-2020 goes through `_out_of_range`, and the docstring's own error list attributes it to R16). Two implementations refuse the same document and name different rules to the user, and the a10b refusal-code table maps R16 to a message about a key out of range rather than about the floor. The contract should say which identifier the refusal carries.
- a8a.md OVERSTATES W6's DECIDABILITY AND UNDERSTATES W1. Its table (lines 121-127) marks every W 'loader? yes' flatly. W6 is decidable only through the canonical round trip R10 — the parsed value has already lost the duplicate — and a bare 'yes' sends an implementer looking for an entry-level check that cannot exist. Its W1 row also drops W1's second half, the forbidden side on every non-label role, keeping only 'appear on published level entries only'.

## SOURCES

W1-W7 transcribed element by element from profile-contract-v4.md
lines 1505-1546 (section 7.4.3), each with the reason stated there;
W5's disclosure reason from v4 7.4.5 (lines 1560-1568, "no variant
crosses the boundary that a whole label would not"). Seven stated,
seven transcribed.

Loader decidability checked against shipped code, not inferred:
src/synthtwin/contract.py `_variants` (lines 3571-3627) raises W2, W3,
W4, W5, W7 by name; `_multiplicity` (1955-2043) bounds
`variants_withheld` keys at `floor - 1`; contract.py lines 497-499
state that W1 and W6 "are enforced by the key sets and by the
canonical round trip: a repeated key cannot survive it"; `_parsed`
(1410-1431) fills no pairs hook, and the round-trip docstring
(1505-1523) lists "a duplicated key" among the seven defects one check
catches. R10 is the round-trip refusal code (v6-build/a10a.md line 24,
a10b.md line 66; v4 lines 2312, 2486).

Producer side: src/synthtwin/taxonomy.py `_variants` (3040-3102) names
a spelling only at `count >= settings.small_cell_floor` and pools the
rest through `_multiplicity_map` (4144-...), matching W5.

Folded identity: v6-build/s1.md line 169 ("trimming and a Unicode
`casefold()`"); shipped fold is `text.strip().casefold()`,
src/synthtwin/parsing.py lines 364-375.

Fourth label role: v6-build/r2.md lines 1-46 (the four label roles
share the block; B1-B8 "stated over a block that carries `levels`, not
over a list of roles"; 6.3.1 gives the entry its four keys and defers
`variants`/`variants_withheld` "in full" to 7.4); profile-contract-v6.md
C6-16 (lines 346-349); phase-4-columns.md lines 946-947.

Ownership boundaries respected: disposition EXACT-OBSERVABLE is a9.md
line 165; exact-storage of `variants` keys and the required-even-when-
empty rule are a14.md 13.5 and 13.6 (lines 398-414); S13 and the
reserved-word carve-out are s4.md lines 366-412; the multiplicity map
is s3.md/5.3.