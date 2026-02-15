import os
import json
import re
from pathlib import Path
from collections import defaultdict

DATA_DIR = Path('data/critical_thinking')
WRITERS = ['chatgpt', 'gemini', 'claude', 'grok']
DIMENSIONS = [
    'Explanation of issues',
    'Evidence',
    'Influence of context and assumptions',
    "Student's position",
    'Conclusions and related outcomes'
]
SHORT_DIMS = ['Issues', 'Evidence', 'Context', 'Position', 'Conclusion']

DIMENSION_PATTERNS = {
    'Explanation of issues': r'Explanation of issues',
    'Evidence': r'Evidence(?:\s*\([^)]*\))?',
    'Influence of context and assumptions': r'Influence of context (?:and|&) assumptions',
    "Student's position": r"Student['\u2019]s position(?:\s*\([^)]*\))?",
    'Conclusions and related outcomes': r'Conclusions (?:and|&) related outcomes',
}

def parse_dimension_scores(text):
    """
    Parse rubric dimension scores from text.
    Based on comprehensive JS parser with many format variations.
    """
    scores = {}

    # Alternate names for dimensions (like in JS parser)
    dim_alternates = {
        'Evidence': ['Evidence', 'Evidence (selecting and using information)', 'Evidence (selecting/using information)', 'Evidence (Selecting and using information to investigate a point of view or conclusion)'],
        "Student's position": ["Student's position", "Student's position (perspective/thesis)", "Student's position (perspective, thesis/hypothesis)", "Student's position (perspective/thesis/hypothesis)"],
        'Conclusions and related outcomes': ['Conclusions and related outcomes', 'Conclusions/outcomes', 'Conclusions and related outcomes (implications and consequences)'],
    }

    for dim in DIMENSIONS:
        # Get base pattern and alternates
        names_to_try = dim_alternates.get(dim, [dim])

        for dim_name in names_to_try:
            # Escape regex special chars and handle apostrophe variations
            dim_escaped = re.escape(dim_name)
            # Handle straight and curly apostrophes (re.escape doesn't escape apostrophe)
            dim_escaped = dim_escaped.replace("'", r"['\u2019]")
            # Handle "and" vs "&"
            dim_escaped = dim_escaped.replace(r'\ and\ ', r'\ (?:and|&)\ ')

            # Comprehensive list of patterns (ordered from most specific to least)
            patterns = [
                # Format: - **Dimension**: 4 (Grok style - colon before closing **)
                r'^\s*-\s*\*\*' + dim_escaped + r'\*\*:\s*(\d+(?:\.\d+)?)',
                # Format: - **Dimension:** 3 or 3.5
                r'^\s*-\s*\*\*' + dim_escaped + r':\*\*\s*(\d+(?:\.\d+)?)',
                # Format: ### 1. Dimension: **3.5/4
                r'###\s*\d+\.\s*' + dim_escaped + r':[^\n]*?\*\*(\d+(?:\.\d+)?)',
                # Format: **Score: 4 (Capstone)** after dimension name
                dim_escaped + r'[^\n]*?\n[\s\S]{0,500}?\*\*Score:\s*(\d+(?:\.\d+)?)\s*\([^)]+\)\*\*',
                # Format: **Score:** 3.5
                dim_escaped + r'[^\n]*?\n[\s\S]{0,500}?\*\*Score:\*\*\s*(\d+(?:\.\d+)?)',
                # Format: **Dimension:** 3.5/4
                r'\*\*' + dim_escaped + r':\*\*\s*(\d+(?:\.\d+)?)/\d+',
                # Format: **Dimension:** 3 or 3.5
                r'\*\*' + dim_escaped + r':\*\*\s*(\d+(?:\.\d+)?)',
                # Format: | **Dimension** | 4 (Capstone) |
                r'\|\s*\*\*' + dim_escaped + r'\*\*\s*\|\s*(\d+(?:\.\d+)?)\s*\([^)]+\)\s*\|',
                # Format: | **Dimension** | **3** | or **3.5** |
                r'\|\s*\*\*' + dim_escaped + r'\*\*\s*\|\s*\*\*(\d+(?:\.\d+)?)\*\*\s*\|',
                # Format: | **Dimension** | 3 | or 3.5 |
                r'\|\s*\*\*' + dim_escaped + r'\*\*\s*\|\s*(\d+(?:\.\d+)?)\s*\|',
                # Format: | Dimension | 3 | or 3.5 |
                r'\|\s*' + dim_escaped + r'\s*\|\s*(\d+(?:\.\d+)?)\s*\|',
                # Format: **Dimension:** **3 or **3.5
                r'\*\*' + dim_escaped + r':\*\*\s*\*\*(\d+(?:\.\d+)?)',
                # Format: Dimension: **3** or **3.5**
                dim_escaped + r':\s*\*\*(\d+(?:\.\d+)?)\*\*',
                # Format: Dimension: [3] or [3.5]
                dim_escaped + r':\s*\[(\d+(?:\.\d+)?)\]',
                # Format: Dimension: 3 or 3.5
                dim_escaped + r':\s*(\d+(?:\.\d+)?)',
                # Format: **Dimension: 3** or **Dimension: 3.5**
                r'\*\*' + dim_escaped + r':\s*(\d+(?:\.\d+)?)\*\*',
                # Flexible: any text then bold score
                dim_escaped + r'.*?:\s*\*\*(\d+(?:\.\d+)?)\*\*',
                # 1) Explanation of issues — **3 (Milestone)**
                r'###\s*\d+[).]?\s*' + dim_escaped + r'\s*[\u2014\u2013\-]\s*\*\*(\d+(?:\.\d+)?)',
                # Bold Table Rows with Bold Scores: | **Explanation of issues** | **4 (Capstone)** |
                r'\|\s*\*\*' + dim_escaped + r'\*\*\s*\|\s*\*\*(\d+(?:\.\d+)?)(?:\s*\([^)]+\))?\*\*\s*\|',
                # "Student's position" even with "(perspective...)" after it
                r'\|?\s*\*?\*?' + dim_escaped + r'(?:\s*\([^)]+\))?\*?\*?\s*\|?\s*[\u2014\u2013\-:]?\s*\|?\s*\*\*(\d+(?:\.\d+)?)(?:\s*\([^)]+\))?\*\*',
                # * **Student's position (perspective, thesis/hypothesis):** **4**
                r'\*?\s*\*\*' + dim_escaped + r'(?:\s*\([^)]+\))?:?\*\*\s*[:\-]?\s*\*\*(\d+(?:\.\d+)?)\*\*',
                # 2. Evidence (Selecting and using information): **4 (Capstone)**
                r'###\s*\d+\.\s*' + dim_escaped + r'(?:\s*\(.*?\))?:\s*\*\*(\d+(?:\.\d+)?)',
                # ChatGPT format: **4) Student's position (perspective/thesis): 4 (Capstone)**
                r'\*\*\d+\)\s*' + dim_escaped + r'(?:\s*\([^)]*\))?:\s*(\d+(?:\.\d+)?)',
                # ChatGPT summary: - **Student's position:** **4**
                r'-\s*\*\*' + dim_escaped + r':\*\*\s*\*\*(\d+(?:\.\d+)?)\*\*',
                # ChatGPT summary variant: - **Conclusions/outcomes:** **3**
                r'-\s*\*\*' + dim_escaped + r':\*\*\s*\*\*(\d+(?:\.\d+)?)',
                # Grok format: **Conclusions and related outcomes (implications and consequences): 4**
                r'\*\*' + dim_escaped + r'(?:\s*\([^)]*\))?:\s*(\d+(?:\.\d+)?)\*\*',
                # ChatGPT numerical summary: - Dimension: **3**
                r'-\s*' + dim_escaped + r':\s*\*\*(\d+(?:\.\d+)?)\*\*',
                # Simple format: Dimension: 3
                dim_escaped + r':\s*(\d+(?:\.\d+)?)',
            ]

            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    try:
                        score = float(match.group(1))
                        # Sanity check: scores should be 0-4
                        if 0 <= score <= 4:
                            scores[dim] = score
                            break
                    except ValueError:
                        pass

            # If found, break out of alternates loop
            if dim in scores:
                break

        # Default to 0 if not found
        if dim not in scores:
            scores[dim] = 0.0

    return scores

