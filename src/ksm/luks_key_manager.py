import sqlite3
import os
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from argon2.low_level import hash_secret, Type

DB_FILE = "keys.db"
SALT = b"your_static_salt_32_bytes"  # Replace with a securely stored salt
ARGON2_TIME_COST = 3
ARGON2_MEMORY_COST = 65536
ARGON2_PARALLELISM = 4
KEY_SIZE = 32  # AES-256 requires a 32-byte key


def derive_key(master_password: bytes) -> bytes:
    """Derives a 32-byte encryption key using Argon2id."""
    return hash_secret(
        secret=master_password,
        salt=SALT,
        time_cost=ARGON2_TIME_COST,
        memory_cost=ARGON2_MEMORY_COST,
        parallelism=ARGON2_PARALLELISM,
        hash_len=KEY_SIZE,
        type=Type.ID
    )


def encrypt_data(data: bytes, key: bytes) -> bytes:
    """Encrypts data using AES-256 in GCM mode."""
    iv = os.urandom(12)  # 96-bit IV
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(data) + encryptor.finalize()
    return iv + encryptor.tag + ciphertext


def decrypt_data(encrypted_data: bytes, key: bytes) -> bytes:
    """Decrypts data using AES-256 in GCM mode."""
    iv, tag, ciphertext = encrypted_data[:12], encrypted_data[12:28], encrypted_data[28:]
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend())
    decryptor = cipher.decryptor()
    return decryptor.update(ciphertext) + decryptor.finalize()


def init_db():
    """Initializes the SQLite database to store encrypted LUKS keys."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS luks_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key_name TEXT UNIQUE,
            encrypted_key BLOB
        )
    """)
    conn.commit()
    conn.close()


def store_key(key_name: str, luks_key: bytes, master_password: bytes):
    """Stores an encrypted LUKS key in the database."""
    key = derive_key(master_password)
    encrypted_key = encrypt_data(luks_key, key)

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO luks_keys (key_name, encrypted_key) VALUES (?, ?)",
                   (key_name, encrypted_key))
    conn.commit()
    conn.close()


def retrieve_key(key_name: str, master_password: bytes) -> bytes:
    """Retrieves and decrypts a LUKS key from the database."""
    key = derive_key(master_password)

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT encrypted_key FROM luks_keys WHERE key_name = ?", (key_name,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return decrypt_data(row[0], key)
    else:
        raise ValueError("Key not found!")


if __name__ == "__main__":
    init_db()
    print("Database initialized. Use store_key() and retrieve_key() to manage LUKS keys.")
