import sys
import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

sys.path.append(os.path.join(os.getcwd(), 'src'))
from visualization import score_chart

FOLDER_PATH = 'data/critical_thinking'
OUTPUT_DIR = 'src/visualization/rubric_plots'

def get_paired_scores(merged_data, filter_key, filter_index):
    """Extract paired E1/E2 scores filtered by a specific key (writer or assignment)."""
    e1_scores = []
    e2_scores = []
    for key, values in merged_data.items():
        if key[filter_index] == filter_key:
            g1 = values.get('p1_gen')
            g2 = values.get('p2_gen')
            if g1 is not None and g2 is not None:
                e1_scores.append(g1)
                e2_scores.append(g2)
    return e1_scores, e2_scores


def run_paired_ttest(e1_scores, e2_scores, label):
    """Run paired t-test and print results."""
    if len(e1_scores) >= 2:
        t_stat, p_value = stats.ttest_rel(e1_scores, e2_scores)
        mean_e1 = np.mean(e1_scores)
        mean_e2 = np.mean(e2_scores)
        sig = "Yes" if p_value < 0.05 else "No"
        print(label + ": N=" + str(len(e1_scores)) +
              ", E1=" + str(round(mean_e1, 2)) +
              ", E2=" + str(round(mean_e2, 2)) +
              ", t=" + str(round(t_stat, 3)) +
              ", p=" + str(round(p_value, 4)) +
              ", Sig=" + sig)
        return {'t': t_stat, 'p': p_value, 'sig': sig}
    else:
        print(label + ": Not enough paired samples")
        return None


def print_section_header(title):
    """Print a formatted section header."""
    print("\n" + "=" * 50)
    print(title)
    print("=" * 50)


def get_sum(gen, tune):
    """Calculate sum of gen and tune scores, treating None as 0."""
    total = 0
    if gen is not None:
        total += gen
    if tune is not None:
        total += tune
    return total


def render_mpl_table(data, col_width=3.0, row_height=0.5, font_size=11,
                     header_color='#34495e', row_colors=['#ffffff', '#fcfcfc'],
                     edge_color='#ecf0f1', bbox=[0, 0, 1, 1], ax=None, **kwargs):
    """Render a pandas DataFrame as a matplotlib table."""
    if ax is None:
        size = (np.array(data.shape[::-1]) + np.array([0, 1])) * np.array([col_width, row_height])
        _, ax = plt.subplots(figsize=size)
        ax.axis('off')

    data = data.fillna('')
    mpl_table = ax.table(cellText=data.values, bbox=bbox, colLabels=data.columns,
                         cellLoc='center', **kwargs)
    mpl_table.auto_set_font_size(False)
    mpl_table.set_fontsize(font_size)

    for k, cell in mpl_table._cells.items():
        cell.set_edgecolor(edge_color)
        cell.set_linewidth(1)

        if k[0] == 0:  # Header row
            cell.set_text_props(weight='bold', color='w')
            cell.set_facecolor(header_color)
            cell.set_height(0.1)
        else:
            cell.set_facecolor(row_colors[k[0] % len(row_colors)])
            col_label = data.columns[k[1]]

            if col_label in ['Writer', 'Reasons']:
                cell.set_text_props(ha='left')
                text = cell.get_text().get_text()
                cell.get_text().set_text('  ' + text)

            if col_label == 'E2 Better':
                val = cell.get_text().get_text().strip()
                if val == 'YES':
                    cell.set_text_props(weight='bold', color='#ffffff')
                    cell.set_facecolor('#27ae60')
                elif val == 'SIMILAR':
                    cell.set_text_props(weight='normal', color='#7f8c8d')
                    cell.set_facecolor('#f4f6f7')
                else:
                    cell.set_text_props(weight='normal', color='#bdc3c7')
                    cell.set_facecolor('#ffffff')

            if 'Gen' in col_label or 'Tune' in col_label:
                cell.set_text_props(color='#2c3e50')

    return ax


def load_and_merge_data():
    """Load scores from both experiments and merge into a single dictionary."""
    data_p1 = score_chart.load_scores(FOLDER_PATH, 1)
    data_p2 = score_chart.load_scores(FOLDER_PATH, 2)

    merged_data = {}
    for d in data_p1:
        key = (d['assignment'], d['writer'], d['grader'])
        if key not in merged_data:
            merged_data[key] = {}
        if d['essay_type'] == 'generate':
            merged_data[key]['p1_gen'] = d['total']
        elif d['essay_type'] == 'tune':
            merged_data[key]['p1_tune'] = d['total']

    for d in data_p2:
        key = (d['assignment'], d['writer'], d['grader'])
        if key not in merged_data:
            merged_data[key] = {}
        if d['essay_type'] == 'generate':
            merged_data[key]['p2_gen'] = d['total']
        elif d['essay_type'] == 'tune':
            merged_data[key]['p2_tune'] = d['total']

    return merged_data


