### 5.4 The absent cells: the vocabulary, two maps and two counts

Every column block says how many of its cells held no value, and then
says it again three more ways: by the REASON the cell was counted
absent, by the SPELLING the cell wore, and by two counts standing
beside the spelling map for the cells no spelling could name. The four
answer different questions and none replaces another.

#### 5.4.1 The published vocabulary

**C6-31 (the closed list).** The published vocabulary is the set of
values synthtwin itself reads as "no value" or judges as a stand-in,
without anybody naming them. It is a closed list of THREE parts, and
its size is stated here because every surface that counts it must
count the same number:

- **EIGHTEEN text spellings** read as "no value". Seventeen are
  matched after trimming and a Unicode case fold: the ten plain
  spellings — the empty spelling, `-`, `--`, `.`, `?`, `n/a`, `na`,
  `nan`, `none`, `null` — and the seven spreadsheet error literals
  `#DIV/0!`, `#N/A`, `#NAME?`, `#NULL!`, `#NUM!`, `#REF!`, `#VALUE!`.
  The eighteenth, `NaT`, is matched by raw byte equality with the
  cell, with no trimming and no case folding.
- **THREE stand-in numbers**: −9999, −999, 9999, written on the wire
  as `-9999.0`, `-999.0` and `9999.0`.
- **TWO calendar placeholders**: `1900-01-01` and `9999-12-31`.

**Twenty-three members in all.** Extending any of the three parts is a
change to this contract and advances `profile_version`.

**This list is synthtwin's own.** It is the same in every
installation, it contains no text from any table, and a document
naming one of its members in a declaration record therefore discloses
something about a command line rather than about a column.

**C6-32 (why one member is matched differently).** A difference in a
matching rule is the kind of thing a reader must not have to infer, so
it is stated rather than left to the code. Every folded member's
folded form collides with no human word. `NaT`'s does: folded, it is a
person's name, so admitting it under the folded rule would silently
read name cells as absent.

It therefore joins as the vocabulary's one exact-spelling member, and
that one operation — raw byte equality — is applied identically
wherever the vocabulary is consulted: recognizing a cell as absent;
recording which members a declaration named; **the test of whether a
declaration names a vocabulary member and so rescues a cell that this
list would otherwise make absent**; the published-vocabulary tests;
and the validator's reconstruction. The rescue test is named
explicitly because leaving it to be inferred is how the kept-side
completeness proof (8.4) came to be carried with one of its six ways
unproved.

The criterion that keeps `unknown` and `missing` OUT of this list — a
human word carries meaning somewhere — stands unweakened for every
folded member.

#### 5.4.2 `missing_by_class` — by reason

An object with exactly these SIX keys, always all six, on every column
block of every role, each an integer at least 0:

| key | meaning |
|---|---|
| `(blank)` | the cell was empty or held only spaces |
| `(date-sentinel)` | a calendar placeholder the column-level pass of 6.6.4 judged to mean "no value" |
| `(declared-missing)` | the person named this value with `--missing-value` |
| `(numeric-sentinel)` | a stand-in number the column-level rule judged to mean "no value" |
| `(text-code)` | one of the spellings of the published vocabulary (14.9) |
| `(withheld)` | the pooled remainder of the classes above whose own counts fell below the floor |

**Invariant N1.** The six values sum to `n_missing`.

**Invariant N2.** A class other than `(withheld)` is either 0 or at
least `small_cell_floor`. A class whose real count fell between 1 and
the floor is pooled into `(withheld)` and reads 0 here. `(withheld)` is
exempt from the floor in both directions: it is the remainder the named
counts were pooled out of, and one remainder may pool several classes.

**These keys are a closed first-party enumeration** into which no text
of anybody's table can land, so they carry no collision to close. That
is what separates this map from the next one.

#### 5.4.3 `missing_by_source` — by spelling

An object mapping an exact absent-value spelling to how many rows of
this column held it. Every key is a spelling that at least
`small_cell_floor` rows shared, written character for character as the
file held it, having passed through the display boundary that turns a
line, control or bidirectional formatting character into a printable
form that shows itself (2.4).

**It carries no `(blank)` key and no `(withheld)` key.** Those two are
`n_missing_blank` and `n_missing_withheld`, fields of their own beside
it, and 5.4.4 says why the split matters.

**Invariant N3 (the source accounting closes).** On a column that is
not a nothing-publishing column (6.10):

```
sum(missing_by_source.values()) + n_missing_blank + n_missing_withheld
    == n_missing
```

On a nothing-publishing column, `missing_by_source` is `{}`,
`n_missing_blank` is 0 and `n_missing_withheld` is 0, whatever
`n_missing` is. Naming a spelling there would publish a value out of a
column that publishes none.

**Invariant N4.** Every value of `missing_by_source` is at least
`small_cell_floor`, with no exemption, and `n_missing_blank` is 0 or at
least the floor. `n_missing_withheld` is bounded in neither direction,
for N2's reason.

