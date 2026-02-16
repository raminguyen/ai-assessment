#!/bin/bash

echo "Starting all generation runs in parallel for Prompt 9 (p9 - iterative + generate knowledge)"

# Assignment 1
python main.py generate chatgpt 1 --folder critical_thinking --prompt 9 &
python main.py generate gemini 1 --folder critical_thinking --prompt 9 &
python main.py generate claude 1 --folder critical_thinking --prompt 9 &
python main.py generate grok 1 --folder critical_thinking --prompt 9 &

# Assignment 2
python main.py generate chatgpt 2 --folder critical_thinking --prompt 9 &
python main.py generate gemini 2 --folder critical_thinking --prompt 9 &
python main.py generate claude 2 --folder critical_thinking --prompt 9 &
python main.py generate grok 2 --folder critical_thinking --prompt 9 &

# Assignment 3
python main.py generate chatgpt 3 --folder critical_thinking --prompt 9 &
python main.py generate gemini 3 --folder critical_thinking --prompt 9 &
python main.py generate claude 3 --folder critical_thinking --prompt 9 &
python main.py generate grok 3 --folder critical_thinking --prompt 9 &

# Wait for all background jobs to finish
wait

echo "All p9 generation runs completed!"
