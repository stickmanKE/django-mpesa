class MpesaError(Exception):
    """Base exception for all M-Pesa errors."""
    pass


class MpesaAuthError(MpesaError):
    """Raised when OAuth token acquisition fails."""
    pass


class MpesaRequestError(MpesaError):
    """Raised when a Daraja API request fails."""
    def __init__(self, message, response=None):
        super().__init__(message)
        self.response = response


class MpesaValidationError(MpesaError):
    """Raised for invalid input (phone number, amount, etc.)."""
    pass
