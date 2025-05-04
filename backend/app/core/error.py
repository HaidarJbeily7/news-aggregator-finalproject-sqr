from fastapi import HTTPException
from fastapi import status
from firebase_admin import auth


def handle_auth_error(error: Exception) -> None:
    """Handle authentication errors and raise appropriate HTTP exceptions."""
    error_messages = {
        auth.ExpiredIdTokenError: "Expired authentication token",
        auth.InvalidIdTokenError: "Invalid authentication token",
    }

    error_message = error_messages.get(
        type(error),
        f"Authentication error: {str(error)}")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=error_message,
    )
