"""Private patient image upload and access endpoints."""

import logging
import uuid
from datetime import timezone

from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from database.database import get_db
from Patient.models.PatientImage import PatientImage
from uploads.ImageUploads import (
    delete_patient_image,
    get_patient_image_url,
    upload_patient_image,
)
from utilityfunctions.reusable_functions import extract_patient_id

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/patients/me/images", tags=["patient images"])
bearer_scheme = HTTPBearer(auto_error=False)
MAX_IMAGE_BYTES = 8 * 1024 * 1024
IMAGE_TYPES = {
    "jpeg": ("image/jpeg", b"\xff\xd8\xff"),
    "png": ("image/png", b"\x89PNG\r\n\x1a\n"),
    "webp": ("image/webp", b"RIFF"),
}


def _patient_id(credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme)) -> int:
    return extract_patient_id(credentials)


def _inspect_image(file: UploadFile) -> tuple[int, str, str]:
    """Validate image bytes (not the caller-supplied MIME type) and rewind."""
    file.file.seek(0)
    prefix = file.file.read(12)
    file.file.seek(0)
    if prefix.startswith(IMAGE_TYPES["jpeg"][1]):
        extension = "jpg"
        content_type = IMAGE_TYPES["jpeg"][0]
    elif prefix.startswith(IMAGE_TYPES["png"][1]):
        extension = "png"
        content_type = IMAGE_TYPES["png"][0]
    elif prefix.startswith(IMAGE_TYPES["webp"][1]) and prefix[8:12] == b"WEBP":
        extension = "webp"
        content_type = IMAGE_TYPES["webp"][0]
    else:
        raise HTTPException(status_code=415, detail="Upload a JPEG, PNG, or WebP image.")

    size = 0
    while chunk := file.file.read(64 * 1024):
        size += len(chunk)
        if size > MAX_IMAGE_BYTES:
            raise HTTPException(status_code=413, detail="Images must be 8 MB or smaller.")
    if size == 0:
        raise HTTPException(status_code=422, detail="The selected image is empty.")
    file.file.seek(0)
    return size, content_type, extension


def _iso(value):
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.isoformat()


@router.get("")
def list_my_images(
    response: Response,
    patient_id: int = Depends(_patient_id),
    db: Session = Depends(get_db),
) -> list[dict]:
    response.headers["Cache-Control"] = "no-store"
    records = (
        db.query(PatientImage)
        .filter(PatientImage.patientID == patient_id)
        .order_by(PatientImage.uploadedAt.desc(), PatientImage.imageID.desc())
        .all()
    )
    try:
        return [
            {
                "imageID": item.imageID,
                "contentType": item.contentType,
                "fileSize": item.fileSize,
                "uploadedAt": _iso(item.uploadedAt),
                "imageUrl": get_patient_image_url(item.objectKey),
            }
            for item in records
        ]
    except Exception as exc:
        logger.exception("Unable to create a temporary URL for a patient image")
        raise HTTPException(status_code=502, detail="Images are temporarily unavailable.") from exc


@router.post("", status_code=status.HTTP_201_CREATED)
def add_my_image(
    response: Response,
    file: UploadFile = File(...),
    patient_id: int = Depends(_patient_id),
    db: Session = Depends(get_db),
) -> dict:
    response.headers["Cache-Control"] = "no-store"
    size, content_type, extension = _inspect_image(file)
    object_key = f"patients/{patient_id}/images/{uuid.uuid4().hex}.{extension}"
    try:
        upload_patient_image(file.file, object_key, content_type)
    except Exception as exc:
        logger.exception("Patient image upload failed")
        raise HTTPException(status_code=502, detail="Image upload failed. Please try again.") from exc

    record = PatientImage(
        patientID=patient_id,
        objectKey=object_key,
        contentType=content_type,
        fileSize=size,
    )
    try:
        db.add(record)
        db.commit()
        db.refresh(record)
    except Exception as exc:
        db.rollback()
        try:
            delete_patient_image(object_key)
        except Exception:
            logger.exception("Could not clean up an uploaded image after its database write failed")
        logger.exception("Patient image metadata could not be saved")
        raise HTTPException(status_code=500, detail="Image metadata could not be saved.") from exc

    return {
        "imageID": record.imageID,
        "contentType": record.contentType,
        "fileSize": record.fileSize,
        "uploadedAt": _iso(record.uploadedAt),
    }


@router.delete("/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_my_image(
    image_id: int,
    patient_id: int = Depends(_patient_id),
    db: Session = Depends(get_db),
) -> None:
    record = (
        db.query(PatientImage)
        .filter(PatientImage.imageID == image_id, PatientImage.patientID == patient_id)
        .first()
    )
    if record is None:
        raise HTTPException(status_code=404, detail="Image not found.")

    object_key = record.objectKey
    db.delete(record)
    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        logger.exception("Patient image metadata could not be deleted")
        raise HTTPException(status_code=500, detail="Image could not be deleted.") from exc

    # Deleting the metadata first makes the image inaccessible through the
    # patient API even if object-store cleanup needs to be retried.
    try:
        delete_patient_image(object_key)
    except Exception as exc:
        logger.exception("Patient image object cleanup failed after metadata deletion")
        raise HTTPException(status_code=502, detail="Image removed from your portal; storage cleanup is pending.") from exc
