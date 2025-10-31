"""This module contains the TuiState class."""

from collections import defaultdict
from collections.abc import MutableMapping, MutableSequence
import queue
from dataclasses import dataclass
from typing import Any


from ..config import Config
from ..utils import Status


@dataclass
class ValueStatus:
    val: Any
    status: Status
    reps_done: int
    reps_total: int
    timings: MutableSequence[float]
    has_failed_reps: bool


class TuiState:
    """
    Manages the state of the TUI application.
    """

    def __init__(self, config: Config):
        self.config = config
        self.job_id_to_value_index: MutableMapping[int, int] = {}
        self.value_statuses: MutableSequence[ValueStatus] = []
        self.job_id_counter = 0
        self.status_queue: queue.Queue = queue.Queue()
        self.job_results_by_val: defaultdict[str, MutableSequence] = defaultdict(list)
        self.total_jobs = 0
        self.jobs_completed = 0

        self.keep_running = True

    def setup_jobs(self) -> None:
        """
        Sets up job data structures and initial TUI state.
        """
        for i, val in enumerate(self.config.values):
            self.value_statuses.append(
                ValueStatus(
                    val=val,
                    status=Status.PENDING,
                    reps_done=0,
                    reps_total=self.config.repetitions,
                    timings=[],
                    has_failed_reps=False,
                )
            )
            for _ in range(self.config.repetitions):
                self.job_id_to_value_index[self.job_id_counter] = i
                self.job_id_counter += 1
        self.total_jobs = self.job_id_counter
