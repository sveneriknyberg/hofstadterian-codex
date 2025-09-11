import os
import sys
import subprocess
from datetime import datetime

# --- ANSI Color Codes ---
CYAN = '\033[0;36m'
YELLOW = '\033[1;33m'
GREEN = '\033[0;32m'
NC = '\033[0m'

def get_multiline_input(prompt):
    """Gets multiline input from the user."""
    print(f"{YELLOW}{prompt} (type 'END' on a new line when finished):{NC}")
    lines = []
    while True:
        try:
            line = input()
            if line == "END":
                break
            lines.append(line)
        except EOFError:
            break
    return "\n".join(lines)

def get_git_status():
    """Gets the list of modified files from git status."""
    try:
        result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "Could not retrieve git status."

def main():
    """Main function to create and process a handoff file."""
    print(f"{CYAN}--- Starting Interactive Handoff Creation ---{NC}")

    # --- Gather Handoff Content ---
    summary = get_multiline_input("1. Summary of Work")
    decisions = get_multiline_input("2. Key Decisions (prefix each with '- DECISION:')")
    lessons = get_multiline_input("3. Lessons Learned (prefix each with '- LESSON:')")
    analogies = get_multiline_input("4. New Analogies (use ANALOGY/RATIONALE/TRIGGER format)")
    roadmap = get_multiline_input("5. Roadmap Updates (prefix each with '- ROADMAP:')")

    # --- Pre-populate with Git Status ---
    git_modifications = get_git_status()
    unresolved = get_multiline_input(f"6. Unresolved Issues & Next Steps\n\nGit Status:\n---\n{git_modifications}\n---\n")

    # --- Assemble Handoff File ---
    timestamp_str = datetime.now().strftime('%Y%m%d%H%M%S')
    filename = f"{timestamp_str}.md"

    handoff_content = f"""\
# Handoff: {timestamp_str}

## 1. Summary of Work
{summary}

## 2. Key Decisions
{decisions}

## 3. Lessons Learned
{lessons}

## 4. New Analogies
{analogies}

## 5. Roadmap Updates
{roadmap}

## 6. Unresolved Issues & Next Steps
{unresolved}
"""

    # --- Write Handoff File ---
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    handoffs_dir = os.path.join(project_root, 'handoffs')
    os.makedirs(handoffs_dir, exist_ok=True)
    handoff_filepath = os.path.join(handoffs_dir, filename)

    try:
        with open(handoff_filepath, 'w') as f:
            f.write(handoff_content)
        print(f"\n{GREEN}Successfully created handoff file: {handoff_filepath}{NC}")
    except IOError as e:
        print(f"Error: Could not write handoff file: {e}")
        sys.exit(1)

    # --- Automatically Process the New Handoff ---
    print(f"\n{CYAN}--- Automatically processing the new handoff file... ---{NC}")
    process_script_path = os.path.join(script_dir, 'process_handoff.py')
    try:
        # We pass the relative path to the process script
        relative_handoff_path = os.path.join('handoffs', filename)
        result = subprocess.run(
            ['python3', process_script_path, relative_handoff_path],
            capture_output=True, text=True, check=True
        )
        print(result.stdout)
        if result.stderr:
            print(f"{YELLOW}Processing warnings/errors:{NC}\n{result.stderr}")
        print(f"{GREEN}Handoff processed successfully.{NC}")
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to process handoff file.")
        print(e.stdout)
        print(e.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
