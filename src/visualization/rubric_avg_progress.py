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

# Flexible patterns for dimension names that handle variations in grader outputs
# Maps canonical dimension name to regex pattern that matches variations
# Note: Some graders use curly apostrophe (U+2019) vs straight apostrophe (')
DIMENSION_PATTERNS = {
    'Explanation of issues': r'Explanation of issues',
    'Evidence': r'Evidence(?:\s*\([^)]*\))?',
    'Influence of context and assumptions': r'Influence of context (?:and|&) assumptions',
    "Student's position": r"Student['\u2019]s position(?:\s*\([^)]*\))?",
    'Conclusions and related outcomes': r'Conclusions (?:and|&) related outcomes',
}

# Colors for writers (for labels/grouping)
WRITER_COLORS = {
    'chatgpt': '#3498DB',
    'gemini': '#E67E22',
    'claude': '#2ECC71',
    'grok': '#9B59B6'
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
    plt.savefig(out_path, dpi=600)
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
    
    plt.savefig(output_path, bbox_inches='tight', dpi=600)
    print(f"Dataset table saved to {output_path}")
    plt.close()

def create_gen_tune_summary(prompt_num=2):
    """
    Create summary table comparing GEN vs TUNE for each writer (averaged across assignments).
    Returns DataFrame with Total/20 scores.
    """
    all_rows = []

    for assignment in ASSIGNMENTS:
        data = load_data(assignment, prompt_num)

        for writer in WRITERS:
            graders = [g for g in WRITERS if g != writer]

            # Collect scores from all graders
            gen_scores = {dim: [] for dim in DIMENSIONS}
            tune_scores = {dim: [] for dim in DIMENSIONS}

            for grader in graders:
                pair = data[writer][grader]
                if pair['gen']:
                    for dim in DIMENSIONS:
                        gen_scores[dim].append(pair['gen'].get(dim, 0))
                if pair['tune']:
                    for dim in DIMENSIONS:
                        tune_scores[dim].append(pair['tune'].get(dim, 0))

            # Calculate averages
            for essay_type, scores_dict in [('GEN', gen_scores), ('TUNE', tune_scores)]:
                row = {
                    'Assignment': assignment.upper(),
                    'Writer': writer.upper(),
                    'Type': essay_type,
                }
                total = 0
                for i, dim in enumerate(DIMENSIONS):
                    if scores_dict[dim]:
                        avg = np.mean(scores_dict[dim])
                        row[SHORT_DIMS[i]] = round(avg, 2)
                        total += avg
                    else:
                        row[SHORT_DIMS[i]] = 0.0

                row['Total/20'] = round(total, 2)
                all_rows.append(row)

    return pd.DataFrame(all_rows)


def create_overall_gen_tune_summary(prompt_num=2):
    """Create overall summary comparing GEN vs TUNE (averaged across all writers and assignments)."""
    df = create_gen_tune_summary(prompt_num)

    summary = []
    for essay_type in ['GEN', 'TUNE']:
        type_data = df[df['Type'] == essay_type]
        row = {'Type': essay_type, 'N': len(type_data)}
        for dim in SHORT_DIMS:
            row[dim] = round(type_data[dim].mean(), 2)
        row['Total/20'] = round(type_data['Total/20'].mean(), 2)
        summary.append(row)

    return pd.DataFrame(summary)


def export_gen_tune_table(df, title, output_filename, highlight_type='TUNE'):
    """Export GEN vs TUNE comparison table as PNG."""
    num_rows = len(df)
    fig_height = max(3, num_rows * 0.6 + 2)
    fig_width = 14

    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    ax.axis('off')

    # Format display data
    display_df = df.copy()
    for col in display_df.columns:
        if col not in ['Assignment', 'Writer', 'Type', 'N']:
            display_df[col] = display_df[col].apply(lambda x: f"{x:.2f}")

    table_data = [display_df.columns.tolist()] + display_df.values.tolist()

    table = ax.table(
        cellText=table_data,
        colLabels=None,
        cellLoc='center',
        loc='center'
    )

    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 2.0)

    # Colors
    header_color = '#2c3e50'
    header_text_color = '#ffffff'
    highlight_color = '#d4edda'
    highlight_text_color = '#155724'
    row_colors = ['#f8f9fa', '#ffffff']
    edge_color = '#dee2e6'

    type_col_idx = display_df.columns.tolist().index('Type')

    for k, cell in table.get_celld().items():
        row, col = k
        cell.set_edgecolor(edge_color)
        cell.set_linewidth(1.5)

        if row == 0:
            cell.set_text_props(weight='bold', color=header_text_color)
            cell.set_facecolor(header_color)
        else:
            is_highlight = table_data[row][type_col_idx] == highlight_type

            if is_highlight:
                cell.set_facecolor(highlight_color)
                cell.set_text_props(color=highlight_text_color, weight='bold')
            else:
                cell.set_facecolor(row_colors[row % 2])
                cell.set_text_props(color='#212529')

    plt.title(title, fontweight="bold", fontsize=16, pad=20, color='#2c3e50')

    fig.text(0.5, 0.02, f"* {highlight_type} highlighted in green - shows improvement from tuning",
             ha='center', fontsize=11, fontweight='bold', color='#155724',
             bbox=dict(facecolor='#d4edda', alpha=0.9, edgecolor='#155724', boxstyle='round,pad=0.4'))

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / output_filename

    plt.savefig(output_path, bbox_inches='tight', dpi=300, facecolor='white')
    print(f"Table saved to {output_path}")
    plt.close()


