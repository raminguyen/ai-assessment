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

# Dimension alternates for parsing
dim_alternates = {
    'Evidence': ['Evidence', 'Evidence (selecting and using information)', 'Evidence (selecting/using information)', 'Evidence (Selecting and using information to investigate a point of view or conclusion)'],
    "Student's position": ["Student's position", "Student's position (perspective/thesis)", "Student's position (perspective, thesis/hypothesis)", "Student's position (perspective/thesis/hypothesis)"],
    'Conclusions and related outcomes': ['Conclusions and related outcomes', 'Conclusions/outcomes', 'Conclusions and related outcomes (implications and consequences)'],
}


def parse_dimension_scores(text):
    """Parse rubric dimension scores from text."""
    scores = {}

    for dim in DIMENSIONS:
        names_to_try = dim_alternates.get(dim, [dim])

        for dim_name in names_to_try:
            dim_escaped = re.escape(dim_name)
            dim_escaped = dim_escaped.replace("'", r"['\u2019]")
            dim_escaped = dim_escaped.replace(r'\ and\ ', r'\ (?:and|&)\ ')

            patterns = [
                r'^\s*-\s*\*\*' + dim_escaped + r'\*\*:\s*(\d+(?:\.\d+)?)',
                r'^\s*-\s*\*\*' + dim_escaped + r':\*\*\s*(\d+(?:\.\d+)?)',
                r'\*\*' + dim_escaped + r':\*\*\s*(\d+(?:\.\d+)?)',
                r'\|\s*\*\*' + dim_escaped + r'\*\*\s*\|\s*(\d+(?:\.\d+)?)',
                dim_escaped + r':\s*(\d+(?:\.\d+)?)',
                r'-\s*\*\*' + dim_escaped + r':\*\*\s*\*\*(\d+(?:\.\d+)?)\*\*',
                r'\*\*' + dim_escaped + r'(?:\s*\([^)]*\))?:\s*(\d+(?:\.\d+)?)\*\*',
            ]

            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    try:
                        score = float(match.group(1))
                        if 0 <= score <= 4:
                            scores[dim] = score
                            break
                    except ValueError:
                        pass

            if dim in scores:
                break

        if dim not in scores:
            scores[dim] = 0.0

    return scores


def load_all_scores():
    """Load all scores from data files for both EXP1 (p1) and EXP2 (p2)."""
    all_data = []

    for filename in os.listdir(DATA_DIR):
        if not filename.endswith('.json'):
            continue
        if '_score_' not in filename:
            continue

        # Parse filename
        parts = filename.replace('.json', '').split('_')

        # Determine prompt (EXP1 or EXP2)
        if '_p1' in filename:
            exp = 'EXP1'
        elif '_p2' in filename:
            exp = 'EXP2'
        else:
            continue

        # Determine essay type
        if 'gen' in parts:
            essay_type = 'gen'
        elif 'tune' in parts:
            essay_type = 'tune'
        else:
            continue

        # Find assignment
        assignment = parts[0] if parts[0] in ASSIGNMENTS else None
        if not assignment:
            continue

        # Find writer and grader
        try:
            if essay_type == 'gen':
                type_idx = parts.index('gen')
            else:
                type_idx = parts.index('tune')
            writer = parts[type_idx + 1]

            score_idx = parts.index('score')
            grader = parts[score_idx + 1]
        except (ValueError, IndexError):
            continue

        if writer not in WRITERS or grader not in WRITERS:
            continue
        if writer == grader:
            continue

        # Load and parse scores
        filepath = DATA_DIR / filename
        try:
            with open(filepath, 'r') as f:
                content = json.load(f)
            result_text = content.get('result', '')
            scores = parse_dimension_scores(result_text)

            row = {
                'Experiment': exp,
                'Assignment': assignment.upper(),
                'Type': essay_type,
                'Writer': writer,
                'Grader': grader,
            }
            for i, dim in enumerate(DIMENSIONS):
                row[SHORT_DIMS[i]] = scores.get(dim, 0.0)

            row['Total'] = sum(scores.values())
            row['Average'] = np.mean(list(scores.values()))

            all_data.append(row)

        except Exception as e:
            continue

    return pd.DataFrame(all_data)


def create_summary_by_experiment(df):
    """Create summary table comparing EXP1 vs EXP2."""
    summary = []

    for exp in ['EXP1', 'EXP2']:
        exp_data = df[df['Experiment'] == exp]
        if len(exp_data) == 0:
            continue

        row = {'Experiment': exp, 'N': len(exp_data)}
        for dim in SHORT_DIMS:
            row[dim] = round(exp_data[dim].mean(), 2)
        row['Total'] = round(exp_data['Total'].mean(), 2)
        row['Average'] = round(exp_data['Average'].mean(), 2)

        summary.append(row)

    return pd.DataFrame(summary)


