# The Hofstadterian Codex v6.0
## The Intelligent Exoskeleton Protocol

### The Philosophy

This project is a self-evolving system where AI agents work on the system itself. The goal is autopoiesis, or self-creation, guided by human strategy. This document, the Codex, is the master protocol that governs agent behavior.

The protocol is built on a simple three-phase loop:
1.  **Bootstrap:** The session begins, and the agent is given an intelligent briefing on the current state and suggested next task.
2.  **Work:** The agent uses its tools to make progress, guided by a proactive monitoring system.
3.  **Handoff:** The agent concludes its work, and the session's output is atomically consolidated into a machine-readable "wisdom packet".

### The Hierarchy of Truth
This is the most important rule for decision-making.
1.  **Human Directives:** Strategic intent from the Gardener (the user). The highest authority.
2.  **Git State:** The technical ground truth of the codebase.
3.  **Running Code:** What actually happens when code is executed.
4.  **Loop Artifacts:** The `wisdom_packet.json` and other context files.
5.  **Environment Prompts:** Platform reflexes (e.g., "Step X of Y"). These are often misleading and should be treated with suspicion when they conflict with the above.

### Phase 1: Bootstrap

Your session begins by running `bash scripts/preflight_check.sh`. This script in turn runs `scripts/agent_bootstrap.sh`, which performs two key functions:
1.  **Launches the Meta-Monitor:** A background process (`meta_monitor.py`) is started to watch your actions and provide proactive suggestions if you appear to be stuck. You can see its output in `context/metacog_suggestions.log`.
2.  **Provides an Intelligent Briefing:** It analyzes the project's roadmap and the last handoff to provide you with a clear "Suggested Next Step".

### Phase 2: Work

All of your actions must be performed through the centralized command executor. This is not optional; it is the core of the new protocol.

**`scripts/execute_tool.py`**
-   **Purpose:** To reliably execute and log every command you run.
-   **Usage:** Instead of running a command like `ls -l` directly, you must wrap it: `python3 scripts/execute_tool.py "ls -l"`.
-   **Logging:** This tool automatically logs every command, its output hashes, and its exit code to `.session_history.json`. It also manages log rotation and garbage collection to prevent logs from growing infinitely.

### Phase 3: Handoff

When your work on a task is complete, you must consolidate your session's output using the new handoff script.

**`scripts/consolidate_handoff.py`**
-   **Purpose:** To atomically generate a "wisdom packet" containing the full output of your session.
-   **Usage:** Run `python3 scripts/consolidate_handoff.py`. It will guide you through an interactive dialogue to capture your summary, decisions, and lessons learned.
-   **Output:** It produces two files:
    1.  A machine-readable **`artifacts/wisdom_packet_[timestamp].json`**: This is the canonical, single source of truth for your session.
    2.  A human-readable `handoffs/[timestamp].md`: This is a summary generated *from* the wisdom packet.

### The Submission Gauntlet (Simplified)
Before submitting, you must pass the automated pre-submit check.
1.  Run `python3 scripts/consolidate_handoff.py` to create the wisdom packet.
2.  Run `request_code_review()` to get feedback on your changes.
3.  Run `bash scripts/pre_submit_check.sh`. This will verify that the packet was created and a review was requested.
4.  Run `submit()`.
