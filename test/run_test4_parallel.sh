#!/bin/bash
SCRIPT_PATH="../src/test_main.py"

echo "Starting test4 runs for all assignments in parallel"

# Assignment 1
python $SCRIPT_PATH a1 chatgpt test4 &
python $SCRIPT_PATH a1 grok test4 &
python $SCRIPT_PATH a1 claude test4 &
python $SCRIPT_PATH a1 gemini test4 &

python $SCRIPT_PATH a1 chatgpt test4 --tune &
python $SCRIPT_PATH a1 grok test4 --tune &
python $SCRIPT_PATH a1 claude test4 --tune &
python $SCRIPT_PATH a1 gemini test4 --tune &

# Assignment 2
python $SCRIPT_PATH a2 chatgpt test4 &
python $SCRIPT_PATH a2 grok test4 &
python $SCRIPT_PATH a2 claude test4 &
python $SCRIPT_PATH a2 gemini test4 &

python $SCRIPT_PATH a2 chatgpt test4 --tune &
python $SCRIPT_PATH a2 grok test4 --tune &
python $SCRIPT_PATH a2 claude test4 --tune &
python $SCRIPT_PATH a2 gemini test4 --tune &

# Assignment 3
python $SCRIPT_PATH a3 chatgpt test4 &
python $SCRIPT_PATH a3 grok test4 &
python $SCRIPT_PATH a3 claude test4 &
python $SCRIPT_PATH a3 gemini test4 &

python $SCRIPT_PATH a3 chatgpt test4 --tune &
python $SCRIPT_PATH a3 grok test4 --tune &
python $SCRIPT_PATH a3 claude test4 --tune &
python $SCRIPT_PATH a3 gemini test4 --tune &

# Wait for all background jobs to finish
wait

echo "All test4 runs completed."
