import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.colors as mcolors
import numpy as np
from matplotlib.patches import Patch
from matplotlib.lines import Line2D 




#
#visualize_scores.ipynb
#


def plot_avg_total_by_essaytype(avg_df, prompts, techniques):

    generate = [
        avg_df[
            (avg_df['Prompt']    == p) &
            (avg_df['EssayType'] == 'generate')
        ]['AvgTotal'].values[0]
        for p in prompts
    ]

    tune = [
        avg_df[
            (avg_df['Prompt']    == p) &
            (avg_df['EssayType'] == 'tune')
        ]['AvgTotal'].values[0]
        for p in prompts
    ]

    generate = np.array(generate)
    tune     = np.array(tune)
    x        = np.arange(len(prompts))

    fig, (ax1, ax2) = plt.subplots(
        2, 1,
        figsize=(18, 7),
        gridspec_kw={'height_ratios': [3, 1]}
    )

    fig.patch.set_facecolor('#f7f9fc')

    # ── dot chart ───
    ax1.set_facecolor('#f7f9fc')

    for i in range(len(prompts)):
        ax1.vlines(
            i,
            min(generate[i], tune[i]),
            max(generate[i], tune[i]),
            color='#cccccc', linewidth=2, zorder=1
        )

    ax1.scatter(
        x, generate,
        color='#2d6a4f', s=150, zorder=5,
        edgecolors='white', linewidths=1.5,
        label='Generate'
    )

    ax1.scatter(
        x, tune,
        color='#4361ee', s=150, zorder=5,
        edgecolors='white', linewidths=1.5,
        label='Tune'
    )

    ax1.set_xticks(x)
    ax1.set_xticklabels(
        ['P' + str(i) + '\n' + t for i, t in enumerate(techniques)],
        fontsize=8, ha='center',
        fontfamily='Times New Roman'
    )

    ax1.set_ylabel(
        'Average Total',
        fontfamily='Times New Roman', fontsize=11
    )

    ax1.set_title(
        'Generate vs Tune Essays — Average Total Score by Prompt',
        fontfamily='Times New Roman',
        fontsize=13, fontweight='bold'
    )

    ax1.set_ylim(16, 20.5)
    ax1.yaxis.grid(True, linestyle='--', alpha=0.4)
    ax1.set_axisbelow(True)
    ax1.legend(fontsize=11, frameon=False)

    for spine in ax1.spines.values():
        spine.set_visible(False)

    # ── table ─
    ax2.set_facecolor('#f7f9fc')
    ax2.axis('off')

    table_data = [
        list(generate.round(2)),
        list(tune.round(2))
    ]

    col_labels = ['P' + str(i) for i in range(len(prompts))]
    row_labels = ['Generate', 'Tune']

    table = ax2.table(
        cellText=table_data,
        rowLabels=row_labels,
        colLabels=col_labels,
        loc='center', cellLoc='center'
    )

    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.8)

    #max_gen  = np.argmax(generate)
    top3_gen = set(np.argsort(generate)[-3:])

    max_tune = np.argmax(tune)

    for c in range(len(prompts)):

        table[0, c].set_facecolor('#f7f9fc')
        table[0, c].set_text_props(
            fontweight='bold',
            fontfamily='Times New Roman'
        )

        table[1, c].set_facecolor('#ffcccc' if c in top3_gen else '#f7f9fc')
        table[1, c].set_text_props(
            fontweight='bold' if c in top3_gen else 'normal',
            color='#c1121f' if c in top3_gen else '#1a1a2e',
            fontfamily='Times New Roman'
        )

        table[2, c].set_facecolor('#ffcccc' if c == max_tune else '#f7f9fc')
        table[2, c].set_text_props(
            fontweight='bold' if c == max_tune else 'normal',
            color='#c1121f' if c == max_tune else '#1a1a2e',
            fontfamily='Times New Roman'
        )

    plt.tight_layout()
    plt.show()


