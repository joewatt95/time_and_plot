"""This module contains the console logging implementation."""

from collections.abc import MutableSequence, Sequence
import logging
from collections import defaultdict
from typing import Optional
import concurrent.futures

from .config import Config
from .runner import run_single_command
from .utils import JobInfo, JobData, Status


def console_main(
    config: Config, job_id_to_info: MutableSequence[JobInfo], logger: logging.Logger
) -> defaultdict[str, MutableSequence[Optional[float]]]:
    """
    Runs the experiment with simple print statements for progress.
    This is a fallback for when the TUI is disabled or unsupported.
    """
    logger.info("TUI disabled. Using simple console logging.")
    logger.info(
        f"Submitting {len(job_id_to_info)} jobs to a pool of {config.parallel_workers or 'max'} workers..."
    )

    job_results_by_val: defaultdict[str, MutableSequence[Optional[float]]] = defaultdict(list)
    jobs_completed = 0
    # total_jobs = len(job_id_to_info)

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=config.parallel_workers
    ) as executor:
        futures = {
            executor.submit(
                run_single_command,
                job.id,
                config.command,
                job.val,
                lambda update: handle_update(
                    update.update, job_id_to_info, job_results_by_val, logger
                ),
            ): job
            for job in job_id_to_info
        }

        try:
            for future in concurrent.futures.as_completed(futures):
                jobs_completed += 1
                # We don't need to do anything with the result here, as the handler does it
                pass
        except KeyboardInterrupt:
            logger.info("Caught interrupt! Shutting down...")
            # The executor will be cleaned up by the 'with' statement
            return defaultdict(list)

    return job_results_by_val


def handle_update(
    update: JobData,
    job_id_to_info: Sequence[JobInfo],
    job_results_by_val: defaultdict[str, MutableSequence[Optional[float]]],
    logger: logging.Logger,
) -> None:
    """
    Processes a single job update and logs it to the console.
    """
    job_info = job_id_to_info[update.id]
    val, rep = job_info.val, job_info.rep
    total_done = sum(len(v) for v in job_results_by_val.values())

    match update.status:
        case Status.COMPLETED:
            duration = update.duration
            job_results_by_val[val].append(duration)
            logger.info(
                f"  [Job OK] val={val} (rep {rep}): {duration:.4f}s ({total_done}/{len(job_id_to_info)} done)"
            )
        case Status.FAILED:
            error = update.error
            job_results_by_val[val].append(None)  # Mark as failed
            logger.error(
                f"  [Job FAILED] val={val} (rep {rep}): {error} ({total_done}/{len(job_id_to_info)} done)"
            )