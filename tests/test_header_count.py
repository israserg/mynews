"""Black-box tests for the item count shown in the page header (BASE_URL, like test_api.py)."""
import os
import re

import httpx
import pytest

BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:8000")


@pytest.fixture(scope="module")
def client():
    with httpx.Client(base_url=BASE_URL, timeout=30) as c:
        yield c


def test_index_has_item_count_element(client):
    r = client.get("/")
    assert r.status_code == 200
    assert re.search(r'<header>.*id="count".*</header>', r.text, re.S)


def test_index_script_fills_count_from_news(client):
    r = client.get("/")
    assert r.status_code == 200
    assert 'getElementById("count")' in r.text
    assert "items.length" in r.text
