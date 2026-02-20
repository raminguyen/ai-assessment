#!/bin/bash
p=${1#p}
echo "Tuning all p${p} essays in parallel..."

for a in 1 2 3; do

  for model in chatgpt claude gemini grok; do

    python main.py tune $model $a critical_thinking --prompt $p &

  done

done

wait
echo "All p${p} tuning done!"
