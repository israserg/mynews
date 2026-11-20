"""Black-box tests: they talk to a RUNNING mynews over HTTP (BASE_URL, default http://127.0.0.1:8000)."""
import os
import re

import httpx
import pytest

BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:8000")


@pytest.fixture(scope="module")
def client():
    with httpx.Client(base_url=BASE_URL, timeout=30) as c:
        yield c


def test_heading_text(client):
    r = client.get("/")
    assert r.status_code == 200
    m = re.search(r"<h1>(.*?)</h1>", r.text, re.S)
    assert m is not None
    assert m.group(1) == "AI TL/DR What’s new"


def test_heading_is_magenta(client):
    r = client.get("/")
    assert r.status_code == 200
    style = re.search(r"<style>(.*?)</style>", r.text, re.S)
    assert style is not None
    rule = re.search(r"(?<![-\w.#])h1\s*\{([^}]*)\}", style.group(1))
    assert rule is not None, "no CSS rule with selector h1"
    color = re.search(r"(?<![-\w])color\s*:\s*(#[0-9a-fA-F]{6})", rule.group(1))
    assert color is not None, "h1 rule sets no hex colour"
    value = color.group(1)
    red, green, blue = (int(value[i:i + 2], 16) for i in (1, 3, 5))
    assert red >= 0xC0 and blue >= 0xC0 and green <= 0x60
