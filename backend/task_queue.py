from __future__ import annotations

"""Very lightweight in-memory task queue used for unit tests and dev.

This queue is *not* intended for production; Use Celery with Redis instead.
"""

from collections import deque
import time
from threading import Thread
from typing import Any, Callable, Deque, Dict

Task = Callable[[], Any]

_queue: Deque[Task] = deque()
_job_counter: int = 0
_job_status: Dict[int, str] = {}


def enqueue(task: Task) -> int:
    """Enqueue *task* and return a monotonically increasing job id."""
    global _job_counter
    _job_counter += 1
    job_id: int = _job_counter
    _job_status[job_id] = "queued"

    def wrapper() -> None:
        _job_status[job_id] = "running"
        try:
            task()
            _job_status[job_id] = "completed"
        except Exception:  # pragma: no cover
            _job_status[job_id] = "failed"
            raise

    _queue.append(wrapper)
    return job_id


def get_status(job_id: int) -> str:
    """Return status string for *job_id* or ``"unknown"`` if id is invalid."""
    return _job_status.get(job_id, "unknown")


def _worker() -> None:
    """Background thread that processes the queue synchronously."""
    while True:
        if _queue:
            job: Task = _queue.popleft()
            try:
                job()
            except Exception as exc:  # pragma: no cover
                print(f"[TaskQueue] Job error: {exc}")
        else:
            time.sleep(0.1)


def start_background_worker() -> None:
    """Start daemon worker thread if not already running."""
    thread = Thread(target=_worker, daemon=True)
    thread.start()