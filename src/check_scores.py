import os
import sys
import re
import json
import glob
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

def parse_dimension_scores(text):
    """Parse rubric dimension scores from text. Same logic as parser.js"""
    dimensions = [
        'Explanation of issues',
        'Evidence',
        'Influence of context and assumptions',
        "Student's position",
        'Conclusions and related outcomes'
    ]

    scores = {}

    for dim in dimensions:
        flexible_dim = re.escape(dim)
        flexible_dim = flexible_dim.replace(r'and', r'(?:and|&)')
        flexible_dim = flexible_dim.replace(r"'", r"['\u2019\u2018]")

        patterns = [
            flexible_dim + r'[^\n|]{0,120}(?::|—|–)\s*\**(\d+(?:\.\d+)?)',
            r'\*\*' + flexible_dim + r'.*?:\*\*\s*(\d+(?:\.\d+)?)',
            r'\|[^\|]*'+ flexible_dim + r'[^\|]*\|\s*(?:\*\*)?(\d+(?:\.\d+)?)[^\|]*\|',
            r'- \*\*' + flexible_dim + r'.*?\*\*\s*:?\s*(\d+(?:\.\d+)?)',
            flexible_dim + r'[\s\S]{0,150}?\*\*Score:\s*(\d+(?:\.\d+)?)',
            flexible_dim + r'[\s\S]{0,150}?\*\*Score:\s*\w+(?:\s+\w+)*?\s*\((\d+(?:\.\d+)?)\)',
            flexible_dim + r'[^\n|]*(?::|—|–)[^\n|]*\((\d+(?:\.\d+)?)\)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                val = float(match.group(1))
                if 0 <= val <= 4:
                    scores[dim] = val
                    break

        if dim not in scores:
            scores[dim] = 0

    return scores

def parse_prompt(data_dir, prompt_num, dimensions, short_dims):
    pattern = os.path.join(data_dir, '*_score_*_p' + str(prompt_num) + '.json')
    files = sorted(glob.glob(pattern))
    header = ['Assignment', 'Writer', 'Grader'] + short_dims + ['Total']
    rows = []
    for filepath in files:
        filename = os.path.basename(filepath)
        m = re.match(r'a(\d+)_gen_([\w-]+)_score_([\w-]+)_p\d+\.json', filename)
        if not m:
            continue
        a_num, writer_name, grader_name = int(m.group(1)), m.group(2), m.group(3)
        with open(filepath, 'r', encoding='utf-8') as jf:
            data = json.load(jf)
        scores = parse_dimension_scores(data.get('result', ''))
        total = sum(scores.get(dim, 0) for dim in dimensions)
        rows.append(['A' + str(a_num), writer_name, grader_name] +
                    [scores.get(dim, 0) for dim in dimensions] + [total])
    return pd.DataFrame(rows, columns=header)


def join_scores():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'data', 'critical_thinking')
    src_dir = os.path.dirname(os.path.abspath(__file__))

    dimensions = [
        'Explanation of issues', 'Evidence',
        'Influence of context and assumptions',
        "Student's position", 'Conclusions and related outcomes'
    ]
    short_dims = ['Issues', 'Evidence', 'Context', 'Position', 'Conclusions']
    dim_cols = short_dims + ['Total']

    dfs = []
    for p_num in range(0, 12):
        df = parse_prompt(data_dir, p_num, dimensions, short_dims)
        if df.empty:
            continue
        df.insert(0, 'Prompt', 'p' + str(p_num))
        dfs.append(df)

    all_df = pd.concat(dfs, ignore_index=True)

    for col in dim_cols:
        all_df[col] = pd.to_numeric(all_df[col], errors='coerce').fillna(0)

    all_df['HasZero'] = np.any(all_df[dim_cols].values == 0, axis=1)
    for col in short_dims:
        all_df[col + '_zero'] = all_df[col] == 0

    all_df.to_csv(os.path.join(src_dir, 'scores_all.csv'), index=False)
    all_df.to_excel(os.path.join(src_dir, 'scores_all.xlsx'), index=False)
    zeros = int(all_df['HasZero'].sum())
    print('Saved scores_all.csv / scores_all.xlsx (' + str(len(all_df)) + ' rows, ' + str(zeros) + ' with zeros)')


