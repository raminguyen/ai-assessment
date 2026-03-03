import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pathlib import Path

OUTPUT_DIR = Path('src/visualization/rubric_plots')
CSV_PATH = Path('src/word_count_results.csv')

MODEL_COLORS = {
    'chatgpt': '#3498DB',
    'claude': '#2ECC71',
    'gemini': '#E67E22',
    'grok': '#9B59B6'
}

TECHNIQUE_NAMES = [
    'Persona\n+ Write', 'Persona\n+ Write Formal', 'CoT\n+ Write',
    'Generate', 'CoT\n+ Generate', 'Persona\n+ Generate',
    'Iter + Persona\n+ Generate', 'Iter + Persona\n+ Write',
    'Iter\n+ Generate', 'Iter + CoT\n+ Generate'
]

def load_data():
    df = pd.read_csv(CSV_PATH, skiprows=[1])  # skip technique row
    prompt_cols = [f'p{i}' for i in range(1, 11)]
    for col in prompt_cols:
        df[col] = pd.to_numeric(df[col])
    return df, prompt_cols


def plot_avg_by_prompt():
    """Chart 1: Boxplot of word count by prompt technique (all models)."""
    df, prompt_cols = load_data()

    # Each prompt column has 12 values (4 models x 3 assignments)
    box_data = [df[col].values for col in prompt_cols]

    fig, ax = plt.subplots(figsize=(14, 6))
    x = np.arange(1, len(prompt_cols) + 1)

    bp = ax.boxplot(box_data, positions=x, widths=0.5, patch_artist=True,
                    boxprops=dict(facecolor='#3498DB', alpha=0.6),
                    medianprops=dict(color='#E74C3C', linewidth=2),
                    whiskerprops=dict(color='#555'),
                    capprops=dict(color='#555'),
                    flierprops=dict(marker='o', markerfacecolor='#E74C3C', markersize=5))

    # Add mean markers
    means = [np.mean(d) for d in box_data]
    ax.scatter(x, means, color='white', edgecolors='black', s=50, zorder=5, label='Mean')

    # Label mean values
    for i, m in enumerate(means):
        ax.text(x[i], m + 15, f'{m:.0f}', ha='center', va='bottom', fontsize=8, fontweight='bold')

    ax.set_xticks(x)
    ax.set_xticklabels(TECHNIQUE_NAMES, fontsize=8)
    ax.set_ylabel('Word Count', fontsize=11)
    ax.set_title('Word Count Distribution by Prompt Technique (All Models)', fontsize=13, fontweight='bold')
    ax.legend(loc='lower right', fontsize=9)
    ax.grid(axis='y', linestyle='--', alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    output_path = OUTPUT_DIR / 'word_count_by_prompt.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"Saved to {output_path}")
    plt.close()


def plot_avg_by_model_and_assignment():
    """Chart 2: Boxplot of word count by model, grouped by assignment."""
    df, prompt_cols = load_data()

    models = ['chatgpt', 'claude', 'gemini', 'grok']
    assignments = ['Assignment 1', 'Assignment 2', 'Assignment 3']
    assign_colors = ['#3498DB', '#E67E22', '#2ECC71']

    fig, ax = plt.subplots(figsize=(12, 6))

    n_assign = len(assignments)
    width = 0.6
    gap = 0.2
    group_width = n_assign * width + (n_assign - 1) * gap
    group_spacing = group_width + 1.5

    positions_map = []  # for xticks

    for mi, model in enumerate(models):
        group_start = mi * group_spacing
        for ai, assign in enumerate(assignments):
            row = df[(df['Model'] == model) & (df['Assignment'] == assign)]
            if row.empty:
                continue
            vals = row[prompt_cols].values.flatten()
            pos = group_start + ai * (width + gap)
            positions_map.append((pos, model, assign))

            bp = ax.boxplot([vals], positions=[pos], widths=width, patch_artist=True,
                            boxprops=dict(facecolor=assign_colors[ai], alpha=0.6),
                            medianprops=dict(color='#E74C3C', linewidth=2),
                            whiskerprops=dict(color='#555'),
                            capprops=dict(color='#555'),
                            flierprops=dict(marker='o', markerfacecolor='#E74C3C', markersize=5))

            mean_val = np.mean(vals)
            ax.scatter(pos, mean_val, color='white', edgecolors='black', s=40, zorder=5)
            ax.text(pos, mean_val + 15, f'{mean_val:.0f}', ha='center', va='bottom', fontsize=7, fontweight='bold')

    # X-axis: model labels centered on each group
    model_centers = [mi * group_spacing + (group_width - width) / 2 for mi in range(len(models))]
    ax.set_xticks(model_centers)
    ax.set_xticklabels([m.capitalize() for m in models], fontsize=11)

    # Legend
    legend_handles = [plt.Rectangle((0, 0), 1, 1, facecolor=assign_colors[i], alpha=0.6) for i in range(n_assign)]
    ax.legend(legend_handles, assignments, loc='upper right', fontsize=9)

    ax.set_ylabel('Word Count', fontsize=11)
    ax.set_title('Word Count Distribution by Model and Assignment', fontsize=13, fontweight='bold')
    ax.grid(axis='y', linestyle='--', alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    output_path = OUTPUT_DIR / 'word_count_by_model_assignment.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"Saved to {output_path}")
    plt.close()


if __name__ == '__main__':
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    plot_avg_by_prompt()
    plot_avg_by_model_and_assignment()
