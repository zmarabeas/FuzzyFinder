import pytest  # type: ignore

from backend.utils.youtube_downloader import (
    is_valid_youtube_url,
    download_youtube_video,
    InvalidYouTubeURLError,
    YouTubeDownloadError,
)

from unittest import mock


def test_is_valid_youtube_url():
    assert is_valid_youtube_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    assert is_valid_youtube_url("https://youtu.be/dQw4w9WgXcQ")
    assert not is_valid_youtube_url("https://example.com/video.mp4")


@mock.patch("backend.utils.youtube_downloader.YouTube")
@mock.patch("backend.utils.youtube_downloader.Path")
@mock.patch("backend.utils.youtube_downloader.tempfile.NamedTemporaryFile")
def test_download_youtube_video_success(mock_tmp, mock_path, mock_yt):
    mock_stream = mock.Mock()
    mock_stream.download.return_value = None
    mock_yt.return_value.streams.filter.return_value.order_by.return_value.desc.return_value.first.return_value = mock_stream

    # Mock tempfile
    temp_instance = mock.MagicMock()
    temp_instance.name = "/tmp/test.mp4"
    mock_tmp.return_value = temp_instance

    # Mock Path to avoid filesystem operations
    mock_path.return_value.exists.return_value = True

    path = download_youtube_video("https://youtu.be/video")
    assert isinstance(path, mock.Mock)


def test_download_invalid_url():
    with pytest.raises(InvalidYouTubeURLError):
        download_youtube_video("https://invalidsite.com/video")


@mock.patch("backend.utils.youtube_downloader.YouTube", side_effect=Exception("network error"))
def test_download_error(mock_yt):
    with pytest.raises(YouTubeDownloadError):
        download_youtube_video("https://youtu.be/video")