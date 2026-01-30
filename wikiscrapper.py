# wikiscrapper.py

from config.args_parser import parse_args
from config.run_modes import *


def main() -> None:
    args = parse_args()

    if args.summary:
        handle_summary(phrase=args.summary)

    elif args.table:
        handle_table(
            phrase=args.table,
            number=args.number,
            header=args.first_row_is_header
        )

    elif args.count_words:
        handle_count_words(args.count_words)

    elif args.auto_count_words:
        handle_auto_count(
            phrase=args.auto_count_words,
            depth=args.depth,
            wait=args.wait
        )

    elif args.analyze_relative_word_frequency:
        handle_analysis(
            mode=args.mode,
            count=args.count,
            chart=args.chart
        )

    else:
        print("No valid arguments provided")

    exit(0)


if __name__ == "__main__":
    main()