def build_comparison_dataframe(merged_data):
    """Build a comparison DataFrame from merged data."""
    results = []
    for key, values in merged_data.items():
        assignment, writer, grader = key
        g1 = values.get('p1_gen')
        t1 = values.get('p1_tune')
        g2 = values.get('p2_gen')
        t2 = values.get('p2_tune')

        total1 = get_sum(g1, t1)
        total2 = get_sum(g2, t2)

        if total2 > total1:
            status = 'YES'
            reasons = []
            if g2 is not None and g1 is not None and g2 > g1:
                reasons.append("Gen: " + str(int(g1)) + "->" + str(int(g2)))
            if t2 is not None and t1 is not None and t2 > t1:
                reasons.append("Tune: " + str(int(t1)) + "->" + str(int(t2)))
        elif total1 == total2 and g2 is not None:
            status = 'SIMILAR'
            reasons = []
        else:
            status = 'NO'
            reasons = []

        results.append({
            'Assignment': assignment.upper(),
            'Writer': writer.capitalize(),
            'Grader': grader.capitalize(),
            'E1 Gen': g1 if g1 is not None else '-',
            'E1 Tune': t1 if t1 is not None else '-',
            'E2 Gen': g2 if g2 is not None else '-',
            'E2 Tune': t2 if t2 is not None else '-',
            'E2 Better': status,
            'Reasons': "\n".join(reasons) if reasons else "-"
        })

    return pd.DataFrame(results).sort_values(by=['Assignment', 'Writer', 'Grader'])



def run_ttest_analysis(merged_data):
    """Run all t-test analyses and print results."""

    # Overall independent t-test
    print_section_header("Independent samples t-test: E1 Gen vs E2 Gen")
    e1_all = [v.get('p1_gen') for v in merged_data.values() if v.get('p1_gen') is not None]
    e2_all = [v.get('p2_gen') for v in merged_data.values() if v.get('p2_gen') is not None]

    if len(e1_all) >= 2 and len(e2_all) >= 2:
        t_stat, p_value = stats.ttest_ind(e1_all, e2_all)
        print("E1 Gen: N = " + str(len(e1_all)) + ", Mean = " + str(round(np.mean(e1_all), 2)) +
              ", SD = " + str(round(np.std(e1_all, ddof=1), 2)))
        print("E2 Gen: N = " + str(len(e2_all)) + ", Mean = " + str(round(np.mean(e2_all), 2)) +
              ", SD = " + str(round(np.std(e2_all, ddof=1), 2)))
        print("t-statistic: " + str(round(t_stat, 4)))
        print("p-value: " + str(round(p_value, 4)))
        print("Significant (p < 0.05): " + ("Yes" if p_value < 0.05 else "No"))
    print("=" * 50)

    # Paired t-test by Writer
    print_section_header("Paired t-test by Writer (E1 Gen vs E2 Gen)")
    writers = sorted(set(key[1] for key in merged_data.keys()))
    for writer in writers:
        e1_scores, e2_scores = get_paired_scores(merged_data, writer, 1)
        run_paired_ttest(e1_scores, e2_scores, writer.capitalize())

    # Paired t-test by Assignment
    print_section_header("Paired t-test by Assignment (E1 Gen vs E2 Gen)")
    assignments = sorted(set(key[0] for key in merged_data.keys()))
    for assignment in assignments:
        e1_scores, e2_scores = get_paired_scores(merged_data, assignment, 0)
        run_paired_ttest(e1_scores, e2_scores, assignment.upper())

    print("=" * 50 + "\n")


def create_visualization(df):
    """Create and save the comparison table visualization."""
    assignments = sorted(df['Assignment'].unique())
    _, axes = plt.subplots(len(assignments), 1, figsize=(14, 22))
    if len(assignments) == 1:
        axes = [axes]

    for assignment, ax in zip(assignments, axes):
        sub_df = df[df['Assignment'] == assignment].drop(columns=['Assignment']).copy()
        sub_df['Writer'] = sub_df['Writer'].mask(sub_df['Writer'].duplicated(), '')

        ax.axis('off')
        ax.set_axis_off()
        ax.set_title('E1 vs E2 Performance: Assignment ' + assignment,
                     fontweight='bold', fontsize=18, pad=20, color='#2c3e50')
        render_mpl_table(sub_df, ax=ax, col_width=1.6, row_height=0.6, font_size=10)

    plt.tight_layout(pad=4.0)
    png_path = os.path.join(OUTPUT_DIR, "exp2_comparison_table.png")
    plt.savefig(png_path, bbox_inches='tight', dpi=300, facecolor='white')
    print("[INFO] Finalized table image saved to " + png_path)


def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    try:
        merged_data = load_and_merge_data()
    except Exception as e:
        print("Error loading scores: " + str(e))
        return

    df = build_comparison_dataframe(merged_data)
    csv_path = os.path.join(OUTPUT_DIR, "exp2_comparison_table.csv")
    df.to_csv(csv_path, index=False)

    run_ttest_analysis(merged_data)
    create_visualization(df)


if __name__ == "__main__":
    main()
