# AI Assessment System - Commands

## Generate
```bash
python main.py generate [model] [assignment] --folder [rubric]
```

**Examples:**
```bash

python main.py generate gemini 2 --folder critical_thinking
python main.py generate claude 3 --folder critical_thinking
python main.py generate grok 1 --folder oral_communication
```

---

## Tune
```bash
python main.py tune [model] [assignment] [rubric]
```

**Examples:**
```bash
python main.py tune chatgpt 1 critical_thinking
python main.py tune gemini 2 critical_thinking
python main.py tune claude 3 critical_thinking
python main.py tune grok 1 oral_communication
```

---

## Reflection
```bash
python main.py reflection [model] [assignment] [rubric]
```

**Examples:**
```bash
python main.py reflection chatgpt 1 critical_thinking
python main.py reflection gemini 2 critical_thinking
python main.py reflection claude 3 critical_thinking
python main.py reflection grok 1 oral_communication
```

---

## Score
```bash
python main.py score [grader] [rubric] [filename] [assignment]
```

**Examples:**
```bash
python main.py score claude critical_thinking a1_gen_chatgpt.json 1
python main.py score grok critical_thinking a1_gen_chatgpt.json 1
python main.py score gemini critical_thinking a1_gen_chatgpt.json 1

python main.py score claude critical_thinking a1_tune_chatgpt.json 1
python main.py score grok critical_thinking a2_gen_claude.json 1
python main.py score chatgpt oral_communication a1_gen_gemini.json 1
```

---

## Pipeline Scripts

### Run single pipeline
```bash
bash run_pipeline.sh [model] [rubric] [assignment]
```

**Examples:**
```bash
bash run_pipeline.sh chatgpt critical_thinking 1
bash run_pipeline.sh gemini critical_thinking 2
bash run_pipeline.sh claude oral_communication 1
```

### Run all pipelines
```bash
bash run_all.sh
```

---

## Parameters

**Models:** `chatgpt` | `gemini` | `claude` | `grok`

**Rubrics:** `critical_thinking` | `oral_communication`

**Assignments:** `1` | `2` | `3`
