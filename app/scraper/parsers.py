"""HTML parsing classes."""

from urllib.parse import urljoin
from bs4 import BeautifulSoup


class MovieListParser:
    LINK_SELECTOR = 'a[href^="/film/"]'

    def __init__(self, html: str, base_url: str):
        self.soup = BeautifulSoup(html, "html.parser")
        self.base_url = base_url

    def get_movies(self) -> list[dict]:
        movies = []
        for link in self.soup.select(self.LINK_SELECTOR):
            href = link.get("href", "")
            title = link.get_text(strip=True)

            if not title or "/prehled/" not in href:
                continue

            url = urljoin(self.base_url, href)
            if any(m["url"] == url for m in movies):
                continue

            movies.append({"rank": len(movies) + 1, "title": title, "url": url})

        return movies


class MoviePageParser:
    CREATORS_SELECTOR = "div.creators"
    ACTOR_SELECTOR = "a"

    def __init__(self, html: str):
        self.soup = BeautifulSoup(html, "html.parser")

    def get_actors(self) -> list[str]:
        creators = self.soup.select_one(self.CREATORS_SELECTOR)
        if not creators:
            return []

        for div in creators.select("div"):
            h4 = div.select_one("h4")
            if h4 and "Hrají" in h4.get_text():
                return [
                    link.get_text(strip=True)
                    for link in div.select(self.ACTOR_SELECTOR)
                    if "/tvurce/" in link.get("href", "") and link.get_text(strip=True)
                ]

        return []
