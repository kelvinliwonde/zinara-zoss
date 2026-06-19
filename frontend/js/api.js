// ============================================================
// ZINARA ZOSS — frontend/js/api.js
// Defines the API object used by auth.js, dashboard.js, admin.js, etc.
// Must be loaded AFTER app.js (depends on APP.BASE_URL / APP.token / APP.user)
// ============================================================

const API = {

    // Low-level request helper — talks to the Flask backend
    async _request(path, { method = 'GET', body = null, auth = false } = {}) {
        const headers = { 'Content-Type': 'application/json' };
        if (auth && APP.token) {
            headers['Authorization'] = 'Bearer ' + APP.token;
        }

        let res;
        try {
            res = await fetch(APP.BASE_URL + path, {
                method,
                headers,
                body: body ? JSON.stringify(body) : undefined,
            });
        } catch (networkErr) {
            // fetch() itself failed — backend unreachable, CORS blocked, no internet, etc.
            throw new Error('Could not reach the server. Please check your connection and try again.');
        }

        let data = {};
        try { data = await res.json(); } catch { /* empty/non-JSON response body */ }

        if (!res.ok) {
            throw new Error(data.error || `Request failed (${res.status})`);
        }
        return data;
    },

    // ---------- AUTH ----------
    async login(email, password) {
        const result = await API._request('/api/auth/login', {
            method: 'POST',
            body: { email, password },
        });
        APP.token = result.token;
        APP.user  = result.user;
        localStorage.setItem('user', JSON.stringify(result.user)); // admin.js reads this key
        return result;
    },

    async register(formData) {
        // Map frontend field names -> backend field names
        if (formData.password !== formData.confirm_password) {
            throw new Error('Passwords do not match');
        }
        const payload = {
            name:      formData.full_name,
            email:     formData.email,
            password:  formData.password,
            id_number: formData.national_id,
            phone:     formData.phone,
        };
        const result = await API._request('/api/auth/register', {
            method: 'POST',
            body: payload,
        });
        return result;
    },

    async me() {
        return API._request('/api/auth/me', { auth: true });
    },

    async changePassword(old_password, new_password) {
        return API._request('/api/auth/change-password', {
            method: 'POST',
            auth: true,
            body: { old_password, new_password },
        });
    },
};
