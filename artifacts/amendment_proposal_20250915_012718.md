# Codex Amendment Proposal - 20250915_012718

Requires review and approval from the Gardener.

## 1. Proposed Change (Diff)

```diff
- When you have achieved the user's high-level objective, you **MUST** perform the following two steps in order:
+ After completing a task or a set of tasks, you should remain active and await further directives from the user. Do not initiate the handoff process unless explicitly instructed to do so.
+
+ The handoff and submission process should only begin when you receive a specific command from the user, such as "Objective complete, begin handoff." At that point, you **MUST** perform the following two steps in order:
```

## 2. Rationale

The current protocol mandates the end of a session after achieving a single high-level objective. This is inefficient, as it requires a full session teardown and bootstrap for each new task. This amendment changes the protocol to allow for multi-task sessions, where the agent remains active and awaits new directives after completing a task. This will improve efficiency, reduce overhead, and allow for better context retention between related tasks.

## 3. Impact Analysis

This is a low-risk, high-reward change to the core protocol. It makes the agent's session management more flexible and user-driven. By requiring an explicit command to begin the handoff process, it prevents premature session endings and gives the user more control over the workflow. There are no anticipated negative side-effects. This change will make the agent more useful for complex, multi-step projects.
