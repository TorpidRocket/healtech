// Sidebar toggle functionality - ONLY triggered by button click
const sidebar = document.getElementById('sidebar');
const toggleBtn = document.getElementById('toggleBtn');

// Toggle sidebar when button is clicked
toggleBtn.addEventListener('click', function(e) {
    e.preventDefault();
    e.stopPropagation();
    sidebar.classList.toggle('collapsed');
    console.log('Sidebar toggled:', sidebar.classList.contains('collapsed'));
});

// Navigation active state based on current page
const navItems = document.querySelectorAll('.nav-item:not(.logout-btn)');
const currentPage = window.location.pathname.split('/').pop() || 'index.html';

navItems.forEach(item => {
    const href = item.getAttribute('href');
    
    // Set active state based on current page
    if (href === currentPage || (currentPage === 'index.html' && href === 'dashboard.html')) {
        item.classList.add('active');
    }
});

// View button functionality
const viewButtons = document.querySelectorAll('.view-btn');
viewButtons.forEach(btn => {
    btn.addEventListener('click', (e) => {
        const row = e.target.closest('tr');
        const fileName = row.querySelector('.file-name').textContent;
        console.log('Viewing file:', fileName);
        alert(`Opening ${fileName}...`);
    });
});