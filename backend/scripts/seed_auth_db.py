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
# Password hashing (SAFE)
# ----------------------------
def hash_password(password: str) -> str:
    """
    Production-safe hashing:
    1. Strip hidden whitespace
    2. SHA-256 pre-hash (avoids bcrypt 72-byte limit)
    3. bcrypt hash
    """
    clean = password.strip()
    sha = hashlib.sha256(clean.encode("utf-8")).hexdigest()
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
        doctor_id = str(row["doctor_id"]).strip()
        password = str(row["password"])

        cur.execute(
            """
            INSERT OR IGNORE INTO doctors (doctor_id, password_hash)
            VALUES (?, ?)
            """,
            (doctor_id, hash_password(password))
        )

# ----------------------------
# Seed patients
# ----------------------------
def seed_patients():
    df = pd.read_csv(PATIENT_CSV)

    for _, row in df.iterrows():
        patient_id = str(row["patient_id"]).strip()
        password = str(row["password"])

        cur.execute(
            """
            INSERT OR IGNORE INTO patients (patient_id, password_hash)
            VALUES (?, ?)
            """,
            (patient_id, hash_password(password))
        )

# ----------------------------
# Run seeding
# ----------------------------
seed_doctors()
seed_patients()

conn.commit()
conn.close()

print("Authentication database created and seeded successfully.")
