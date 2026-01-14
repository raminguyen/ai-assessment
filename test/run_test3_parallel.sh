#!/bin/bash
SCRIPT_PATH="../src/test_main.py"

echo "Starting test3 runs for all assignments in parallel"

# Assignment 1
python $SCRIPT_PATH a1 chatgpt test3 &
python $SCRIPT_PATH a1 grok test3 &
python $SCRIPT_PATH a1 claude test3 &
python $SCRIPT_PATH a1 gemini test3 &

python $SCRIPT_PATH a1 chatgpt test3 --tune &
python $SCRIPT_PATH a1 grok test3 --tune &
python $SCRIPT_PATH a1 claude test3 --tune &
python $SCRIPT_PATH a1 gemini test3 --tune &

# Assignment 2
python $SCRIPT_PATH a2 chatgpt test3 &
python $SCRIPT_PATH a2 grok test3 &
python $SCRIPT_PATH a2 claude test3 &
python $SCRIPT_PATH a2 gemini test3 &

python $SCRIPT_PATH a2 chatgpt test3 --tune &
python $SCRIPT_PATH a2 grok test3 --tune &
python $SCRIPT_PATH a2 claude test3 --tune &
python $SCRIPT_PATH a2 gemini test3 --tune &

# Assignment 3
python $SCRIPT_PATH a3 chatgpt test3 &
python $SCRIPT_PATH a3 grok test3 &
python $SCRIPT_PATH a3 claude test3 &
python $SCRIPT_PATH a3 gemini test3 &

python $SCRIPT_PATH a3 chatgpt test3 --tune &
python $SCRIPT_PATH a3 grok test3 --tune &
python $SCRIPT_PATH a3 claude test3 --tune &
python $SCRIPT_PATH a3 gemini test3 --tune &

# Wait for all background jobs to finish
wait

echo "All test3 runs completed."