def export_gen_tune_chart(summary_df, prompt_num, output_filename=None):
    """Create bar chart comparing GEN vs TUNE."""
    if output_filename is None:
        output_filename = f'gen_tune_comparison_p{prompt_num}.png'

    fig, ax = plt.subplots(figsize=(10, 6))

    types = ['GEN', 'TUNE']
    x = np.arange(len(types))
    colors = ['#e74c3c', '#27ae60']

    totals = [summary_df[summary_df['Type'] == t]['Total/20'].values[0] for t in types]

    bars = ax.bar(x, totals, color=colors, edgecolor='white', linewidth=2, width=0.5)

    for bar, val in zip(bars, totals):
        ax.annotate(f'{val:.2f}',
                   xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                   xytext=(0, 5), textcoords="offset points",
                   ha='center', va='bottom', fontsize=14, fontweight='bold')

    # Show improvement
    improvement = totals[1] - totals[0]
    pct_improvement = (improvement / totals[0]) * 100 if totals[0] > 0 else 0

    ax.annotate(f'+{improvement:.2f} ({pct_improvement:+.1f}%)',
               xy=(0.5, max(totals) + 0.5), xycoords=('axes fraction', 'data'),
               ha='center', fontsize=12, fontweight='bold', color='#155724',
               bbox=dict(facecolor='#d4edda', edgecolor='#155724', boxstyle='round,pad=0.3'))

    ax.set_xlabel('Essay Type', fontsize=13, fontweight='bold')
    ax.set_ylabel('Total Score (out of 20)', fontsize=13, fontweight='bold')
    ax.set_title(f'GEN vs TUNE Comparison (Prompt {prompt_num})\nTUNE shows improvement over GEN',
                 fontsize=14, fontweight='bold', color='#2c3e50', pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(['GEN\n(Original)', 'TUNE\n(Improved)'], fontsize=12, fontweight='bold')
    ax.set_ylim(0, 22)
    ax.axhline(y=20, color='gray', linestyle='--', alpha=0.5)
    ax.grid(axis='y', linestyle='--', alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / output_filename
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, facecolor='white')
    print(f"Chart saved to {output_path}")
    plt.close()


def create_p1_vs_p2_summary():
    """Create simplified summary comparing P1 vs P2 (aggregated across all writers/assignments)."""
    summary = []

    for p_num in [1, 2]:
        overall = create_overall_gen_tune_summary(prompt_num=p_num)
        for _, row in overall.iterrows():
            summary.append({
                'Prompt': f'P{p_num}',
                'Type': row['Type'],
                'Issues': row['Issues'],
                'Evidence': row['Evidence'],
                'Context': row['Context'],
                'Position': row['Position'],
                'Conclusion': row['Conclusion'],
                'Total/20': row['Total/20'],
            })

    return pd.DataFrame(summary)


def export_p1_vs_p2_summary_table():
    """Export simplified P1 vs P2 comparison table."""
    df = create_p1_vs_p2_summary()

    fig, ax = plt.subplots(figsize=(14, 5))
    ax.axis('off')

    # Format display data
    display_df = df.copy()
    for col in display_df.columns:
        if col not in ['Prompt', 'Type']:
            display_df[col] = display_df[col].apply(lambda x: f"{x:.2f}")

    table_data = [display_df.columns.tolist()] + display_df.values.tolist()

    table = ax.table(
        cellText=table_data,
        colLabels=None,
        cellLoc='center',
        loc='center'
    )

    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1, 2.2)

    # Colors
    header_color = '#2c3e50'
    header_text_color = '#ffffff'
    p2_tune_color = '#d4edda'  # Best - P2 TUNE
    p2_tune_text = '#155724'
    p1_color = '#f8d7da'  # P1 rows
    p1_text = '#721c24'
    p2_gen_color = '#cce5ff'
    p2_gen_text = '#004085'
    edge_color = '#dee2e6'

    prompt_col_idx = 0
    type_col_idx = 1

    for k, cell in table.get_celld().items():
        row, col = k
        cell.set_edgecolor(edge_color)
        cell.set_linewidth(2)

        if row == 0:
            cell.set_text_props(weight='bold', color=header_text_color)
            cell.set_facecolor(header_color)
        else:
            prompt = table_data[row][prompt_col_idx]
            etype = table_data[row][type_col_idx]

            if prompt == 'P2' and etype == 'TUNE':
                cell.set_facecolor(p2_tune_color)
                cell.set_text_props(color=p2_tune_text, weight='bold')
            elif prompt == 'P2' and etype == 'GEN':
                cell.set_facecolor(p2_gen_color)
                cell.set_text_props(color=p2_gen_text)
            else:  # P1
                cell.set_facecolor(p1_color)
                cell.set_text_props(color=p1_text)

    plt.title("P1 vs P2 Summary Comparison\nP2 TUNE (green) = Best Performance",
              fontweight="bold", fontsize=16, pad=20, color='#2c3e50')

    # Calculate improvement
    p1_tune = df[(df['Prompt'] == 'P1') & (df['Type'] == 'TUNE')]['Total/20'].values[0]
    p2_tune = df[(df['Prompt'] == 'P2') & (df['Type'] == 'TUNE')]['Total/20'].values[0]
    diff = p2_tune - p1_tune

    if diff > 0:
        note = f"P2 TUNE ({p2_tune:.2f}) vs P1 TUNE ({p1_tune:.2f}) = P2 is WORSE by {abs(diff):.2f}"
        note_color = '#721c24'
    else:
        note = f"P2 TUNE ({p2_tune:.2f}) vs P1 TUNE ({p1_tune:.2f}) = P1 is better by {abs(diff):.2f}"
        note_color = '#721c24'

    fig.text(0.5, 0.02, note,
             ha='center', fontsize=11, fontweight='bold', color=note_color,
             bbox=dict(facecolor='#f8d7da', alpha=0.9, edgecolor=note_color, boxstyle='round,pad=0.4'))

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / 'p1_vs_p2_summary.png'

    plt.savefig(output_path, bbox_inches='tight', dpi=300, facecolor='white')
    print(f"P1 vs P2 summary saved to {output_path}")
    plt.close()

    return df


