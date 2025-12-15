# AI Essay Assessment Tool

## How It Works

1. **Generate** - A model writes an essay
2. **Tune** - The same model improves the essay based on a rubric
3. **Score** - Other models grade both essays

All results are saved to `data.json` organized by assignment.

## Installation

```bash
pip install -r requirements.txt
```

## Commands

Generate essay:
```bash
python main.py generate chatgpt 1
```

Tune essay:
```bash
python main.py tune chatgpt critical_thinking 1
```

Score essay:
```bash
python main.py score grok chatgpt generate critical_thinking 1
```

All commands are flexible. Change writer, grader, rubric, and assignment.

## Full Pipeline

```bash
bash ./run_pipeline.sh chatgpt critical_thinking 1
```

**Note:** chatgpt is writer, the rest (grok, gemini, claude) are graders.

## Results

Results saved to `../data/data.json`