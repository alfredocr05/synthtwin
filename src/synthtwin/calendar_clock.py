"""The censuses of the time of day: their keys, and the rules they will share.

Stage 3b (plan P4-D364). A column of moments will publish how many cells
of its BODY -- the cells between the two tail boundaries, both included
-- fall on each hour (`hour_census`), each minute and each second of the
written wall clock (`minute_census`, `second_census`), beside the
minutes and seconds that stand out from their neighbours
(`minute_heaps`, `second_heaps`); and a column of clock times its own
census of ten-minute bins (`clock_census`), its heaps (`clock_heaps`),
the step its values were written on (`clock_step`) and the codes it
writes among them (`clock_codes`). Each landing of stage 3b's time-of-day
track fills its own keys and its own block below; until it does, every
one of these keys is empty on every block -- `clock_step` is `null` --
and the loader refuses anything else.

The bin rules every census shares -- the floor, the merge, the
stand-out rule and the checker of a published census -- are
`calendar_rules`', stated once there for the dates and the clock alike.

Nothing here reads a table: every name is a constant or a function of
the numbers handed to it. No I/O of any kind.
"""

# The keys of a column block of moments (contract 6.6.2), each `[]` on
# every block until its landing fills it.
HOUR_CENSUS = "hour_census"
MINUTE_CENSUS = "minute_census"
SECOND_CENSUS = "second_census"
MINUTE_HEAPS = "minute_heaps"
SECOND_HEAPS = "second_heaps"

# The keys of a column block of clock times (contract 6.13): the three
# lists `[]` and the step `null` on every block until their landing fills
# them.
CLOCK_CENSUS = "clock_census"
CLOCK_HEAPS = "clock_heaps"
CLOCK_STEP = "clock_step"
CLOCK_CODES = "clock_codes"

# The empty lists among them, in the order the keys are named above.
DATETIME_CLOCK_LISTS = (
    HOUR_CENSUS,
    MINUTE_CENSUS,
    SECOND_CENSUS,
    MINUTE_HEAPS,
    SECOND_HEAPS,
)
CLOCK_LISTS = (CLOCK_CENSUS, CLOCK_HEAPS, CLOCK_CODES)


# THE LANDINGS' ANCHORS (plan P4-D364). Each landing of stage 3b that
# adds to this module adds below its own line, so two landings built
# side by side never touch the same lines; a landing with nothing to add
# leaves its line alone. In the order of the plan's numbering table.
# anchor 3b-D1 (P4-D365)
# anchor 3b-D0 (P4-D366)
# anchor 3b-D2 (P4-D367)
# anchor 3b-D3 (P4-D368)
# anchor 3b-D4 (P4-D369)
# anchor 3b-T1 (P4-D370)
# anchor 3b-T2 (P4-D371)
# anchor 3b-T3 (P4-D372)
# anchor 3b-C1 (P4-D373)
# anchor 3b-C2 (P4-D374)
# anchor 3b-G1 (P4-D375)
# anchor 3b-G3 (P4-D376)
# anchor 3b-G2 (P4-D377)
# anchor 3b-7 (P4-D378)
# anchor 3b-J (P4-D379)
