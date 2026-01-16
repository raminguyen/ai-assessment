#!/bin/bash

echo "Starting all runs in parallel for Prompt 1 (p1)"

# Assignment 1
bash run_pipeline.sh chatgpt critical_thinking a1 p1 &
#bash run_pipeline.sh gemini critical_thinking a1 p1 &
#bash run_pipeline.sh grok critical_thinking a1 p1 &
#bash run_pipeline.sh claude critical_thinking a1 p1 &

# Assignment 2
# bash run_pipeline.sh chatgpt critical_thinking a2 p1 &
# bash run_pipeline.sh gemini critical_thinking a2 p1 &
# bash run_pipeline.sh grok critical_thinking a2 p1 &
# bash run_pipeline.sh claude critical_thinking a2 p1 &

# Assignment 3
# bash run_pipeline.sh chatgpt critical_thinking a3 p1 &
# bash run_pipeline.sh gemini critical_thinking a3 p1 &
# bash run_pipeline.sh grok critical_thinking a3 p1 &
# bash run_pipeline.sh claude critical_thinking a3 p1 &

# Wait for all background jobs to finish
wait

echo "All p1 runs completed!"
