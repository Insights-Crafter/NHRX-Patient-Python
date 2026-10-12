# app/core/encryption.py
import os
from typing import Optional

from dotenv import load_dotenv
from cryptography.hazmat.primitives.ciphers.aead import AESSIV

load_dotenv()

# AES-SIV key must be 32, 48 or 64 bytes (64, 96 or 128 hex characters).
_cipher: AESSIV | None = None

_PREFIX = "NHRX-"


def _aad(context: str) -> list[bytes]:
    return [f"{_PREFIX}{context}".encode("utf-8")]


def _get_cipher() -> AESSIV:
    global _cipher
    if _cipher is None:
        key_hex = os.getenv("AES_SIV_KEY")
        if not key_hex:
            raise RuntimeError("AES_SIV_KEY must be configured to encrypt patient data")
        try:
            key = bytes.fromhex(key_hex)
        except ValueError as exc:
            raise RuntimeError("AES_SIV_KEY must be valid hexadecimal") from exc
        _cipher = AESSIV(key)
    return _cipher


def encrypt(value: Optional[str], context: str) -> Optional[str]:
    """Encrypt any string. `context` names the field, e.g. 'nationalID', 'phone'."""
    if value is None:
        return None
    encrypted = _get_cipher().encrypt(str(value).encode("utf-8"), _aad(context))
    return encrypted.hex()


def decrypt(encrypted_value: Optional[str], context: str) -> Optional[str]:
    """Decrypt a value. `context` must be exactly the one used to encrypt it."""
    if encrypted_value is None:
        return None
    decrypted = _get_cipher().decrypt(bytes.fromhex(encrypted_value), _aad(context))
    return decrypted.decode("utf-8")
