import os
import json
import re
import matplotlib.pyplot as plt


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
        # Try multiple patterns
        escaped_dim = re.escape(dim)
        patterns = [
            escaped_dim + r'.*?(\d+(?:\.\d+)?)',
            r'\*\*' + escaped_dim + r':\*\*\s*(\d+(?:\.\d+)?)',
            r'\|.*?' + escaped_dim + r'.*?\|\s*(\d+(?:\.\d+)?)\s*\|',
            r'- \*\*' + escaped_dim + r'\s*:?\*\*\s*:?\s*(\d+(?:\.\d+)?)'
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                scores[dim] = float(match.group(1))
                break

        if dim not in scores:
            scores[dim] = 0

    return scores


def get_total_score(text):
    """Get total score (sum of 5 dimensions)."""
    scores = parse_dimension_scores(text)
    total = sum(scores.values())
    return total


def load_scores(folder_path, prompt_num=1):
    """Load gen and tune scores from folder."""
    data = []
    p_suffix = '_p' + str(prompt_num)

    for filename in os.listdir(folder_path):
        if not filename.endswith('.json'):
            continue
        if p_suffix not in filename:
            continue
        if '_score_' not in filename:
            continue

        filepath = os.path.join(folder_path, filename)

        with open(filepath, 'r') as f:
            file_data = json.load(f)

        essay_type = file_data.get('essay_type', '')
        result = file_data.get('result', '')

        total = get_total_score(result)

        # Parse filename: a1_gen_chatgpt_score_claude_p1.json
        parts = filename.replace('.json', '').split('_')
        assignment = parts[0]  # a1
        writer = parts[2]      # chatgpt
        grader = parts[4]      # claude

        data.append({
            'assignment': assignment,
            'writer': writer,
            'grader': grader,
            'essay_type': essay_type,
            'total': total,
            'filename': filename
        })

    return data


def _plot_assignment_on_axis(ax, folder_path, assignment, show_orientation_labels=False):
    """Helper to plot a single assignment on a given axis."""
    import numpy as np
    from matplotlib.patches import Rectangle

    writers = ['chatgpt', 'gemini', 'claude', 'grok']
    writer_colors = {
        'chatgpt': '#3498DB',
        'gemini': '#E67E22',
        'claude': '#2ECC71',
        'grok': '#9B59B6'
    }
    grader_initials = {'chatgpt': 'C', 'gemini': 'G', 'claude': 'CL', 'grok': 'Gr'}

    data_p1 = load_scores(folder_path, 1)
    data_p2 = load_scores(folder_path, 2)

    positions = []
    all_labels = [] # Initialize labels list
    pos = 0

    # Add background shading for groups
    for writer_idx, writer in enumerate(writers):
        graders = [g for g in writers if g != writer]
        
        # Start of this writer's group
        group_x_start = pos - 0.5

        for grader in graders:
            # --- PROMPT 1 ---
            gen_p1 = [d['total'] for d in data_p1
                   if d['assignment'] == assignment
                   and d['writer'] == writer
                   and d['grader'] == grader
                   and d['essay_type'] == 'generate']

            tune_p1 = [d['total'] for d in data_p1
                    if d['assignment'] == assignment
                    and d['writer'] == writer
                    and d['grader'] == grader
                    and d['essay_type'] == 'tune']

            # --- PROMPT 2 ---
            gen_p2 = [d['total'] for d in data_p2
                   if d['assignment'] == assignment
                   and d['writer'] == writer
                   and d['grader'] == grader
                   and d['essay_type'] == 'generate']

            tune_p2 = [d['total'] for d in data_p2
                    if d['assignment'] == assignment
                    and d['writer'] == writer
                    and d['grader'] == grader
                    and d['essay_type'] == 'tune']
            
            # Check if we have data for at least one
            has_p1 = gen_p1 and tune_p1
            has_p2 = gen_p2 and tune_p2
            
            g1 = None # Store P1 gen score
            t1 = None # Store P1 tune score

            if has_p1 or has_p2:
                positions.append(pos)
                
                # Grader Annotation (Collect for X-axis)
                g_init = grader_initials.get(grader, grader[0].upper())
                all_labels.append(g_init)

                # Draw a very faint vertical line to separate P1 and P2 within this grader slot
                ax.axvline(x=pos, color='gray', linestyle=':', linewidth=0.8, alpha=0.2, zorder=0)
                
                color = writer_colors[writer]
                
                # Plot P1 (Left offset)
                if has_p1:
                    g, t = gen_p1[0], tune_p1[0]
                    g1 = g
                    t1 = t
                    x_p1 = pos - 0.15
                    
                    improved = t >= g
                    line_color = '#27AE60' if improved else '#E74C3C'
                    marker = '^' if improved else 'v'
                    
                    # Line
                    ax.plot([x_p1, x_p1], [g, t], color=line_color, linewidth=2, alpha=0.8, zorder=2)
                    # Gen
                    ax.scatter(x_p1, g, s=100, c=color, marker='o', edgecolors='white', linewidths=1.5, zorder=4)
                    # Tune
                    ax.scatter(x_p1, t, s=100, c=color, marker=marker, edgecolors='white', linewidths=1.5, zorder=4)
                    
                    # Orientation Label (Only for the first slot in the chart)
                    if show_orientation_labels and graders.index(grader) == 0:
                        ax.annotate('EXP1', xy=(x_p1, 0.5), ha='center', va='bottom', fontsize=8, color='gray', fontweight='bold')


                # Plot P2 (Right offset)
                if has_p2:
                    g, t = gen_p2[0], tune_p2[0]
                    x_p2 = pos + 0.15
                    
                    improved = t >= g
                    line_color = '#27AE60' if improved else '#E74C3C'
                    marker = '^' if improved else 'v'
                    
                    # Line
                    ax.plot([x_p2, x_p2], [g, t], color=line_color, linewidth=2, alpha=0.8, zorder=2)
                    # Gen
                    ax.scatter(x_p2, g, s=100, c=color, marker='o', edgecolors='white', linewidths=1.5, zorder=4, alpha=0.6) 
                    # Tune
                    ax.scatter(x_p2, t, s=100, c=color, marker=marker, edgecolors='white', linewidths=1.5, zorder=4, alpha=0.9)
                    
                    # Highlight if P2 > P1 significantly or a "comeback"
                    p2_wins = False
                    if g1 is not None and g > g1: p2_wins = True # P2 Gen is better
                    if t1 is not None and t > (t1 + 1): p2_wins = True # P2 Tune is significantly better
                    # Comeback case: P2 starts lower than P1 but finishes higher
                    if g1 is not None and t1 is not None and g < g1 and t > t1: p2_wins = True
                    
                    if p2_wins:
                        # Draw a red highlight box around the P2 segment
                        ymin, ymax = min(g, t) - 0.6, max(g, t) + 0.6
                        rect_p2 = Rectangle((x_p2 - 0.1, ymin), 0.2, ymax - ymin, 
                                           linewidth=1.5, edgecolor='#C0392B', facecolor='none', 
                                           linestyle='-', zorder=5, alpha=0.8)
                        ax.add_patch(rect_p2)
                        
                        ax.text(x_p2, ymax + 0.8, "EXP2 Better", ha='center', va='bottom', fontsize=7, fontweight='bold', color='#C0392B')

                    # Orientation Label (Only for the first slot in the chart)
                    if show_orientation_labels and graders.index(grader) == 0:
                        ax.annotate('EXP2', xy=(x_p2, 0.5), ha='center', va='bottom', fontsize=8, color='gray', fontweight='bold')

                pos += 1

        # End of this writer's group
        group_x_end = pos - 0.5
        
        # Add subtle background for all groups (visual separation)
        rect = Rectangle((group_x_start, 0), group_x_end - group_x_start, 30, 
                        facecolor='#F2F3F4', alpha=0.5, zorder=0)
        ax.add_patch(rect)
        
        # Writer Label (Centered above the group) - ONLY ON TOP SUBPLOT
        if assignment == 'a1':
            mid_point = (group_x_start + group_x_end) / 2
            ax.text(mid_point, 26, writer.upper(), ha='center', va='bottom', 
                    fontsize=11, fontweight='bold', color=writer_colors[writer])

        pos += 0.5  # Gap between writer groups

    # X-axis setup
    ax.set_xticks(positions)
    ax.set_xticklabels(all_labels, fontsize=10, fontweight='bold', color='#555555')
    ax.set_xlim(-0.5, pos)

    # Styling
    ax.set_ylabel('Total Score (0-20)', fontsize=12)
    ax.set_ylim(0, 28) # Increased limit for labels
    ax.set_title(f'Assignment {assignment[1]}', fontsize=14, fontweight='bold', pad=25)
    ax.grid(True, alpha=0.2, axis='y', linestyle='--')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)


