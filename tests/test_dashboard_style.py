"""Black-box tests for the restyled mynews dashboard (BASE_URL, like test_api.py)."""
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


def test_table_container_has_rounded_corners(client):
    r = client.get("/")
    assert r.status_code == 200
    assert re.search(r"border-radius\s*:\s*\d+px", _style_block(r.text)), (
        "a CSS rule must give the table container a px border-radius"
    )


def test_table_container_has_shadow(client):
    r = client.get("/")
    assert r.status_code == 200
    values = re.findall(r"box-shadow\s*:\s*([^;}]+)", _style_block(r.text))
    assert values, "a CSS rule must set box-shadow"
    assert any(v.strip() != "none" for v in values), "box-shadow must not be none"


def test_rows_highlight_on_hover(client):
    r = client.get("/")
    assert r.status_code == 200
    rules = re.findall(r"([^{}]*:hover[^{}]*)\{([^}]*)\}", _style_block(r.text))
    assert rules, "a CSS rule with a :hover selector is required"
    row_hover = [
        sel for sel, body in rules
        if re.search(r"\b(tr|td)\b", sel) and re.search(r"background(?:-color)?\s*:\s*\S+", body)
    ]
    assert row_hover, "a :hover rule on table rows or cells must set a background colour"


def test_topics_rendered_as_chips(client):
    r = client.get("/")
    assert r.status_code == 200
    assert 'createElement("span")' in r.text, "topics must be rendered as span elements"
    assert '"chip"' in r.text, "topic spans must carry the chip class"
    chip_rules = [
        body for sel, body in re.findall(r"([^{}]*)\{([^}]*)\}", _style_block(r.text))
        if re.search(r"(?<![\w-])\.chip\b", sel)
    ]
    assert chip_rules, "a .chip CSS rule is required"
    assert any(re.search(r"border-radius\s*:", body) for body in chip_rules), (
        ".chip rule must set border-radius"
    )


def test_striped_rows_still_neutral_grey(client):
    r = client.get("/")
    assert r.status_code == 200
    css = _style_block(r.text)
    odd = _background_for(css, "nth-child(odd)")
    even = _background_for(css, "nth-child(even)")
    assert odd and even, "both odd and even row backgrounds must be set"
    assert _is_light_grey(odd), f"odd row colour {odd} must be neutral light grey"
    assert _is_light_grey(even), f"even row colour {even} must be neutral light grey"
    assert odd.lower() != even.lower(), "odd and even rows need different colours"


def test_heading_and_count_still_present(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "<h1>AI TL/DR What’s new</h1>" in r.text
    assert re.search(r'<header>.*id="count".*</header>', r.text, re.S)
