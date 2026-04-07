import pytest
from app import create_app, db


@pytest.fixture()
def app(tmp_path, monkeypatch):
    test_db = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{test_db}")

    flask_app = create_app()
    flask_app.config.update(TESTING=True)

    with flask_app.app_context():
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def app_context(app):
    with app.app_context():
        yield
