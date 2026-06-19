// ============================================================
// ZINARA ZOSS — frontend/js/app.js
// ============================================================

const APP = {
    // ── Your live Render URL ──────────────────────────────────
    BASE_URL: 'https://zinaraz-zoss.onrender.com',

    get token()  { return localStorage.getItem('zoss_token'); },
    set token(v) { v ? localStorage.setItem('zoss_token', v) : localStorage.removeItem('zoss_token'); },

    get user() {
        const raw = localStorage.getItem('zoss_user');
        try { return raw ? JSON.parse(raw) : null; } catch { return null; }
    },
    set user(v) {
        v ? localStorage.setItem('zoss_user', JSON.stringify(v))
          : localStorage.removeItem('zoss_user');
    },
};

// ── Demo data (used when backend returns nothing / not logged in yet) ─
const DEMO = {
    user: {
        id: 'u001', name: 'Anesu Mhaka',
        email: 'anesu.mhaka1@gmail.com',
        role: 'admin', initials: 'AM',
    },
    vehicles: [
        { registration: 'ABC 1234', make: 'Toyota', model: 'Hilux', year: 2020, color: 'White',  status: 'active'  },
        { registration: 'XYZ 5678', make: 'Honda',  model: 'Fit',   year: 2018, color: 'Silver', status: 'expired' },
    ],
    applications: [
        { id: 'APP-001', user: 'Anesu Mhaka',    type: 'Vehicle', amount: 50, status: 'pending',   date: '2026-06-18' },
        { id: 'APP-002', user: 'Tendai Moyo',    type: 'Radio',   amount: 20, status: 'verified',  date: '2026-06-17' },
        { id: 'APP-003', user: 'Rudo Chikwanda', type: 'Both',    amount: 70, status: 'paid',      date: '2026-06-15' },
        { id: 'APP-004', user: 'Farai Dube',     type: 'Vehicle', amount: 50, status: 'completed', date: '2026-06-10' },
        { id: 'APP-005', user: 'Nyasha Banda',   type: 'Radio',   amount: 20, status: 'rejected',  date: '2026-06-08' },
    ],
    spending: { labels: ['Jan','Feb','Mar','Apr','May','Jun'], data: [0,50,50,0,70,0] },
};

// ── API helpers ───────────────────────────────────────────────
async function apiGet(path) {
    try {
        const res = await fetch(APP.BASE_URL + path, {
            headers: { 'Authorization': 'Bearer ' + APP.token }
        });
        if (res.status === 401) { handleLogout(); return null; }
        if (!res.ok) throw new Error(res.statusText);
        return res.json();
    } catch (e) {
        console.warn('API GET failed, using demo data.', path, e);
        return null;
    }
}

async function apiPost(path, body) {
    try {
        const res = await fetch(APP.BASE_URL + path, {
            method: 'POST',
            headers: {
                'Content-Type':  'application/json',
                'Authorization': 'Bearer ' + APP.token,
            },
            body: JSON.stringify(body),
        });
        const data = await res.json();
        if (!res.ok) throw { status: res.status, ...data };
        return data;
    } catch (e) {
        console.error('API POST failed.', path, e);
        throw e;
    }
}

// ── Toast ─────────────────────────────────────────────────────
function showToast(message, type = 'info') {
    let container = document.getElementById('toastContainer');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container';
        document.body.appendChild(container);
    }
    const icons = {
        success: '<i class="fas fa-check-circle" style="color:var(--green)"></i>',
        error:   '<i class="fas fa-times-circle" style="color:#ef4444"></i>',
        warning: '<i class="fas fa-exclamation-triangle" style="color:var(--gold)"></i>',
        info:    '<i class="fas fa-info-circle" style="color:var(--blue)"></i>',
    };
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `${icons[type] || icons.info} <span>${message}</span>`;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 4600);
}

// ── Auth ──────────────────────────────────────────────────────
function handleLogout() {
    APP.token = null;
    APP.user  = null;
    window.location.href = '/login.html';
}

// ── Status badge ──────────────────────────────────────────────
function statusBadge(status) {
    const map = {
        pending:   'badge-pending',
        verified:  'badge-verified',
        paid:      'badge-paid',
        completed: 'badge-completed',
        rejected:  'badge-rejected',
        active:    'badge-paid',
        expired:   'badge-rejected',
    };
    return `<span class="badge ${map[status] || 'badge-pending'}">${status}</span>`;
}

// ── Sidebar role UI ───────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    const user = APP.user;
    if (!user) return;

    const setEl   = (id, v) => { const e = document.getElementById(id); if (e) e.textContent = v; };

    setEl('userName',      user.name);
    setEl('userNameShort', user.name);
    setEl('userEmail',     user.email);
    setEl('userRole',      (user.role || '').replace('_', ' '));
    setEl('userAvatar',    user.initials || (user.name || 'U').split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase());

    if (user.role === 'admin' || user.role === 'super_admin') {
        ['adminLabel', 'integrationLink', 'adminLink'].forEach(id => {
            const el = document.getElementById(id);
            if (el) el.style.display = '';
        });
    }
});
