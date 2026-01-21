"""
Prompt 1 vs Prompt 2 Performance Comparison
Uses the improved parser function to compare scores between prompts.
"""

import os
import json
import re
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from collections import defaultdict

DATA_DIR = Path('data/critical_thinking')
OUTPUT_DIR = Path('src/visualization/rubric_plots')
WRITERS = ['chatgpt', 'gemini', 'claude', 'grok']
DIMENSIONS = [
    'Explanation of issues',
    'Evidence',
    'Influence of context and assumptions',
    "Student's position",
    'Conclusions and related outcomes'
]
SHORT_DIMS = ['Issues', 'Evidence', 'Context', 'Position', 'Conclusion']

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


def load_data_for_prompt(prompt_num):
    """Load all score data for a specific prompt number."""
    # Structure: data[assignment][writer][essay_type][dim] = [scores from all graders]
    data = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list))))

    for filename in os.listdir(DATA_DIR):
        if not filename.endswith('.json') or '_score_' not in filename:
            continue

        # Parse filename
        parts = filename.replace('.json', '').split('_')
        assignment = parts[0]  # a1, a2, a3

        # Get prompt number
        file_prompt = None
        for p in parts:
            if p.startswith('p') and len(p) == 2:
                file_prompt = int(p[1])
                break

        if file_prompt != prompt_num:
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

    return data


def calculate_averages(data):
    """Calculate average scores from data structure."""
    # Structure: result[assignment][writer][essay_type] = {dim: avg_score}
    result = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))

    for assignment in ['a1', 'a2', 'a3']:
        for writer in WRITERS:
            for essay_type in ['gen', 'tune']:
                for dim in DIMENSIONS:
                    scores = data[assignment][writer][essay_type].get(dim, [])
                    if scores:
                        result[assignment][writer][essay_type][dim] = sum(scores) / len(scores)
                    else:
                        result[assignment][writer][essay_type][dim] = 0.0

    return result


