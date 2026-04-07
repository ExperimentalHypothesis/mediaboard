from app import db


class MovieActor(db.Model):
    __tablename__ = "movie_actors"

    movie_id = db.Column(db.Integer, db.ForeignKey("movie.id"), primary_key=True)
    actor_id = db.Column(db.Integer, db.ForeignKey("actor.id"), primary_key=True)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    rank = db.Column(db.Integer, nullable=False)
    url = db.Column(db.String(500), nullable=False, unique=True)
    search_title = db.Column(db.String(255), nullable=False, index=True)

    actors = db.relationship(
        "Actor",
        secondary=MovieActor.__table__,
        backref=db.backref("movies", lazy="dynamic"),
        lazy="dynamic",
    )

    def __repr__(self):
        return f"<Movie #{self.rank} {self.title}>"


class Actor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    search_name = db.Column(db.String(255), nullable=False, index=True)

    def __repr__(self):
        return f"<Actor {self.name}>"
