import json
import os
import fcntl

# --- Constants ---
SESSION_HISTORY_FILE = ".session_history.json"
PROVEN_WORKFLOWS_FILE = "context/proven_workflows.json"

# --- Helper Functions ---

def load_json_log(file_path, default=None):
    """Safely loads a JSON file, with file locking."""
    if default is None:
        default = []
    if not os.path.exists(file_path):
        return default
    try:
        with open(file_path, 'r') as f:
            fcntl.flock(f, fcntl.LOCK_SH)
            content = json.load(f)
            fcntl.flock(f, fcntl.LOCK_UN)
            return content
    except (json.JSONDecodeError, IOError):
        return default

def save_json_log(file_path, data):
    """Safely saves data to a JSON file, with file locking."""
    try:
        with open(file_path, 'w') as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            json.dump(data, f, indent=2)
            fcntl.flock(f, fcntl.LOCK_UN)
    except IOError as e:
        print(f"Error saving JSON file: {e}")

def is_pytest_run(event):
    """Checks if a history event is a pytest execution."""
    # This is a simple check. A more robust version might be needed
    # if tests are run in more complex ways.
    return "pytest" in event.get("command", "")

def find_last_run_by_status(history, status):
    """Finds the index and event of the last pytest run with a given status."""
    for i, event in reversed(list(enumerate(history))):
        if is_pytest_run(event) and event.get("status") == status:
            return i, event
    return -1, None

def extract_workflow_from_slice(log_slice):
    """Extracts the core actions from a sequence of events."""
    workflow_steps = []
    modified_files = set()

    for event in log_slice:
        tool_name = event.get("tool_name")
        # We only care about actions the agent took, not observations
        if tool_name in ["create_file_with_block", "overwrite_file_with_block", "replace_with_git_merge_diff"]:
            # The file path is usually the first argument
            filepath = event.get("tool_args", [])[0] if event.get("tool_args") else "unknown_file"
            modified_files.add(filepath)
            workflow_steps.append({
                "tool_name": tool_name,
                "tool_args": event.get("tool_args")
            })

    return workflow_steps, list(modified_files)

# --- Main Logic ---

def main():
    history = load_json_log(SESSION_HISTORY_FILE)
    if not history or len(history) < 2:
        return # Not enough events to find a workflow

    # 1. Check if the last event was a successful test run
    last_event = history[-1]
    if not (is_pytest_run(last_event) and last_event.get("status") == "success"):
        return

    # 2. Check if this success has already been processed
    proven_workflows = load_json_log(PROVEN_WORKFLOWS_FILE)
    success_timestamp = last_event.get("timestamp")
    if any(wf.get("success_timestamp") == success_timestamp for wf in proven_workflows):
        return # This success has already generated a workflow

    # 3. Find the most recent test failure before this success
    failure_index, _ = find_last_run_by_status(history[:-1], "error")
    if failure_index == -1:
        return # No prior failure found

    # 4. Extract the slice of events that constitutes the workflow
    # The slice starts right after the failure and ends right before the success
    workflow_slice = history[failure_index + 1 : -1]

    workflow_steps, modified_files = extract_workflow_from_slice(workflow_slice)

    if not workflow_steps:
        return # The workflow had no meaningful file-editing actions

    # 5. Create the new proven workflow object
    new_workflow = {
        "name": f"Workflow that fixed tests related to: {', '.join(modified_files)}",
        "success_timestamp": success_timestamp,
        "modified_files": modified_files,
        "sequence": workflow_steps,
    }

    # 6. Append and save
    proven_workflows.append(new_workflow)
    save_json_log(PROVEN_WORKFLOWS_FILE, proven_workflows)
    # print(f"New workflow discovered and saved: {new_workflow['name']}") # Optional: for debugging

if __name__ == "__main__":
    main()
