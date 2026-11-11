import pytest

from app.core.config import Settings


@pytest.mark.parametrize(
    "database_url",
    [
        "postgres://jl:secret@db.internal:5432/jl",
        "postgresql://jl:secret@db.internal:5432/jl",
        "postgresql+psycopg://jl:secret@db.internal:5432/jl",
    ],
)
def test_database_url_uses_psycopg(database_url):
    settings = Settings(database_url=database_url)

    assert settings.database_url == "postgresql+psycopg://jl:secret@db.internal:5432/jl"