.PHONY: install scrape-async scrape-sync run clean test

install:
	uv sync --extra dev
	uv run playwright install chromium

scrape-sync:
	uv run python manage.py scrape-sync

scrape-async:
	uv run python manage.py scrape-async

run:
	uv run python main.py

test:
	uv run pytest

clean:
	rm -f db/csfd.db
