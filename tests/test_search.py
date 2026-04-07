import pytest

from app.queries import save_movie


@pytest.fixture
def sample_data(app_context):
    save_movie(
        {
            "title": "Matrix",
            "rank": 1,
            "url": "http://example.com/matrix",
            "actors": ["Keanu Reeves", "Carrie-Anne Moss"],
        }
    )
    save_movie(
        {
            "title": "Pelíšky",
            "rank": 2,
            "url": "http://example.com/pelisky",
            "actors": ["Bolek Polívka", "Jiří Kodet"],
        }
    )


def test_search_matches_substrings(client, sample_data):
    response = client.get("/?q=tri")
    body = response.data.decode("utf-8")

    assert "Matrix" in body
    assert "Pelíšky" not in body


def test_search_returns_matching_actor(client, sample_data):
    response = client.get("/?q=keanu")
    body = response.data.decode("utf-8")

    assert "Keanu Reeves" in body
    assert "Bolek Polívka" not in body


def test_search_ignores_diacritics(client, sample_data):
    response = client.get("/?q=polivka")
    body = response.data.decode("utf-8")

    assert "Bolek Polívka" in body


def test_movie_search_ignores_diacritics(client, sample_data):
    response = client.get("/?q=pelis")
    body = response.data.decode("utf-8")

    assert "Pelíšky" in body


def test_actor_deduplicates_across_movies(client, app_context):
    save_movie(
        {
            "title": "Matrix",
            "rank": 1,
            "url": "http://example.com/matrix",
            "actors": ["Keanu Reeves"],
        }
    )
    save_movie(
        {
            "title": "Ďáblův advokát",
            "rank": 2,
            "url": "http://example.com/dabluv-advokat",
            "actors": ["Keanu Reeves"],
        }
    )

    response = client.get("/?q=keanu")
    body = response.data.decode("utf-8")

    assert body.count("Keanu Reeves") == 1
