from io import BytesIO

from fastapi import HTTPException
from PIL import Image, ImageOps, UnidentifiedImageError

MAX_UPLOAD_BYTES = 5 * 1024 * 1024
MAX_IMAGE_DIMENSION = 4096


def normalize_uploaded_image(raw: bytes) -> bytes:
    if len(raw) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Ảnh tối đa 5 MB.")

    try:
        with Image.open(BytesIO(raw)) as image:
            if image.format not in {"JPEG", "PNG", "WEBP"}:
                raise HTTPException(
                    status_code=415,
                    detail="Chỉ chấp nhận ảnh JPEG, PNG hoặc WebP.",
                )
            if image.width > MAX_IMAGE_DIMENSION or image.height > MAX_IMAGE_DIMENSION:
                raise HTTPException(
                    status_code=413,
                    detail="Kích thước ảnh tối đa 4096 × 4096.",
                )
            image = ImageOps.exif_transpose(image)
            if image.mode not in {"RGB", "RGBA"}:
                image = image.convert("RGBA" if "A" in image.getbands() else "RGB")
            output = BytesIO()
            image.save(output, format="WEBP", quality=85, method=5)
            return output.getvalue()
    except (UnidentifiedImageError, OSError):
        raise HTTPException(
            status_code=415,
            detail="Tệp tải lên không phải ảnh hợp lệ.",
        ) from None
    except Image.DecompressionBombError:
        raise HTTPException(
            status_code=413,
            detail="Ảnh có kích thước vượt giới hạn an toàn.",
        ) from None
