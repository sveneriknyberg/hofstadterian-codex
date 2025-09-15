# scripts/bootstrap_session.py (Corrected)
import os
import json
import sys
import subprocess

SENTINEL_FILE = ".preflight_failed"

def find_latest_wisdom_packet():
    artifacts_dir = 'artifacts'
    if not os.path.exists(artifacts_dir): return None
    packets = [f for f in os.listdir(artifacts_dir) if f.startswith('wisdom_packet_')]
    if not packets: return None
    return max(packets, key=lambda f: os.path.getmtime(os.path.join(artifacts_dir, f)))

def main():
    preflight_result = subprocess.run(
        "bash preflight_check.sh", shell=True,
        capture_output=True, text=True
    )
    print(preflight_result.stdout)
    print(preflight_result.stderr, file=sys.stderr)

    if os.path.exists(SENTINEL_FILE):
        failure_briefing = {
            "status": "SESSION_FAILED_TO_START",
            "message": "The pre-flight check failed. Environment is not safe."
        }
        print(json.dumps(failure_briefing, indent=2))
        os.remove(SENTINEL_FILE)
        sys.exit(1)

    latest_packet = find_latest_wisdom_packet()
    context_message = f"Latest context found in: {latest_packet}" if latest_packet else "No prior context found."

    briefing = {
        "status": "SESSION_STARTED",
        "message": "Hofstadterian Protocol v12.0 session is active.",
        "context": context_message,
        "next_step": {
            "status": "HUMAN_INPUT_REQUIRED",
            "prompt": "Please state your high-level objective."
        }
    }
    print(json.dumps(briefing, indent=2))

if __name__ == "__main__":
    main()
