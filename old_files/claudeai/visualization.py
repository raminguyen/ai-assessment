import matplotlib.pyplot as plt

def plot_top_less(df, top_words, less_words, essays=("V1","V4"), title="Causation Words: V1 vs V4"):
    """
    df: DataFrame (rows = essays, cols = words)
    top_words: list of words (e.g., TOP_CAUSATION)
    less_words: list of words (e.g., LESS_CAUSATION)
    essays: which rows to show (default V1, V4)
    title: figure title
    """
    # keep only words that exist
    top_cols  = [w for w in top_words  if w in df.columns]
    less_cols = [w for w in less_words if w in df.columns]

    # subset essays
    df_v = df.loc[list(essays)]

    # make plots
    fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharey=True)

    # left: top words
    (df_v[top_cols].T).plot(kind="bar", ax=axes[0], width=0.75, color=["#4e79a7", "#f28e2b"])
    axes[0].set_title("Top Words")
    axes[0].set_xlabel("Words")
    axes[0].set_ylabel("Count")
    axes[0].legend(title="Essay")

    # right: less words
    (df_v[less_cols].T).plot(kind="bar", ax=axes[1], width=0.75, color=["#4e79a7", "#f28e2b"])
    axes[1].set_title("Less Words")
    axes[1].set_xlabel("Words")
    axes[1].legend(title="Essay")

    # add small numbers on bars
    for ax in axes:
        for p in ax.patches:
            h = p.get_height()
            if h > 0:
                ax.annotate(str(int(h)),
                            (p.get_x() + p.get_width()/2.0, h),
                            ha="center", va="bottom", fontsize=8)

    fig.suptitle(title, fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.show()
