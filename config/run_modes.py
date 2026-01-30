# utils/run_modes.py

import time
from collections import deque

from utils.graphic_utils import *
from utils.path_utils import *
from utils.text_utils import *
from wiki.factory import get_wiki_client


def handle_summary(phrase):
    with get_wiki_client() as client:
        summary = client.get_summary(
            client.search(phrase))
        print(summary)


def handle_table(phrase, number, header):
    if number < 1:
        raise IndexError("Table number is 1-based")

    with get_wiki_client() as client:
        table: pd.DataFrame = client.get_tables(
            client.search(phrase),
            number - 1,
            header)  # list <tr>

        table.reset_index(drop=True)
        print(table)

        # filename = f"{safe_filename(phrase)}_{number}.csv"
        # table.to_csv(filename)


def handle_count_words(phrase):
    # 1. Get text
    with get_wiki_client() as client:
        text: str = client.get_page_text(client.search(phrase))

    # 2. Count current words
    current_counts = Counter(count_words(text))
    update_wiki_dict(current_counts)


def handle_analysis(mode, count, chart):
    if mode == "article":
        data = article_analysis(count)
    elif mode == "language":
        data = language_analysis(count)
    else:
        raise ValueError(
            "The only supported analysis modes are 'article' and 'language'")

    print(data)
    if chart:
        draw_chart(data, safe_filename(chart))


def handle_auto_count(phrase: str, depth: int, wait: float) -> None:
    """
    BFS traversal of Wikipedia article graph starting from `phrase`.
    For each visited page, performs count_words(page_text).
    """

    if depth < 0:
        raise ValueError(f"Can't travel negative path length: {depth}")

    if wait < 0:
        raise ValueError(f"Cant wait for negative time: {wait}")

    visited: set[str] = set()
    queue: deque[tuple[str, int]] = deque()
    queue.append((phrase, 0))
    visited.add(phrase)

    with get_wiki_client() as client:
        while queue:
            current_phrase, current_depth = queue.popleft()

            # --- fetch page ---
            page = client.search(current_phrase)
            page_text = client.get_page_text(page)
            counts = Counter(count_words(page_text))
            update_wiki_dict(counts)

            # --- depth limit ---
            if current_depth > depth:
                continue

            # --- wait before next network request ---
            time.sleep(wait)

            # --- fetch links ---
            links = client.get_links(page)

            for link_phrase in links:
                if link_phrase in visited:
                    continue

                visited.add(link_phrase)
                queue.append((link_phrase, current_depth + 1))