def create_summary_by_writer(df):
    """Create summary table for each writer model comparing EXP1 vs EXP2 (with gen/tune breakdown)."""
    summary = []

    for writer in WRITERS:
        for exp in ['EXP1', 'EXP2']:
            for essay_type in ['gen', 'tune']:
                writer_data = df[(df['Writer'] == writer) & (df['Experiment'] == exp) & (df['Type'] == essay_type)]
                if len(writer_data) == 0:
                    continue

                row = {
                    'Writer': writer.upper(),
                    'Experiment': exp,
                    'Type': essay_type.upper(),
                    'N': len(writer_data),
                }
                for dim in SHORT_DIMS:
                    row[dim] = round(writer_data[dim].mean(), 2)

                # Total out of 20 (5 dimensions x 4 max)
                row['Total/20'] = round(writer_data['Total'].mean(), 2)

                summary.append(row)

    return pd.DataFrame(summary)


def create_summary_by_experiment_type(df):
    """Create summary comparing EXP1 vs EXP2, with gen and tune breakdown."""
    summary = []

    for exp in ['EXP1', 'EXP2']:
        for essay_type in ['gen', 'tune']:
            exp_data = df[(df['Experiment'] == exp) & (df['Type'] == essay_type)]
            if len(exp_data) == 0:
                continue

            row = {
                'Experiment': exp,
                'Type': essay_type.upper(),
                'N': len(exp_data),
            }
            for dim in SHORT_DIMS:
                row[dim] = round(exp_data[dim].mean(), 2)

            row['Total/20'] = round(exp_data['Total'].mean(), 2)
            summary.append(row)

    return pd.DataFrame(summary)


def export_pretty_table(df, title, output_filename, highlight_exp='EXP2'):
    """Export DataFrame as a pretty PNG table with EXP2 highlighted."""
    num_rows = len(df)
    fig_height = max(3, num_rows * 0.8 + 2)
    fig_width = 14

    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    ax.axis('off')

    # Format display data
    display_df = df.copy()
    for col in display_df.columns:
        if col not in ['Experiment', 'Assignment', 'Type', 'Writer', 'Grader', 'N']:
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
    highlight_color = '#d4edda'
    highlight_text_color = '#155724'
    row_colors = ['#f8f9fa', '#ffffff']
    edge_color = '#dee2e6'

    exp_col_idx = display_df.columns.tolist().index('Experiment')

    for k, cell in table.get_celld().items():
        row, col = k
        cell.set_edgecolor(edge_color)
        cell.set_linewidth(1.5)

        if row == 0:
            cell.set_text_props(weight='bold', color=header_text_color)
            cell.set_facecolor(header_color)
        else:
            is_highlight = table_data[row][exp_col_idx] == highlight_exp

            if is_highlight:
                cell.set_facecolor(highlight_color)
                cell.set_text_props(color=highlight_text_color, weight='bold')
            else:
                cell.set_facecolor(row_colors[row % 2])
                cell.set_text_props(color='#212529')

    plt.title(title, fontweight="bold", fontsize=16, pad=20, color='#2c3e50')

    fig.text(0.5, 0.02, f"* {highlight_exp} (Prompt 2) highlighted in green - BEST PERFORMING",
             ha='center', fontsize=11, fontweight='bold', color='#155724',
             bbox=dict(facecolor='#d4edda', alpha=0.9, edgecolor='#155724', boxstyle='round,pad=0.4'))

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / output_filename

    plt.savefig(output_path, bbox_inches='tight', dpi=300, facecolor='white')
    print(f"Table saved to {output_path}")
    plt.close()


