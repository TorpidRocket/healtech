const documents = [
  { date: "10 Jan 2026", type: "Blood Test", file: "CBC_Report.pdf" },
  { date: "05 Jan 2026", type: "Prescription", file: "Rx_January.png" },
  { date: "28 Dec 2025", type: "Scan", file: "Chest_Xray.jpg" }
];

function toggleSidebar() {
  document.getElementById("sidebar").classList.toggle("collapsed");
  document.getElementById("main-content").classList.toggle("expanded");
}

function switchTab(tab, el) {
  document.querySelectorAll(".sidebar li").forEach(li =>
    li.classList.remove("active")
  );
  el.classList.add("active");

  document.querySelectorAll(".tab-section").forEach(sec =>
    sec.classList.add("hidden")
  );

  document.getElementById(`tab-${tab}`).classList.remove("hidden");
}

document.addEventListener("DOMContentLoaded", () => {
  const tbody = document.getElementById("docs-body");

  documents.forEach(doc => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${doc.date}</td>
      <td>${doc.type}</td>
      <td>${doc.file}</td>
      <td><button class="btn-secondary">View</button></td>
    `;
    tbody.appendChild(tr);
  });
});
