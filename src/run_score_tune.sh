#!/bin/bash
p=${1#p}
echo "Scoring all p${p} essays (cross-grading) in parallel..."

for a in 1 2 3; do

  for writer in chatgpt claude gemini grok; do

    for grader in chatgpt claude gemini grok; do

      [ "$writer" != "$grader" ] && python main.py score $grader critical_thinking a${a}_tune_${writer}_p${p}.json $a --prompt $p &
    
    done

  done

done

wait
echo "All p${p} scoring done!"

python parse_scores.py --join
