import sys
import subprocess
import json
import os
import hashlib
from datetime import datetime

LOG_FILE = ".session_history.json"
OUTPUT_DIR = ".session_outputs"
MAX_LOG_ENTRIES = 200

def manage_log_rotation_and_gc(history):
    """
    Manages log rotation by truncating old entries and performing garbage
    collection on unreferenced output files.
    """
    if len(history) <= MAX_LOG_ENTRIES:
        return history  # Nothing to do

    # Truncate the log to keep only the most recent entries
    truncated_history = history[-MAX_LOG_ENTRIES:]

    # Garbage Collection: Find all hashes still in use
    active_hashes = set()
    for entry in truncated_history:
        if entry.get("stdout_hash"):
            active_hashes.add(entry["stdout_hash"])
        if entry.get("stderr_hash"):
            active_hashes.add(entry["stderr_hash"])

    # Scan output directory and delete unreferenced files
    try:
        if os.path.exists(OUTPUT_DIR):
            for filename in os.listdir(OUTPUT_DIR):
                if filename not in active_hashes:
                    file_path = os.path.join(OUTPUT_DIR, filename)
                    try:
                        os.remove(file_path)
                    except OSError as e:
                        # This could happen if another process deleted it, which is fine.
                        # Print a warning for other unexpected errors.
                        print(f"GC_WARNING: Error deleting file {file_path}: {e}", file=sys.stderr)
    except FileNotFoundError:
        # This is fine, means the directory was deleted between the check and listdir.
        pass

    return truncated_history

def ensure_output_dir():
    """Ensures the output directory for stdout/stderr content exists."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

def hash_and_save_output(output_str):
    """
    Hashes the given string using SHA256 and saves it to a file named
    by the hash in the output directory.
    Returns the hex digest of the hash, or None if the input is empty.
    """
    if not output_str:
        return None

    hash_obj = hashlib.sha256(output_str.encode('utf-8'))
    hex_digest = hash_obj.hexdigest()

    output_filepath = os.path.join(OUTPUT_DIR, hex_digest)

    # Avoid re-writing if the content is already there
    if not os.path.exists(output_filepath):
        with open(output_filepath, 'w') as f:
            f.write(output_str)

    return hex_digest

def main():
    if len(sys.argv) < 2:
        print("Usage: python execute_tool.py '<command>'", file=sys.stderr)
        sys.exit(1)

    command_to_run = sys.argv[1]

    ensure_output_dir()

    # Load existing history
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f:
            try:
                history = json.load(f)
                if not isinstance(history, list):
                    history = []
            except (json.JSONDecodeError, FileNotFoundError):
                history = []
    else:
        history = []

    start_time = datetime.now().isoformat()

    # Execute the command
    try:
        result = subprocess.run(
            command_to_run,
            shell=True,
            capture_output=True,
            text=True,
            executable='/bin/bash'
        )
        stdout = result.stdout
        stderr = result.stderr
        exit_code = result.returncode
    except Exception as e:
        stdout = ""
        stderr = f"CRITICAL_EXECUTION_ERROR: The command failed to launch: {e}"
        exit_code = -1

    end_time = datetime.now().isoformat()

    # Hash and save outputs
    stdout_hash = hash_and_save_output(stdout)
    stderr_hash = hash_and_save_output(stderr)

    # Create log entry with hashes
    log_entry = {
        "timestamp_start": start_time,
        "timestamp_end": end_time,
        "command": command_to_run,
        "stdout_hash": stdout_hash,
        "stderr_hash": stderr_hash,
        "exit_code": exit_code
    }

    history.append(log_entry)

    # Manage log rotation and garbage collection
    history = manage_log_rotation_and_gc(history)

    # Write the updated history back to the log file
    try:
        with open(LOG_FILE, 'w') as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        print(f"CRITICAL_LOGGING_ERROR: Failed to write to {LOG_FILE}: {e}", file=sys.stderr)

    # Mirror the output to the console for the agent
    if stdout:
        sys.stdout.write(stdout)
        sys.stdout.flush()
    if stderr:
        sys.stderr.write(stderr)
        sys.stderr.flush()

    sys.exit(exit_code)

if __name__ == "__main__":
    main()
