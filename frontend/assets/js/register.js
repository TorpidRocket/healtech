/* ======================================================
   Healtech – Patient Registration Frontend Logic
   ====================================================== */

/* -------------------------------
   Utility: status message
-------------------------------- */
function showStatus(message, type = "info") {
  const el = document.getElementById("status-msg");
  if (!el) return;

  el.innerText = message;
  el.style.display = "block";

  if (type === "success") el.style.color = "#059669";
  else if (type === "error") el.style.color = "#dc2626";
  else el.style.color = "#6b7280";
}

/* -------------------------------
   STEP 1: Start Registration
   register_email.html
-------------------------------- */
async function startRegistration() {
  const email = document.getElementById("email").value.trim();

  if (!email) {
    showStatus("Please enter your email address", "error");
    return;
  }

  try {
    const res = await fetch(
      "http://127.0.0.1:5000/api/register/patient/start",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email })
      }
    );

    const data = await res.json();

    if (data.status === "email_exists") {
      showStatus(
        "Email already exists. Redirecting to Forgot Password...",
        "error"
      );

      setTimeout(() => {
        window.location.href = "forgot.html";
      }, 10000);
      return;
    }

    if (data.status === "otp_sent") {
      // ✅ Save ONLY after success
      localStorage.setItem("reg_email", email);
      localStorage.setItem(
        "reg_expiry",
        Date.now() + 30 * 60 * 1000
      );

      window.location.href = "register_otp.html";
      return;
    }

    showStatus("Unexpected error. Try again.", "error");

  } catch (err) {
    console.error(err);
    showStatus("Server error. Please try again later.", "error");
  }
}

/* -------------------------------
   STEP 2: Verify OTP
   register_otp.html
-------------------------------- */
async function verifyRegistrationOTP() {
  const otp = document.getElementById("otp").value.trim();
  const email = localStorage.getItem("reg_email");

  if (!otp || otp.length !== 6) {
    showStatus("Enter a valid 6-digit OTP", "error");
    return;
  }

  try {
    const res = await fetch(
      "http://127.0.0.1:5000/api/register/patient/verify-otp",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, otp })
      }
    );

    const data = await res.json();

    if (data.status === "otp_verified") {
      localStorage.setItem("reg_otp_verified", "true");
      window.location.href = "register_done.html";
      return;
    }

    showStatus(data.error || "Invalid OTP", "error");

  } catch (err) {
    console.error(err);
    showStatus("Server error. Please try again.", "error");
  }
}

/* -------------------------------
   STEP 3: Complete Registration
   register_done.html
-------------------------------- */
async function completeRegistration() {
  const password = document.getElementById("new_pass").value;
  const confirm = document.getElementById("confirm_pass").value;
  const email = localStorage.getItem("reg_email");

  if (!password || !confirm) {
    showStatus("Please fill both password fields", "error");
    return;
  }

  if (password !== confirm) {
    showStatus("Passwords do not match", "error");
    return;
  }

  const PASSWORD_REGEX = /^[A-Za-z0-9 !#$%&*,-.]{6,20}$/;
  if (!PASSWORD_REGEX.test(password)) {
    showStatus(
      "Password must be 6–20 characters and contain only allowed symbols",
      "error"
    );
    return;
  }

  try {
    const res = await fetch(
      "http://127.0.0.1:5000/api/register/patient/complete",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
      }
    );

    const data = await res.json();

    if (data.status === "account_created") {
      showStatus(
        "Account created successfully! Patient ID sent to email. Redirecting to login...",
        "success"
      );

      // ✅ Clean only registration data
      localStorage.removeItem("reg_email");
      localStorage.removeItem("reg_expiry");
      localStorage.removeItem("reg_otp_verified");

      setTimeout(() => {
        window.location.href = "login.html";
      }, 2000);
      return;
    }

    showStatus(data.error || "Registration failed", "error");

  } catch (err) {
    console.error(err);
    showStatus("Server error. Please try again.", "error");
  }
}

/* -------------------------------
   PAGE GUARD + EMAIL AUTOFILL
   (runs on all pages safely)
-------------------------------- */
document.addEventListener("DOMContentLoaded", () => {
  const email = localStorage.getItem("reg_email");
  const otpVerified = localStorage.getItem("reg_otp_verified");
  const path = window.location.pathname;

  // Guard ONLY OTP page
  if (path.includes("register_otp") && !email) {
    alert("Session expired. Please start again.");
    window.location.href = "register_email.html";
    return;
  }

  // Guard DONE page ONLY if OTP not verified
  if (path.includes("register_done") && otpVerified !== "true") {
    alert("OTP not verified.");
    window.location.href = "register_email.html";
    return;
  }

  // Autofill email if field exists
  const emailInput = document.getElementById("email");
  if (emailInput && email) {
    emailInput.value = email;
  }
});

function togglePassword(inputId, toggleEl) {
  const input = document.getElementById(inputId);
  if (!input) return;

  if (input.type === "password") {
    input.type = "text";
    toggleEl.innerText = "-_-";
  } else {
    input.type = "password";
    toggleEl.innerText = "👀";
  }
}