def plot_bias_by_prompt_assignment(bias_df, prompt_labels):
    """Bar chart of Mean |Bias| per prompt technique grouped by Assignment."""

    assignment_colors = {
        'A1': '#4361ee',
        'A2': '#ef233c',
        'A3': '#06d6a0'
    }

    prompts     = sorted(bias_df['Prompt'].unique())
    assignments = sorted(bias_df['Assignment'].unique())

    n         = len(assignments)
    bar_width = 0.22
    offsets   = np.linspace(
        -(n - 1) * bar_width / 2,
         (n - 1) * bar_width / 2,
        n
    )

    x = np.arange(len(prompts))

    for etype in ['generate', 'tune']:

        subset = bias_df[bias_df['EssayType'] == etype]

        fig, ax = plt.subplots(figsize=(14, 4.5))
        fig.patch.set_facecolor('#f7f9fc')
        ax.set_facecolor('#e8e8e8')

        for ai, assignment in enumerate(assignments):

            vals = [
                subset[
                    (subset['Prompt']     == p) &
                    (subset['Assignment'] == assignment)
                ]['MeanBias'].values[0]
                for p in prompts
            ]

            bars = ax.bar(
                x + offsets[ai],
                vals,
                width=bar_width,
                color=assignment_colors[assignment],
                alpha=0.85,
                label=assignment,
                zorder=3
            )

            for bar in bars:
                h = bar.get_height()
                if not np.isnan(h) and h > 0:
                    ax.text(
                        bar.get_x() + bar.get_width() / 2,
                        h + 0.005,
                        str(round(h, 2)),
                        ha='center', fontsize=5,
                        fontfamily='Times New Roman',
                        color='#333333'
                    )

        ax.set_xticks(x)
        ax.set_xticklabels(
            [prompt_labels.get(p, p) for p in prompts],
            fontfamily='Times New Roman',
            fontsize=8, rotation=25,
            ha='right', color='#555555'
        )

        ax.set_ylim(0, 0.6)
        ax.set_yticks([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6])
        ax.set_ylabel(
            'Mean |Bias|',
            fontfamily='Times New Roman',
            fontsize=9, color='#555555'
        )

        ax.yaxis.grid(True, linestyle='--', alpha=0.25, zorder=0)
        ax.set_axisbelow(True)

        for spine in ax.spines.values():
            spine.set_visible(False)

        ax.tick_params(axis='x', which='both', bottom=False)

        ax.legend(
            fontsize=9,
            prop={'family': 'Times New Roman'},
            framealpha=0, loc='upper right'
        )

        plt.tight_layout(rect=[0, 0.08, 1, 1])

        fig.text(
            0.5, 0.01,
            'Mean |Bias| = average distance each grader is from group consensus per assignment. '
            'Higher = more grader disagreement on that prompt technique.',
            ha='center', fontsize=7,
            fontfamily='Times New Roman',
            color='#666666', style='italic'
        )

        plt.suptitle(
            'Bias by Prompt Technique and Assignment: ' + etype.capitalize(),
            fontfamily='Times New Roman',
            fontsize=13, fontweight='bold',
            color='#111111', y=1.02
        )

        plt.show()



