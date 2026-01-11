import sqlite3
import hashlib
from flask import Flask, request, jsonify
from flask_cors import CORS
from passlib.hash import bcrypt
from pathlib import Path
import time
import random
import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import re
import random
import string
from datetime import datetime, timedelta
# ----------------------------
# App setup
# ----------------------------
app = Flask(__name__)
CORS(app)

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "healtech.db"

load_dotenv()
MAIL_USER = os.getenv("MAIL_USER")
MAIL_PASS = os.getenv("MAIL_PASS")

PASSWORD_REGEX = r'^[A-Za-z0-9 !#$%&*,-.]{6-20}$'



# ----------------------------
# Helpers
# ----------------------------
def hash_new_password(password: str) -> str:
    clean = password.strip()
    sha = hashlib.sha256(clean.encode("utf-8")).hexdigest()
    return bcrypt.using(rounds=10).hash(sha)

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

# def hash_otp(otp: str) -> str:
#     sha = hashlib.sha256(otp.encode("utf-8")).hexdigest()
#     return bcrypt.using(rounds=10).hash(sha)

def send_otp_email(to_email: str, otp: str):
    msg = EmailMessage()
    msg["Subject"] = "Healtech Password Reset OTP"
    msg["From"] = MAIL_USER
    msg["To"] = to_email

    msg.set_content(
        f"""
Your Healtech OTP is:

{otp}

This OTP is valid for 15 minutes.
If you did not request this, please ignore this email.
"""
    )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as server:
        server.login(MAIL_USER, MAIL_PASS)
        server.send_message(msg)
def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

def hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def generate_next_patient_id(cur):
    cur.execute("""
        SELECT patient_id
        FROM patients_auth
        ORDER BY patient_id DESC
        LIMIT 1
    """)
    row = cur.fetchone()

    if not row:
        return "PAAA001"

    last_id = row[0]          # e.g. PAAA027
    next_num = int(last_id[4:]) + 1
    return f"PAAA{next_num:03d}"

def send_email(to_email: str, subject: str, body: str):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = MAIL_USER
    msg["To"] = to_email
    msg.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as server:
        server.login(MAIL_USER, MAIL_PASS)
        server.send_message(msg)

