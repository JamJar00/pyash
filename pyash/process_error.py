class ProcessError(Exception):
    """Exception raised when a process exits with a non-zero exit code."""

    def __init__(self, message):
        self.message = message
