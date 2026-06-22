import pytest

from brews import db
from brews.models import Beer


@pytest.fixture
def temp_db(tmp_path, monkeypatch):
    monkeypatch.setenv("BREWS_DB_PATH", str(tmp_path / "test.db"))
    db.init_db()


def test_list_is_empty_initially(temp_db):
    assert db.list_beers() == []


def test_replace_then_list_preserves_order(temp_db):
    db.replace_beers([Beer(name="Pils"), Beer(name="Stout", abv=6.2)])
    beers = db.list_beers()
    assert [beer.name for beer in beers] == ["Pils", "Stout"]
    assert beers[1].abv == 6.2


def test_replace_overwrites_previous_list(temp_db):
    db.replace_beers([Beer(name="Old")])
    db.replace_beers([Beer(name="New")])
    assert [beer.name for beer in db.list_beers()] == ["New"]