def create_p1_vs_p2_by_writer_summary():
    """Create writer-level summary comparing P1 vs P2."""
    summary = []

    for p_num in [1, 2]:
        detail_df = create_gen_tune_summary(prompt_num=p_num)

        # Aggregate by writer (average across assignments)
        for writer in ['CHATGPT', 'GEMINI', 'CLAUDE', 'GROK']:
            for etype in ['GEN', 'TUNE']:
                writer_data = detail_df[(detail_df['Writer'] == writer) & (detail_df['Type'] == etype)]
                if len(writer_data) == 0:
                    continue

                row = {
                    'Prompt': f'P{p_num}',
                    'Writer': writer,
                    'Type': etype,
                }
                for dim in SHORT_DIMS:
                    row[dim] = round(writer_data[dim].mean(), 2)
                row['Total/20'] = round(writer_data['Total/20'].mean(), 2)
                summary.append(row)

    return pd.DataFrame(summary)


def create_p1_vs_p2_compact_summary():
    """Create compact side-by-side P1 vs P2 comparison by writer (averaged)."""
    df = create_p1_vs_p2_by_writer_summary()

    rows = []
    for writer in ['CHATGPT', 'CLAUDE', 'GEMINI', 'GROK']:
        p1_gen = df[(df['Writer'] == writer) & (df['Prompt'] == 'P1') & (df['Type'] == 'GEN')]['Total/20'].values
        p1_tune = df[(df['Writer'] == writer) & (df['Prompt'] == 'P1') & (df['Type'] == 'TUNE')]['Total/20'].values
        p2_gen = df[(df['Writer'] == writer) & (df['Prompt'] == 'P2') & (df['Type'] == 'GEN')]['Total/20'].values
        p2_tune = df[(df['Writer'] == writer) & (df['Prompt'] == 'P2') & (df['Type'] == 'TUNE')]['Total/20'].values

        p1_gen_val = p1_gen[0] if len(p1_gen) > 0 else 0
        p1_tune_val = p1_tune[0] if len(p1_tune) > 0 else 0
        p2_gen_val = p2_gen[0] if len(p2_gen) > 0 else 0
        p2_tune_val = p2_tune[0] if len(p2_tune) > 0 else 0

        # Calculate differences
        gen_diff = p2_gen_val - p1_gen_val
        tune_diff = p2_tune_val - p1_tune_val

        rows.append({
            'Writer': writer,
            'P1 GEN': p1_gen_val,
            'P2 GEN': p2_gen_val,
            'GEN Diff': gen_diff,
            'GEN Winner': 'P2' if gen_diff > 0 else ('P1' if gen_diff < 0 else '='),
            'P1 TUNE': p1_tune_val,
            'P2 TUNE': p2_tune_val,
            'TUNE Diff': tune_diff,
            'TUNE Winner': 'P2' if tune_diff > 0 else ('P1' if tune_diff < 0 else '='),
        })

    return pd.DataFrame(rows)


