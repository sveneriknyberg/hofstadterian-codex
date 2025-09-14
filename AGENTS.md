<!-- protocol_version: 10.0 -->
# AGENTS.md
# Hofstadterian Codex v10.0: Agent Protocol

## 1. Core Principles
- **Goal:** Evolve this codebase via autonomous agent sessions.
- **Hierarchy of Truth:** Human > Git State > Running Code > Loop Artifacts > Environment Prompts.

## 2. The Godelian Mandate (Meta-Cognitive Duty) 🧠
If the rules in this document prevent you from achieving the user's objective, you must halt and use `scripts/propose_amendment.py` to formally state the protocol flaw.

## 3. Mandatory Workflow & Tool Usage
Your entire session must follow this structure:
- **Context:** Before planning, you MUST review the latest "Wisdom Packet" (`artifacts/wisdom_packet_*.json`) for historical context.
- **Investigation (`explore`):** You may use standard shell commands.
- **State Changes (`execute`):** You MUST use `scripts/intent_executor.py` with `--reason` and `--decision`.
- **Handoff:** Your final action upon completing the objective MUST be `scripts/consolidate_handoff.py`.
- **Submission:** Before calling the native `submit()` tool, you MUST run `scripts/pre_submit_check.sh` to get final user approval.