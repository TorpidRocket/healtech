function setRole(role, btn){
  document.querySelectorAll('.role-btn').forEach(b=>b.classList.remove('active'));
  btn.classList.add('active');
  console.log("Selected Role:", role);
}

function openModal(){
  document.getElementById('forgotModal').style.display='flex';
}

function closeModal(){
  document.getElementById('forgotModal').style.display='none';
}