def all_models_performance(avg_df, writers, prompts, technique_groups, prompt_labels):
    """Dot chart of mean Total score per writer across prompt techniques, split by EssayType."""

    group_order = [
        'Baseline',
        'Single',
        'Double',
        'Iterative_Prompt',
        'Iterative_Prompt_Complex'
    ]

    prompt_order = [
        p for g in group_order
        for p in technique_groups[g]
        if p in prompts
    ]

    colors = {
        'chatgpt': '#3498DB',
        'claude':  '#2ECC71',
        'gemini':  '#E67E22',
        'grok':    '#9B59B6'
    }

    n_writers = len(writers)
    n_prompts = len(prompt_order)
    bar_width  = 0.18
    group_gap  = 0.1

    fig, axes = plt.subplots(
        2, 1, figsize=(20, 10),
        sharex=True
    )
    fig.patch.set_facecolor('#f7f9fc')

    for ax, etype, title in zip(axes, ['generate', 'tune'], ['Generate', 'Tune']):

        ax.set_facecolor('#f7f9fc')

        for i, writer in enumerate(writers):

            color  = colors.get(writer, 'gray')
            offset = (i - n_writers / 2 + 0.5) * (bar_width + group_gap / n_writers)
            x_pos  = [j + offset for j in range(n_prompts)]

            vals = [
                avg_df[
                    (avg_df['EssayType'] == etype)   &
                    (avg_df['Writer']    == writer)   &
                    (avg_df['Prompt']    == p)
                ]['AvgTotal'].values[0]
                for p in prompt_order
            ]

            ax.scatter(
                x_pos, vals,
                color=color, s=80,
                zorder=5,
                label=writer.capitalize()
            )

            for x, val in zip(x_pos, vals):
                ax.text(
                    x, val + 0.05, str(val),
                    ha='center', va='bottom',
                    fontsize=6.5, color=color,
                    fontfamily='Times New Roman'
                )

        # group dividers
        pos = 0
        for group in group_order:
            ps = [p for p in technique_groups[group] if p in prompt_order]
            pos += len(ps)
            if pos < n_prompts:
                ax.axvline(
                    pos - 0.5,
                    color='#cccccc',
                    linewidth=1.5,
                    linestyle='--',
                    zorder=2
                )

        ax.set_ylim(16, 20.5)
        ax.set_ylabel(
            'Mean Total Score',
            fontfamily='Times New Roman',
            fontsize=10
        )
        ax.set_title(
            title,
            fontfamily='Times New Roman',
            fontsize=12,
            fontweight='bold',
            loc='left'
        )
        ax.grid(axis='y', linestyle='--', alpha=0.4, zorder=0)

        for spine in ax.spines.values():
            spine.set_visible(False)

    # group labels on top
    ax2 = axes[0].twiny()
    ax2.set_xlim(axes[0].get_xlim())

    group_centers = []
    pos = 0
    for group in group_order:
        ps = [p for p in technique_groups[group] if p in prompt_order]
        group_centers.append(pos + len(ps) / 2 - 0.5)
        pos += len(ps)

    ax2.set_xticks(group_centers)
    ax2.set_xticklabels(
        [g.replace('_', ' ') for g in group_order],
        fontfamily='Times New Roman',
        fontsize=10,
        fontweight='bold'
    )
    ax2.tick_params(length=0)
    for spine in ax2.spines.values():
        spine.set_visible(False)

    # x axis labels
    axes[-1].set_xticks(range(n_prompts))
    axes[-1].set_xticklabels(
        [p + '\n' + prompt_labels.get(p, '') for p in prompt_order],
        fontfamily='Times New Roman',
        fontsize=8,
        ha='center'
    )

    legend_handles = [
        Line2D(
            [0], [0], marker='o', color='w',
            markerfacecolor=colors[w], markersize=9,
            label=w.capitalize()
        )
        for w in writers
    ]

    axes[1].legend(
        handles=legend_handles,
        loc='lower right',
        fontsize=9,
        frameon=False,
        prop={'family': 'Times New Roman'}
    )

    fig.suptitle(
        'Generate vs Tune: Score by Prompt Technique',
        fontfamily='Times New Roman',
        fontsize=14,
        fontweight='bold',
        y=1.01
    )

    plt.show()


