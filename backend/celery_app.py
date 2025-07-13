from __future__ import annotations

"""Celery application instance.

Replace the in-memory queue with a Celery worker backed by Redis.
The broker URL can be configured via the *CELERY_BROKER_URL* environment
variable (defaults to ``redis://localhost:6379/0``).
"""

import os
from typing import Final

from celery import Celery  # type: ignore

BROKER_URL: Final[str] = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
BACKEND_URL: Final[str] = os.getenv("CELERY_RESULT_BACKEND", BROKER_URL)

celery_app: Celery = Celery("fuzzyfinder", broker=BROKER_URL, backend=BACKEND_URL)

# Optional Celery configuration
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
)