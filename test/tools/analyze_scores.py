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

DIMENSION_PATTERNS = {
    'Explanation of issues': r'Explanation of issues',
    'Evidence': r'Evidence(?:\s*\([^)]*\))?',
    'Influence of context and assumptions': r'Influence of context (?:and|&) assumptions',
    "Student's position": r"Student['\u2019]s position(?:\s*\([^)]*\))?",
    'Conclusions and related outcomes': r'Conclusions (?:and|&) related outcomes',
}

def parse_dimension_scores(text):
    scores = {}
    for dim in DIMENSIONS:
        dim_pattern = DIMENSION_PATTERNS.get(dim, re.escape(dim))
        patterns = [
            dim_pattern + r'.*?(\d+(?:\.\d+)?)',
            r'\*\*' + dim_pattern + r':\*\*\s*(\d+(?:\.\d+)?)',
            r'\|.*?' + dim_pattern + r'.*?\|\s*\*?\*?(\d+(?:\.\d+)?)\*?\*?\s*\|',
            r'- \*\*' + dim_pattern + r'\s*:?\*\*\s*:?\s*(\d+(?:\.\d+)?)',
            r'\*\*' + dim_pattern + r'\*\*\s*:?\s*(\d+(?:\.\d+)?)',
            r'\d+\.\s*\*?\*?' + dim_pattern + r'\*?\*?\s*:?\s*(\d+(?:\.\d+)?)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                try:
                    scores[dim] = float(match.group(1))
                except ValueError:
                    scores[dim] = 0.0
                break
        if dim not in scores:
            scores[dim] = 0.0
    return scores

# Storage: data[assignment][writer][essay_type] = {dim: [scores from all graders]}
data = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list))))

for filename in os.listdir(DATA_DIR):
    if not filename.endswith('.json') or '_score_' not in filename:
        continue

    # Parse filename
    parts = filename.replace('.json', '').split('_')
    assignment = parts[0]  # a1, a2, a3

    # Get prompt number
    prompt_num = None
    for p in parts:
        if p.startswith('p') and len(p) == 2:
            prompt_num = p
            break

    # We'll analyze prompt 2 (p2) as it seems to be the main one used
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

    # Load and parse
    with open(DATA_DIR / filename) as f:
        content = json.load(f)

    result_text = content.get('result', '')
    scores = parse_dimension_scores(result_text)

    for dim, score in scores.items():
        data[assignment][writer][essay_type][dim].append(score)

# Calculate averages and print results
print('='*80)
print('DETAILED WRITER ANALYSIS (P2 Data)')
print('='*80)

for writer in WRITERS:
    print(f'\n' + '='*80)
    print(f'WRITER: {writer.upper()}')
    print('='*80)

    for assignment in ['a1', 'a2', 'a3']:
        gen_data = data[assignment][writer]['gen']
        tune_data = data[assignment][writer]['tune']

        print(f'\n--- {assignment.upper()} ---')
        gen_avg_total = 0
        tune_avg_total = 0

        for dim in DIMENSIONS:
            gen_scores = gen_data.get(dim, [])
            tune_scores = tune_data.get(dim, [])

            gen_avg = sum(gen_scores)/len(gen_scores) if gen_scores else 0
            tune_avg = sum(tune_scores)/len(tune_scores) if tune_scores else 0
            diff = tune_avg - gen_avg

            gen_avg_total += gen_avg
            tune_avg_total += tune_avg

            short_dim = dim[:20]
            print(f'  {short_dim:25} Gen: {gen_avg:.2f}  Tune: {tune_avg:.2f}  Diff: {diff:+.2f}')

        total_diff = tune_avg_total - gen_avg_total
        print(f'  {"TOTAL (sum of 5 dims)":25} Gen: {gen_avg_total:.2f}  Tune: {tune_avg_total:.2f}  Diff: {total_diff:+.2f}')
        print(f'  {"AVG (total/5)":25} Gen: {gen_avg_total/5:.2f}  Tune: {tune_avg_total/5:.2f}  Diff: {total_diff/5:+.2f}')

