import asyncio
import time

from playwright.async_api import async_playwright
from playwright.sync_api import sync_playwright

from app import create_app
from app.queries import save_movie, get_existing_urls, get_counts
from app.scraper.parsers import MovieListParser, MoviePageParser

BASE_URL = "https://www.csfd.cz"
TOP_300_URL = f"{BASE_URL}/zebricky/filmy/nejlepsi/"
PAGE_OFFSETS = [1, 100, 200, 300]
TOP_MOVIE_LIMIT = 300


flask_app = create_app()


class SyncScraper:
    def __init__(self, delay: float = 1.0):
        self.delay = delay
        self.success = 0
        self.failed = 0
        self.skipped = 0
        self.start_time = 0.0


    def run(self) -> tuple[int, int]:
        """Main entrypoint."""
        with flask_app.app_context():
            existing_urls = get_existing_urls()
            return self._run(existing_urls)

    def _run(self, existing_urls: set[str]) -> tuple[int, int]:
        """Scrape movies from CSFD top 300 list and save to database."""
        self.start_time = time.time()
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            all_movies = self._scrape_movie_list(browser)
            movies = [m for m in all_movies if m["url"] not in existing_urls]
            self.skipped = len(all_movies) - len(movies)

            if movies:
                print(f"Scraping {len(movies)}/{len(all_movies)} movies (skipped {self.skipped})...")
                self._scrape_movie_details(browser, movies)
            else:
                print(f"All {len(all_movies)} movies already scraped")

            browser.close()
            self._print_summary()

        return get_counts()

    def _scrape_movie_list(self, browser) -> list[dict]:
        """Fetch movie titles and URLs from the top 300 ranking pages."""
        movies = []
        page = browser.new_page()

        for offset in PAGE_OFFSETS:
            url = f"{TOP_300_URL}?from={offset}"
            print(f"Fetching list page: offset={offset}")

            try:
                page.goto(url, timeout=30000)
                html = page.content()

                for movie in MovieListParser(html, BASE_URL).get_movies():
                    if not any(m["url"] == movie["url"] for m in movies):
                        movie["rank"] = len(movies) + 1
                        movies.append(movie)
                    if len(movies) >= TOP_MOVIE_LIMIT:
                        break

            except Exception as e:
                print(f"Error fetching list page: {e}")
            if len(movies) >= TOP_MOVIE_LIMIT:
                break

        page.close()
        return movies

    def _scrape_movie_details(self, browser, movies: list[dict]) -> None:
        """Fetch details for each movie and save to database."""
        for movie in movies:
            print(f"[{movie['rank']:3d}] {movie['title']}...", end=" ", flush=True)
            actors = self._scrape_actors(browser, movie["url"])
            if actors is not None:
                print(f"{len(actors)} actors")
                save_movie({**movie, "actors": actors})
                self.success += 1
            else:
                self.failed += 1
            time.sleep(self.delay)

    def _scrape_actors(self, browser, url: str) -> list[str] | None:
        """Fetch actor list from a movie's detail page. Retries up to 3 times."""
        page = browser.new_page()

        for attempt in range(3):
            try:
                page.goto(url, timeout=30000)
                time.sleep(1)
                html = page.content()
                page.close()
                return MoviePageParser(html).get_actors()
            except Exception:
                if attempt < 2:
                    print(f"Retry {attempt + 1}/3...", end=" ", flush=True)
                    time.sleep((attempt + 1) * 2)
                else:
                    print("Failed")

        page.close()
        return None

    def _print_summary(self) -> None:
        elapsed = time.time() - self.start_time
        print(f"\n--- Summary ---")
        print(f"Inserted: {self.success}, Failed: {self.failed}, Skipped: {self.skipped}")
        print(f"Time: {elapsed:.1f}s")



class AsyncScraper:
    def __init__(self, delay: float = 0.5, workers: int = 5):
        self.delay = delay
        self.workers = workers
        self.success = 0
        self.failed = 0
        self.skipped = 0
        self.start_time = 0.0

    def run(self) -> tuple[int, int]:
        """Main entrypoint."""
        with flask_app.app_context():
            existing_urls = get_existing_urls()
            return asyncio.run(self._run(existing_urls))

    async def _run(self, existing_urls: set[str]) -> tuple[int, int]:
        """Scrape movies from CSFD top 30
        0 list and save to database."""
        self.start_time = time.time()
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            all_movies = await self._scrape_movie_list(browser)
            movies = [m for m in all_movies if m["url"] not in existing_urls]
            self.skipped = len(all_movies) - len(movies)

            if movies:
                print(f"Scraping {len(movies)}/{len(all_movies)} movies (skipped {self.skipped}), max {self.workers} concurrent...")
                await self._scrape_movie_details(browser, movies)
            else:
                print(f"All {len(all_movies)} movies already scraped")

            await browser.close()
            self._print_summary()

        return get_counts()

    async def _scrape_movie_list(self, browser) -> list[dict]:
        """Fetch movie titles and URLs from the top 300 ranking pages."""
        movies = []
        page = await browser.new_page()

        for offset in PAGE_OFFSETS:
            url = f"{TOP_300_URL}?from={offset}"
            print(f"Fetching list page: offset={offset}")

            try:
                await page.goto(url, timeout=20000)
                html = await page.content()

                for movie in MovieListParser(html, BASE_URL).get_movies():
                    if not any(m["url"] == movie["url"] for m in movies):
                        movie["rank"] = len(movies) + 1
                        movies.append(movie)
                    if len(movies) >= TOP_MOVIE_LIMIT:
                        break

            except Exception as e:
                print(f"Error fetching list page: {e}")
            if len(movies) >= TOP_MOVIE_LIMIT:
                break

        await page.close()
        return movies

    async def _scrape_movie_details(self, browser, movies: list[dict]) -> None:
        """Fetch details for each movie concurrently and save to database."""
        semaphore = asyncio.Semaphore(self.workers)
        tasks = [self._scrape_actors(browser, semaphore, m) for m in movies]

        for coro in asyncio.as_completed(tasks):
            result = await coro
            if result:
                save_movie(result)
                self.success += 1
            else:
                self.failed += 1

    async def _scrape_actors(self, browser, semaphore: asyncio.Semaphore, movie: dict) -> dict | None:
        """Fetch actor list from a movie's detail page. Retries up to 3 times."""
        async with semaphore:
            page = await browser.new_page()

            for attempt in range(3):
                try:
                    await page.goto(movie["url"], timeout=20000)
                    html = await page.content()
                    actors = MoviePageParser(html).get_actors()
                    print(f"[{movie['rank']:3d}] {movie['title']}: {len(actors)} actors")
                    await page.close()
                    await asyncio.sleep(self.delay)
                    return {**movie, "actors": actors}
                except Exception:
                    if attempt < 2:
                        print(f"[{movie['rank']:3d}] Retry {attempt + 1}/3: {movie['title']}")
                        await asyncio.sleep((attempt + 1) * 2)
                    else:
                        print(f"[{movie['rank']:3d}] Failed: {movie['title']}")

            await page.close()
            return None

    def _print_summary(self) -> None:
        """Print scraping results summary."""
        elapsed = time.time() - self.start_time
        print(f"\n--- Summary ---")
        print(f"Inserted: {self.success}, Failed: {self.failed}, Skipped: {self.skipped}")
        print(f"Time: {elapsed:.1f}s")
