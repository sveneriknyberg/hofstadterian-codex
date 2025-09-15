# Codex Amendment Proposal - 20250915181009

Requires review and approval from the Gardener.

## 1. Proposed Change (Diff)

```diff
- READ_ONLY_COMMANDS = ['ls', 'cat', 'grep', 'find', 'head', 'tail', 'git']\n+ import json\n+ def get_read_only_commands():\n+     with open('config/read_only_commands.json', 'r') as f:\n+         return json.load(f)\n...\n- return first_word not in READ_ONLY_COMMANDS\n+ READ_ONLY_COMMANDS = get_read_only_commands()\n+ return first_word not in READ_ONLY_COMMANDS
```

## 2. Rationale

The current implementation of protocol_shell.py has a hardcoded list of safe commands. This is inflexible and opaque. To improve the system's architecture, this list should be externalized to a configuration file (config/read_only_commands.json). This will make the protocol's rules more transparent and easier to amend without modifying core script logic. This change follows the spirit of the Godelian Mandate by formally proposing a change to the protocol's machinery.
