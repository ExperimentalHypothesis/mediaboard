import pytest

from app.queries import normalize


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("Matrix", "matrix"),
        ("Vykoupení z věznice Shawshank", "vykoupeni z veznice shawshank"),
        ("  Forrest  Gump  ", "  forrest  gump  "),
        ("", ""),
        (None, ""),
    ],
)
def test_normalize(value, expected):
    assert normalize(value) == expected
