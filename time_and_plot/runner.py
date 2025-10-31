"""This module contains the core logic for running jobs in parallel."""

import shlex
import subprocess
import time
from typing import Any, Callable

from .tui.messages import JobData, JobUpdate
from .tui.state import Status


def run_single_command(
    job_id: int,
    command_template: str,
    value: str,
    post_message: Callable[[JobUpdate], Any],
) -> None:
    """
    Runs a single instance of the command and posts its status via a callback.
    This function is designed to be executed in a separate thread or worker.
    """
    try:
        start_time = time.perf_counter()

        full_command = command_template.format(value)
        command_args = shlex.split(full_command)

        subprocess.run(
            command_args,
            check=True,
            capture_output=True,
            text=True,
        )

        end_time = time.perf_counter()
        duration = end_time - start_time

        post_message(JobUpdate(JobData(id=job_id, status=Status.COMPLETED, duration=duration)))

    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip().split("\n")[-1]
        post_message(JobUpdate(JobData(id=job_id, status=Status.FAILED, error=error_msg)))
    except FileNotFoundError:
        post_message(JobUpdate(JobData(id=job_id, status=Status.FAILED, error="Command not found")))
    except Exception as e:
        post_message(JobUpdate(JobData(id=job_id, status=Status.FAILED, error=str(e))))

