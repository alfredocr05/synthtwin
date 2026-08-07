#!/bin/sh
# One-command advisory pre-push hook installer (plan D13).
# Usage: sh tools/hooks/install.sh   (from the repository root)
set -e
REPO_ROOT="$(git rev-parse --show-toplevel)"
HOOK="$REPO_ROOT/.git/hooks/pre-push"
cat > "$HOOK" <<'HOOKBODY'
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
chmod +x "$HOOK"
echo "Installed the advisory pre-push hook at $HOOK"
