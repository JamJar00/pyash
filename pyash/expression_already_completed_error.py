class ExpressionAlreadyCompletedError(Exception):
    """Exception raised when expression has already been evaluated and so cannot be run again."""

    def __init__(self, message):
        self.message = message
