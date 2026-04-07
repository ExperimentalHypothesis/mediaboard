import pytest

from app.scraper.parsers import MovieListParser, MoviePageParser

LIST_HTML = """
<html>
  <body>
    <div class="content">
      <a href="/film/12345-matrix/prehled/">Matrix</a>
      <a href="/film/67890-pelisky/prehled/">Pelíšky</a>
      <a href="/film/duplicate/prehled/">Duplicate</a>
      <a href="/film/duplicate/prehled/">Duplicate</a>
      <a href="/serial/ignore/prehled/">Ignore serial</a>
    </div>
  </body>
</html>
"""

DETAIL_HTML = """
<html>
  <body>
    <div class="creators">
      <div>
        <h4>Režie</h4>
        <a href="/tvurce/1/">Someone</a>
      </div>
      <div>
        <h4>Hrají</h4>
        <a href="/tvurce/717/">Keanu Reeves</a>
        <a href="/tvurce/999/">Carrie-Anne Moss</a>
        <a href="/tvurce/888/">Laurence Fishburne</a>
        <a href="/jiny-link/">Ignore me</a>
      </div>
    </div>
  </body>
</html>
"""


@pytest.fixture
def list_html():
    return LIST_HTML


@pytest.fixture
def detail_html():
    return DETAIL_HTML


def test_movie_list_parser_extracts_unique_ranked_movies(list_html):
    parser = MovieListParser(list_html, base_url="https://www.csfd.cz")
    movies = parser.get_movies()

    assert len(movies) == 3
    assert movies[0] == {
        "rank": 1,
        "title": "Matrix",
        "url": "https://www.csfd.cz/film/12345-matrix/prehled/",
    }
    assert [m["rank"] for m in movies] == [1, 2, 3]


def test_movie_page_parser_extracts_actors(detail_html):
    parser = MoviePageParser(detail_html)
    actors = parser.get_actors()

    assert actors == [
        "Keanu Reeves",
        "Carrie-Anne Moss",
        "Laurence Fishburne",
    ]
