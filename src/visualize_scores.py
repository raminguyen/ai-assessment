import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.colors as mcolors
import numpy as np
from matplotlib.patches import Patch
from matplotlib.lines import Line2D 


def avg_total_score_by_essay_type(scores, prompts, techniques):

    df = scores.pivot_table(index='EssayType', columns='Prompt', values='Total').round(2)

    generate = df.loc['generate', prompts].values
    
    tune     = df.loc['tune', prompts].values

    x = np.arange(len(prompts))

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(18, 7),
                                    gridspec_kw={'height_ratios': [3, 1]})
    fig.patch.set_facecolor('#f7f9fc')

    # --- dot chart ---
    ax1.set_facecolor('#f7f9fc')

    for i in range(len(prompts)):
        ax1.vlines(i, min(generate[i], tune[i]), max(generate[i], tune[i]),
                   color='#cccccc', linewidth=2, zorder=1)
        
    ax1.scatter(x, generate, color='#2d6a4f', s=150, zorder=5,
                edgecolors='white', linewidths=1.5, label='Generate')
    
    ax1.scatter(x, tune, color='#4361ee', s=150, zorder=5,
                edgecolors='white', linewidths=1.5, label='Tune')
    
    ax1.set_xticks(x)
    
    ax1.set_xticklabels([f'P{i}\n{t}' for i, t in enumerate(techniques)],
                         fontsize=8, ha='center', fontfamily='Times New Roman')
    
    ax1.set_ylabel('Average Total', fontfamily='Times New Roman', fontsize=11)

    ax1.set_title('Generate vs Tune Essays — Average Total Score by Prompt',
                  fontfamily='Times New Roman', fontsize=13, fontweight='bold')
    
    ax1.set_ylim(16, 20.5)
    
    ax1.yaxis.grid(True, linestyle='--', alpha=0.4)
    ax1.set_axisbelow(True)

    ax1.legend(fontsize=11, frameon=False)

    for spine in ax1.spines.values():
        spine.set_visible(False)

    # --- table ---
    ax2.set_facecolor('#f7f9fc')
    ax2.axis('off')

    table_data = [
    list(generate.round(2)),
    list(tune.round(2))
]

    col_labels = ['P' + str(i) for i in range(len(prompts))]
    row_labels = ['Generate', 'Tune']


    table = ax2.table(cellText=table_data,
                      rowLabels=row_labels,
                      colLabels=col_labels,
                      loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.8)

    # highlight max in red
    max_gen = np.argmax(generate)
    max_tune = np.argmax(tune)

    for c in range(len(prompts)):

        # header row
        table[0, c].set_facecolor('#f7f9fc')

        table[0, c].set_text_props(fontweight='bold', fontfamily='Times New Roman')

        # generate row (row 1)
        table[1, c].set_facecolor('#ffcccc' if c == max_gen else '#f7f9fc')
        table[1, c].set_text_props(
            fontweight='bold' if c == max_gen else 'normal',
            color='#c1121f' if c == max_gen else '#1a1a2e',
            fontfamily='Times New Roman')
        
        # tune row (row 2)
        table[2, c].set_facecolor('#ffcccc' if c == max_tune else '#f7f9fc')
        table[2, c].set_text_props(
            fontweight='bold' if c == max_tune else 'normal',
            color='#c1121f' if c == max_tune else '#1a1a2e',
            fontfamily='Times New Roman')


    plt.show()

