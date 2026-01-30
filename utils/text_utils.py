# utils/text_utils.py

import json
import re
from collections import Counter

import pandas as pd
from wordfreq import zipf_frequency

_WORD_RE = re.compile(r"[^\W\d_]+", re.UNICODE)


def count_words(text: str) -> dict[str, int]:
    """
    Counts word occurrences in text.
    A word is any contiguous sequence of Unicode letters.
    """
    return Counter(_WORD_RE.findall(text))


def __process_json_file(path: str) -> Counter:
    counter = Counter()

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            print(type(data))

            if isinstance(data, str):
                texts = [data]
            elif isinstance(data, list):
                texts = (t for t in data if isinstance(t, str))
            elif isinstance(data, dict):
                texts = (v for v in data.values() if isinstance(v, str))
            else:
                return counter

            for text in texts:
                counter.update(_WORD_RE.findall(text.lower()))

            return counter

    except Exception:
        print("Failed to process json file")
        return counter


def __collect_graph_data(lang: str = "en") -> pd.DataFrame:
    result = []

    with open("word-counts.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        for word, wiki_count in data.items():
            rel = zipf_frequency(word, lang)
            rel_count = rel if rel > 0 else 0
            result.append((word, rel_count, round(wiki_count / 1000, 2)))

    return pd.DataFrame(result, columns=["word", "rel_freq", "wiki_freq"])


def __sort_by_wiki_count(
    data: pd.DataFrame,
    descending: bool = True
) -> pd.DataFrame:
    return (
        data
        .sort_values(
            by="wiki_freq",
            ascending=not descending,
            kind="mergesort"
        )
        .reset_index(drop=True)
    )


def __sort_by_rel_count(
    data: pd.DataFrame,
    descending: bool = True
) -> pd.DataFrame:
    return (
        data
        .sort_values(
            by="rel_freq",
            ascending=not descending,
            kind="mergesort"
        )
        .reset_index(drop=True)
    )


def article_analysis(count: int) -> pd.DataFrame:
    return (
        __sort_by_wiki_count(__collect_graph_data())
        .iloc[:count]
        .fillna(0)
        .reset_index(drop=True)
    )


def language_analysis(count: int) -> pd.DataFrame:
    return (
        __sort_by_rel_count(__collect_graph_data())
        .iloc[:count]
        .fillna(0)
        .reset_index(drop=True)
    )


def update_wiki_dict(counts: Counter) -> None:
    file_path = "word-counts.json"
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            stored_counts = Counter(json.load(f))
    except (FileNotFoundError, IOError):
        stored_counts = Counter()

    stored_counts.update(counts)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(dict(stored_counts), f, ensure_ascii=False, indent=2)
