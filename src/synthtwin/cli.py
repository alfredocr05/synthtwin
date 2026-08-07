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
