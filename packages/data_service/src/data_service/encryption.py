"""AES-256-GCM encryption with per-profile key derivation."""

import base64
import hashlib
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class ProfileEncryption:
    """Encrypts/decrypts health data for a single profile.

    Key derived via HKDF from (SECRET_KEY + profile_uuid).
    Each encrypted value: base64(nonce[12] || ciphertext || tag[16]).
    """

    NONCE_LENGTH = 12

    def __init__(self, secret_key: str, profile_uuid: str) -> None:
        self._key = self._derive_key(secret_key, profile_uuid)
        self._aesgcm = AESGCM(self._key)

    @staticmethod
    def _derive_key(secret_key: str, profile_uuid: str) -> bytes:
        material = f"{secret_key}:{profile_uuid}".encode()
        return hashlib.sha256(material).digest()

    def encrypt(self, plaintext: str | float | None) -> str | None:
        if plaintext is None:
            return None
        nonce = os.urandom(self.NONCE_LENGTH)
        data = str(plaintext).encode("utf-8")
        ciphertext = self._aesgcm.encrypt(nonce, data, None)
        return base64.urlsafe_b64encode(nonce + ciphertext).decode("ascii")

    def decrypt(self, encrypted: str | None) -> str | None:
        if encrypted is None:
            return None
        raw = base64.urlsafe_b64decode(encrypted)
        nonce = raw[:self.NONCE_LENGTH]
        ciphertext = raw[self.NONCE_LENGTH:]
        return self._aesgcm.decrypt(nonce, ciphertext, None).decode("utf-8")

    def decrypt_float(self, encrypted: str | None) -> float | None:
        value = self.decrypt(encrypted)
        if value is None:
            return None
        return float(value)