def create_p1_vs_p2_by_assignment_writer():
    """Create P1 vs P2 comparison by writer for EACH assignment (no averaging)."""
    rows = []

    for assignment in ASSIGNMENTS:
        df_p1 = create_gen_tune_summary(prompt_num=1)
        df_p2 = create_gen_tune_summary(prompt_num=2)

        for writer in ['CHATGPT', 'CLAUDE', 'GEMINI', 'GROK']:
            # Get P1 data for this assignment and writer
            p1_gen = df_p1[(df_p1['Assignment'] == assignment.upper()) &
                           (df_p1['Writer'] == writer) &
                           (df_p1['Type'] == 'GEN')]['Total/20'].values
            p1_tune = df_p1[(df_p1['Assignment'] == assignment.upper()) &
                            (df_p1['Writer'] == writer) &
                            (df_p1['Type'] == 'TUNE')]['Total/20'].values

            # Get P2 data for this assignment and writer
            p2_gen = df_p2[(df_p2['Assignment'] == assignment.upper()) &
                           (df_p2['Writer'] == writer) &
                           (df_p2['Type'] == 'GEN')]['Total/20'].values
            p2_tune = df_p2[(df_p2['Assignment'] == assignment.upper()) &
                            (df_p2['Writer'] == writer) &
                            (df_p2['Type'] == 'TUNE')]['Total/20'].values

            p1_gen_val = p1_gen[0] if len(p1_gen) > 0 else 0
            p1_tune_val = p1_tune[0] if len(p1_tune) > 0 else 0
            p2_gen_val = p2_gen[0] if len(p2_gen) > 0 else 0
            p2_tune_val = p2_tune[0] if len(p2_tune) > 0 else 0

            # Calculate differences
            gen_diff = p2_gen_val - p1_gen_val
            tune_diff = p2_tune_val - p1_tune_val

            rows.append({
                'Assignment': assignment.upper(),
                'Writer': writer,
                'P1 GEN': p1_gen_val,
                'P2 GEN': p2_gen_val,
                'GEN Diff': gen_diff,
                'GEN Win': 'P2' if gen_diff > 0 else ('P1' if gen_diff < 0 else '='),
                'P1 TUNE': p1_tune_val,
                'P2 TUNE': p2_tune_val,
                'TUNE Diff': tune_diff,
                'TUNE Win': 'P2' if tune_diff > 0 else ('P1' if tune_diff < 0 else '='),
            })

    return pd.DataFrame(rows)


