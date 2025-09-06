class SentinelError(Exception):
    """Base exception for all errors raised by the Sentinel SDK."""
    pass

class BudgetExceededError(SentinelError):
    """Raised when an API call is blocked because the budget has been exceeded."""
    pass