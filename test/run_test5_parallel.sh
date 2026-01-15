#!/bin/bash
SCRIPT_PATH="../src/test_main.py"

echo "Starting test5 runs for all assignments in parallel"

# Assignment 1
python $SCRIPT_PATH a1 chatgpt test5 &
python $SCRIPT_PATH a1 grok test5 &
python $SCRIPT_PATH a1 claude test5 &
python $SCRIPT_PATH a1 gemini test5 &

python $SCRIPT_PATH a1 chatgpt test5 --tune &
python $SCRIPT_PATH a1 grok test5 --tune &
python $SCRIPT_PATH a1 claude test5 --tune &
python $SCRIPT_PATH a1 gemini test5 --tune &

# Assignment 2
python $SCRIPT_PATH a2 chatgpt test5 &
python $SCRIPT_PATH a2 grok test5 &
python $SCRIPT_PATH a2 claude test5 &
python $SCRIPT_PATH a2 gemini test5 &

python $SCRIPT_PATH a2 chatgpt test5 --tune &
python $SCRIPT_PATH a2 grok test5 --tune &
python $SCRIPT_PATH a2 claude test5 --tune &
python $SCRIPT_PATH a2 gemini test5 --tune &

# Assignment 3
python $SCRIPT_PATH a3 chatgpt test5 &
python $SCRIPT_PATH a3 grok test5 &
python $SCRIPT_PATH a3 claude test5 &
python $SCRIPT_PATH a3 gemini test5 &

python $SCRIPT_PATH a3 chatgpt test5 --tune &
python $SCRIPT_PATH a3 grok test5 --tune &
python $SCRIPT_PATH a3 claude test5 --tune &
python $SCRIPT_PATH a3 gemini test5 --tune &

# Wait for all background jobs to finish
wait

echo "All test5 runs completed."
