"""Black-box tests for the news list rendered as a table (BASE_URL, like test_api.py)."""
import os
import re

import httpx
import pytest

BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:8000")


@pytest.fixture(scope="module")
def client():
    with httpx.Client(base_url=BASE_URL, timeout=30) as c:
        yield c


def test_index_renders_news_table(client):
    r = client.get("/")
    assert r.status_code == 200
    assert re.search(r'createElement\("table"\)|<table', r.text)


def test_index_table_has_expected_columns(client):
    r = client.get("/")
    assert r.status_code == 200
    assert '"Date"' in r.text
    assert '"Topics"' in r.text
    assert '"Link"' in r.text


def test_index_rows_built_per_item(client):
    r = client.get("/")
    assert r.status_code == 200
    assert 'createElement("tr")' in r.text
    assert 'a.target = "_blank"' in r.text
    assert 'a.rel = "noopener"' in r.text


def test_index_no_article_per_item(client):
    r = client.get("/")
    assert r.status_code == 200
    assert 'createElement("article")' not in r.text


def test_index_still_fills_count(client):
    r = client.get("/")
    assert r.status_code == 200
    assert 'getElementById("count")' in r.text
    assert "items.length" in r.text
