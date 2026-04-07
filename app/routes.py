from flask import Blueprint, render_template, request
from unidecode import unidecode

from app.models import Movie, Actor

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    """Search page (Screen 1)."""
    query = request.args.get("q", "").strip()
    movies = []
    actors = []

    if query:
        q = unidecode(query).lower()

        movies = (
            Movie.query.filter(Movie.search_title.contains(q))
            .order_by(Movie.rank)
            .all()
        )

        actors = (
            Actor.query.filter(Actor.search_name.contains(q))
            .order_by(Actor.name)
            .all()
        )

    return render_template(
        "search.html",
        query=query,
        movies=movies,
        actors=actors,
    )


@bp.route("/movie/<int:movie_id>")
def movie_detail(movie_id: int):
    """Movie detail page (Screen 2)."""
    movie = Movie.query.get_or_404(movie_id)
    return render_template("movie.html", movie=movie)


@bp.route("/actor/<int:actor_id>")
def actor_detail(actor_id: int):
    """Actor detail page (Screen 2)."""
    actor = Actor.query.get_or_404(actor_id)
    return render_template("actor.html", actor=actor)
