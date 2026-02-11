from cryptography.fernet import Fernet
import base64
import os
import hashlib

def get_fernet():
    """Get Fernet instance for encryption/decryption"""
    raw_key = os.getenv("FILE_ENCRYPTION_KEY")
    if not raw_key:
        raise RuntimeError("FILE_ENCRYPTION_KEY is not set in .env")
    
    # Derive 32-byte key from environment variable
    key = hashlib.sha256(raw_key.encode()).digest()
    key_base64 = base64.urlsafe_b64encode(key)
    return Fernet(key_base64)

def encrypt_bytes(data: bytes) -> bytes:
    """Encrypt binary data"""
    return get_fernet().encrypt(data)

def decrypt_bytes(data: bytes) -> bytes:
    """Decrypt binary data"""
    return get_fernet().decrypt(data)