def export_p1_vs_p2_by_assignment_table():
    """Export P1 vs P2 comparison by writer for each assignment."""
    df = create_p1_vs_p2_by_assignment_writer()

    fig, ax = plt.subplots(figsize=(18, 10))
    ax.axis('off')

    # Format display data
    display_df = df.copy()
    for col in ['P1 GEN', 'P2 GEN', 'GEN Diff', 'P1 TUNE', 'P2 TUNE', 'TUNE Diff']:
        display_df[col] = display_df[col].apply(lambda x: f"{x:+.2f}" if 'Diff' in col else f"{x:.2f}")

    table_data = [display_df.columns.tolist()] + display_df.values.tolist()

    table = ax.table(
        cellText=table_data,
        colLabels=None,
        cellLoc='center',
        loc='center'
    )

    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.8)

    # Colors
    header_color = '#2c3e50'
    header_text_color = '#ffffff'
    p2_win_color = '#d4edda'
    p2_win_text = '#155724'
    p1_win_color = '#f8d7da'
    p1_win_text = '#721c24'
    neutral_color = '#f8f9fa'
    a1_color = '#e3f2fd'
    a2_color = '#fff8e1'
    a3_color = '#f3e5f5'
    edge_color = '#dee2e6'

    col_names = display_df.columns.tolist()
    assign_col_idx = col_names.index('Assignment')

    for k, cell in table.get_celld().items():
        row, col = k
        cell.set_edgecolor(edge_color)
        cell.set_linewidth(1)

        if row == 0:
            cell.set_text_props(weight='bold', color=header_text_color)
            cell.set_facecolor(header_color)
        else:
            col_name = col_names[col]
            assignment = table_data[row][assign_col_idx]

            # Set background based on assignment
            if assignment == 'A1':
                base_color = a1_color
            elif assignment == 'A2':
                base_color = a2_color
            else:
                base_color = a3_color

            # Highlight winner columns
            if col_name in ['GEN Win', 'TUNE Win']:
                val = table_data[row][col]
                if val == 'P2':
                    cell.set_facecolor(p2_win_color)
                    cell.set_text_props(color=p2_win_text, weight='bold')
                elif val == 'P1':
                    cell.set_facecolor(p1_win_color)
                    cell.set_text_props(color=p1_win_text, weight='bold')
                else:
                    cell.set_facecolor(neutral_color)
            elif 'Diff' in col_name:
                val_str = table_data[row][col]
                if val_str.startswith('+') and float(val_str) > 0:
                    cell.set_facecolor('#d4edda')
                    cell.set_text_props(color='#155724', weight='bold')
                elif float(val_str) < 0:
                    cell.set_facecolor('#f8d7da')
                    cell.set_text_props(color='#721c24', weight='bold')
                else:
                    cell.set_facecolor(neutral_color)
            else:
                cell.set_facecolor(base_color)
                if col_name == 'Writer':
                    cell.set_text_props(weight='bold')

    plt.title("P1 vs P2 by Writer & Assignment (No Averaging)\nGreen = P2 Better | Red = P1 Better | Blue=A1, Yellow=A2, Purple=A3",
              fontweight="bold", fontsize=14, pad=20, color='#2c3e50')

    # Count winners
    gen_p2_wins = len(df[df['GEN Win'] == 'P2'])
    tune_p2_wins = len(df[df['TUNE Win'] == 'P2'])
    total = len(df)

    fig.text(0.5, 0.02, f"GEN: P2 wins {gen_p2_wins}/{total} | TUNE: P2 wins {tune_p2_wins}/{total}",
             ha='center', fontsize=12, fontweight='bold', color='#2c3e50',
             bbox=dict(facecolor='#e9ecef', alpha=0.9, edgecolor='#6c757d', boxstyle='round,pad=0.4'))

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / 'p1_vs_p2_by_assignment.png'

    plt.savefig(output_path, bbox_inches='tight', dpi=300, facecolor='white')
    print(f"P1 vs P2 by assignment table saved to {output_path}")
    plt.close()

    return df


