import pytest
import streamlit as st
from src.utils import firebase


class DummyTab:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class DummyColumns:
    def __init__(self, *args):
        self.cols = [DummyColumn() for _ in args]

    def __iter__(self):
        return iter(self.cols)

    def __getitem__(self, idx):
        return self.cols[idx]


class DummyColumn:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


@pytest.fixture(autouse=True)
def mock_session_state(monkeypatch):
    """Mock Streamlit's session state for testing."""
    session_state = {}
    monkeypatch.setattr(st, "session_state", session_state)
    return session_state


def test_get_firebase_config(monkeypatch):
    monkeypatch.setattr(firebase, "FIREBASE_API_KEY", "key123")
    monkeypatch.setattr(firebase, "FIREBASE_AUTH_DOMAIN", "dom")
    monkeypatch.setattr(firebase, "FIREBASE_PROJECT_ID", "proj")
    monkeypatch.setattr(firebase, "FIREBASE_STORAGE_BUCKET", "buck")
    monkeypatch.setattr(
        firebase, "FIREBASE_MESSAGING_SENDER_ID", "msg"
    )
    monkeypatch.setattr(firebase, "FIREBASE_APP_ID", "app")

    cfg = firebase.get_firebase_config()
    assert cfg == {
        "apiKey": "key123",
        "authDomain": "dom",
        "projectId": "proj",
        "storageBucket": "buck",
        "messagingSenderId": "msg",
        "appId": "app",
    }


@pytest.mark.parametrize(
    "vals, expected",
    [
        (
            {
                "API_KEY": "a",
                "AUTH_DOMAIN": "b",
                "PROJECT_ID": "c",
                "STORAGE_BUCKET": "d",
                "MESSAGING_SENDER_ID": "e",
                "APP_ID": "f",
            },
            True,
        ),
        (
            {
                "API_KEY": "",
                "AUTH_DOMAIN": "b",
                "PROJECT_ID": "c",
                "STORAGE_BUCKET": "d",
                "MESSAGING_SENDER_ID": "e",
                "APP_ID": "f",
            },
            False,
        ),
    ],
)
def test_check_firebase_config(monkeypatch, vals, expected):
    monkeypatch.setattr(firebase, "FIREBASE_API_KEY", vals["API_KEY"])
    monkeypatch.setattr(
        firebase, "FIREBASE_AUTH_DOMAIN", vals["AUTH_DOMAIN"]
    )
    monkeypatch.setattr(
        firebase, "FIREBASE_PROJECT_ID", vals["PROJECT_ID"]
    )
    monkeypatch.setattr(
        firebase, "FIREBASE_STORAGE_BUCKET", vals["STORAGE_BUCKET"]
    )
    monkeypatch.setattr(
        firebase,
        "FIREBASE_MESSAGING_SENDER_ID",
        vals["MESSAGING_SENDER_ID"],
    )
    monkeypatch.setattr(firebase, "FIREBASE_APP_ID", vals["APP_ID"])

    assert firebase.check_firebase_config() is expected


def test_firebase_login_ui_config_incomplete(monkeypatch):
    monkeypatch.setattr(firebase, "check_firebase_config", lambda: False)

    errors = []
    monkeypatch.setattr(st, "error", lambda msg: errors.append(msg))

    result = firebase.firebase_login_ui()
    assert result is None
    assert errors == [
        "Firebase configuration is incomplete. "
        "Please check your .env file."
    ]


def test_firebase_login_ui_no_click(monkeypatch):
    monkeypatch.setattr(firebase, "check_firebase_config", lambda: True)
    monkeypatch.setattr(st, "tabs", lambda labels: (DummyTab(), DummyTab()))
    monkeypatch.setattr(st, "subheader", lambda txt: None)
    monkeypatch.setattr(st, "text_input", lambda *a, **k: "")
    monkeypatch.setattr(
        st, "columns", lambda *a: [DummyColumn(), DummyColumn()]
    )
    monkeypatch.setattr(st, "button", lambda *a, **k: False)
    monkeypatch.setattr(st, "error", lambda msg: None)
    monkeypatch.setattr(st, "success", lambda msg: None)

    result = firebase.firebase_login_ui()
    assert result is None


def test_firebase_logout(monkeypatch):
    called = {}

    def mock_clear_auth_state():
        called["cleared"] = True

    monkeypatch.setattr(
        "src.utils.firebase.clear_auth_state",
        mock_clear_auth_state
    )
    monkeypatch.setattr(st,
                        "success",
                        lambda msg: called.setdefault("success", msg)
                        )
    monkeypatch.setattr(st, "rerun", lambda: called.setdefault("rerun", True))

    firebase.firebase_logout()

    assert called["cleared"] is True
    assert called["success"] == "Logged out successfully!"