def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'data', 'critical_thinking')

    if len(sys.argv) > 1 and sys.argv[1] == '--join':
        join_scores()
        return

    if len(sys.argv) > 1:
        prompt_num = int(sys.argv[1].lstrip('p'))
    else:
        prompt_num = 4

    pattern = os.path.join(data_dir, f'*_score_*_p{prompt_num}.json')

    files = sorted(glob.glob(pattern))

    print(f"Found {len(files)} score files for p{prompt_num}")

    dimensions = [
        'Explanation of issues',
        'Evidence',
        'Influence of context and assumptions',
        "Student's position",
        'Conclusions and related outcomes'
    ]
    short_dims = ['Issues', 'Evidence', 'Context', 'Position', 'Conclusions']

    rows = []
    for filepath in files:
        filename = os.path.basename(filepath)
        match = re.match(r'a(\d+)_gen_([\w-]+)_score_([\w-]+)_p\d+\.json', filename)
        if not match:
            continue

        a_num = int(match.group(1))
        writer_name = match.group(2)
        grader_name = match.group(3)

        with open(filepath, 'r', encoding='utf-8') as jf:
            data = json.load(jf)

        result = data.get('result', '')
        scores = parse_dimension_scores(result)

        total = sum(scores.get(dim, 0) for dim in dimensions)
        rows.append([f'A{a_num}', writer_name, grader_name] + [scores.get(dim, 0) for dim in dimensions] + [total])

    header = ['Assignment', 'Writer', 'Grader'] + short_dims + ['Total']
    df = pd.DataFrame(rows, columns=header)

    # Charts
    plot_avg_by_writer(df, prompt_num)
    plot_by_assignment(df, prompt_num)
    plot_by_dimension(df, prompt_num)