def writer_performance(scores, dimensions, writers):

    writer_colors = {
        'chatgpt': '#4361ee',
        'claude':  '#06d6a0',
        'gemini':  '#f4a261',
        'grok':    '#ef233c'
    }

    essay_types = ['generate', 'tune']
    titles      = {
        'generate': 'Writer Performance Across Dimensions — Generate',
        'tune':     'Writer Performance Across Dimensions — Tune'
    }

    fig, axes = plt.subplots(1, 2, figsize=(20, 6), sharey=True)
    fig.patch.set_facecolor('#f7f9fc')

    for ax, etype in zip(axes, essay_types):

        subset = scores[scores['EssayType'] == etype]
        ax.set_facecolor('#f7f9fc')

        for writer in writers:
            means = [subset[subset['Writer'] == writer][dim].mean()
                     for dim in dimensions]

            ax.plot(dimensions, means,
                    marker='o', markersize=10, linewidth=2.5,
                    color=writer_colors[writer],
                    label=writer.capitalize())

            ax.text(len(dimensions) - 0.95, means[-1],
                    writer.capitalize(),
                    fontsize=9, color=writer_colors[writer],
                    fontweight='bold', fontfamily='Times New Roman',
                    va='center')

        ax.set_ylim(2.8, 4.35)
        ax.set_ylabel('Avg Score', fontfamily='Times New Roman', fontsize=11)
        ax.set_title(titles[etype],
                     fontfamily='Times New Roman', fontsize=13, fontweight='bold')
        
        ax.axhline(3.5, color='red', linewidth=1, linestyle='--', alpha=0.4)
        
        ax.yaxis.grid(True, linestyle='--', alpha=0.4)
        ax.set_axisbelow(True)
        ax.set_xlim(-0.3, len(dimensions) - 0.5)

        for label in ax.get_xticklabels():
            label.set_fontfamily('Times New Roman')
            label.set_fontsize(10)
        for spine in ax.spines.values():
            spine.set_visible(False)

    plt.tight_layout()
    plt.show()

def writer_performance_by_assignment(scores, writers):

    assignments = ['A1', 'A2', 'A3']
    labels      = ['A1: Catlove', 'A2: Economic', 'A3: Real Estate']
    essay_types = ['generate', 'tune']
    
    titles      = {
        'generate': 'Writer Performance by Assignment — Generate',
        'tune':     'Writer Performance by Assignment — Tune'
    }

    dfs = {}

    for etype in essay_types:

        subset = scores[scores['EssayType'] == etype]

        df = subset.groupby(['Writer', 'Assignment'])['Total'].mean().round(2).unstack()

        df = df.reindex(writers)[assignments]

        df.columns = labels

        df.index = [w.capitalize() for w in writers]

        dfs[etype] = df

        fig, ax = plt.subplots(figsize=(10, 5))

        fig.patch.set_facecolor('#f7f9fc')

        ax.set_facecolor('#f7f9fc')

        data = df.values

        norm = mcolors.Normalize(vmin=data.min(), vmax=data.max())

        im = ax.imshow(data, cmap='YlGnBu', norm=norm, aspect='auto')

        for r in range(len(writers)):
            for c in range(len(labels)):
                val = data[r, c]
                ax.text(c, r, str(round(val, 2)),
                        ha='center', va='center',
                        fontsize=11, fontweight='bold',
                        color='white' if val > data.mean() else '#1a3a5c',
                        fontfamily='Times New Roman')

        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, fontfamily='Times New Roman', fontsize=10)
        ax.set_yticks(range(len(writers)))
        ax.set_yticklabels([w.capitalize() for w in writers],
                            fontfamily='Times New Roman', fontsize=11)
        ax.set_title(titles[etype],
                     fontfamily='Times New Roman', fontsize=13, fontweight='bold')

        for x in np.arange(-0.5, len(labels), 1):
            ax.axvline(x, color='#f7f9fc', linewidth=2)
        for y in np.arange(-0.5, len(writers), 1):
            ax.axhline(y, color='#f7f9fc', linewidth=2)
        for spine in ax.spines.values():
            spine.set_visible(False)

        plt.colorbar(im, ax=ax, shrink=0.8, pad=0.02, location='right')
        plt.tight_layout()
        plt.show()

    return dfs  


