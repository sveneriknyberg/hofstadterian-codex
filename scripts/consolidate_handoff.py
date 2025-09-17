# scripts/consolidate_handoff.py
# v14.2: Creates the JSON handoff and merges new wisdom into the Loop's brain.

import json
import os
import uuid
import re
from datetime import datetime, timezone
import argparse
import base64
import subprocess

HANDOFF_DIR = 'context/handoffs'
HANDOFF_NOTES_FILE = 'context/handoff_notes.md'
WISDOM_FILE = 'context/wisdom.json'

def get_command_output(command):
    try:
        return subprocess.run(command, shell=True, check=True, capture_output=True, text=True).stdout.strip()
    except Exception as e:
        return f"Error executing command '{command}': {e}"

def parse_handoff_notes():
    notes = {"summary": "No summary provided.", "decisions": [], "lessons": []}
    if not os.path.exists(HANDOFF_NOTES_FILE):
        return notes
    
    with open(HANDOFF_NOTES_FILE, 'r') as f:
        content = f.read()

    # Define placeholders to ignore
    summary_placeholder = "(Provide a one-paragraph summary of the work accomplished in this session.)"
    decisions_placeholder = "(List the significant decisions made, one per line, starting with a hyphen.)"
    lessons_placeholder = "(List any important lessons learned from errors or unexpected behavior, one per line, starting with a hyphen.)"

    summary_match = re.search(r'## Summary\s*\n(.*?)(?=\n--|$)', content, re.DOTALL)
    if summary_match:
        summary_text = summary_match.group(1).strip()
        if summary_text != summary_placeholder:
            notes['summary'] = summary_text
    
    decisions_match = re.search(r'## Key Decisions\s*\n(.*?)(?=\n--|$)', content, re.DOTALL)
    if decisions_match:
        all_decisions = [line.strip('- ').strip() for line in decisions_match.group(1).strip().split('\n') if line.strip().startswith('- ')]
        # Filter out the placeholder text
        notes['decisions'] = [d for d in all_decisions if d != decisions_placeholder]

    lessons_match = re.search(r'## Lessons Learned\s*\n(.*?)(?=\n--|$)', content, re.DOTALL)
    if lessons_match:
        all_lessons = [line.strip('- ').strip() for line in lessons_match.group(1).strip().split('\n') if line.strip().startswith('- ')]
        # Filter out the placeholder text
        notes['lessons'] = [l for l in all_lessons if l != lessons_placeholder]
        
    return notes

def update_wisdom(new_wisdom):
    os.makedirs(os.path.dirname(WISDOM_FILE), exist_ok=True)
    try:
        with open(WISDOM_FILE, 'r') as f:
            wisdom = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        wisdom = {"decisions": [], "lessons": [], "analogies": {}, "proven_workflows": []}

    timestamp = datetime.now(timezone.utc).isoformat()
    for decision in new_wisdom['decisions']:
        if decision not in [d.get('decision') for d in wisdom.get('decisions', [])]:
             wisdom['decisions'].append({"timestamp": timestamp, "decision": decision, "source": "session_handoff"})
    for lesson in new_wisdom['lessons']:
        if lesson not in [l.get('lesson') for l in wisdom.get('lessons', [])]:
            wisdom['lessons'].append({"timestamp": timestamp, "lesson": lesson, "source": "session_handoff"})
    
    with open(WISDOM_FILE, 'w') as f:
        json.dump(wisdom, f, indent=2)
    print(f"✅ Wisdom file updated.")

def main():
    parser = argparse.ArgumentParser(description="v14.2 Consolidate Handoff")
    parser.add_argument("--session-data", help="Base64 encoded session log data.")
    args = parser.parse_args()

    os.makedirs(HANDOFF_DIR, exist_ok=True)
    
    session_log = []
    if args.session_data:
        try:
            log_content = base64.b64decode(args.session_data).decode('utf-8')
            session_log = [json.loads(line) for line in log_content.strip().split('\n') if line]
        except Exception: pass

    notes = parse_handoff_notes()
    update_wisdom(notes)

    handoff_data = {
        "handoff_id": str(uuid.uuid4()),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "protocol_version": "14.2",
        "summary": notes['summary'],
        "state": {
            "git_status": get_command_output("git status --porcelain"),
            "git_diff_staged": get_command_output("git diff --staged")
        },
        "full_session_log": session_log
    }
    
    ts_str = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')
    handoff_filename = os.path.join(HANDOFF_DIR, f"handoff_{ts_str}.json")
    
    with open(handoff_filename, 'w') as f:
        json.dump(handoff_data, f, indent=2)
        
    if os.path.exists(HANDOFF_NOTES_FILE):
        os.remove(HANDOFF_NOTES_FILE)
        
    print(f"✅ Handoff complete. Packaged into: {handoff_filename}")

if __name__ == "__main__":
    main()