def plot_all_assignments(folder_path):
    """Plot A1, A2, and A3 stacked vertically in a single figure."""
    from matplotlib.lines import Line2D
    
    assignments = ['a1', 'a2', 'a3']
    fig, axes = plt.subplots(3, 1, figsize=(20, 18))
    
    for idx, assignment in enumerate(assignments):
        ax = axes[idx]
        # Only show orientation labels (P1/P2) for the first chart (Assignment 1)
        _plot_assignment_on_axis(ax, folder_path, assignment, show_orientation_labels=(idx == 0))
        
        if idx == 2:
             ax.set_xlabel('Grader Initials (C=ChatGPT, G=Gemini, CL=Claude, Gr=Grok)', fontsize=12)
        
    # Shared Legend
    legend_elements = [
        Line2D([0], [0], color='w', markerfacecolor='none', label='WRITERS'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#3498DB', markersize=10, label='ChatGPT'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#E67E22', markersize=10, label='Gemini'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#2ECC71', markersize=10, label='Claude'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#9B59B6', markersize=10, label='Grok'),
        Line2D([0], [0], color='gray', linewidth=0, label=' '),
        Line2D([0], [0], color='w', markerfacecolor='none', label='MARKERS'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='gray', markersize=10, label='Generated'),
        Line2D([0], [0], marker='^', color='w', markerfacecolor='gray', markersize=10, label='Tuned (Improved)'),
        Line2D([0], [0], marker='v', color='w', markerfacecolor='gray', markersize=10, label='Tuned (Declined)'),
        Line2D([0], [0], color='gray', linewidth=0, label=' '),
        Line2D([0], [0], color='w', markerfacecolor='none', label='PROMPTS'),
        Line2D([0], [0], color='gray', linestyle='-', linewidth=2, label='Left Line: EXP1'),
        Line2D([0], [0], color='gray', linestyle='-', linewidth=2, label='Right Line: EXP2'),
    ]
    
    axes[0].legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1.01, 1), borderaxespad=0, fontsize=10)

    # Center main title relative to the plot area (not the figure)
    left, right = 0.1, 0.85
    title_x = (left + right) / 2
    fig.suptitle('Comparison of EXP1 and EXP2\n(Total Score / 20)', fontsize=20, fontweight='bold', x=title_x, y=0.97)
    
    plt.tight_layout()
    plt.subplots_adjust(left=left, right=right, top=0.90, bottom=0.08, hspace=0.3)
    return fig, axes


