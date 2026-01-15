#!/bin/bash

echo "Starting all runs in parallel for Prompt 2 (p2)"

# Assignment 1
python main.py generate chatgpt 1 --folder critical_thinking --prompt 2 &
python main.py generate gemini 1 --folder critical_thinking --prompt 2 &
python main.py generate grok 1 --folder critical_thinking --prompt 2 &
python main.py generate claude 1 --folder critical_thinking --prompt 2 &

python main.py tune chatgpt 1 critical_thinking --prompt 2 &
python main.py tune gemini 1 critical_thinking --prompt 2 &
python main.py tune grok 1 critical_thinking --prompt 2 &
python main.py tune claude 1 critical_thinking --prompt 2 &

python main.py reflection chatgpt 1 critical_thinking --prompt 2 &
python main.py reflection gemini 1 critical_thinking --prompt 2 &
python main.py reflection grok 1 critical_thinking --prompt 2 &
python main.py reflection claude 1 critical_thinking --prompt 2 &

# Assignment 2
python main.py generate chatgpt 2 --folder critical_thinking --prompt 2 &
python main.py generate gemini 2 --folder critical_thinking --prompt 2 &
python main.py generate grok 2 --folder critical_thinking --prompt 2 &
python main.py generate claude 2 --folder critical_thinking --prompt 2 &

python main.py tune chatgpt 2 critical_thinking --prompt 2 &
python main.py tune gemini 2 critical_thinking --prompt 2 &
python main.py tune grok 2 critical_thinking --prompt 2 &
python main.py tune claude 2 critical_thinking --prompt 2 &

python main.py reflection chatgpt 2 critical_thinking --prompt 2 &
python main.py reflection gemini 2 critical_thinking --prompt 2 &
python main.py reflection grok 2 critical_thinking --prompt 2 &
python main.py reflection claude 2 critical_thinking --prompt 2 &

# Assignment 3
python main.py generate chatgpt 3 --folder critical_thinking --prompt 2 &
python main.py generate gemini 3 --folder critical_thinking --prompt 2 &
python main.py generate grok 3 --folder critical_thinking --prompt 2 &
python main.py generate claude 3 --folder critical_thinking --prompt 2 &

python main.py tune chatgpt 3 critical_thinking --prompt 2 &
python main.py tune gemini 3 critical_thinking --prompt 2 &
python main.py tune grok 3 critical_thinking --prompt 2 &
python main.py tune claude 3 critical_thinking --prompt 2 &

python main.py reflection chatgpt 3 critical_thinking --prompt 2 &
python main.py reflection gemini 3 critical_thinking --prompt 2 &
python main.py reflection grok 3 critical_thinking --prompt 2 &
python main.py reflection claude 3 critical_thinking --prompt 2 &

# Wait for all background jobs to finish
wait

echo "All p2 runs completed!"
