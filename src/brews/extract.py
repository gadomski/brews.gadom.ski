import base64

from anthropic import Anthropic

from .models import Extraction
from .settings import Settings

_PROMPT = """This is a photo of a bar's beer list. The beers are in a five row,
four column grid (twenty beers total). For each beer, capture its name, and the
brewery, style, ABV, and price when they are shown. Leave a field empty if it is
not present. Ignore the extra plates below the 5x4 grid.

For each beer, also generate a comment about the plate. The comment could include:

    - Things that were ambiguous about the image that you weren't sure about
    - Any pictures that are on the beer plate
"""


def beers(image: bytes, media_type: str, settings: Settings) -> Extraction | None:
    client = Anthropic(api_key=settings.anthropic_api_key.get_secret_value())
    data = base64.standard_b64encode(image).decode("utf-8")
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
    return response.parsed_output
