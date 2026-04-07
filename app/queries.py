from sqlalchemy.dialects.sqlite import insert
from unidecode import unidecode

from app import db
from app.models import Movie, Actor


def normalize(value: str) -> str:
    return unidecode(value or "").lower()


def save_movie(data: dict):
    """Save a movie with its actors."""
    movie = Movie(
        title=data["title"],
        rank=data["rank"],
        url=data["url"],
        search_title=normalize(data["title"]),
    )
    db.session.add(movie)

    for name in dict.fromkeys(data["actors"]):
        normalized = normalize(name)
        stmt = (
            insert(Actor)
            .values(name=name, search_name=normalized)
            .on_conflict_do_nothing(index_elements=["name"])
        )
        db.session.execute(stmt)
        actor = Actor.query.filter_by(name=name).first()
        movie.actors.append(actor)
    db.session.commit()


def get_existing_urls() -> set[str]:
    return {m.url for m in Movie.query.all()}


def get_counts() -> tuple[int, int]:
    return Movie.query.count(), Actor.query.count()
