#!/bin/bash

# --- Pre-Submit Check Script (v4) ---
# This script acts as a gatekeeper to ensure the repository is in a
# clean and consistent state before a submission is requested.
# It validates that a handoff has been created for the latest work
# and that the test suite passes.

echo "--- Running Pre-Submit Checks (v4) ---"

# --- Check 1: Handoff exists for uncommitted work ---
echo "[1/3] Checking for a new handoff file..."

GIT_STATUS=$(git status --porcelain)

if [ -z "$GIT_STATUS" ]; then
    echo "  [PASS] Git working directory is clean. No new handoff required."
else
    # There are changes, so we expect an untracked handoff file
    if echo "$GIT_STATUS" | grep -q "^?? handoffs/"; then
        echo "  [PASS] Found new, untracked handoff file for the current changes."
    else
        echo "  [FAIL] There are uncommitted changes, but no new handoff file was found in the 'handoffs/' directory."
        echo "         Please run 'python3 scripts/create_handoff.py' to document your work."
        exit 1
    fi
fi

# --- Check 2: Git working directory is clean (should be redundant now, but good for sanity) ---
# This check is slightly different. The one above checks for a handoff IF there is work.
# This one will fail if there are modified (but tracked) files without a handoff, which is a valid failure case.
# The logic is: if there are changes, the only untracked file should be the handoff.
# This is getting complex. Let's simplify. The first check is sufficient. If there are changes, there must be a handoff.
# The check for a fully clean directory is a different state.

# Let's stick to the main logic:
# 1. Are there changes?
# 2. If yes, is one of them a new handoff?

# The logic from above is correct. I will remove the old Check 2.


# --- Check 2: Run unit tests ---
echo "[2/3] Running unit tests..."
# Ensure dependencies are installed for this ephemeral session
python3 -m pip install -r scripts/requirements.txt -r tests/requirements.txt > /dev/null 2>&1
if python3 -m pytest; then
    echo "  [PASS] All unit tests passed."
else
    echo "  [FAIL] Unit tests failed. Please fix them before submitting."
    exit 1
fi

# --- Check 3: Final check for modified tracked files ---
# This is a final sanity check. If we have a new handoff, we should not have other modified files
# unless they are also being committed. This is a good check to have.
if echo "$GIT_STATUS" | grep -q "^ M "; then
    echo "  [WARNING] Found modified tracked files. Ensure they are part of this commit."
fi


echo "--- All Pre-Submit Checks Passed ---"
exit 0
