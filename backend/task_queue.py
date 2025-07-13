from collections import deque
from threading import Thread
from typing import Callable, Any, Deque, Dict
import time

Task = Callable[[], Any]

_queue: Deque[Task] = deque()
_job_counter = 0
_job_status: Dict[int, str] = {}


def enqueue(task: Task) -> int:
    global _job_counter
    _job_counter += 1
    job_id = _job_counter
    _job_status[job_id] = 'queued'

    def wrapper():
        _job_status[job_id] = 'running'
        try:
            task()
            _job_status[job_id] = 'completed'
        except Exception:
            _job_status[job_id] = 'failed'
            raise

    _queue.append(wrapper)
    return job_id


def get_status(job_id: int) -> str:
    return _job_status.get(job_id, 'unknown')


def _worker() -> None:
    while True:
        if _queue:
            job = _queue.popleft()
            try:
                job()
            except Exception as exc:  # pragma: no cover
                # Log exception in real implementation
                print(f"[TaskQueue] Job error: {exc}")
        else:
            time.sleep(0.1)


def start_background_worker() -> None:
    """Start a daemon thread that processes the in-memory queue."""
    worker = Thread(target=_worker, daemon=True)
    worker.start()