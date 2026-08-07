r"""Path-locality validation (Phase 0 plan, D6.1).

synthtwin accepts only plain paths to files and folders on the local
computer.  This module is the single gate that every user-supplied
input, output, or temp path must pass, in every phase.  The order of
operations is fixed by the plan and is security-relevant:

1.  Lexical checks run on the raw string BEFORE any filesystem call.
    Rejected outright: URL forms (``scheme://``), Windows shared-network
    (UNC) forms (``\\server``, ``//server``), and Windows
    device/namespace forms (``\\.\``, ``\\?\``), in either slash style.
2.  On Windows, every existing path component is examined with
    ``os.lstat`` and the path is rejected if any component is a reparse
    point (symbolic link, junction, or mount point).  Only the link
    node's own local metadata is read; the link target is never read or
    followed, so no remote traversal can occur.  ``Path.resolve()`` runs
    only after this walk finds no reparse points.
3.  On POSIX, symbolic links are permitted: the path is resolved and
    the resolved string is re-validated against the same lexical rules.

Links are legitimately rare in this tool's audience workflows; the
Windows restriction and its rationale are documented in SECURITY.md,
together with the named residuals (OS-transparent network mounts,
local-actor TOCTOU).

Imports here are restricted to the exact Phase 0 allowlist (plan D6.2):
``pathlib``, ``os`` (``os.getcwd`` and ``os.lstat`` are used), ``sys``.
"""

import os
import pathlib
import sys

# Windows marks symbolic links, junctions, and mount points with this
# bit in a file's attribute flags (FILE_ATTRIBUTE_REPARSE_POINT in the
# Win32 API).  The standard-library `stat` module also defines it, but
# `stat` is not on the Phase 0 import allowlist (plan D6.2), so the
# fixed Win32 value is spelled out here instead.
FILE_ATTRIBUTE_REPARSE_POINT = 0x400

_ADVICE = (
    "Please give a plain path to a file or folder on this computer, for "
    "example /home/you/data on Linux or macOS, or C:\\Users\\you\\data "
    "on Windows."
)


class PathValidationError(ValueError):
    """A user-supplied path was rejected by the path-locality rules."""


def _is_sep(character: str) -> bool:
    """True if ``character`` is a path separator in either slash style."""
    return character == "/" or character == "\\"


def _url_scheme(text: str) -> str | None:
    """Return the scheme if ``text`` is shaped like ``scheme://...``.

    A scheme is one ASCII letter followed by zero or more ASCII letters
    or digits, immediately followed by ``://`` at the very start of the
    string.  Returns None when ``text`` is not shaped that way.
    """
    marker = text.find("://")
    if marker <= 0:
        return None
    scheme = text[:marker]
    first = scheme[0]
    if not ("a" <= first <= "z" or "A" <= first <= "Z"):
        return None
    for ch in scheme[1:]:
        if not ("a" <= ch <= "z" or "A" <= ch <= "Z" or "0" <= ch <= "9"):
            return None
    return scheme


def _rejection_reason(text: str) -> str | None:
    """Plain-language reason to reject ``text``, or None if it is clean.

    Purely lexical: this function never touches the filesystem.  It is
    applied to the raw input string first, and again to the resolved
    path string after resolution.
    """
    scheme = _url_scheme(text)
    if scheme is not None:
        return (
            f"it looks like a web or network address (it starts with "
            f"'{scheme}://'). synthtwin never reads from or writes to "
            f"the network."
        )
    if (
        len(text) >= 4
        and _is_sep(text[0])
        and _is_sep(text[1])
        and (text[2] == "." or text[2] == "?")
        and _is_sep(text[3])
    ):
        return (
            "it starts with a special Windows device prefix ('\\\\.\\' "
            "or '\\\\?\\'). synthtwin does not accept these prefixes "
            "because they bypass normal path handling."
        )
    if len(text) >= 2 and _is_sep(text[0]) and _is_sep(text[1]):
        return (
            "it starts with two slashes, which is how a shared network "
            "location is written (for example '\\\\server\\share'). "
            "synthtwin never reads from or writes to the network."
        )
    return None


def validate_local_path(raw: str, *, purpose: str) -> pathlib.Path:
    """Validate ``raw`` as a plain local path; return the resolved path.

    ``purpose`` names what the path is for (for example "input",
    "output", or "temp") and appears in every error message.

    Guarantees (plan D6.1): lexical rejection of URL, UNC, and Windows
    device forms happens on the raw string before any filesystem call;
    on Windows, a path with a reparse-point component (symbolic link,
    junction, mount point) is rejected without the target ever being
    read or followed, and resolution runs only after that walk; on
    POSIX, symbolic links are followed and the resolved string is
    re-validated against the same lexical rules.

    Raises PathValidationError (a ValueError) with a plain-language
    explanation of what was rejected and what to do instead.
    """
    if raw == "":
        raise PathValidationError(
            f"The {purpose} path is empty. Please give the path to a "
            f"file or folder on this computer."
        )

    reason = _rejection_reason(raw)
    if reason is not None:
        raise PathValidationError(
            f"The {purpose} path {raw!r} was not accepted: {reason} {_ADVICE}"
        )

    if sys.platform == "win32":
        candidate = pathlib.Path(raw)
        if not candidate.is_absolute():
            candidate = pathlib.Path(os.getcwd()) / candidate
        # Walk every existing component with os.lstat.  lstat reads the
        # component's own metadata and never follows a link, so a link
        # to a network location is rejected without any remote access.
        prefix: pathlib.Path | None = None
        for part in candidate.parts:
            prefix = pathlib.Path(part) if prefix is None else prefix / part
            try:
                details = os.lstat(prefix)
            except OSError:
                # This component does not exist yet (for example an
                # output file about to be created).  Nothing to examine.
                continue
            if details.st_file_attributes & FILE_ATTRIBUTE_REPARSE_POINT:
                raise PathValidationError(
                    f"The {purpose} path {raw!r} was not accepted: "
                    f"{str(prefix)!r} is a link (a symbolic link, "
                    f"junction, or mount point). On Windows, synthtwin "
                    f"refuses links because a link can quietly lead to "
                    f"a network location. Please spell out the real "
                    f"folder the link points to and use that path "
                    f"instead."
                )
        # Resolution is invoked only after the walk found no links.
        resolved = candidate.resolve()
    else:
        resolved = pathlib.Path(raw).resolve()

    # Re-validate the resolved string against the same lexical rules.
    # Mandated on POSIX by D6.1(iii); also applied on Windows as an
    # extra safety net (for example a drive letter mapped to a shared
    # network location resolving to a '\\server' form).
    resolved_reason = _rejection_reason(str(resolved))
    if resolved_reason is not None:
        raise PathValidationError(
            f"The {purpose} path {raw!r} was not accepted: when fully "
            f"spelled out it leads to {str(resolved)!r}, and "
            f"{resolved_reason} {_ADVICE}"
        )
    return resolved
