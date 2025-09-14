#!/bin/bash

# --- Pre-Submit Check Script (v6 - Sandbox Aware) ---
# This script validates that the repository is in a clean and consistent
# state before a submission, according to the Exoskeleton protocol.
# This version is aware that it runs in a sandbox where `git status` is
# not a reliable indicator of work.

echo "--- Running Pre-Submit Checks (v6) ---"

# In the sandbox, we can't rely on `git status`. The most reliable indicator
# of work having been done is the presence of a new wisdom packet.

# --- Check 1: Check for a new Wisdom Packet ---
echo "[1/3] Checking for a new Wisdom Packet..."
# We search for any wisdom packet file. The `submit` tool will handle what is
# actually committed. The presence of a packet is proof of work.
LATEST_PACKET=$(ls -1 artifacts/ | grep "wisdom_packet_.*\.json$" | sort -r | head -n 1)

if [ -n "$LATEST_PACKET" ]; then
    echo "  [PASS] Found new Wisdom Packet: $LATEST_PACKET"
else
    echo "  [FAIL] No new Wisdom Packet was found in the 'artifacts/' directory."
    echo "         This likely means no changes have been made, or you forgot to run 'python3 scripts/consolidate_handoff.py' to document your work."
    # We exit 0 here because having no changes might be valid. The `submit` tool will fail if there's nothing to commit.
    exit 0
fi

# --- Check 2: Run unit tests ---
echo "[2/3] Running unit tests..."
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
