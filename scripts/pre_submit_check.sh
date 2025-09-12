#!/bin/bash

# --- Pre-Submit Check Script ---
# This script acts as a gatekeeper to ensure the repository is in a
# clean and consistent state before a submission is requested.
# It will exit with a non-zero status code if any check fails.

echo "--- Running Pre-Submit Checks ---"

# --- Check 1: Verify a handoff has been created since the last commit ---
echo "[1/5] Checking for a new handoff file..."
LAST_COMMIT_TIME=$(git log -1 --format=%ct)
NEW_HANDOFF=$(find handoffs -name "*.md" -newermt "@${LAST_COMMIT_TIME}" | head -n 1)
if [ -z "$NEW_HANDOFF" ]; then
    echo "  [FAIL] No new handoff file found since the last commit."
    echo "         Please run 'python3 scripts/create_handoff.py' to document your work."
    exit 1
else
    echo "  [PASS] Found new handoff: $NEW_HANDOFF"
fi

# --- Check 2: Verify the latest handoff has been processed ---
echo "[2/5] Checking if the latest handoff has been processed..."
LATEST_HANDOFF_BY_NAME=$(ls -1 handoffs/*.md | sort -r | head -n 1)
LATEST_HANDOFF_FILENAME=$(basename "$LATEST_HANDOFF_BY_NAME")

if grep -q "$LATEST_HANDOFF_FILENAME" context/history.log; then
    echo "  [PASS] Latest handoff '$LATEST_HANDOFF_FILENAME' has been processed."
else
    echo "  [FAIL] Latest handoff '$LATEST_HANDOFF_FILENAME' not found in context/history.log."
    echo "         This should have been handled by 'create_handoff.py'. Please check for errors."
    exit 1
fi

# --- Check 3: Verify a code review has been requested since the last commit ---
echo "[3/5] Checking for a new code review request..."
REVIEW_LOG="context/reviews.log"
if [ ! -f "$REVIEW_LOG" ]; then
    echo "  [FAIL] Review log '$REVIEW_LOG' not found."
    echo "         Please run 'bash scripts/request_review.sh' to log your request."
    exit 1
fi

LAST_COMMIT_TIME=$(git log -1 --format=%ct)
# Check if the review log file's modification time is newer than the last commit time
if [ "$(stat -c %Y "$REVIEW_LOG")" -lt "$LAST_COMMIT_TIME" ]; then
    echo "  [FAIL] No new code review has been requested since the last commit."
    echo "         Please run 'bash scripts/request_review.sh' and then use the 'request_code_review' tool."
    exit 1
else
    echo "  [PASS] A new code review has been requested."
fi

# --- Check 4: Verify the Git working directory is clean ---
echo "[4/5] Checking for a clean Git working directory..."
if [ -z "$(git status --porcelain)" ]; then
    echo "  [PASS] Git working directory is clean."
else
    echo "  [FAIL] Git working directory is not clean. Found untracked or modified files:"
    git status --porcelain
    exit 1
fi

# --- Check 5: Run unit tests ---
echo "[5/5] Running unit tests..."
if pytest; then
    echo "  [PASS] All unit tests passed."
else
    echo "  [FAIL] Unit tests failed. Please fix them before submitting."
    exit 1
fi


echo "--- All Pre-Submit Checks Passed ---"
exit 0
