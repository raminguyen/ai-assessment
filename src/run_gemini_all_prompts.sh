#!/bin/bash
# Re-run all gemini tasks for prompts p0 to p11
# Existing non-gemini files are skipped automatically

source ~/miniconda3/etc/profile.d/conda.sh
conda activate assessment

OTHER_MODELS=("chatgpt" "claude" "grok")

for p in 0 1 2 3 4 5 6 7 8 9 10 11; do
  echo "===== Prompt p${p} ====="

  # Step 1: Generate gemini essays
  echo "  [p${p}] Generating gemini essays..."
  for a in 1 2 3; do
    python main.py generate gemini $a --folder critical_thinking --prompt $p &
  done
  wait
  echo "  [p${p}] Generation done."

  # Step 2: Tune gemini essays
  echo "  [p${p}] Tuning gemini essays..."
  for a in 1 2 3; do
    python main.py tune gemini $a critical_thinking --prompt $p &
  done
  wait
  echo "  [p${p}] Tuning done."

  # Step 3: Score gemini-generated essays (graded by others)
  echo "  [p${p}] Scoring gemini-gen essays (others grading gemini)..."
  for a in 1 2 3; do
    for grader in "${OTHER_MODELS[@]}"; do
      python main.py score $grader critical_thinking a${a}_gen_gemini_p${p}.json $a --prompt $p &
    done
  done
  wait

  # Step 4: Score others' generated essays (graded by gemini)
  echo "  [p${p}] Scoring others' gen essays (gemini grading)..."
  for a in 1 2 3; do
    for writer in "${OTHER_MODELS[@]}"; do
      python main.py score gemini critical_thinking a${a}_gen_${writer}_p${p}.json $a --prompt $p &
    done
  done
  wait

  # Step 5: Score gemini-tuned essays (graded by others)
  echo "  [p${p}] Scoring gemini-tune essays (others grading gemini)..."
  for a in 1 2 3; do
    for grader in "${OTHER_MODELS[@]}"; do
      python main.py score $grader critical_thinking a${a}_tune_gemini_p${p}.json $a --prompt $p &
    done
  done
  wait

  # Step 6: Score others' tuned essays (graded by gemini)
  echo "  [p${p}] Scoring others' tune essays (gemini grading)..."
  for a in 1 2 3; do
    for writer in "${OTHER_MODELS[@]}"; do
      python main.py score gemini critical_thinking a${a}_tune_${writer}_p${p}.json $a --prompt $p &
    done
  done
  wait

  echo "  [p${p}] All done!"
done

echo "===== All prompts p0-p11 complete! ====="
