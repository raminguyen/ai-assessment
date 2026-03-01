import numpy as np
import pandas as pd







#
#visualize_scores.ipynb
#


def compute_avg_total_by_essaytype(scores, prompts):

    """
     Average Total score per Prompt and EssayType.

    """

    df = (
        scores
        .groupby(['EssayType', 'Prompt'])['Total']
        .mean()
        .round(2)
        .reset_index()
    )

    records = []

    for prompt in prompts:
        for etype in ['generate', 'tune']:
            subset = df[
                (df['Prompt']    == prompt) &
                (df['EssayType'] == etype)
            ]
            records.append({
                'Prompt':    prompt,
                'EssayType': etype,
                'AvgTotal':  subset['Total'].values[0] if not subset.empty else np.nan
            })

    return pd.DataFrame(records)


def compute_bias_by_prompt_assignment(scores, writers, dimensions):
    """Mean |Bias| per Prompt, Assignment and EssayType."""

    consensus = (
        scores
        .groupby(['Prompt', 'EssayType', 'Writer', 'Assignment'])[dimensions]
        .mean()
        .reset_index()
        .rename(columns={d: d + '_consensus' for d in dimensions})
    )

    scores_bias = scores.merge(
        consensus,
        on=['Prompt', 'EssayType', 'Writer', 'Assignment']
    )

    for d in dimensions:
        scores_bias[d + '_abs_bias'] = (
            scores_bias[d] - scores_bias[d + '_consensus']
        ).abs()

    abs_cols    = [d + '_abs_bias' for d in dimensions]
    prompts     = sorted(scores['Prompt'].unique())
    assignments = sorted(scores['Assignment'].unique())
    records     = []

    for prompt in prompts:
        for assignment in assignments:
            for etype in ['generate', 'tune']:

                subset = scores_bias[
                    (scores_bias['Prompt']     == prompt)     &
                    (scores_bias['Assignment'] == assignment) &
                    (scores_bias['EssayType']  == etype)
                ]

                vals = subset[abs_cols].values.flatten()
                vals = vals[~np.isnan(vals)]

                records.append({
                    'Prompt':     prompt,
                    'Assignment': assignment,
                    'EssayType':  etype,
                    'N':          len(vals),
                    'MeanBias':   round(np.mean(vals), 4)  if len(vals) > 0 else np.nan,
                    'StdBias':    round(np.std(vals, ddof=1), 4) if len(vals) > 1 else 0,
                    'MaxBias':    round(np.max(vals), 4)   if len(vals) > 0 else np.nan,
                    'MinBias':    round(np.min(vals), 4)   if len(vals) > 0 else np.nan,
                })

    return pd.DataFrame(records)


def compute_avg_total_by_writer_prompt(scores, writers, prompts, technique_groups):
    """Mean Total score per Writer and Prompt, split by EssayType."""

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

    records = []

    for etype in ['generate', 'tune']:
        for writer in writers:
            for prompt in prompt_order:

                subset = scores[
                    (scores['EssayType'] == etype)  &
                    (scores['Writer']    == writer)  &
                    (scores['Prompt']    == prompt)
                ]

                mean_total = round(subset['Total'].mean(), 2) if len(subset) > 0 else np.nan

                records.append({
                    'EssayType': etype,
                    'Writer':    writer,
                    'Prompt':    prompt,
                    'AvgTotal':  mean_total
                })

    return pd.DataFrame(records)


def compute_trend_by_writer_prompt(scores, writers, prompts, technique_groups):
    """Mean Total score per Writer, Prompt and EssayType for trend plotting."""

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

    records = []

    for etype in ['generate', 'tune']:
        for writer in writers:
            for prompt in prompt_order:

                subset = scores[
                    (scores['EssayType'] == etype)  &
                    (scores['Writer']    == writer)  &
                    (scores['Prompt']    == prompt)
                ]

                records.append({
                    'EssayType': etype,
                    'Writer':    writer,
                    'Prompt':    prompt,
                    'AvgTotal':  round(subset['Total'].mean(), 2) if len(subset) > 0 else np.nan
                })

    return pd.DataFrame(records), prompt_order


#
#visualize_scores_p0.ipynb
#



#visualize_scores_po.ipynb
def compute_cross_grading_scores(scores, writers, dimensions, grader=None):

    """
    grader=None  → all graders
    grader='claude' → single grader
    """

    results = []

    graders = writers if grader is None else [grader]

    for etype in ['generate', 'tune']:
        for writer in writers:

            subset = scores[
                (scores['EssayType'] == etype) &
                (scores['Writer']    == writer)
            ]

            for g in graders:

                g_subset = subset[subset['Grader'] == g]

                for dimension in dimensions:

                    y_vals = g_subset[dimension].dropna().values

                    mean_val = np.mean(y_vals)        if len(y_vals) > 0 else np.nan

                    std_val  = np.std(y_vals, ddof=1) if len(y_vals) > 1 else 0

                    results.append({
                        
                        'EssayType':  etype,
                        'Writer':     writer,
                        'Grader':     g,
                        'Dimension':  dimension,
                        'N':          len(y_vals),
                        'Mean':       round(mean_val, 4),
                        'Std':        round(std_val,  4),
                        'Bar_bottom': round(mean_val - std_val, 4),
                        'Bar_top':    round(mean_val + std_val, 4),
                        'Values':     list(y_vals)
                    })

    return pd.DataFrame(results) 

def compute_grading_bias_by_assignment(scores, writers, dimensions):

    # consensus = mean of all graders per Prompt + EssayType + Writer + Assignment
    consensus = (
        scores
        .groupby(['Prompt', 'EssayType', 'Writer', 'Assignment'])[dimensions]
        .mean()
        .reset_index()
        .rename(columns={d: d + '_consensus' for d in dimensions})
    )

    scores_bias = scores.merge(
        consensus,
        on=['Prompt', 'EssayType', 'Writer', 'Assignment']
    )

    for d in dimensions:
        scores_bias[d + '_bias']     = scores_bias[d] - scores_bias[d + '_consensus']
        scores_bias[d + '_abs_bias'] = scores_bias[d + '_bias'].abs()

    results = []

    for prompt in sorted(scores['Prompt'].unique()):
        for etype in ['generate', 'tune']:
            for writer in writers:
                for assignment in sorted(scores['Assignment'].unique()):

                    subset = scores_bias[
                        (scores_bias['Prompt']     == prompt)     &
                        (scores_bias['EssayType']  == etype)      &
                        (scores_bias['Writer']      == writer)     &
                        (scores_bias['Assignment']  == assignment)
                    ]

                    for dimension in dimensions:

                        # e.g. generate + chatgpt + A3 + Context:
                        # claude  → 2.0, gemini → 4.0, grok → 3.0
                        # consensus = (2+4+3)/3 = 3.0
                        # abs_bias  = [1.0, 1.0, 0.0]
                        # Mean_AbsBias = 0.667

                        vals = subset[dimension + '_abs_bias'].dropna().values

                        consensus_val = subset[dimension + '_consensus'].values[0] if len(subset) > 0 else np.nan

                        results.append({
                            'Prompt':       prompt,
                            'EssayType':    etype,
                            'Writer':       writer,
                            'Assignment':   assignment,
                            'Dimension':    dimension,
                            'N':            len(vals),
                            'AbsBiasValues': [round(v, 2) for v in vals],
                            'Consensus':    round(consensus_val, 2),
                            'Mean_AbsBias': round(np.mean(vals), 4) if len(vals) > 0 else np.nan,
                        })

    return pd.DataFrame(results)