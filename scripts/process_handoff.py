import sys
import re
import json
from datetime import datetime
import os

# --- Path Setup ---
# The project root is the current working directory.
# This makes the script location-independent and testable.
PROJECT_ROOT = os.getcwd()

# Define full paths for all context and log files
CONTEXT_DIR = os.path.join(PROJECT_ROOT, 'context')
ANALOGIES_DIR = os.path.join(PROJECT_ROOT, 'analogies')

DECISIONS_LOG = os.path.join(CONTEXT_DIR, 'decisions.log')
LESSONS_LOG = os.path.join(CONTEXT_DIR, 'lessons.log')
ROADMAP_FILE = os.path.join(CONTEXT_DIR, 'roadmap.md')
HISTORY_LOG = os.path.join(CONTEXT_DIR, 'history.log')
ANALOGY_REGISTRY = os.path.join(ANALOGIES_DIR, 'registry.json')

# --- Helper Functions ---

def parse_section(content, section_name):
    """Extracts content from a specific H2 section of the handoff file."""
    pattern = re.compile(rf'## \d+\. {section_name}\n(.*?)(?=\n## \d+\.|\Z)', re.DOTALL)
    match = pattern.search(content)
    return match.group(1).strip() if match else ""

def process_decisions(section_content, timestamp):
    """Parses decisions and appends them to the log, avoiding duplicates."""
    decisions_to_add = re.findall(r'-\s*DECISION:\s*(.*)', section_content)
    if not decisions_to_add:
        return 0

    try:
        with open(DECISIONS_LOG, 'r') as f:
            # Extract the decision text from each line to check for content uniqueness
            existing_decisions = {line.split(' - ', 1)[1].strip() for line in f if ' - ' in line}
    except FileNotFoundError:
        existing_decisions = set()

    added_count = 0
    with open(DECISIONS_LOG, 'a') as f:
        for decision_text in decisions_to_add:
            stripped_decision = decision_text.strip()
            if stripped_decision not in existing_decisions:
                f.write(f"{timestamp} - {stripped_decision}\n")
                added_count += 1
    return added_count

def process_lessons(section_content, timestamp):
    """Parses lessons and appends them to the log, avoiding duplicates."""
    lessons_to_add = re.findall(r'-\s*LESSON:\s*(.*)', section_content)
    if not lessons_to_add:
        return 0

    try:
        with open(LESSONS_LOG, 'r') as f:
            # Extract the lesson text from each line to check for content uniqueness
            existing_lessons = {line.split(' - ', 1)[1].strip() for line in f if ' - ' in line}
    except FileNotFoundError:
        existing_lessons = set()

    added_count = 0
    with open(LESSONS_LOG, 'a') as f:
        for lesson_text in lessons_to_add:
            stripped_lesson = lesson_text.strip()
            if stripped_lesson not in existing_lessons:
                f.write(f"{timestamp} - {stripped_lesson}\n")
                added_count += 1
    return added_count

def process_roadmap(section_content):
    """Parses roadmap updates and appends them to the roadmap file, avoiding duplicates."""
    updates_to_add = re.findall(r'-\s*ROADMAP:\s*(.*)', section_content)
    if not updates_to_add:
        return 0

    try:
        with open(ROADMAP_FILE, 'r') as f:
            existing_lines = {line.strip() for line in f}
    except FileNotFoundError:
        existing_lines = set()

    added_count = 0
    with open(ROADMAP_FILE, 'a') as f:
        for update_text in updates_to_add:
            line_to_add = f"- {update_text.strip()}"
            if line_to_add not in existing_lines:
                f.write(f"{line_to_add}\n")
                added_count += 1
    return added_count

def process_analogies(section_content):
    """
    Parses new analogies and updates the JSON registry.
    This function is idempotent by nature. If an analogy with the same name
    exists, its entry will be overwritten with the new data, which is the
    desired behavior.
    """
    analogy_blocks = re.findall(r'-\s*ANALOGY:\s*(\w+)\s*\n\s*-\s*RATIONALE:\s*(.*?)\n\s*-\s*TRIGGER:\s*(.*)', section_content)
    if not analogy_blocks:
        return 0

    try:
        with open(ANALOGY_REGISTRY, 'r') as f:
            # Handle case where file might be empty but exists
            file_content = f.read()
            if not file_content:
                registry = {}
            else:
                registry = json.loads(file_content)
    except (FileNotFoundError, json.JSONDecodeError):
        registry = {}

    for name, rationale, trigger in analogy_blocks:
        registry[name] = {
            'rationale': rationale.strip(),
            'trigger': trigger.strip()
        }

    with open(ANALOGY_REGISTRY, 'w') as f:
        json.dump(registry, f, indent=2)

    return len(analogy_blocks)

def main(handoff_file_rel_path):
    """Main function to process the handoff file."""
    handoff_file_abs_path = os.path.join(PROJECT_ROOT, handoff_file_rel_path)
    print(f"Processing handoff file: {handoff_file_abs_path}")

    try:
        with open(handoff_file_abs_path, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: Handoff file not found at '{handoff_file_abs_path}'")
        sys.exit(1)

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Extract sections from the handoff file
    decisions_section = parse_section(content, "Key Decisions")
    lessons_section = parse_section(content, "Lessons Learned")
    analogies_section = parse_section(content, "New Analogies")
    roadmap_section = parse_section(content, "Roadmap Updates")

    # Process each section and update the corresponding logs/registries
    decisions_count = process_decisions(decisions_section, timestamp)
    lessons_count = process_lessons(lessons_section, timestamp)
    analogies_count = process_analogies(analogies_section)
    roadmap_count = process_roadmap(roadmap_section)

    print(f"  - Processed {decisions_count} decisions.")
    print(f"  - Processed {lessons_count} lessons.")
    print(f"  - Processed {analogies_count} analogies.")
    print(f"  - Processed {roadmap_count} roadmap updates.")

    # Log the execution to the history log
    with open(HISTORY_LOG, 'a') as f:
        f.write(f"{timestamp} - Successfully processed handoff '{handoff_file_rel_path}'.\n")

    print("Handoff processing complete. Logs and registries updated.")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python scripts/process_handoff.py <path_to_handoff_file.md>")
        sys.exit(1)
    main(sys.argv[1])