def plot_avg_by_writer(df, prompt_num):
    """Boxplot: total score distribution grouped by writer."""
    models = ['chatgpt', 'claude', 'gemini', 'grok']
    colors = {
        'chatgpt': '#3498DB',
        'claude': '#2ECC71',
        'gemini': '#E67E22',
        'grok': '#9B59B6'
    }

    fig, ax = plt.subplots(figsize=(8, 5))

    box_data = [df[df['Writer'] == m]['Total'].values for m in models]
    x = np.arange(1, len(models) + 1)

    bp = ax.boxplot(box_data, positions=x, widths=0.5, patch_artist=True,
                    medianprops=dict(color='#E74C3C', linewidth=2),
                    whiskerprops=dict(color='#555'),
                    capprops=dict(color='#555'),
                    flierprops=dict(marker='o', markerfacecolor='#E74C3C', markersize=5))

    for patch, model in zip(bp['boxes'], models):
        patch.set_facecolor(colors[model])
        patch.set_alpha(0.6)

    means = [np.mean(d) for d in box_data]
    ax.scatter(x, means, color='white', edgecolors='black', s=50, zorder=5, label='Mean')

    for i, m in enumerate(means):
        ax.text(x[i], m + 0.2, f'{m:.1f}', ha='center', va='bottom', fontsize=10, fontweight='bold')

    ax.set_xticks(x)
    ax.set_xticklabels([m.capitalize() for m in models], fontsize=11)
    ax.set_ylabel('Total Score (0-20)', fontsize=11)
    ax.set_title(f'Score Distribution by Writer (p{prompt_num} - Cross-graded)', fontsize=13, fontweight='bold')
    ax.set_ylim(0, 22)
    ax.legend(loc='lower right', fontsize=9)
    ax.grid(axis='y', linestyle='--', alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    output = f'scores_p{prompt_num}_by_writer.png'
    plt.savefig(output, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"Chart saved to {output}")
    plt.close()


def plot_by_assignment(df, prompt_num):
    """Boxplot: total score distribution by assignment, grouped by writer."""
    models = ['chatgpt', 'claude', 'gemini', 'grok']
    assignments = ['A1', 'A2', 'A3']
    assign_colors = ['#3498DB', '#E67E22', '#2ECC71']

    fig, ax = plt.subplots(figsize=(12, 6))

    width = 0.6
    gap = 0.2
    group_width = len(assignments) * width + (len(assignments) - 1) * gap
    group_spacing = group_width + 1.5

    for mi, model in enumerate(models):
        group_start = mi * group_spacing
        for ai, assign in enumerate(assignments):
            vals = df[(df['Writer'] == model) & (df['Assignment'] == assign)]['Total'].values
            if len(vals) == 0:
                continue
            pos = group_start + ai * (width + gap)

            bp = ax.boxplot([vals], positions=[pos], widths=width, patch_artist=True,
                            boxprops=dict(facecolor=assign_colors[ai], alpha=0.6),
                            medianprops=dict(color='#E74C3C', linewidth=2),
                            whiskerprops=dict(color='#555'),
                            capprops=dict(color='#555'),
                            flierprops=dict(marker='o', markerfacecolor='#E74C3C', markersize=5))

            mean_val = np.mean(vals)
            ax.scatter(pos, mean_val, color='white', edgecolors='black', s=40, zorder=5)
            ax.text(pos, mean_val + 0.3, f'{mean_val:.1f}', ha='center', va='bottom', fontsize=8, fontweight='bold')

    model_centers = [mi * group_spacing + (group_width - width) / 2 for mi in range(len(models))]
    ax.set_xticks(model_centers)
    ax.set_xticklabels([m.capitalize() for m in models], fontsize=11)

    legend_handles = [plt.Rectangle((0, 0), 1, 1, facecolor=assign_colors[i], alpha=0.6) for i in range(len(assignments))]
    ax.legend(legend_handles, assignments, loc='lower left', fontsize=9)

    ax.set_ylabel('Total Score (0-20)', fontsize=11)
    ax.set_title(f'Score Distribution by Writer and Assignment (p{prompt_num})', fontsize=13, fontweight='bold')
    ax.set_ylim(0, 22)
    ax.grid(axis='y', linestyle='--', alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    output = f'scores_p{prompt_num}_by_assignment.png'
    plt.savefig(output, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"Chart saved to {output}")
    plt.close()


def plot_by_dimension(df, prompt_num):
    """Scatter plot: dimension scores by writer, one chart per assignment."""
    models = ['chatgpt', 'claude', 'gemini', 'grok']
    short_dims = ['Issues', 'Evidence', 'Context', 'Position', 'Conclusions']
    model_colors = {
        'chatgpt': '#3498DB',
        'claude': '#2ECC71',
        'gemini': '#E67E22',
        'grok': '#9B59B6'
    }

    assignments = ['A1', 'A2', 'A3']
    assign_names = {'A1': 'Catlove', 'A2': 'Economic', 'A3': 'Real Estate'}
    fig, axes = plt.subplots(3, 1, figsize=(9, 10), sharey=True, sharex=True)
    x = np.arange(len(short_dims))

    for ri, assign in enumerate(assignments):
        ax = axes[ri]
        for mi, model in enumerate(models):
            means = []
            for dim in short_dims:
                vals = df[(df['Writer'] == model) & (df['Assignment'] == assign)][dim].values
                means.append(np.mean(vals) if len(vals) > 0 else 0)
            offset = (mi - 1.5) * 0.1
            ax.scatter(x + offset, means, color=model_colors[model],
                       s=80, zorder=5, label=model.capitalize() if ri == 0 else '')
            for i, m in enumerate(means):
                ax.text(x[i] + offset, m + 0.06, f'{m:.1f}',
                        ha='center', va='bottom', fontsize=7)

        ax.set_ylabel('Score (0-4)', fontsize=10)
        ax.set_title(f'{assign}: {assign_names[assign]}', fontsize=11, fontweight='bold')
        ax.set_ylim(2, 4.5)
        ax.grid(axis='y', linestyle='--', alpha=0.3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

    axes[2].set_xticks(x)
    axes[2].set_xticklabels(short_dims, fontsize=10)
    fig.legend(*axes[0].get_legend_handles_labels(), loc='upper right',
               fontsize=9, bbox_to_anchor=(0.98, 0.98))
    fig.suptitle(f'Dimension Scores by Writer and Assignment - p{prompt_num} (Generate)',
                 fontsize=13, fontweight='bold')

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    output = f'scores_p{prompt_num}_by_dimension.png'
    plt.savefig(output, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"Chart saved to {output}")
    plt.close()


if __name__ == '__main__':
    main()
