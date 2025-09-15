# start_session.sh

#!/bin/bash
# A zero-dependency script to initiate a session without triggering the agent's planning logic.

echo '{
  "status": "SESSION_STARTED_RAW",
  "message": "Protocol v10.0 session initiated. Ready for bootstrap command.",
  "next_step": {
    "status": "HUMAN_INPUT_REQUIRED",
    "prompt": "Please provide the command to run the full bootstrap and pre-flight check."
  }
}'