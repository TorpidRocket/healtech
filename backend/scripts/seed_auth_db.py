import sqlite3
import pandas as pd
from passlib.hash import bcrypt
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "healtech.db"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Load schema
with open(BASE_DIR / "schema.sql", "r") as f:
    cur.executescript(f.read())

def seed_doctors():
    df = pd.read_csv(BASE_DIR / "data/doctor_auth.csv")
    for _, row in df.iterrows():
        cur.execute(
            """
            INSERT OR IGNORE INTO doctors (doctor_id, password_hash)
            VALUES (?, ?)
            """,
            (row["doctor_id"], bcrypt.hash(row["password"]))
        )

def seed_patients():
    df = pd.read_csv(BASE_DIR / "data/patient_auth.csv")
    for _, row in df.iterrows():
        cur.execute(
            """
            INSERT OR IGNORE INTO patients (patient_id, password_hash)
            VALUES (?, ?)
            """,
            (row["patient_id"], bcrypt.hash(row["password"]))
        )

seed_doctors()
seed_patients()

conn.commit()
conn.close()

print("Authentication database created and seeded successfully.")
