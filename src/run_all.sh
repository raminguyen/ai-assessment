#!/bin/bash

echo "Starting all runs in parallel"

# Assignment 1
bash run_pipeline.sh chatgpt critical_thinking 1 &
bash run_pipeline.sh gemini critical_thinking 1 &
bash run_pipeline.sh grok critical_thinking 1 &
bash run_pipeline.sh claude critical_thinking 1 &

# Assignment 2
bash run_pipeline.sh chatgpt critical_thinking 2 &
bash run_pipeline.sh gemini critical_thinking 2 &
bash run_pipeline.sh grok critical_thinking 2 &
bash run_pipeline.sh claude critical_thinking 2 &

# Assignment 3
bash run_pipeline.sh chatgpt critical_thinking 3 &
bash run_pipeline.sh gemini critical_thinking 3 &
bash run_pipeline.sh grok critical_thinking 3 &
bash run_pipeline.sh claude critical_thinking 3 &

# Wait for all background jobs to finish
wait

echo "All done!"
