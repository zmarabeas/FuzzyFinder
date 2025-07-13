from __future__ import annotations

"""Utility functions responsible for validating and downloading YouTube videos.

The public API intentionally remains very small:
  * `is_valid_youtube_url`
  * `download_youtube_video`

Both are fully typed, raise domain-specific exceptions, and do not leak the
pytube dependency to callers.
"""

import os
import re
import tempfile
from pathlib import Path
from typing import Final

# Third-party import guarded to keep linter happy when not installed.
try:
    from pytube import YouTube  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    YouTube = None  # type: ignore

from backend.utils.exceptions import InvalidYouTubeURLError, YouTubeDownloadError

_YOUTUBE_REGEX: Final[re.Pattern[str]] = re.compile(
    r"^(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+$",
    flags=re.IGNORECASE,
)


def is_valid_youtube_url(url: str) -> bool:
    """Return *True* if *url* matches a basic YouTube URL pattern."""
    return bool(_YOUTUBE_REGEX.match(url))


def download_youtube_video(url: str) -> Path:
    """Download the YouTube *url* and return a path to a temporary MP4 file.

    Raises
    ------
    InvalidYouTubeURLError
        If the URL does not look like a YouTube URL.
    YouTubeDownloadError
        For any failure during download or missing dependencies.
    """
    if not is_valid_youtube_url(url):
        raise InvalidYouTubeURLError(f"Invalid YouTube URL: {url}")

    if YouTube is None:
        # Library not installed in environment.
        raise YouTubeDownloadError("pytube library not installed")

    try:
        yt = YouTube(url)
        stream = (
            yt.streams.filter(progressive=True, file_extension="mp4")
            .order_by("resolution")
            .desc()
            .first()
        )
        if stream is None:
            raise YouTubeDownloadError("No suitable MP4 stream found")

        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        tmp_path = Path(tmp_file.name)
        tmp_file.close()
        stream.download(output_path=str(tmp_path.parent), filename=tmp_path.name)
        return tmp_path
    except Exception as exc:  # pragma: no cover – external library complexity
        if "tmp_path" in locals() and isinstance(tmp_path, Path) and tmp_path.exists():
            os.unlink(tmp_path)
        raise YouTubeDownloadError(str(exc)) from exc