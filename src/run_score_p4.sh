#!/bin/bash
echo "Scoring all p4 essays (cross-grading) in parallel..."

for a in 1 2 3; do
  for writer in chatgpt claude gemini grok; do
    for grader in chatgpt claude gemini grok; do
      [ "$writer" != "$grader" ] && python main.py score $grader critical_thinking a${a}_gen_${writer}_p4.json $a --prompt 4 &
    done
  done
done

wait
echo "All p4 scoring done!"
