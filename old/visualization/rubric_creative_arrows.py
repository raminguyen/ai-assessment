import sys
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from matplotlib.lines import Line2D
import matplotlib.patches as mpatches

# Add project root to sys.path to allow importing from src
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent
sys.path.append(str(project_root))

from src.visualization.rubric_avg_progress import load_data, WRITERS, WRITER_COLORS, DIMENSIONS, SHORT_DIMS

OUTPUT_DIR = Path('src/visualization/rubric_plots')

def plot_creative_arrows(assignment='a1', prompt_num=2):
    """
    Visualizes score progression using a Grouped Arrow/Dumbbell Chart.
    This avoids the 'spaghetti' look of overlapping line charts by isolating
    each dimension and showing the Gen -> Tune movement clearly.
    """
    print(f"Generating creative arrow plots for {assignment.upper()} Prompt {prompt_num}...")
    data = load_data(assignment, prompt_num)
    
    # 2x2 Grid
    fig, axes = plt.subplots(2, 2, figsize=(22, 14), sharex=True, sharey=True)
    axes = axes.flatten()
    
    fig.suptitle(f'Score Progression by Grader: {assignment.upper()} - Prompt {prompt_num}\n(Arrow indicates shift from Gen -> Tune)', 
                 fontsize=22, fontweight='bold', color='#2c3e50', y=0.98)

    # Configuration for grouped bars/arrows
    bar_width = 0.2
    # Offsets for 3 graders: -1, 0, +1 times the width
    offsets = [-bar_width, 0, bar_width]
    
    # Y-axis ticks
    y_range = np.arange(0, 6)

    for idx, writer in enumerate(WRITERS):
        ax = axes[idx]
        ax.set_title(f"Writer: {writer.upper()}", fontsize=16, fontweight='bold', 
                     color=WRITER_COLORS[writer], pad=20)
        
        graders = [g for g in WRITERS if g != writer]
        
        # Draw nice background bands for dimensions to distinguish them
        for d_i in range(0, len(DIMENSIONS), 2):
            ax.axvspan(d_i - 0.5, d_i + 0.5, color='#f2f2f2', alpha=0.5, zorder=0)

        for dim_i, dim in enumerate(DIMENSIONS):
            for g_i, grader in enumerate(graders):
                grader_color = WRITER_COLORS[grader]
                pair_data = data[writer][grader]
                
                gen_score = pair_data['gen'].get(dim, 0.0) if pair_data['gen'] else 0
                tune_score = pair_data['tune'].get(dim, 0.0) if pair_data['tune'] else 0
                
                # Skip if missing data (0.0 often implies missing in this context, or distinct 0 score)
                if gen_score == 0 and tune_score == 0:
                    continue

                # X position for this specific grader arrow
                x_pos = dim_i + offsets[g_i]
                
                # 1. Draw the vertical "track" (faint line) to ground the arrow? 
                # No, simpler is cleaner.
                
                # 2. Draw the Arrow
                # If scores are equal, draw a dot
                if abs(tune_score - gen_score) < 0.1:
                    ax.scatter(x_pos, gen_score, color=grader_color, s=100, alpha=0.8, edgecolors='white', zorder=3)
                else:
                    # Arrow style
                    # arrow_props = dict(facecolor=grader_color, edgecolor=grader_color, width=2, headwidth=8, headlength=8)
                    # ax.annotate('', xy=(x_pos, tune_score), xytext=(x_pos, gen_score), arrowprops=arrow_props)
                    
                    # Manual arrow using plot + marker for better control
                    ax.plot([x_pos, x_pos], [gen_score, tune_score], color=grader_color, linewidth=2, alpha=0.6, zorder=2)
                    
                    # Start Point (Gen) - Hollow Circle
                    ax.scatter(x_pos, gen_score, color='white', edgecolors=grader_color, s=60, linewidth=2, zorder=3)
                    
                    # End Point (Tune) - Filled Triangle/Arrowhead
                    marker = '^' if tune_score > gen_score else 'v'
                    ax.scatter(x_pos, tune_score, color=grader_color, marker=marker, s=80, zorder=3)

        # Formatting
        ax.set_xticks(np.arange(len(DIMENSIONS)))
        ax.set_xticklabels(SHORT_DIMS, fontsize=11, fontweight='500')
        ax.set_yticks(y_range)
        ax.set_ylim(0, 5.5)
        ax.grid(axis='y', linestyle='--', alpha=0.3, zorder=0)
        
        # Remove spines
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#bdc3c7')
        ax.spines['bottom'].set_color('#bdc3c7')
        
        # Internal Legend for this plot (Graders)
        # Only needed on the first plot or all? All is safer for quick lookup.
        legend_handles = []
        for g in graders:
            legend_handles.append(mpatches.Patch(color=WRITER_COLORS[g], label=g.title()))
        
        ax.legend(handles=legend_handles, loc='upper center', bbox_to_anchor=(0.5, -0.05),
                  ncol=3, frameon=False, fontsize=10)

    # Adjust layout to make room for x-labels and legends
    plt.tight_layout()
    plt.subplots_adjust(top=0.90, hspace=0.35, bottom=0.05)
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / f'{assignment}_p{prompt_num}_creative_arrows.png'
    plt.savefig(out_path, dpi=600, bbox_inches='tight')
    print(f"Saved creative arrow plot to {out_path}")
    plt.close()

