#!/bin/bash

# Usage: bash run_pipeline.sh <model> <rubric> <assignment> <prompt>
# Example: bash run_pipeline.sh chatgpt critical_thinking a1 p1

WRITER=$1
RUBRIC=$2
ASSIGNMENT_RAW=$3
PROMPT_RAW=$4

# Extract number from a1 -> 1, p1 -> 1
ASSIGNMENT=${ASSIGNMENT_RAW//a/}
PROMPT=${PROMPT_RAW//p/}

ALL_MODELS=("chatgpt" "grok" "gemini" "claude")

GRADERS=()
for model in "${ALL_MODELS[@]}"; do
    if [ "$model" != "$WRITER" ]; then
        GRADERS+=("$model")
    fi
done

source ~/miniconda3/etc/profile.d/conda.sh
conda activate assessment
echo "Conda activated"

echo "Step 1: Writer ($WRITER) generating and tuning for assignment $ASSIGNMENT, prompt $PROMPT"

python main.py generate $WRITER $ASSIGNMENT --folder $RUBRIC --prompt $PROMPT
python main.py tune $WRITER $ASSIGNMENT $RUBRIC --prompt $PROMPT

echo "Step 2: Writer ($WRITER) reflecting on changes."

python main.py reflection $WRITER $ASSIGNMENT $RUBRIC --prompt $PROMPT

echo "Step 3: Graders (${GRADERS[@]}) scoring."

for GRADER in "${GRADERS[@]}"; do
    python main.py score $GRADER $RUBRIC a${ASSIGNMENT}_gen_${WRITER}_p${PROMPT}.json $ASSIGNMENT --prompt $PROMPT
    python main.py score $GRADER $RUBRIC a${ASSIGNMENT}_tune_${WRITER}_p${PROMPT}.json $ASSIGNMENT --prompt $PROMPT
done

echo "Done with $WRITER, assignment $ASSIGNMENT, prompt $PROMPT!"