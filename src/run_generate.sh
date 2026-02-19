#!/bin/bash
p=${1#p}
echo "Generating all p${p} essays in parallel..."

for a in 1 2 3; do

  for model in chatgpt claude gemini grok; do

    python main.py generate $model $a --folder critical_thinking --prompt $p &

  done

done

wait
echo "All p${p} generation done!"
