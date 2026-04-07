import typer

from app import create_app
from app.scraper import AsyncScraper, SyncScraper

app = typer.Typer(help="CSFD Top 300 management commands")
flask_app = create_app()


@app.command()
def scrape_sync(
    delay: float = typer.Option(1.0, "--delay", "-d", help="Delay between requests (seconds)"),
):
    """Scrape CSFD top 300 movies using sync mode."""
    typer.echo("Starting scrape (sync)...")
    movie_count, actor_count = SyncScraper(delay=delay).run()
    typer.echo(f"\nDone! {movie_count} movies and {actor_count} actors.")


@app.command()
def scrape_async(
    delay: float = typer.Option(0.5, "--delay", "-d", help="Delay between requests (seconds)"),
    workers: int = typer.Option(5, "--workers", "-w", help="Max concurrent workers"),
):
    """Scrape CSFD top 300 movies using async mode."""
    typer.echo(f"Starting scrape (async with {workers} workers)...")
    movie_count, actor_count = AsyncScraper(delay=delay, workers=workers).run()
    typer.echo(f"\nDone! {movie_count} movies and {actor_count} actors.")


if __name__ == "__main__":
    app()
