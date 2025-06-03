class RateLimitError(Exception):
    """Exception raised when rate limiting thresholds are exceeded.

    This exception is used to handle cases when a user or system has made too many
    requests within a specific time period and needs to be rate limited.
    """
    def __init__(self, message):
        super().__init__(message)


class UnsupportedEntryError(Exception):
    """Exception raised when an unsupported data entry is encountered.

    This exception is used when the system encounters data entries or formats
    that are not supported or cannot be processed by the application.
    """
    def __init__(self, message):
        super().__init__(message)
