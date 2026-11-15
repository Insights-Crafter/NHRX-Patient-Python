"""Doctor uploads and patient-scoped access to private reports and prescriptions."""

import logging
import os
import uuid
from datetime import timezone

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Response, UploadFile, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from appointments.models.AppointmentModel import Appointments
from database.database import get_db
from Patient.models.PatientDocument import PatientDocument
from uploads.ImageUploads import (
    delete_report_document,
    get_report_document_url,
    report_document_exists,
    upload_report_document,
)
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


def _object_prefix(name: str, default: str) -> str:
    """Read a configured R2 key prefix and normalize it for key construction."""
    value = os.getenv(name, default).strip().strip("/")
    if not value:
        value = default.strip("/")
    return f"{value}/"


def _report_prefixes() -> tuple[str, str]:
    return (
        _object_prefix("R2_LAB_REPORTS_PREFIX", "Lab-Reports/"),
        _object_prefix("R2_RADIOLOGY_REPORTS_PREFIX", "Radiology-Reports/"),
    )


def _prescription_prefix() -> str:
    return _object_prefix("R2_PRESCRIPTIONS_PREFIX", "prescriptions/")


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
    object_prefix = _report_prefixes()[0] if document_type == "report" else _prescription_prefix()
    object_key = f"{object_prefix}{appointment.patientID}/{doctor_id}/{uuid.uuid4().hex}.{extension}"
    try:
        upload_report_document(file.file, object_key, content_type)
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
            delete_report_document(object_key)
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
        documents = []
        for item in records:
            lab_prefix, radiology_prefix = _report_prefixes()
            prescription_prefix = _prescription_prefix()
            belongs_to_patient = item.objectKey.startswith(
                (f"{lab_prefix}{patient_id}/", f"{radiology_prefix}{patient_id}/", f"{prescription_prefix}{patient_id}/")
            )
            available = belongs_to_patient and report_document_exists(item.objectKey)
            documents.append({
                "documentID": item.documentID,
                "documentType": item.documentType,
                "fileName": item.fileName,
                "description": item.description,
                "contentType": item.contentType,
                "fileSize": item.fileSize,
                "uploadedAt": _iso(item.uploadedAt),
                "available": available,
                "documentUrl": get_report_document_url(item.objectKey) if available else None,
            })
        bind = db.get_bind()
        inspector = inspect(bind)
        tables = set(inspector.get_table_names())
        if "LabReport" in tables:
            columns = {column["name"] for column in inspector.get_columns("LabReport")}
            required = {"id", "patientID", "fileName", "fileType", "createdAt", "objectKey"}
            if required.issubset(columns):
                rows = db.execute(text('''
                    SELECT id, "fileName", "fileType", "createdAt", "objectKey"
                    FROM "LabReport"
                    WHERE "patientID" = :patient_id AND "objectKey" IS NOT NULL
                    ORDER BY "createdAt" DESC, id DESC
                '''), {"patient_id": patient_id}).mappings()
                for item in rows:
                    object_key = item["objectKey"]
                    lab_prefix, radiology_prefix = _report_prefixes()
                    if not object_key.startswith((f"{lab_prefix}{patient_id}/", f"{radiology_prefix}{patient_id}/")):
                        continue
                    available = report_document_exists(object_key)
                    documents.append({
                        "documentID": f"lab-report-{item['id']}",
                        "documentType": "report",
                        "fileName": item["fileName"],
                        "description": None,
                        "contentType": item["fileType"],
                        "fileSize": None,
                        "uploadedAt": _iso(item["createdAt"]),
                        "available": available,
                        "documentUrl": get_report_document_url(object_key) if available else None,
                    })
        if "MedicalRecords" in tables:
            columns = {column["name"] for column in inspector.get_columns("MedicalRecords")}
            if {"recordID", "patientID", "recordDATE", "prescriptionObjectKey"}.issubset(columns):
                rows = db.execute(text('''
                    SELECT "recordID", "recordDATE", "prescriptionObjectKey"
                    FROM "MedicalRecords"
                    WHERE "patientID" = :patient_id AND "prescriptionObjectKey" IS NOT NULL
                    ORDER BY "recordDATE" DESC, "recordID" DESC
                '''), {"patient_id": patient_id}).mappings()
                for item in rows:
                    object_key = item["prescriptionObjectKey"]
                    if not object_key.startswith(f"{_prescription_prefix()}{patient_id}/"):
                        continue
                    available = report_document_exists(object_key)
                    documents.append({
                        "documentID": f"prescription-{item['recordID']}",
                        "documentType": "prescription",
                        "fileName": f"Prescription - {item['recordDATE'].date().isoformat() if item['recordDATE'] else 'Medical record'}",
                        "description": None,
                        "contentType": "application/pdf",
                        "fileSize": None,
                        "uploadedAt": _iso(item["recordDATE"]),
                        "available": available,
                        "documentUrl": get_report_document_url(object_key) if available else None,
                    })
        if document_type:
            documents = [item for item in documents if item["documentType"] == document_type]
        documents.sort(key=lambda item: item["uploadedAt"] or "", reverse=True)
        return documents
    except Exception as exc:
        logger.exception("Unable to create temporary URLs for patient documents")
        raise HTTPException(status_code=502, detail="Documents are temporarily unavailable.") from exc