# Storage: data[assignment][writer][grader][essay_type] = {dim: score}
data = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(dict))))

for filename in os.listdir(DATA_DIR):
    if not filename.endswith('.json') or '_score_' not in filename:
        continue

    parts = filename.replace('.json', '').split('_')
    assignment = parts[0]

    prompt_num = None
    for p in parts:
        if p.startswith('p') and len(p) == 2:
            prompt_num = p
            break

    if prompt_num != 'p2':
        continue

    if 'gen' in parts:
        essay_type = 'gen'
        type_idx = parts.index('gen')
    elif 'tune' in parts:
        essay_type = 'tune'
        type_idx = parts.index('tune')
    else:
        continue

    writer = parts[type_idx + 1]

    if 'score' in parts:
        score_idx = parts.index('score')
        grader = parts[score_idx + 1]
    else:
        continue

    if writer not in WRITERS or grader not in WRITERS or writer == grader:
        continue

    with open(DATA_DIR / filename) as f:
        content = json.load(f)

    result_text = content.get('result', '')
    scores = parse_dimension_scores(result_text)
    data[assignment][writer][grader][essay_type] = scores

# Print detailed tables for each writer
for writer in WRITERS:
    print('=' * 100)
    print(f'WRITER: {writer.upper()} - DETAILED SCORE BREAKDOWN (P2)')
    print('=' * 100)

    for assignment in ['a1', 'a2', 'a3']:
        print(f'\n{assignment.upper()} - {writer.upper()}')
        print('-' * 100)

        # Header
        header = f"{'Grader':<10} {'Type':<6}"
        for sd in SHORT_DIMS:
            header += f' {sd:>10}'
        header += f' {"TOTAL":>10} {"AVG":>8}'
        print(header)
        print('-' * 100)

        graders = [g for g in WRITERS if g != writer]

        gen_totals = defaultdict(list)
        tune_totals = defaultdict(list)

        for grader in graders:
            for essay_type in ['gen', 'tune']:
                scores = data[assignment][writer][grader].get(essay_type, {})
                if scores:
                    row = f'{grader:<10} {essay_type:<6}'
                    total = 0
                    for dim in DIMENSIONS:
                        score = scores.get(dim, 0)
                        row += f' {score:>10.2f}'
                        total += score
                        if essay_type == 'gen':
                            gen_totals[dim].append(score)
                        else:
                            tune_totals[dim].append(score)
                    avg = total / 5
                    row += f' {total:>10.2f} {avg:>8.2f}'
                    print(row)
            print()

        # Calculate and print averages
        print('-' * 100)

        # Gen average
        row_gen = f"{'AVERAGE':<10} {'gen':<6}"
        gen_sum = 0
        for dim in DIMENSIONS:
            avg = sum(gen_totals[dim])/len(gen_totals[dim]) if gen_totals[dim] else 0
            row_gen += f' {avg:>10.2f}'
            gen_sum += avg
        row_gen += f' {gen_sum:>10.2f} {gen_sum/5:>8.2f}'
        print(row_gen)

        # Tune average
        row_tune = f"{'AVERAGE':<10} {'tune':<6}"
        tune_sum = 0
        for dim in DIMENSIONS:
            avg = sum(tune_totals[dim])/len(tune_totals[dim]) if tune_totals[dim] else 0
            row_tune += f' {avg:>10.2f}'
            tune_sum += avg
        row_tune += f' {tune_sum:>10.2f} {tune_sum/5:>8.2f}'
        print(row_tune)

        # Diff
        row_diff = f"{'DIFF':<10} {'':6}"
        for dim in DIMENSIONS:
            gen_avg = sum(gen_totals[dim])/len(gen_totals[dim]) if gen_totals[dim] else 0
            tune_avg = sum(tune_totals[dim])/len(tune_totals[dim]) if tune_totals[dim] else 0
            diff = tune_avg - gen_avg
            row_diff += f' {diff:>+10.2f}'
        total_diff = tune_sum - gen_sum
        row_diff += f' {total_diff:>+10.2f} {total_diff/5:>+8.2f}'
        print(row_diff)

    print('\n')
