"""Doctor uploads and patient-scoped access to private reports and prescriptions."""

import logging
import uuid
from datetime import timezone

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Response, UploadFile, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from appointments.models.AppointmentModel import Appointments
from database.database import get_db
from Patient.models.PatientDocument import PatientDocument
from uploads.ImageUploads import delete_patient_image, get_patient_image_url, upload_patient_document
from utilityfunctions.reusable_functions import extract_doctor_id, extract_patient_id

logger = logging.getLogger(__name__)
patient_router = APIRouter(prefix="/patients/me/documents", tags=["patient documents"])
doctor_router = APIRouter(prefix="/doctors/me/appointments", tags=["doctor documents"])
bearer_scheme = HTTPBearer(auto_error=False)
MAX_DOCUMENT_BYTES = 20 * 1024 * 1024
DOCUMENT_SIGNATURES = {
    "pdf": ("application/pdf", b"%PDF-"),
    "jpg": ("image/jpeg", b"\xff\xd8\xff"),
    "png": ("image/png", b"\x89PNG\r\n\x1a\n"),
    "webp": ("image/webp", b"RIFF"),
}


def _doctor_id(credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme)) -> int:
    return extract_doctor_id(credentials)


def _patient_id(credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme)) -> int:
    return extract_patient_id(credentials)


def _inspect_document(file: UploadFile) -> tuple[int, str, str]:
    file.file.seek(0)
    prefix = file.file.read(12)
    file.file.seek(0)
    if prefix.startswith(DOCUMENT_SIGNATURES["pdf"][1]):
        extension = "pdf"
    elif prefix.startswith(DOCUMENT_SIGNATURES["jpg"][1]):
        extension = "jpg"
    elif prefix.startswith(DOCUMENT_SIGNATURES["png"][1]):
        extension = "png"
    elif prefix.startswith(DOCUMENT_SIGNATURES["webp"][1]) and prefix[8:12] == b"WEBP":
        extension = "webp"
    else:
        raise HTTPException(status_code=415, detail="Upload a PDF, JPEG, PNG, or WebP file.")

    size = 0
    while chunk := file.file.read(64 * 1024):
        size += len(chunk)
        if size > MAX_DOCUMENT_BYTES:
            raise HTTPException(status_code=413, detail="Files must be 20 MB or smaller.")
    if not size:
        raise HTTPException(status_code=422, detail="The selected file is empty.")
    file.file.seek(0)
    return size, DOCUMENT_SIGNATURES[extension][0], extension


def _iso(value):
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.isoformat()


@doctor_router.post("/{appointment_id}/documents", status_code=status.HTTP_201_CREATED)
def upload_appointment_document(
    appointment_id: int,
    response: Response,
    document_type: str = Form(..., alias="documentType"),
    description: str | None = Form(default=None, max_length=1000),
    file: UploadFile = File(...),
    doctor_id: int = Depends(_doctor_id),
    db: Session = Depends(get_db),
) -> dict:
    response.headers["Cache-Control"] = "no-store"
    document_type = document_type.strip().lower()
    if document_type not in {"report", "prescription"}:
        raise HTTPException(status_code=422, detail="documentType must be report or prescription.")

    appointment = (
        db.query(Appointments)
        .filter(Appointments.AppointmentID == appointment_id, Appointments.DoctorID == doctor_id)
        .first()
    )
    if appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found for this doctor.")

    size, content_type, extension = _inspect_document(file)
    submitted_name = (file.filename or "document").replace("\\", "/").rsplit("/", 1)[-1]
    safe_name = submitted_name.strip()[:255] or f"{document_type}.{extension}"
    object_key = f"patients/{appointment.patientID}/documents/{uuid.uuid4().hex}.{extension}"
    try:
        upload_patient_document(file.file, object_key, content_type)
    except Exception as exc:
        logger.exception("Doctor document upload failed")
        raise HTTPException(status_code=502, detail="Document upload failed. Please try again.") from exc

    record = PatientDocument(
        patientID=appointment.patientID,
        doctorID=doctor_id,
        appointmentID=appointment_id,
        documentType=document_type,
        fileName=safe_name,
        description=(description or "").strip() or None,
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
            logger.exception("Failed to clean up an unreferenced document object")
        logger.exception("Document metadata could not be saved")
        raise HTTPException(status_code=500, detail="Document metadata could not be saved.") from exc

    return {
        "documentID": record.documentID,
        "documentType": record.documentType,
        "fileName": record.fileName,
        "uploadedAt": _iso(record.uploadedAt),
    }


@patient_router.get("")
def list_my_documents(
    response: Response,
    document_type: str | None = Query(default=None, alias="type"),
    patient_id: int = Depends(_patient_id),
    db: Session = Depends(get_db),
) -> list[dict]:
    response.headers["Cache-Control"] = "no-store"
    if document_type is not None and document_type not in {"report", "prescription"}:
        raise HTTPException(status_code=422, detail="type must be report or prescription.")
    query = db.query(PatientDocument).filter(PatientDocument.patientID == patient_id)
    if document_type:
        query = query.filter(PatientDocument.documentType == document_type)
    records = query.order_by(PatientDocument.uploadedAt.desc(), PatientDocument.documentID.desc()).all()
    try:
        return [
            {
                "documentID": item.documentID,
                "documentType": item.documentType,
                "fileName": item.fileName,
                "description": item.description,
                "contentType": item.contentType,
                "fileSize": item.fileSize,
                "uploadedAt": _iso(item.uploadedAt),
                "documentUrl": get_patient_image_url(item.objectKey),
            }
            for item in records
        ]
    except Exception as exc:
        logger.exception("Unable to create temporary URLs for patient documents")
        raise HTTPException(status_code=502, detail="Documents are temporarily unavailable.") from exc