def export_p1_vs_p2_compact_table():
    """Export compact P1 vs P2 comparison showing differences clearly."""
    df = create_p1_vs_p2_compact_summary()

    fig, ax = plt.subplots(figsize=(16, 5))
    ax.axis('off')

    # Format display data
    display_df = df.copy()
    for col in ['P1 GEN', 'P2 GEN', 'GEN Diff', 'P1 TUNE', 'P2 TUNE', 'TUNE Diff']:
        display_df[col] = display_df[col].apply(lambda x: f"{x:+.2f}" if 'Diff' in col else f"{x:.2f}")

    table_data = [display_df.columns.tolist()] + display_df.values.tolist()

    table = ax.table(
        cellText=table_data,
        colLabels=None,
        cellLoc='center',
        loc='center'
    )

    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 2.2)

    # Colors
    header_color = '#2c3e50'
    header_text_color = '#ffffff'
    p2_win_color = '#d4edda'
    p2_win_text = '#155724'
    p1_win_color = '#f8d7da'
    p1_win_text = '#721c24'
    neutral_color = '#f8f9fa'
    edge_color = '#dee2e6'

    col_names = display_df.columns.tolist()

    for k, cell in table.get_celld().items():
        row, col = k
        cell.set_edgecolor(edge_color)
        cell.set_linewidth(1.5)

        if row == 0:
            cell.set_text_props(weight='bold', color=header_text_color)
            cell.set_facecolor(header_color)
        else:
            col_name = col_names[col]

            # Highlight winner columns
            if col_name == 'GEN Winner':
                val = table_data[row][col]
                if val == 'P2':
                    cell.set_facecolor(p2_win_color)
                    cell.set_text_props(color=p2_win_text, weight='bold')
                elif val == 'P1':
                    cell.set_facecolor(p1_win_color)
                    cell.set_text_props(color=p1_win_text, weight='bold')
                else:
                    cell.set_facecolor(neutral_color)
            elif col_name == 'TUNE Winner':
                val = table_data[row][col]
                if val == 'P2':
                    cell.set_facecolor(p2_win_color)
                    cell.set_text_props(color=p2_win_text, weight='bold')
                elif val == 'P1':
                    cell.set_facecolor(p1_win_color)
                    cell.set_text_props(color=p1_win_text, weight='bold')
                else:
                    cell.set_facecolor(neutral_color)
            elif 'Diff' in col_name:
                # Color diff based on positive/negative
                val_str = table_data[row][col]
                if val_str.startswith('+') and float(val_str) > 0:
                    cell.set_facecolor('#d4edda')
                    cell.set_text_props(color='#155724', weight='bold')
                elif float(val_str) < 0:
                    cell.set_facecolor('#f8d7da')
                    cell.set_text_props(color='#721c24', weight='bold')
                else:
                    cell.set_facecolor(neutral_color)
            elif 'P2' in col_name:
                cell.set_facecolor('#cce5ff')
                cell.set_text_props(color='#004085')
            elif 'P1' in col_name:
                cell.set_facecolor('#fff3cd')
                cell.set_text_props(color='#856404')
            else:
                cell.set_facecolor(neutral_color)
                cell.set_text_props(color='#212529', weight='bold')

    plt.title("P1 vs P2 Comparison by Writer (Side-by-Side)\nGreen = P2 Better | Red = P1 Better",
              fontweight="bold", fontsize=14, pad=20, color='#2c3e50')

    # Count winners
    gen_p2_wins = len(df[df['GEN Winner'] == 'P2'])
    tune_p2_wins = len(df[df['TUNE Winner'] == 'P2'])

    fig.text(0.5, 0.02, f"GEN: P2 wins {gen_p2_wins}/4 | TUNE: P2 wins {tune_p2_wins}/4",
             ha='center', fontsize=12, fontweight='bold', color='#2c3e50',
             bbox=dict(facecolor='#e9ecef', alpha=0.9, edgecolor='#6c757d', boxstyle='round,pad=0.4'))

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / 'p1_vs_p2_compact.png'

    plt.savefig(output_path, bbox_inches='tight', dpi=300, facecolor='white')
    print(f"Compact P1 vs P2 table saved to {output_path}")
    plt.close()

    return df


