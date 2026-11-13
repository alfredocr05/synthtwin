"""The computer's reader (lane ARR-a, plan P4-D466; LANE I4m RULINGS 26 (5)).

`synthtwin.computer` reads this computer's installed memory and number
of processors, the two facts the start-of-run check rests on (lane
CHON's check and lane TW's words wire and word it). These cases hold
what it hands back on every computer CI runs on, and what it says where
it cannot read one: Windows' memory above all, which no standard-library
route reads without a native call, so the reader says None and the check
asks the person. The offline audit's side (os.cpu_count and os.sysconf
in this module alone, os.sysconf with its two memory names) is held in
tests/test_offline_scan.py.
"""

import os
import sys

from synthtwin import cli, computer


def test_the_processor_count_is_a_whole_number_or_none():
    count = computer.processor_count()
    assert count is None or (type(count) is int and count >= 1)
    if os.cpu_count() is not None:
        assert count == os.cpu_count()


def test_the_installed_memory_is_a_whole_number_where_it_can_be_read():
    memory = computer.installed_memory()
    if sys.platform == "win32":
        assert memory is None
    else:
        assert type(memory) is int and memory > 0
        assert memory == os.sysconf("SC_PHYS_PAGES") * os.sysconf("SC_PAGE_SIZE")


def test_windows_memory_is_none_and_said_so(monkeypatch):
    """os.sysconf does not exist on Windows: the reader says None, never a guess."""
    monkeypatch.setattr(computer.sys, "platform", "win32")
    assert computer.installed_memory() is None


def test_an_unreadable_or_absent_reading_is_none(monkeypatch):
    def refused(name):
        raise ValueError(name)

    monkeypatch.setattr(computer.sys, "platform", "linux")
    monkeypatch.setattr(computer.os, "sysconf", refused, raising=False)
    assert computer.installed_memory() is None
    monkeypatch.setattr(computer.os, "sysconf", lambda name: -1, raising=False)
    assert computer.installed_memory() is None
    monkeypatch.delattr(computer.os, "sysconf", raising=False)
    assert computer.installed_memory() is None
    monkeypatch.setattr(computer.os, "cpu_count", lambda: None)
    assert computer.processor_count() is None
    monkeypatch.setattr(computer.os, "cpu_count", lambda: 0)
    assert computer.processor_count() is None


def test_the_reading_of_this_mac_s_kind(monkeypatch):
    """1,572,864 pages of 16,384 bytes are 24.0 GB; ten processors are ten."""
    pages = {"SC_PHYS_PAGES": 1_572_864, "SC_PAGE_SIZE": 16_384}
    monkeypatch.setattr(computer.sys, "platform", "darwin")
    monkeypatch.setattr(computer.os, "sysconf", pages.__getitem__, raising=False)
    monkeypatch.setattr(computer.os, "cpu_count", lambda: 10)
    assert computer.installed_memory() == 24 * 1024 ** 3
    assert computer.processor_count() == 10


def test_the_doctor_reads_the_memory_through_the_one_reader(monkeypatch):
    """cli._total_memory is a one-line delegate: the doctor's bytes are unchanged."""
    monkeypatch.setattr(computer, "installed_memory", lambda: 123_456)
    assert cli._total_memory() == 123_456
    monkeypatch.setattr(computer, "installed_memory", lambda: None)
    assert cli._total_memory() is None
