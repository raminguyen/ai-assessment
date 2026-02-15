#!/bin/bash

echo "Starting all generation runs in parallel for Prompt 6 (p6)"

# Assignment 1
python main.py generate chatgpt 1 --folder critical_thinking --prompt 6 &
python main.py generate gemini 1 --folder critical_thinking --prompt 6 &
python main.py generate claude 1 --folder critical_thinking --prompt 6 &
python main.py generate grok 1 --folder critical_thinking --prompt 6 &

# Assignment 2
python main.py generate chatgpt 2 --folder critical_thinking --prompt 6 &
python main.py generate gemini 2 --folder critical_thinking --prompt 6 &
python main.py generate claude 2 --folder critical_thinking --prompt 6 &
python main.py generate grok 2 --folder critical_thinking --prompt 6 &

# Assignment 3
python main.py generate chatgpt 3 --folder critical_thinking --prompt 6 &
python main.py generate gemini 3 --folder critical_thinking --prompt 6 &
python main.py generate claude 3 --folder critical_thinking --prompt 6 &
python main.py generate grok 3 --folder critical_thinking --prompt 6 &

# Wait for all background jobs to finish
wait

echo "All p6 generation runs completed!"
