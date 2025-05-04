import pytest
import streamlit as st
import httpx
from src.utils import auth


# --- Helpers for async fetch_user_info tests ---

class DummyResponse:
    def __init__(self, json_data):
        self._json = json_data

    def json(self):
        return self._json

    def raise_for_status(self):
        # simulate successful status
        return None


class DummyClient:
    def __init__(self, response=None, exc=None):
        self._response = response
        self._exc = exc

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def get(self, url, headers=None):
        if self._exc:
            raise self._exc
        return self._response


# --- Fixtures ---

@pytest.fixture(autouse=True)
def mock_session_state(monkeypatch):
    """Mock Streamlit's session state for testing."""
    session_state = {}
    monkeypatch.setattr(st, "session_state", session_state)
    return session_state


# --- sync tests ---

def test_init_auth_state_sets_default():
    # session_state starts empty
    auth.init_auth_state()
    assert "auth_state" in st.session_state
    assert st.session_state["auth_state"] == {
        "is_authenticated": False,
        "user": None,
        "token": None
    }


def test_set_and_get_auth_state():
    user = {"id": 42, "name": "Alice"}
    auth.set_auth_state(user, "tok123")
    # stored in session_state
    assert st.session_state["auth_state"]["is_authenticated"] is True
    assert st.session_state["auth_state"]["user"] == user
    assert st.session_state["auth_state"]["token"] == "tok123"
    # get_auth_state returns same dict
    assert auth.get_auth_state() == st.session_state["auth_state"]


def test_clear_auth_state():
    # put some data in
    st.session_state["auth_state"] = {
        "is_authenticated": True,
        "user": {"foo": "bar"},
        "token": "xyz"
    }
    auth.clear_auth_state()
    assert st.session_state["auth_state"] == {
        "is_authenticated": False,
        "user": None,
        "token": None
    }


def test_is_authenticated_and_getters():
    st.session_state["auth_state"] = {
        "is_authenticated": True,
        "user": {"u": 1},
        "token": "t"
    }
    assert auth.is_authenticated() is True
    assert auth.get_current_user() == {"u": 1}
    assert auth.get_auth_token() == "t"


def test_require_auth_when_not_authenticated(monkeypatch):
    # ensure state is unauthenticated
    st.session_state["auth_state"] = {
        "is_authenticated": False,
        "user": None,
        "token": None
    }

    errors = []
    # stub out st.error and st.stop
    monkeypatch.setattr(st, "error", lambda msg: errors.append(msg))

    class StopExc(Exception):
        pass
    monkeypatch.setattr(st, "stop", lambda: (_ for _ in ()).throw(StopExc()))

    with pytest.raises(StopExc):
        auth.require_auth()

    assert errors == ["Please log in to access this page."]


# --- async tests for fetch_user_info ---

@pytest.mark.asyncio
async def test_fetch_user_info_success(monkeypatch):
    dummy_resp = DummyResponse({"user_id": 7})
    dummy_client = DummyClient(response=dummy_resp)

    monkeypatch.setattr(httpx, "AsyncClient", lambda: dummy_client)
    result = await auth.fetch_user_info("mytoken")
    assert result == {"user_id": 7}


@pytest.mark.asyncio
async def test_fetch_user_info_request_error(monkeypatch):
    dummy_client = DummyClient(exc=httpx.RequestError("network down"))
    monkeypatch.setattr(httpx, "AsyncClient", lambda: dummy_client)

    with pytest.raises(Exception) as exc:
        await auth.fetch_user_info("mytoken")
    assert "Failed to fetch user info" in str(exc.value)
