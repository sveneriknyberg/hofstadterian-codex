#!/bin/bash

# --- Pre-Submit Check Script (v5 - Exoskeleton) ---
# This script validates that the repository is in a clean and consistent
# state before a submission, according to the Exoskeleton protocol.

echo "--- Running Pre-Submit Checks (v5) ---"

# --- Check 1: Check for uncommitted work ---
echo "[1/4] Checking for uncommitted work..."
GIT_STATUS=$(git status --porcelain)

if [ -z "$GIT_STATUS" ]; then
    echo "  [PASS] Git working directory is clean. Nothing to check."
    exit 0
else
    echo "  [INFO] Found uncommitted changes. Proceeding with checks..."
fi

# --- Check 2: Check for a new Wisdom Packet ---
echo "[2/4] Checking for a new Wisdom Packet..."
# If there are changes, there must be a new, untracked wisdom packet.
if echo "$GIT_STATUS" | grep -q "^?? artifacts/wisdom_packet_.*\.json$"; then
    echo "  [PASS] Found new, untracked Wisdom Packet."
else
    echo "  [FAIL] There are uncommitted changes, but no new Wisdom Packet was found in the 'artifacts/' directory."
    echo "         Please run 'python3 scripts/consolidate_handoff.py' to document your work."
    exit 1
fi

# --- Check 3: Run unit tests ---
echo "[3/3] Running unit tests..."
# Ensure dependencies are installed for this ephemeral session
if [ -f "scripts/requirements.txt" ]; then
    python3 -m pip install -r scripts/requirements.txt > /dev/null 2>&1
fi
if [ -f "tests/requirements.txt" ]; then
    python3 -m pip install -r tests/requirements.txt > /dev/null 2>&1
fi

if python3 -m pytest; then
    echo "  [PASS] All unit tests passed."
else
    echo "  [FAIL] Unit tests failed. Please fix them before submitting."
    exit 1
fi

echo ""
echo "--- All Pre-Submit Checks Passed ---"
exit 0
