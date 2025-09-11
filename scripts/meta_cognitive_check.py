import json
import os
import hashlib
from collections import Counter
import yaml

# --- Constants ---
SESSION_HISTORY_FILE = ".session_history.json"
TRIGGERS_FILE = "scripts/meta_triggers.yaml"
# Number of recent events to analyze
HISTORY_LOOKBACK = 10

def load_yaml(file_path):
    """Loads a YAML file."""
    try:
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)
    except (IOError, yaml.YAMLError) as e:
        print(f"WARNING: Could not read or parse YAML file '{file_path}': {e}")
        return None

def load_history(history_file_path):
    """Loads the session history from the specified JSON file."""
    if not os.path.exists(history_file_path):
        print("INFO: Session history file not found. Cannot perform meta-cognitive check.")
        return None
    try:
        with open(history_file_path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"WARNING: Could not read or parse session history file: {e}")
        return None

def _analyze_sequence(pattern, recent_events):
    """Checks for a sequence of specific tool types."""
    threshold = pattern['threshold']
    tool_names = set(pattern['tools'])

    consecutive_count = 0
    sequence_tools = []
    for event in recent_events:
        tool_name = event.get('tool_name', 'unknown_tool')
        if tool_name in tool_names:
            consecutive_count += 1
            sequence_tools.append(tool_name)
        else:
            # Reset if the sequence is broken
            consecutive_count = 0
            sequence_tools = []

        if consecutive_count >= threshold:
            return {
                "type": pattern['name'],
                "message": pattern['message'],
                "details": {
                    "count": consecutive_count,
                    "tool_list": ", ".join(sequence_tools)
                }
            }
    return None

def _analyze_repetition(pattern, recent_events):
    """Checks for repeated failures of the same tool."""
    threshold = pattern['threshold']

    error_events = []
    for event in recent_events:
        if event.get('status') == 'error':
            tool_name = event.get('tool_name', 'unknown_tool')
            error_output = str(event.get('output', ''))
            error_hash = hashlib.sha256(error_output.encode()).hexdigest()
            error_signature = (tool_name, error_hash)
            error_events.append(error_signature)

    if not error_events:
        return None

    # Count occurrences of each unique error
    error_counts = Counter(error_events)
    most_common_error, count = error_counts.most_common(1)[0]

    if count >= threshold:
        # This is a simplified check. A more robust version might check for consecutive errors.
        # The original script's logic was for consecutive errors, this is for total recent errors.
        # Let's stick to the spirit of "Tool Fixation" which is about recent repetition.
        return {
            "type": pattern['name'],
            "message": pattern['message'],
            "details": {
                "count": count,
                "tool_name": most_common_error[0]
            }
        }
    return None


def analyze_history(triggers, history):
    """Analyzes the last few events in the history for patterns defined in triggers."""
    if not history or not triggers:
        return []

    findings = []
    recent_events = history[-HISTORY_LOOKBACK:]

    for pattern in triggers.get('patterns', []):
        finding = None
        if pattern['type'] == 'sequence':
            finding = _analyze_sequence(pattern, recent_events)
        elif pattern['type'] == 'repetition':
            finding = _analyze_repetition(pattern, recent_events)

        if finding:
            findings.append(finding)
            # Stop after the first finding to not overwhelm the agent
            break

    return findings

def report_findings(findings):
    """Prints Socratic questions based on the analysis findings."""
    if not findings:
        print("Meta-cognitive check passed. No obvious loops or issues detected.")
        return

    print("\n--- META-COGNITIVE CHECK ---")
    print("Potential issues detected. Please consider the following:")

    for finding in findings:
        # Use the message from the trigger, formatting it with the finding details
        message = finding['message'].format(**finding['details'])
        print(f"\n{message}")

    print("\n--- END CHECK ---")


def main():
    """Main function to run the meta-cognitive check."""
    # The script assumes it's run from the project root.
    project_root = os.getcwd()
    history_file_path = os.path.join(project_root, SESSION_HISTORY_FILE)
    triggers_file_path = os.path.join(project_root, TRIGGERS_FILE)

    history = load_history(history_file_path)
    if history is None:
        return

    triggers = load_yaml(triggers_file_path)
    if triggers is None:
        return

    findings = analyze_history(triggers, history)
    report_findings(findings)

if __name__ == "__main__":
    main()
