#!/usr/bin/env python3
"""Read the DLLs each Windows program file of the ready folder needs.

Plan P4-D483 (lane WIN of the December plan). The ready folder carries
its own Python and libraries, and a library file (`.pyd` or `.dll`)
loads only when every DLL its import table names can be found. CI's
Windows runners have every Visual C++ runtime installed system-wide, so
a library that needs one the folder does not carry loads there and
fails on a bare hospital computer ("DLL load failed while importing").
This check reads the import table and the delay-import table of every
`.exe`, `.pyd` and `.dll` in the folder, with the standard library
alone, and refuses the folder when a DLL named in an import table is
neither in the folder nor on `SYSTEM_DLLS`, the short list of DLLs every
Windows 10 and 11 on a 64-bit Intel or AMD computer holds (51 names
written before the workflow's first run, which its printed names
confirm or prune).
The Visual C++ runtime's own DLLs (`VCRUNTIME`, `MSVCP`, `VCOMP`,
`CONCRT`) are never on that list, and one of them that the folder holds
only where Windows would not look for the file that needs it is refused
too: on the runner the system's own copy answers, on a hospital
computer nothing does. Where Windows looks depends on WHEN the file
loads: python.exe, its DLLs and the standard library's modules in
`python\\` load before any library is imported, so for them only
`python\\` counts; a library's own `<package>.libs` folder counts only
for that package's files, once its import has registered it. Only a
FILE answers a name (a folder named like a DLL is no DLL). Any other
DLL found only in another folder of the ready folder is reported (the
rehearsal's own imports prove those).
A DLL named only in a delay-import table loads when a function of it is
first called, so one missing there is reported, not refused. A file
that is not a readable program file is refused with a plain message,
never a traceback. The report ends with every DLL name the folder's
files import and how many import it, so a reviewer can read the list.

    python tools/bundle/pe_imports.py FOLDER

exits 0 when the closure holds and 1 when it does not; it opens no
network connection and writes nothing.
"""

import os
import pathlib
import struct
import sys

# DLLs every Windows 10 and 11 x64 holds in its system folder: 51 names
# written from the libraries' known imports before run 1; run 1's printed
# names confirm or prune them, and a name is added after that only when a
# run names it and a reviewer confirms it ships with Windows itself. The
# Visual C++ runtime is never here (NEVER_SYSTEM).
SYSTEM_DLLS = frozenset(
    {
        "advapi32.dll",
        "bcrypt.dll",
        "cfgmgr32.dll",
        "combase.dll",
        "comctl32.dll",
        "comdlg32.dll",
        "crypt32.dll",
        "cryptbase.dll",
        "cryptnet.dll",
        "dbghelp.dll",
        "dnsapi.dll",
        "dwmapi.dll",
        "gdi32.dll",
        "imagehlp.dll",
        "imm32.dll",
        "iphlpapi.dll",
        "kernel32.dll",
        "kernelbase.dll",
        "mpr.dll",
        "msvcrt.dll",
        "mswsock.dll",
        "ncrypt.dll",
        "netapi32.dll",
        "normaliz.dll",
        "ntdll.dll",
        "ole32.dll",
        "oleaut32.dll",
        "powrprof.dll",
        "propsys.dll",
        "psapi.dll",
        "rpcrt4.dll",
        "secur32.dll",
        "setupapi.dll",
        "shcore.dll",
        "shell32.dll",
        "shlwapi.dll",
        "sspicli.dll",
        "ucrtbase.dll",
        "user32.dll",
        "userenv.dll",
        "uxtheme.dll",
        "version.dll",
        "winhttp.dll",
        "wininet.dll",
        "winmm.dll",
        "winspool.drv",
        "wintrust.dll",
        "wldap32.dll",
        "ws2_32.dll",
        "wsock32.dll",
        "wtsapi32.dll",
    }
)
# Windows 10's API sets: names the system's own loader answers (the
# Universal C runtime among them), never files on disk.
API_SET_PREFIX = "api-ms-win-"
# The Visual C++ runtime: CI's runners hold it system-wide, hospital
# computers often do not, so the folder carries every one it needs.
NEVER_SYSTEM = ("vcruntime", "msvcp", "vcomp", "concrt")

_MACHINES = {0x8664: "x64", 0xAA64: "Arm64", 0x14C: "x86"}
_IMPORT = 1
_DELAY_IMPORT = 13


class PEError(ValueError):
    """A file that is not a Windows program file this check can read."""


