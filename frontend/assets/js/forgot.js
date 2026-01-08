/*************************************************
 * Healtech Forgot Password Flow (forgot.js)
 *************************************************/

/* ---------- Shared State ---------- */
let selectedRole = localStorage.getItem("fp_role") || "patient";

/* ---------- On Page Load ---------- */
document.addEventListener("DOMContentLoaded", () => {
  // Apply role-based background
  document.body.classList.remove("doctor", "patient");
  document.body.classList.add(selectedRole);

  // Autofill email if present (OTP & reset pages)
  const email = localStorage.getItem("fp_email");
  const emailInput = document.getElementById("email");
  if (email && emailInput) {
    emailInput.value = email;
  }

  // Apply toggle active state if toggle exists
  if (document.querySelector(".role-btn")) {
    applyRoleToggleState();
  }
});

/* ---------- UI Helpers ---------- */
function applyRoleToggleState() {
  const role = localStorage.getItem("fp_role");
  if (!role) return;

  document.querySelectorAll(".role-btn").forEach(btn => {
    const btnRole = btn.innerText.toLowerCase();
    btn.classList.toggle("active", btnRole === role);
  });
}
function startResendCooldown(seconds = 60) {
  const btn = document.getElementById("resend-btn");
  if (!btn) return;

  let remaining = seconds;
  btn.disabled = true;
  btn.style.opacity = "0.6";
  btn.innerText = `Resend (${remaining}s)`;

  const timer = setInterval(() => {
    remaining--;
    btn.innerText = `Resend (${remaining}s)`;

    if (remaining <= 0) {
      clearInterval(timer);
      btn.disabled = false;
      btn.style.opacity = "1";
      btn.innerText = "Resend OTP";
    }
  }, 1000);
}

function setRole(role, btn) {
  selectedRole = role;
  localStorage.setItem("fp_role", role);

  document.querySelectorAll(".role-btn").forEach(b =>
    b.classList.remove("active")
  );
  btn.classList.add("active");

  document.body.classList.remove("doctor", "patient");
  document.body.classList.add(role);
}

let statusTimeout = null;

function showStatus(message, type = "info") {
  const el = document.getElementById("status-msg");
  if (!el) return;

  el.innerText = message;
  el.style.display = "block";

  if (type === "success") {
    el.style.color = "#059669";
  } else if (type === "error") {
    el.style.color = "#dc2626";
  } else {
    el.style.color = "#6b7280";
  }

  // 🔁 Clear any previous timer
  if (statusTimeout) {
    clearTimeout(statusTimeout);
  }

  // ⏳ Hide after 30 seconds
  statusTimeout = setTimeout(() => {
    el.style.display = "none";
    el.innerText = "";
  }, 30000);
}

/* ---------- STEP 1: Request OTP ---------- */
async function requestOTP() {
  const email = document.getElementById("email").value.trim();
  const role = localStorage.getItem("fp_role") || "patient";

  if (!email) {
    showStatus("Please enter your registered email.", "error");
    return;
  }

  try {
    const res = await fetch("http://127.0.0.1:5000/api/forgot/request", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, role })
    });

    const data = await res.json();

    if (res.ok && data.status === "otp_sent") {
      localStorage.setItem("fp_email", email);
      localStorage.setItem("fp_role", role);
      window.location.href = "otp_verify.html";
    } else {
      showStatus(data.error || "Unable to send OTP.", "error");
    }
  } catch (err) {
    console.error(err);
    showStatus("Server error. Please try again later.", "error");
  }
}

/* ---------- STEP 2: Verify OTP ---------- */
async function verifyOTP() {
  const otp = document.getElementById("otp").value.trim();
  const email = localStorage.getItem("fp_email");
  const role = localStorage.getItem("fp_role");

  if (!otp) {
    showStatus("Please enter the OTP.", "error");
    return;
  }

  try {
    const res = await fetch("http://127.0.0.1:5000/api/forgot/verify", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, role, otp })
    });

    const data = await res.json();

    if (res.ok && data.status === "otp_verified") {
      localStorage.setItem("fp_user_id", data.user_id);
      showStatus("OTP verified successfully.", "success");
      setTimeout(() => {
        window.location.href = "reset_password.html";
      }, 800);
    } else {
      showStatus(data.error || "Invalid OTP.", "error");
    }
  } catch (err) {
    console.error(err);
    showStatus("Server error. Please try again.", "error");
  }
}

/* ---------- STEP 2b: Resend OTP ---------- */
async function resendOTP() {
  const email = localStorage.getItem("fp_email");
  const role = localStorage.getItem("fp_role") || "patient";

  if (!email) {
    window.location.href = "forgot.html";
    return;
  }

  try {
    const res = await fetch("http://127.0.0.1:5000/api/forgot/request", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, role })
    });

    const data = await res.json();

    if (res.ok) {
      showStatus("OTP resent successfully. Please check your email.", "success");
      startResendCooldown(60);
    } else {
      showStatus(data.error || "Unable to resend OTP.", "error");
    }
  } catch (err) {
    console.error(err);
    showStatus("Server error. Please try again.", "error");
  }
}

/* ---------- STEP 3: Reset Password ---------- */
async function resetPassword() {
  const email = localStorage.getItem("fp_email");
  const role = localStorage.getItem("fp_role");
  const new_password = document.getElementById("new_pass").value;
  const confirm_password = document.getElementById("confirm_pass").value;

  if (!new_password || !confirm_password) {
    showStatus("Please fill in all fields.", "error");
    return;
  }

  try {
    const res = await fetch("http://127.0.0.1:5000/api/forgot/reset", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email,
        role,
        new_password,
        confirm_password
      })
    });

    const data = await res.json();

    if (res.ok && data.status === "password_reset_success") {
      showStatus("Password reset successful. Redirecting to login...", "success");
      setTimeout(() => {
        localStorage.clear();
        window.location.href = "login.html";
      }, 1500);
    } else {
      showStatus(data.error || "Password reset failed.", "error");
    }
  } catch (err) {
    console.error(err);
    showStatus("Server error. Please try again.", "error");
  }
}
