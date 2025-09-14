import json
import os
import fcntl
import subprocess
import re

# --- Constants ---
SESSION_HISTORY_FILE = ".session_history.json"
SEMANTIC_INSIGHTS_FILE = "context/semantic_insights.json"

# --- Helper Functions ---

def load_json_log(file_path, default=None):
    if default is None: default = []
    if not os.path.exists(file_path): return default
    try:
        with open(file_path, 'r') as f:
            fcntl.flock(f, fcntl.LOCK_SH)
            content = json.load(f)
            fcntl.flock(f, fcntl.LOCK_UN)
            return content
    except (json.JSONDecodeError, IOError): return default

def save_json_log(file_path, data):
    try:
        with open(file_path, 'w') as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            json.dump(data, f, indent=2)
            fcntl.flock(f, fcntl.LOCK_UN)
    except IOError as e: print(f"Error saving JSON file: {e}")

def is_pytest_run(event):
    return "pytest" in event.get("command", "")

def find_last_run_by_status(history, status):
    for i, event in reversed(list(enumerate(history))):
        if is_pytest_run(event) and event.get("status") == status:
            return i, event
    return -1, None

def extract_workflow_from_slice(log_slice):
    modified_files = set()
    for event in log_slice:
        tool_name = event.get("tool_name")
        if tool_name in ["create_file_with_block", "overwrite_file_with_block", "replace_with_git_merge_diff"]:
            filepath = event.get("tool_args", [])[0] if event.get("tool_args") else "unknown_file"
            modified_files.add(filepath)
    return list(modified_files)

def get_git_diff(filepath):
    try:
        command = ["git", "diff", "HEAD", "--", filepath]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0 and result.stderr:
             if os.path.exists(filepath):
                 with open(filepath, 'r') as f:
                     return "--- /dev/null\n" + f"+++ b/{filepath}\n" + "".join([f"+{line}" for line in f])
             else:
                return f"Error: Git diff failed for {filepath} and file not found."
        return result.stdout
    except FileNotFoundError:
        return "Error: 'git' command not found."
    except Exception as e:
        return f"An unexpected error occurred in get_git_diff: {e}"

def summarize_diff(diff_content):
    if diff_content.startswith("Error:"): return diff_content
    lines = diff_content.split('\n')
    summary_parts = []
    context = "general code"
    func_class_regex = re.compile(r'^(?:def|class)\s+([a-zA-Z0-9_]+)')
    for line in lines:
        if line.startswith('@@'):
            match = func_class_regex.search(line)
            if match: context = f"in '{match.group(1)}'"
        elif line.startswith(' '):
            match = func_class_regex.search(line.strip())
            if match: context = f"in '{match.group(1)}'"
        if line.startswith('+'):
            added_line = line[1:].strip()
            if not added_line or added_line.startswith(('#', '"""', "'''")): continue
            keywords = ['if', 'for', 'while', 'return', 'import', 'raise', 'try', 'except', 'assert']
            found_keywords = [k for k in keywords if k in added_line.split()]
            if func_class_regex.search(added_line):
                 summary_parts.append(f"Added new function/class {context}")
            elif found_keywords:
                summary_parts.append(f"Added line with '{', '.join(found_keywords)}' {context}")
            else:
                if "Modified code" not in summary_parts:
                     summary_parts.append(f"Modified code {context}")
    if not summary_parts: return "Analyzed diff but found no definitive semantic changes."
    return ". ".join(sorted(list(set(summary_parts)))) + "."

# --- Main Logic ---

def main():
    history = load_json_log(SESSION_HISTORY_FILE)
    if not history or len(history) < 2: return

    # MODIFIED LOGIC: Find the last successful test run, not just the last event.
    success_index, last_success = find_last_run_by_status(history, "success")
    if success_index == -1:
        return # No successful test run found

    insights = load_json_log(SEMANTIC_INSIGHTS_FILE)
    success_timestamp = last_success.get("timestamp")
    if any(insight.get("success_timestamp") == success_timestamp for insight in insights):
        return # This success has already been processed

    # Search for the failure in the history *before* the success
    failure_index, _ = find_last_run_by_status(history[:success_index], "error")
    if failure_index == -1:
        return # No prior failure found

    # The workflow is the slice between the failure and the success
    workflow_slice = history[failure_index + 1 : success_index]
    modified_files = extract_workflow_from_slice(workflow_slice)

    if not modified_files:
        return

    file_insights = []
    for file in modified_files:
        diff_content = get_git_diff(file)
        summary = summarize_diff(diff_content)
        file_insights.append({
            "file": file,
            "diff": diff_content,
            "summary": summary
        })

    new_insight = {
        "name": f"Semantic insight for test fix related to: {', '.join(modified_files)}",
        "success_timestamp": success_timestamp,
        "modified_files": modified_files,
        "insights": file_insights
    }

    insights.append(new_insight)
    save_json_log(SEMANTIC_INSIGHTS_FILE, insights)
    print(f"New semantic insight discovered and saved: {new_insight['name']}")

if __name__ == "__main__":
    main()
