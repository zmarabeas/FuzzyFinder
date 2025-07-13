from __future__ import annotations

"""Celery task definitions for the backend."""

from pathlib import Path
from typing import Dict, List

import os

from backend.celery_app import celery_app
from backend.utils.youtube_downloader import download_youtube_video
from backend.utils.video_processor import extract_frames, find_animal_segments
from backend.server import DETECTORS  # reuse factory

@celery_app.task(name="tasks.process_youtube")
def process_youtube(url: str, detector_name: str = "yolo") -> Dict[str, object]:
    """Download a YouTube video, run detection, and return results.

    Parameters
    ----------
    url : str
        YouTube URL to download.
    detector_name : str, optional
        Name of detector as defined in ``backend.server.DETECTORS`` (default ``"yolo"``).
    """
    # 1. Download video
    video_path: Path = download_youtube_video(url)

    try:
        # 2. Load detector
        detector_factory = DETECTORS.get(detector_name, DETECTORS["yolo"])
        detector = detector_factory()
        detector.load()

        # 3. Extract frames
        video_data = extract_frames(str(video_path))

        frame_results: List[Dict[str, object]] = []
        for i, frame in enumerate(video_data["frames"]):
            result = detector.detect(frame)
            result["frame_number"] = i
            result["timestamp"] = i / video_data["fps"]
            frame_results.append(result)

        segments = find_animal_segments(frame_results, video_data["fps"])

        return {
            "metadata": {
                "fps": video_data["fps"],
                "frame_count": video_data["frame_count"],
                "duration": video_data["duration"],
                "detector": detector.name,
            },
            "frames": frame_results,
            "animal_segments": segments,
        }
    finally:
        if os.path.exists(video_path):
            os.unlink(video_path)