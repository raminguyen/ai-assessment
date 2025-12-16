#!/bin/bash

WRITER=$1
RUBRIC=$2
ASSIGNMENT=$3

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

echo "Step 1: Writer ($WRITER) is working."

python main.py generate $WRITER $ASSIGNMENT --folder $RUBRIC
python main.py tune $WRITER $ASSIGNMENT $RUBRIC 

echo "Step 2: Graders (${GRADERS[@]}) scoring."

for GRADER in "${GRADERS[@]}"; do
    python main.py score $GRADER $RUBRIC a${ASSIGNMENT}_gen_${WRITER}.json $ASSIGNMENT
    python main.py score $GRADER $RUBRIC a${ASSIGNMENT}_tune_${WRITER}.json $ASSIGNMENT
done

echo "Step 3: Export to CSV and DOCX"

cd ../tools
python table.py
python converttodoc.py

echo "Done!"