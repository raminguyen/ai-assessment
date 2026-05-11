#!/bin/bash
# Usage:
#   bash run.sh generate <prompt>                              # generate all models, all assignments
#   bash run.sh tune <prompt>                                  # tune all models, all assignments
#   bash run.sh score-gen <prompt>                             # cross-grade generated essays
#   bash run.sh score-tune <prompt>                            # cross-grade tuned essays
#   bash run.sh pipeline <model> <rubric> <assignment> <prompt> # full single-model pipeline
#   bash run.sh all                                            # run all pipelines in parallel
#   bash run.sh gemini-all                                     # re-run all gemini tasks p0-p11

source ~/miniconda3/etc/profile.d/conda.sh
conda activate assessment

CMD=$1
shift

case "$CMD" in

  generate)
    p=${1#p}
    echo "Generating all p${p} essays in parallel..."
    for a in 1 2 3; do
      for model in chatgpt claude gemini grok; do
        python main.py generate $model $a --folder critical_thinking --prompt $p &
      done
    done
    wait
    echo "All p${p} generation done!"
    ;;

  tune)
    p=${1#p}
    echo "Tuning all p${p} essays in parallel..."
    for a in 1 2 3; do
      for model in chatgpt claude gemini grok; do
        python main.py tune $model $a critical_thinking --prompt $p &
      done
    done
    wait
    echo "All p${p} tuning done!"
    ;;

  score-gen)
    p=${1#p}
    echo "Scoring all p${p} generated essays (cross-grading)..."
    for a in 1 2 3; do
      for writer in chatgpt claude gemini grok; do
        for grader in chatgpt claude gemini grok; do
          [ "$writer" != "$grader" ] && python main.py score $grader critical_thinking a${a}_gen_${writer}_p${p}.json $a --prompt $p &
        done
      done
    done
    wait
    echo "All p${p} score-gen done!"
    python analysis/parse_scores.py --join
    ;;

  score-tune)
    p=${1#p}
    echo "Scoring all p${p} tuned essays (cross-grading)..."
    for a in 1 2 3; do
      for writer in chatgpt claude gemini grok; do
        for grader in chatgpt claude gemini grok; do
          [ "$writer" != "$grader" ] && python main.py score $grader critical_thinking a${a}_tune_${writer}_p${p}.json $a --prompt $p &
        done
      done
    done
    wait
    echo "All p${p} score-tune done!"
    python analysis/parse_scores.py --join
    ;;

  pipeline)
    WRITER=$1; RUBRIC=$2; ASSIGNMENT_RAW=$3; PROMPT_RAW=$4
    ASSIGNMENT=${ASSIGNMENT_RAW//a/}; PROMPT=${PROMPT_RAW//p/}
    ALL_MODELS=("chatgpt" "grok" "gemini" "claude")
    GRADERS=()
    for model in "${ALL_MODELS[@]}"; do
      [ "$model" != "$WRITER" ] && GRADERS+=("$model")
    done
    echo "Step 1: $WRITER generating + tuning (assignment $ASSIGNMENT, prompt $PROMPT)"
    python main.py generate $WRITER $ASSIGNMENT --folder $RUBRIC --prompt $PROMPT
    python main.py tune $WRITER $ASSIGNMENT $RUBRIC --prompt $PROMPT
    echo "Step 2: $WRITER reflecting"
    python main.py reflection $WRITER $ASSIGNMENT $RUBRIC --prompt $PROMPT
    echo "Step 3: Graders (${GRADERS[*]}) scoring"
    for GRADER in "${GRADERS[@]}"; do
      python main.py score $GRADER $RUBRIC a${ASSIGNMENT}_gen_${WRITER}_p${PROMPT}.json $ASSIGNMENT --prompt $PROMPT
      python main.py score $GRADER $RUBRIC a${ASSIGNMENT}_tune_${WRITER}_p${PROMPT}.json $ASSIGNMENT --prompt $PROMPT
    done
    echo "Done: $WRITER / assignment $ASSIGNMENT / prompt $PROMPT"
    ;;

  all)
    echo "Starting all pipelines in parallel..."
    for a in 1 2 3; do
      for model in chatgpt gemini grok claude; do
        bash run.sh pipeline $model critical_thinking $a &
      done
    done
    wait
    echo "All done!"
    ;;

  gemini-all)
    OTHER_MODELS=("chatgpt" "claude" "grok")
    for p in 0 1 2 3 4 5 6 7 8 9 10 11; do
      echo "===== Prompt p${p} ====="
      for a in 1 2 3; do python main.py generate gemini $a --folder critical_thinking --prompt $p &; done
      wait
      for a in 1 2 3; do python main.py tune gemini $a critical_thinking --prompt $p &; done
      wait
      for a in 1 2 3; do
        for grader in "${OTHER_MODELS[@]}"; do
          python main.py score $grader critical_thinking a${a}_gen_gemini_p${p}.json $a --prompt $p &
        done
      done
      wait
      for a in 1 2 3; do
        for writer in "${OTHER_MODELS[@]}"; do
          python main.py score gemini critical_thinking a${a}_gen_${writer}_p${p}.json $a --prompt $p &
        done
      done
      wait
      for a in 1 2 3; do
        for grader in "${OTHER_MODELS[@]}"; do
          python main.py score $grader critical_thinking a${a}_tune_gemini_p${p}.json $a --prompt $p &
        done
      done
      wait
      for a in 1 2 3; do
        for writer in "${OTHER_MODELS[@]}"; do
          python main.py score gemini critical_thinking a${a}_tune_${writer}_p${p}.json $a --prompt $p &
        done
      done
      wait
      echo "  [p${p}] Done!"
    done
    echo "===== All prompts p0-p11 complete! ====="
    ;;

  *)
    echo "Usage: bash run.sh <command> [args]"
    echo ""
    echo "Commands:"
    echo "  generate <prompt>                               Generate essays (all models, all assignments)"
    echo "  tune <prompt>                                   Tune essays"
    echo "  score-gen <prompt>                              Cross-grade generated essays"
    echo "  score-tune <prompt>                             Cross-grade tuned essays"
    echo "  pipeline <model> <rubric> <assignment> <prompt> Full pipeline for one model"
    echo "  all                                             Run all pipelines in parallel"
    echo "  gemini-all                                      Re-run all gemini tasks (p0-p11)"
    ;;
esac
