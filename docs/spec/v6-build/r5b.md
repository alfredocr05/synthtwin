### 6.13 `time_of_day`

A column of clock times written with no date beside them: an hour, a
minute, and on some columns a second. It is rule 9 of the order in
section 5.2, tested after the categorical rule, so it claims only a
column every earlier rule declined — in particular only one the
datetime rule did not read, that rule running at 6 and reading a clock
only as the tail of a date.

#### When a column takes this role

**C6-10.** At least the parse-line count of the column's present cells
match ONE of the exactly two clock forms below, and no earlier rule
claimed the column. The line is the count `minimum_parse_rate` fixes
(section 4.4), applied as a COUNT and never as a compared share, so
that no rounding of a division decides a role; the arithmetic of the
count itself is section 4.5.2's.

| `clock_form` | the text a cell wears | fields and ranges | the form's ordinal unit | spellings |
|---|---|---|---|---|
| `hh-mm` | `HH:MM` | hours `00`–`23`, minutes `00`–`59` | minutes of day, `0` to `1439`: 60 × `HH` + `MM` | 1,440 |
| `hh-mm-ss` | `HH:MM:SS` | hours `00`–`23`, minutes `00`–`59`, seconds `00`–`59` | seconds of day, `0` to `86399`: 3600 × `HH` + 60 × `MM` + `SS` | 86,400 |

Every field is exactly two digits, and no cell matches both forms. The
fixed width is what gives each ordinal exactly one spelling, and what
makes plain text comparison of two cells agree with their clock order.
Both are load-bearing: the first is why every value an interpolation
can reach has a canonical spelling in the column's own form and no
generated cell is ever truncated or widened to fit, the second is why
the ladder can be checked as written text. These are also the two
forms the `month-first-datetime` and `day-first-datetime` members of
the format vocabulary read as the tail of a slashed date; they are
enumerated here and nowhere else.

**One form must clear the line; cells of the other are counted, not
fatal.** This is the datetime rule's arithmetic transposed, where one
date format must clear the line. Cells of the other clock form, and
every other present cell no clock reading accepted, are counted in
`n_unparsed` inside the slack the line leaves. An in-slack minority
form is the line's ordinary arithmetic and not a decline.

**Where BOTH forms clear the line, the finer wins: the column takes
`hh-mm-ss`.** A cell matches at most one form, so both clear only
where twice the parse-line count is at most `n_present`, which a
lowered `minimum_parse_rate` permits and a high one does not. The
tie-break is fixed here so that two producers reading one table under
one setting cannot disagree about the column's form, its endpoints,
its ladder or its unparsed count. Under it the `HH:MM` cells are the
ones counted in `n_unparsed`.

#### Four readings this role refuses, each a rule and not an omission

1. **A fractional part on the seconds field does not parse.** This
   role publishes no key that could record one — `subsecond_digits` is
   `datetime`'s and is not imported — so a reading that accepted such
   a cell would silently drop the fraction and thereby approximate
   every cell of the column.
2. **A seconds field of `60` does not parse.** The ordinal spaces
   above have no faithful point for a leap second. `datetime` accepts
   an `SS` field of `60` on its local-clock endpoints, on the strength
   of an endpoint construction that publishes an instant's own FIELDS
   rather than an ordinal; this role publishes ordinals and does not
   import that machinery, so it refuses the reading rather than carry
   a value it would have to move to the following minute.
3. **A single-digit hour does not parse.** Both forms are fixed-width,
   which is what merits the two properties above; a variable width
   would give one ordinal two spellings.
4. **Two clock forms in one column are not read as one clock.** There
   is no JOINT reading: one form carries the column and the other
   form's cells are counted in `n_unparsed`, and where neither carries
   it the column declines to the later rules. `datetime` has a joint
   reading across ISO resolutions because that mix is the dominant
   export shape; clock-precision mixes are not, so this version takes
   the narrow reading and names the joint one as the candidate for a
   later widening, on the resolution-mix precedent.

Each refusal sends the column to the later rules, where — if nothing
later claims it — it is declined with the competing-readings remark,
whose clock argument names how many cells a clock reading accepted
under the form that came closest (section 4.5, `remark_no_reading_fits`).
All four are named residual R-P4-5.

#### Added keys: five

| key | JSON type | permitted values | meaning | disposition |
|---|---|---|---|---|
| `clock_form` | string | `hh-mm`, `hh-mm-ss` | which form the column's cells wore, and the form every published clock value of the block is written in | EXACT-CONTROL |
| `earliest` | string | a clock value in `clock_form` | the earliest clock value the column holds | EXACT-OBSERVABLE |
| `latest` | string | a clock value in `clock_form` | the latest clock value the column holds | EXACT-OBSERVABLE |
| `clock_percentiles` | ladder of strings | section 5.6, rungs in `clock_form` | the eleven-rung ladder over the ordered clock values of the cells that parsed | `min` and `max` EXACT-OBSERVABLE; the nine interior rungs APPROXIMATED, inside the window the generation method's approximated-fields table fixes for this role |
| `n_unparsed` | integer ≥ 0 | — | present cells no clock reading of C6-10 accepted, the other form's cells among them | EXACT-OBSERVABLE as counted neutral stand-ins, explicitly OUTSIDE the clock representation obligation |