def writer_performance_by_technique(scores, writers, prompts, techniques, technique_groups, essay_type='generate'):

    # build df

    df_filtered = scores[scores['EssayType'] == essay_type]

    df = df_filtered.groupby(['Writer', 'Prompt'])['Total'].mean().round(2).unstack()


    df = df.reindex(writers)[prompts]

    df.index = [w.capitalize() for w in writers]

    # reorder prompts by group
    group_order = [
        'Baseline',
        'Single',
        'Double',
        'Iterative_Prompt',
        'Iterative_Prompt_Complex'
    ]

    prompt_order = []

    group_boundaries = []

    group_centers = []

    for group in group_order:

        ps = technique_groups[group]

        group_boundaries.append(len(prompt_order) - 0.5)

        group_centers.append(len(prompt_order) + len(ps) / 2 - 0.5)

        prompt_order.extend(ps)

    group_boundaries.append(len(prompt_order) - 0.5)

    df = df[prompt_order]
    data = df.values

    fig, ax = plt.subplots(figsize=(22, 5))
    fig.patch.set_facecolor('#f7f9fc')
    ax.set_facecolor('#f7f9fc')

    norm = mcolors.Normalize(vmin=data.min(), vmax=data.max())
    im = ax.imshow(data, cmap='YlGnBu', norm=norm, aspect='auto')

    for r in range(len(writers)):
        for c in range(len(prompt_order)):
            val = data[r, c]
            ax.text(c, r, str(round(val, 2)),
                    ha='center', va='center',
                    fontsize=10, fontweight='bold',
                    color='white' if val > data.mean() else '#1a3a5c',
                    fontfamily='Times New Roman')

    # group dividers
    for b in group_boundaries[1:-1]:
        ax.axvline(b, color='white', linewidth=3, zorder=5)

    # group labels on top
    ax2 = ax.twiny()

    ax2.set_xlim(ax.get_xlim())

    ax2.set_xticks(group_centers)

    ax2.set_xticklabels(group_order, fontfamily='Times New Roman',
                         fontsize=11, fontweight='bold')
    
    ax2.tick_params(length=0)
    for spine in ax2.spines.values():
        spine.set_visible(False)

    # prompt labels on bottom
    ax.set_xticks(range(len(prompt_order)))

    ax.set_xticklabels(
        [p + '\n' + techniques[prompts.index(p)] for p in prompt_order],
        fontfamily='Times New Roman', fontsize=8, ha='center'
    )

    persona_prompts = ['p1', 'p2', 'p6', 'p8', 'p7']  # all prompts with Role-based

    for tick, p in zip(ax.get_xticklabels(), prompt_order):
        if p in persona_prompts:
            tick.set_fontweight('bold')
            tick.set_color('#1a3a5c')


    for c, p in enumerate(prompt_order):
        if p in persona_prompts:
            ax.add_patch(plt.Rectangle(
                (c - 0.5, -0.5),          # bottom-left corner
                1,                          # width = one column
                len(writers),               # height = all rows
                linewidth=2,
                edgecolor='red',
                facecolor='none',
                zorder=10,
                clip_on=False
            ))

    legend_elements = [
        
    Patch(facecolor='none', edgecolor='red', linewidth=2, label='Persona prompts')
]

    ax.legend(
        handles=legend_elements,
        loc='lower left',
        bbox_to_anchor=(0, -0.35),
        fontsize=10,
        frameon=False,
        prop={'family': 'Times New Roman'}
    )

    ax.set_yticks(range(len(writers)))

    ax.set_yticklabels([w.capitalize() for w in writers],
                        fontfamily='Times New Roman', fontsize=11)
    
    ax.set_title('Writer Performance by Technique Group',
                 fontfamily='Times New Roman', fontsize=13,
                 fontweight='bold', pad=25)

    for y in np.arange(-0.5, len(writers), 1):
        ax.axhline(y, color='#f7f9fc', linewidth=2)
    for spine in ax.spines.values():
        spine.set_visible(False)

    plt.colorbar(im, ax=ax, shrink=0.8, pad=0.02, location='right')
    
    plt.show()

    return df

