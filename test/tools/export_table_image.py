import os
import json
import re
import numpy as np
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

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

def render_mpl_table(data, col_width=3.0, row_height=0.625, font_size=12,
                     header_color='#40466e', row_colors=['#f1f1f2', 'w'], edge_color='w',
                     bbox=[0, 0, 1, 1], header_columns=0,
                     ax=None, **kwargs):
    if ax is None:
        size = (np.array(data.shape[::-1]) + np.array([0, 1])) * np.array([col_width, row_height])
        fig, ax = plt.subplots(figsize=size)
        ax.axis('off')

    mpl_table = ax.table(cellText=data.values, bbox=bbox, colLabels=data.columns, **kwargs)

    mpl_table.auto_set_font_size(False)
    mpl_table.set_fontsize(font_size)

    for k, cell in mpl_table._cells.items():
        cell.set_edgecolor(edge_color)
        if k[0] == 0 or k[1] < header_columns:
            cell.set_text_props(weight='bold', color='w')
            cell.set_facecolor(header_color)
        else:
            cell.set_facecolor(row_colors[k[0]%len(row_colors) ])
    return ax

def save_table_image(prompt_num=2):
    output_dir = Path('src/visualization/rubric_plots')
    output_dir.mkdir(parents=True, exist_ok=True)

    for assignment in ASSIGNMENTS:
        print(f"Generating table image for {assignment.upper()}...")
        data = load_data(assignment, prompt_num)
        
        # Prepare rows for DataFrame
        rows = []
        
        for writer in WRITERS:
            graders = [g for g in WRITERS if g != writer]
            
            gen_totals = np.zeros(len(DIMENSIONS))
            gen_counts = np.zeros(len(DIMENSIONS))
            tune_totals = np.zeros(len(DIMENSIONS))
            tune_counts = np.zeros(len(DIMENSIONS))

            for grader in graders:
                pair = data[writer][grader]
                if pair['gen']:
                    for i, dim in enumerate(DIMENSIONS):
                        gen_totals[i] += pair['gen'].get(dim, 0)
                        gen_counts[i] += 1
                if pair['tune']:
                    for i, dim in enumerate(DIMENSIONS):
                        tune_totals[i] += pair['tune'].get(dim, 0)
                        tune_counts[i] += 1
            
            gen_counts[gen_counts == 0] = 1
            tune_counts[tune_counts == 0] = 1
            gen_means = gen_totals / gen_counts
            tune_means = tune_totals / tune_counts
            
            row_gen = {
                'Writer': writer.capitalize(),
                'Stage': 'Gen',
                'Issues': f"{gen_means[0]:.2f}",
                'Evidence': f"{gen_means[1]:.2f}",
                'Context': f"{gen_means[2]:.2f}",
                'Position': f"{gen_means[3]:.2f}",
                'Conclusion': f"{gen_means[4]:.2f}",
                'Total': f"{np.sum(gen_means):.2f}"
            }
            rows.append(row_gen)
            
            row_tune = {
                'Writer': writer.capitalize(),
                'Stage': 'Tune',
                'Issues': f"{tune_means[0]:.2f}",
                'Evidence': f"{tune_means[1]:.2f}",
                'Context': f"{tune_means[2]:.2f}",
                'Position': f"{tune_means[3]:.2f}",
                'Conclusion': f"{tune_means[4]:.2f}",
                'Total': f"{np.sum(tune_means):.2f}"
            }
            rows.append(row_tune)

        df = pd.DataFrame(rows)
        
        # Plotting
        fig, ax = plt.subplots(figsize=(14, 6)) # Adjust size as needed
        ax.axis('off')
        ax.set_title(f"Consensus Scores - Assignment {assignment.upper()} (Prompt {prompt_num})", 
                     fontweight='bold', fontsize=16, pad=20)
        
        render_mpl_table(df, header_columns=0, col_width=2.5, ax=ax)
        
        out_path = output_dir / f"table_{assignment}_p{prompt_num}_consensus.png"
        plt.tight_layout()
        plt.savefig(out_path, bbox_inches='tight', dpi=300)
        print(f"Saved: {out_path}")
        plt.close()

if __name__ == "__main__":
    save_table_image(prompt_num=2)
