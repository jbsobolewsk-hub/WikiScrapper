# wikiscrapper_tests.py

import unittest


def main():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.discover(
        "./", pattern="unit_test.py")
    )

    suite.addTests(loader.discover(
        "./", pattern="integration_test.py")
    )

    runner = unittest.TextTestRunner(
        verbosity=1, warnings='ignore'
    )

    runner.run(suite)


if __name__ == "__main__":
    main()
