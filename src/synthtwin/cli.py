"""The `synthtwin` command. Phase 0: version and status only.

Imports here are restricted to the exact allowlist in the Phase 0 plan
(D6.2); the offline-static scanner enforces the list in CI.
"""

import argparse
import importlib.metadata
import sys

_REPO_URL = "https://github.com/alfredocr05/synthtwin"

_STATUS = """synthtwin {version}

Status: pre-alpha skeleton. The tool that will profile your table and
generate its synthetic twin is being built phase by phase, in the open,
with an adversarial review gate on every phase. Nothing here reads data
yet.

What exists today: this command, the security baseline (offline guarantee,
decontamination scanner, data-provenance guard), and the project's plans
and review record.

Project home: {repo}
"""


def _version() -> str:
    try:
        return importlib.metadata.version("synthtwin")
    except Exception:  # noqa: BLE001 -- the import allowlist (plan
        # D6.2) permits only importlib.metadata.version, so the
        # specific PackageNotFoundError name cannot be referenced.
        # Running from an uninstalled source tree: metadata is absent.
        return "0+unknown (package not installed; run `pip install -e .`)"


def main(argv: "list[str] | None" = None) -> int:
    """Run the `synthtwin` command.

    Guarantees:

    - Inputs: `argv` is the list of command-line arguments to parse, or
      `None` to parse `sys.argv[1:]`. The only recognized flags are
      `--version` and `--help`.
    - Return codes: returns 0 on every handled invocation. With
      `--version` it prints exactly the installed package version (from
      `importlib.metadata.version("synthtwin")`, the single version
      source, plan D4) followed by a newline; with no arguments it
      prints the version-and-status block. If the package metadata is
      absent (uninstalled source tree), a plain-language placeholder
      version is printed instead of raising.
    - Errors raised: argparse raises `SystemExit` - exit code 2 for an
      unrecognized argument (message on stderr), exit code 0 for
      `--help`. If writing to the output stream fails (for example, the
      stream is closed), the interpreter's ordinary I/O exception
      propagates unchanged.
    - Boundary: no user data path is read. The version lookup consults
      the installed package's metadata on disk through
      `importlib.metadata`; no other filesystem access occurs, and no
      network, subprocess, native, or dynamic-code operation is
      performed. Imports stay within the plan D6.2 allowlist.
    """
    parser = argparse.ArgumentParser(
        prog="synthtwin",
        description=(
            "Create a synthetic twin of your tabular data: same shape, "
            "same statistics, no real records. Pre-alpha: no data "
            "functionality yet."
        ),
    )
    parser.add_argument(
        "--version", action="store_true", help="print the version and exit"
    )
    args = parser.parse_args(argv)

    if args.version:
        print(_version())
        return 0

    print(_STATUS.format(version=_version(), repo=_REPO_URL))
    return 0


if __name__ == "__main__":
    sys.exit(main())
