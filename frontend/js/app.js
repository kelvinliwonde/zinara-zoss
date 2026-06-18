// ============================================================
// ZINARA ZOSS - Main Application (app.js)
// Complete with Integration API Methods & Admin Controls
// ============================================================

// ---------- APP STATE ----------
const APP = {
    user: null,
    token: localStorage.getItem('access_token'),
    refreshToken: localStorage.getItem('refresh_token'),
    apiBase: 'http://127.0.0.1:5000/api'
};

// ---------- API WRAPPER ----------
const API = {
    async request(method, endpoint, data = null, auth = true) {
        const url = `${APP.apiBase}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
        };
        
        if (auth && APP.token) {
            headers['Authorization'] = `Bearer ${APP.token}`;
        }
        
        const options = {
            method,
            headers,
            body: data ? JSON.stringify(data) : null
        };
        
        try {
            const response = await fetch(url, options);
            const result = await response.json();
            
            if (response.status === 401) {
                localStorage.removeItem('access_token');
                localStorage.removeItem('refresh_token');
                localStorage.removeItem('user');
                APP.token = null;
                APP.user = null;
                window.location.href = '/login.html';
                throw new Error('Session expired. Please login again.');
            }
            
            if (!response.ok) {
                throw new Error(result.error || 'An error occurred');
            }
            
            return result;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },
    
    // ---------- AUTH ENDPOINTS ----------
    async login(email, password) {
        const result = await this.request('POST', '/auth/login', { email, password }, false);
        if (result.access_token) {
            APP.token = result.access_token;
            APP.refreshToken = result.refresh_token;
            APP.user = result.user;
            localStorage.setItem('access_token', result.access_token);
            localStorage.setItem('refresh_token', result.refresh_token);
            localStorage.setItem('user', JSON.stringify(result.user));
        }
        return result;
    },
    
    async register(data) {
        return this.request('POST', '/auth/register', data, false);
    },
    
    async logout() {
        try {
            await this.request('POST', '/auth/logout');
        } catch {}
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        APP.token = null;
        APP.refreshToken = null;
        APP.user = null;
        window.location.href = '/login.html';
    },
    
    async refreshToken() {
        try {
            const response = await fetch(`${APP.apiBase}/auth/refresh`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${APP.refreshToken}`
                }
            });
            const result = await response.json();
            if (response.ok && result.access_token) {
                APP.token = result.access_token;
                localStorage.setItem('access_token', result.access_token);
                return true;
            }
            return false;
        } catch {
            return false;
        }
    },
    
    // ---------- USER ENDPOINTS ----------
    async getProfile() {
        return this.request('GET', '/user/profile');
    },
    
    async getVehicles() {
        return this.request('GET', '/user/vehicles');
    },
    
    async addVehicle(data) {
        return this.request('POST', '/user/vehicles', data);
    },
    
    async getRadioLicenses() {
        return this.request('GET', '/user/radio-licenses');
    },
    
    async addRadioLicense(data) {
        return this.request('POST', '/user/radio-licenses', data);
    },
    
    // ---------- RENEWAL ENDPOINTS ----------
    async applyRenewal(data) {
        return this.request('POST', '/renewal/apply', data);
    },
    
    async getApplications() {
        return this.request('GET', '/renewal/applications');
    },
    
    async calculateFees(data) {
        return this.request('POST', '/renewal/calculate-fees', data);
    },

    // ---------- INTEGRATION ENDPOINTS (Admin Only) ----------
    async verifyVehicle(registration_number) {
        return this.request('POST', '/integration/verify-vehicle', { registration_number });
    },

    async verifyRadio(radio_serial_number) {
        return this.request('POST', '/integration/verify-radio', { radio_serial_number });
    },

    async submitToZinara(application_id) {
        return this.request('POST', '/integration/submit-application', { application_id });
    },

    async checkZinaraStatus(reference_number) {
        return this.request('GET', `/integration/check-status/${reference_number}`);
    },

    async processZinaraPayment(application_id, payment_method = 'ecocash') {
        return this.request('POST', '/integration/process-payment', { 
            application_id, 
            payment_method 
        });
    },

    async getSystemStatus() {
        return this.request('GET', '/integration/system-status');
    },

    async generateLicense(application_id) {
        return this.request('POST', `/integration/generate-license/${application_id}`);
    }
};

// ---------- TOAST NOTIFICATIONS ----------
function showToast(message, type = 'success') {
    const types = {
        success: 'toast-success',
        error: 'toast-error',
        warning: 'toast-warning',
        info: 'toast-info'
    };
    
    const existingToasts = document.querySelectorAll('.toast');
    existingToasts.forEach(toast => toast.remove());
    
    const toast = document.createElement('div');
    toast.className = `toast ${types[type] || 'toast-info'}`;
    toast.innerHTML = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        if (toast.parentNode) {
            toast.remove();
        }
    }, 4500);
}

// ---------- FORMAT HELPERS ----------
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-ZW', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function formatCurrency(amount) {
    return `$${Number(amount).toFixed(2)}`;
}

function getStatusBadge(status) {
    const classes = {
        'pending': 'badge-pending',
        'verified': 'badge-verified',
        'paid': 'badge-paid',
        'completed': 'badge-completed',
        'rejected': 'badge-rejected'
    };
    return `<span class="badge ${classes[status] || 'badge-pending'}">${status.toUpperCase()}</span>`;
}

// ---------- CHECK AUTH ON PAGE LOAD ----------
document.addEventListener('DOMContentLoaded', function() {
    // Skip auth check for login and register pages
    if (window.location.pathname.includes('login') || 
        window.location.pathname.includes('register')) {
        return;
    }
    
    // Check if user is logged in
    if (!APP.token) {
        window.location.href = '/login.html';
        return;
    }
    
    // Load user data from localStorage
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
        APP.user = JSON.parse(storedUser);
    }
    
    // Show admin-only links if user is admin
    if (APP.user && (APP.user.role === 'admin' || APP.user.role === 'super_admin')) {
        // Show Admin link
        const adminLink = document.getElementById('adminLink');
        if (adminLink) {
            adminLink.style.display = 'inline';
        }
        // Show Integration link (admin only)
        const integrationLink = document.getElementById('integrationLink');
        if (integrationLink) {
            integrationLink.style.display = 'inline';
        }
    } else {
        // Hide Integration link for regular users
        const integrationLink = document.getElementById('integrationLink');
        if (integrationLink) {
            integrationLink.style.display = 'none';
        }
    }
});

// ---------- LOGOUT FUNCTION ----------
function handleLogout() {
    if (confirm('Are you sure you want to logout?')) {
        API.logout();
    }
}

// ---------- EXPOSE TO GLOBAL SCOPE ----------
window.APP = APP;
window.API = API;
window.showToast = showToast;
window.formatDate = formatDate;
window.formatCurrency = formatCurrency;
window.getStatusBadge = getStatusBadge;
window.handleLogout = handleLogout;