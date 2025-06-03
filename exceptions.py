class RateLimitError(Exception):
    """Exception raised when rate limiting thresholds are exceeded.

    This exception is used to handle cases when a user or system has made too many
    requests within a specific time period and needs to be rate limited.
    """
    def __init__(self, message):
        super().__init__(message)