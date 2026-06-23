import base64

from anthropic import Anthropic

from brews import config
from brews.models import Beer, Extraction

_PROMPT = """This is a photo of a bar's beer list.
Extract every beer you can read from the top five rows (it's a five row, four
column grid, with some extra plates beneath that you can ignore).
For each beer, capture its name, and the brewery, style, ABV, and price
when they are shown. Leave a field empty if it is not present."""


def extract_beers(image_bytes: bytes, media_type: str) -> list[Beer] | None:
    """Read a beer-list photo with Claude and return the beers it contains."""
    client = Anthropic(api_key=config.get_anthropic_api_key())
    data = base64.standard_b64encode(image_bytes).decode("utf-8")
    response = client.messages.parse(
        model="claude-opus-4-8",
        max_tokens=8192,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": data,
                        },
                    },  # pyright: ignore[reportArgumentType]
                    {"type": "text", "text": _PROMPT},
                ],
            }
        ],
        output_format=Extraction,
    )
    return response.parsed_output and response.parsed_output.beers or None
