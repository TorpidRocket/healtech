-- Doctors
CREATE TABLE IF NOT EXISTS doctors_auth (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    doctor_id TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at INTEGER NOT NULL
);

-- Patients
CREATE TABLE IF NOT EXISTS patients_auth (
  patient_id TEXT PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- OTP table for password reset
CREATE TABLE IF NOT EXISTS password_reset_otps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    role TEXT NOT NULL,              -- 'doctor' or 'patient'
    otp_hash TEXT NOT NULL,
    expires_at INTEGER NOT NULL,
    used INTEGER DEFAULT 0,
    created_at INTEGER NOT NULL
);
-- Temporary registration table
CREATE TABLE IF NOT EXISTS patient_registration_temp (
  email TEXT PRIMARY KEY,
  otp_hash TEXT NOT NULL,
  otp_expiry DATETIME NOT NULL,
  verified INTEGER DEFAULT 0,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- Documents uploaded by patients
-- =====================================================
CREATE TABLE IF NOT EXISTS documents (
  document_id     INTEGER PRIMARY KEY AUTOINCREMENT,
  patient_id      TEXT NOT NULL,
  file_name       TEXT NOT NULL,
  document_type   TEXT NOT NULL,        -- blood_test, prescription, scan, etc.
  storage_path    TEXT NOT NULL,        -- local path OR cloud URL
  uploaded_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

  FOREIGN KEY (patient_id)
    REFERENCES patients_auth(patient_id)
    ON DELETE CASCADE
);

-- =====================================================
-- Doctor access control for documents (privacy layer)
-- =====================================================
CREATE TABLE IF NOT EXISTS document_access (
  id              INTEGER PRIMARY KEY AUTOINCREMENT,
  document_id     INTEGER NOT NULL,
  doctor_id       TEXT NOT NULL,
  can_view        INTEGER NOT NULL DEFAULT 0,  -- 0 = no, 1 = yes
  granted_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

  FOREIGN KEY (document_id)
    REFERENCES documents(document_id)
    ON DELETE CASCADE,

  FOREIGN KEY (doctor_id)
    REFERENCES doctors_auth(doctor_id)
    ON DELETE CASCADE,

  UNIQUE (document_id, doctor_id)
);

