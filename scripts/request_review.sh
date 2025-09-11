#!/bin/bash
# This script acts as a formal first step for requesting a code review.
# It creates a token file that the pre-submit check can verify.

echo "Creating .review_requested token file..."
touch .review_requested
echo "Token file created."
echo "Please now run the 'request_code_review' tool to get feedback on your changes."
