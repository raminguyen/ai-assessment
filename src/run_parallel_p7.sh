#!/bin/bash

echo "Starting all generation runs in parallel for Prompt 7 (p7 - iterative)"

# Assignment 1
python main.py generate chatgpt 1 --folder critical_thinking --prompt 7 &
python main.py generate gemini 1 --folder critical_thinking --prompt 7 &
python main.py generate claude 1 --folder critical_thinking --prompt 7 &
python main.py generate grok 1 --folder critical_thinking --prompt 7 &

# Assignment 2
python main.py generate chatgpt 2 --folder critical_thinking --prompt 7 &
python main.py generate gemini 2 --folder critical_thinking --prompt 7 &
python main.py generate claude 2 --folder critical_thinking --prompt 7 &
python main.py generate grok 2 --folder critical_thinking --prompt 7 &

# Assignment 3
python main.py generate chatgpt 3 --folder critical_thinking --prompt 7 &
python main.py generate gemini 3 --folder critical_thinking --prompt 7 &
python main.py generate claude 3 --folder critical_thinking --prompt 7 &
python main.py generate grok 3 --folder critical_thinking --prompt 7 &

# Wait for all background jobs to finish
wait

echo "All p7 generation runs completed!"
