// forgot.js
let selectedRole = localStorage.getItem("fp_role") || "patient";

document.addEventListener("DOMContentLoaded", () => {
  document.body.classList.add(selectedRole);
});

function applyRoleBackground() {
  const role = localStorage.getItem("fp_role");
  const body = document.body;

  body.classList.remove("doctor", "patient");

  if (role === "doctor") {
    body.classList.add("doctor");
  } else {
    body.classList.add("patient");
  }
}

document.addEventListener("DOMContentLoaded", () => {
  applyRoleBackground();
  applyRoleToggleState();
});


async function requestOTP() {
  const email = document.getElementById("email").value.trim();

  if (!email) {
    alert("Please enter your registered email");
    return;
  }

  // 🔑 Get role from storage
  const role = localStorage.getItem("fp_role") || "patient";

  fetch("http://127.0.0.1:5000/api/forgot/request", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, role })
  })
  .then(res => res.json())
  .then(data => {
    if (data.status === "otp_sent") {
      localStorage.setItem("fp_email", email);
      localStorage.setItem("fp_role", role);

      window.location.href = "otp_verify.html";
    } else {
      document.getElementById("msg").innerText = data.error;
    }
  })
  .catch(err => {
    console.error(err);
    alert("Server error. Please try again.");
  });
}


function applyRoleToggleState() {
  const role = localStorage.getItem("fp_role");

  if (!role) return;

  document.querySelectorAll(".role-btn").forEach(btn => {
    const btnRole = btn.innerText.toLowerCase();
    btn.classList.toggle("active", btnRole === role);
  });
}


function verifyOTP() {
  const otp = document.getElementById("otp").value;
  const email = localStorage.getItem("fp_email");
  const role = localStorage.getItem("fp_role");

  fetch("http://127.0.0.1:5000/api/forgot/verify", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, role, otp })
  })
  .then(res => res.json())
  .then(data => {
    if (data.status === "otp_verified") {
      localStorage.setItem("fp_user_id", data.user_id);
      window.location.href = "reset_password.html";
    } else {
      document.getElementById("msg").innerText = data.error;
    }
  });
}

function resetPassword() {
  const email = localStorage.getItem("fp_email");
  const role = localStorage.getItem("fp_role");

  const new_password = document.getElementById("new_pass").value;
  const confirm_password = document.getElementById("confirm_pass").value;

  fetch("http://127.0.0.1:5000/api/forgot/reset", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      email,
      role,
      new_password,
      confirm_password
    })
  })
  .then(res => res.json())
  .then(data => {
    if (data.status === "password_reset_success") {
      localStorage.clear();
      alert("Password reset successful!");
      window.location.href = "login.html";
    } else {
      document.getElementById("msg").innerText = data.error;
    }
  });
}
async function resendOTP() {
  const email = localStorage.getItem("fp_email");
  const role = localStorage.getItem("fp_role") || "patient";

  if (!email) {
    alert("Missing email. Please start again.");
    window.location.href = "forgot.html";
    return;
  }

  try {
    const response = await fetch(
      "http://127.0.0.1:5000/api/forgot/request",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, role })
      }
    );

    const data = await response.json();

    if (response.ok) {
      document.getElementById("msg").innerText =
        "OTP resent successfully. Please check your email.";
    } else {
      document.getElementById("msg").innerText =
        data.error || "Unable to resend OTP.";
    }
  } catch (err) {
    console.error(err);
    alert("Server error. Please try again later.");
  }
}

function setRole(role, btn) {
  localStorage.setItem("fp_role", role);

  document.querySelectorAll(".role-btn").forEach(b =>
    b.classList.remove("active")
  );
  btn.classList.add("active");

  // update background immediately
  document.body.classList.remove("doctor", "patient");
  document.body.classList.add(role);
}

document.addEventListener("DOMContentLoaded", () => {
  const email = localStorage.getItem("fp_email");
  if (email) {
    document.getElementById("email").value = email;
  }
});