import json
import os
import hashlib
from collections import Counter
import yaml

# --- Constants ---
SESSION_HISTORY_FILE = ".session_history.json"
TRIGGERS_FILE = "scripts/meta_triggers.yaml"
ANALOGIES_FILE = "analogies/registry.json"
HISTORY_LOOKBACK = 10

# --- File Loading ---

def load_json(file_path):
    if not os.path.exists(file_path):
        return None
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"WARNING: Could not read or parse JSON file '{file_path}': {e}")
        return None

def load_yaml(file_path):
    try:
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)
    except (IOError, yaml.YAMLError) as e:
        print(f"WARNING: Could not read or parse YAML file '{file_path}': {e}")
        return None

# --- Analysis Functions ---

def _analyze_sequence(pattern, recent_events):
    # (No changes needed in this function)
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
            consecutive_count = 0
            sequence_tools = []
        if consecutive_count >= threshold:
            finding = {
                "type": pattern['name'],
                "message": pattern['message'],
                "details": {"count": consecutive_count, "tool_list": ", ".join(sequence_tools)}
            }
            if 'analogy_id' in pattern:
                finding['analogy_id'] = pattern['analogy_id']
            return finding
    return None

def _analyze_repetition(pattern, recent_events):
    """
    Checks for repeated failures, now extracting command context for better reporting.
    """
    threshold = pattern['threshold']
    error_events = []
    # We need to associate the error signature with the full command for context
    error_details = {}

    for event in recent_events:
        if event.get('status') == 'error':
            tool_name = event.get('tool_name', 'unknown_tool')
            error_output = str(event.get('output', ''))
            error_hash = hashlib.sha256(error_output.encode()).hexdigest()
            error_signature = (tool_name, error_hash)
            error_events.append(error_signature)
            # Store the command details against the signature
            if error_signature not in error_details:
                 error_details[error_signature] = {
                     "full_command": event.get("command", tool_name)
                 }

    if not error_events:
        return None

    error_counts = Counter(error_events)
    most_common_error, count = error_counts.most_common(1)[0]

    if count >= threshold:
        details = {
            "count": count,
            "tool_name": most_common_error[0]
        }
        # Add the full command from our lookup
        if most_common_error in error_details:
            details["full_command"] = error_details[most_common_error]["full_command"]

        finding = {
            "type": pattern['name'],
            "message": pattern.get('message'), # Keep for fallback
            "contextual_messages": pattern.get('contextual_messages', {}),
            "details": details
        }
        if 'analogy_id' in pattern:
            finding['analogy_id'] = pattern['analogy_id']
        return finding
    return None


def analyze_history(triggers, history):
    # (No changes needed in this function)
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
            break
    return findings

# --- Reporting ---

def report_findings(findings, analogies):
    """
    Prints findings, now with logic to select context-aware messages.
    """
    if not findings:
        print("Meta-cognitive check passed. No obvious loops or issues detected.")
        return

    print("\n--- META-COGNITIVE CHECK ---")
    print("Potential issues detected. Please consider the following:")

    for finding in findings:
        message = finding['message'] # Default message

        # New logic for contextual messages
        if finding.get('contextual_messages'):
            full_command = finding['details'].get('full_command', '')
            for keyword, specific_message in finding['contextual_messages'].items():
                if keyword in full_command:
                    message = specific_message
                    break # Use the first one that matches

        if message:
             print(f"\n{message.format(**finding['details'])}")
        else: # Fallback if no message is defined at all
            print(f"\n[!] Finding: {finding['type']}")


        if 'analogy_id' in finding and analogies:
            analogy_id = finding['analogy_id']
            analogy = analogies.get(analogy_id)
            if analogy:
                print("\n  [Suggested Analogy]: " + analogy_id)
                print(f"  > {analogy['rationale']}")

    print("\n--- END CHECK ---")

# --- Main Execution ---

def main():
    project_root = os.getcwd()
    history_file_path = os.path.join(project_root, SESSION_HISTORY_FILE)
    triggers_file_path = os.path.join(project_root, TRIGGERS_FILE)
    analogies_file_path = os.path.join(project_root, ANALOGIES_FILE)

    history = load_json(history_file_path) or []
    triggers = load_yaml(triggers_file_path)
    if triggers is None: return

    analogies = load_json(analogies_file_path)

    findings = analyze_history(triggers, history)
    report_findings(findings, analogies)

if __name__ == "__main__":
    main()
