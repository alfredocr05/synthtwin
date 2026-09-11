### 6.13 `time_of_day`

A column of clock times: an hour, a minute, and on some columns a
second, with no date beside them and no zone. It is rule 9 of the
order in section 5.2, tested after the categorical rule, so it claims
only a column every earlier rule declined.

**C6-10 (when a column takes this role).** A column at least the
parse-line count of whose present cells — and at least one of them —
match ONE AND THE SAME of exactly two clock forms, no earlier rule
having claimed it. The line is the count `minimum_parse_rate` fixes
(section 4.4), applied as a COUNT and never as a compared share, so no
rounding of a division decides a role.

| `clock_form` | the text a cell wears | fields and ranges | the form's ordinal unit | distinct spellings its space holds |
|---|---|---|---|---|
| `hh-mm` | `HH:MM` | hours `00`–`23`, minutes `00`–`59` | minutes of day, `0` to `1439` | 1,440 |
| `hh-mm-ss` | `HH:MM:SS` | hours `00`–`23`, minutes `00`–`59`, seconds `00`–`59` | seconds of day, `0` to `86399` | 86,400 |

Every field is exactly two digits, and no cell matches both forms: one
form is five characters wide and the other eight. The last column is
the size of each form's whole space, and it is what the generator's
all-different obligation is bounded by — the obligation binds through
the ordinal mechanism, and a demand no space can meet is a generator
refusal, named in the refusal catalogue rather than checked here.

**The one parsed cell is written into the rule, not left to the
invariants.** At a `minimum_parse_rate` of zero the parse-line count is
zero, so the line ALONE would hand this role every column that reached
rule 9, a column holding no clock among them; the block written for it
would then fail T4, which is a producer writing what its own loader
refuses. Requiring a cell in the detection rule is what makes T4's
reason true and what makes both endpoints real values.

**One form must clear the line; cells of the other are counted, not
fatal.** Cells of the other form, and every other present cell no
clock reading of this section accepted, are counted in `n_unparsed`
inside the slack the line leaves. An in-slack minority form is the
line's ordinary arithmetic and not a decline, exactly as one date
format must clear the line on a `datetime` column, where the cells
that format did not read are counted in that block's own `n_unparsed`.

**Where BOTH forms clear the line the finer one wins: the column takes
`hh-mm-ss`.** A cell matches at most one form, so both can clear only
where each form is worn by at least one cell and twice the parse-line
count is at most `n_present`, which a lowered `minimum_parse_rate`
permits. The tie-break is fixed here so that two producers reading one
table under one setting cannot disagree about the column's form, its
endpoints, its ladder or its unparsed count.

**C6-11 (added keys: five).** The dispositions below are section 2.2's
classes.

| key | JSON type | permitted values | meaning | disposition |
|---|---|---|---|---|
| `clock_form` | string | `hh-mm`, `hh-mm-ss` | which of the two forms the column's cells wore, and the form every published clock value of the block is written in | EXACT-CONTROL |
| `earliest` | string | a clock value in `clock_form` | the earliest clock value the column holds | EXACT-OBSERVABLE |
| `latest` | string | a clock value in `clock_form` | the latest clock value the column holds | EXACT-OBSERVABLE |
| `clock_percentiles` | ladder of strings | section 5.6, rungs in `clock_form` | the eleven-rung ladder over the ordered clock values of the cells that parsed | `min` and `max` EXACT-OBSERVABLE; the nine interior rungs APPROXIMATED |
| `n_unparsed` | integer ≥ 0 | — | present cells no clock reading of C6-10 accepted, the other form's cells among them | EXACT-OBSERVABLE as counted neutral stand-ins, explicitly OUTSIDE the parsed-value representation obligation |

`clock_percentiles` is a ladder in the shape section 5.6 fixes: an
OBJECT with exactly the eleven keys `min`, `p01`, `p05`, `p10`, `p25`,
`p50`, `p75`, `p90`, `p95`, `p99`, `max`, no more and no fewer — never
an array. The rungs are NAMED rather than positional, as `percentiles`
and `date_percentiles` are, because the generator pins `min` and `max`
by name and a positional array would make the two ends a counting
convention.

##### The ordinal, the endpoints and the ladder

