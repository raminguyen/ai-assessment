#!/bin/bash

#Assignment 1, Rubric: critical_thinking
bash run_pipeline.sh chatgpt critical_thinking 1
bash run_pipeline.sh gemini critical_thinking 1
bash run_pipeline.sh grok critical_thinking 1
bash run_pipeline.sh claude critical_thinking 1

bash run_pipeline.sh chatgpt critical_thinking 2
bash run_pipeline.sh gemini critical_thinking 2
bash run_pipeline.sh grok critical_thinking 2
bash run_pipeline.sh claude critical_thinking 2

bash run_pipeline.sh chatgpt critical_thinking 3
bash run_pipeline.sh gemini critical_thinking 3
bash run_pipeline.sh grok critical_thinking 3
bash run_pipeline.sh claude critical_thinking 3

#Assignment 2, Rubric: oral_communication
bash run_pipeline.sh chatgpt oral_communication 1
bash run_pipeline.sh gemini oral_communication 1
bash run_pipeline.sh grok oral_communication 1
bash run_pipeline.sh claude oral_communication 1

echo "All done!"