// ============================================================
// ZINARA ZOSS - Admin Dashboard (admin.js)
// ============================================================

document.addEventListener('DOMContentLoaded', async function() {
    if (!APP.token) {
        window.location.href = '/login.html';
        return;
    }
    
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
        APP.user = JSON.parse(storedUser);
        if (APP.user.role !== 'admin' && APP.user.role !== 'super_admin') {
            window.location.href = '/dashboard.html';
            showToast('Access denied. Admin only.', 'error');
            return;
        }
    }
    
    await loadAdminData();
});

async function loadAdminData() {
    try {
        showToast('Admin dashboard loaded', 'info');
    } catch (error) {
        console.error('Error loading admin data:', error);
        showToast('Error loading admin data', 'error');
    }
}

function viewUserDetails(userId) {
    showToast(`Viewing user ${userId}`, 'info');
}

function approveApplication(appId) {
    if (confirm('Approve this application?')) {
        showToast(`Application ${appId} approved`, 'success');
    }
}

function rejectApplication(appId) {
    if (confirm('Reject this application?')) {
        showToast(`Application ${appId} rejected`, 'warning');
    }
}

function generateReport() {
    showToast('Generating report...', 'info');
    setTimeout(() => {
        showToast('Report generated successfully!', 'success');
    }, 2000);
}