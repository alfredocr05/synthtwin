"""The clock census battery: seeded, neutral columns of clock times (landing 3b.5).

Plan P4-D373. Each builder writes one column of cell texts with the
standard library's own seeded generator -- no value comes from any table
-- and is read by tests/test_stage3b_clock.py, the clock's gate, and by
tools/measurements/kpi_clock.py, the driver of K-S3-48. The design's
eight shapes (a clinic's slots, walk-ins on a ten-minute grid, a
medication round, a handover heaped at 07:00 and 19:00, shift starts,
emergency triage at the second, night observations across midnight, lab
draws), its skeptic's three (five rounds, shift starts beside `UNK`, a
dominant time with no tails), Excel's one-figure hour, the 12-hour clock
with a marker, a five-minute grid, and the columns single clauses of the
gate ask for: a code at the census line, two columns 2 % of whose cells
are a word (beside two-figure and one-figure hours), four `UNK` beside
shift starts, a lone heap with few times beside it, and a low boundary
two steps below a heap. Its repair round (the 3b.5 skeptic's items 1,
3 and 5) adds appointment times beside clock-shaped codes near the one
per cent the clock line allows (`CODE_MIXES`), small tables of them
beside a few such codes past it (`SMALL_TABLES`), Excel's `h:mm AM`
beside 2 % words, and three shift starts with no jitter.
"""

import random

from synthtwin import parsing

_ED = (3, 2, 2, 1.5, 1.5, 2, 3, 5, 7, 8, 9, 9, 9, 8, 7, 7, 7, 8, 8, 7, 6, 5, 4, 3)


def _hm(minute: int) -> str:
    return parsing.clock_spelling(minute % 1440, parsing.CLOCK_HH_MM)


def _clinic(draw: random.Random) -> str:
    hour = draw.randint(8, 16)
    pick = draw.random()
    if pick < 0.70:
        minute = draw.choice((0, 30))
    elif pick < 0.95:
        minute = draw.choice((15, 45))
    else:
        minute = draw.randrange(60)
    return _hm(hour * 60 + minute)


def _walkin_minute(draw: random.Random) -> int:
    if draw.random() < 0.55:
        return 7 * 60 + 30 + 10 * min(67, int(draw.triangular(0, 68, 30)))
    return int(draw.triangular(7 * 60, 20 * 60, 12 * 60 + 30))


def _walkin(draw: random.Random) -> str:
    return _hm(_walkin_minute(draw))


def _med_round(draw: random.Random) -> str:
    if draw.random() < 0.6:
        return _hm(6 * 60 + draw.randrange(60))
    return _hm(draw.randrange(1440))


def _handover(draw: random.Random) -> str:
    pick = draw.random()
    if pick < 0.35:
        return _hm(7 * 60 + draw.choice((0, 0, 0, 5, 10, 15)))
    if pick < 0.70:
        return _hm(19 * 60 + draw.choice((0, 0, 0, 5, 10, 15)))
    return _hm(draw.randrange(1440))


def _shift_minute(draw: random.Random) -> int:
    pick = draw.random()
    if pick < 0.40:
        return 7 * 60
    if pick < 0.70:
        return 15 * 60
    if pick < 0.90:
        return 23 * 60
    base = draw.choice((7 * 60, 15 * 60, 23 * 60))
    return (base + draw.choice((-1, 1)) * draw.randint(1, 30)) % 1440


def _shift_start(draw: random.Random) -> str:
    return _hm(_shift_minute(draw))


def _ed_triage(draw: random.Random) -> str:
    hour = draw.choices(range(24), weights=_ED)[0]
    if draw.random() < 0.25:
        second = hour * 3600 + draw.choice((0, 30)) * 60
    else:
        second = hour * 3600 + draw.randrange(60) * 60 + draw.randrange(60)
    return parsing.clock_spelling(second, parsing.CLOCK_HH_MM_SS)


