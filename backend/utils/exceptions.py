class YouTubeError(Exception):
    """Base class for YouTube related errors."""


class InvalidYouTubeURLError(YouTubeError):
    """Raised when provided URL is not a valid YouTube link."""


class YouTubeDownloadError(YouTubeError):
    """Raised when downloading a YouTube video fails."""