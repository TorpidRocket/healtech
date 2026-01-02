let selectedRole = "patient";

function setRole(role, btn) {
  selectedRole = role.toLowerCase();

  document.querySelectorAll(".role-btn").forEach(b => {
    b.classList.remove("active");
  });
  btn.classList.add("active");
}

async function loginUser() {
  const id = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value;

  if (!id || !password) {
    alert("Please enter both ID and password");
    return;
  }

  const endpoint =
    selectedRole === "doctor"
      ? "http://127.0.0.1:5000/api/login/doctor"
      : "http://127.0.0.1:5000/api/login/patient";

  try {
    const response = await fetch(endpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        id: id,
        password: password
      })
    });

    const result = await response.json();

    if (response.ok) {
      alert(`${result.role} login successful`);

      // 🔀 Role-based redirect (placeholder)
      if (result.role === "doctor") {
        window.location.href = "../doctor/dashboard.html";
      } else {
        window.location.href = "../patient/dashboard.html";
      }
    } else {
      alert("Invalid credentials");
    }
  } catch (error) {
    console.error(error);
    alert("Server error. Please try again later.");
  }
}

// async function sendResetLink() {
//   const email = document.querySelector("#forgotModal input").value.trim();

//   if (!email) {
//     alert("Please enter your ID");
//     return;
//   }

//   const endpoint =
//     selectedRole === "doctor"
//       ? "http://127.0.0.1:5000/api/forgot/doctor"
//       : "http://127.0.0.1:5000/api/forgot/patient";

//   try {
//     const res = await fetch(endpoint, {
//       method: "POST",
//       headers: { "Content-Type": "application/json" },
//       body: JSON.stringify({ id: email })
//     });

//     if (res.ok) {
//       alert("Password reset request received.");
//       closeModal();
//     } else {
//       alert("User not found");
//     }
//   } catch {
//     alert("Server error");
//   }
}
