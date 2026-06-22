import base64

from brews import extract
from brews.models import Beer, Extraction


def test_extract_returns_parsed_beers(monkeypatch):
    captured = {}

    class FakeMessages:
        def parse(self, **kwargs):
            captured.update(kwargs)

            class Response:
                parsed_output = Extraction(beers=[Beer(name="Hazy IPA", abv=6.5)])

            return Response()

    class FakeAnthropic:
        def __init__(self, *args, **kwargs):
            self.messages = FakeMessages()

    monkeypatch.setattr(extract, "Anthropic", FakeAnthropic)

    beers = extract.extract_beers(b"rawbytes", "image/jpeg")

    assert [beer.name for beer in beers] == ["Hazy IPA"]
    assert captured["model"] == "claude-opus-4-8"
    image_block = captured["messages"][0]["content"][0]
    assert image_block["source"]["data"] == base64.standard_b64encode(b"rawbytes").decode("utf-8")
    assert image_block["source"]["media_type"] == "image/jpeg"
