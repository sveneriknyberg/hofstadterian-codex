import os
import sys

# --- ANSI Color Codes ---
CYAN = '\033[0;36m'
YELLOW = '\033[1;33m'
GREEN = '\033[0;32m'
RED = '\033[0;31m'
NC = '\033[0m' # No Color

def print_status(message, status):
    """Prints a status message with a colored [PASS] or [FAIL] tag."""
    if status:
        print(f"  {GREEN}[PASS]{NC} {message}")
    else:
        print(f"  {RED}[FAIL]{NC} {message}")

def main():
    """Runs a series of checks to validate the Loop's context."""
    print(f"\n{YELLOW}V. LOOP HEALTH CHECK (from validate_context.py):{NC}")

    all_checks_passed = True

    # --- Path Setup ---
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)

    context_dir = os.path.join(project_root, 'context')
    scripts_dir = os.path.join(project_root, 'scripts')
    handoffs_dir = os.path.join(project_root, 'handoffs')

    # --- 1. Check for essential files and directories ---
    print(f"{CYAN}[1/3] Checking for essential files and directories...{NC}")
    essential_files = [
        os.path.join(project_root, 'AGENTS.md'),
        os.path.join(context_dir, 'history.log'),
        os.path.join(context_dir, 'roadmap.md'),
        os.path.join(scripts_dir, 'agent_bootstrap.sh'),
        os.path.join(scripts_dir, 'meta_cognitive_check.py'),
        os.path.join(scripts_dir, 'pre_submit_check.sh'),
        os.path.join(scripts_dir, 'consolidate_handoff.py'),
    ]

    for fpath in essential_files:
        exists = os.path.exists(fpath)
        print_status(f"Found: {os.path.relpath(fpath, project_root)}", exists)
        if not exists:
            all_checks_passed = False

    # --- 2. Check script executability ---
    print(f"{CYAN}[2/3] Checking script executability...{NC}")
    executable_scripts = [
        os.path.join(scripts_dir, 'agent_bootstrap.sh'),
        os.path.join(scripts_dir, 'pre_submit_check.sh'),
    ]
    for fpath in executable_scripts:
        is_executable = os.access(fpath, os.X_OK)
        print_status(f"Executable: {os.path.relpath(fpath, project_root)}", is_executable)
        if not is_executable:
            print(f"    -> Tip: Run 'chmod +x {os.path.relpath(fpath, project_root)}'")
            all_checks_passed = False

    # --- 3. Check for unprocessed handoff files ---
    print(f"{CYAN}[3/3] Checking for unprocessed handoff files...{NC}")
    try:
        handoff_files = [f for f in os.listdir(handoffs_dir) if f.endswith('.md')]
        if not handoff_files:
            print_status("No handoffs found, skipping check.", True)
        else:
            history_log_path = os.path.join(context_dir, 'history.log')
            with open(history_log_path, 'r') as f:
                history_content = f.read()

            unprocessed_handoffs = []
            for handoff_filename in handoff_files:
                if handoff_filename not in history_content:
                    unprocessed_handoffs.append(handoff_filename)

            if not unprocessed_handoffs:
                print_status("All handoff files have been processed.", True)
            else:
                print_status(f"Found {len(unprocessed_handoffs)} unprocessed handoff file(s).", False)
                for fname in unprocessed_handoffs:
                    print(f"    - {fname}")
                print(f"    -> Tip: Run 'python3 scripts/consolidate_handoff.py' to process handoffs.")
                all_checks_passed = False

    except FileNotFoundError:
        print_status("Handoffs directory or history.log not found, cannot check consistency.", False)
        all_checks_passed = False

    if not all_checks_passed:
        print(f"\n{RED}Loop health check failed. Please address the issues above.{NC}")
        # sys.exit(1) # We can decide later if we want to exit with an error
    else:
        print(f"\n{GREEN}Loop health check passed.{NC}")

if __name__ == '__main__':
    main()
