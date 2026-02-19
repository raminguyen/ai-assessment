import glob
import re
import pandas as pd
import numpy as np

src_dir = '/Users/ramihuunguyen/Documents/PhD/ai-assessment/src'
files = sorted(glob.glob(f'{src_dir}/scores_p*.csv'),
               key=lambda f: int(re.search(r'scores_p(\d+)', f).group(1)))

dfs = []
for f in files:
    p_num = int(re.search(r'scores_p(\d+)', f).group(1))
    df = pd.read_csv(f)
    df = df[~df['Assignment'].astype(str).str.startswith('Average')]
    df.insert(0, 'Prompt', f'p{p_num}')
    dfs.append(df)

all_df = pd.concat(dfs, ignore_index=True)

# Flag zero scores
dim_cols = ['Issues', 'Evidence', 'Context', 'Position', 'Conclusions', 'Total']
all_df['HasZero'] = np.any(all_df[dim_cols].values == 0, axis=1)

all_df.to_excel(f'{src_dir}/scores_all.xlsx', index=False)
print(f"Saved scores_all.xlsx ({len(all_df)} rows, {all_df['HasZero'].sum()} with zeros)")
