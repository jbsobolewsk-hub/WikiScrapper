# config/args_parser.py

import argparse


def validate_args(parser, args):
    if args.table:
        if args.number is None:
            parser.error("--table requires --number option")

    if args.analyze_relative_word_frequency:
        if args.mode is None or args.count is None:
            parser.error(
                "--analyze-relative-word-frequency requires --mode and --count options"
            )

    if args.auto_count_words:
        if args.depth is None or args.wait is None:
            parser.error(
                "--auto-count-words requires --depth and --wait options"
            )


def parse_args():
    parser = argparse.ArgumentParser(
        description="WikiScrapper - wiki scrapping and textual analysis"
    )

    # ===== PROGRAM RUNNING MODES =====
    mode = parser.add_mutually_exclusive_group(required=True)

    mode.add_argument(
        "--summary",
        metavar="PHRASE",
        help="Shows plain text of the wiki page related to searched phrase"
    )

    mode.add_argument(
        "--table",
        metavar="PHRASE",
        help="Finds the --number n table on the wiki page and saves it to 'searched phrase'.csv"
    )

    mode.add_argument(
        "--count-words",
        metavar="PHRASE",
        help="Counts on the wiki page and saves the summarised totals to 'searched phrase'.json'"
    )

    mode.add_argument(
        "--analyze-relative-word-frequency",
        action="store_true",
        help="Analyzes word counts in wiki page relative to average " +
             "statistical frequencies of the article's language " +
             "--chart option saves the analysis results to provided directory"
    )

    mode.add_argument(
        "--auto-count-words",
        metavar="PHRASE",
        help="Counts words in the searched and linked articles"
    )

    # ===== RELATED OPTIONS AND MODIFIERS =====
    parser.add_argument(
        "--number",
        type=int,
        help="n_th table on the page, starting from 1",
        default=1
    )

    parser.add_argument(
        "--first-row-is-header",
        action="store_true",
        help="Flag to treat the first row as column headers"
    )

    parser.add_argument(
        "--mode",
        choices=["article", "language"],
        help="Analysis mode and data sorting"
    )

    parser.add_argument(
        "--count",
        type=int,
        help="Number of top words to include in analysis"
    )

    parser.add_argument(
        "--chart",
        metavar="PATH",
        help="File path to produced chart"
    )

    parser.add_argument(
        "--depth",
        type=int,
        help="Depth of URL expansion"
    )

    parser.add_argument(
        "--wait",
        type=float,
        help="Timeout (sec)"
    )

    args = parser.parse_args()
    validate_args(parser, args)
    return args