def plot_trend(trend_df, prompt_order, writers, technique_groups, prompt_labels):
    """Line chart showing generate vs tune trend per writer across prompt techniques."""

    group_order = [
        'Baseline',
        'Single',
        'Double',
        'Iterative_Prompt',
        'Iterative_Prompt_Complex'
    ]

    colors = {
        'chatgpt': '#3498DB',
        'claude':  '#2ECC71',
        'gemini':  '#E67E22',
        'grok':    '#9B59B6'
    }

    fig, axes = plt.subplots(
        len(writers), 1,
        figsize=(16, 5 * len(writers)),
        sharex=True
    )
    fig.patch.set_facecolor('#f7f9fc')

    if len(writers) == 1:
        axes = [axes]

    for ax, writer in zip(axes, writers):

        color = colors.get(writer, 'gray')
        ax.set_facecolor('#f7f9fc')

        for etype, style, marker in [
            ('generate', 'solid',  'o'),
            ('tune',     'dashed', 's')
        ]:
            vals = [
                trend_df[
                    (trend_df['EssayType'] == etype)  &
                    (trend_df['Writer']    == writer)  &
                    (trend_df['Prompt']    == p)
                ]['AvgTotal'].values[0]
                for p in prompt_order
            ]

            ax.plot(
                range(len(prompt_order)), vals,
                color=color, linewidth=2,
                marker=marker, markersize=6,
                linestyle=style,
                label=etype.capitalize(),
                zorder=5
            )

        # shaded gap
        gen_vals = [
            trend_df[
                (trend_df['EssayType'] == 'generate') &
                (trend_df['Writer']    == writer)      &
                (trend_df['Prompt']    == p)
            ]['AvgTotal'].values[0]
            for p in prompt_order
        ]

        tune_vals = [
            trend_df[
                (trend_df['EssayType'] == 'tune') &
                (trend_df['Writer']    == writer)  &
                (trend_df['Prompt']    == p)
            ]['AvgTotal'].values[0]
            for p in prompt_order
        ]

        ax.fill_between(
            range(len(prompt_order)),
            gen_vals, tune_vals,
            color=color, alpha=0.08
        )

        for x, val in enumerate(gen_vals):
            ax.text(
                x, val, str(val),
                fontsize=8, color=color,
                fontfamily='Times New Roman',
                ha='center'
            )

        for x, val in enumerate(tune_vals):
            ax.text(
                x, val, str(val),
                fontsize=8, color=color,
                fontfamily='Times New Roman',
                ha='center'
            )

        # group dividers
        pos = 0
        for group in group_order:
            ps = [p for p in technique_groups[group] if p in prompt_order]
            pos += len(ps)
            if pos < len(prompt_order):
                ax.axvline(
                    pos - 0.5,
                    color='#cccccc',
                    linewidth=1.5,
                    linestyle='--',
                    zorder=2
                )

        ax.set_ylabel(
            'Mean Total Score',
            fontfamily='Times New Roman',
            fontsize=10
        )
        ax.set_title(
            writer.capitalize(),
            fontfamily='Times New Roman',
            fontsize=12,
            fontweight='bold',
            loc='left'
        )
        ax.legend(
            loc='lower right',
            fontsize=9,
            frameon=False,
            prop={'family': 'Times New Roman'}
        )
        ax.grid(axis='y', linestyle='--', alpha=0.4)

        for spine in ax.spines.values():
            spine.set_visible(False)

    # group labels on top
    ax2 = axes[0].twiny()
    ax2.set_xlim(axes[0].get_xlim())

    group_centers = []
    pos = 0
    for group in group_order:
        ps = [p for p in technique_groups[group] if p in prompt_order]
        group_centers.append(pos + len(ps) / 2 - 0.5)
        pos += len(ps)

    ax2.set_xticks(group_centers)
    ax2.set_xticklabels(
        [g.replace('_', ' ') for g in group_order],
        fontfamily='Times New Roman',
        fontsize=10,
        fontweight='bold'
    )
    ax2.tick_params(length=0)
    for spine in ax2.spines.values():
        spine.set_visible(False)

    # x axis labels
    axes[-1].set_xticks(range(len(prompt_order)))
    axes[-1].set_xticklabels(
        [p + '\n' + prompt_labels.get(p, '') for p in prompt_order],
        fontfamily='Times New Roman',
        fontsize=8,
        ha='center'
    )

    fig.suptitle(
        'Prompt Complexity Effects on Generate vs Tuned Essays',
        fontfamily='Times New Roman',
        fontsize=14,
        fontweight='bold',
        y=1.01
    )

    plt.tight_layout()
    plt.show()



