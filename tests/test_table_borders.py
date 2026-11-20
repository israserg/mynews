"""Black-box tests for the newsfeed table cell borders and background (BASE_URL, like test_api.py)."""
import os
import re

import httpx
import pytest

BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:8000")


@pytest.fixture(scope="module")
def client():
    with httpx.Client(base_url=BASE_URL, timeout=30) as c:
        yield c


def _style_block(html):
    m = re.search(r"<style[^>]*>(.*?)</style>", html, re.S)
    assert m, "no inline <style> block in /"
    return m.group(1)


def _rules_for(css, selector):
    # Returns the declaration bodies of every rule whose selector list includes `selector`.
    bodies = []
    for m in re.finditer(r"([^{}]+)\{([^}]*)\}", css):
        selectors = [s.strip() for s in m.group(1).split(",")]
        if selector in selectors:
            bodies.append(m.group(2))
    return bodies


def test_td_has_full_border(client):
    r = client.get("/")
    assert r.status_code == 200
    css = _style_block(r.text)
    bodies = _rules_for(css, "td") + _rules_for(css, "th, td")
    assert any(
        re.search(r"(?<![-\w])border\s*:\s*1px\s+solid\s+(?!#eee\b)[^;]+;", body)
        for body in bodies
    ), "td cells need a 1px solid border on all sides with a colour other than #eee"


def test_td_has_light_background(client):
    r = client.get("/")
    assert r.status_code == 200
    css = _style_block(r.text)
    bodies = _rules_for(css, "td")
    assert any(re.search(r"background(-color)?\s*:\s*\S+", body) for body in bodies), (
        "a td rule must set a background colour"
    )


def test_table_view_still_rendered(client):
    r = client.get("/")
    assert r.status_code == 200
    assert re.search(r'createElement\("table"\)|<table', r.text)
    assert '"Date"' in r.text
    assert '"Topics"' in r.text
    assert '"Link"' in r.text
