"""This module contains the configuration data structure for the application."""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    """
    Holds the configuration for the application.
    """

    command: str
    values: Sequence[str]
    repetitions: int
    show_plot: bool
    output_plot: Optional[str]
    output_stats: Optional[str]
    no_tui: bool
    verbose: int
    parallel_workers: int = 1
