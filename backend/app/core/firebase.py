from typing import Any, Optional
from firebase_admin import auth, credentials
from app.core.config import settings


def create_test_credentials() -> Any:
    """Create mock credentials for testing environment."""
    from unittest.mock import MagicMock
    cred = MagicMock()
    auth.verify_id_token = MagicMock(
        return_value={"uid": "test-user-id"}
    )
    return cred


def create_production_credentials() -> credentials.Certificate:
    """Create production credentials for Firebase."""
    return credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)


def initialize_firebase() -> Optional[Any]:
    """Initialize Firebase Admin SDK based on environment."""
    try:
        return (
            create_test_credentials()
            if settings.TESTING
            else create_production_credentials()
        )
    except Exception as e:
        print(f"Firebase initialization error: {str(e)}")
        return None
