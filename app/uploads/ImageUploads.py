import os
from functools import lru_cache

import boto3
from dotenv import load_dotenv

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


def _storage_settings() -> tuple[str, str, str, str]:
    names = ("R2_ENDPOINT", "R2_ACCESS_KEY", "R2_SECRET_KEY", "R2_PATIENT_BUCKET")
    values = tuple(os.getenv(name, "").strip() for name in names)
    missing = [name for name, value in zip(names, values) if not value]
    if missing:
        raise RuntimeError("Missing object storage setting(s): " + ", ".join(missing))
    return values  # type: ignore[return-value]


@lru_cache(maxsize=2)
def _client(endpoint: str, access_key: str, secret_key: str, region: str = "auto"):
    return boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region,
    )


def _storage():
    endpoint, access_key, secret_key, bucket = _storage_settings()
    return _client(endpoint, access_key, secret_key), bucket


def get_patient_image_url(object_key: str) -> str:
    client, bucket = _storage()
    return client.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": bucket,
            "Key": object_key,
        },
        ExpiresIn=300,
    )


def get_report_document_url(object_key: str) -> str:
    client, bucket = _report_storage()
    return client.generate_presigned_url(
        "get_object",
        Params={"Bucket": bucket, "Key": object_key},
        ExpiresIn=300,
    )


def report_document_exists(object_key: str) -> bool:
    client, bucket = _report_storage()
    try:
        client.head_object(Bucket=bucket, Key=object_key)
        return True
    except Exception as exc:
        error = getattr(exc, "response", {}).get("Error", {}).get("Code")
        if error in {"404", "NoSuchKey", "NotFound"}:
            return False
        raise


def _report_storage():
    endpoint = os.getenv("R2_REPORTS_ENDPOINT", "").strip() or os.getenv("R2_ENDPOINT", "").strip()
    access_key = os.getenv("R2_REPORTS_ACCESS_KEY_ID", "").strip() or os.getenv("R2_ACCESS_KEY", "").strip()
    secret_key = os.getenv("R2_REPORTS_SECRET_ACCESS_KEY", "").strip() or os.getenv("R2_SECRET_KEY", "").strip()
    bucket = os.getenv("R2_REPORTS_BUCKET", "").strip() or os.getenv("R2_PATIENT_BUCKET", "").strip()
    region = os.getenv("R2_REPORTS_REGION", "").strip() or "auto"
    missing = [name for name, value in (
        ("R2_REPORTS_ENDPOINT", endpoint),
        ("R2_REPORTS_ACCESS_KEY_ID", access_key),
        ("R2_REPORTS_SECRET_ACCESS_KEY", secret_key),
        ("R2_REPORTS_BUCKET", bucket),
    ) if not value]
    if missing:
        raise RuntimeError("Missing report storage setting(s): " + ", ".join(missing))
    return _client(endpoint, access_key, secret_key, region), bucket


def upload_patient_image(file, object_key: str, content_type: str) -> str:
    client, bucket = _storage()
    client.upload_fileobj(
        file,
        bucket,
        object_key,
        ExtraArgs={"ContentType": content_type},
    )
    return object_key


def upload_patient_document(file, object_key: str, content_type: str) -> str:
    client, bucket = _storage()
    client.upload_fileobj(
        file,
        bucket,
        object_key,
        ExtraArgs={"ContentType": content_type},
    )
    return object_key


def upload_report_document(file, object_key: str, content_type: str) -> str:
    client, bucket = _report_storage()
    client.upload_fileobj(file, bucket, object_key, ExtraArgs={"ContentType": content_type})
    return object_key


def delete_patient_image(object_key: str) -> None:
    client, bucket = _storage()
    client.delete_object(Bucket=bucket, Key=object_key)


def delete_report_document(object_key: str) -> None:
    client, bucket = _report_storage()
    client.delete_object(Bucket=bucket, Key=object_key)



