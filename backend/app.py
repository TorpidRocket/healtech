import sqlite3
import hashlib
from flask import Flask, request, jsonify
from flask_cors import CORS
from passlib.hash import bcrypt
from pathlib import Path
import time
import random
# ----------------------------
# App setup
# ----------------------------
app = Flask(__name__)
CORS(app)

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "healtech.db"

# ----------------------------
# Helpers
# ----------------------------
def verify_password(plain_password: str, stored_hash: str) -> bool:
    """
    Verify password using:
    SHA-256 pre-hash → bcrypt verify
    """
    clean = plain_password.strip()
    sha = hashlib.sha256(clean.encode("utf-8")).hexdigest()
    return bcrypt.verify(sha, stored_hash)


def fetch_one(query, params):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(query, params)
    row = cur.fetchone()
    conn.close()
    return row

def hash_otp(otp: str) -> str:
    sha = hashlib.sha256(otp.encode("utf-8")).hexdigest()
    return bcrypt.using(rounds=10).hash(sha)

# ----------------------------
# Routes
# ----------------------------

@app.post("/api/login/doctor")
def doctor_login():
    data = request.get_json()

    doctor_id = data.get("id")
    password = data.get("password")

    if not doctor_id or not password:
        return jsonify({"error": "Missing credentials"}), 400

    row = fetch_one(
        "SELECT password_hash FROM doctors_auth WHERE doctor_id = ?",
        (doctor_id,)
    )

    if row and verify_password(password, row[0]):
        return jsonify({
            "status": "success",
            "role": "doctor"
        }), 200

    return jsonify({"status": "invalid credentials"}), 401


@app.post("/api/login/patient")
def patient_login():
    data = request.get_json()

    patient_id = data.get("id")
    password = data.get("password")

    if not patient_id or not password:
        return jsonify({"error": "Missing credentials"}), 400

    row = fetch_one(
        "SELECT password_hash FROM patients_auth WHERE patient_id = ?",
        (patient_id,)
    )

    if row and verify_password(password, row[0]):
        return jsonify({
            "status": "success",
            "role": "patient"
        }), 200

    return jsonify({"status": "invalid credentials"}), 401

@app.post("/api/forgot/request")
def request_otp():
    data = request.get_json()
    email = data.get("email")
    role = data.get("role")  # 'doctor' or 'patient'

    if not email or role not in ("doctor", "patient"):
        return jsonify({"error": "Invalid request"}), 400

    table = "doctors_auth" if role == "doctor" else "patients_auth"
    id_col = "doctor_id" if role == "doctor" else "patient_id"

    row = fetch_one(
        f"SELECT {id_col} FROM {table} WHERE email = ?",
        (email.strip().lower(),)
    )

    if not row:
        return jsonify({"error": "Account not found"}), 404

    otp = f"{random.randint(100000, 999999)}"
    otp_hash = hash_otp(otp)
    now = int(time.time())
    expires_at = now + 15 * 60

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO password_reset_otps
        (email, role, otp_hash, expires_at, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (email.lower(), role, otp_hash, expires_at, now)
    )
    conn.commit()
    conn.close()

    # PHASE 1: print OTP to console (email later)
    print(f"[OTP] {email} ({role}) → {otp}")

    return jsonify({"status": "otp_sent"}), 200

@app.post("/api/forgot/verify")
def verify_otp():
    data = request.get_json()
    email = data.get("email")
    role = data.get("role")
    otp = data.get("otp")

    if not email or not otp or role not in ("doctor", "patient"):
        return jsonify({"error": "Invalid request"}), 400

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, otp_hash, expires_at
        FROM password_reset_otps
        WHERE email = ? AND role = ? AND used = 0
        ORDER BY created_at DESC
        LIMIT 1
        """,
        (email.lower(), role)
    )

    row = cur.fetchone()

    if not row:
        conn.close()
        return jsonify({"error": "OTP not found"}), 404

    otp_id, otp_hash, expires_at = row

    if int(time.time()) > expires_at:
        conn.close()
        return jsonify({"error": "OTP expired"}), 410

    sha = hashlib.sha256(otp.encode("utf-8")).hexdigest()
    if not bcrypt.verify(sha, otp_hash):
        conn.close()
        return jsonify({"error": "Invalid OTP"}), 401

    # mark OTP as used
    cur.execute(
        "UPDATE password_reset_otps SET used = 1 WHERE id = ?",
        (otp_id,)
    )
    conn.commit()
    conn.close()

    return jsonify({"status": "otp_verified"}), 200

# ----------------------------
# Run
# ----------------------------
if __name__ == "__main__":
    app.run()