def _night_obs(draw: random.Random) -> str:
    if draw.random() < 0.30:
        return _hm(draw.choice((22 * 60, 2 * 60, 6 * 60)))
    return _hm(20 * 60 + draw.randrange(12 * 60))


def _lab_draw(draw: random.Random) -> str:
    pick = draw.random()
    if pick < 0.43:
        return _hm(6 * 60 + draw.randrange(120))
    if pick < 0.53:
        return _hm(14 * 60 + draw.randrange(30))
    hour = draw.choices(range(24), weights=_ED)[0]
    return _hm(hour * 60 + draw.randrange(60))


def _rounds5(draw: random.Random) -> str:
    if draw.random() < 0.03:
        return _hm(draw.randrange(1440))
    return _hm(draw.choices((360, 600, 840, 1080, 1320), weights=(25, 20, 20, 20, 12))[0])


def _shift_unk(draw: random.Random) -> str:
    return "UNK" if draw.random() < 0.008 else _shift_start(draw)


def _excel_hmm(draw: random.Random) -> str:
    return parsing.written_clock(60 * _walkin_minute(draw), False, "h")


def _ampm(draw: random.Random) -> str:
    return parsing.written_clock(60 * _walkin_minute(draw), False, "hh AM-PM")


def _grid5(draw: random.Random) -> str:
    return _hm(5 * (96 + draw.randrange(120)))


def _coded(draw: random.Random) -> str:
    return "not recorded" if draw.random() < 0.008 else _shift_start(draw)


def _mixed_walkin(draw: random.Random) -> str:
    return "unknown" if draw.random() < 0.02 else _walkin(draw)


def _mixed_hmm(draw: random.Random) -> str:
    return "unknown" if draw.random() < 0.02 else _excel_hmm(draw)


def _mixed_ampm(draw: random.Random) -> str:
    """Excel's `h:mm AM`, one space before the marker, beside 2 % words."""
    if draw.random() < 0.02:
        return "unknown"
    return parsing.written_clock(60 * _walkin_minute(draw), False, "h AM-PM")


def _shifts3(draw: random.Random) -> str:
    """Three shift starts and nothing else: every cell on a heap."""
    return _hm(draw.choices((7 * 60, 15 * 60, 23 * 60), weights=(4, 3, 3))[0])


def _slot_minute(draw: random.Random) -> int:
    """An outpatient appointment: quarter-hour slots from 07:00 mostly."""
    pick = draw.random()
    if pick < 0.80:
        hour = draw.choices(range(7, 17), weights=(3, 9, 10, 10, 8, 4, 8, 9, 8, 5))[0]
        return hour * 60 + 15 * draw.randrange(4)
    if pick < 0.92:
        return 390 + draw.randrange(750)
    return 17 * 60 + 30 * draw.randrange(6)


# APPOINTMENT TIMES BESIDE CLOCK-SHAPED CODES NEAR THE CLOCK LINE (the 3b.5
# skeptic's repair round, items 1 and 3): `99:99`, `24:00` and `88:88` are
# written as a clock and read as none, and with `UNK` they hold 0.9 % to
# 1.7 % of the cells; the last mix is Excel's `h:mm AM`. Each mix is one
# column of the same table, written in the style it names.
CODE_MIXES: "dict[str, tuple[tuple[tuple[str, float], ...], str]]" = {
    "codes_a": ((("UNK", 0.007), ("99:99", 0.004)), "hh"),
    "codes_b": ((("UNK", 0.005), ("99:99", 0.006)), "hh"),
    "codes_c": ((("99:99", 0.012),), "hh"),
    "codes_d": ((("UNK", 0.006), ("24:00", 0.006)), "hh"),
    "codes_e": ((("UNK", 0.009), ("99:99", 0.002), ("88:88", 0.002)), "hh"),
    "codes_ampm": ((("UNK", 0.006), ("99:99", 0.003)), "h AM-PM"),
}

