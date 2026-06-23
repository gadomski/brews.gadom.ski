import io

import pytest
from PIL import Image

from brews import images


def _png_bytes(width: int, height: int) -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (width, height), "white").save(buffer, format="PNG")
    return buffer.getvalue()


def test_downscale_shrinks_to_max_edge_and_returns_jpeg():
    data, media_type = images.downscale(_png_bytes(4000, 3000))
    assert media_type == "image/jpeg"
    result = Image.open(io.BytesIO(data))
    assert result.format == "JPEG"
    assert max(result.size) <= 1568


def test_downscale_leaves_small_images_within_bounds():
    data, _ = images.downscale(_png_bytes(800, 600))
    result = Image.open(io.BytesIO(data))
    assert result.size == (800, 600)


def test_downscale_rejects_non_image_bytes():
    with pytest.raises(Exception):
        images.downscale(b"not an image")
