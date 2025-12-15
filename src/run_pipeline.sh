#!/bin/bash

WRITER=$1
GRADERS=$2
RUBRIC=$3
ASSIGNMENT=$4

echo "Running pipeline: Writer=$WRITER, Graders=$GRADERS, Rubric=$RUBRIC, Assignment=$ASSIGNMENT"

# Generate
echo "Step 1: Generating essay"
python main.py generate $WRITER $ASSIGNMENT

# Tune
echo "Step 2: Tuning essay"
python main.py tune $WRITER $RUBRIC $ASSIGNMENT

# Score with each grader
STEP=3

for GRADER in $GRADERS; do
    
    echo "Step ${STEP}a: $GRADER grading generated essay"
    python main.py score $GRADER $RUBRIC ${WRITER}_essay.json $ASSIGNMENT
    
    echo "Step ${STEP}b: $GRADER grading tuned essay"
    python main.py score $GRADER $RUBRIC ${WRITER}_essay_tuned.json $ASSIGNMENT
    
    STEP=$((STEP + 1))

done

echo "Done! Check assignment_${ASSIGNMENT}.json"