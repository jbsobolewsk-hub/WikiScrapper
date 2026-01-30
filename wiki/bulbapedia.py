# wiki/bulbapedia.py

from abc import ABC
from dataclasses import dataclass
from re import sub, compile, IGNORECASE
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup, Tag
from requests.exceptions import RequestException

from wiki.client import WikiClient


@dataclass
class Cell:
    value: str | None
    merged: bool
    merge_id: int | None


class BulbapediaClient(WikiClient, ABC):
    _BULBAPEDIA_ARTICLE_RE = compile(
        r'^https?://(?:www\.)?bulbapedia\.bulbagarden\.net/wiki/[^:#?\s]+$',
        IGNORECASE,
    )

    _URL_BASE = compile(
        r'^http[^#?\s]+$',
        IGNORECASE
    )

    def __init__(self):
        self.base_url = "https://bulbapedia.bulbagarden.net"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "WikiScrapper/BulbapediaClient"
        })

    def search(self, query: str) -> BeautifulSoup:
        """
        Searches Bulbapedia for a given query.
        Returns BeautifulSoup object with page HTML.
        """

        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        url = self.__build_article_url(query)

        try:
            response = self.session.get(url, timeout=10)
        except RequestException as exc:
            self.__request_failed(exc)

        if response.status_code != 200:
            self.__query_not_found(query)

        soup = BeautifulSoup(response.text, "html.parser")

        if self.__is_missing_article(soup):
            self.__query_not_found(query)

        return soup

    def close(self):
        """Closes underlying HTTP session."""
        self.session.close()

    def get_summary(self, soup: BeautifulSoup) -> str:
        """Returns the first summary paragraphs of an article as plain text."""

        content_div = soup.find("div", id="mw-content-text")
        if not content_div:
            return ""

        # Get all <p> in div, ignoring empty and const tags
        paragraphs = content_div.find_all("p", recursive=True)
        summary_texts = []
        for p in paragraphs:
            text = p.get_text(strip=False)
            if text:
                summary_texts.append(text)

            # End after first text block
            if summary_texts:
                break

        summary_text = " ".join(summary_texts)

        # Delete redundant whitespace characters
        summary_text = sub(r'\s+([.,;:!?%)])', r'\1', summary_text)
        summary_text = sub(r'([(\[¿¡])\s+', r'\1', summary_text)

        return summary_text.replace(". ", ".\n").strip()

    def _cleanup_df(df: pd.DataFrame) -> pd.DataFrame:
        df = df.dropna(axis=0, how="all")
        df = df.dropna(axis=1, how="all")
        return df.reset_index(drop=True)

    def _collapse_ul_corner(grid: list[list[Cell]]) -> None:
        ul = grid[0][0]
        if not ul.merged:
            return

        mid = ul.merge_id
        max_r = max(i for i, row in enumerate(grid) if
                    any(c.merge_id == mid for c in row))
        max_c = max(j for j in range(len(grid[0])) if
                    any(row[j].merge_id == mid for row in grid))

        # keep only bottom-right
        for i in range(len(grid)):
            for j in range(len(grid[0])):
                if grid[i][j].merge_id == mid and (i, j) != (max_r, max_c):
                    grid[i][j] = Cell(None, False, None)

    def _drop_merged_axes(grid: list[list[Cell]]) -> list[list[Cell]]:
        rows_to_keep = [
            i for i, row in enumerate(grid)
            if not all(c.merged for c in row if c.value is not None)
        ]

        cols_to_keep = [
            j for j in range(len(grid[0]))
            if not all(grid[i][j].merged for i in range(len(grid)) if
                       grid[i][j].value is not None)
        ]

        return [
            [grid[i][j] for j in cols_to_keep]
            for i in rows_to_keep
        ]

    def _grid_to_df(grid: list[list[Cell]]) -> pd.DataFrame:
        return pd.DataFrame([[c.value for c in row] for row in grid])

    @staticmethod
    def _expand_table(table: Tag) -> list[list[Cell]]:
        grid: list[list[Cell]] = []
        spans: dict[tuple[int, int], tuple[int, Cell]] = {}
        merge_counter = 0

        rows = table.find_all("tr")

        for r_idx, row in enumerate(rows):
            grid.append([])
            c_idx = 0

            while (r_idx, c_idx) in spans:
                cell, rows_left = spans.pop((r_idx, c_idx))
                grid[r_idx].append(cell)
                if rows_left > 1:
                    spans[(r_idx + 1, c_idx)] = (cell, rows_left - 1)
                c_idx += 1

            for tag in row.find_all(["td", "th"]):
                rowspan = int(tag.get("rowspan", 1))
                colspan = int(tag.get("colspan", 1))
                text = tag.get_text(strip=True) or None

                merged = rowspan > 1 or colspan > 1
                merge_id = merge_counter if merged else None
                if merged:
                    merge_counter += 1

                cell = Cell(text, merged, merge_id)

                for _ in range(colspan):
                    grid[r_idx].append(cell)
                    if rowspan > 1:
                        spans[(r_idx + 1, c_idx)] = (cell, rowspan - 1)
                    c_idx += 1

        max_cols = max(len(r) for r in grid)
        for r in grid:
            r.extend([Cell(None, False, None)] * (max_cols - len(r)))

        return grid

    def get_tables(
        self,
        soup: BeautifulSoup,
        table_index: int = 0,
        header: bool = True
    ) -> pd.DataFrame:

        content_div = soup.find("div", id="mw-content-text")
        if not content_div:
            raise LookupError("Content not found on the page.")

        tables = [
            t for t in content_div.find_all("table")
            if not set(t.get("class", [])) & {"toc", "navbox"}
        ]

        if table_index >= len(tables):
            raise IndexError(
                f"Requested table index {table_index} out of range. Only {len(tables)} tables found."
            )

        grid = self._expand_table(tables[table_index])
        if header:
            BulbapediaClient._collapse_ul_corner(grid)
            grid = BulbapediaClient._drop_merged_axes(grid)

        df = BulbapediaClient._grid_to_df(grid)
        df = df.dropna(axis=0, how="all").dropna(axis=1,
                                                 how="all").reset_index(
            drop=True)
        df = BulbapediaClient._cleanup_df(df)

        return df

    def get_page_text(self, soup: BeautifulSoup) -> str:
        """
        Returns full page text as plain text, ignoring constant page elements
        and removing embedded URLs and HTML tags.
        """

        content_div = soup.find("div", id="mw-content-text")
        if not content_div:
            return ""

        # Remove constant elements: navboxes, infoboxes, tables of contents, and scripts/styles
        for selector in ['table.navbox', 'table.infobox', 'div.toc', 'style',
                         'script', 'table.metadata']:
            for el in content_div.select(selector):
                el.decompose()

        # Remove embedded links but keep text
        for a in content_div.find_all("a", recursive=True):
            a.unwrap()  # keeps text, removes <a> tag

        # Remove images, spans, references
        for selector in ['sup', 'span', 'img', 'table']:
            for el in content_div.select(selector):
                el.decompose()

        # Get all remaining text
        text = content_div.get_text()

        return text.lower()

    def get_links(self, soup: BeautifulSoup) -> list[str]:
        links: set[str] = set()

        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"].strip()

            # reject fragments
            if href.startswith("#"):
                continue

            # absolute URL
            if BulbapediaClient._URL_BASE.match(href):
                # allow only canonical Bulbapedia article URLs
                if not BulbapediaClient._BULBAPEDIA_ARTICLE_RE.match(href):
                    continue
                full_url = href

            # relative URL
            else:
                # only /wiki/... paths
                if not href.startswith("/wiki/"):
                    continue

                # reject non-article namespaces and queries
                if ":" in href or "?" in href or "#" in href:
                    continue

                # reject main page
                if href in ("/wiki/Main_Page", "/wiki/"):
                    continue

                full_url = urljoin(self.base_url, href)

            links.add(full_url)

        return list(links)

    # ========================
    # Private helper methods
    #   - error handling
    # ========================

    def __build_article_url(self, query: str) -> str:
        """
        Converts query into Bulbapedia article URL.
        If query is already a valid Bulbapedia article URL,
        returns it unchanged.
        """
        query = query.strip()

        if self._BULBAPEDIA_ARTICLE_RE.match(query):
            return query

        normalized = query.replace(" ", "_")
        return f"{self.base_url}/wiki/{normalized}"

    def __is_missing_article(self, soup: BeautifulSoup) -> bool:
        """
        Detects Bulbapedia 'page does not exist' content.
        """
        content = soup.find("div", id="mw-content-text")
        if not content:
            return True

        missing_phrases = [
            "There is currently no text in this page",
            "You can search for this page title"
        ]

        text = content.get_text()
        return any(phrase in text for phrase in missing_phrases)

    def __request_failed(self, exc: Exception):
        raise ConnectionError(
            f"Request to Bulbapedia failed: {exc}"
        ) from exc

    def __query_not_found(self, query: str):
        raise LookupError(
            f"Bulbapedia article not found for query: '{query}'"
        )

    # ========================
    # support for java-style
    # "try with resources"
    # ========================

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __enter__(self):
        return self
