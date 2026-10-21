#!/usr/bin/env python3
"""Assemble synthtwin's offline bundle from a checked wheelhouse.

Plan P4-D416 (lane DEP-2 of the December plan; the owner's D3 of
2026-10-20: the offline bundle is the only way synthtwin is installed;
plan P4-D409 part 7). CI's `bundle-build` job runs this on each
platform's own runner, after pip has downloaded every file of
`requirements-install.lock` for every supported Python with its hash
checked; nothing here touches the network and nothing it makes is ever
committed:

* wheels are binary files, which the decontamination scanner reports
  as violations, and
* THIRD-PARTY-NOTICES.txt quotes the libraries' licence texts, lines
  of which the scanner matches (numpy's, scipy's and pyarrow's).

The bundle folder holds:

    INSTALL.txt                  the plain-words guide (scripts/INSTALL.txt)
    LICENSE                      synthtwin's own licence
    THIRD-PARTY-NOTICES.txt      gathered here from the wheels' metadata
    requirements-install.lock    the lock pip installs from, as committed
    scripts/install.sh           the install script for macOS and Linux
    scripts/install.bat          the install script for Windows
    scripts/check_bundle.py      the check both scripts run first
                                 (tools/bundle/check_bundle.py)
    wheelhouse/*.whl             every library wheel and synthtwin's own
    SHA256SUMS                   the SHA-256 of every file above

Every library wheel must be one whose SHA-256 the lock pins, and only
wheels may enter: a source archive would run its build code on the
person's computer. Usage:

    python tools/bundle/build_bundle.py --wheelhouse DIR \
        --synthtwin-wheel FILE --platform NAME --out DIR [--zip-into DIR]

It makes the folder synthtwin-<version>-<platform> in --out and, given
--zip-into, the zip synthtwin-<version>-<platform>.zip there, the name
README gives it, holding that one folder; it prints both and the zip's
SHA-256.
"""

import argparse
import email.parser
import hashlib
import pathlib
import re
import shutil
import sys
import zipfile

REPO = pathlib.Path(__file__).resolve().parents[2]

# What the bundle copies from the repository, by its place in the bundle.
COPIED = {
    "INSTALL.txt": "scripts/INSTALL.txt",
    "LICENSE": "LICENSE",
    "requirements-install.lock": "requirements-install.lock",
    "scripts/install.sh": "scripts/install.sh",
    "scripts/install.bat": "scripts/install.bat",
    "scripts/check_bundle.py": "tools/bundle/check_bundle.py",
}

NOTICES = "THIRD-PARTY-NOTICES.txt"
SUMS = "SHA256SUMS"

_PINNED = re.compile(r"--hash=sha256:([0-9a-f]{64})")
_LICENCE_NAME = re.compile(r"(?i)(licen[cs]e|copying|notice|authors)")
# A fixed time for every zip member, so two builds of the same files
# make the same zip.
_ZIP_TIME = (1980, 1, 1, 0, 0, 0)


