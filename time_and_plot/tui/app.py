"""This module contains the TUI application logic using Textual."""

import statistics
import time
from collections import defaultdict
from collections.abc import MutableSequence
from typing import Optional, cast

from rich.progress_bar import ProgressBar as RichProgressBar
from textual.app import App, ComposeResult
from textual.coordinate import Coordinate
from textual.widgets import DataTable, Footer, Header, Log, ProgressBar, Static

from ..config import Config
from ..runner import run_single_command
from .messages import JobUpdate
from .state import TuiState, Status, ValueStatus


class TuiApp(App):
    """
    A Textual app to display the progress of running commands.
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
    ]

    def __init__(self, config: Config, **kwargs) -> None:
        # kwargs.setdefault("ansi_color", True)
        super().__init__(**kwargs)
        self.config = config
        self.tui_state = TuiState(config)
        self.start_time = time.time()
        self.progress_bars: MutableSequence[RichProgressBar] = []

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Static(f"Command: {self.config.command}")
        yield Static(
            f"Repetitions: {self.config.repetitions}, "
            f"Parallel workers: {self.config.parallel_workers}"
        )
        yield Static(id="total_running_time")
        yield Static(id="overall_progress")
        yield ProgressBar(total=100, id="overall_progress_bar")
        yield DataTable(id="results_table")
        yield Log(id="log", auto_scroll=True)
        yield Footer()

    def on_mount(self) -> None:
        """Called when the app is mounted."""
        self.set_interval(1.0, self.update_running_time)
        self.tui_state.setup_jobs()
        self.query_one(ProgressBar).total = self.tui_state.total_jobs
        self.update_overall_progress()
        self.call_later(self.populate_table)

    def populate_table(self) -> None:
        """Populate the DataTable."""
        table = self.query_one(DataTable)
        table.add_columns("Value", "Progress", "Reps done")

        for stat in ["Mean", "Median", "Min", "Max"]:
            table.add_column(stat, width=12)

        for i, val_stat in enumerate(self.tui_state.value_statuses):
            reps_total = val_stat.reps_total
            progress_bar = RichProgressBar(total=reps_total, width=20)
            self.progress_bars.append(progress_bar)
            table.add_row(
                val_stat.val,
                progress_bar,
                "pending",
                "n/a",
                "n/a",
                "n/a",
                "n/a",
                key=str(i),
            )
        self.submit_jobs()

    def submit_jobs(self) -> None:
        """Submit all jobs to the thread pool."""
        for job_id in range(self.tui_state.total_jobs):
            value_index = self.tui_state.job_id_to_value_index[job_id]
            val = self.tui_state.value_statuses[value_index].val
            self.run_worker(
                lambda job_id=job_id, val=val: run_single_command(
                    job_id,
                    self.config.command,
                    val,
                    self.post_message,
                ),
                thread=True,
                exclusive=False,
            )

    def on_job_update(self, message: JobUpdate) -> None:
        """Update the TUI with the latest job status."""
        update = message.update
        self.tui_state.jobs_completed += 1
        job_id = update.id
        value_index = self.tui_state.job_id_to_value_index[job_id]
        val_stat = self.tui_state.value_statuses[value_index]

        val_stat.reps_done += 1

        match update.status:
            case Status.COMPLETED:
                duration = update.duration
                if duration is not None:
                    val_stat.timings.append(duration)
                self.tui_state.job_results_by_val[val_stat.val].append(
                    duration)
            case Status.FAILED:
                self.tui_state.job_results_by_val[val_stat.val].append(None)
                log = self.query_one(Log)
                log.write_line(
                    f"Job for value {val_stat.val} failed: {update.error}"
                )

        self._update_value_status(val_stat, update.status)

        self.update_overall_progress()
        self.update_table(value_index)

        if self.tui_state.jobs_completed == self.tui_state.total_jobs:
            self.exit(self.tui_state.job_results_by_val)

    def _update_value_status(self, val_stat: ValueStatus, job_update_status: Status) -> None:
        """Update the status of a ValueStatus object based on its repetitions and job update status."""
        if job_update_status == Status.FAILED:
            val_stat.has_failed_reps = True

        match (val_stat.reps_done < val_stat.reps_total, val_stat.has_failed_reps):
            case (True, _):
                val_stat.status = Status.RUNNING
            case (False, True):
                val_stat.status = Status.FAILED
            case (False, False):
                val_stat.status = Status.COMPLETED

    def _format_float(self, value: float) -> str:
        """Formats a float to 4 decimal places."""
        return f"{value:.4f}"

    def update_running_time(self) -> None:
        """Update the total running time display."""
        running_time_widget = self.query_one("#total_running_time", Static)
        elapsed_time = time.time() - self.start_time
        running_time_widget.update(f"Total Running Time: {elapsed_time:.2f}s")

    def update_overall_progress(self) -> None:
        """Update the overall progress indicator."""
        progress_widget = self.query_one("#overall_progress", Static)
        total_jobs = self.tui_state.total_jobs
        completed_jobs = self.tui_state.jobs_completed
        progress_widget.update(
            f"Overall Progress: {completed_jobs} / {total_jobs}")
        self.query_one(ProgressBar).progress = completed_jobs

    def update_table(self, value_index: int) -> None:
        """Update a row in the DataTable."""
        table = self.query_one(DataTable)
        val_stat = self.tui_state.value_statuses[value_index]
        reps_done = val_stat.reps_done
        # reps_total = val_stat.reps_total
        timings = val_stat.timings

        progress_bar = self.progress_bars[value_index]
        progress_bar.update(reps_done)

        # Conditional coloring
        match val_stat.status:
            case Status.FAILED:
                colour = "red"
            case Status.RUNNING | Status.PENDING:
                colour = "yellow"
            case Status.COMPLETED:
                colour = "green"

        progress_bar.complete_style = colour
        progress_bar.finished_style = colour

        if timings:
          mean_str = self._format_float(statistics.mean(timings))
          median_str = self._format_float(statistics.median(timings))
          min_str = self._format_float(min(timings))
          max_str = self._format_float(max(timings))
        else:
          mean_str = "n/a"
          median_str = "n/a"
          min_str = "n/a"
          max_str = "n/a"

        for col, val in enumerate([val_stat.val, progress_bar, reps_done,
                                  mean_str, median_str, min_str, max_str]):
          table.update_cell_at(Coordinate(value_index, col), val)


def tui_main(config: Config) -> defaultdict[str, MutableSequence[Optional[float]]]:
    """
    Sets up and runs the interactive TUI using Textual.
    """
    app = TuiApp(config)
    return cast(defaultdict[str, MutableSequence[Optional[float]]], app.run())
