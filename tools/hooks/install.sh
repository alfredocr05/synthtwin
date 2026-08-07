#!/bin/sh
# One-command advisory pre-push hook installer (plan D13).
# Usage: sh tools/hooks/install.sh   (from the repository root)
#
# Safe to re-run: when the installed hook is already exactly this hook,
# the script quietly succeeds and changes nothing. When a DIFFERENT
# pre-push hook exists, the script refuses to touch it and prints what
# to do instead, so an existing organizational or security hook is
# never destroyed.
set -e
# Ask git for the ACTIVE pre-push hook path (review item R3-m1). This
# honors core.hooksPath and linked worktrees, where the hard-coded
# .git/hooks/pre-push shape is wrong or inactive. git prints the path
# relative to the current directory when it can; make it absolute so
# the messages below name one unambiguous file.
HOOK="$(git rev-parse --git-path hooks/pre-push)"
case "$HOOK" in
    /*) ;;
    [A-Za-z]:*) ;;
    *) HOOK="$(pwd)/$HOOK" ;;
esac
mkdir -p "$(dirname "$HOOK")"
NEW_HOOK="$HOOK.synthtwin.tmp"
cat > "$NEW_HOOK" <<'HOOKBODY'
#!/bin/sh
# synthtwin advisory pre-push hook: runs the three guards on the tree
# about to be pushed. Advisory by design (plan D13): it can be bypassed
# with --no-verify, and the public CI gate remains the enforced check.
set -e
cd "$(git rev-parse --show-toplevel)"
PY=".venv/bin/python"; [ -x "$PY" ] || PY="python3"
echo "pre-push: decontamination scan..."
"$PY" tools/decontamination/check.py
echo "pre-push: attestation verification..."
"$PY" tools/decontamination/verify_attestation.py
echo "pre-push: offline static scan..."
"$PY" tools/offline_scan/scan_imports.py src
echo "pre-push: provenance check..."
"$PY" tools/provenance/check_provenance.py
echo "pre-push: all guards passed."
HOOKBODY
if [ -e "$HOOK" ]; then
    if cmp -s "$HOOK" "$NEW_HOOK"; then
        # Identical hook already installed: quiet success.
        rm -f "$NEW_HOOK"
        chmod +x "$HOOK"
        exit 0
    fi
    rm -f "$NEW_HOOK"
    echo "ERROR: a different pre-push hook already exists at:" >&2
    echo "  $HOOK" >&2
    echo "Refusing to overwrite it, because doing so would silently" >&2
    echo "remove whatever that hook currently does. Pick one:" >&2
    echo "  1. Chain manually: copy the guard commands from" >&2
    echo "     tools/hooks/install.sh into your existing hook." >&2
    echo "  2. Remove the existing hook, then re-run this installer:" >&2
    echo "     rm \"$HOOK\" && sh tools/hooks/install.sh" >&2
    exit 1
fi
mv "$NEW_HOOK" "$HOOK"
chmod +x "$HOOK"
echo "Installed the advisory pre-push hook at $HOOK"
