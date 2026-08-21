### 6.14 `long_tail_labels`

A column holding more different values than a set of categories may
hold, some of which are nevertheless shared by enough rows to be
named. It is rule 11 of the order in section 5.2 — tested after every
other rule but the free-text fallback — so it claims only a column
every earlier rule declined.

**The detection rule, in full.** A column takes this role when all
three of the following hold.

1. **It is past the categorical ceiling.** Its `n_distinct_folded` —
   how many different folded identities it holds, counted after
   trimming and case folding — EXCEEDS the ceiling for a table of this
   many rows: the smaller of `categorical_ceiling` and the largest
   whole number of rows lying within `categorical_share` of `n_rows`,
   never below `categorical_floor`. That is the arithmetic section
   6.6.1 states, read against the settings of section 4.4 and the
   document's own `n_rows`.
2. **No earlier rule of section 5.2's order claimed it.** This
   includes the two rules tested immediately before it, on the terms
   their own sections state: a column whose cells read as clock text
   takes `time_of_day`, and a column whose cells read as numbers
   inside one affix pair takes `affixed_number`, even where a level of
   it would clear the line in 3.
3. **At least one of its folded levels covers
   `max(small_cell_floor, long_tail_minimum_level)` rows.** Both
   settings are keys of section 4.4, so the line is on the document's
   own face and no reader has to work out which of the two produced
   it.

**A column past the ceiling with no such level is not this role, and
there is no partial form of it.** It falls through to rule 12, takes
`free_text`, and its block is exactly what the section for `free_text`
specifies: no value of the column appears anywhere in it. That is what
keeps the free-text promise literally true rather than approximately
true. An all-different or nearly all-different column — names, street
addresses, typed comments — has no level covering eleven rows at any
floor, so it stays free text at EVERY floor, and the promise is
floor-invariant.

**Why the detection line is a `max`, and never falls below eleven.**
`long_tail_minimum_level` has exactly one permitted value in this
contract, the integer `11` (section 4.4), and a loader refuses any
other. At the default floor of `11` the two terms coincide. Raising
the floor raises the detection line with it, because publishing a
floor-clearing spelling is CONSTITUTIVE of this role: a level too
small to be published must not be the level that made a column
label-publishing, so a column that cannot publish one under the
recorded settings takes the next rule instead. In a table of fewer
than eleven rows no level can meet the line at all, and the role is
unreachable there. LOWERING the floor does not lower the line:
`small_cell_floor` may be set as low as `1`, and at a floor of `1`
every level a label column holds is published, but no column becomes a
long-tail column that was not one at eleven. **A settings combination
must not be able to widen which columns publish labels at all**, and
that is the whole of what the `max` buys. Which levels of an admitted
column are then SHOWN is the floor's question and moves with it;
whether the column is admitted is this line's question and does not.

**Added keys:** the four shared label keys of section 6.3 and nothing
else — `levels`, whose entries carry exactly `label`, `count`,
`variants` and `variants_withheld` under section 6.3.1;
`suppressed_levels`; `suppressed_rows`; and `suppressed_level_counts`.
Their JSON types and meanings are section 6.3's, identically, and
`variants` and `variants_withheld` are specified in full in section
7.4: the spellings of a published label that cleared the floor are
named in its `variants`, and those that did not are counted, unnamed,
in its `variants_withheld` — exactly as on any other label role.

**`level_ceiling` is FORBIDDEN on this role.** It is `categorical`'s
own key. Its invariant, G1, is that folded distinctness is at or under
the ceiling — and that is precisely what a long-tail column violates
by definition, since condition 1 of the detection rule puts it past
the ceiling. This format has no optional keys, so the key is ABSENT
from every block of this role rather than sometimes-present, and a
loader refuses a `long_tail_labels` block that carries it. The ceiling
the column passed is recorded instead in that column's
`detection_evidence` sentence, which is a built sentence of the closed
note grammar of section 4.5.1 like every other sentence of this
document.

**Which shared label invariants reach this role: all eight of them.**
B1 through B8 are stated in section 6.3.2 over a block that carries
`levels`, not over a list of roles, so each binds a `long_tail_labels`
block identically and none needs widening or restating here: B1
(published identity is normalized), B2 (level completeness), B3 (row
completeness), B4 (the suppressed multiset), B5 (the floor, both
ways), B6 (label order), B7 (labels are distinct) and B8 (levels may
be empty).

