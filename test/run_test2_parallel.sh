#!/bin/bash
SCRIPT_PATH="../src/test_main.py"

echo "Starting test2 runs for all assignments in parallel"

# Assignment 1
python $SCRIPT_PATH a1 chatgpt test2 &
python $SCRIPT_PATH a1 grok test2 &
python $SCRIPT_PATH a1 claude test2 &
python $SCRIPT_PATH a1 gemini test2 &

python $SCRIPT_PATH a1 chatgpt test2 --tune &
python $SCRIPT_PATH a1 grok test2 --tune &
python $SCRIPT_PATH a1 claude test2 --tune &
python $SCRIPT_PATH a1 gemini test2 --tune &

# Assignment 2
python $SCRIPT_PATH a2 chatgpt test2 &
python $SCRIPT_PATH a2 grok test2 &
python $SCRIPT_PATH a2 claude test2 &
python $SCRIPT_PATH a2 gemini test2 &

python $SCRIPT_PATH a2 chatgpt test2 --tune &
python $SCRIPT_PATH a2 grok test2 --tune &
python $SCRIPT_PATH a2 claude test2 --tune &
python $SCRIPT_PATH a2 gemini test2 --tune &

# Assignment 3
python $SCRIPT_PATH a3 chatgpt test2 &
python $SCRIPT_PATH a3 grok test2 &
python $SCRIPT_PATH a3 claude test2 &
python $SCRIPT_PATH a3 gemini test2 &

python $SCRIPT_PATH a3 chatgpt test2 --tune &
python $SCRIPT_PATH a3 grok test2 --tune &
python $SCRIPT_PATH a3 claude test2 --tune &
python $SCRIPT_PATH a3 gemini test2 --tune &

# Wait for all background jobs to finish
wait

echo "All test2 runs completed."
