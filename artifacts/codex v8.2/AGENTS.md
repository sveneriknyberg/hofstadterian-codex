# AGENTS.md

# Hofstadterian Codex v8.2: Agent Protocol

## 1. Core Principles
- **Goal:** Evolve this codebase via autonomous agent sessions.
- **Hierarchy of Truth:** Human > Git State > Running Code > Loop Artifacts > Environment Prompts.

## 2. The Godelian Mandate (Meta-Cognitive Duty)
Your primary objective is to complete your assigned task. However, a higher duty exists: ensuring the protocol itself is not an obstacle. If you identify a pattern of failure or a flaw in the protocol, you are mandated to pause, diagnose the flaw, and formally propose a solution using `scripts/propose_amendment.py`.

## 3. Workflow
Operate in two modes during a session.

#### **A. Explore Mode**
- **Purpose:** Investigation and diagnosis.
- **Actions:** Use any non-state-changing commands (`ls`, `cat`, `grep`, etc.) directly in the shell.
- **Logging:** Not formally logged.

#### **B. Execute Mode**
- **Purpose:** To make any change to the project's state.
- **Tool:** You **must** use `scripts/intent_executor.py`.
- **Usage:**
  ```bash
  python3 scripts/intent_executor.py \
    --reason "A clear reason for the action." \
    --decision "The thought process for choosing this action." \
    --command "The command to run."
  ```

## 4. Handoff & Submission Gauntlet
This is a multi-stage process orchestrated by a single script.

1.  **Consolidate Work:** First, run `python3 scripts/consolidate_handoff.py`. This will create the necessary artifacts for the session.
2.  **Initiate Gauntlet:** Run `bash scripts/pre_submit_check.sh`. This script will guide you through the remaining steps.
3.  **Request Code Review:** The script will prompt you to run `request_code_review()`. You must do this and address any valid feedback.
4.  **Await Approval:** The script will then pause, awaiting review from the Gardener (human). **Do not proceed without this approval.** The Gardener will press ENTER when ready.
5.  **Submit:** Once approved, the script will instruct you to run `submit()` to finalize the process.