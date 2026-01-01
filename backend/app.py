import sqlite3
import hashlib
from flask import Flask, request, jsonify
from flask_cors import CORS
from passlib.hash import bcrypt
from pathlib import Path

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

# ----------------------------
# Run
# ----------------------------
if __name__ == "__main__":
    app.run()
