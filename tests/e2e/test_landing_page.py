import re
from urllib.parse import urlsplit

from playwright.sync_api import Page, expect

WCAG_AA_NORMAL_TEXT = 4.5


def _luminance(css_color: str) -> float:
    match = re.fullmatch(r"rgba?\((\d+), (\d+), (\d+)(?:, [\d.]+)?\)", css_color)
    assert match, css_color
    channels = []
    for value in match.groups():
        c = int(value) / 255
        channels.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    red, green, blue = channels
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def _contrast(foreground: str, background: str) -> float:
    lighter, darker = sorted((_luminance(foreground), _luminance(background)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


def test_landing_page_shows_product_name_in_turkish(page: Page) -> None:
    """AC-1, AC-2: started with the README command; one h1, Turkish 'coming soon' text, lang=tr."""
    page.goto("/")

    expect(page.locator("html")).to_have_attribute("lang", "tr")
    expect(page.locator("h1")).to_have_count(1)
    expect(page.locator("h1")).to_have_text("Polsan İzin Yönetimi")
    expect(page.get_by_text("yakında kullanıma açılacak")).to_be_visible()


def test_landing_page_text_contrast_meets_wcag_aa(page: Page) -> None:
    """AC-2: text/background contrast >= 4.5:1."""
    page.goto("/")
    background = page.evaluate("getComputedStyle(document.body).backgroundColor")

    for selector in ("h1", "p"):
        color = page.locator(selector).evaluate("el => getComputedStyle(el).color")
        assert _contrast(color, background) >= WCAG_AA_NORMAL_TEXT, selector


def test_landing_page_makes_no_cross_origin_requests(page: Page, base_url: str) -> None:
    """AC-3: every request while loading the page goes to the app's own origin."""
    requested: list[str] = []
    page.on("request", lambda request: requested.append(request.url))

    page.goto("/")
    page.wait_for_load_state("networkidle")

    own_origin = urlsplit(base_url).netloc
    assert any(url.endswith("/styles.css") for url in requested)
    assert [url for url in requested if urlsplit(url).netloc != own_origin] == []
