from __future__ import annotations

"""Celery application instance.

Replace the in-memory queue with a Celery worker backed by Redis.
The broker URL can be configured via the *CELERY_BROKER_URL* environment
variable (defaults to ``redis://localhost:6379/0``).
"""

try:
    from celery import Celery  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    Celery = None  # type: ignore

if Celery is None:
    raise RuntimeError("Celery is required but not installed. Install with `pip install celery redis`. ")

import os
from typing import Final

BROKER_URL: Final[str] = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
BACKEND_URL: Final[str] = os.getenv("CELERY_RESULT_BACKEND", BROKER_URL)

celery_app: Celery = Celery(
    "fuzzyfinder",
    broker=BROKER_URL,
    backend=BACKEND_URL,
    broker_connection_retry=True,
    broker_connection_max_retries=5,
)

# Kombu/Redis connection pool limit (10 connections)
celery_app.conf.broker_transport_options = {"max_connections": 10}

# Global retry settings for all tasks can be set via task annotations if needed.

# Optional Celery configuration
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
)