import sys
import json
import os

LOG_FILE = ".session_history.json"

def main():
    """
    Safely appends a JSON object to a JSON array in a file.
    Takes one argument: a string containing the JSON object to append.
    """
    if len(sys.argv) != 2:
        print("Usage: python append_to_log.py '<json_object_string>'", file=sys.stderr)
        sys.exit(1)

    new_entry_str = sys.argv[1]

    try:
        new_entry = json.loads(new_entry_str)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON object provided: {new_entry_str}", file=sys.stderr)
        sys.exit(1)

    log_data = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, 'r') as f:
                # Handle case where file is empty
                content = f.read()
                if content:
                    log_data = json.loads(content)
                    # Ensure it's a list
                    if not isinstance(log_data, list):
                        log_data = []
        except (json.JSONDecodeError, IOError):
            # If file is corrupted or unreadable, start fresh
            log_data = []

    log_data.append(new_entry)

    try:
        with open(LOG_FILE, 'w') as f:
            json.dump(log_data, f, indent=4)
    except IOError as e:
        print(f"Error writing to log file: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
