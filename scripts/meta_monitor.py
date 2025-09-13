import time
import json
import os
import yaml

# --- Configuration ---
SESSION_HISTORY_FILE = ".session_history.json"
TRIGGERS_FILE = "scripts/meta_triggers.yaml"
SUGGESTIONS_LOG = "context/metacog_suggestions.log"
ANALOGY_REGISTRY = "analogies/registry.json"
SLEEP_INTERVAL = 15  # seconds

# --- State ---
last_processed_entry_count = 0

def load_json(filepath, default=None):
    """Safely load a JSON file."""
    if not os.path.exists(filepath):
        return default
    with open(filepath, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return default

def load_yaml(filepath):
    """Safely load a YAML file."""
    if not os.path.exists(filepath):
        return None
    with open(filepath, 'r') as f:
        try:
            return yaml.safe_load(f)
        except yaml.YAMLError:
            return None

def log_suggestion(message):
    """Append a suggestion to the suggestions log."""
    with open(SUGGESTIONS_LOG, 'a') as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")
    print(f"Meta-cognitive suggestion logged: {message}")

def check_analysis_paralysis(history, pattern):
    """Check for the 'Analysis Paralysis' pattern."""
    threshold = pattern.get('threshold', 5)
    if len(history) < threshold:
        return

    recent_commands = [entry['command'].split(' ')[0] for entry in history[-threshold:]]
    read_only_tools = set(pattern.get('tools', []))

    if all(cmd in read_only_tools for cmd in recent_commands):
        tool_list_str = ", ".join(recent_commands)
        message = pattern['message'].format(count=threshold, tool_list=tool_list_str)
        log_suggestion(message)
        return True # Pattern detected
    return False

def check_tool_fixation(history, pattern):
    """Check for the 'Tool Fixation' pattern."""
    threshold = pattern.get('threshold', 3)
    lookback = 10 # Check the last 10 commands for failures

    if len(history) < threshold:
        return

    recent_failures = {}
    for entry in history[-lookback:]:
        if entry['exit_code'] != 0:
            tool_name = entry['command'].split(' ')[0]
            recent_failures[tool_name] = recent_failures.get(tool_name, 0) + 1

    for tool, count in recent_failures.items():
        if count >= threshold:
            # Check for a specific message for this tool, otherwise use default
            message = pattern.get('contextual_messages', {}).get(tool, pattern['message'])
            message = message.format(tool_name=tool, count=count)
            log_suggestion(message)
            return True # Pattern detected
    return False


def main():
    global last_processed_entry_count
    print("Meta-cognitive monitor started in the background.")

    while True:
        history = load_json(SESSION_HISTORY_FILE, [])
        triggers = load_yaml(TRIGGERS_FILE)

        if not history or not triggers:
            time.sleep(SLEEP_INTERVAL)
            continue

        # Process only new entries
        if len(history) > last_processed_entry_count:
            # For simplicity in this first pass, we'll re-evaluate the whole window
            # A more complex implementation would only check the new slice.

            patterns = triggers.get('patterns', [])
            detected_pattern = False
            for pattern in patterns:
                if detected_pattern: break # Only log one suggestion per cycle

                if pattern['name'] == 'Analysis Paralysis':
                    if check_analysis_paralysis(history, pattern):
                        detected_pattern = True

                elif pattern['name'] == 'Tool Fixation':
                    if check_tool_fixation(history, pattern):
                        detected_pattern = True

        last_processed_entry_count = len(history)
        time.sleep(SLEEP_INTERVAL)


if __name__ == "__main__":
    main()
