// ============================================================
// ZINARA ZOSS - Authentication (auth.js)
// ============================================================

document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
    }
});

// ---------- HANDLE LOGIN ----------
async function handleLogin(e) {
    e.preventDefault();
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const errorDiv = document.getElementById('errorMessage');
    const loginBtn = document.getElementById('loginBtn');
    
    errorDiv.classList.add('hidden');
    loginBtn.disabled = true;
    loginBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Signing in...';
    
    try {
        const result = await API.login(email, password);
        showToast('✅ Login successful! Redirecting...', 'success');
        setTimeout(() => {
            window.location.href = '/dashboard.html';
        }, 1000);
    } catch (error) {
        errorDiv.textContent = error.message || 'Login failed. Please try again.';
        errorDiv.classList.remove('hidden');
        loginBtn.disabled = false;
        loginBtn.innerHTML = '<i class="fas fa-sign-in-alt mr-2"></i> Sign In';
    }
}

// ---------- HANDLE REGISTER ----------
async function handleRegister(e) {
    e.preventDefault();
    
    const data = {
        full_name: document.getElementById('full_name').value,
        national_id: document.getElementById('national_id').value,
        email: document.getElementById('email').value,
        phone: document.getElementById('phone').value,
        password: document.getElementById('password').value,
        confirm_password: document.getElementById('confirm_password').value
    };
    
    const errorDiv = document.getElementById('errorMessage');
    const successDiv = document.getElementById('successMessage');
    const registerBtn = document.getElementById('registerBtn');
    
    errorDiv.classList.add('hidden');
    successDiv.classList.add('hidden');
    registerBtn.disabled = true;
    registerBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Creating account...';
    
    try {
        const result = await API.register(data);
        successDiv.textContent = '✅ Registration successful! Redirecting to login...';
        successDiv.classList.remove('hidden');
        showToast('✅ Account created successfully!', 'success');
        setTimeout(() => {
            window.location.href = '/login.html';
        }, 2000);
    } catch (error) {
        errorDiv.textContent = error.message || 'Registration failed. Please try again.';
        errorDiv.classList.remove('hidden');
        registerBtn.disabled = false;
        registerBtn.innerHTML = '<i class="fas fa-user-plus mr-2"></i> Create Account';
    }
}