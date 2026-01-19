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
                        ax.annotate('P1', xy=(x_p1, 0.5), ha='center', va='bottom', fontsize=8, color='gray', fontweight='bold')


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
                        
                        ax.text(x_p2, ymax + 0.8, "P2 Better", ha='center', va='bottom', fontsize=7, fontweight='bold', color='#C0392B')

                    # Orientation Label (Only for the first slot in the chart)
                    if show_orientation_labels and graders.index(grader) == 0:
                        ax.annotate('P2', xy=(x_p2, 0.5), ha='center', va='bottom', fontsize=8, color='gray', fontweight='bold')

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
        Line2D([0], [0], color='gray', linestyle='-', linewidth=2, label='Left Line: P1'),
        Line2D([0], [0], color='gray', linestyle='-', linewidth=2, label='Right Line: P2'),
    ]
    
    axes[0].legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1.01, 1), borderaxespad=0, fontsize=10)

    # Center main title relative to the plot area (not the figure)
    left, right = 0.1, 0.85
    title_x = (left + right) / 2
    fig.suptitle('Comparison of Prompt 1 vs Prompt 2 Performance\n(Total Score / 20)', fontsize=20, fontweight='bold', x=title_x, y=0.97)
    
    plt.tight_layout()
    plt.subplots_adjust(left=left, right=right, top=0.90, bottom=0.08, hspace=0.3)
    return fig, axes

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