def sha256_of(path: pathlib.Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            hasher.update(block)
    return hasher.hexdigest()


def wheelhouse_problems(wheelhouse: pathlib.Path, lock: pathlib.Path) -> "list[str]":
    """Every file of the wheelhouse that may not enter a bundle.

    A file that is not a wheel, a synthtwin wheel (it is given on its
    own), and a wheel whose SHA-256 the lock does not pin.
    """
    pinned = set(_PINNED.findall(lock.read_text(encoding="utf-8")))
    problems: "list[str]" = []
    files = sorted(path for path in wheelhouse.iterdir() if path.is_file())
    if not files:
        problems += ["the wheelhouse is empty; the download produced nothing"]
    for path in files:
        if path.suffix != ".whl":
            problems += [
                f"{path.name} is not a wheel (only built wheels enter the "
                "bundle; a source archive runs build code when installed)"
            ]
        elif path.name.startswith("synthtwin-"):
            problems += [f"{path.name}: synthtwin's wheel is given on its own"]
        elif sha256_of(path) not in pinned:
            problems += [f"{path.name} has a SHA-256 the lock does not pin"]
    return problems


def _project(name: str) -> str:
    return name.split("-", 1)[0].lower().replace("_", "-")


def notices(wheels: "list[pathlib.Path]") -> str:
    """THIRD-PARTY-NOTICES.txt's text, read from the wheels' own metadata.

    For each project and version once, in name order: its name, version
    and declared licence from METADATA, then every licence, copying,
    notice or authors file its dist-info carries, each text once
    whichever Python's wheel it came from.
    """
    projects: "dict[tuple[str, str], dict[str, object]]" = {}
    for wheel in sorted(wheels, key=lambda path: path.name):
        with zipfile.ZipFile(wheel) as archive:
            names = sorted(archive.namelist())
            info = [name for name in names if re.fullmatch(r"[^/]+\.dist-info/METADATA", name)]
            if len(info) != 1:
                continue
            folder = info[0].rsplit("/", 1)[0] + "/"
            meta = email.parser.HeaderParser().parsestr(
                archive.read(info[0]).decode("utf-8", "replace")
            )
            key = (str(meta.get("Name", wheel.name)), str(meta.get("Version", "")))
            declared = str(meta.get("License") or "").strip().splitlines()
            entry = projects.setdefault(
                key,
                {
                    "licence": str(meta.get("License-Expression") or "").strip()
                    or (declared[0] if declared else "not declared in its metadata"),
                    "texts": {},
                },
            )
            texts = entry["texts"]
            assert isinstance(texts, dict)
            for name in names:
                if not name.startswith(folder) or name.endswith("/"):
                    continue
                inside = name[len(folder) :]
                if inside.startswith("licenses/") or _LICENCE_NAME.search(
                    inside.rsplit("/", 1)[-1]
                ):
                    text = archive.read(name).decode("utf-8", "replace")
                    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
                    if digest not in texts:
                        texts[digest] = (inside, text)
    lines = [
        "Third-party notices for the libraries in this synthtwin bundle.",
        "",
        "Gathered when the bundle was built, from each library wheel's own",
        "metadata and licence files, unchanged. synthtwin's own licence is",
        "the file LICENSE beside this one.",
        "",
    ]
    for (name, version), entry in sorted(projects.items(), key=lambda item: item[0][0].lower()):
        lines += ["=" * 72, f"{name} {version}", f"Licence: {entry['licence']}", "=" * 72]
        texts = entry["texts"]
        assert isinstance(texts, dict)
        for inside, text in sorted(texts.values()):
            lines += ["", f"--- {inside} ---", "", text.rstrip("\n"), ""]
    return "\n".join(lines) + "\n"


def assemble(
    wheelhouse: pathlib.Path,
    synthtwin_wheel: pathlib.Path,
    out: pathlib.Path,
    repo: pathlib.Path = REPO,
) -> "list[str]":
    """Make the bundle folder ``out``; return the problems, empty when made.

    ``out`` must not exist yet. Nothing is written when the wheelhouse
    has a problem.
    """
    lock = repo / "requirements-install.lock"
    problems = wheelhouse_problems(wheelhouse, lock)
    if not re.fullmatch(r"synthtwin-[^-]+-py3-none-any\.whl", synthtwin_wheel.name):
        problems += [f"{synthtwin_wheel.name} is not a synthtwin wheel for any Python"]
    if out.exists():
        problems += [f"{out} exists already; the bundle is made in a new folder"]
    if problems:
        return problems
    (out / "wheelhouse").mkdir(parents=True)
    (out / "scripts").mkdir()
    for placed, source in COPIED.items():
        shutil.copyfile(repo / source, out / placed)
    wheels = sorted(path for path in wheelhouse.iterdir() if path.is_file())
    for wheel in wheels:
        shutil.copyfile(wheel, out / "wheelhouse" / wheel.name)
    shutil.copyfile(synthtwin_wheel, out / "wheelhouse" / synthtwin_wheel.name)
    (out / NOTICES).write_bytes(notices(wheels).encode("utf-8"))
    listed = sorted(
        path.relative_to(out).as_posix()
        for path in out.rglob("*")
        if path.is_file() and path.name != SUMS
    )
    sums = "".join(f"{sha256_of(out / name)}  {name}\n" for name in listed)
    (out / SUMS).write_bytes(sums.encode("utf-8"))
    return []


def bundle_name(synthtwin_wheel: pathlib.Path, platform: str) -> str:
    """synthtwin-<version>-<platform>: the bundle's folder, and its zip's name before .zip."""
    return f"synthtwin-{synthtwin_wheel.name.split('-')[1]}-{platform}"


def zip_folder(folder: pathlib.Path, target: pathlib.Path) -> str:
    """Zip ``folder`` under its own name, member order and times fixed; its SHA-256."""
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(folder.rglob("*")):
            if not path.is_file():
                continue
            member = zipfile.ZipInfo(
                (pathlib.PurePosixPath(folder.name) / path.relative_to(folder).as_posix()).as_posix(),
                _ZIP_TIME,
            )
            member.compress_type = zipfile.ZIP_DEFLATED
            member.external_attr = (0o755 if path.suffix == ".sh" else 0o644) << 16
            archive.writestr(member, path.read_bytes())
    return sha256_of(target)


def main(argv: "list[str] | None" = None) -> int:
    parser = argparse.ArgumentParser(prog="build_bundle", description=__doc__.split("\n")[0])
    parser.add_argument("--wheelhouse", required=True, type=pathlib.Path)
    parser.add_argument("--synthtwin-wheel", required=True, type=pathlib.Path)
    parser.add_argument("--platform", required=True)
    parser.add_argument("--out", required=True, type=pathlib.Path)
    parser.add_argument("--zip-into", type=pathlib.Path)
    args = parser.parse_args(argv)
    out = args.out / bundle_name(args.synthtwin_wheel, args.platform)
    problems = assemble(args.wheelhouse, args.synthtwin_wheel, out)
    if problems:
        print("The bundle was not made:")
        for problem in problems:
            print(" -", problem)
        return 1
    print(f"made {out}")
    if args.zip_into is not None:
        args.zip_into.mkdir(parents=True, exist_ok=True)
        target = args.zip_into / (out.name + ".zip")
        print(f"{zip_folder(out, target)}  {target.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
