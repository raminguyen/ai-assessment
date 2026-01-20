import os
import json
import re
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pathlib import Path

# Configuration
DATA_DIR = Path(__file__).resolve().parent.parent.parent / 'data' / 'critical_thinking'
OUTPUT_DIR = Path('src/visualization/rubric_plots')
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

# Colors for writers (for labels/grouping)
WRITER_COLORS = {
    'chatgpt': '#3498DB',
    'gemini': '#E67E22',
    'claude': '#2ECC71',
    'grok': '#9B59B6'
}

def parse_dimension_scores(text):
    """Parse rubric dimension scores from text. Adapted from score_chart.py"""
    scores = {}
    for dim in DIMENSIONS:
        # Try multiple patterns
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
            # Finding writer and grader indices
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
            # Silently skip file errors to avoid clutter
            continue

    return data

def _draw_avg_progression_on_axis(ax, data, writer):
    """Helper to draw avg progression for a single writer on an axis."""
    writer_color = WRITER_COLORS[writer]
    x_indices = np.arange(len(DIMENSIONS))
    
    # Aggregate scores
    gen_totals = np.zeros(len(DIMENSIONS))
    tune_totals = np.zeros(len(DIMENSIONS))
    counts = np.zeros(len(DIMENSIONS))
    
    graders = [g for g in WRITERS if g != writer]
    for grader in graders:
        pair = data[writer][grader]
        if pair['gen'] and pair['tune']:
            for d_i, dim in enumerate(DIMENSIONS):
                gen_totals[d_i] += pair['gen'].get(dim, 0)
                tune_totals[d_i] += pair['tune'].get(dim, 0)
                counts[d_i] += 1
    
    # Check if we have data, avoid division by zero
    if np.all(counts == 0):
        # No data to plot for this writer
        ax.text(0.5, 0.5, "No Data", ha='center', va='center', color='gray')
        ax.set_xticks(x_indices)
        ax.set_xticklabels(SHORT_DIMS, rotation=45, ha='right', fontsize=9)
        ax.set_ylim(0, 5.0)
        return

    counts[counts == 0] = 1
    gen_avg = gen_totals / counts
    tune_avg = tune_totals / counts
    
    # Calculate Total Score Difference (Summary Statistic)
    sum_gen = np.sum(gen_avg)
    sum_tune = np.sum(tune_avg)
    overall_delta = sum_tune - sum_gen
    
    # Plot
    line_gen, = ax.plot(x_indices, gen_avg, color='gray', linestyle='--', marker='o', alpha=0.6, label='Gen')
    line_tune, = ax.plot(x_indices, tune_avg, color=writer_color, linewidth=2.5, marker='o', markersize=8, label='Tune')
    ax.fill_between(x_indices, gen_avg, tune_avg, color=writer_color, alpha=0.1)
    
    # Annotate deltas
    for d_i, (g, t) in enumerate(zip(gen_avg, tune_avg)):
        diff = t - g
        if abs(diff) > 0.1:
            txt = f"{diff:+.1f}"
            y_pos = max(g, t) + 0.15
            ax.text(d_i, y_pos, txt, ha='center', va='bottom', fontsize=8, 
                    fontweight='bold', color=('#27AE60' if diff > 0 else '#C0392B'))

    # Add Summary Statistic Box
    stat_color = '#27AE60' if overall_delta > 0 else ('#C0392B' if overall_delta < -0.01 else 'gray')
    stat_text = f"Diff: {overall_delta:+.1f}"
    ax.text(0.02, 0.95, stat_text, transform=ax.transAxes, fontsize=9, fontweight='bold',
            color=stat_color, verticalalignment='top', bbox=dict(facecolor='white', alpha=0.8, edgecolor=stat_color, boxstyle='round,pad=0.3'))

    ax.set_xticks(x_indices)
    ax.set_xticklabels(SHORT_DIMS, rotation=45, ha='right', fontsize=9)
    ax.set_ylim(0, 5.0)
    ax.grid(True, linestyle='--', alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    ax.legend(handles=[line_gen, line_tune], loc='upper right', fontsize=8, frameon=True, facecolor='white', framealpha=0.9)

def plot_combined_average(prompt_num=2):
    """Combines Average Progression into a 3x4 grid (Rows=Assignments, Cols=Writers)."""
    fig, axes = plt.subplots(3, 4, figsize=(22, 14), sharex=True, sharey=True)
    fig.suptitle(f'Rubric Progression by Average Score by Dimension: A1, A2, A3 (Prompt {prompt_num})\nTitle = Writer | Average score from other 3 grader models', fontsize=22, fontweight='bold', y=0.98)
    
    for row_idx, assignment in enumerate(ASSIGNMENTS):
        data = load_data(assignment, prompt_num)
        
        # Row Label
        axes[row_idx, 0].set_ylabel(f'{assignment.upper()}\nAvg Score', fontsize=12, fontweight='bold')
        
        for col_idx, writer in enumerate(WRITERS):
            ax = axes[row_idx, col_idx]
            
            # Column Title (Top row only)
            if row_idx == 0:
                ax.set_title(f"WRITER: {writer.upper()}", fontsize=14, fontweight='bold', color=WRITER_COLORS[writer], pad=25)
                ax.text(0.5, 1.05, "(Average score from other 3 grader models)", transform=ax.transAxes, 
                        ha='center', fontsize=9, style='italic', color='#555555')
            
            _draw_avg_progression_on_axis(ax, data, writer)
            
    # Add a global footer/caption
    fig.text(0.5, 0.02, "Total Difference = Sum of (Tune Average Total - Gen Average Total) across all dimensions.", 
             ha='center', fontsize=12, style='italic', bbox=dict(facecolor='white', alpha=0.5, edgecolor='gray', boxstyle='round,pad=0.5'))

    plt.tight_layout()
    plt.subplots_adjust(top=0.88, left=0.08, bottom=0.08)
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / f'all_assignments_p{prompt_num}_rubric_avg_progression.png'
    plt.savefig(out_path, dpi=1500)
    print(f"Saved combined average plot to {out_path}")
    plt.close()

def visualize_dataset_as_png(assignment='a1', prompt_num=2, output_filename=None):
    """
    Generates a pretty table of the dataset for a specific assignment and prompt.
    """
    print(f"Generating dataset table for {assignment}, prompt {prompt_num}...")
    data = load_data(assignment, prompt_num)
    
    rows = []
    for writer in WRITERS:
        for grader in WRITERS:
            if writer == grader:
                continue
            pair_data = data[writer][grader]
            
            for essay_type in ['gen', 'tune']:
                scores = pair_data.get(essay_type)
                if scores:
                    row = {
                        'Writer': writer,
                        'Grader': grader,
                        'Type': essay_type,
                    }
                    for dim in DIMENSIONS:
                        short_dim = dim.split(' ')[0] 
                        row[short_dim] = scores.get(dim, 0.0)
                    rows.append(row)
    
    if not rows:
        print("No data found for table generation!")
        return

    df = pd.DataFrame(rows)
    
    # Sort for better readability
    df = df.sort_values(by=['Writer', 'Grader', 'Type'])

    # Setup plotting
    num_rows = len(df)
    # Calculate figure size: roughly 0.5 inch per row + headers
    fig_height = max(6, num_rows * 0.4 + 2)
    fig_width = 14
    
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    ax.axis('off')
    
    # Prepare table data
    # Format floats
    display_df = df.copy()
    dim_cols = [c for c in df.columns if c not in ['Writer', 'Grader', 'Type']]
    for col in dim_cols:
        display_df[col] = display_df[col].apply(lambda x: f"{x:.2f}")

    table_data = [display_df.columns.tolist()] + display_df.values.tolist()
    
    # Create table
    table = ax.table(cellText=table_data, 
                     colLabels=None, 
                     cellLoc='center', 
                     loc='center')
    
    # Styling
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 1.8) # Increase row height
    
    # Colors
    header_color = '#40466e'
    header_text_color = '#ffffff'
    row_colors = ['#f1f1f2', '#ffffff']
    edge_color = '#bcbcbc'

    for k, cell in table.get_celld().items():
        row, col = k
        cell.set_edgecolor(edge_color)
        
        # Header
        if row == 0:
            cell.set_text_props(weight='bold', color=header_text_color)
            cell.set_facecolor(header_color)
        else:
            # Body
            cell.set_facecolor(row_colors[row % 2])
            cell.set_text_props(color='black')
            
            # Optional: Color code 'Type' (Gen vs Tune)
            if display_df.columns[col] == 'Type':
                val = table_data[row][col]
                if val == 'tune':
                    cell.set_text_props(color='#d35400', weight='bold') # Dark Orange
                elif val == 'gen':
                    cell.set_text_props(color='#2980b9', weight='bold') # Blue

    # Add title
    plt.title(f"Dataset Preview: Assignment {assignment.upper()} - Prompt {prompt_num}", 
              fontweight="bold", fontsize=16, pad=20, color='#2c3e50')
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if output_filename is None:
        output_filename = f'{assignment}_p{prompt_num}_dataset_table.png'
    output_path = OUTPUT_DIR / output_filename
    
    plt.savefig(output_path, bbox_inches='tight', dpi=1500)
    print(f"Dataset table saved to {output_path}")
    plt.close()

if __name__ == "__main__":
    print("Generating Rubric visualizations...")
    
    # 1. Combined Average Progression plots
    plot_combined_average(prompt_num=2)
    plot_combined_average(prompt_num=1)

    # 2. Dataset Tables (Pretty PNGs)
    visualize_dataset_as_png(assignment='a1', prompt_num=2)
    # You can uncomment or add loops here to generate tables for other assignments if needed
    # for assign in ASSIGNMENTS:
    #     visualize_dataset_as_png(assignment=assign, prompt_num=2)
        
    print("All visualizations completed.")
