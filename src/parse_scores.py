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

            flexible_dim + r'[^\n|]{0,120}(?::|—|–)\s*\**(\d+(?:\.\d+)?)', #Evidence: 3  or  Evidence — 3  or  Evidence: **3**

            r'\*\*' + flexible_dim + r'.*?:\*\*\s*(\d+(?:\.\d+)?)',  #**Evidence**: 3 

            r'\|[^\|]*'+ flexible_dim + r'[^\|]*\|\s*(?:\*\*)?(\d+(?:\.\d+)?)[^\|]*\|', #| Evidence | 3 | 

            r'- \*\*' + flexible_dim + r'.*?\*\*\s*:?\s*(\d+(?:\.\d+)?)', # **Evidence**: 3 

            flexible_dim + r'[\s\S]{0,150}?\*\*Score:\s*(\d+(?:\.\d+)?)', # Evidence ... **Score: 3 

            flexible_dim + r'[\s\S]{0,150}?\*\*Score:\s*\w+(?:\s+\w+)*?\s*\((\d+(?:\.\d+)?)\)', # Evidence ... **Score: Milestone (3)

            flexible_dim + r'[^\n|]*(?::|—|–)[^\n|]*\((\d+(?:\.\d+)?)\)', #Evidence: something (3)
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

    header = ['Assignment', 'EssayType', 'Writer', 'Grader'] + short_dims + ['Total']

    rows = []

    for filepath in files:

        filename = os.path.basename(filepath)

        m = re.match(r'a(\d+)_(gen|tune)_([\w-]+)_score_([\w-]+)_p\d+\.json', filename)

        if not m:
            continue

        a_num = int(m.group(1)) #a1, a2, a3: assignment number

        writer_name = m.group(3) #writer model

        grader_name = m.group(4) #grader model

        with open(filepath, 'r', encoding='utf-8') as jf:
            data = json.load(jf)

        essay_type = data.get('essay_type', 'generate') #generate (default) or tune

        scores = parse_dimension_scores(data.get('result', '')) #output: dictionary (5 rows)

        total = sum(scores.get(dim, 0) for dim in dimensions) #sum all scores

        rows.append(['A' + str(a_num), essay_type, writer_name, grader_name] +
                    
                    [scores.get(dim, 0) for dim in dimensions] + [total]) # one row: metadata + 5 scores + total

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

    for p_num in range(0, 13):

        df = parse_prompt(data_dir, p_num, dimensions, short_dims) #parse all files for this prompt number

        if df.empty:
            continue

        df.insert(0, 'Prompt', 'p' + str(p_num))  #add Prompt column as first column → p0, p1, p2

        dfs.append(df)

    all_df = pd.concat(dfs, ignore_index=True)

    for col in dim_cols:
        all_df[col] = pd.to_numeric(all_df[col], errors='coerce').fillna(0) # force all score columns to numbers, replace any non-numeric with 0

    all_df['HasZero'] = np.any(all_df[dim_cols].values == 0, axis=1)

    for col in short_dims:
        all_df[col + '_zero'] = all_df[col] == 0 ## True if any score in that each dimension is 0

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


if __name__ == '__main__':
    main()