def plot_all_assignments_creative(prompt_num=2):
    """
    Combines all 3 assignments (A1, A2, A3) into a single 3x4 grid visualization.
    Rows: Assignments
    Cols: Writers
    """
    print(f"Generating Combined Creative Arrow Plots for Prompt {prompt_num}...")
    
    assignments = ['a1', 'a2', 'a3']
    
    # 3 Rows (Assignments) x 4 Cols (Writers)
    fig, axes = plt.subplots(3, 4, figsize=(24, 18), sharex=True, sharey=True)
    
    fig.suptitle(f'Detailed Score Progression: All Assignments (Prompt {prompt_num})\nRows: Assignments | Cols: Writers', 
                 fontsize=24, fontweight='bold', color='#2c3e50', y=0.98)

    # Configuration for grouped bars/arrows
    bar_width = 0.2
    offsets = [-bar_width, 0, bar_width]
    y_range = np.arange(0, 6)

    for row_idx, assignment in enumerate(assignments):
        data = load_data(assignment, prompt_num)
        
        # Label the Row (Assignment)
        axes[row_idx, 0].set_ylabel(f"{assignment.upper()}", fontsize=18, fontweight='bold', labelpad=10)

        for col_idx, writer in enumerate(WRITERS):
            ax = axes[row_idx, col_idx]
            
            # Label the Column (Writer) - Top Row Only
            if row_idx == 0:
                ax.set_title(f"{writer.upper()}", fontsize=18, fontweight='bold', 
                             color=WRITER_COLORS[writer], pad=20)
            
            graders = [g for g in WRITERS if g != writer]
            
            # Background bands
            for d_i in range(0, len(DIMENSIONS), 2):
                ax.axvspan(d_i - 0.5, d_i + 0.5, color='#f2f2f2', alpha=0.5, zorder=0)

            for dim_i, dim in enumerate(DIMENSIONS):
                for g_i, grader in enumerate(graders):
                    grader_color = WRITER_COLORS[grader]
                    pair_data = data[writer][grader]
                    
                    gen_score = pair_data['gen'].get(dim, 0.0) if pair_data['gen'] else 0
                    tune_score = pair_data['tune'].get(dim, 0.0) if pair_data['tune'] else 0
                    
                    if gen_score == 0 and tune_score == 0:
                        continue

                    x_pos = dim_i + offsets[g_i]
                    
                    # Draw Arrow/Line
                    if abs(tune_score - gen_score) < 0.1:
                        ax.scatter(x_pos, gen_score, color=grader_color, s=80, alpha=0.8, edgecolors='white', zorder=3)
                    else:
                        ax.plot([x_pos, x_pos], [gen_score, tune_score], color=grader_color, linewidth=2, alpha=0.6, zorder=2)
                        
                        # Start (Gen) - Hollow
                        ax.scatter(x_pos, gen_score, color='white', edgecolors=grader_color, s=50, linewidth=2, zorder=3)
                        
                        # End (Tune) - Filled
                        marker = '^' if tune_score > gen_score else 'v'
                        ax.scatter(x_pos, tune_score, color=grader_color, marker=marker, s=60, zorder=3)

            # Formatting
            if row_idx == 2: # X-labels only on bottom row
                ax.set_xticks(np.arange(len(DIMENSIONS)))
                ax.set_xticklabels(SHORT_DIMS, fontsize=10, fontweight='500', rotation=30, ha='right')
            else:
                ax.set_xticks(np.arange(len(DIMENSIONS))) # Keep ticks
                ax.tick_params(labelbottom=False) # Hide labels

            ax.set_yticks(y_range)
            ax.set_ylim(0, 5.5)
            ax.grid(axis='y', linestyle='--', alpha=0.3, zorder=0)
            
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color('#bdc3c7')
            ax.spines['bottom'].set_color('#bdc3c7')
            
            # Legend? Maybe just once or global? 
            # It's dense. Let's put a small legend in the first plot of each row to remind viewers.
            if col_idx == 0 and row_idx == 0:
                legend_handles = []
                for g in WRITERS: # We don't know exactly which graders are present per writer easily without logic, 
                                  # but showing all 4 colors generally helps decode the chart.
                                  # Actually, the graders are everyone EXCEPT the writer. 
                                  # So the colors vary per column. 
                                  # Better to have a global legend at the bottom.
                    pass 

    # Global Legend at the bottom
    legend_handles = [mpatches.Patch(color=WRITER_COLORS[w], label=w.title()) for w in WRITERS]
    legend_handles.append(Line2D([0], [0], color='gray', marker='o', markerfacecolor='white', markeredgecolor='gray', markersize=8, label='Gen Score'))
    legend_handles.append(Line2D([0], [0], color='gray', marker='^', markerfacecolor='gray', markersize=8, label='Tune Improved'))
    legend_handles.append(Line2D([0], [0], color='gray', marker='v', markerfacecolor='gray', markersize=8, label='Tune Declined'))
    
    fig.legend(handles=legend_handles, loc='lower center', ncol=8, fontsize=14, frameon=False, bbox_to_anchor=(0.5, 0.01))

    plt.tight_layout()
    plt.subplots_adjust(top=0.92, bottom=0.08, left=0.05, right=0.98, hspace=0.1, wspace=0.1)
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / f'all_assignments_p{prompt_num}_combined_creative_arrows.png'
    plt.savefig(out_path, dpi=600, bbox_inches='tight')
    print(f"Saved combined creative arrow plot to {out_path}")
    plt.close()

if __name__ == "__main__":
    plot_all_assignments_creative(prompt_num=2)