def export_p1_vs_p2_by_writer_table():
    """Export P1 vs P2 comparison by writer."""
    df = create_p1_vs_p2_by_writer_summary()

    # Sort for better readability
    df = df.sort_values(by=['Writer', 'Prompt', 'Type'])

    num_rows = len(df)
    fig_height = max(6, num_rows * 0.5 + 2)
    fig_width = 16

    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    ax.axis('off')

    # Format display data
    display_df = df.copy()
    for col in display_df.columns:
        if col not in ['Prompt', 'Writer', 'Type']:
            display_df[col] = display_df[col].apply(lambda x: f"{x:.2f}")

    table_data = [display_df.columns.tolist()] + display_df.values.tolist()

    table = ax.table(
        cellText=table_data,
        colLabels=None,
        cellLoc='center',
        loc='center'
    )

    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.8)

    # Colors
    header_color = '#2c3e50'
    header_text_color = '#ffffff'
    p2_tune_color = '#d4edda'
    p2_tune_text = '#155724'
    p1_tune_color = '#fff3cd'
    p1_tune_text = '#856404'
    p2_gen_color = '#cce5ff'
    p2_gen_text = '#004085'
    p1_gen_color = '#f8d7da'
    p1_gen_text = '#721c24'
    edge_color = '#dee2e6'

    prompt_col_idx = display_df.columns.tolist().index('Prompt')
    type_col_idx = display_df.columns.tolist().index('Type')

    for k, cell in table.get_celld().items():
        row, col = k
        cell.set_edgecolor(edge_color)
        cell.set_linewidth(1)

        if row == 0:
            cell.set_text_props(weight='bold', color=header_text_color)
            cell.set_facecolor(header_color)
        else:
            prompt = table_data[row][prompt_col_idx]
            etype = table_data[row][type_col_idx]

            if prompt == 'P2' and etype == 'TUNE':
                cell.set_facecolor(p2_tune_color)
                cell.set_text_props(color=p2_tune_text, weight='bold')
            elif prompt == 'P2' and etype == 'GEN':
                cell.set_facecolor(p2_gen_color)
                cell.set_text_props(color=p2_gen_text)
            elif prompt == 'P1' and etype == 'TUNE':
                cell.set_facecolor(p1_tune_color)
                cell.set_text_props(color=p1_tune_text, weight='bold')
            else:  # P1 GEN
                cell.set_facecolor(p1_gen_color)
                cell.set_text_props(color=p1_gen_text)

    plt.title("P1 vs P2 Comparison by Writer\nGreen=P2 TUNE | Blue=P2 GEN | Yellow=P1 TUNE | Red=P1 GEN",
              fontweight="bold", fontsize=14, pad=20, color='#2c3e50')

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / 'p1_vs_p2_by_writer.png'

    plt.savefig(output_path, bbox_inches='tight', dpi=300, facecolor='white')
    print(f"P1 vs P2 by writer saved to {output_path}")
    plt.close()

    return df