def export_comparison_chart(summary_df, output_filename='exp_comparison_chart.png'):
    """Create bar chart comparing EXP1 vs EXP2."""
    fig, ax = plt.subplots(figsize=(12, 6))

    x = np.arange(len(SHORT_DIMS))
    width = 0.35

    colors = {'EXP1': '#95a5a6', 'EXP2': '#27ae60'}

    for i, exp in enumerate(['EXP1', 'EXP2']):
        exp_data = summary_df[summary_df['Experiment'] == exp]
        if len(exp_data) == 0:
            continue
        scores = [exp_data[dim].values[0] for dim in SHORT_DIMS]

        bars = ax.bar(x + i * width, scores, width, label=exp, color=colors[exp],
                     edgecolor='white', linewidth=2,
                     alpha=1.0 if exp == 'EXP2' else 0.6)

        if exp == 'EXP2':
            for bar, score in zip(bars, scores):
                ax.annotate(f'{score:.2f}',
                           xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                           xytext=(0, 3), textcoords="offset points",
                           ha='center', va='bottom', fontsize=10, fontweight='bold',
                           color='#155724')

    ax.set_xlabel('Rubric Dimensions', fontsize=12, fontweight='bold')
    ax.set_ylabel('Average Score (0-4 scale)', fontsize=12, fontweight='bold')
    ax.set_title('EXP1 vs EXP2: EXP2 (Prompt 2) Outperforms EXP1 (Prompt 1)',
                 fontsize=14, fontweight='bold', color='#2c3e50', pad=15)
    ax.set_xticks(x + width / 2)
    ax.set_xticklabels(SHORT_DIMS, fontsize=11)
    ax.set_ylim(0, 4.5)
    ax.legend(loc='upper right', fontsize=11)
    ax.grid(axis='y', linestyle='--', alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Add improvement annotation
    exp1_avg = summary_df[summary_df['Experiment'] == 'EXP1']['Average'].values
    exp2_avg = summary_df[summary_df['Experiment'] == 'EXP2']['Average'].values

    if len(exp1_avg) > 0 and len(exp2_avg) > 0:
        improvement = ((exp2_avg[0] - exp1_avg[0]) / exp1_avg[0]) * 100
        ax.text(0.02, 0.95, f"EXP2 Improvement: +{improvement:.1f}%",
                transform=ax.transAxes, fontsize=12, fontweight='bold', color='#155724',
                verticalalignment='top',
                bbox=dict(facecolor='#d4edda', alpha=0.9, edgecolor='#155724', boxstyle='round,pad=0.4'))

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / output_filename
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, facecolor='white')
    print(f"Chart saved to {output_path}")
    plt.close()


def export_writer_comparison_chart(writer_summary_df, output_filename='exp_writer_comparison_chart.png'):
    """Create grouped bar chart comparing EXP1 vs EXP2 for each writer model with gen/tune breakdown."""
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    writers = ['CHATGPT', 'GEMINI', 'CLAUDE', 'GROK']
    x = np.arange(len(writers))
    width = 0.35

    colors = {'EXP1': '#e74c3c', 'EXP2': '#27ae60'}

    for idx, essay_type in enumerate(['GEN', 'TUNE']):
        ax = axes[idx]

        exp1_totals = []
        exp2_totals = []

        for writer in writers:
            exp1_data = writer_summary_df[(writer_summary_df['Writer'] == writer) &
                                          (writer_summary_df['Experiment'] == 'EXP1') &
                                          (writer_summary_df['Type'] == essay_type)]
            exp2_data = writer_summary_df[(writer_summary_df['Writer'] == writer) &
                                          (writer_summary_df['Experiment'] == 'EXP2') &
                                          (writer_summary_df['Type'] == essay_type)]

            exp1_totals.append(exp1_data['Total/20'].values[0] if len(exp1_data) > 0 else 0)
            exp2_totals.append(exp2_data['Total/20'].values[0] if len(exp2_data) > 0 else 0)

        bars1 = ax.bar(x - width/2, exp1_totals, width, label='EXP1 (Prompt 1)', color=colors['EXP1'],
                       edgecolor='white', linewidth=2, alpha=0.7)
        bars2 = ax.bar(x + width/2, exp2_totals, width, label='EXP2 (Prompt 2)', color=colors['EXP2'],
                       edgecolor='white', linewidth=2, alpha=1.0)

        # Add value labels
        for bar, val in zip(bars1, exp1_totals):
            ax.annotate(f'{val:.1f}',
                       xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                       xytext=(0, 3), textcoords="offset points",
                       ha='center', va='bottom', fontsize=10, fontweight='bold', color='#c0392b')

        for bar, val in zip(bars2, exp2_totals):
            ax.annotate(f'{val:.1f}',
                       xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                       xytext=(0, 3), textcoords="offset points",
                       ha='center', va='bottom', fontsize=11, fontweight='bold', color='#155724')

        # Highlight winner
        for i, (e1, e2) in enumerate(zip(exp1_totals, exp2_totals)):
            if e2 > e1:
                marker = "EXP2 ^"
                color = '#27ae60'
            elif e1 > e2:
                marker = "EXP1 ^"
                color = '#e74c3c'
            else:
                marker = "="
                color = 'gray'
            ax.text(i, max(e1, e2) + 1.2, marker, ha='center', fontsize=9, fontweight='bold', color=color)

        ax.set_xlabel('Writer Model', fontsize=12, fontweight='bold')
        ax.set_ylabel('Total Score (out of 20)', fontsize=12, fontweight='bold')
        ax.set_title(f'{essay_type} Essays: EXP1 vs EXP2',
                     fontsize=14, fontweight='bold', color='#2c3e50', pad=10)
        ax.set_xticks(x)
        ax.set_xticklabels(writers, fontsize=11, fontweight='bold')
        ax.set_ylim(0, 22)
        ax.axhline(y=20, color='gray', linestyle='--', alpha=0.5)
        ax.legend(loc='upper right', fontsize=10)
        ax.grid(axis='y', linestyle='--', alpha=0.3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

    fig.suptitle('EXP1 vs EXP2 Comparison by Writer Model (GEN and TUNE)',
                 fontsize=16, fontweight='bold', color='#2c3e50', y=1.02)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / output_filename
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, facecolor='white', bbox_inches='tight')
    print(f"Writer comparison chart saved to {output_path}")
    plt.close()


