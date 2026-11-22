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


def test_together_with_is_populated_for_some_item(client):
    items = client.get("/api/news").json()
    assert any(it["together_with"] and it["together_with"]["link"] for it in items)


def test_together_with_urls_are_http(client):
    items = client.get("/api/news").json()
    twl = [it["together_with"] for it in items if it["together_with"]]
    assert twl
    for tw in twl:
        assert tw["link"].startswith("http")
        assert tw["logo"] == "" or tw["logo"].startswith("http")


def test_index_has_together_with_header(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "Together With" in r.text
    assert r.text.index('"Link"') < r.text.index('"Together With"')


def test_index_builds_together_with_cell(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "together_with" in r.text
