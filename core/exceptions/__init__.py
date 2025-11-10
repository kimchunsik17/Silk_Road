class ReservationConflictError(Exception):
    """Raised when a reservation conflicts with an existing one."""
    pass

class PaymentFailedError(Exception):
    """Raised when a payment transaction fails."""
    pass

class InsufficientPermissionsError(PermissionError):
    """Raised when a user does not have sufficient permissions to perform an action."""
    pass
