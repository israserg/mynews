"""Black-box tests: they talk to a RUNNING mynews over HTTP (BASE_URL, default http://127.0.0.1:8000)."""
import os

import httpx
import pytest

BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:8000")


@pytest.fixture(scope="module")
def client():
    with httpx.Client(base_url=BASE_URL, timeout=30) as c:
        yield c


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_version_is_semver_like(client):
    r = client.get("/version")
    assert r.status_code == 200
    assert r.json()["version"].count(".") == 2


def test_news_shape(client):
    r = client.get("/api/news")
    assert r.status_code == 200
    items = r.json()
    assert 1 <= len(items) <= 10
    for it in items:
        assert it["title"] and it["link"].startswith("http")
        assert isinstance(it["topics"], list) and it["topics"]


def test_index_page(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "mynews" in r.text
