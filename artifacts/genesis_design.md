# Genesis Seed Design (v1.0)

This document outlines the design for the `genesis_seed.json` file and the `germination_protocol` it contains. The goal is to create a single, portable file that acts as a self-contained "genome" for a Strange Loop, allowing for both deterministic and agent-interpreted germination.

---

## 1. `genesis_seed.json` Top-Level Structure

The seed will be a JSON object with three top-level keys:

1.  `metadata`: Contains information about the seed itself.
2.  `germination_protocol`: An ordered list of high-level instructions for an agent to follow to construct the Loop.
3.  `file_content_map`: A key-value store where keys are the relative file paths and values are the file contents as base64 encoded strings to ensure integrity of multi-line scripts and special characters.

### Example:
```json
{
  "metadata": {
    "seed_format_version": "1.0",
    "timestamp": "2025-09-12T10:30:00Z",
    "source_loop_id": "oracle-loop-v1"
  },
  "germination_protocol": [
    // ... see section 2 ...
  ],
  "file_content_map": {
    "AGENTS.md": "VGhlIEhvZnN0YWR0ZXJpYW4gQ29kZXggdjUuMg...",
    "scripts/agent_bootstrap.sh": "IyEvYmluL2Jhc2gK...",
    // ... all other files, base64 encoded ...
  }
}
```

---

## 2. `germination_protocol` Specification

The protocol is a list of JSON objects, each representing a single action for the germination agent to take. It is designed to be human-readable and interpretable by an LLM agent.

### Protocol Actions

| Action                 | Parameters        | Description                                                                                                                                                                                          |
| ---------------------- | ----------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `log_message`          | `message: string` | Displays a message to the user/log. Useful for tracking progress.                                                                                                                                    |
| `create_directory`     | `path: string`    | Creates a directory at the specified relative path.                                                                                                                                                  |
| `create_file`          | `path: string`    | Creates a file at the specified path. The content for the file must be looked up from the `file_content_map` using the `path` as the key. The content is base64 decoded before writing.               |
| `make_executable`      | `path: string`    | Makes the file at the specified path executable. Essential for shell scripts.                                                                                                                        |
| `emergency_fallback`   | `instruction: string` | The final step. Provides explicit instructions for a fallback germination method (`germinate.py`) if the agent fails to follow the protocol. This is the "emergency hatch."                        |

### Example Protocol:
```json
"germination_protocol": [
  {
    "action": "log_message",
    "message": "Starting Loop Germination Protocol v1.0..."
  },
  {
    "action": "create_directory",
    "path": "scripts/"
  },
  {
    "action": "create_directory",
    "path": "context/"
  },
  {
    "action": "create_file",
    "path": "AGENTS.md"
  },
  {
    "action": "create_file",
    "path": "scripts/agent_bootstrap.sh"
  },
  {
    "action": "make_executable",
    "path": "scripts/agent_bootstrap.sh"
  },
  // ... many more create_file actions ...
  {
    "action": "log_message",
    "message": "Germination complete. To initialize the new Loop, run: bash scripts/agent_bootstrap.sh"
  },
  {
    "action": "emergency_fallback",
    "instruction": "Protocol interpretation failed. To germinate, create 'scripts/germinate.py' from the file_content_map, make it executable, and run: python3 scripts/germinate.py --seed_file genesis_seed.json"
  }
]
```

---

## 3. `germinate.py` Reference Implementation

The `scripts/germinate.py` script will be created as the official, deterministic reference implementation of this protocol. It will:
1.  Accept a `--seed_file` argument.
2.  Load and parse the `genesis_seed.json`.
3.  Iterate through the `germination_protocol` step-by-step.
4.  Execute each action exactly as specified.
5.  Base64 decode all file content from the `file_content_map` before writing to disk.
6.  Set file permissions for executables.

This provides a reliable path to germination and serves as a clear example for any agent attempting to interpret the protocol.
