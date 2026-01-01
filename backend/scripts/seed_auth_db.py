import sqlite3
import pandas as pd
import hashlib
import time
from passlib.hash import bcrypt
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "healtech.db"
SCHEMA_PATH = BASE_DIR / "schema.sql"
DATA_DIR = BASE_DIR / "data"

DOCTOR_CSV = DATA_DIR / "doctor_auth.csv"
PATIENT_CSV = DATA_DIR / "patient_auth.csv"

def hash_password(password: str) -> str:
    clean = password.strip()
    sha = hashlib.sha256(clean.encode("utf-8")).hexdigest()
    return bcrypt.using(rounds=10).hash(sha)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Load schema
with open(SCHEMA_PATH, "r") as f:
    cur.executescript(f.read())

now = int(time.time())

def seed_doctors():
    df = pd.read_csv(DOCTOR_CSV)
    for _, row in df.iterrows():
        cur.execute(
            """
            INSERT INTO doctors_auth
            (doctor_id, email, password_hash, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (
                row["doctor_id"].strip(),
                row["email_id"].strip().lower(),
                hash_password(row["password"]),
                now
            )
        )

def seed_patients():
    df = pd.read_csv(PATIENT_CSV)
    for _, row in df.iterrows():
        cur.execute(
            """
            INSERT INTO patients_auth
            (patient_id, email, password_hash, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (
                row["patient_id"].strip(),
                row["email_id"].strip().lower(),
                hash_password(row["password"]),
                now
            )
        )

seed_doctors()
seed_patients()

conn.commit()
conn.close()

print("Phase 0: auth database rebuilt and seeded successfully.")