def plot_prompt_comparison_by_writer():
    """Create a comparison chart showing P1 vs P2 performance for each writer."""

    # Load data for both prompts
    data_p1 = load_data_for_prompt(1)
    data_p2 = load_data_for_prompt(2)

    avg_p1 = calculate_averages(data_p1)
    avg_p2 = calculate_averages(data_p2)

    fig, axes = plt.subplots(4, 3, figsize=(18, 20))

    for w_idx, writer in enumerate(WRITERS):
        for a_idx, assignment in enumerate(['a1', 'a2', 'a3']):
            ax = axes[w_idx, a_idx]

            x = np.arange(len(SHORT_DIMS))
            width = 0.35

            # Get scores for P1 and P2
            p1_gen = [avg_p1[assignment][writer]['gen'].get(dim, 0) for dim in DIMENSIONS]
            p1_tune = [avg_p1[assignment][writer]['tune'].get(dim, 0) for dim in DIMENSIONS]
            p2_gen = [avg_p2[assignment][writer]['gen'].get(dim, 0) for dim in DIMENSIONS]
            p2_tune = [avg_p2[assignment][writer]['tune'].get(dim, 0) for dim in DIMENSIONS]

            # Calculate totals
            p1_gen_total = sum(p1_gen) / 5
            p1_tune_total = sum(p1_tune) / 5
            p2_gen_total = sum(p2_gen) / 5
            p2_tune_total = sum(p2_tune) / 5

            # Plot bars - P1 (left) and P2 (right)
            bars1 = ax.bar(x - width/2 - 0.05, p1_tune, width, label='P1 Tune', color='#85C1E9', edgecolor='#2980B9', linewidth=1)
            bars2 = ax.bar(x + width/2 + 0.05, p2_tune, width, label='P2 Tune', color='#82E0AA', edgecolor='#27AE60', linewidth=1)

            # Add gen scores as markers
            ax.scatter(x - width/2 - 0.05, p1_gen, s=60, c='#2980B9', marker='o', zorder=5, label='P1 Gen')
            ax.scatter(x + width/2 + 0.05, p2_gen, s=60, c='#27AE60', marker='o', zorder=5, label='P2 Gen')

            # Connect gen to tune with lines
            for i in range(len(DIMENSIONS)):
                ax.plot([x[i] - width/2 - 0.05, x[i] - width/2 - 0.05], [p1_gen[i], p1_tune[i]],
                       color='#2980B9', linewidth=1.5, alpha=0.7)
                ax.plot([x[i] + width/2 + 0.05, x[i] + width/2 + 0.05], [p2_gen[i], p2_tune[i]],
                       color='#27AE60', linewidth=1.5, alpha=0.7)

            # Labels and styling
            ax.set_ylabel('Score (0-4)')
            ax.set_ylim(0, 4.5)
            ax.set_xticks(x)
            ax.set_xticklabels(SHORT_DIMS, rotation=45, ha='right', fontsize=9)
            ax.set_title(f'{writer.upper()} - {assignment.upper()}', fontweight='bold', fontsize=11)
            ax.axhline(y=4, color='gray', linestyle='--', alpha=0.3)
            ax.grid(axis='y', alpha=0.2)

            # Add summary annotation
            p1_diff = p1_tune_total - p1_gen_total
            p2_diff = p2_tune_total - p2_gen_total

            summary = f'P1: {p1_gen_total:.2f}→{p1_tune_total:.2f} ({p1_diff:+.2f})\nP2: {p2_gen_total:.2f}→{p2_tune_total:.2f} ({p2_diff:+.2f})'
            ax.text(0.98, 0.98, summary, transform=ax.transAxes, fontsize=8, verticalalignment='top',
                   horizontalalignment='right', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

            # Legend only for first subplot
            if w_idx == 0 and a_idx == 0:
                ax.legend(loc='upper left', fontsize=8)

    plt.suptitle('Prompt 1 vs Prompt 2 Performance Comparison\n(By Writer and Assignment)',
                fontsize=16, fontweight='bold', y=0.995)
    plt.tight_layout()
    plt.subplots_adjust(top=0.94, hspace=0.35, wspace=0.25)

    return fig


def plot_prompt_comparison_summary():
    """Create a summary comparison showing overall P1 vs P2 performance."""

    # Load data for both prompts
    data_p1 = load_data_for_prompt(1)
    data_p2 = load_data_for_prompt(2)

    avg_p1 = calculate_averages(data_p1)
    avg_p2 = calculate_averages(data_p2)

    fig, axes = plt.subplots(1, 2, figsize=(16, 8))

    # Left plot: Average by Writer (across all assignments)
    ax1 = axes[0]

    x = np.arange(len(WRITERS))
    width = 0.2

    writer_p1_gen = []
    writer_p1_tune = []
    writer_p2_gen = []
    writer_p2_tune = []

    for writer in WRITERS:
        p1_gen_scores = []
        p1_tune_scores = []
        p2_gen_scores = []
        p2_tune_scores = []

        for assignment in ['a1', 'a2', 'a3']:
            for dim in DIMENSIONS:
                p1_gen_scores.append(avg_p1[assignment][writer]['gen'].get(dim, 0))
                p1_tune_scores.append(avg_p1[assignment][writer]['tune'].get(dim, 0))
                p2_gen_scores.append(avg_p2[assignment][writer]['gen'].get(dim, 0))
                p2_tune_scores.append(avg_p2[assignment][writer]['tune'].get(dim, 0))

        writer_p1_gen.append(np.mean(p1_gen_scores))
        writer_p1_tune.append(np.mean(p1_tune_scores))
        writer_p2_gen.append(np.mean(p2_gen_scores))
        writer_p2_tune.append(np.mean(p2_tune_scores))

    bars1 = ax1.bar(x - 1.5*width, writer_p1_gen, width, label='P1 Gen', color='#AED6F1', edgecolor='#2980B9')
    bars2 = ax1.bar(x - 0.5*width, writer_p1_tune, width, label='P1 Tune', color='#5DADE2', edgecolor='#2980B9')
    bars3 = ax1.bar(x + 0.5*width, writer_p2_gen, width, label='P2 Gen', color='#ABEBC6', edgecolor='#27AE60')
    bars4 = ax1.bar(x + 1.5*width, writer_p2_tune, width, label='P2 Tune', color='#58D68D', edgecolor='#27AE60')

    ax1.set_ylabel('Average Score (0-4)', fontsize=12)
    ax1.set_xlabel('Writer', fontsize=12)
    ax1.set_title('Average Performance by Writer\n(Across All Assignments)', fontweight='bold', fontsize=13)
    ax1.set_xticks(x)
    ax1.set_xticklabels([w.upper() for w in WRITERS], fontsize=11, fontweight='bold')
    ax1.legend(loc='upper right', fontsize=10)
    ax1.set_ylim(0, 4.5)
    ax1.axhline(y=4, color='gray', linestyle='--', alpha=0.3)
    ax1.grid(axis='y', alpha=0.2)

    # Add value labels on bars
    for bars in [bars1, bars2, bars3, bars4]:
        for bar in bars:
            height = bar.get_height()
            ax1.annotate(f'{height:.2f}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3), textcoords="offset points",
                        ha='center', va='bottom', fontsize=8, rotation=90)

    # Right plot: Improvement comparison (P2 - P1)
    ax2 = axes[1]

    x = np.arange(len(WRITERS))
    width = 0.35

    gen_diff = [writer_p2_gen[i] - writer_p1_gen[i] for i in range(len(WRITERS))]
    tune_diff = [writer_p2_tune[i] - writer_p1_tune[i] for i in range(len(WRITERS))]

    colors_gen = ['#27AE60' if d >= 0 else '#E74C3C' for d in gen_diff]
    colors_tune = ['#27AE60' if d >= 0 else '#E74C3C' for d in tune_diff]

    bars1 = ax2.bar(x - width/2, gen_diff, width, label='Generated (P2-P1)', color=colors_gen, alpha=0.7, edgecolor='black')
    bars2 = ax2.bar(x + width/2, tune_diff, width, label='Tuned (P2-P1)', color=colors_tune, edgecolor='black')

    ax2.axhline(y=0, color='black', linewidth=1)
    ax2.set_ylabel('Score Difference (P2 - P1)', fontsize=12)
    ax2.set_xlabel('Writer', fontsize=12)
    ax2.set_title('Prompt 2 vs Prompt 1 Difference\n(Positive = P2 Better)', fontweight='bold', fontsize=13)
    ax2.set_xticks(x)
    ax2.set_xticklabels([w.upper() for w in WRITERS], fontsize=11, fontweight='bold')
    ax2.legend(loc='upper right', fontsize=10)
    ax2.grid(axis='y', alpha=0.2)
    ax2.set_ylim(-0.5, 0.5)

    # Add value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            va = 'bottom' if height >= 0 else 'top'
            offset = 3 if height >= 0 else -3
            ax2.annotate(f'{height:+.2f}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, offset), textcoords="offset points",
                        ha='center', va=va, fontsize=9, fontweight='bold')

    plt.suptitle('Prompt 1 vs Prompt 2: Summary Comparison', fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()

    return fig


def plot_dimension_comparison_by_prompt():
    """Create a comparison showing dimension-level performance for P1 vs P2."""

    # Load data for both prompts
    data_p1 = load_data_for_prompt(1)
    data_p2 = load_data_for_prompt(2)

    avg_p1 = calculate_averages(data_p1)
    avg_p2 = calculate_averages(data_p2)

    fig, axes = plt.subplots(1, 3, figsize=(18, 7))

    for a_idx, assignment in enumerate(['a1', 'a2', 'a3']):
        ax = axes[a_idx]

        x = np.arange(len(SHORT_DIMS))
        width = 0.2

        # Calculate average across all writers for each dimension
        p1_gen_dim = []
        p1_tune_dim = []
        p2_gen_dim = []
        p2_tune_dim = []

        for dim in DIMENSIONS:
            p1_gen_scores = [avg_p1[assignment][w]['gen'].get(dim, 0) for w in WRITERS]
            p1_tune_scores = [avg_p1[assignment][w]['tune'].get(dim, 0) for w in WRITERS]
            p2_gen_scores = [avg_p2[assignment][w]['gen'].get(dim, 0) for w in WRITERS]
            p2_tune_scores = [avg_p2[assignment][w]['tune'].get(dim, 0) for w in WRITERS]

            p1_gen_dim.append(np.mean(p1_gen_scores))
            p1_tune_dim.append(np.mean(p1_tune_scores))
            p2_gen_dim.append(np.mean(p2_gen_scores))
            p2_tune_dim.append(np.mean(p2_tune_scores))

        bars1 = ax.bar(x - 1.5*width, p1_gen_dim, width, label='P1 Gen', color='#AED6F1', edgecolor='#2980B9')
        bars2 = ax.bar(x - 0.5*width, p1_tune_dim, width, label='P1 Tune', color='#5DADE2', edgecolor='#2980B9')
        bars3 = ax.bar(x + 0.5*width, p2_gen_dim, width, label='P2 Gen', color='#ABEBC6', edgecolor='#27AE60')
        bars4 = ax.bar(x + 1.5*width, p2_tune_dim, width, label='P2 Tune', color='#58D68D', edgecolor='#27AE60')

        ax.set_ylabel('Average Score (0-4)', fontsize=11)
        ax.set_title(f'Assignment {assignment[1].upper()}', fontweight='bold', fontsize=13)
        ax.set_xticks(x)
        ax.set_xticklabels(SHORT_DIMS, rotation=45, ha='right', fontsize=10)
        ax.set_ylim(0, 4.5)
        ax.axhline(y=4, color='gray', linestyle='--', alpha=0.3)
        ax.grid(axis='y', alpha=0.2)

        if a_idx == 0:
            ax.legend(loc='lower left', fontsize=9)

    plt.suptitle('Dimension-Level Performance: Prompt 1 vs Prompt 2\n(Averaged Across All Writers)',
                fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()

    return fig


def print_prompt_comparison_table():
    """Print a detailed comparison table of P1 vs P2."""

    # Load data for both prompts
    data_p1 = load_data_for_prompt(1)
    data_p2 = load_data_for_prompt(2)

    avg_p1 = calculate_averages(data_p1)
    avg_p2 = calculate_averages(data_p2)

    print("=" * 100)
    print("PROMPT 1 vs PROMPT 2 COMPARISON TABLE")
    print("=" * 100)

    for writer in WRITERS:
        print(f"\n{'='*80}")
        print(f"WRITER: {writer.upper()}")
        print(f"{'='*80}")

        for assignment in ['a1', 'a2', 'a3']:
            print(f"\n  {assignment.upper()}:")
            print(f"  {'-'*70}")
            print(f"  {'Metric':<20} {'P1 Gen':>10} {'P1 Tune':>10} {'P2 Gen':>10} {'P2 Tune':>10} {'P2-P1 Diff':>12}")
            print(f"  {'-'*70}")

            for i, dim in enumerate(DIMENSIONS):
                p1_gen = avg_p1[assignment][writer]['gen'].get(dim, 0)
                p1_tune = avg_p1[assignment][writer]['tune'].get(dim, 0)
                p2_gen = avg_p2[assignment][writer]['gen'].get(dim, 0)
                p2_tune = avg_p2[assignment][writer]['tune'].get(dim, 0)
                diff = (p2_gen + p2_tune) / 2 - (p1_gen + p1_tune) / 2

                print(f"  {SHORT_DIMS[i]:<20} {p1_gen:>10.2f} {p1_tune:>10.2f} {p2_gen:>10.2f} {p2_tune:>10.2f} {diff:>+12.2f}")

            # Totals
            p1_gen_total = sum(avg_p1[assignment][writer]['gen'].get(dim, 0) for dim in DIMENSIONS) / 5
            p1_tune_total = sum(avg_p1[assignment][writer]['tune'].get(dim, 0) for dim in DIMENSIONS) / 5
            p2_gen_total = sum(avg_p2[assignment][writer]['gen'].get(dim, 0) for dim in DIMENSIONS) / 5
            p2_tune_total = sum(avg_p2[assignment][writer]['tune'].get(dim, 0) for dim in DIMENSIONS) / 5
            total_diff = (p2_gen_total + p2_tune_total) / 2 - (p1_gen_total + p1_tune_total) / 2

            print(f"  {'-'*70}")
            print(f"  {'AVERAGE':<20} {p1_gen_total:>10.2f} {p1_tune_total:>10.2f} {p2_gen_total:>10.2f} {p2_tune_total:>10.2f} {total_diff:>+12.2f}")

    # Overall summary
    print(f"\n{'='*100}")
    print("OVERALL SUMMARY (Averaged across all writers and assignments)")
    print(f"{'='*100}")

    overall_p1_gen = []
    overall_p1_tune = []
    overall_p2_gen = []
    overall_p2_tune = []

    for writer in WRITERS:
        for assignment in ['a1', 'a2', 'a3']:
            for dim in DIMENSIONS:
                overall_p1_gen.append(avg_p1[assignment][writer]['gen'].get(dim, 0))
                overall_p1_tune.append(avg_p1[assignment][writer]['tune'].get(dim, 0))
                overall_p2_gen.append(avg_p2[assignment][writer]['gen'].get(dim, 0))
                overall_p2_tune.append(avg_p2[assignment][writer]['tune'].get(dim, 0))

    print(f"\n  P1 Generated Average:  {np.mean(overall_p1_gen):.3f}")
    print(f"  P1 Tuned Average:      {np.mean(overall_p1_tune):.3f}")
    print(f"  P1 Improvement:        {np.mean(overall_p1_tune) - np.mean(overall_p1_gen):+.3f}")
    print()
    print(f"  P2 Generated Average:  {np.mean(overall_p2_gen):.3f}")
    print(f"  P2 Tuned Average:      {np.mean(overall_p2_tune):.3f}")
    print(f"  P2 Improvement:        {np.mean(overall_p2_tune) - np.mean(overall_p2_gen):+.3f}")
    print()
    print(f"  P2 vs P1 (Gen):        {np.mean(overall_p2_gen) - np.mean(overall_p1_gen):+.3f}")
    print(f"  P2 vs P1 (Tune):       {np.mean(overall_p2_tune) - np.mean(overall_p1_tune):+.3f}")
    print(f"  P2 vs P1 (Overall):    {(np.mean(overall_p2_gen) + np.mean(overall_p2_tune))/2 - (np.mean(overall_p1_gen) + np.mean(overall_p1_tune))/2:+.3f}")


if __name__ == "__main__":
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Generating Prompt 1 vs Prompt 2 Comparison Charts...")

    # 1. Detailed comparison by writer
    fig1 = plot_prompt_comparison_by_writer()
    output_path1 = OUTPUT_DIR / 'prompt_comparison_by_writer.png'
    fig1.savefig(output_path1, dpi=600, bbox_inches='tight')
    print(f"Saved: {output_path1}")
    plt.close(fig1)

    # 2. Summary comparison
    fig2 = plot_prompt_comparison_summary()
    output_path2 = OUTPUT_DIR / 'prompt_comparison_summary.png'
    fig2.savefig(output_path2, dpi=600, bbox_inches='tight')
    print(f"Saved: {output_path2}")
    plt.close(fig2)

    # 3. Dimension-level comparison
    fig3 = plot_dimension_comparison_by_prompt()
    output_path3 = OUTPUT_DIR / 'prompt_comparison_dimensions.png'
    fig3.savefig(output_path3, dpi=600, bbox_inches='tight')
    print(f"Saved: {output_path3}")
    plt.close(fig3)

    # 4. Print detailed table
    print("\n")
    print_prompt_comparison_table()

    print("\nAll prompt comparison visualizations completed.")