**What B8 comes to on this role, which is not what it comes to on the
others.** B8 admits `levels == []` for a block carrying levels. On
this role that case is unreachable: the detection line is at or above
`small_cell_floor`, so a level meeting it clears the floor and cannot
be one of the below-floor levels B5 bounds — it is published — and LT1
requires that there be one. **`levels` is never empty on a
`long_tail_labels` column.** This is a consequence of LT1 and B5
together and not a rule of its own, which is why it is stated rather
than numbered.

**Invariant LT1.** At least one entry of `levels` has a `count` of at
least `max(small_cell_floor, long_tail_minimum_level)`. This is the
detection rule's third condition made checkable against a parsed
document: both settings are in the document, and the level that met
the line is one the floor could not hold back.

**Invariant LT2.** `n_distinct_folded` exceeds the categorical ceiling
the settings imply — the same number the arithmetic of section 6.6.1
computes from `categorical_ceiling`, `categorical_share`,
`categorical_floor` and `n_rows`. A loader recomputes it and refuses a
block that does not clear it.

**The two roles are checked differently, and here is why.** On
`categorical` the ceiling is a published integer and G2 makes it
LOADER-ONLY, with no invariant tying the published value to the
arithmetic. Here the key is absent, so the settings and `n_rows` are
the only ceiling the document carries, and LT2 reads them directly.
Nothing is lost by the absence: the number was never a fact about the
column's values.

**Invariant G1L.** A `long_tail_labels` block carries no
`level_ceiling`. Stated as its own invariant, and not left to the
general rule that every key not listed for a role is forbidden on it
(section 6.11), because this is the one key a reader will expect on a
role defined by its relation to the ceiling.

**Publication class: LABELS.** Its published spellings are whole
values of the table, folded, with their counts, and only where at
least `small_cell_floor` rows share them — the same bound every label
of this format carries, with no exception of its own. Section 6.10 is
the authority on the class.

**A `long_tail_labels` column is never a nothing-publishing column.**
Its `structural_role` is always `data`: the declaration is decided at
rule 2 of section 5.2's order and this rule is tested at 11, so no
declared column can reach this role. So the rules of section 6.10 that
empty `missing_by_source`, zero the two absence counts and withhold
every sentinel candidate do not reach it, and its absent cells are
accounted for under the ordinary rules of sections 5.4 and 5.5. The
column it would otherwise have been — a free-text column — is a
nothing-publishing column, so that crossing is a disclosure of its
own, and it is priced as one in this document's disclosure inventory
rather than left to be discovered.

**Disposition, and what the twin owes.** `levels`,
`suppressed_levels`, `suppressed_rows` and `suppressed_level_counts`
are EXACT-OBSERVABLE, as section 6.3.2 states for every label role:
the twin writes each published label at exactly its count and invents
that many neutral labels at exactly the held-back sizes. The published
spellings go in byte for byte, under section 7.4's own
EXACT-OBSERVABLE rule for `variants` and `variants_withheld`, fold
collisions included. There is no generation rule of this role's own,
and a label column's twin invents neutral labels rather than language.
The twin of a long-tail column therefore carries its real repeated
labels and a counted invented tail, where the free-text twin of the
same column would carry neither.

**The disclosure this role adds, priced exactly.** Two facts, and the
second is narrower than its key looks.

- **The floor-cleared label spellings**, from columns that would
  otherwise publish no value of the table at all. Bounded by the floor
  exactly as every label of this format is: nothing covering fewer
  than `small_cell_floor` rows is named. What is new is WHICH columns
  publish labels — a genuine prose column with eleven identical cells
  names that repeated sentence as a level. Two widenings of that
  sentence's own price are stated rather than left to be discovered:
  the eleven rows are ROWS and not people — the grain is undescribed,
  so eleven repeated cells may be one person's repeated records, the
  caveat this project states for every floor-guarded fact and which
  now guards sentences too; and the profiler's summary names every
  column whose labels will be visible BEFORE anything is written,
  long-tail columns included.
- **The sizes of the BELOW-FLOOR folded identities**, through
  `suppressed_level_counts`. A free-text column already publishes a
  repetition map over its raw present values, so anonymous group sizes
  are not themselves new. That map groups RAW spellings; this multiset
  groups FOLDED identities. **The additional fact is therefore exactly
  which unnamed spellings share a trim-and-case identity — counts
  only, never a spelling** — a fact about below-floor cells the
  repetition map does not carry. It is stated at this width because a
  reader who prices only the first bullet would be approving something
  this role does not do.

**Document size, stated rather than found later.**
`suppressed_level_counts` holds one integer per below-floor level, and
on this role there may be many of them: their number is bounded by
nothing but `n_rows`. No cap is imposed, because a cap would contract
a domain this format has promised, and B4's equalities would then be
unwritable.