**Invariant N5 (the keys are the TABLE's).** No key of
`missing_by_source` carries a first-party meaning — not the six class
words of 5.4.2, and not any other name this format uses,
`n_missing_withheld` and `n_sentinel_candidates_unpublished` among
them. A cell can hold those words too, and a column publishing
`missing_by_source: {"n_missing_withheld": 2}` says that two cells of
the table held exactly those eighteen characters. `levels[].variants`
is the other map the table keys, and a rule that finds this format's
fields by searching a document for names must stop reading a key as a
name inside both.

**Invariant N6.** `n_missing_blank` and `n_missing_withheld` are 0 on
exactly the nothing-publishing columns. That class is a function of
`role` and `structural_role`, both of which every block publishes, so a
consumer can decide it from the document alone.

**Invariant N7 (producer).** A `missing_by_source` key is the source
spelling character for character. A loader holds one document and never
the table it describes, so it cannot check that the spelling published
is the spelling a cell wore.

#### 5.4.4 Why the blank count and the blank CLASS are two numbers

`n_missing_blank` is not the same number as
`missing_by_class["(blank)"]`, and neither replaces the other. The
class count is pooled when the CLASS falls below the floor; the field
is pooled when the SPELLING — here, blankness — falls below it. A
column can therefore publish a class count of zero and a blank count of
forty, or the reverse, and both readings are correct about different
questions. Both are published, in two fields, because a field that
carried both could not be read.

**The dispositions of all four are section 9's**, and they are not the
same: this version reproduces recorded hole spellings in the twin,
which is what makes one of these maps checkable against written bytes
and leaves the others as report facts.

### 5.5 A sentinel verdict entry

`sentinel_verdicts` is an array, possibly empty, of objects each having
exactly these four keys:

| key | JSON type | permitted values |
|---|---|---|
| `candidate` | string | the stand-in number as text; the canonical ISO day spelling of a calendar placeholder (6.6.4); or exactly `(withheld)` |
| `verdict` | string | `read_as_missing`, `kept_as_a_number` |
| `reason` | string | `outlier_and_frequent`, `not_an_outlier`, `too_rare`, `too_few_other_values`, `kept_by_you` |
| `n_occurrences` | integer ≥ 1 | how many rows held the candidate |

**Invariant V1.** Every entry has `n_occurrences` at least
`small_cell_floor`. Candidates below the floor are not listed at all;
they are counted, unnamed, in `n_sentinel_candidates_unpublished`. That
count is the one field of this format that records a thing held back in
its NAME rather than under the `(withheld)` word, and at a floor of one
it is zero under S13, because no candidate can be below one.

**Invariant V2.** `candidate` is `(withheld)` on exactly the columns
where `missing_by_source` is `{}` for N3's reason — a column whose
publication class permits no value of the table anywhere in its block.

**Invariant V3.** `verdict` is `read_as_missing` only when `reason` is
`outlier_and_frequent`. The other four reasons all keep the candidate
as an ordinary value of the column.

**Invariant V4 (the order, total over all three kinds of candidate).**
Entries appear in this order, and the rule is exhaustive over the
candidates this version permits:

1. candidates that are NUMBERS, ascending by the number;
2. candidates that are CALENDAR DAY SPELLINGS, ascending by the
   candidate text — which, for the canonical ISO day spelling, is also
   ascending by date. These follow every numeric entry;
3. candidates that read `(withheld)`, ordered by `n_occurrences`, then
   `verdict`, then `reason`, so that no position can say which of two
   withheld candidates is the smaller.

The three groups appear in that order wherever a block carries more
than one of them. A block never in fact mixes group 3 with groups 1 or
2, because withholding is a property of the whole block and not of a
single entry; the group order settles the mixed case that CAN arise —
numeric together with calendar — and states the rest so a reader need
not infer it. A rule that ordered only the mixed case would leave a
calendar-only block ordered by nothing at all, and the same declared
inputs would canonicalize to different bytes.

### 5.6 The ladder

Two fields carry a ladder: `percentiles` on the numeric roles and
`date_percentiles` on `datetime`. Both are objects with exactly the
eleven keys `min`, `p01`, `p05`, `p10`, `p25`, `p50`, `p75`, `p90`,
`p95`, `p99`, `max`, no more and no fewer.

**Invariant L1 (non-decreasing).** Read in ladder order — `min`, `p01`,
`p05`, `p10`, `p25`, `p50`, `p75`, `p90`, `p95`, `p99`, `max` — the
values never decrease. For `percentiles` the comparison is numeric; for
`date_percentiles` it is plain text comparison, which is why the
canonical datetime forms are chosen to sort as text (6.6.2).

**Invariant L2 (endpoints).** `min` is the smallest value and `max` the
largest. They are the two rungs the generator pins by fixed rule, and
they are EXACT-OBSERVABLE while the nine interior rungs are
APPROXIMATED (section 9).

**Invariant L3 (null rungs).** A `percentiles` rung may be `null`, and
means the exact rung is not a finite binary64 value. No producible
profile is known to reach this — every interpolated rung lies between
two finite neighbours and is therefore finite — but a loader accepts
`null` rather than refusing a document over a case it cannot rule out,
and a generator treats a null rung as carrying no obligation at that
rung and says so in the report. **The value a generator uses in its
place is fixed by `docs/spec/generation-method-v1.md` G5.1**, so a null
rung is one rule and not two: the loader accepts it here, the method
says what is written for it there, and neither document leaves it to an
implementation. `date_percentiles` rungs are never null.
