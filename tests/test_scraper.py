import app.scraper.scrapers as scrapers
from app.models import Movie, Actor

LIST_HTML = """
<html>
  <body>
    <div class="content">
      <a href="/film/1-matrix/prehled/">Matrix</a>
      <a href="/film/2-dabluv-advokat/prehled/">Ďáblův advokát</a>
    </div>
  </body>
</html>
"""

DETAIL_HTMLS = {
    "http://test/film/1-matrix/prehled/": """
    <html>
      <body>
        <div class="creators">
          <div>
            <h4>Hrají</h4>
            <a href="/tvurce/1/">Keanu Reeves</a>
            <a href="/tvurce/2/">Carrie-Anne Moss</a>
          </div>
        </div>
      </body>
    </html>
    """,
    "http://test/film/2-dabluv-advokat/prehled/": """
    <html>
      <body>
        <div class="creators">
          <div>
            <h4>Hrají</h4>
            <a href="/tvurce/3/">Keanu Reeves</a>
            <a href="/tvurce/4/">Al Pacino</a>
          </div>
        </div>
      </body>
    </html>
    """,
}


class _StubPage:
    def __init__(self, html_map: dict[str, str]):
        self._html_map = html_map
        self._current_url: str | None = None

    async def goto(self, url: str, timeout: int = 0):
        if url not in self._html_map:
            raise AssertionError(f"Unexpected URL requested: {url}")
        self._current_url = url

    async def content(self) -> str:
        assert self._current_url is not None, "Page.content() called before goto()"
        return self._html_map[self._current_url]

    async def close(self):
        return None


class _StubBrowser:
    def __init__(self, html_map: dict[str, str]):
        self._html_map = html_map

    async def new_page(self):
        return _StubPage(self._html_map)

    async def close(self):
        return None


class _StubChromium:
    def __init__(self, html_map: dict[str, str]):
        self._html_map = html_map

    async def launch(self, headless: bool = False):
        return _StubBrowser(self._html_map)


class _AsyncPlaywrightStub:
    def __init__(self, html_map: dict[str, str]):
        self.chromium = _StubChromium(html_map)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False


def test_async_scraper_smoke(mocker, app, app_context):
    base_url = "http://test"
    list_url = f"{base_url}/zebricky/filmy/nejlepsi/"
    html_map = {
        f"{list_url}?from=1": LIST_HTML,
        **DETAIL_HTMLS,
    }

    mocker.patch("app.scraper.scrapers.flask_app", app)
    mocker.patch("app.scraper.scrapers.BASE_URL", base_url)
    mocker.patch("app.scraper.scrapers.TOP_300_URL", list_url)
    mocker.patch("app.scraper.scrapers.PAGE_OFFSETS", [1])
    mocker.patch("app.scraper.scrapers.async_playwright", return_value=_AsyncPlaywrightStub(html_map))

    scraper = scrapers.AsyncScraper(delay=0, workers=1)
    movie_count, actor_count = scraper.run()

    assert movie_count == 2
    assert actor_count == 3  # Keanu + Carrie + Al
    assert Movie.query.count() == 2
    assert Actor.query.count() == 3