**C6-11.** Those five are the whole of what this role adds to the
twenty-two universal keys of section 5.1. A container's disposition
does not cover its leaves (section 2.2), which is why the ladder's
ends and its interior are disposed separately.

`clock_percentiles` is a ladder in the shape section 5.6 fixes: an
object with exactly the eleven keys `min`, `p01`, `p05`, `p10`, `p25`,
`p50`, `p75`, `p90`, `p95`, `p99`, `max`, no more and no fewer. The
rungs are NAMED rather than positional, as `percentiles` and
`date_percentiles` are, because the generator pins `min` and `max` by
name and a positional array would make the two ends a counting
convention. The ladder is SELECTION — eleven order statistics of cells
the column really holds, with no interpolation in it.

#### The ordinal, the endpoints and the ladder

A clock value's ORDER is its ordinal in the unit its own form sets:
minutes of day for `hh-mm`, seconds of day for `hh-mm-ss`. That is the
datetime role's resolution-sets-the-unit rule transposed to the clock,
and it is what keeps every value an interpolation can reach inside the
column's one published form. Endpoints and rungs are written as TEXT
in that form, never as ordinals; because both forms are fixed-width
and zero-padded the two orders agree, so T3 is checkable without
arithmetic on the fields.

**A consequence of T1, stated rather than left to be discovered.** No
rung is ever `null`. `percentiles` admits a null rung because an
interpolated numeric rung can fall outside binary64; every rung here
is a value some cell held and every such value has a spelling in its
form, exactly as on `date_percentiles`.

#### Invariants

**T1 (one form, everywhere in the block).** Every published clock
value — `earliest`, `latest` and all eleven rungs — is written in the
form `clock_form` names, every field in two digits and in the ranges
that form's row gives.

**T2 (the ladder ends ARE the endpoints).** `clock_percentiles.min ==
earliest` and `clock_percentiles.max == latest`. Both pairs describe
the same two values, all four built from one ordering of the same
cells, and both ends are EXACT-OBSERVABLE. It is stated because the
generation rule rests on it: a generator pins its first and last ranks
to the endpoints and interpolates inside the ladder, so an untied pair
would let a document publish a ladder end below `earliest`, produce a
twin holding values earlier than the endpoint it published, and
re-describe with a different `earliest` and nothing said about it.
This is the analogue of D11, which pins the datetime ladder.

**T3 (non-decreasing).** Read in ladder order — `min`, `p01`, `p05`,
`p10`, `p25`, `p50`, `p75`, `p90`, `p95`, `p99`, `max` — the values
never decrease in seconds of day. Minutes of day and seconds of day
put the same values in the same order, and both agree with plain text
comparison of the written rungs, so an `hh-mm` ladder is checked by
this one rule and not by a second. Stated for T2's reason: the
generation rule rests on it. It is the reading L1 takes on this field.

**T4 (at least one cell parsed).** `n_unparsed < n_present`. This is
NOT implied by T5: `minimum_parse_rate` may be `0.0`, at which the
parse-line count is zero and T5 is vacuous, and T4 is then the only
rule keeping a cell for the endpoints and the ladder to be values of.
A column with no parsed cell cannot reach this role at all, so both
endpoints are always real values.

**T5 (the detection line, checkable afterwards).** `n_present -
n_unparsed` is at least the parse-line count of `n_present` — the
count `minimum_parse_rate` fixes, applied as a count — so a block
whose one form never cleared the detection line cannot conform.

**T-P (a producer obligation, stated because a loader cannot check
it).** Every published clock value is a value some cell of the source
column held. A loader holds one document and never the table.

**TU-P (the same, for the count).** `n_unparsed` is the count of
present cells no clock reading of C6-10 accepted, and **a loader
cannot recompute it.** Its own type bounds it below at zero; T4 and T5
bound it above — T5 the tighter of the two wherever the parse-line
count is at least one — and neither reaches the measurement: two
documents can satisfy every checkable rule of this section and
disagree about how much of the source read as a clock. The
measurement is the producer's obligation, checked by the
producer-side tests, and it is written down here so that no consumer
reads T4 and T5 as more than the bounds they are.

#### The model the ladder rests on, stated where the fact carries it

