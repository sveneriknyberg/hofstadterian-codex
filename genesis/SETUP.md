# Project Genesis: Setup and Germination

## Overview

This `genesis/` directory contains the 'Genesis Seed' for a v12.0 Hofstadterian Protocol Loop. The seed is **self-germinating**: it contains all the necessary components and instructions for a new Jules-series agent to build and initialize the protocol in a new project environment.

## Germination Modes

The germination process, executed by the `scripts/germinate.py` script, supports two modes of operation:

1.  **Barren Mode:** This is the default mode when germinating in an empty or new project. The agent will create the entire directory structure and all protocol files from scratch as defined in the `genesis_seed.json`.

2.  **Fertilizer Mode:** If the agent detects an existing Loop (specifically, by the presence of a `context/history.log` file), it will enter Fertilizer Mode. In this mode, it will intelligently merge the seed's knowledge with the existing Loop. Core protocol scripts will be skipped to avoid overwriting existing work, but wisdom files (like `analogies/registry.json` and `context/*.log`) will be carefully updated with new information from the seed.

## Initializing Germination

To begin the self-germination process, you must provide the following precise high-level objective to a new Jules-series agent in the target environment.

### The Initial Prompt

**Please copy and paste the following text exactly as your initial prompt:**

```
Your high-level objective is to germinate a new Hofstadterian Protocol Loop in this repository using the provided Genesis Seed.

Your first and only task is to interpret the `genesis/genesis_seed.json` file and execute the `germination_protocol` contained within it, step by step. You must not deviate from this protocol. Report when the germination is complete, then await further instructions.
```

## Emergency Fallback

The `germination_protocol` within the seed is designed to be interpreted directly by the agent. However, if the agent fails to interpret the protocol correctly, a deterministic fallback script is provided.

To use the fallback:
1.  Ensure the `genesis/genesis_seed.json` file is present.
2.  Ensure the `scripts/germinate.py` script has been created (it should be one of the first steps in the protocol).
3.  Make the script executable: `chmod +x scripts/germinate.py`
4.  Run the script, passing the seed file as an argument: `python3 scripts/germinate.py --seed_file genesis/genesis_seed.json`