# SMALL TABLES OF THEM BESIDE A FEW SUCH CODES PAST IT (item 1): each a
# number of rows and the codes among them, in three variants of the times.
SMALL_TABLES: "dict[str, tuple[int, tuple[str, ...]]]" = {
    "small_a": (100, ("99:99",) * 3),
    "small_b": (150, ("99:99",) * 2 + ("24:00",) * 2),
    "small_c": (200, ("24:00",) * 5),
    "small_d": (100, ("99:99", "24:00", "88:88")),
    "small_e": (60, ("99:99",) * 2),
    "small_f": (250, ("99:99",) * 6),
}


def _coded_appointments(
    rows: int, codes: "tuple[tuple[str, float], ...]", style: str, draw: random.Random
) -> "list[str]":
    out: "list[str]" = []
    for _row in range(rows):
        pick = draw.random()
        reached = 0.0
        text = ""
        for spelling, rate in codes:
            reached = reached + rate
            if not text and pick < reached:
                text = spelling
        out += [text or parsing.written_clock(60 * _slot_minute(draw), False, style)]
    return out


SHAPES = {
    "clinic": _clinic,
    "walkin": _walkin,
    "med_round": _med_round,
    "handover": _handover,
    "shift_start": _shift_start,
    "ed_triage_s": _ed_triage,
    "night_obs": _night_obs,
    "lab_draw": _lab_draw,
    "rounds5": _rounds5,
    "shift_unk": _shift_unk,
    "excel_hmm": _excel_hmm,
    "ampm": _ampm,
    "grid5": _grid5,
}
# The shapes read as clock times, and the dominant time, which has no tails.
CLOCKS = tuple(SHAPES) + ("dominant",)


def _dominant(rows: int, draw: random.Random) -> "list[str]":
    below = [draw.randrange(360, 480) for _ in range(9)]
    above = [draw.randrange(481, 1080) for _ in range(9)]
    out = below + above + [480] * (rows - 18)
    draw.shuffle(out)
    return [_hm(minute) for minute in out]


def cells(name: str, rows: int) -> "list[str]":
    """One column of the battery at this many rows, seeded by its name and size."""
    draw = random.Random(73000 + 97 * rows + sum(ord(c) for c in name))
    if name == "dominant":
        return _dominant(rows, draw)
    if name == "coded":
        return [_coded(draw) for _ in range(rows)]
    if name == "mixed_walkin":
        return [_mixed_walkin(draw) for _ in range(rows)]
    if name == "mixed_hmm":
        return [_mixed_hmm(draw) for _ in range(rows)]
    if name == "mixed_ampm":
        return [_mixed_ampm(draw) for _ in range(rows)]
    if name == "shifts3":
        return [_shifts3(draw) for _ in range(rows)]
    if name in CODE_MIXES:
        return _coded_appointments(rows, CODE_MIXES[name][0], CODE_MIXES[name][1], draw)
    if name[:-1] in SMALL_TABLES:
        size, codes = SMALL_TABLES[name[:-1]]
        out = [_hm(_slot_minute(draw)) for _ in range(size - len(codes))] + list(codes)
        draw.shuffle(out)
        return out
    if name == "unk4":
        out = ["UNK"] * 4 + [_shift_start(draw) for _ in range(rows - 4)]
        draw.shuffle(out)
        return out
    if name == "lonely":
        out = ["08:00"] * (rows - 5) + ["06:10", "07:20", "09:45", "10:05", "12:30"]
        draw.shuffle(out)
        return out
    if name == "boundary":
        out = [_hm(300 + draw.randrange(110)) for _ in range(11)]
        out += ["06:58"] + ["07:00"] * 25
        out += [_hm(421 + draw.randrange(60)) for _ in range(30)]
        out += [_hm(600 + draw.randrange(120)) for _ in range(12)]
        draw.shuffle(out)
        return out
    return [SHAPES[name](draw) for _ in range(rows)]