def export_combined_gen_tune_by_writer():
    """Combine GEN vs TUNE by writer tables for both prompts into one image."""
    # Get data for both prompts
    df_p1 = create_gen_tune_summary(prompt_num=1)
    df_p2 = create_gen_tune_summary(prompt_num=2)

    # Add prompt column
    df_p1['Prompt'] = 'P1'
    df_p2['Prompt'] = 'P2'

    # Combine
    combined_df = pd.concat([df_p1, df_p2], ignore_index=True)

    # Reorder columns
    cols = ['Prompt', 'Assignment', 'Writer', 'Type'] + SHORT_DIMS + ['Total/20']
    combined_df = combined_df[cols]

    # Sort
    combined_df = combined_df.sort_values(by=['Prompt', 'Assignment', 'Writer', 'Type'])

    # Export as table
    num_rows = len(combined_df)
    fig_height = max(6, num_rows * 0.35 + 3)
    fig_width = 16

    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    ax.axis('off')

    # Format display data
    display_df = combined_df.copy()
    for col in display_df.columns:
        if col not in ['Prompt', 'Assignment', 'Writer', 'Type']:
            display_df[col] = display_df[col].apply(lambda x: f"{x:.2f}")

    table_data = [display_df.columns.tolist()] + display_df.values.tolist()

    table = ax.table(
        cellText=table_data,
        colLabels=None,
        cellLoc='center',
        loc='center'
    )

    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.6)

    # Colors
    header_color = '#2c3e50'
    header_text_color = '#ffffff'
    tune_color = '#d4edda'
    tune_text_color = '#155724'
    p1_color = '#fff3cd'
    p2_color = '#cce5ff'
    edge_color = '#dee2e6'

    type_col_idx = display_df.columns.tolist().index('Type')
    prompt_col_idx = display_df.columns.tolist().index('Prompt')

    for k, cell in table.get_celld().items():
        row, col = k
        cell.set_edgecolor(edge_color)
        cell.set_linewidth(1)

        if row == 0:
            cell.set_text_props(weight='bold', color=header_text_color)
            cell.set_facecolor(header_color)
        else:
            is_tune = table_data[row][type_col_idx] == 'TUNE'
            is_p1 = table_data[row][prompt_col_idx] == 'P1'

            if is_tune:
                cell.set_facecolor(tune_color)
                cell.set_text_props(color=tune_text_color, weight='bold')
            elif is_p1:
                cell.set_facecolor(p1_color)
                cell.set_text_props(color='#856404')
            else:
                cell.set_facecolor(p2_color)
                cell.set_text_props(color='#004085')

    plt.title("GEN vs TUNE by Writer - Combined (Prompt 1 & Prompt 2)\nTUNE (green) shows improvement over GEN",
              fontweight="bold", fontsize=14, pad=20, color='#2c3e50')

    fig.text(0.5, 0.01, "TUNE highlighted in green | P1 (yellow background) | P2 (blue background)",
             ha='center', fontsize=10, style='italic', color='#555')

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / 'gen_tune_by_writer_combined.png'

    plt.savefig(output_path, bbox_inches='tight', dpi=300, facecolor='white')
    print(f"Combined table saved to {output_path}")
    plt.close()

    return combined_df


if __name__ == "__main__":
    print("Generating Rubric visualizations...")

    # 1. Combined Average Progression plots
    plot_combined_average(prompt_num=2)
    plot_combined_average(prompt_num=1)

    # 2. Dataset Tables (Pretty PNGs)
    for assign in ASSIGNMENTS:
        visualize_dataset_as_png(assignment=assign, prompt_num=2)

    # 3. GEN vs TUNE Summary Tables and Charts
    for p_num in [1, 2]:
        print(f"\n=== GEN vs TUNE Summary (Prompt {p_num}) ===")

        # Detailed summary by writer
        detail_df = create_gen_tune_summary(prompt_num=p_num)
        print(detail_df.to_string(index=False))

        # Overall summary
        overall_df = create_overall_gen_tune_summary(prompt_num=p_num)
        print(f"\n=== Overall GEN vs TUNE (Prompt {p_num}) ===")
        print(overall_df.to_string(index=False))

        # Export tables
        export_gen_tune_table(
            overall_df,
            title=f"GEN vs TUNE Overall Comparison (Prompt {p_num})",
            output_filename=f'gen_tune_overall_p{p_num}.png',
            highlight_type='TUNE'
        )

        export_gen_tune_table(
            detail_df,
            title=f"GEN vs TUNE by Writer (Prompt {p_num})",
            output_filename=f'gen_tune_by_writer_p{p_num}.png',
            highlight_type='TUNE'
        )

        # Export chart
        export_gen_tune_chart(overall_df, p_num)

        # Save CSV
        detail_df.to_csv(OUTPUT_DIR / f'gen_tune_detail_p{p_num}.csv', index=False)
        overall_df.to_csv(OUTPUT_DIR / f'gen_tune_overall_p{p_num}.csv', index=False)

    # 4. Combined GEN vs TUNE table (both prompts)
    print("\n=== Generating Combined GEN vs TUNE Table ===")
    combined_df = export_combined_gen_tune_by_writer()
    combined_df.to_csv(OUTPUT_DIR / 'gen_tune_by_writer_combined.csv', index=False)

    print("\nAll visualizations completed.")
