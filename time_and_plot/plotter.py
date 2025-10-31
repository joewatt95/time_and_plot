"""This module contains the plotting functionality."""

from collections.abc import Sequence
import matplotlib.pyplot as plt
import numpy as np
from typing import Optional

def plot_results(
    values: Sequence[str],
    means: Sequence[float],
    reps: int,
    parallel_workers: int,
    command_template: str,
    show_plot: bool,
    output_plot: Optional[str],
) -> None:
    """
    Generates, displays, and saves a plot of values vs. mean timings.

    Args:
        values: A list of the input values (x-axis).
        means: A list of the corresponding mean execution times (y-axis).
        reps: The number of repetitions for each value.
        parallel_workers: The number of parallel workers used.
        command_template: The command that was run, for the plot title.
        show_plot: Whether to display the plot interactively.
        output_plot: The path to save the plot image to.
    """
    x_axis_labels = values

    # Convert to numpy arrays for easier math
    mean_np = np.array(means)

    plt.figure(figsize=(10, 7))

    # Plot the mean data
    plt.plot(x_axis_labels, mean_np, "-o", label="Mean Execution Time")

    # Add titles and labels
    plt.title("Command Execution Time Analysis", fontsize=16)
    plt.suptitle(
        f"Command: {command_template} (reps={reps}, workers={parallel_workers})",
        fontsize=10,
        y=0.92,
    )
    plt.xlabel("Input Value", fontsize=12)
    plt.ylabel("Execution Time (seconds)", fontsize=12)

    # Add grid, legend, and layout adjustments
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend()
    plt.tight_layout(rect=(0, 0, 1, 0.95))

    if output_plot:
        plt.savefig(output_plot)
        print(f"\nPlot saved as '{output_plot}'")

    if show_plot:
        print("\nDisplaying plot interactively...")
        plt.show()