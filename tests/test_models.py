from brews.models import Beer, Extraction


def test_beer_requires_only_name():
    beer = Beer(name="Hazy IPA")
    assert beer.name == "Hazy IPA"
    assert beer.brewery is None
    assert beer.abv is None


def test_extraction_wraps_beers():
    extraction = Extraction(beers=[Beer(name="Pils"), Beer(name="Stout", abv=6.2)])
    assert [beer.name for beer in extraction.beers] == ["Pils", "Stout"]
    assert extraction.beers[1].abv == 6.2
