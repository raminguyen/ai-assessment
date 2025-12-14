
# Running the AI Assessment System

## Command Format

```bash
python main.py [writer] [workflow] [rubric] [assignment]
```

## Arguments

1. **writer**: Which AI writes the essay
   - Options: `chatgpt`, `gemini`, `claude`, `grok`

2. **workflow**: Which workflow to run
   - `norubric` - Generate without rubric, grade with rubric
   - `withrubric` - Generate with rubric, grade with rubric
   - `both` - Run both workflows

3. **rubric**: Which rubric to use for grading
   - Options: `critical_thinking`, `oral_communication`

4. **assignment**: Assignment number
   - Any number: `1`, `2`, `3`

## Examples

```bash
# ChatGPT writes, both workflows, oral_communication rubric, assignment 1
python main.py chatgpt both oral_communication 1

# Gemini writes, only norubric workflow, critical_thinking rubric, assignment 2
python main.py gemini norubric critical_thinking 2

# Grok writes, only withrubric workflow, oral_communication rubric, assignment 3
python main.py grok withrubric oral_communication 3

# Claude writes, both workflows, critical_thinking rubric, assignment 1
python main.py claude both critical_thinking 1
```

## What Happens

- Writer generates essay
- All other models grade the essay
- Results saved to: `output/assignment_[N]/[writer]/[rubric]/[workflow]/`
- JSON files and Word docs created automatically
```

