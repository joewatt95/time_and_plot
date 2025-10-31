"""This module contains the message classes for the TUI."""

from textual.message import Message

from ..utils import JobData


class JobUpdate(Message):
    """A message to update the TUI with job status."""

    def __init__(self, update: JobData) -> None:
        self.update = update
        super().__init__()
