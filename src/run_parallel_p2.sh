#!/bin/bash

echo "Starting all runs in parallel for Prompt 2 (p2)"

# Assignment 1
bash run_pipeline.sh chatgpt critical_thinking a1 p2 &
bash run_pipeline.sh gemini critical_thinking a1 p2 &
bash run_pipeline.sh grok critical_thinking a1 p2 &
bash run_pipeline.sh claude critical_thinking a1 p2 &

# Assignment 2
bash run_pipeline.sh chatgpt critical_thinking a2 p2 &
bash run_pipeline.sh gemini critical_thinking a2 p2 &
bash run_pipeline.sh grok critical_thinking a2 p2 &
bash run_pipeline.sh claude critical_thinking a2 p2 &

# Assignment 3
bash run_pipeline.sh chatgpt critical_thinking a3 p2 &
bash run_pipeline.sh gemini critical_thinking a3 p2 &
bash run_pipeline.sh grok critical_thinking a3 p2 &
bash run_pipeline.sh claude critical_thinking a3 p2 &

# Wait for all background jobs to finish
wait

echo "All p2 runs completed!"
