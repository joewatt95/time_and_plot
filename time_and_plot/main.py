"""This module contains the main entry point for the application."""

import argparse
import sys
import logging

from .config import Config
from .console import console_main
from .results import process_and_output_results
from .utils import setup_jobs

# Default number of times to run the command for each value to get an average.
DEFAULT_REPS = 5

# Configure basic logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    """
    Parses arguments and orchestrates the timing, UI, and plotting.
    """
    parser = argparse.ArgumentParser(
        description="Run a command with different values, time it, and plot the results.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example Usage:
  # Time 'sleep' and show the plot interactively
  python -m time_and_plot --show-plot "sleep {}" 0.1 0.2 0.5 1.0

  # Time 'my_app' and save the plot to a file
  python -m time_and_plot --output-plot my_plot.svg "my_app -n {}" 100 500

  # Time, save the plot, and also show it
  python -m time_and_plot --show-plot --output-plot my_plot.svg "sleep {}" 0.1 0.2

  # Save statistics to a CSV file
  python -m time_and_plot --output-stats stats.csv "sleep {}" 0.1 0.2
""",
    )

    parser.add_argument(
        "command",
        type=str,
        help="The command template to run, with '{}' as the placeholder for the value.",
    )

    parser.add_argument(
        "values",
        type=str,
        nargs="+",
        help="One or more values to substitute into the command placeholder.",
    )

    parser.add_argument(
        "-r",
        "--reps",
        type=int,
        default=DEFAULT_REPS,
        help=f"Number of repetitions for each value to average. Default: {DEFAULT_REPS}",
    )

    parser.add_argument(
        "-p",
        "--parallel",
        type=int,
        default=None,
        help="Maximum number of parallel processes to use. Default: (all available cores)",
    )

    parser.add_argument(
        "--show-plot",
        action="store_true",
        help="Show the plot interactively.",
    )

    parser.add_argument(
        "--output-plot",
        type=str,
        default=None,
        help="Output filename for the plot.",
    )

    parser.add_argument(
        "--output-stats",
        type=str,
        default=None,
        help="Output filename for the statistics in CSV format. If not provided, no CSV is generated.",
    )

    parser.add_argument(
        "--no-tui",
        action="store_true",
        help="Disable the TUI and use simple console logging instead.",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase verbosity (e.g., -v, -vv, -vvv).",
    )

    args = parser.parse_args()

    config = Config(
        command=args.command,
        values=args.values,
        repetitions=args.reps,
        parallel_workers=args.parallel,
        show_plot=args.show_plot,
        output_plot=args.output_plot,
        output_stats=args.output_stats,
        no_tui=args.no_tui,
        verbose=args.verbose,
    )

    # Set logging level based on verbosity flag
    match config.verbose:
        case 1:
            logger.setLevel(logging.DEBUG)
        case v if v >= 2:
            logger.setLevel(logging.NOTSET)  # Show all messages
        case _:
            logger.setLevel(logging.INFO)

    job_results_by_val = None

    # --- Main Execution ---
    if config.no_tui:
        try:
            job_id_to_info = setup_jobs(config.values, config.repetitions)
            job_results_by_val = console_main(config, job_id_to_info, logger)
        except KeyboardInterrupt:
            logger.info("Operation cancelled by user.")
            sys.exit(0)
    else:
        try:
            from .tui.app import tui_main

            job_results_by_val = tui_main(config)
        except Exception as e:
            logger.error(f"An unexpected TUI error occurred: {e}")
            logger.error("Please try again with the --no-tui flag.")
            sys.exit(1)

    # --- Final Output Processing ---
    if job_results_by_val is not None:
        process_and_output_results(config, job_results_by_val)


if __name__ == "__main__":
    main()
