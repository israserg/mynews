"""Black-box tests for the weekday field: they talk to a RUNNING mynews over HTTP (BASE_URL, default http://127.0.0.1:8000)."""
import email.utils
import os

import httpx
import pytest

BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:8000")
DAYS = {"Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"}


@pytest.fixture(scope="module")
def client():
    with httpx.Client(base_url=BASE_URL, timeout=30) as c:
        yield c


def test_items_have_weekday_key(client):
    items = client.get("/api/news").json()
    assert items
    for it in items:
        assert "weekday" in it


def test_weekday_is_a_day_name(client):
    items = client.get("/api/news").json()
    assert items
    for it in items:
        assert it["weekday"] in DAYS


def test_weekday_matches_published(client):
    items = client.get("/api/news").json()
    assert items
    for it in items:
        assert it["published"]
        expected = email.utils.parsedate_to_datetime(it["published"]).strftime("%A")
        assert it["weekday"] == expected


def test_index_renders_weekday_badge(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "it.weekday" in r.text
    assert ".day" in r.text
