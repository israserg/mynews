"""Black-box tests for the striped newsfeed table rows (BASE_URL, like test_api.py)."""
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


def _background_for(css, marker):
    # Returns the background colour set by the first rule whose selector contains `marker`.
    for m in re.finditer(r"([^{}]+)\{([^}]*)\}", css):
        if marker in m.group(1):
            bg = re.search(r"background(?:-color)?\s*:\s*(#[0-9a-fA-F]{6})\b", m.group(2))
            if bg:
                return bg.group(1)
    return None


def _is_light_grey(colour):
    r, g, b = (int(colour[i:i + 2], 16) for i in (1, 3, 5))
    return r == g == b and min(r, g, b) >= 0xD0


def test_odd_rows_have_light_grey_background(client):
    r = client.get("/")
    assert r.status_code == 200
    colour = _background_for(_style_block(r.text), "nth-child(odd)")
    assert colour is not None, "a rule with nth-child(odd) must set a background colour"
    assert _is_light_grey(colour), f"odd row colour {colour} must be light grey #rrggbb"


def test_even_rows_have_light_grey_background(client):
    r = client.get("/")
    assert r.status_code == 200
    colour = _background_for(_style_block(r.text), "nth-child(even)")
    assert colour is not None, "a rule with nth-child(even) must set a background colour"
    assert _is_light_grey(colour), f"even row colour {colour} must be light grey #rrggbb"


def test_row_colours_differ(client):
    r = client.get("/")
    assert r.status_code == 200
    css = _style_block(r.text)
    odd = _background_for(css, "nth-child(odd)")
    even = _background_for(css, "nth-child(even)")
    assert odd and even, "both odd and even row backgrounds must be set"
    assert odd.lower() != even.lower(), "odd and even rows need different colours"