def send_new_patient_id_email(email, patient_id):
    subject = "Your Healtech Patient ID"
    body = f"""
Welcome to Healtech!

Your Patient ID is:
{patient_id}

You can now log in and start using Healtech.

Regards,
Healtech Team
"""
    send_email(email, subject, body)

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
    # otp_hash = hash_otp(otp)
    otp_hash = hash_text(otp)
    now = int(time.time())
    expires_at = now + 15 * 60

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE password_reset_otps
        SET used = 1
        WHERE email = ? AND role = ? AND used = 0
        """,
        (email, role)
    )
    
    cur.execute(
        """
        INSERT INTO password_reset_otps
        (email, role, otp_hash, expires_at, used, created_at)
        VALUES (?, ?, ?, ?, 0, ?)
        """,
        (email.lower(), role, otp_hash, expires_at, now)
    )
    
    conn.commit()
    conn.close()

    try:
        send_otp_email(email, otp)
    except Exception as e:
        print(f"[EMAIL FAILED] {e}")
        print(f"[OTP] {email} ({role}) → {otp}")
    # Print OTP to console (email later)
    # print(f"[OTP] {email} ({role}) → {otp}")

    return jsonify({"status": "otp_sent"}), 200

@app.post("/api/forgot/verify")
def verify_otp():
    data = request.get_json()
    email = data.get("email")
    role = data.get("role")
    otp = data.get("otp")

    if not email or not otp or role not in ("doctor", "patient"):
        return jsonify({"error": "Invalid request"}), 400

    email = email.strip().lower()

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Fetch latest valid OTP
    cur.execute(
        """
        SELECT id, otp_hash, expires_at
        FROM password_reset_otps
        WHERE email = ? AND role = ? AND used = 0
        ORDER BY created_at DESC
        LIMIT 1
        """,
        (email, role)
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

    # Mark OTP as used
    cur.execute(
        "UPDATE password_reset_otps SET used = 1 WHERE id = ?",
        (otp_id,)
    )

    # 🔥 RETRIEVE USER_ID BASED ON EMAIL + ROLE
    table = "doctors_auth" if role == "doctor" else "patients_auth"
    id_col = "doctor_id" if role == "doctor" else "patient_id"

    cur.execute(
        f"SELECT {id_col} FROM {table} WHERE email = ?",
        (email,)
    )
    user_row = cur.fetchone()

    conn.commit()
    conn.close()

    if not user_row:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "status": "otp_verified",
        "user_id": user_row[0],
        "role": role
    }), 200


@app.post("/api/forgot/reset")
def reset_password():
    data = request.get_json()

    email = data.get("email")
    role = data.get("role")
    new_password = data.get("new_password")
    confirm_password = data.get("confirm_password")

    if not all([email, role, new_password, confirm_password]):
        return jsonify({"error": "Missing fields"}), 400

    if role not in ("doctor", "patient"):
        return jsonify({"error": "Invalid role"}), 400

    if new_password != confirm_password:
        return jsonify({"error": "Passwords do not match"}), 400

    if not re.match(PASSWORD_REGEX, new_password):
        return jsonify({"error": "Password contains invalid characters"}), 400

    email = email.strip().lower()

    table = "doctors_auth" if role == "doctor" else "patients_auth"
    id_col = "doctor_id" if role == "doctor" else "patient_id"

    password_hash = hash_new_password(new_password)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 🔥 RETRIEVE USER_ID AGAIN (AUTHORITATIVE)
    cur.execute(
        f"SELECT {id_col} FROM {table} WHERE email = ?",
        (email,)
    )
    row = cur.fetchone()

    if not row:
        conn.close()
        return jsonify({"error": "User not found"}), 404

    user_id = row[0]

    # Update password
    cur.execute(
        f"""
        UPDATE {table}
        SET password_hash = ?
        WHERE {id_col} = ?
        """,
        (password_hash, user_id)
    )

    conn.commit()
    conn.close()

    return jsonify({
        "status": "password_reset_success",
        "user_id": user_id
    }), 200

@app.post("/api/register/patient/start")
def start_patient_registration():
    data = request.get_json()
    email = data.get("email")

    if not email:
        return jsonify({"error": "Email required"}), 400

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 1️⃣ Check if email already exists
    cur.execute(
        "SELECT 1 FROM patients_auth WHERE email = ?",
        (email,)
    )
    if cur.fetchone():
        conn.close()
        return jsonify({"status": "email_exists"}), 200

    # 2️⃣ Generate OTP
    otp = generate_otp()
    otp_hash = hash_text(otp)
    expiry = datetime.utcnow() + timedelta(minutes=15)

    # 3️⃣ Insert / replace temp registration
    cur.execute("""
        INSERT OR REPLACE INTO patient_registration_temp
        (email, otp_hash, otp_expiry, verified)
        VALUES (?, ?, ?, 0)
    """, (email, otp_hash, expiry))

    conn.commit()
    conn.close()

    # 4️⃣ Send OTP email
    send_otp_email(email, otp)

    return jsonify({"status": "otp_sent"}), 200

@app.post("/api/register/patient/verify-otp")
def verify_patient_registration_otp():
    data = request.get_json()
    email = data.get("email")
    otp = data.get("otp")

    if not email or not otp:
        return jsonify({"error": "Missing data"}), 400

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT otp_hash, otp_expiry
        FROM patient_registration_temp
        WHERE email = ?
    """, (email,))
    row = cur.fetchone()

    if not row:
        conn.close()
        return jsonify({"error": "No registration found"}), 400

    otp_hash, expiry = row

    if datetime.utcnow() > datetime.fromisoformat(expiry):
        conn.close()
        return jsonify({"error": "OTP expired"}), 400

    if hash_text(otp) != otp_hash:
        conn.close()
        return jsonify({"error": "Invalid OTP"}), 400

    cur.execute("""
        UPDATE patient_registration_temp
        SET verified = 1
        WHERE email = ?
    """, (email,))

    conn.commit()
    conn.close()

    return jsonify({"status": "otp_verified"}), 200

@app.post("/api/register/patient/complete")
def complete_patient_registration():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Missing data"}), 400

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 1️⃣ Ensure email is verified
    cur.execute("""
        SELECT verified
        FROM patient_registration_temp
        WHERE email = ?
    """, (email,))
    row = cur.fetchone()

    if not row or row[0] != 1:
        conn.close()
        return jsonify({"error": "Email not verified"}), 400

    # 2️⃣ Generate new patient ID
    patient_id = generate_next_patient_id(cur)

    # # 3️⃣ Hash password (SHA-256 → bcrypt)
    # sha = hashlib.sha256(password.encode("utf-8")).hexdigest()
    # password_hash = bcrypt.hash(sha)
    
    password_hash = hash_new_password(password)

    # 4️⃣ Insert into patients_auth
    cur.execute("""
        INSERT INTO patients_auth (patient_id, email, password_hash)
        VALUES (?, ?, ?)
    """, (patient_id, email, password_hash))

    # 5️⃣ Cleanup temp registration
    cur.execute("""
        DELETE FROM patient_registration_temp
        WHERE email = ?
    """, (email,))

    conn.commit()
    conn.close()

    # 6️⃣ Send ID email
    send_new_patient_id_email(email, patient_id)

    return jsonify({
        "status": "account_created",
        "patient_id": patient_id
    }), 200

# ----------------------------
# Run
# ----------------------------
if __name__ == "__main__":
    app.run()
