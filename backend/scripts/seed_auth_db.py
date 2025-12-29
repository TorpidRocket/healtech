import sqlite3
import pandas as pd
import hashlib
from passlib.hash import bcrypt
from pathlib import Path

# ----------------------------
# Paths
# ----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "healtech.db"
SCHEMA_PATH = BASE_DIR / "schema.sql"
DATA_DIR = BASE_DIR / "data"

DOCTOR_CSV = DATA_DIR / "doctor_auth.csv"
PATIENT_CSV = DATA_DIR / "patient_auth.csv"

# ----------------------------
# Helper: hash password safely
# ----------------------------
def hash_password(plain_password: str) -> str:
    """
    Real-world safe hashing:
    1. SHA-256 pre-hash (avoids bcrypt 72-byte limit)
    2. bcrypt hash (slow + secure)
    """
    sha = hashlib.sha256(plain_password.encode("utf-8")).hexdigest()
    return bcrypt.hash(sha)

# ----------------------------
# Database setup
# ----------------------------
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Load schema
with open(SCHEMA_PATH, "r") as f:
    cur.executescript(f.read())

# ----------------------------
# Seed doctors
# ----------------------------
def seed_doctors():
    df = pd.read_csv(DOCTOR_CSV)

    for _, row in df.iterrows():
        password_hash = hash_password(row["password"])

        cur.execute(
            """
            INSERT OR IGNORE INTO doctors (doctor_id, password_hash)
            VALUES (?, ?)
            """,
            (row["doctor_id"], password_hash)
        )

# ----------------------------
# Seed patients
# ----------------------------
def seed_patients():
    df = pd.read_csv(PATIENT_CSV)

    for _, row in df.iterrows():
        password_hash = hash_password(row["password"])

        cur.execute(
            """
            INSERT OR IGNORE INTO patients (patient_id, password_hash)
            VALUES (?, ?)
            """,
            (row["patient_id"], password_hash)
        )

# ----------------------------
# Run seeding
# ----------------------------
seed_doctors()
seed_patients()

conn.commit()
conn.close()

print("Authentication database created and seeded successfully.")
