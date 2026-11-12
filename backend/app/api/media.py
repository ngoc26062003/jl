from io import BytesIO

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import Response
from PIL import Image, ImageOps, UnidentifiedImageError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import require_admin
from app.db.session import get_db
from app.models import User
from app.models.activity import MediaAsset

router = APIRouter(prefix="/media", tags=["media"])
MAX_UPLOAD_BYTES = 5 * 1024 * 1024
MAX_IMAGE_DIMENSION = 4096
SLOTS = {
    "home-hero": "Ảnh chính trang chủ",
    "activity-hiragana": "Ảnh minh họa Hiragana",
    "activity-katakana": "Ảnh minh họa Katakana",
    "activity-grammar": "Ảnh minh họa bài học",
    "activity-quiz": "Ảnh minh họa trắc nghiệm",
}


@router.get("")
def list_images(
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    assets = {
        asset.slot: asset
        for asset in db.scalars(select(MediaAsset).where(MediaAsset.slot.in_(SLOTS)))
    }
    return [
        {
            "slot": slot,
            "label": label,
            "url": f"/media/{slot}?v={assets[slot].updated_at.timestamp() if slot in assets else 0}",
            "updated_at": assets[slot].updated_at.isoformat() if slot in assets else None,
        }
        for slot, label in SLOTS.items()
    ]


@router.get("/slots")
def public_image_slots(db: Session = Depends(get_db)):
    assets = {
        asset.slot: asset
        for asset in db.scalars(select(MediaAsset).where(MediaAsset.slot.in_(SLOTS)))
    }
    return [
        {
            "slot": slot,
            "url": f"/media/{slot}?v={assets[slot].updated_at.timestamp()}"
            if slot in assets
            else None,
        }
        for slot in SLOTS
    ]


@router.get("/{slot}")
def get_image(slot: str, db: Session = Depends(get_db)):
    if slot not in SLOTS:
        raise HTTPException(status_code=404, detail="Ảnh không tồn tại.")
    asset = db.get(MediaAsset, slot)
    if asset is None:
        raise HTTPException(status_code=404, detail="Ảnh chưa được tải lên.")
    return Response(
        content=asset.data,
        media_type=asset.content_type,
        headers={"Cache-Control": "no-cache"},
    )


@router.put("/{slot}")
async def replace_image(
    slot: str,
    file: UploadFile = File(...),
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    if slot not in SLOTS:
        raise HTTPException(status_code=404, detail="Vị trí ảnh không hợp lệ.")
    raw = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(raw) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Ảnh tối đa 5 MB.")

    try:
        with Image.open(BytesIO(raw)) as image:
            if image.format not in {"JPEG", "PNG", "WEBP"}:
                raise HTTPException(status_code=415, detail="Chỉ chấp nhận ảnh JPEG, PNG hoặc WebP.")
            if image.width > MAX_IMAGE_DIMENSION or image.height > MAX_IMAGE_DIMENSION:
                raise HTTPException(status_code=413, detail="Kích thước ảnh tối đa 4096 × 4096.")
            image = ImageOps.exif_transpose(image)
            if image.mode not in {"RGB", "RGBA"}:
                image = image.convert("RGBA" if "A" in image.getbands() else "RGB")
            output = BytesIO()
            image.save(output, format="WEBP", quality=85, method=5)
            normalized = output.getvalue()
    except (UnidentifiedImageError, OSError):
        raise HTTPException(status_code=415, detail="Tệp tải lên không phải ảnh hợp lệ.") from None
    except Image.DecompressionBombError:
        raise HTTPException(status_code=413, detail="Ảnh có kích thước vượt giới hạn an toàn.") from None

    asset = db.get(MediaAsset, slot)
    if asset is None:
        asset = MediaAsset(slot=slot, content_type="image/webp", data=normalized)
        db.add(asset)
    else:
        asset.content_type = "image/webp"
        asset.data = normalized
    db.commit()
    db.refresh(asset)
    return {
        "slot": slot,
        "label": SLOTS[slot],
        "url": f"/media/{slot}?v={asset.updated_at.timestamp()}",
        "updated_at": asset.updated_at.isoformat(),
    }
