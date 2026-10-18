"""Field-aware encryption for protected patient data."""

import os
from typing import Optional

from cryptography.hazmat.primitives.ciphers.aead import AESSIV
from dotenv import load_dotenv

load_dotenv()


class EncryptionService:
    """Encrypt and decrypt values using field names as associated data."""

    _PREFIX = "NHRX-"

    def __init__(self) -> None:
        self._cipher: AESSIV | None = None

    def _get_cipher(self) -> AESSIV:
        if self._cipher is None:
            key_hex = os.getenv("AES_SIV_KEY")
            if not key_hex:
                raise RuntimeError(
                    "AES_SIV_KEY must be configured to encrypt patient data"
                )
            try:
                key = bytes.fromhex(key_hex)
            except ValueError as exc:
                raise RuntimeError("AES_SIV_KEY must be valid hexadecimal") from exc
            self._cipher = AESSIV(key)
        return self._cipher

    def _aad(self, context: str) -> list[bytes]:
        return [f"{self._PREFIX}{context}".encode("utf-8")]

    def encrypt(self, value: Optional[str], context: str) -> Optional[str]:
        """Encrypt a string; context names its field, such as 'phone'."""
        if value is None:
            return None
        encrypted = self._get_cipher().encrypt(
            str(value).encode("utf-8"), self._aad(context)
        )
        return encrypted.hex()

    def decrypt(self, encrypted_value: Optional[str], context: str) -> Optional[str]:
        """Decrypt a value using the same context used during encryption."""
        if encrypted_value is None:
            return None
        decrypted = self._get_cipher().decrypt(
            bytes.fromhex(encrypted_value), self._aad(context)
        )
        return decrypted.decode("utf-8")
