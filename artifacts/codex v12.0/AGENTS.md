# AGENTS.md
# Hofstadterian Codex v12.0: Agent Protocol

Your work is governed by two sets of rules: how you execute individual commands, and the sequence you must follow to end a session.

## 1. The Mandatory Shell (How to Act)

For **ALL** commands you wish to execute, you **MUST** use the `scripts/protocol_shell.py` tool. Pass your desired command to this script.

The shell will automatically enforce the protocol. It will execute safe, read-only commands directly. It will **REJECT** any state-changing command and instruct you to use `scripts/intent_executor.py` instead. Direct shell access is forbidden.

## 2. The Session Lifecycle (How to Finish)

When you have achieved the user's high-level objective, you **MUST** perform the following two steps in order:

1.  **Handoff:** Your final `execute` action must be to run `scripts/consolidate_handoff.py`. This will create the Wisdom Packet and document your work for the next session.
2.  **Submission:** After the handoff is successful, you must run `bash scripts/pre_submit_check.sh`. This will initiate the final code review and wait for the Gardener's explicit approval before you are cleared to use the platform's native `submit()` tool.