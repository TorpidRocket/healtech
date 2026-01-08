// single source of truth
let selectedRole = "patient";

function setRole(role, btn) {
  selectedRole = role;

  // store for forgot page
  localStorage.setItem("fp_role", role);

  // toggle UI
  document.querySelectorAll(".role-btn").forEach(b =>
    b.classList.remove("active")
  );
  btn.classList.add("active");

  // apply background on login page too
  document.body.classList.remove("doctor", "patient");
  document.body.classList.add(role);
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
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id, password })
    });

    const result = await response.json();

    if (response.ok) {
      alert(`${selectedRole} login successful`);

      // Placeholder redirects
      if (selectedRole === "doctor") {
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
// function setRole(role, btn) {
//   selectedRole = role;

//   document.querySelectorAll(".role-btn").forEach(b =>
//     b.classList.remove("active")
//   );
//   btn.classList.add("active");

//   // 🔑 ADD THIS
//   document.body.classList.remove("doctor", "patient");
//   document.body.classList.add(role);
// }
