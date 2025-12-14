# AI Essay Assessment

Automated essay generation and grading using multiple AI models.

## Quick Start

1. **Install:**
```bash
pip install openai google-genai anthropic xai-sdk python-dotenv python-docx strip-markdown
```

2. **Add API keys to `.env`:**
```
OPENAI_API_KEY=your_key
GOOGLE_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
GROK_API_KEY=your_key
```

3. **Run:**
```bash
python main.py chatgpt both 1
```

## Commands
```bash
# One model, both workflows
python main.py chatgpt both 1

# One model, one workflow
python main.py gemini norubric 1
python main.py grok withrubric 2

# Different assignments
python main.py claude both 3
```

## Workflows

### 1. Without Rubric (norubric)
- Writer generates essay (no rubric)
- All other models grade it (with rubric)

### 2. With Rubric (withrubric)
- Writer generates essay (with rubric)
- All other models grade it (with rubric)

### 3. Both
- Runs norubric workflow
- Then runs withrubric workflow

## Models

- `chatgpt` - GPT-5.2
- `gemini` - Gemini-3 Pro
- `claude` - Claude Sonnet 4
- `grok` - Grok-4

## Output
```
assignment_1/
└── chatgpt/
    ├── norubric/
    │   ├── chatgpt_generate_essay1.json
    │   ├── gemini_grade_essay1.json
    │   ├── claude_grade_essay1.json
    │   ├── grok_grade_essay1.json
    │   └── docs/
    │       ├── chatgpt_generate_essay1.docx
    │       └── ...
    └── withrubric/
        ├── chatgpt_tuned_essay1.json
        ├── gemini_grade_tuned_essay1.json
        └── ...
```

Each JSON includes:
- Essay text
- Model names
- Time taken (minutes)
- Rubric used
- Timestamp

---

By Rami Huu Nguyen