# Summary table
print('\n' + '='*80)
print('SUMMARY: AVERAGE SCORES PER WRITER PER ASSIGNMENT (Average of 5 dimensions)')
print('='*80)
print(f'{"Writer":10} {"A1-Gen":8} {"A1-Tune":8} {"A1-Diff":8} {"A2-Gen":8} {"A2-Tune":8} {"A2-Diff":8} {"A3-Gen":8} {"A3-Tune":8} {"A3-Diff":8} {"Avg-Diff":10}')
print('-'*100)

for writer in WRITERS:
    row = [writer.upper()]
    diffs = []
    for assignment in ['a1', 'a2', 'a3']:
        gen_total = 0
        tune_total = 0
        for dim in DIMENSIONS:
            gen_scores = data[assignment][writer]['gen'].get(dim, [])
            tune_scores = data[assignment][writer]['tune'].get(dim, [])
            gen_total += sum(gen_scores)/len(gen_scores) if gen_scores else 0
            tune_total += sum(tune_scores)/len(tune_scores) if tune_scores else 0

        gen_avg = gen_total / 5
        tune_avg = tune_total / 5
        diff = tune_avg - gen_avg
        diffs.append(diff)
        row.extend([f'{gen_avg:.2f}', f'{tune_avg:.2f}', f'{diff:+.2f}'])

    avg_diff = sum(diffs) / len(diffs)
    row.append(f'{avg_diff:+.2f}')
    print(' '.join(f'{x:8}' for x in row))

# Dimension analysis per writer
print('\n' + '='*80)
print('DIMENSION ANALYSIS: HIGHEST & LOWEST SCORING DIMENSIONS PER WRITER')
print('='*80)

for writer in WRITERS:
    print(f'\n{writer.upper()}:')
    dim_avgs = defaultdict(list)

    for assignment in ['a1', 'a2', 'a3']:
        for dim in DIMENSIONS:
            gen_scores = data[assignment][writer]['gen'].get(dim, [])
            tune_scores = data[assignment][writer]['tune'].get(dim, [])
            gen_avg = sum(gen_scores)/len(gen_scores) if gen_scores else 0
            tune_avg = sum(tune_scores)/len(tune_scores) if tune_scores else 0
            dim_avgs[dim].append((gen_avg, tune_avg))

    # Calculate overall average per dimension
    dim_overall = {}
    for dim, vals in dim_avgs.items():
        avg_gen = sum(v[0] for v in vals) / len(vals)
        avg_tune = sum(v[1] for v in vals) / len(vals)
        dim_overall[dim] = (avg_gen, avg_tune, (avg_gen + avg_tune) / 2)

    sorted_dims = sorted(dim_overall.items(), key=lambda x: x[1][2], reverse=True)
    print(f'  Highest: {sorted_dims[0][0]} (avg: {sorted_dims[0][1][2]:.2f})')
    print(f'  Lowest:  {sorted_dims[-1][0]} (avg: {sorted_dims[-1][1][2]:.2f})')

    print('  All dimensions (sorted high to low):')
    for dim, (gen, tune, overall) in sorted_dims:
        print(f'    {dim[:35]:35} Gen: {gen:.2f}, Tune: {tune:.2f}, Avg: {overall:.2f}')

# Print per-assignment dimension breakdown for each writer
print('\n' + '='*80)
print('PER-ASSIGNMENT DIMENSION BREAKDOWN')
print('='*80)

for writer in WRITERS:
    print(f'\n{"="*40}')
    print(f'{writer.upper()} - Per Assignment Dimension Scores')
    print(f'{"="*40}')

    for assignment in ['a1', 'a2', 'a3']:
        print(f'\n  {assignment.upper()}:')
        dims_scores = []
        for dim in DIMENSIONS:
            gen_scores = data[assignment][writer]['gen'].get(dim, [])
            tune_scores = data[assignment][writer]['tune'].get(dim, [])
            gen_avg = sum(gen_scores)/len(gen_scores) if gen_scores else 0
            tune_avg = sum(tune_scores)/len(tune_scores) if tune_scores else 0
            dims_scores.append((dim, gen_avg, tune_avg))

        # Sort by tune score to show highest/lowest
        sorted_by_tune = sorted(dims_scores, key=lambda x: x[2], reverse=True)
        print(f'    Highest (Tune): {sorted_by_tune[0][0][:25]} = {sorted_by_tune[0][2]:.2f}')
        print(f'    Lowest (Tune):  {sorted_by_tune[-1][0][:25]} = {sorted_by_tune[-1][2]:.2f}')
