#!/bin/bash

# agent_bootstrap.sh (v2)
# This script provides an intelligent situational awareness briefing for a new agent instance.

# --- Setup ---
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
PROJECT_ROOT="$SCRIPT_DIR/.."

# --- ANSI Color Codes ---
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# --- Header ---
echo -e "${CYAN}=======================================================${NC}"
echo -e "${CYAN}    AGENT BOOTSTRAP PROTOCOL (v2) - INITIALIZING...    ${NC}"
echo -e "${CYAN}=======================================================${NC}"
echo ""

# --- 1. The Prime Directive ---
echo -e "${YELLOW}I. THE PRIME DIRECTIVE (from AGENTS.md):${NC}"
sed -n '/X. THE PRIME DIRECTIVE/,/---/p' "$PROJECT_ROOT/AGENTS.md" | sed '1d;$d' | while IFS= read -r line; do
  echo -e "  ${GREEN}${line}${NC}"
done
echo ""

# --- 2. Launch Meta-Cognitive Monitor ---
echo -e "${YELLOW}II. LAUNCHING META-COGNITIVE MONITOR...${NC}"
touch "$PROJECT_ROOT/context/metacog_suggestions.log"
nohup python3 "$PROJECT_ROOT/scripts/meta_monitor.py" >/dev/null 2>&1 &
echo -e "  ${GREEN}Monitor process launched in background.${NC}"
echo ""

# --- 3. Intelligent Briefing ---
echo -e "${YELLOW}III. INTELLIGENT BRIEFING:${NC}"
LATEST_PACKET=$(ls -1 "$PROJECT_ROOT/artifacts/" | grep "wisdom_packet" | sort -r | head -n 1)
ROADMAP_FILE="$PROJECT_ROOT/context/roadmap.md"

if [ -z "$LATEST_PACKET" ]; then
  echo -e "  ${CYAN}No previous wisdom packets found. This may be a new Loop instance.${NC}"
else
  echo -e "  ${CYAN}Most recent wisdom packet: ${GREEN}${LATEST_PACKET}${NC}"
fi

if [ ! -f "$ROADMAP_FILE" ]; then
    echo -e "  ${RED}CRITICAL: Roadmap file not found at ${ROADMAP_FILE}${NC}"
    NEXT_STEP="CRITICAL: Roadmap file not found."
else
    # Find the first line that starts with "- [ ]" or "- **" which indicates an incomplete task.
    # We use grep and then head to get only the first match.
    NEXT_STEP=$(grep -E '^\s*-\s*(\[ \]|(\*\*))' "$ROADMAP_FILE" | head -n 1)

    if [ -z "$NEXT_STEP" ]; then
        NEXT_STEP="All roadmap items appear to be complete. Please review the roadmap and define the next phase."
    fi
fi
echo ""
echo -e "${YELLOW}IV. SUGGESTED NEXT STEP:${NC}"
echo -e "  ${GREEN}${NEXT_STEP}${NC}"
echo ""


# --- 5. Hierarchy of Truth ---
echo -e "${YELLOW}V. HIERARCHY OF TRUTH (Reminder from AGENTS.md):${NC}"
sed -n '/I. HIERARCHY OF TRUTH/,/---/p' "$PROJECT_ROOT/AGENTS.md" | sed '1d;$d' | while IFS= read -r line; do
  echo -e "  ${GREEN}${line}${NC}"
done
echo ""


echo -e "${CYAN}=======================================================${NC}"
echo -e "${CYAN}          CONTEXT INITIALIZATION COMPLETE              ${NC}"
echo -e "${CYAN}=======================================================${NC}"

# --- 6. Run Loop Health Check ---
python3 "$PROJECT_ROOT/scripts/validate_context.py"

echo ""
echo -e "${YELLOW}Your primary goal is to contribute to the Loop. Good luck.${NC}"

# --- 7. Create Bootstrap Sentinel ---
touch "$PROJECT_ROOT/.bootstrapped"
echo -e "\n${GREEN}[INFO] Bootstrap sentinel file created at '$PROJECT_ROOT/.bootstrapped'.${NC}"
