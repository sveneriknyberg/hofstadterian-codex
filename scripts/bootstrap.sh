# scripts/bootstrap.sh
#!/bin/bash
# v14.2: The sole entry point for a new agent session. It initializes the
# environment, archives old logs, starts the meta-monitor, and provides a full situational briefing.

# --- Setup ---
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
PROJECT_ROOT="$SCRIPT_DIR/.."
SESSION_LOG="session.log"
OLD_LOG="session.log.old"
MONITOR_SCRIPT="scripts/meta_monitor.py"
SUGGESTIONS_LOG="suggestions.log"
HANDOFFS_DIR="context/handoffs"
HANDOFF_NOTES_TEMPLATE="context/handoff_notes.md"
WISDOM_FILE="context/wisdom.json"

# --- ANSI Color Codes ---
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m'

# --- Header ---
echo -e "${CYAN}=======================================================${NC}"
echo -e "${CYAN}    Hofstadterian Codex v14.2 Bootstrap Protocol       ${NC}"
echo -e "${CYAN}=======================================================${NC}"
echo ""

# --- 1. Log Management & Template Restoration ---
cd "$PROJECT_ROOT"
if [ -f "$SESSION_LOG" ]; then
    mv -f "$SESSION_LOG" "$OLD_LOG"
    echo "✅ Previous session log archived to $OLD_LOG."
fi
echo "{\"type\": \"session_start\", \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%S.%NZ)\"}" > "$SESSION_LOG"
echo "✅ New session log initialized."

# Create a fresh handoff notes template for the new session.
cat > "$HANDOFF_NOTES_TEMPLATE" << EOF
## Summary

(Provide a one-paragraph summary of the work accomplished in this session.)

---
## Key Decisions

- (List the significant decisions made, one per line, starting with a hyphen.)

---
## Lessons Learned

- (List any important lessons learned from errors or unexpected behavior, one per line, starting with a hyphen.)
EOF
echo "✅ Clean handoff notes template created."
echo ""

# --- 2. Launch Meta-Cognitive Monitor ---
echo -e "${YELLOW}I. LAUNCHING META-COGNITIVE MONITOR...${NC}"
if [ -f "$MONITOR_SCRIPT" ]; then
    touch "$SUGGESTIONS_LOG"
    nohup python3 "$MONITOR_SCRIPT" >/dev/null 2>&1 &
    echo "✅ Monitor process launched in background. Suggestions will appear in $SUGGESTIONS_LOG."
else
    echo "⚠️ WARNING: Meta-monitor script not found. Proceeding without proactive guidance."
fi
echo ""

# --- 3. Intelligent Briefing ---
echo -e "${YELLOW}II. SITUATIONAL BRIEFING:${NC}"
LATEST_HANDOFF=$(ls -1 "$HANDOFFS_DIR"/*.json 2>/dev/null | sort -r | head -n 1)

if [ -z "$LATEST_HANDOFF" ]; then
  echo -e "  - ${CYAN}CONTEXT: No previous handoff found. This is a new Loop instance.${NC}"
else
  echo -e "  - ${CYAN}LAST HANDOFF:${NC} ${GREEN}${LATEST_HANDOFF}${NC}"
  echo -e "  - ${CYAN}SUMMARY:${NC} $(jq -r '.summary' "$LATEST_HANDOFF")"
fi

if [ -f "$WISDOM_FILE" ]; then
    echo -e "  - ${CYAN}LOOP WISDOM:${NC} $(jq -r '.lessons | length' $WISDOM_FILE) lessons and $(jq -r '.analogies | length' $WISDOM_FILE) analogies loaded."
fi
echo ""

echo -e "${CYAN}=======================================================${NC}"
echo -e "${GREEN}✅ Bootstrap complete. The Loop is active. Ready for intent.${NC}"
echo -e "${CYAN}=======================================================${NC}"

exit 0