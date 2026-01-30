# utils/graphic_utils.py

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt


def draw_chart(data: pd.DataFrame, path: str) -> None:
    """
    Draws and saves a chart of the data.
    Expects DataFrame columns: 'word', 'rel_count', 'wiki_count'
    """

    if data.empty:
        raise ValueError("Empty DataFrame")

    required_cols = {"word", "rel_freq", "wiki_freq"}
    if not required_cols.issubset(data.columns):
        raise ValueError(f"DataFrame must contain columns: {required_cols}")

    words = data["word"].to_numpy()
    wiki_counts = data["wiki_freq"].to_numpy()
    rel_counts = data["rel_freq"].to_numpy()

    x = np.arange(len(words))
    width = 0.35

    fig, ax = plt.subplots(
        layout="constrained",
        figsize=(max(10, len(words) * 0.6), 6)
    )

    rects1 = ax.bar(
        x - width / 2,
        wiki_counts,
        width,
        label="wiki",
        color="#fdba45"
    )

    rects2 = ax.bar(
        x + width / 2,
        rel_counts,
        width,
        label="language",
        color="#1e7a3a"
    )

    ax.bar_label(rects1, padding=3)
    ax.bar_label(rects2, padding=3)

    ax.set_ylabel("Counts")
    ax.set_title("Frequencies of some words from the wiki")
    ax.set_xticks(x)
    ax.set_xticklabels(words, rotation=60, ha="right")

    ax.grid(True, which="major", axis="y", linestyle="--", alpha=0.6)
    ax.legend(
        loc="upper left",
        bbox_to_anchor=(0, 1.07),
        ncols=2,
        frameon=False
    )

    plt.savefig(path)
    plt.close()
