#!/bin/bash
# export PYTHONPATH="/workspaces/GenAI" # Or the parent directory of L4_RAG
# # ... rest of your worker startup command
export $(grep -v '^#' .env | xargs -d '\n') 
rq worker --with-scheduler