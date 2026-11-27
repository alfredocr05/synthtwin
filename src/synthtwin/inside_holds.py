"""THE HOLDS NARROWED FOR THE INSIDE RECORD (lane IN-7, plan P4-D501): a column or a spelling is held only as an identifier or a Safe Harbor element.

WHY. The description holds back what a shared page could not show: a
level 1 to 10 people hold is pooled or listed by a fixed rule, a column
whose identifier question was answered otherwise may still be held as
record numbers when a few people write it another way (plan P4-D486
(6)(a)). The inside record never leaves the computer and the twin is
the only thing Safe Harbor binds (the owner, 2026-11-15 and 2026-11-18):
an ordinary value merely present in the twin -- a rare diagnosis, a
rare level, a rare number -- discloses nothing. So the record, read
inside at describe time, narrows those holds; the twin keeps every Safe
Harbor rule: identifiers are made up, never a real one (the description's
twin's own), dates are the dates zone's, ages are capped at 90.

WHAT IT NARROWS.

* `carried_spec`: a label column the relations zone models (an ordinary
  label: not an identifier, no Safe Harbor top code, no key) carries
  every real spelling of its `LEVEL_CAP` commonest that the product's
  readers let through (`held_spelling`): not a person's details, a date,
  an age, a run of `FIGURE_RUN` figures or more (a record number, a ZIP
  code); the description's published spellings stay carried as before.
  The relations zone may then model any of them as a level and draws
  the rest from their real counts (`inside_relations.encode_label`).
  A column whose name says it holds an identifier element carries
  nothing new.
* `narrowed_spec`: a column the description holds as record numbers
  although the person answered it a measurement (`forced_measurements`
  of the description's settings), whose name names no identifier and
  that no declaration or person question makes an identifier, is
  modelled as a number; capped at 90 where its name says age, where the
  description top-codes it, or where every number it holds could be an
  age (0 to 125) and its name names no measurement (lane RX-1's reading,
  HIPAA first). A column with any cell of `FIGURE_RUN` figures in a row
  (a ZIP code, a record number) or reading as a date stays held: it may
  be a Safe Harbor element whatever its identifier answer says.

Nothing here is drawn: it runs at describe time, inside, on the real
table's cells, and decides what the record holds. It prints nothing.
"""

import dataclasses

from synthtwin import inside_relations, taxonomy, twin_checks

# A label's spellings read, commonest first (the marginals zone's own cap).
LEVEL_CAP = 1000
# A spelling holding this many figures in a row is held (a record number, a ZIP code, a telephone's digits).
FIGURE_RUN = 5
# The largest number an age can be, for a held column's numbers read as possible ages.
AGE_MOST = 125
_FIGURES = "0123456789"
# Why the description keeps a column as record numbers (`inside_relations.column_spec`).
_HELD_AS_RECORD_NUMBERS = (inside_relations.AN_IDENTIFIER, "its kind (identifier) is drawn by the description")


def _bare(text: object) -> str:
    if not isinstance(text, str):
        raise TypeError("synthtwin reads a table's cells as text only.")
    return text.strip()


def _figure_run(text: str) -> int:
    longest = 0
    run = 0
    for character in text:
        if character in _FIGURES:
            run += 1
            longest = max(longest, run)
        else:
            run = 0
    return longest


def held_spelling(text: object) -> bool:
    """Whether a real spelling of an ordinary label stays held: it reads as a person's details, a date, an age, or a long run of figures."""
    bare = _bare(text)
    if not bare:
        return False
    if _figure_run(bare) >= FIGURE_RUN:
        return True
    if twin_checks.read_date(bare) is not None or twin_checks.a_persons_detail(bare):
        return True
    return taxonomy.ages_named_in_cells([bare], False, frozenset())


def carried_spec(spec: inside_relations.ColumnSpec, block: object,
                 cells: "list[str]") -> inside_relations.ColumnSpec:
    """A modelled label column's spec carrying every real spelling the readers let through; any other spec as it is."""
    if spec.kind != inside_relations.LABEL or not isinstance(block, dict):
        return spec
    if "top_coded" in block and block["top_coded"]:
        return spec
    if twin_checks.named_as_an_identifier(spec.name):
        return spec
    counts: "dict[str, int]" = {}
    for cell in cells:
        if _bare(cell):
            counts[cell] = (counts[cell] if cell in counts else 0) + 1
    ranked = sorted((-counts[cell], cell) for cell in counts)
    published = set(spec.spellings)
    added: "list[str]" = []
    for _negative, cell in ranked[:LEVEL_CAP]:
        if cell not in published and not held_spelling(cell):
            added += [cell]
    return dataclasses.replace(spec, spellings=spec.spellings + tuple(added), carried=True)


def _named_list(settings: object, key: str) -> "list[str]":
    found = settings[key] if isinstance(settings, dict) and key in settings else None
    out: "list[str]" = []
    if isinstance(found, list):
        for each in found:
            if isinstance(each, str):
                out += [each]
    return out


def narrowed_spec(spec: inside_relations.ColumnSpec, block: object, settings: object,
                  cells: "list[str]") -> inside_relations.ColumnSpec:
    """A column held as record numbers though the person answered it a measurement, read as a number; any other spec as it is."""
    if spec.kind or spec.why_kept not in _HELD_AS_RECORD_NUMBERS:
        return spec
    if spec.name not in _named_list(settings, "forced_measurements"):
        return spec
    if spec.name in _named_list(settings, "forced_identifiers") or spec.name in _named_list(settings, "person_columns"):
        return spec
    if twin_checks.named_as_an_identifier(spec.name):
        return spec
    # A cell holding five figures in a row (a ZIP code, a record number) or reading as a date keeps the column
    # held: such a column may be a Safe Harbor element whatever its identifier answer says.
    for cell in cells:
        bare = _bare(cell)
        if bare and (_figure_run(bare) >= FIGURE_RUN or twin_checks.read_date(bare) is not None):
            return spec
    top = 0
    if isinstance(block, dict) and "top_coded" in block and isinstance(block["top_coded"], int):
        top = block["top_coded"]
    if taxonomy.named_as_an_age(spec.name):
        top = 90
    if not top and not taxonomy.named_as_a_measurement(spec.name):
        wrapper = inside_relations.common_wrapper(cells)
        ages = True
        seen = False
        for cell in cells:
            bare = _bare(cell)
            if not bare:
                continue
            found = inside_relations.wrapped(bare) if wrapper is not None else None
            value = inside_relations.number_of(found[1] if found is not None else bare)
            if value is None:
                continue
            seen = True
            if value < 0.0 or value > AGE_MOST:
                ages = False
                break
        if seen and ages:
            top = 90
    return inside_relations.ColumnSpec(spec.name, spec.place, inside_relations.NUMBER, top, (), "")