**C6-13.** The ladder reads the day as a LINE from `00:00` to
`23:59:59`, as every ladder reads its axis. A column whose values
cluster across midnight is therefore described as two edge clusters
with an empty middle, and a twin's interior interpolation fills that
middle. The rungs are exact values of real cells either way. The clock
face's circular reading is not modeled — exactly as a two-humped
numeric column's valley is not — and this is a bound of the ladder
model rather than a defect of this role.

#### Publication class, and the floor-free endpoints

**C6-14.** `time_of_day` is a RANGES-class role (section 6.10): no
spelling of the column appears in the block, and order statistics
computed from its values do. It carries no exception of its own — the
one named exception to the ranges class is `affixed_number`'s two
affix keys, and section 6.11 confines it there.

**The endpoints and the eleven rungs are exact values of real cells,
published FLOOR-FREE, and that is a disclosure rather than a
formality.** No `small_cell_floor` governs an endpoint or a rung: a
clock value one single cell held is published if it is the smallest,
the largest, or the cell an order statistic lands on. That is the
ratified ranges-class endpoint policy, the same one `datetime`,
`count` and `continuous` endpoints already have, and it newly reaches
columns that were free text and published no value at all. The
disclosure inventory prices it, and prices `clock_form` and
`n_unparsed` beside it: those two carry a shape and a count of the
table, but no value of it.

This role is not a nothing-publishing column, so its absent-cell
accounting is published under the floor exactly as N3 and N6 have it
for every column that is not.

#### The keys forbidden on this role

Every key not listed above is FORBIDDEN, universal or role-specific,
and a loader refuses one, naming the key and the column. The
forbidden-key matrix of section 6.11 carries the same listing for this
role and for the other twelve; three groups are named here because a
reader will expect them and their absence is a decision.

- **The other ten datetime keys.** `format`, `resolution`,
  `resolution_mix`, `time_precision`, `subsecond_digits`,
  `datetimes_read_at`, `earliest_utc_offset`, `latest_utc_offset`,
  `date_percentiles` and `utc_offsets` are `datetime`'s. `clock_form`
  answers the form question here, and a clock with no date carries no
  zone: an offset moves an instant, and this role publishes none.
- **Every quantitative key.** `percentiles`, `mean`, `std`, `skew`,
  `numeric_styles`, `fraction_widths`, `integer_valued` and the rest
  belong to `count`, `continuous` and `affixed_number`, as does the
  per-column `n_rows` echo, which Q1 confines to those three.
- **Every label key.** `levels`, `suppressed_levels`,
  `suppressed_rows` and `suppressed_level_counts` belong to the four
  labels-class roles, and `level_ceiling` to `categorical` alone. This
  role is in neither place.

`earliest`, `latest` and `n_unparsed` are the three names this role
shares with `datetime`. They ask the same question of a different
domain: here the endpoints are clock values in `clock_form` rather
than canonical instants at a recorded resolution, and `n_unparsed`
counts cells no CLOCK reading accepted rather than cells no date
format read.

#### The remarks it carries, and the one it does not

This role raises no note form of its own. The clock clause of the
competing-readings remark belongs to a column this rule DECLINED and
no later rule claimed; it is written on that column's block, never on
a `time_of_day` one. Like every column, a `time_of_day` block carries
a `detection_evidence` sentence built from the closed note grammar of
section 4.5, and carries any remark whose trigger its values reach.

#### What the twin owes

Rank 0 and the last rank are pinned to `earliest` and `latest`; the
interior ranks are interpolated by floor division between them in the
ordinal unit the published form itself sets, so every value written
has a canonical spelling in that one form. Every present cell is
written in `clock_form`, and the `n_unparsed` cells are written as
counted neutral stand-ins and counted on the surfaces that say what
was invented. The interpolation is always satisfiable: the two ends
are real values of a closed finite space and every interior value
floor-divides between them in that same unit.

Where the column publishes `n_distinct == n_present` the all-different
obligation binds on this role, and it binds through that same ordinal
mechanism — distinct ordinals, distinct spellings. This is not one of
the places the obligation cannot bind; what it has instead is a
capacity, because the ordinal space is finite, and that is the one
place a description of this role can be infeasible. The unparsed
stand-ins come from an unbounded text family and supply distinctness
of their own, so the shape no twin can hold is a description whose
distinct demand NET of them — `n_distinct - n_unparsed` — exceeds the
form's 1,440 or 86,400 spellings.

**Such a document is a VALID description and a loader accepts it.**
The conflict is decided at the generation-feasibility stage, which
runs after the loader and before any cell is built, and it is refused
there by name: it is the one refusal this role adds to the generation
method's closed list of generation refusals, which stood at four. The
message says the profile is valid, names the two published facts that
cannot both hold, and gives remediation that does not assume the
person still holds the table. Only that shape is refused. A
description whose own source met every published count, unparsed cells
included, is never refused by this rule.