import sys
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from matplotlib.lines import Line2D

# Add project root to sys.path to allow importing from src
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent
sys.path.append(str(project_root))

from src.visualization.rubric_avg_progress import load_data, WRITERS, WRITER_COLORS, DIMENSIONS, SHORT_DIMS

OUTPUT_DIR = Path('src/visualization/rubric_plots')

def plot_detailed_progression(assignment='a1', prompt_num=2):
    """
    Plots the detailed score progression (Gen -> Tune) for each Writer,
    showing the individual scores from each Grader (no averaging).
    """
    print(f"Generating detailed progression plots for {assignment.upper()} Prompt {prompt_num}...")
    data = load_data(assignment, prompt_num)
    
    # Setup Figure: 2x2 grid for 4 writers
    fig, axes = plt.subplots(2, 2, figsize=(24, 16), sharex=True, sharey=True)
    axes = axes.flatten()
    
    fig.suptitle(f'Detailed Rubric Progression: {assignment.upper()} - Prompt {prompt_num}\n(Individual Grader Scores: Dashed=Gen, Solid=Tune)', 
                 fontsize=24, fontweight='bold', y=0.98)

    x_indices = np.arange(len(DIMENSIONS))

    for idx, writer in enumerate(WRITERS):
        ax = axes[idx]
        
        # Title
        ax.set_title(f"Writer: {writer.upper()}", fontsize=18, fontweight='bold', 
                     color=WRITER_COLORS[writer], pad=15)
        
        graders = [g for g in WRITERS if g != writer]
        
        for grader in graders:
            grader_color = WRITER_COLORS[grader]
            pair_data = data[writer][grader]
            
            # Extract scores maintaining dimension order
            gen_scores = [pair_data['gen'].get(d, 0.0) for d in DIMENSIONS] if pair_data['gen'] else None
            tune_scores = [pair_data['tune'].get(d, 0.0) for d in DIMENSIONS] if pair_data['tune'] else None
            
            # Plot Gen (Dashed, Lighter)
            if gen_scores:
                ax.plot(x_indices, gen_scores, color=grader_color, linestyle='--', marker='o', 
                        markersize=6, alpha=0.6, label=f'{grader.title()} (Gen)')
            
            # Plot Tune (Solid, Stronger)
            if tune_scores:
                ax.plot(x_indices, tune_scores, color=grader_color, linestyle='-', marker='o', 
                        markersize=8, linewidth=2.5, alpha=0.9, label=f'{grader.title()} (Tune)')
                
                # Draw small arrows or lines connecting Gen -> Tune for this grader
                if gen_scores:
                    for i, (g_val, t_val) in enumerate(zip(gen_scores, tune_scores)):
                        if abs(t_val - g_val) > 0.1: # Only if change is significant
                            arrow_color = '#2ecc71' if t_val > g_val else '#e74c3c'
                            ax.annotate('', xy=(x_indices[i], t_val), xytext=(x_indices[i], g_val),
                                        arrowprops=dict(arrowstyle='->', color=grader_color, alpha=0.5, lw=1.5))

        # Formatting
        ax.set_xticks(x_indices)
        ax.set_xticklabels(SHORT_DIMS, rotation=30, ha='right', fontsize=11)
        ax.set_ylim(0, 5.5)
        ax.grid(True, linestyle='--', alpha=0.3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Legend (Per subplot to identify graders clearly)
        # Custom legend elements to reduce clutter (1 color = 1 grader)
        legend_elements = []
        for g in graders:
            legend_elements.append(Line2D([0], [0], color=WRITER_COLORS[g], lw=2, label=g.title()))
        
        # Add visual guide for Line Styles
        legend_elements.append(Line2D([0], [0], color='gray', linestyle='--', lw=1, label='Gen'))
        legend_elements.append(Line2D([0], [0], color='gray', linestyle='-', lw=2, label='Tune'))

        ax.legend(handles=legend_elements, loc='lower right', fontsize=10, ncol=2, frameon=True, facecolor='#f8f9fa')

    plt.tight_layout()
    plt.subplots_adjust(top=0.90, hspace=0.3)
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / f'{assignment}_p{prompt_num}_detailed_progression.png'
    plt.savefig(out_path, dpi=600, bbox_inches='tight')
    print(f"Saved detailed progression plot to {out_path}")
    plt.close()

if __name__ == "__main__":
    # Default to A1, Prompt 2 as requested
    plot_detailed_progression(assignment='a1', prompt_num=2)