def plot_trend(scores, writers, prompts, technique_groups):

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

    technique_labels = {
        'p0':  'Baseline',
        'p1':  'Role-based',
        'p2':  'Role-based\n+ Formal',
        'p3':  'Chain of\nThought',
        'p4':  'Generate\nKnowledge',
        'p5':  'CoT +\nGen Know',
        'p6':  'Role +\nGen Know',
        'p7':  'Role + CoT\n+ Gen Know',
        'p8':  'Iter +\nRole',
        'p9':  'Iter +\nGen Know',
        'p10': 'Iter + CoT\n+ Gen Know',
        'p11': 'Iter +\nOriginal'
    }

    # one row per writer
    fig, axes = plt.subplots(
        len(writers), 1,
        figsize=(16, 5 * len(writers)),
        sharex=True
    )
    fig.patch.set_facecolor('#f7f9fc')

    # make iterable if only one writer
    if len(writers) == 1:
        axes = [axes]

    for ax, writer in zip(axes, writers):

        color = colors.get(writer, 'gray')
        ax.set_facecolor('#f7f9fc')
        

        # plot generate and tune lines
        for essay_type, style, marker in [
            ('generate', 'solid',  'o'),
            ('tune',     'dashed', 's')
        ]:
            vals = (
                scores[scores['EssayType'] == essay_type]
                .groupby(['Writer', 'Prompt'])['Total']
                .mean().round(2)
                .unstack()
                .reindex([writer])[prompt_order]
                .values.flatten()
            )

            ax.plot(
                range(len(prompt_order)), vals,
                color=color, linewidth=2,
                marker=marker, markersize=6,
                linestyle=style,
                label=f'{essay_type.capitalize()}',
                zorder=5
            )

        # compute gen and tune for shaded gap + labels
        gen = (
            scores[scores['EssayType'] == 'generate']
            .groupby(['Writer', 'Prompt'])['Total']
            .mean().round(2)
            .unstack()
            .reindex([writer])[prompt_order]
            .values.flatten()
        )

        tune = (
            scores[scores['EssayType'] == 'tune']
            .groupby(['Writer', 'Prompt'])['Total']
            .mean().round(2)
            .unstack()
            .reindex([writer])[prompt_order]
            .values.flatten()
        )

        # shaded gap between generate and tune
        ax.fill_between(
            range(len(prompt_order)),
            gen, tune,
            color=color, alpha=0.08
        )
        for x, val in enumerate(gen):
            t = ax.text(
                x, val, str(val),
                fontsize=8, color=color,
                fontfamily='Times New Roman',
                ha='center'
            )
        

        for x, val in enumerate(tune):
            t = ax.text(
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

    # group labels on top — first subplot only
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

    # x axis labels — last subplot only
    axes[-1].set_xticks(range(len(prompt_order)))

    axes[-1].set_xticklabels(
        [f"{p}\n{technique_labels.get(p, '')}" for p in prompt_order],
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

def all_models_performance(scores, writers, prompts, technique_groups):

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

    technique_labels = {
        'p0':  'Baseline',
        'p1':  'Role-based',
        'p2':  'Role-based\n+ Formal',
        'p3':  'Chain of\nThought',
        'p4':  'Generate\nKnowledge',
        'p5':  'CoT +\nGen Know',
        'p6':  'Role +\nGen Know',
        'p7':  'Role + CoT\n+ Gen Know',
        'p8':  'Iter +\nRole',
        'p9':  'Iter +\nGen Know',
        'p10': 'Iter + CoT\n+ Gen Know',
        'p11': 'Iter +\nOriginal'
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

    for ax, essay_type, title in zip(axes, ['generate', 'tune'], ['Generate', 'Tune']):

        ax.set_facecolor('#f7f9fc')

        df = (
            scores[scores['EssayType'] == essay_type]
            .groupby(['Writer', 'Prompt'])['Total']
            .mean().round(2)
            .unstack()
            .reindex(writers)[prompt_order]
        )

        for i, writer in enumerate(writers):
            color  = colors.get(writer, 'gray')
            offset = (i - n_writers / 2 + 0.5) * (bar_width + group_gap / n_writers)
            x_pos  = [j + offset for j in range(n_prompts)]
            vals   = df.loc[writer].values

            # dots only — no lines
            ax.scatter(
                x_pos, vals,
                color=color,
                s=80,
                zorder=5,
                label=writer.capitalize()
            )

            # value labels above each dot
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

    # group labels on top — first subplot only
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

    # x axis labels — last subplot only
    axes[-1].set_xticks(range(n_prompts))

    axes[-1].set_xticklabels(
        [f"{p}\n{technique_labels.get(p, '')}" for p in prompt_order],
        fontfamily='Times New Roman',
        fontsize=8,
        ha='center'
    )

    legend_handles = [
        Line2D([0], [0], marker='o', color='w',
               markerfacecolor=colors[w], markersize=9,
               label=w.capitalize())
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
        'Generate vs Tune — Score by Prompt Technique',
        fontfamily='Times New Roman',
        fontsize=14,
        fontweight='bold',
        y=1.01
    )


    plt.show()