A clock value's ORDER is its ordinal in the unit its own form sets:
minutes of day for `hh-mm`, seconds of day for `hh-mm-ss`, exactly as
a datetime column's recorded `resolution` sets the unit its own ladder
is filled in. The endpoints and every rung are written as TEXT in that
form, never as ordinals; both forms being fixed-width and zero-padded,
the text order and the ordinal order agree, which is why T3 is
checkable without arithmetic on the fields, and why every value an
interpolation can reach has exactly one canonical spelling and no
generated cell is truncated or widened to fit.

The producer's ladder is SELECTION: eleven order statistics of cells
the column really holds, no interpolation anywhere in it, as the date
ladder is built. The GENERATOR interpolates: it pins rank 0 and the
last rank to the published ends and fills the interior ranks by the
same floor-division interpolation the date rule uses, in the form's own
ordinal unit. It is always satisfiable, because the ends are real cells
of a closed finite space and every interior value floor-divides between
them in that same unit. Every cell of the twin's parsed population is
written in the column's one published form, and the generation report
names each achieved interior rung beside the published one, as every
APPROXIMATED fact is reported.

**A consequence of T1, stated rather than left to be discovered.** No
rung of `clock_percentiles` is ever `null`. A `percentiles` rung may be
null because a loader accepts a rung it cannot rule out as a value
outside binary64, rather than refusing a document over that case; every
rung here is a value some cell held and has a spelling in its form, so
the case cannot arise — exactly as it cannot on `date_percentiles`.

##### C6-12: the invariants

**Invariant T1.** Every published clock value — `earliest`, `latest`
and all eleven rungs — is written in the form `clock_form` names.

**Invariant T2 (the ladder ends ARE the two endpoints).**
`clock_percentiles.min == earliest` and `clock_percentiles.max ==
latest`.

**Invariant T3.** `clock_percentiles` is non-decreasing in
seconds-of-day, read in ladder order.

T2 and T3 are stated because the generation rule rests on them, and
they are this role's analogue of D11, which pins the datetime ladder to
its endpoints, and of L1, which holds the two older rung sets
non-decreasing. Left untied, a hand-made document could publish a
ladder end below `earliest`; a generator pins its first cell to
`earliest` and interpolates inside the ladder, so the twin would hold
clock values EARLIER than the endpoint it published, and describing
that twin again would give back a different `earliest` with nothing
said about it.

**Invariant T4.** `n_unparsed < n_present`. Where every present cell is
unparsed the column has no parsed cell and cannot reach this role at
all — C6-10 requires one — so both endpoints are always real values.

**Invariant T5.** `n_present − n_unparsed` is at least the parse-line
count of `n_present` — the count `minimum_parse_rate` fixes, applied as
a count — so a block whose one form never cleared the detection line
cannot conform. T4 is not implied by T5 and is stated beside it: at a
`minimum_parse_rate` of zero the parse-line count is zero, and T5 alone
would admit a block with no parsed cell.

**T-P (a producer obligation, stated because a loader cannot check
it).** Every published clock value is a value some cell of the source
held.

**TU-P (a producer obligation, stated because a loader cannot check
it).** `n_unparsed` is the count of present cells that no clock reading
of C6-10 accepted. **T4 and T5 bound it from both sides and neither
reaches the measurement itself: a loader holds one document and never
the table it describes, so it cannot recompute this number.** Two
documents can satisfy every checkable row here and disagree about what
the source held. Against the TWIN the count is EXACT-OBSERVABLE, the
unparsed cells being written back as counted neutral stand-ins.

##### Four readings this role refuses, each stated as a rule

1. **A fractional part on the seconds field does not parse.** This role
   publishes no key that could record one — the datetime role carries
   `subsecond_digits` for exactly that purpose and this role does not
   import it — so a clock reading that accepted such a cell would
   silently drop the fraction and approximate every cell of the column.
2. **A seconds field of `60` does not parse.** The ordinal spaces above
   have no faithful point for a leap second. The datetime role admits
   `SS` of `60`, on the strength of an endpoint construction that
   publishes an instant's own FIELDS rather than an ordinal; this role
   publishes ordinals and does not import that machinery, so it refuses
   the reading rather than carry a value it would move to the following
   minute.
