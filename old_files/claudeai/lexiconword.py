import pandas as pd

def build_lexicon_stats(csv_path, top_at_least=4, less_below=3, dedupe=True):
    """
    one-call function:
      - read csv (source, category, phrase)
      - normalize phrases
      - (optional) drop duplicate (source, phrase) rows
      - compute counts per phrase: sources_mentioning, total_mentions
      - return (table, top_list, less_list)
    """
    df = pd.read_csv(csv_path)
    df["phrase_norm"] = df["phrase"].str.strip().str.lower()
    if dedupe:
        df = df.drop_duplicates(subset=["source", "phrase_norm"])

    # both become the same if each source lists a phrase once
    counts = (
        df.groupby("phrase_norm")["source"]
          .nunique()
          .rename("sources_mentioning")
          .sort_values(ascending=False)
          .to_frame()
    )
    counts["total_mentions"] = counts["sources_mentioning"]  # same in your case

    # sort by sources_mentioning then phrase
    table = counts.sort_values(["sources_mentioning", "total_mentions",], ascending=False)

    # buckets
    top_list  = table.query("sources_mentioning >= @top_at_least").index.tolist()
    less_list = table.query("sources_mentioning <  @less_below").index.tolist()

    return table, top_list, less_list

