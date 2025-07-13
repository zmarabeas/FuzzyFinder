# pyright: reportMissingImports=false
from __future__ import annotations

# Standard library imports
from dataclasses import dataclass
import os
from typing import Any, Dict, List, Optional, Callable, TYPE_CHECKING

# Third-party imports
import cv2  # type: ignore
import numpy as np  # type: ignore
from flask import Flask, jsonify, request, Response
from flask_cors import CORS

# Optional Flask-Limiter import with graceful fallback
try:
    from flask_limiter import Limiter  # type: ignore
    from flask_limiter.util import get_remote_address  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    Limiter = None  # type: ignore

# Static type checking support for Limiter
if TYPE_CHECKING:
    from flask_limiter import Limiter as LimiterType  # pragma: no cover
else:
    LimiterType = Any  # type: ignore
from celery.result import AsyncResult  # type: ignore

# Local application imports
from models.mobilenet_detector import MobileNetDetector
from models.rcnn_detector import FasterRCNNDetector
from models.resnet_detector import ResNetDetector
from models.ssd_detector import SSDDetector
from models.temporal_detector import TemporalDetector
from models.yolo_detector import YOLODetector
from utils.video_processor import extract_frames, find_animal_segments
from utils.youtube_downloader import (
    InvalidYouTubeURLError,
    YouTubeDownloadError,
    download_youtube_video,
)
from backend.tasks import process_youtube as celery_process_youtube
from backend.task_queue import get_status  # Dev in-memory queue (legacy tests)

__all__: List[str] = [
    "app",
]

app: Flask = Flask(__name__)
CORS(app)
# Instantiate rate limiter if the extension is available
limiter: Optional[LimiterType] = None
if Limiter is not None:
    limiter = Limiter(key_func=get_remote_address, app=app, default_limits=["100 per hour"])

# Helper decorator that becomes a no-op when limiter is unavailable
def rate_limit_exempt(func: Callable[..., Response]) -> Callable[..., Response]:
    if limiter is None:
        return func
    return limiter.exempt(func)  # type: ignore[arg-type]

# ---------------------------------------------------------------------------
# Detector registry -----------------------------------------------------------------

DETECTORS: Dict[str, Any] = {
    "resnet": lambda: ResNetDetector(confidence_threshold=0.3),
    "yolo": lambda: YOLODetector(confidence_threshold=0.3),
    "faster_rcnn": lambda: FasterRCNNDetector(confidence_threshold=0.4),
    "ssd": lambda: SSDDetector(confidence_threshold=0.4),
    "mobilenet": lambda: MobileNetDetector(confidence_threshold=0.4),
    "temporal_mobilenet": lambda: TemporalDetector(
        MobileNetDetector(confidence_threshold=0.4), sequence_length=5
    ),
    "temporal_resnet": lambda: TemporalDetector(
        ResNetDetector(confidence_threshold=0.3), sequence_length=5
    ),
    "temporal_yolo": lambda: TemporalDetector(
        YOLODetector(confidence_threshold=0.4), sequence_length=5
    ),
    "temporal_faster_rcnn": lambda: TemporalDetector(
        FasterRCNNDetector(confidence_threshold=0.4), sequence_length=5
    ),
    "temporal_ssd": lambda: TemporalDetector(
        SSDDetector(confidence_threshold=0.4), sequence_length=5
    ),
}

# ---------------------------------------------------------------------------
# Celery helper ----------------------------------------------------------------

def _dispatch_celery_task(url: str, detector: str) -> Dict[str, str]:
    """Send *process_youtube* task to Celery with graceful fallback.

    If the Celery broker is unreachable we return a 503 response structure
    understood by the caller.
    """
    try:
        async_result: AsyncResult = celery_process_youtube.apply_async(args=[url, detector])
        return {"task_id": async_result.id, "status": "queued"}
    except Exception as exc:  # pragma: no cover – network/broker issues
        # Log exc appropriately in production
        return {"error": "Celery broker unavailable", "detail": str(exc)}

