#!/bin/sh
# One-command advisory hook installer (plans D13 and P4-D362).
# Usage: sh tools/hooks/install.sh   (from the repository root)
#
# Installs two hooks. pre-push runs the guards on the tree about to be
# pushed and scans the message of every commit the push sends;
# commit-msg scans a message before its commit exists. Both read the
# messages with tools/hooks/check_messages.py.
#
# Safe to re-run: when an installed hook is already exactly this
# installer's hook, the script quietly succeeds and changes nothing.
# When a DIFFERENT hook exists, the script refuses to touch it and
# prints what to do instead, so an existing organizational or security
# hook is never destroyed; the other hook is still installed. The one
# hook it does replace is a pre-push hook byte for byte the one an
# earlier version of this installer wrote: the new hook runs every
# guard that one ran, so nothing it did is lost.
set -e

# The git blob ids of the three pre-push hooks earlier versions of this
# installer wrote (58d3599, 41982f7 and 2bf3907).
EARLIER_PRE_PUSH="90e9dd0702afca8cb39af7bd69248889c8613542 e07367274fad699b5267ea33c9e42404944fc222 df568b2b28a032c382486dddb8460c5eb17ab7cc"
REFUSED=0

# install_hook NAME EARLIER_IDS, with the hook's text on standard input.
install_hook() {
    # Ask git for the ACTIVE hook path (review item R3-m1). This honors
    # core.hooksPath and linked worktrees, where the hard-coded
    # .git/hooks/NAME shape is wrong or inactive. git prints the path
    # relative to the current directory when it can; make it absolute so
    # the messages below name one unambiguous file.
    hook="$(git rev-parse --git-path "hooks/$1")"
    case "$hook" in
        /*) ;;
        [A-Za-z]:*) ;;
        *) hook="$(pwd)/$hook" ;;
    esac
    mkdir -p "$(dirname "$hook")"
    new_hook="$hook.synthtwin.tmp"
    cat > "$new_hook"
    if [ -e "$hook" ]; then
        if cmp -s "$hook" "$new_hook"; then
            # Identical hook already installed: quiet success.
            rm -f "$new_hook"
            chmod +x "$hook"
            return 0
        fi
        if [ -n "$2" ]; then
            found="$(git hash-object --stdin < "$hook")"
            case " $2 " in
                *" $found "*)
                    mv "$new_hook" "$hook"
                    chmod +x "$hook"
                    echo "Replaced the earlier synthtwin $1 hook at $hook"
                    return 0
                    ;;
            esac
        fi
        rm -f "$new_hook"
        echo "ERROR: a different $1 hook already exists at:" >&2
        echo "  $hook" >&2
        echo "Refusing to overwrite it, because doing so would silently" >&2
        echo "remove whatever that hook currently does. Pick one:" >&2
        echo "  1. Chain manually: copy the guard commands from" >&2
        echo "     tools/hooks/install.sh into your existing hook." >&2
        echo "  2. Remove the existing hook, then re-run this installer:" >&2
        echo "     rm \"$hook\" && sh tools/hooks/install.sh" >&2
        REFUSED=1
        return 0
    fi
    mv "$new_hook" "$hook"
    chmod +x "$hook"
    echo "Installed the advisory $1 hook at $hook"
}

install_hook pre-push "$EARLIER_PRE_PUSH" <<'HOOKBODY'
#!/bin/sh
# synthtwin advisory pre-push hook: runs the guards on the tree about to
# be pushed and scans the message of every commit the push sends.
# Advisory by design (plan D13): it can be bypassed with --no-verify.
# CI remains the authoritative check; from Phase 3's visibility flip the
# branch ruleset makes the CI gate a mechanically enforced merge
# requirement (see SECURITY.md's activation record).
set -e
cd "$(git rev-parse --show-toplevel)"
PY=".venv/bin/python"; [ -x "$PY" ] || PY="python3"
# git names the refs being pushed on this hook's input: kept before any
# guard runs, so that none of them can consume it.
PUSHED="$(cat)"
echo "pre-push: decontamination scan..."
"$PY" tools/decontamination/check.py
echo "pre-push: commit messages..."
if [ -f tools/hooks/check_messages.py ]; then
    printf '%s\n' "$PUSHED" | "$PY" tools/hooks/check_messages.py --pre-push
else
    echo "pre-push: this checkout has no tools/hooks/check_messages.py, so no message was scanned."
fi
echo "pre-push: attestation verification..."
"$PY" tools/decontamination/verify_attestation.py
echo "pre-push: offline static scan..."
"$PY" tools/offline_scan/scan_imports.py src
echo "pre-push: provenance check..."
"$PY" tools/provenance/check_provenance.py
echo "pre-push: all guards passed."
HOOKBODY

install_hook commit-msg "" <<'HOOKBODY'
#!/bin/sh
# synthtwin advisory commit-msg hook: scans the message of the commit
# being made against the decontamination manifest, before that commit
# exists (plan P4-D362). Advisory by design (plan D13): it can be
# bypassed with --no-verify; the pre-push hook and CI read the stored
# message again.
set -e
TOP="$(git rev-parse --show-toplevel)"
PY="$TOP/.venv/bin/python"; [ -x "$PY" ] || PY="python3"
if [ ! -f "$TOP/tools/hooks/check_messages.py" ]; then
    echo "commit-msg: this checkout has no tools/hooks/check_messages.py, so the message was not scanned."
    exit 0
fi
exec "$PY" "$TOP/tools/hooks/check_messages.py" --message-file "$1"
HOOKBODY

exit "$REFUSED"
