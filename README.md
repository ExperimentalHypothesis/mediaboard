# CSFD Top 300 Movies Search

Flask application for searching the CSFD Top 300 catalogue backed by SQLite.

## Requirements

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager

## Setup

```bash
make install       # Install dependencies + Playwright chromium build
make scrape-async  # Scrape CSFD (async Playwright, default workers=5)
# or: make scrape-sync
```

The repository includes a pre-scraped `db/csfd.db` with 300 movies and their actors.
Run `make scrape-async` again whenever you want to refresh the dataset.

```bash
make run           # Start server at http://localhost:5555
make clean         # Remove the SQLite database
```

You can also use the typer CLI directly, e.g.:

```bash
uv run python manage.py scrape-async --workers 8 --delay 0.3
```

## Usage

1. Open http://localhost:5555
2. Enter a movie title or actor name in the search box
3. Click on a movie/actor to see its detail page

Search ignores case, diacritics, and matches substrings.

## Next Steps
1. Make DB migrations with Alembic
2. Add resilient scraping
3. Observability 
4. ...

