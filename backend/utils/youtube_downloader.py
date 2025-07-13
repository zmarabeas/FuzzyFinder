import re
import tempfile
import os
from pathlib import Path
from pytube import YouTube  # type: ignore

from .exceptions import InvalidYouTubeURLError, YouTubeDownloadError

_YOUTUBE_REGEX = re.compile(r"^(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+$")

def is_valid_youtube_url(url: str) -> bool:
    """Simple regex based validation for YouTube URLs."""
    return bool(_YOUTUBE_REGEX.match(url))


def download_youtube_video(url: str) -> Path:
    """Download a YouTube video and return the path to the temporary MP4 file.

    This is a blocking call and should be executed in a background thread or
    separate worker in production.
    """
    if not is_valid_youtube_url(url):
        raise InvalidYouTubeURLError(f"Invalid YouTube URL: {url}")

    try:
        yt = YouTube(url)
        stream = yt.streams.filter(progressive=True, file_extension="mp4").order_by('resolution').desc().first()
        if stream is None:
            raise YouTubeDownloadError("Could not find suitable MP4 stream")

        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        tmp_path = Path(tmp_file.name)
        tmp_file.close()
        stream.download(output_path=str(tmp_path.parent), filename=tmp_path.name)
        return tmp_path
    except Exception as exc:
        # Clean up file if it was created
        if 'tmp_path' in locals() and tmp_path.exists():
            os.unlink(tmp_path)
        raise YouTubeDownloadError(str(exc)) from exc