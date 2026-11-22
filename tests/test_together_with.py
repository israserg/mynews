"""Black-box tests for the "Together With" column (BASE_URL, default http://127.0.0.1:8000)."""
import os

import httpx
import pytest

BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:8000")


@pytest.fixture(scope="module")
def client():
    with httpx.Client(base_url=BASE_URL, timeout=30) as c:
        yield c


def test_news_items_have_together_with_key(client):
    items = client.get("/api/news").json()
    assert items
    for it in items:
        assert "together_with" in it
        tw = it["together_with"]
        if tw is not None:
            assert isinstance(tw, dict)
            assert isinstance(tw["logo"], str)
            assert isinstance(tw["link"], str)


def test_together_with_urls_are_http(client):
    for it in client.get("/api/news").json():
        tw = it["together_with"]
        if tw is None:
            continue
        for key in ("link", "logo"):
            assert tw[key] == "" or tw[key].startswith("http")


def test_index_has_together_with_header(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "Together With" in r.text
    assert r.text.index('"Link"') < r.text.index('"Together With"')


def test_index_builds_together_with_cell(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "together_with" in r.text