def export_exp_type_chart(exp_type_df, output_filename='exp_type_comparison_chart.png'):
    """Create bar chart comparing EXP1 vs EXP2 with gen/tune breakdown."""
    fig, ax = plt.subplots(figsize=(10, 7))

    categories = ['EXP1\nGEN', 'EXP1\nTUNE', 'EXP2\nGEN', 'EXP2\nTUNE']
    x = np.arange(len(categories))

    totals = []
    colors_list = []

    for exp in ['EXP1', 'EXP2']:
        for etype in ['GEN', 'TUNE']:
            data = exp_type_df[(exp_type_df['Experiment'] == exp) & (exp_type_df['Type'] == etype)]
            totals.append(data['Total/20'].values[0] if len(data) > 0 else 0)
            colors_list.append('#e74c3c' if exp == 'EXP1' else '#27ae60')

    bars = ax.bar(x, totals, color=colors_list, edgecolor='white', linewidth=2, alpha=0.85)

    for bar, val in zip(bars, totals):
        ax.annotate(f'{val:.1f}',
                   xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                   xytext=(0, 3), textcoords="offset points",
                   ha='center', va='bottom', fontsize=12, fontweight='bold')

    ax.set_xlabel('Experiment / Essay Type', fontsize=13, fontweight='bold')
    ax.set_ylabel('Total Score (out of 20)', fontsize=13, fontweight='bold')
    ax.set_title('EXP1 vs EXP2: Overall Comparison (GEN & TUNE)',
                 fontsize=15, fontweight='bold', color='#2c3e50', pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=11, fontweight='bold')
    ax.set_ylim(0, 22)
    ax.axhline(y=20, color='gray', linestyle='--', alpha=0.5)
    ax.grid(axis='y', linestyle='--', alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Add legend
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor='#e74c3c', label='EXP1 (Prompt 1)'),
                       Patch(facecolor='#27ae60', label='EXP2 (Prompt 2)')]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=11)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / output_filename
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, facecolor='white')
    print(f"Exp type comparison chart saved to {output_path}")
    plt.close()


if __name__ == "__main__":
    print("Loading data from existing files...")

    # Load all data
    df = load_all_scores()
    print(f"Loaded {len(df)} score entries")

    # Create overall summary
    summary_df = create_summary_by_experiment(df)
    print("\n=== Summary: EXP1 vs EXP2 (Overall) ===")
    print(summary_df.to_string(index=False))

    # Create summary by experiment and type (gen/tune)
    exp_type_df = create_summary_by_experiment_type(df)
    print("\n=== Summary: EXP1 vs EXP2 with GEN/TUNE breakdown ===")
    print(exp_type_df.to_string(index=False))

    # Create per-writer summary with gen/tune
    writer_summary_df = create_summary_by_writer(df)
    print("\n=== Summary by Writer Model: EXP1 vs EXP2 (GEN & TUNE) ===")
    print(writer_summary_df.to_string(index=False))

    # Export experiment/type summary table
    export_pretty_table(
        exp_type_df,
        title="EXP1 vs EXP2 Comparison (GEN & TUNE)",
        output_filename='exp_type_summary_table.png',
        highlight_exp='EXP2'
    )

    # Export per-writer summary table
    export_pretty_table(
        writer_summary_df,
        title="Writer Model Comparison: EXP1 vs EXP2 (GEN & TUNE, Total/20)",
        output_filename='exp_writer_summary_table.png',
        highlight_exp='EXP2'
    )

    # Export charts
    export_exp_type_chart(exp_type_df)
    export_writer_comparison_chart(writer_summary_df)

    # Save CSVs
    csv_path = OUTPUT_DIR / 'exp_comparison_data.csv'
    df.to_csv(csv_path, index=False)
    exp_type_df.to_csv(OUTPUT_DIR / 'exp_type_summary.csv', index=False)
    writer_summary_df.to_csv(OUTPUT_DIR / 'exp_writer_summary.csv', index=False)
    print(f"\nCSV saved to {csv_path}")

    print("\nDone!")
