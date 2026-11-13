"""THE COMPUTER'S READER (plan P4-D466, lane ARR-a; LANE I4m RULINGS 26 (5) and LANE ARR RULINGS 1 (3)).

Before any hour of work the shipped command is to tell the person, in
plain words, what a run needs and whether this computer is enough (lane
CHON's start-of-run check and lane TW's words wire it; nothing calls it
from there yet). This module reads the two facts that check rests on,
and no other module reads them: the offline audit admits `os.cpu_count`
and `os.sysconf` here alone, `os.sysconf` with its two memory names only
(tools/offline_scan/scan_imports.py).

- `installed_memory()`: the computer's installed memory in bytes, from
  `os.sysconf`'s SC_PHYS_PAGES and SC_PAGE_SIZE (macOS and Linux), or
  None where it cannot be read. On Windows `os.sysconf` does not exist
  and the standard library has no other way to ask without starting a
  program or calling native code, which this package never does
  (charter principle 3): the check says so in plain words and asks the
  person. Total memory, not free memory: no portable call reports what
  is free. Inside a Linux container it is the HOST's memory, not the
  share the container is granted (no admitted call reads that limit): a
  stated limit, which the check's words are to name (lanes CHON and TW;
  lane ARR-a's repair 2). (It was `cli._total_memory`, plan P4-D397; the doctor still
  calls it through that name.)
- `processor_count()`: the logical processors `os.cpu_count()` reports,
  or None where it cannot say. It counts the computer's processors, not
  the share a container or a scheduler grants this process: the calls
  that would say that (`os.process_cpu_count`, Python 3.13 and later;
  `os.sched_getaffinity`, Linux alone) are not admitted. A stated limit,
  which lane PAR's default -- the smaller of the processors less one and
  4 (LANE I4m RULINGS 26 (6)) -- bounds.

No file, no process, no network, no callable and no code loaded.
"""

import os
import sys


def installed_memory() -> "int | None":
    """This computer's installed memory in bytes, or None where it cannot be read (Windows above all)."""
    if sys.platform == "win32":
        return None
    try:
        pages = os.sysconf("SC_PHYS_PAGES")
        page_size = os.sysconf("SC_PAGE_SIZE")
    except (ValueError, OSError, AttributeError):
        return None
    if pages <= 0 or page_size <= 0:
        return None
    return pages * page_size


def processor_count() -> "int | None":
    """The number of logical processors this computer has, or None where it cannot say."""
    count = os.cpu_count()
    if count is None or count < 1:
        return None
    return count
