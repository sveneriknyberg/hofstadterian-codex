# scripts/meta_monitor.py
# v14.2: Proactive meta-cognitive monitor.

import time
import json
import os
import yaml
from datetime import datetime, timezone

SESSION_LOG_FILE = "session.log"
TRIGGERS_FILE = "config/meta_triggers.yaml"
SUGGESTIONS_LOG = "suggestions.log"
SLEEP_INTERVAL = 10

last_processed_line = 0

def load_file(filepath, loader, default):
    try:
        with open(filepath, 'r') as f:
            return loader(f)
    except Exception:
        return default

def log_suggestion(message):
    with open(SUGGESTIONS_LOG, 'a') as f:
        f.write(f"[{datetime.now(timezone.utc).isoformat()}] {message}\n")

def check_for_patterns(log_entries, triggers):
    if not log_entries: return
    history_window = 10
    if len(log_entries) < 2: return

    for pattern in triggers.get('patterns', []):
        if pattern['name'] == 'Analysis Paralysis':
            threshold = pattern.get('threshold', 5)
            whitelist = pattern.get('tools', [])
            if not whitelist: continue # Skip if no tools are defined for this check

            command_entries = [e for e in log_entries if e.get('type') == 'command_result']

            if len(command_entries) < threshold: continue
            
            recent_commands = command_entries[-threshold:]
            is_paralysis = True
            command_list = []
            for entry in recent_commands:
                cmd_base = entry.get('command', ' ').split()[0]
                command_list.append(cmd_base)
                if cmd_base not in whitelist:
                    is_paralysis = False
                    break
            
            if is_paralysis:
                log_suggestion(pattern['message'].format(count=threshold, tool_list=", ".join(command_list)))
                return

        elif pattern['name'] == 'Tool Fixation':
            threshold = pattern.get('threshold', 3)
            failures = {}
            for entry in log_entries[-history_window:]:
                if entry.get('type') == 'command_result' and entry.get('returncode') != 0:
                    tool_name = entry.get('command', ' ').split()[0]
                    failures[tool_name] = failures.get(tool_name, 0) + 1
            
            for tool, count in failures.items():
                if count >= threshold:
                    log_suggestion(pattern['message'].format(tool_name=tool, count=count))
                    return

def main():
    global last_processed_line
    log_suggestion("Meta-cognitive monitor initialized and running.")

    triggers = load_file(TRIGGERS_FILE, yaml.safe_load, {})

    if not triggers:
        log_suggestion(f"ERROR: Missing triggers config file '{TRIGGERS_FILE}'. Monitor will not run effectively.")
        return

    while True:
        try:
            if os.path.exists(SESSION_LOG_FILE):
                with open(SESSION_LOG_FILE, 'r') as f:
                    lines = f.readlines()
                
                if len(lines) > last_processed_line:
                    all_log_entries = [json.loads(line) for line in lines if line.strip()]
                    check_for_patterns(all_log_entries, triggers)
                    last_processed_line = len(lines)
        except Exception as e:
            log_suggestion(f"MONITOR-ERROR: An exception occurred: {e}")

        time.sleep(SLEEP_INTERVAL)

if __name__ == "__main__":
    main()
