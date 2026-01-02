function requestOTP() {
  const email = document.getElementById("email").value;
  const role = document.getElementById("role").value;

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
