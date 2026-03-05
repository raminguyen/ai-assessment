#!/bin/bash
echo "Tuning p7 to p12..."

for p in 7 8 9 10 11 12; do
  echo "-- Tuning p$p --"
  bash run_tune.sh p$p
done

echo "All tuning done: p7 to p12!"