def _unpack(data: bytes, fmt: str, offset: int) -> "tuple[int, ...]":
    size = struct.calcsize(fmt)
    if offset < 0 or offset + size > len(data):
        raise PEError("it ends before its own headers do")
    return struct.unpack_from(fmt, data, offset)


def _sections(data: bytes, start: int, count: int) -> "list[tuple[int, int, int, int]]":
    found = []
    for index in range(count):
        place = start + 40 * index
        virtual_size, address, raw_size, raw_at = _unpack(data, "<IIII", place + 8)
        found.append((address, max(virtual_size, raw_size), raw_at, raw_size))
    return found


def _offset(rva: int, sections: "list[tuple[int, int, int, int]]", headers: int) -> int:
    for address, span, raw_at, raw_size in sections:
        if address <= rva < address + span:
            inside = rva - address
            if inside >= raw_size:
                raise PEError("an import table points past the data the file holds")
            return raw_at + inside
    if rva < headers:
        return rva
    raise PEError("an import table points outside every section of the file")


def _name_at(data: bytes, offset: int) -> str:
    end = data.find(b"\0", offset, offset + 260)
    if offset >= len(data) or end < 0:
        raise PEError("a DLL name in its import table does not end")
    raw = data[offset:end]
    if not raw or any(byte < 0x20 or byte > 0x7E for byte in raw):
        raise PEError("a DLL name in its import table is not plain text")
    return raw.decode("ascii")


def imports_of(data: bytes) -> "tuple[str, list[str], list[str]]":
    """(machine, imported DLLs, delay-imported DLLs) of one program file's bytes.

    Raises PEError, with words a person can read, for anything that is
    not a whole PE32 or PE32+ file.
    """
    if data[:2] != b"MZ":
        raise PEError("it is not a Windows program file (it does not start with MZ)")
    (header_at,) = _unpack(data, "<I", 0x3C)
    if data[header_at : header_at + 4] != b"PE\0\0":
        raise PEError("it is not a Windows program file (no PE header where its start says)")
    machine, section_count, _, _, _, optional_size, _ = _unpack(data, "<HHIIIHH", header_at + 4)
    optional_at = header_at + 24
    (magic,) = _unpack(data, "<H", optional_at)
    if magic == 0x20B:
        (image_base,) = _unpack(data, "<Q", optional_at + 24)
        (headers,) = _unpack(data, "<I", optional_at + 60)
        (directory_count,) = _unpack(data, "<I", optional_at + 108)
        directories_at = optional_at + 112
    elif magic == 0x10B:
        (image_base,) = _unpack(data, "<I", optional_at + 28)
        (headers,) = _unpack(data, "<I", optional_at + 60)
        (directory_count,) = _unpack(data, "<I", optional_at + 92)
        directories_at = optional_at + 96
    else:
        raise PEError("its optional header is neither PE32 nor PE32+")
    sections = _sections(data, optional_at + optional_size, section_count)

    def directory(index: int) -> "tuple[int, int]":
        if index >= directory_count:
            return 0, 0
        address, size = _unpack(data, "<II", directories_at + 8 * index)
        return address, size

    imported: "list[str]" = []
    address, size = directory(_IMPORT)
    if address and size:
        place = _offset(address, sections, headers)
        while True:
            entry = _unpack(data, "<IIIII", place)
            if not any(entry):
                break
            imported.append(_name_at(data, _offset(entry[3], sections, headers)))
            place += 20
    delayed: "list[str]" = []
    address, size = directory(_DELAY_IMPORT)
    if address and size:
        place = _offset(address, sections, headers)
        while True:
            entry = _unpack(data, "<IIIIIIII", place)
            if not any(entry):
                break
            name_rva = entry[1] if entry[0] & 1 else entry[1] - image_base
            delayed.append(_name_at(data, _offset(name_rva, sections, headers)))
            place += 32
    return _MACHINES.get(machine, hex(machine)), imported, delayed


def is_system(name: str) -> bool:
    """Whether every Windows 10 and 11 x64 answers this DLL name itself."""
    lowered = name.lower()
    if lowered.startswith(NEVER_SYSTEM):
        return False
    return lowered in SYSTEM_DLLS or lowered.startswith(API_SET_PREFIX)


def program_files(folder: pathlib.Path) -> "list[pathlib.Path]":
    """Every .exe, .pyd and .dll under ``folder``, in a fixed order."""
    return sorted(
        path
        for path in folder.rglob("*")
        if path.is_file() and path.suffix.lower() in (".exe", ".pyd", ".dll")
    )


