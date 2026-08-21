### 7.7 The twin reproduces the recorded hole spellings

Every version of this format before this one wrote every absent cell
of a twin as an empty field, and reproduced no absent-value spelling
anywhere. That is no longer true of the file this version's generator
produces, and this part states what replaces it. It is one rule, in
one place, because a twin's absent cells are written by one
construction whatever role the column took.

**C6-115 (the write rule).** A version 6 twin writes, per column:

1. each `missing_by_source` spelling at exactly its published count —
   EXCEPT a spelling a JUDGED PASS put there, which stays blank;
2. every other absent cell empty: the blank count, the withheld
   remainder, and every judged-pass-sourced cell;
3. all of them placed by the same single permutation that places
   everything else, with spellings assigned to absent slots in a fixed
   sorted order before the permutation runs.

A judged pass is either of the two this version has: the stand-in
number pass, and the calendar placeholder pass of 6.6.4.

**C6-116 (why judged-pass cells stay blank).** A reproduced TEXT
spelling is read back as absence by a fixed rule of the description
alone — it is a member of the published vocabulary (5.4.1), or a value
the person named with `--missing-value`, and either way the reading
does not depend on the twin's own values. A stand-in NUMBER is that
rule's named exclusion, and a CALENDAR PLACEHOLDER is excluded for
exactly the same reason: the absence reading of both runs through the
producer's outlier-and-share judgement over the measured file's own
values, which a twin's generated distribution is not guaranteed to
re-fire.

Reproducing those cells would make the twin's own measurement
contingent on a re-judgement; leaving them blank keeps every
reproduced cell's reading deterministic. **Nothing the description
records is lost by it**: the twin's report names, per column, the
stand-in cells, the placeholder cells and the below-floor spellings
that were not reproduced.

**C6-117 (declaration wins, on every pass).** Where a person named a
value with `--keep-value`, that value is data and no judged pass may
read it as a hole — the numeric pass, the calendar pass and the
published vocabulary alike. A cell rescued that way is a PRESENT cell:
its spelling reaches `missing_by_source` for no column, and the twin
writes it wherever its column's publication rules put a value.

**C6-118 (the collision rule, with no runtime escape).** No PRESENT
cell of a twin may wear a spelling the description publishes as a hole
source for its column. If it could, a twin would hold a cell that
reads as absent to the rule of C6-116 while standing where a value
belongs, and the file would describe itself two ways.

The generation method carries the written proof that no construction
is ever forced onto such a spelling. **A shape outside that proof is a
defect of the method, found at review** — it is never a deviation
printed at run time. That distinction is the whole of this clause: a
rule a generator may break and then report is not a rule, and this one
holds by construction or the method is wrong.

**The SUM identity this creates.** Because the construction writes
several pools of absent cells as empty fields, no per-field equality
holds between the twin's blank cells and any single published count.
What holds is a sum: the twin's recounted blank absent cells equal
`n_missing_blank` plus `n_missing_withheld` plus the judged-pass-
sourced count, over BOTH judged passes. An identity naming only the
stand-in pass would be false by construction on any column carrying
judged calendar placeholders, and a validator checking it would report
a failure against a correct twin — which is worse than no check,
because it teaches its reader to stop believing the report.
