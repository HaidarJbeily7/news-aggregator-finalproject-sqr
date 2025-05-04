import pytest
from src.utils import api


class DummyResponse:
    def __init__(self, status_code, json_data=None, text=""):
        self.status_code = status_code
        self._json = json_data or {}
        self.text = text

    def json(self):
        return self._json


class DummyClient:
    def __init__(
        self,
        expected_method,
        expected_url,
        expected_headers=None,
        expected_params=None,
        response=None,
    ):
        self.expected_method = expected_method
        self.expected_url = expected_url
        self.expected_headers = expected_headers
        self.expected_params = expected_params
        self._response = response

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def get(self, url, headers=None, params=None):
        assert self.expected_method == "get"
        assert url == self.expected_url

        if self.expected_headers is not None:
            assert headers == self.expected_headers

        if self.expected_params is not None:
            assert params == self.expected_params

        return self._response

    async def post(self, url, headers=None, json=None):
        assert self.expected_method == "post"
        assert url == self.expected_url

        if self.expected_headers is not None:
            assert headers == self.expected_headers

        return self._response

    async def delete(self, url, headers=None):
        assert self.expected_method == "delete"
        assert url == self.expected_url

        if self.expected_headers is not None:
            assert headers == self.expected_headers

        return self._response


@pytest.fixture(autouse=True)
def set_base_url(monkeypatch):
    """Use a fixed base URL for all API tests."""
    monkeypatch.setattr(
        api, "API_BASE_URL", "https://test.example.com"
    )
    yield


@pytest.mark.asyncio
async def test_get_headlines_no_token(monkeypatch):
    monkeypatch.setattr(api, "get_auth_token", lambda: None)

    with pytest.raises(Exception) as exc:
        await api.get_headlines()

    assert "Authentication required" in str(exc.value)


@pytest.mark.asyncio
async def test_get_headlines_success(monkeypatch):
    monkeypatch.setattr(api, "get_auth_token", lambda: "tok123")

    fake_data = [{"title": "A"}]
    dummy = DummyClient(
        expected_method="get",
        expected_url=(
            "https://test.example.com"
            "/api/v1/news/headlines"
        ),
        expected_headers={"Authorization": "Bearer tok123"},
        expected_params={"country": "us", "page_size": 10},
        response=DummyResponse(200, json_data=fake_data),
    )
    monkeypatch.setattr(api.httpx, "AsyncClient", lambda: dummy)

    result = await api.get_headlines()
    assert result == fake_data


@pytest.mark.asyncio
async def test_get_headlines_with_category(monkeypatch):
    monkeypatch.setattr(api, "get_auth_token", lambda: "tok456")

    fake_data = [{"title": "B"}]
    dummy = DummyClient(
        expected_method="get",
        expected_url=(
            "https://test.example.com"
            "/api/v1/news/headlines"
        ),
        expected_headers={"Authorization": "Bearer tok456"},
        expected_params={
            "country": "us",
            "page_size": 5,
            "category": "sports",
        },
        response=DummyResponse(200, json_data=fake_data),
    )
    monkeypatch.setattr(api.httpx, "AsyncClient", lambda: dummy)

    result = await api.get_headlines(
        category="sports", page_size=5
    )
    assert result == fake_data


@pytest.mark.asyncio
async def test_search_news_error_status(monkeypatch):
    monkeypatch.setattr(api, "get_auth_token", lambda: "t")

    dummy = DummyClient(
        expected_method="get",
        expected_url=(
            "https://test.example.com"
            "/api/v1/news/search"
        ),
        expected_headers={"Authorization": "Bearer t"},
        expected_params={"language": "en", "page_size": 10, "page": 1},
        response=DummyResponse(500, text="oops"),
    )
    monkeypatch.setattr(api.httpx, "AsyncClient", lambda: dummy)

    with pytest.raises(Exception) as exc:
        await api.search_news()

    assert "Failed to search news" in str(exc.value)


@pytest.mark.asyncio
async def test_get_bookmarks_and_delete(monkeypatch):
    monkeypatch.setattr(api, "get_auth_token", lambda: "tok")

    bm_data = [{"id": 1}]
    dummy_get = DummyClient(
        expected_method="get",
        expected_url=(
            "https://test.example.com"
            "/api/v1/bookmarks"
        ),
        expected_headers={"Authorization": "Bearer tok"},
        response=DummyResponse(200, json_data=bm_data),
    )
    monkeypatch.setattr(api.httpx, "AsyncClient", lambda: dummy_get)

    result = await api.get_bookmarks()
    assert result == bm_data

    dummy_del = DummyClient(
        expected_method="delete",
        expected_url=(
            "https://test.example.com"
            "/api/v1/bookmarks/42"
        ),
        expected_headers={"Authorization": "Bearer tok"},
        response=DummyResponse(204),
    )
    monkeypatch.setattr(api.httpx, "AsyncClient", lambda: dummy_del)

    await api.delete_bookmark(42)


@pytest.mark.asyncio
async def test_create_bookmark_and_delete_error(monkeypatch):
    monkeypatch.setattr(api, "get_auth_token", lambda: "abc")

    new_bm = {"url": "x"}
    created = {"id": 99, **new_bm}
    dummy_post = DummyClient(
        expected_method="post",
        expected_url=(
            "https://test.example.com"
            "/api/v1/bookmarks"
        ),
        expected_headers={"Authorization": "Bearer abc"},
        response=DummyResponse(201, json_data=created),
    )
    monkeypatch.setattr(api.httpx, "AsyncClient", lambda: dummy_post)

    result = await api.create_bookmark(new_bm)
    assert result == created

    dummy_bad_del = DummyClient(
        expected_method="delete",
        expected_url=(
            "https://test.example.com"
            "/api/v1/bookmarks/7"
        ),
        expected_headers={"Authorization": "Bearer abc"},
        response=DummyResponse(400, text="bad"),
    )
    monkeypatch.setattr(
        api.httpx,
        "AsyncClient",
        lambda: dummy_bad_del
    )

    with pytest.raises(Exception) as exc:
        await api.delete_bookmark(7)

    assert "Failed to delete bookmark" in str(exc.value)
