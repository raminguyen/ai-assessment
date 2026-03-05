#!/bin/bash
echo "Scoring tune p7 to p12..."

for p in 7 8 9 10 11 12; do
  echo "-- Scoring tune p$p --"
  bash run_score_tune.sh p$p
done

echo "All scoring done: p7 to p12!"
