# tests/test_bulbapedia.py

import unittest
from unittest.mock import Mock, patch

import pandas as pd
import requests
from bs4 import BeautifulSoup

from wiki.bulbapedia import BulbapediaClient, Cell


class BulbapediaUnitTests(unittest.TestCase):

    def setUp(self):
        self.client = BulbapediaClient()

    def tearDown(self):
        self.client.close()

    # 1. __build_article_url via search: empty query
    def test_search_empty_query_raises(self):
        with self.assertRaises(ValueError):
            self.client.search("   ")

    # 2. search: non-200 HTTP response
    @patch.object(requests.Session, "get")
    def test_search_http_error_status(self, mock_get):
        mock_resp = Mock(status_code=404, text="<html></html>")
        mock_get.return_value = mock_resp

        with self.assertRaises(LookupError):
            self.client.search("Pikachu")

    # 3. get_summary: extracts first paragraph only
    def test_get_summary_first_paragraph(self):
        html = """
        <div id="mw-content-text">
            <p>First paragraph.</p>
            <p>Second paragraph.</p>
        </div>
        """
        soup = BeautifulSoup(html, "html.parser")
        summary = self.client.get_summary(soup)

        self.assertEqual(summary.strip(), "First paragraph.")

    # 4. _expand_table: handles rowspan/colspan and merge flags
    def test_expand_table_merges(self):
        html = """
        <table>
            <tr><th rowspan="2">A</th><th>B</th></tr>
            <tr><td>C</td></tr>
        </table>
        """
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table")

        grid = BulbapediaClient._expand_table(table)

        self.assertEqual(len(grid), 2)
        self.assertTrue(grid[0][0].merged)
        self.assertEqual(grid[0][0].value, "A")
        self.assertEqual(grid[1][0].value, "A")

    # 5. get_tables: basic table to DataFrame
    def test_get_tables_simple(self):
        html = """
        <div id="mw-content-text">
            <table>
                <tr><th>X</th><th>Y</th></tr>
                <tr><td>1</td><td>2</td></tr>
            </table>
        </div>
        """
        soup = BeautifulSoup(html, "html.parser")
        df = self.client.get_tables(soup)

        expected = pd.DataFrame([["X", "Y"], ["1", "2"]])
        pd.testing.assert_frame_equal(df, expected)

    # 6. get_links: filters only valid Bulbapedia article URLs
    def test_get_links_filters(self):
        html = """
        <div>
            <a href="/wiki/Pikachu">ok</a>
            <a href="/wiki/Main_Page">bad</a>
            <a href="/wiki/File:Img.png">bad</a>
            <a href="https://bulbapedia.bulbagarden.net/wiki/Eevee">ok</a>
            <a href="https://example.com/wiki/Test">bad</a>
        </div>
        """
        soup = BeautifulSoup(html, "html.parser")
        links = self.client.get_links(soup)

        self.assertEqual(
            set(links),
            {
                "https://bulbapedia.bulbagarden.net/wiki/Pikachu",
                "https://bulbapedia.bulbagarden.net/wiki/Eevee",
            },
        )

    # 7. get_page_text: removes links, tables, and lowercases
    def test_get_page_text_cleanup(self):
        html = """
        <div id="mw-content-text">
            <p>Hello <a href="/wiki/Test">World</a></p>
            <table><tr><td>X</td></tr></table>
        </div>
        """
        soup = BeautifulSoup(html, "html.parser")
        text = self.client.get_page_text(soup)

        self.assertIn("hello world", text)
        self.assertNotIn("x", text)

    # 8 sprawdza czy dobrze budowany jest url z podanej frazy
    def test_build_article_url_from_query(self):
        url = self.client._BulbapediaClient__build_article_url("Mr Mime")
        self.assertEqual(
            url,
            "https://bulbapedia.bulbagarden.net/wiki/Mr_Mime"
        )

    # 9 sprawda czy popranie buduje się linki do chodzenia po grafie
    def test_build_article_url_passthrough(self):
        url = "https://bulbapedia.bulbagarden.net/wiki/Pikachu"
        result = self.client._BulbapediaClient__build_article_url(url)
        self.assertEqual(result, url)

    # 10 pusta strona
    def test_missing_article_detection(self):
        html = """
        <div id="mw-content-text">
            There is currently no text in this page.
        </div>
        """
        soup = BeautifulSoup(html, "html.parser")
        missing = self.client._BulbapediaClient__is_missing_article(soup)

        self.assertTrue(missing)

    # 11 formatowanie tabel prz opcji header
    def test_drop_merged_axes_drops_full_merged_row(self):
        grid = [
            [Cell("A", True, 0), Cell("A", True, 0)],
            [Cell("B", False, None), Cell("C", False, None)],
        ]

        result = BulbapediaClient._drop_merged_axes(grid)

        self.assertEqual(len(result), 1)
        self.assertEqual([c.value for c in result[0]], ["B", "C"])


if __name__ == "__main__":
    unittest.main()