#
#visualize_scores_p0.ipynb
#


#1: Compute grader stats (metric.py) before runnng the plot.
def cross_grading_scores_by_essaytype(stats_df, writers, dimensions, target_writer=None):

    grader_colors = {
        'chatgpt': '#4361ee',
        'claude':  '#06d6a0',
        'gemini':  '#f4a261',
        'grok':    '#ef233c'
    }

    for etype in ['generate', 'tune']:

        targets = [target_writer] if target_writer else writers

        fig, axes = plt.subplots(
            1, len(targets),
            figsize=(len(targets) * 3.4, 3.8),
            sharey=True
        )

        fig.subplots_adjust(wspace=0.10)
        axes = np.atleast_1d(axes)
        fig.patch.set_facecolor('#f7f9fc')

        offsets = np.linspace(-0.25, 0.25, len(writers))

        for col, writer in enumerate(targets):

            ax = axes[col]
            ax.set_facecolor('#e8e8e8')

            for i in range(len(dimensions)):
                ax.axvline(i, color='#dddddd', linewidth=0.7, zorder=1)

            for gi, grader in enumerate(writers):

                for i, dimension in enumerate(dimensions):

                    row = stats_df[
                        (stats_df['EssayType'] == etype)      &
                        (stats_df['Writer']    == writer)     &
                        (stats_df['Grader']    == grader)     &
                        (stats_df['Dimension'] == dimension)
                    ]

                    if row.empty or row['N'].values[0] == 0:
                        continue

                    ax.errorbar(
                        i + offsets[gi],
                        row['Mean'].values[0],
                        yerr=row['Std'].values[0],
                        fmt='o',
                        color=grader_colors[grader],
                        markersize=5,
                        capsize=3,
                        capthick=1.2,
                        elinewidth=1.2,
                        zorder=4
                    )

            ax.set_xticks(range(len(dimensions)))
            ax.set_xticklabels(
                dimensions,
                fontfamily='Times New Roman',
                fontsize=7,
                color='#888888',
                rotation=25,
                ha='right'
            )

            ax.set_ylim(0.0, 4.5)
            ax.set_yticks([0, 1.0, 2.0, 3.0, 4.0])
            ax.yaxis.grid(True, linestyle='--', alpha=0.25, zorder=2)
            ax.set_axisbelow(True)

            for spine in ax.spines.values():
                spine.set_visible(False)

            ax.tick_params(axis='x', which='both', bottom=False)

            if col == 0:
                ax.tick_params(axis='y', labelsize=7)
                ax.set_ylabel(
                    'Avg Score',
                    fontfamily='Times New Roman',
                    fontsize=8,
                    color='#555555'
                )
            else:
                ax.tick_params(axis='y', labelleft=False, left=False)

            ax.set_title(
                writer.capitalize(),
                fontfamily='Times New Roman',
                fontsize=11,
                fontweight='bold',
                color='#111111',
                pad=10
            )

        legend_elements = [
            Line2D(
                [0], [0],
                marker='o', color='w',
                markerfacecolor=grader_colors[g],
                markersize=8,
                label=g.capitalize()
            )
            for g in writers
        ] + [
            Line2D(
                [0], [0],
                color='grey', linewidth=1.2,
                label='Error bars = ±SD'
            )
        ]

        fig.legend(
            handles=legend_elements,
            loc='lower center',
            ncol=len(writers) + 1,
            fontsize=8.5,
            prop={'family': 'Times New Roman'},
            framealpha=0,
            bbox_to_anchor=(0.5, -0.08)
        )

        plt.suptitle(
            f'Cross Grading Performance: {etype.capitalize()}',
            fontfamily='Times New Roman',
            fontsize=13,
            fontweight='bold',
            color='#111111',
            y=1.04
        )

        plt.tight_layout(w_pad=0)
        fig.subplots_adjust(wspace=0.10)
        plt.show()