def _loader_places(path: pathlib.Path, folder: pathlib.Path) -> "list[pathlib.Path]":
    """The folders Windows searches for this file's DLLs, at the stage that loads it.

    Every file: its own folder and python.exe's folder (python/, the
    program's own). A library's `<package>.libs` folder (the layout the
    wheels' repair tool writes) is searched only once that package's
    import has registered it, so it counts only for the files of that
    same package under python/lib/<package>/; python.exe, its DLLs and
    the standard library's modules in python/ load before any library is
    imported, so no `.libs` folder counts for them.
    """
    python = folder / "python"
    places = [path.parent, python]
    try:
        inside = path.relative_to(python / "lib").parts
    except ValueError:
        return places
    if len(inside) > 1:
        own = python / "lib" / (inside[0] + ".libs")
        if own.is_dir():
            places += [own]
    return places


def closure(folder: pathlib.Path) -> "dict[str, list[str]]":
    """The closure report of the folder: what is missing, delayed, elsewhere or unreadable.

    Keys: `missing` (refused), `damaged` (refused), `foreign` (refused:
    a file for another kind of processor), `missing_delayed` and
    `elsewhere` (reported only), `checked` (one line a file) and
    `names` (each DLL name imported, with how many files import it).
    """
    files = program_files(folder)
    names = {path.name.lower() for path in files}
    report: "dict[str, list[str]]" = {
        "missing": [],
        "damaged": [],
        "foreign": [],
        "missing_delayed": [],
        "elsewhere": [],
        "checked": [],
        "names": [],
    }
    counted: "dict[str, int]" = {}
    seen: "dict[pathlib.Path, frozenset[str]]" = {}
    for path in files:
        shown = path.relative_to(folder).as_posix()
        try:
            machine, imported, delayed = imports_of(path.read_bytes())
        except PEError as error:
            report["damaged"].append(f"{shown}: {error}")
            continue
        except OSError as error:
            report["damaged"].append(f"{shown}: it could not be read ({error.strerror or type(error).__name__})")
            continue
        if machine != "x64":
            report["foreign"].append(f"{shown}: made for {machine}, not for a 64-bit Intel or AMD computer")
        report["checked"].append(f"{shown}: {len(imported)} imports, {len(delayed)} delayed")
        places = _loader_places(path, folder)
        for kind, listed in (("missing", imported), ("missing_delayed", delayed)):
            for name in listed:
                counted[name.lower()] = counted.get(name.lower(), 0) + 1
                if is_system(name):
                    continue
                if any(name.lower() in _files_in(place, seen) for place in places):
                    continue
                if name.lower() not in names:
                    report[kind] += [f"{shown} needs {name}"]
                elif name.lower().startswith(NEVER_SYSTEM) and kind == "missing":
                    report["missing"] += [
                        f"{shown} needs {name}, which the folder holds only in another folder, "
                        "where Windows does not look for it"
                    ]
                else:
                    report["elsewhere"] += [f"{shown} needs {name}, found only in another folder"]
    report["names"] = [f"{name}: {count}" for name, count in sorted(counted.items())]
    return report


def _files_in(place: pathlib.Path, seen: "dict[pathlib.Path, frozenset[str]]") -> "frozenset[str]":
    """The FILES ``place`` holds, by lower-case name (a folder named like a DLL is no DLL); read once a place."""
    if place not in seen:
        try:
            seen[place] = frozenset(entry.lower() for entry in os.listdir(place) if (place / entry).is_file())
        except OSError:
            seen[place] = frozenset()
    return seen[place]


def main(argv: "list[str] | None" = None) -> int:
    arguments = sys.argv[1:] if argv is None else argv
    if len(arguments) != 1:
        print("Give the folder to check: python tools/bundle/pe_imports.py FOLDER")
        return 2
    folder = pathlib.Path(arguments[0])
    report = closure(folder)
    print(f"read the import tables of {len(report['checked'])} program files")
    for line in report["missing_delayed"]:
        print(f"note (a delayed import, loaded only when first called): {line}")
    for line in report["elsewhere"]:
        print(f"note: {line}")
    print("the DLL names imported, with how many files import each:")
    for line in report["names"]:
        print(f"  {line}")
    refused = report["missing"] + report["damaged"] + report["foreign"]
    if refused:
        print("The DLL closure does not hold:")
        for line in refused:
            print(" -", line)
        print(
            "Every DLL a library file needs must be in the folder, or be one that "
            "every Windows 10 and 11 holds (SYSTEM_DLLS in tools/bundle/pe_imports.py). "
            "The Visual C++ runtime never counts as one."
        )
        return 1
    print("every DLL an import table names is in the folder or ships with Windows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