def plot_average_scores(folder_path):
    """Plot AVERAGE Total Scores (averaged across graders) for each Writer."""
    import numpy as np
    from matplotlib.patches import Rectangle
    from matplotlib.lines import Line2D

    assignments = ['a1', 'a2', 'a3']
    writers = ['chatgpt', 'gemini', 'claude', 'grok']
    writer_colors = {
        'chatgpt': '#3498DB',
        'gemini': '#E67E22',
        'claude': '#2ECC71',
        'grok': '#9B59B6'
    }

    data_p1 = load_scores(folder_path, 1)
    data_p2 = load_scores(folder_path, 2)

    fig, axes = plt.subplots(3, 1, figsize=(14, 18), sharex=True, sharey=True)
    
    for idx, assignment in enumerate(assignments):
        ax = axes[idx]
        pos = 0
        x_ticks = []
        x_labels = []

        for writer in writers:
            # Find all evaluations for this writer (from OTHER graders)
            graders = [g for g in writers if g != writer]
            
            # --- PROMPT 1 ---
            # Collect scores from all 3 graders
            p1_gen_scores = []
            p1_tune_scores = []
            
            for grader in graders:
                g_score = [d['total'] for d in data_p1 if d['assignment'] == assignment and d['writer'] == writer and d['grader'] == grader and d['essay_type'] == 'generate']
                t_score = [d['total'] for d in data_p1 if d['assignment'] == assignment and d['writer'] == writer and d['grader'] == grader and d['essay_type'] == 'tune']
                if g_score: p1_gen_scores.append(g_score[0])
                if t_score: p1_tune_scores.append(t_score[0])
            
            # Calculate Averages
            p1_g_avg = np.mean(p1_gen_scores) if p1_gen_scores else None
            p1_t_avg = np.mean(p1_tune_scores) if p1_tune_scores else None


            # --- PROMPT 2 ---
            p2_gen_scores = []
            p2_tune_scores = []
            
            for grader in graders:
                g_score = [d['total'] for d in data_p2 if d['assignment'] == assignment and d['writer'] == writer and d['grader'] == grader and d['essay_type'] == 'generate']
                t_score = [d['total'] for d in data_p2 if d['assignment'] == assignment and d['writer'] == writer and d['grader'] == grader and d['essay_type'] == 'tune']
                if g_score: p2_gen_scores.append(g_score[0])
                if t_score: p2_tune_scores.append(t_score[0])
            
            p2_g_avg = np.mean(p2_gen_scores) if p2_gen_scores else None
            p2_t_avg = np.mean(p2_tune_scores) if p2_tune_scores else None
            
            
            # PLOTTING
            if p1_g_avg is not None or p2_g_avg is not None:
                x_ticks.append(pos)
                x_labels.append(writer.upper())
                color = writer_colors[writer]
                
                # --- P1 (Left) ---
                if p1_g_avg is not None and p1_t_avg is not None:
                    x_p1 = pos - 0.15
                    improved = p1_t_avg >= p1_g_avg
                    line_color = '#27AE60' if improved else '#E74C3C'
                    marker = '^' if improved else 'v'
                    
                    ax.plot([x_p1, x_p1], [p1_g_avg, p1_t_avg], color=line_color, linewidth=2, alpha=0.8, zorder=2)
                    ax.scatter(x_p1, p1_g_avg, s=120, c=color, marker='o', edgecolors='white', linewidths=1.5, zorder=4, label='Gen' if idx==0 and pos==0 else "")
                    ax.scatter(x_p1, p1_t_avg, s=120, c=color, marker=marker, edgecolors='white', linewidths=1.5, zorder=4, label='Tune' if idx==0 and pos==0 else "")
                    
                    if idx == 0 and pos == 0: # Legend/Annotation hack
                         ax.annotate('EXP1', xy=(x_p1, 0.5), ha='center', va='bottom', fontsize=9, color='gray', fontweight='bold')

                # --- P2 (Right) ---
                if p2_g_avg is not None and p2_t_avg is not None:
                    x_p2 = pos + 0.15
                    improved = p2_t_avg >= p2_g_avg
                    line_color = '#27AE60' if improved else '#E74C3C'
                    marker = '^' if improved else 'v'
                    
                    ax.plot([x_p2, x_p2], [p2_g_avg, p2_t_avg], color=line_color, linewidth=2, alpha=0.8, zorder=2)
                    ax.scatter(x_p2, p2_g_avg, s=120, c=color, marker='o', edgecolors='white', linewidths=1.5, zorder=4, alpha=0.7)
                    ax.scatter(x_p2, p2_t_avg, s=120, c=color, marker=marker, edgecolors='white', linewidths=1.5, zorder=4, alpha=0.9)

                    if idx == 0 and pos == 0:
                         ax.annotate('EXP2', xy=(x_p2, 0.5), ha='center', va='bottom', fontsize=9, color='gray', fontweight='bold')
                
                # Vertical Separator
                if pos < len(writers) - 1:
                    ax.axvline(x=pos + 0.5, color='gray', linestyle='-', linewidth=0.5, alpha=0.2)
                    
                pos += 1

        # Axis Styling
        ax.set_xticks(x_ticks)
        ax.set_xticklabels(x_labels, fontsize=11, fontweight='bold')
        ax.set_ylabel('Avg Total Score (0-20)', fontsize=12)
        ax.set_title(f'Assignment {assignment[1]} (Averaged across 3 Graders)', fontsize=14, fontweight='bold', pad=15)
        ax.grid(True, alpha=0.15, axis='y', linestyle='--')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.set_ylim(0, 26)

    # Main Title
    fig.suptitle('Consensus Performance: Average Total Scores\n(Smoothed out grader biases)', fontsize=18, fontweight='bold', y=0.96)
    
    # Simple Legend
    legend_elements = [
        Line2D([0], [0], color='gray', linestyle='-', linewidth=2, label='Left: EXP1 | Right: EXP2'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='gray', markersize=10, label='Generated'),
        Line2D([0], [0], marker='^', color='w', markerfacecolor='gray', markersize=10, label='Tune Improved'),
        Line2D([0], [0], marker='v', color='w', markerfacecolor='gray', markersize=10, label='Tune Declined'),
    ]
    axes[0].legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1, 1), fontsize=10)

    plt.tight_layout()
    plt.subplots_adjust(top=0.90, right=0.85)
    return fig


if __name__ == "__main__":
    folder_path = 'data/critical_thinking'
    output_dir = 'src/visualization/rubric_plots'
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    print(f"Generating score comparison chart from {folder_path}...")
    fig, axes = plot_all_assignments(folder_path)
    
    output_path = os.path.join(output_dir, 'score_comparison_between_prompts.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Saved score comparison chart to {output_path}")
    plt.close()

    print(f"Generating AVERAGE score chart...")
    fig_avg = plot_average_scores(folder_path)
    output_path_avg = os.path.join(output_dir, 'average_total_scores.png')
    plt.savefig(output_path_avg, dpi=300, bbox_inches='tight')
    print(f"Saved average score chart to {output_path_avg}")
    plt.close()