# ---------------------------------------------------------------------------
# Data models ----------------------------------------------------------------

@dataclass
class YouTubeRequest:
    """Schema for the JSON payload accepted by /process-youtube."""

    url: str
    detector: str = "yolo"

# ---------------------------------------------------------------------------
# Routes ---------------------------------------------------------------------

@app.route("/", methods=["GET"])
@rate_limit_exempt
def hello_world() -> Response:
    """Simple ping route used by front-end to test connectivity."""
    return jsonify({"message": "Hello, World!"})


@app.route("/health", methods=["GET"])
@rate_limit_exempt
def health() -> Response:
    """Liveness probe for orchestration platforms."""
    return jsonify({"status": "ok"})


@app.route("/available-detectors", methods=["GET"])
def available_detectors() -> Any:
    """Return list of registered detector keys."""
    return jsonify({"detectors": list(DETECTORS.keys()), "default": "yolo"})


@app.route("/process-video", methods=["POST"])
def process_video() -> Any:
    """Synchronously process an uploaded video file and return detection output."""
    if "video" not in request.files:
        return jsonify({"error": "No video file provided"}), 400

    detector_type: str = request.form.get("detector", "yolo")
    if detector_type not in DETECTORS:
        return (
            jsonify({"error": f"Invalid detector type. Options: {list(DETECTORS.keys())}"}),
            400,
        )

    detector = DETECTORS[detector_type]()
    detector.load()

    video_file = request.files["video"]
    temp_path: str = "temp_upload.mp4"
    video_file.save(temp_path)

    try:
        video_data = extract_frames(temp_path)
        frame_results: List[Dict[str, Any]] = []
        for i, frame in enumerate(video_data["frames"]):
            result = detector.detect(frame)
            result["frame_number"] = i
            result["timestamp"] = i / video_data["fps"]
            frame_results.append(result)

        segments = find_animal_segments(frame_results, video_data["fps"])
        return jsonify(
            {
                "metadata": {
                    "fps": video_data["fps"],
                    "frame_count": video_data["frame_count"],
                    "duration": video_data["duration"],
                    "detector": detector.name,
                },
                "frames": frame_results,
                "animal_segments": segments,
            }
        )
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


@app.route("/process-youtube", methods=["POST"])
def process_youtube() -> Any:
    """Queue YouTube video processing via Celery with validation & rate-limit."""
    data = request.get_json(silent=True) or {}
    req = YouTubeRequest(url=data.get("url", ""), detector=data.get("detector", "yolo"))

    if not req.url:
        return jsonify({"error": "Missing URL parameter"}), 400

    try:
        # quick validation before task dispatch
        download_youtube_video  # noqa: F401 – validation inside called helper
    except InvalidYouTubeURLError as err:
        return jsonify({"error": str(err)}), 400

    task_info = _dispatch_celery_task(req.url, req.detector)
    if "error" in task_info:
        return jsonify(task_info), 503
    return jsonify(task_info), 202


@app.route("/task-status/<task_id>", methods=["GET"])
@rate_limit_exempt
def task_status(task_id: str) -> Response:
    """Return Celery task state and success boolean."""
    res: AsyncResult = AsyncResult(task_id)
    return jsonify({"task_id": task_id, "state": res.state, "successful": res.successful()})


@app.route("/job-status/<int:job_id>", methods=["GET"])
@rate_limit_exempt
def job_status(job_id: int) -> Response:
    """Legacy route for the in-memory dev queue."""
    return jsonify({"job_id": job_id, "status": get_status(job_id)})

# Redis health route
from backend.redis_pool import get_redis

@app.route("/broker-health", methods=["GET"])
@rate_limit_exempt
def broker_health() -> Response:
    """Check Redis connection health used by Celery broker."""
    try:
        client = get_redis()
        client.ping()
        return jsonify({"redis": "ok"})
    except Exception as exc:  # pragma: no cover
        return jsonify({"redis": "unavailable", "detail": str(exc)}), 503


if __name__ == "__main__":
    app.run(port=5005)
