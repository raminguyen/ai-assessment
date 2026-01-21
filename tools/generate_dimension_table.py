import os
import json
import re
import numpy as np
from pathlib import Path
import pandas as pd

# Configuration
DATA_DIR = Path('data/critical_thinking')
ASSIGNMENTS = ['a1', 'a2', 'a3']
WRITERS = ['chatgpt', 'gemini', 'claude', 'grok']
DIMENSIONS = [
    'Explanation of issues',
    'Evidence',
    'Influence of context and assumptions',
    "Student's position",
    'Conclusions and related outcomes'
]
SHORT_DIMS = ['Issues', 'Evidence', 'Context', 'Position', 'Conclusion']

def parse_dimension_scores(text):
    """Parse rubric dimension scores from text."""
    scores = {}
    for dim in DIMENSIONS:
        escaped_dim = re.escape(dim)
        patterns = [
            escaped_dim + r'.*?(\d+(?:\.\d+)?)',
            r'\*\*' + escaped_dim + r':\*\*\s*(\d+(?:\.\d+)?)',
            r'\|.*?'+ escaped_dim + r'.*?\|\s*(\d+(?:\.\d+)?)\s*\|',
            r'- \*\*' + escaped_dim + r'\s*:?\*\*\s*:?\s*(\d+(?:\.\d+)?)'
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

def load_data(assignment, prompt_num=2):
    """
    Load data for a specific assignment and prompt.
    Returns a nested dict: data[writer][grader] = {'gen': {dims...}, 'tune': {dims...}}
    """
    data = {}
    p_suffix = f'_p{prompt_num}'

    # Initialize structure
    for w in WRITERS:
        data[w] = {}
        for g in WRITERS:
            if w == g: continue
            data[w][g] = {'gen': None, 'tune': None}

    # Iterate files
    for filename in os.listdir(DATA_DIR):
        if not filename.endswith('.json'):
            continue
        if not filename.startswith(f'{assignment}_'):
            continue
        if p_suffix not in filename:
            continue
        if '_score_' not in filename:
            continue

        parts = filename.replace('.json', '').split('_')
        try:
            if 'gen' in parts:
                type_idx = parts.index('gen')
                essay_type = 'gen'
            elif 'tune' in parts:
                type_idx = parts.index('tune')
                essay_type = 'tune'
            else:
                continue

            writer = parts[type_idx + 1]
            if 'score' in parts:
                score_idx = parts.index('score')
                grader = parts[score_idx + 1]
            else:
                continue
            
            if writer not in WRITERS or grader not in WRITERS:
                continue
            
            if writer == grader:
                continue

            filepath = DATA_DIR / filename
            with open(filepath, 'r') as f:
                content = json.load(f)
            
            result_text = content.get('result', '')
            scores = parse_dimension_scores(result_text)
            
            data[writer][grader][essay_type] = scores

        except Exception as e:
            continue

    return data

def generate_table(prompt_num=2):
    print(f"\n# Consensus Dimension Scores (Prompt {prompt_num})")
    print(f"Values are the average score (0-4) given by the 3 other models acting as graders.\n")

    for assignment in ASSIGNMENTS:
        print(f"## Assignment: {assignment.upper()}")
        data = load_data(assignment, prompt_num)
        
        # Prepare rows for DataFrame
        rows = []
        
        for writer in WRITERS:
            # Calculate averages across graders
            graders = [g for g in WRITERS if g != writer]
            
            # GEN SCORES
            gen_totals = np.zeros(len(DIMENSIONS))
            gen_counts = np.zeros(len(DIMENSIONS))
            
            # TUNE SCORES
            tune_totals = np.zeros(len(DIMENSIONS))
            tune_counts = np.zeros(len(DIMENSIONS))

            for grader in graders:
                pair = data[writer][grader]
                
                # Sum Gen
                if pair['gen']:
                    for i, dim in enumerate(DIMENSIONS):
                        gen_totals[i] += pair['gen'].get(dim, 0)
                        gen_counts[i] += 1
                
                # Sum Tune
                if pair['tune']:
                    for i, dim in enumerate(DIMENSIONS):
                        tune_totals[i] += pair['tune'].get(dim, 0)
                        tune_counts[i] += 1
            
            # Calculate Means
            # Avoid division by zero
            gen_counts[gen_counts == 0] = 1
            tune_counts[tune_counts == 0] = 1
            
            gen_means = gen_totals / gen_counts
            tune_means = tune_totals / tune_counts
            
            # Format row
            # Writer | Stage | Issues | Evidence | Context | Position | Conclusion | Total (Avg)
            
            # Row for Gen
            row_gen = {
                'Writer': writer.capitalize(),
                'Stage': 'Gen',
                'Issues': f"{gen_means[0]:.2f}",
                'Evidence': f"{gen_means[1]:.2f}",
                'Context': f"{gen_means[2]:.2f}",
                'Position': f"{gen_means[3]:.2f}",
                'Conclusion': f"{gen_means[4]:.2f}",
                'Avg Total': f"{np.sum(gen_means):.2f}"
            }
            rows.append(row_gen)
            
            # Row for Tune
            row_tune = {
                'Writer': writer.capitalize(),
                'Stage': 'Tune',
                'Issues': f"{tune_means[0]:.2f}",
                'Evidence': f"{tune_means[1]:.2f}",
                'Context': f"{tune_means[2]:.2f}",
                'Position': f"{tune_means[3]:.2f}",
                'Conclusion': f"{tune_means[4]:.2f}",
                'Avg Total': f"{np.sum(tune_means):.2f}"
            }
            rows.append(row_tune)

        df = pd.DataFrame(rows)
        print(df.to_markdown(index=False))
        print("\n")

if __name__ == "__main__":
    generate_table(prompt_num=2)