3. **A single-digit hour does not parse.** Both forms are fixed-width,
   which is what merits the two properties named above; a variable width
   would give one ordinal two spellings.
4. **Two clock forms in one column are not read as one column's
   clock.** There is no JOINT clock reading: one form carries the
   column and the other form's cells are counted in `n_unparsed`; where
   neither carries it, the column declines to the later rules. The
   datetime role has a joint reading across ISO resolutions because
   that mix is the dominant export shape; clock-precision mixes are
   not, so this version takes the narrow reading and names the joint
   one as the candidate for a later widening, on the resolution-mix
   precedent.

Each refusal sends the column on to the later rules, where — if nothing
later claims it — it is declined with the competing-readings remark,
whose clock argument names how many of its cells a clock reading
accepted under the form that came closest (section 4.5, form
`remark_no_reading_fits`). All four are named residual R-P4-5.

##### C6-13: the model, stated where the fact carries it

**The ladder reads the day as a LINE from `00:00` to `23:59:59`**, as
every ladder reads its axis. A column whose values cluster across
midnight is therefore described as two edge clusters with an empty
middle, and a twin's interior interpolation fills that middle with
values the source never held. The rungs are exact values of real cells
either way; the clock face's circular reading is not modeled, exactly
as a two-humped numeric column's valley is not.

##### C6-14: the publication class

**Ranges. No exception of its own.** The ranges class publishes no
spelling of the table; what it publishes are order statistics computed
from the values. The one named exception to its "no spelling appears"
sentence is C6-9's, confined by the forbidden-key matrix to the two
affix keys of `affixed_number`, and no key of a `time_of_day` block
carries shared cell text under that exception or under anything else.

**Its endpoints and its rungs publish exact values of real cells,
floor-free, under the ranges-class endpoint policy** — the same policy
that publishes a numeric column's `min` and `max` and a datetime
column's `earliest` and `latest`. No floor governs them and none is
consulted before they are written. Because such a column published
nothing under version 5, this is a NEW disclosure and the inventory of
section 12 prices it: clock endpoints and rungs stand there beside the
affixed cores and the newly-claimed calendar endpoints, and
`clock_form` with `n_unparsed` have a row of their own — the first says
which written form the cells wore, the second counts the cells no clock
reading accepted; neither carries a value, both carry a shape and a
count of the table.

##### What a `time_of_day` block does NOT carry

Every key not listed above is FORBIDDEN on this role, and a loader
refuses one it finds, naming the key and the column. The ones a reader
will look for:

- **The datetime block's other ten keys** — `format`, `resolution`,
  `resolution_mix`, `time_precision`, `subsecond_digits`,
  `datetimes_read_at`, `earliest_utc_offset`, `latest_utc_offset`,
  `utc_offsets`, `date_percentiles`. The two forms of C6-10 carry no
  date, no offset and no fractional part, so there is nothing for those
  fields to record; they are ABSENT, not null and not withheld, because
  this format has no optional keys.
- **The quantitative set** — `percentiles`, `mean`, `std`, `skew` and
  the rest — which stands on `count`, `continuous` and `affixed_number`
  and nowhere else. A clock value is an ordinal, not a quantity, and no
  mean of one is published.
- **The per-column `n_rows` echo**, confined by Q1 to those same three
  roles, and `numeric_styles` with `fraction_widths` beside it,
  required on those three and forbidden on every other role.
- **The four label keys and `level_ceiling`**: this is a ranges-class
  role and publishes no level.

`earliest`, `latest` and `n_unparsed` are the three key names this role
shares with `datetime`. They ask the same question of two domains:
there the endpoints are canonical instants at the recorded `resolution`
and `n_unparsed` counts cells no date format read; here they are clock
values written in `clock_form` (T1) and `n_unparsed` counts cells no
clock reading accepted.

##### The remarks this role carries

**None of its own.** No form of the note grammar is bound to this role,
and the clock argument of `remark_no_reading_fits` belongs to a column
that DECLINED, not to one that took the role. Its axes are fixed with
every other role's — `statistical_type` `time_of_day`, `quality_state`
`ok`, `structural_role` `data`, no column named with `--identifier`
being able to reach rule 9, since the declaration is decided at rule 2
— and its `detection_evidence` sentence is built from the grammar like
every other sentence of this document.