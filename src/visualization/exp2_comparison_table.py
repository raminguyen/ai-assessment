import sys
import os
import pandas as pd
import json
import matplotlib
matplotlib.use('Agg') # Set backend to non-interactive
import matplotlib.pyplot as plt
import numpy as np

# Add src to sys.path to import score_chart
sys.path.append(os.path.join(os.getcwd(), 'src'))

from visualization import score_chart

def render_mpl_table(data, col_width=3.0, row_height=0.5, font_size=11,
                     header_color='#34495e', row_colors=['#ffffff', '#fcfcfc'], edge_color='#ecf0f1',
                     bbox=[0, 0, 1, 1], ax=None, **kwargs):
    if ax is None:
        size = (np.array(data.shape[::-1]) + np.array([0, 1])) * np.array([col_width, row_height])
        fig, ax = plt.subplots(figsize=size)
        ax.axis('off')

    # Remove empty strings/nan for cleaner look
    data = data.fillna('')
    
    mpl_table = ax.table(cellText=data.values, bbox=bbox, colLabels=data.columns, cellLoc='center', **kwargs)

    mpl_table.auto_set_font_size(False)
    mpl_table.set_fontsize(font_size)

    # Style cells
    for k, cell in mpl_table._cells.items():
        cell.set_edgecolor(edge_color)
        cell.set_linewidth(1)
        
        # Header
        if k[0] == 0:
            cell.set_text_props(weight='bold', color='w')
            cell.set_facecolor(header_color)
            cell.set_height(0.1) # Thicker header
        else:
            # Row styling
            cell.set_facecolor(row_colors[k[0]%len(row_colors)])
            
            # Text alignment
            col_label = data.columns[k[1]]
            if col_label in ['Writer', 'Reasons']:
                cell.set_text_props(ha='left')
                text = cell.get_text().get_text()
                cell.get_text().set_text('  ' + text)

            # Conditional Formatting for "E2 Better"
            if col_label == 'E2 Better':
                val = cell.get_text().get_text().strip()
                if val == 'YES':
                    cell.set_text_props(weight='bold', color='#ffffff')
                    cell.set_facecolor('#27ae60') # Solid Vibrant Green
                elif val == 'SIMILAR':
                    cell.set_text_props(weight='normal', color='#7f8c8d')
                    cell.set_facecolor('#f4f6f7') # Very Light Gray
                else:
                    cell.set_text_props(weight='normal', color='#bdc3c7')
                    cell.set_facecolor('#ffffff') # White / Faint text for NO

            # Highlight the scores columns slightly
            if 'Gen' in col_label or 'Tune' in col_label:
                cell.set_text_props(color='#2c3e50')

    return ax

def main():
    folder_path = 'data/critical_thinking'
    output_dir = 'src/visualization/rubric_plots'
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Load data
    try:
        data_p1 = score_chart.load_scores(folder_path, 1)
        data_p2 = score_chart.load_scores(folder_path, 2)
    except Exception as e:
        print(f"Error loading scores: {e}")
        return

    merged_data = {}
    for d in data_p1:
        key = (d['assignment'], d['writer'], d['grader'])
        if key not in merged_data: merged_data[key] = {}
        if d['essay_type'] == 'generate': merged_data[key]['p1_gen'] = d['total']
        elif d['essay_type'] == 'tune': merged_data[key]['p1_tune'] = d['total']
            
    for d in data_p2:
        key = (d['assignment'], d['writer'], d['grader'])
        if key not in merged_data: merged_data[key] = {}
        if d['essay_type'] == 'generate': merged_data[key]['p2_gen'] = d['total']
        elif d['essay_type'] == 'tune': merged_data[key]['p2_tune'] = d['total']
            
    results = []
    for key, values in merged_data.items():
        assignment, writer, grader = key
        g1, t1 = values.get('p1_gen'), values.get('p1_tune')
        g, t = values.get('p2_gen'), values.get('p2_tune')
        
        # Calculate totals for comparison
        # Use 0 as default if one is missing for sum, but keep track of existence
        def get_sum(gen, tune):
            s = 0
            if gen is not None: s += gen
            if tune is not None: s += tune
            return s

        total1 = get_sum(g1, t1)
        total2 = get_sum(g, t)
        
        status = 'NO'
        reasons = []
        
        if total2 > total1:
            status = 'YES'
            if g is not None and g1 is not None and g > g1:
                reasons.append(f"Gen: {int(g1)}→{int(g)}")
            if t is not None and t1 is not None and t > t1:
                reasons.append(f"Tune: {int(t1)}→{int(t)}")
        elif total1 == total2 and g is not None:
            status = 'SIMILAR'
        else:
            status = 'NO'

        results.append({
            'Assignment': assignment.upper(),
            'Writer': writer.capitalize(),
            'Grader': grader.capitalize(),
            'E1 Gen': g1 if g1 is not None else '-',
            'E1 Tune': t1 if t1 is not None else '-',
            'E2 Gen': g if g is not None else '-',
            'E2 Tune': t if t is not None else '-',
            'E2 Better': status,
            'Reasons': "\n".join(reasons) if reasons else "-"
        })

    df = pd.DataFrame(results).sort_values(by=['Assignment', 'Writer', 'Grader'])
    
    csv_path = os.path.join(output_dir, "exp2_comparison_table.csv")
    df.to_csv(csv_path, index=False)

    # Visualization
    assignments = sorted(df['Assignment'].unique())
    # Adjust figure size based on content
    fig, axes = plt.subplots(len(assignments), 1, figsize=(14, 22)) # Increased height
    if len(assignments) == 1: axes = [axes]

    for idx, (assignment, ax) in enumerate(zip(assignments, axes)):
        sub_df = df[df['Assignment'] == assignment].drop(columns=['Assignment'])
        
        # Clean up writer column repetition within each sub-table
        sub_df['Writer'] = sub_df['Writer'].mask(sub_df['Writer'].duplicated(), '')
        
        # Ensure Axis off
        ax.axis('off')
        ax.set_axis_off() # Double ensure
        
        ax.set_title(f'E1 vs E2 Performance: Assignment {assignment}', fontweight='bold', fontsize=18, pad=20, color='#2c3e50')
        # Increased row_height to 0.6 to fit wrapped text
        render_mpl_table(sub_df, ax=ax, col_width=1.6, row_height=0.6, font_size=10)

    plt.tight_layout(pad=4.0)
    
    png_path = os.path.join(output_dir, "exp2_comparison_table.png")
    plt.savefig(png_path, bbox_inches='tight', dpi=300, facecolor='white')
    print(f"[INFO] Finalized table image saved to {png_path}")

if __name__ == "__main__":
    main()
