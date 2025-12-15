#!/bin/bash

WRITER=$1
RUBRIC=$2
ASSIGNMENT=$3

# All models
ALL_MODELS=("chatgpt" "grok" "gemini" "claude")

# Filter graders (exclude writer)
GRADERS=()

for model in "${ALL_MODELS[@]}"; do
    if [ "$model" != "$WRITER" ]; then
        GRADERS+=("$model")
    fi
done

cd src
source ~/miniconda3/etc/profile.d/conda.sh
conda activate assessment
echo "Conda activated"

echo "Step 1: Writer ($WRITER) is working."

python main.py generate $WRITER $ASSIGNMENT
python main.py tune $WRITER $RUBRIC $ASSIGNMENT

echo "Step 2: Graders (${GRADERS[@]}) scoring."

for GRADER in "${GRADERS[@]}"; do
    python main.py score $GRADER $WRITER generate $RUBRIC $ASSIGNMENT
    python main.py score $GRADER $WRITER tune $RUBRIC $ASSIGNMENT
done

echo "Step 3: Export to CSV"

cd ../ tools 
python table.py

echo "Done!"