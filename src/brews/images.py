import io

from PIL import Image

_MAX_EDGE = 1568


def downscale(image_bytes: bytes) -> tuple[bytes, str]:
    """Re-encode an image as a JPEG whose longest edge is at most 1568 px.

    Returns the JPEG bytes and the `image/jpeg` media type. Raises if the
    input is not a readable image.
    """
    image = Image.open(io.BytesIO(image_bytes))
    image = image.convert("RGB")
    image.thumbnail((_MAX_EDGE, _MAX_EDGE))
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=85)
    return buffer.getvalue(), "image/jpeg"
