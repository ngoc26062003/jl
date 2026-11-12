from io import BytesIO

import pytest
from fastapi import HTTPException
from PIL import Image

from app.services.images import normalize_uploaded_image


def test_normalize_uploaded_image_converts_supported_images_to_webp():
    source = BytesIO()
    Image.new("RGB", (16, 12), "pink").save(source, format="PNG")

    normalized = normalize_uploaded_image(source.getvalue())

    with Image.open(BytesIO(normalized)) as image:
        assert image.format == "WEBP"
        assert image.size == (16, 12)


def test_normalize_uploaded_image_rejects_non_image_data():
    with pytest.raises(HTTPException) as error:
        normalize_uploaded_image(b"not an image")

    assert error.value.status_code == 415


def test_normalize_uploaded_image_rejects_oversized_upload():
    with pytest.raises(HTTPException) as error:
        normalize_uploaded_image(b"x" * (5 * 1024 * 1024 + 1))

    assert error.value.status_code == 413