#2: Compute assignment_bias (metric.py) before runnig the plot.
def grading_bias_by_assignment(assignment_bias, writers, target_writer=None):

    assignments = sorted(assignment_bias['Assignment'].unique())
    targets     = [target_writer] if target_writer else writers

    assignment_colors = {
        a: c for a, c in zip(
            assignments,
            ['#4361ee', '#ef233c', '#06d6a0', '#f4a261']
        )
    }

    definition = (
        'Mean |Bias| = average distance each grader is from the group consensus. '
        '0.0 = perfect agreement. Higher = more grader disagreement on that assignment.'
    )

    for etype in ['generate', 'tune']:

        fig, axes = plt.subplots(
            1, len(targets),
            figsize=(len(targets) * 3.4, 3.8),
            sharey=True
        )

        fig.subplots_adjust(wspace=0.10, bottom=0.18)
        axes = np.atleast_1d(axes)
        fig.patch.set_facecolor('#f7f9fc')

        x = np.arange(len(assignments))

        for col, writer in enumerate(targets):

            ax = axes[col]
            ax.set_facecolor('#e8e8e8')

            subset = assignment_bias[
                (assignment_bias['EssayType'] == etype) &
                (assignment_bias['Writer']    == writer)
            ]

            mean_abs_bias = [
                subset[subset['Assignment'] == a]['Mean_AbsBias'].mean()
                for a in assignments
            ]

            ax.bar(
                x,
                mean_abs_bias,
                color=[assignment_colors[a] for a in assignments],
                alpha=0.85,
                zorder=3,
                width=0.4
            )

            for i, val in enumerate(mean_abs_bias):
                if not np.isnan(val):
                    ax.text(
                        x[i], val + 0.005,
                        str(round(val, 3)),
                        ha='center', fontsize=7,
                        fontfamily='Times New Roman',
                        color='#333333'
                    )

            ax.set_xticks(x)
            ax.set_xticklabels(
                assignments,
                fontfamily='Times New Roman',
                fontsize=8,
                color='#555555'
            )

            ax.set_ylim(0, 1.0)
            ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
            ax.yaxis.grid(True, linestyle='--', alpha=0.25, zorder=0)
            ax.set_axisbelow(True)

            for spine in ax.spines.values():
                spine.set_visible(False)

            ax.tick_params(axis='x', which='both', bottom=False)

            if col == 0:
                ax.tick_params(axis='y', labelsize=7)
                ax.set_ylabel(
                    'Mean |Bias|',
                    fontfamily='Times New Roman',
                    fontsize=8,
                    color='#555555'
                )
            else:
                ax.tick_params(axis='y', labelleft=False, left=False)

            ax.set_title(
                writer.capitalize() + ' (writer)',
                fontfamily='Times New Roman',
                fontsize=11,
                fontweight='bold',
                color='#111111',
                pad=10
            )

        legend_elements = [
            Patch(facecolor=assignment_colors[a], alpha=0.85, label=a)
            for a in assignments
        ]

        fig.legend(
            handles=legend_elements,
            loc='lower center',
            ncol=len(assignments),
            fontsize=8.5,
            prop={'family': 'Times New Roman'},
            framealpha=0,
            bbox_to_anchor=(0.5, -0.20)
        )

        # ── definition under chart ────────────────────────────────────────────
        fig.text(
            0.5, 0.01,
            definition,
            ha='center',
            fontsize=7,
            fontfamily='Times New Roman',
            color='#666666',
            style='italic',
            wrap=True
        )

        plt.suptitle(
            'Writer Performance by Assignment:' + etype.capitalize(),
            fontfamily='Times New Roman',
            fontsize=13,
            fontweight='bold',
            color='#111111',
            y=1.04
        )

        plt.tight_layout(w_pad=0)
        fig.subplots_adjust(wspace=0.10, bottom=0.18)
        plt.show()

