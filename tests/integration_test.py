# tests/integration_test.py
import os
import unittest

import pandas as pd

from config.run_modes import handle_count_words
from utils.text_utils import count_words, article_analysis, language_analysis
from wiki.bulbapedia import BulbapediaClient


class BulbapediaIntegrationTest(unittest.TestCase):

    def setUp(self):
        if os.path.exists("/../word-counts.json"):
            os.remove("/../word-counts.json")

        self.client = BulbapediaClient()

    def tearDown(self):
        self.client.close()

    def test_summary(self):
        summary = self.client.get_summary(
            self.client.search("Team Rocket")
        )

        self.assertStartsWith(summary, "Team Rocket")
        self.assertEndsWith(summary, "Sevii Islands.")

    def test_table(self):
        search = self.client.search("Type")

        table_1: pd.DataFrame = self.client.get_tables(
            search,
            0,
            False
        )

        self.assertIsNotNone(table_1)
        self.assertListEqual(list(table_1.shape), [31, 7])
        self.assertEqual(table_1.iloc[30][6], "Stellar")

        table_2 = self.client.get_tables(
            search,
            1,
            False
        )

        self.assertIsNotNone(table_2)
        self.assertListEqual(list(table_2.shape), [21, 20])
        self.assertEqual(table_2.iloc[19][0], "Attacking\xa0type")

    def test_table_no_header(self):
        table: pd.DataFrame = self.client.get_tables(
            self.client.search("Type"),
            1,
            True
        )

        self.assertIsNotNone(table)
        self.assertListEqual(list(table.shape), [19, 19])
        self.assertEqual(table.iloc[0][0], "×")
        self.assertEqual(table.iloc[0][1], "Normal")
        self.assertEqual(table.iloc[0][18], "Fairy")
        self.assertEqual(table.iloc[1][0], "Normal")
        self.assertEqual(table.iloc[18][0], "Fairy")

    def test_count_words(self):
        if os.path.exists("./word-counts.json"):
            os.remove("./word-counts.json")

        handle_count_words("Team Rocket")

        text: str = self.client.get_page_text(
            self.client.search("Team Rocket")
        )

        counts: dict = count_words(text)

        self.assertIsNotNone(counts)
        self.assertEqual(len(counts), 1496)

        self.assertTrue("if" in counts)
        self.assertTrue("pokémon" in counts)
        self.assertTrue("islands" in counts)

        self.assertEqual(counts["if"], 3)
        self.assertEqual(counts["pokémon"], 94)
        self.assertEqual(counts["islands"], 10)

        self.assertTrue(os.path.exists("./word-counts.json"))

    def test_article_analysis(self):
        if os.path.exists("./word-counts.json"):
            os.remove("./word-counts.json")

        handle_count_words("Team Rocket")

        data: pd.DataFrame = article_analysis(4)

        self.assertIsNotNone(data)
        self.assertEqual(data.loc[3][0], "rocket")
        self.assertEqual(str(data.loc[3][1]), "4.31")
        self.assertEqual(str(data.loc[3][2]), "0.18")

    def test_language_analysis(self):
        if not os.path.exists("./word-counts.json"):
            handle_count_words("Team Rocket")

        data: pd.DataFrame = language_analysis(3)

        self.assertIsNotNone(data)
        self.assertEqual(data.loc[2][0], "and")
        self.assertEqual(str(data.loc[2][1]), "7.41")
        self.assertEqual(str(data.loc[2][2]), "0.22")


if __name__ == '__main__':
    unittest.main(warnings='ignore')
