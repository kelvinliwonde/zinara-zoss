// ============================================================
// ZINARA ZOSS - Renewal (renew.js)
// 2026 World-Class Renewal Flow
// ============================================================

let userVehicles = [];
let userRadios = [];

document.addEventListener('DOMContentLoaded', async function() {
    console.log('🔵 Renew page loaded');
    
    if (!APP.token) {
        window.location.href = '/login.html';
        return;
    }
    
    // Update sidebar user
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
        APP.user = JSON.parse(storedUser);
        const initial = APP.user.full_name.split(' ').map(n => n[0]).join('');
        document.getElementById('userAvatar').textContent = initial;
        document.getElementById('userNameShort').textContent = APP.user.full_name;
        document.getElementById('userRole').textContent = APP.user.role.charAt(0).toUpperCase() + APP.user.role.slice(1);
        
        if (APP.user.role === 'admin' || APP.user.role === 'super_admin') {
            document.getElementById('adminLabel').style.display = 'block';
            document.getElementById('adminLink').style.display = 'flex';
            document.getElementById('integrationLink').style.display = 'flex';
        }
    }
    
    try {
        // Load vehicles
        const vehicles = await API.getVehicles();
        userVehicles = vehicles.vehicles || [];
        console.log('🚗 Vehicles loaded:', userVehicles.length);
        
        // Load radio licenses
        const radios = await API.getRadioLicenses();
        userRadios = radios.radio_licenses || [];
        console.log('📻 Radio licenses loaded:', userRadios.length);
        
        populateVehicleDropdown();
        populateRadioDropdown();
        
    } catch (error) {
        console.error('❌ Error loading data:', error);
        showToast('Error loading your data. Please refresh.', 'error');
    }
    
    // Event listeners
    document.getElementById('applicationType').addEventListener('change', handleTypeChange);
    document.getElementById('vehicleId').addEventListener('change', calculateFees);
    document.getElementById('radioLicenseId').addEventListener('change', calculateFees);
    document.getElementById('renewalForm').addEventListener('submit', handleSubmit);
    
    console.log('✅ Renew page initialized');
});

// ---------- POPULATE VEHICLE DROPDOWN ----------
function populateVehicleDropdown() {
    const select = document.getElementById('vehicleId');
    if (!select) return;
    
    select.innerHTML = '<option value="">Select a vehicle...</option>';
    
    if (!userVehicles || userVehicles.length === 0) {
        const option = document.createElement('option');
        option.value = '';
        option.textContent = '⚠️ No vehicles registered. Add one first.';
        option.disabled = true;
        select.appendChild(option);
        return;
    }
    
    userVehicles.forEach(v => {
        const option = document.createElement('option');
        option.value = v.id;
        option.textContent = `${v.registration_number} - ${v.make} ${v.model} (${v.year})`;
        select.appendChild(option);
    });
    
    console.log('🚗 Vehicle dropdown populated with', userVehicles.length, 'vehicles');
}

// ---------- POPULATE RADIO DROPDOWN ----------
function populateRadioDropdown() {
    const select = document.getElementById('radioLicenseId');
    if (!select) return;
    
    select.innerHTML = '<option value="">Select a radio license...</option>';
    
    if (!userRadios || userRadios.length === 0) {
        const option = document.createElement('option');
        option.value = '';
        option.textContent = '⚠️ No radio licenses registered. Add one first.';
        option.disabled = true;
        select.appendChild(option);
        return;
    }
    
    userRadios.forEach(r => {
        const option = document.createElement('option');
        option.value = r.id;
        option.textContent = `${r.radio_serial_number} - ${r.radio_make} ${r.radio_model}`;
        select.appendChild(option);
    });
    
    console.log('📻 Radio dropdown populated with', userRadios.length, 'radios');
}

// ---------- HANDLE TYPE CHANGE ----------
function handleTypeChange() {
    const type = document.getElementById('applicationType').value;
    const vehicleSection = document.getElementById('vehicleSection');
    const radioSection = document.getElementById('radioSection');
    const feeDisplay = document.getElementById('feeDisplay');
    const vehicleSelect = document.getElementById('vehicleId');
    const radioSelect = document.getElementById('radioLicenseId');
    
    console.log('🔄 Type changed to:', type);
    
    // Hide all
    vehicleSection.style.display = 'none';
    radioSection.style.display = 'none';
    feeDisplay.style.display = 'none';
    
    // Remove required
    vehicleSelect.removeAttribute('required');
    radioSelect.removeAttribute('required');
    
    // Show relevant
    if (type === 'vehicle' || type === 'both') {
        vehicleSection.style.display = 'block';
        vehicleSelect.setAttribute('required', 'required');
    }
    
    if (type === 'radio' || type === 'both') {
        radioSection.style.display = 'block';
        radioSelect.setAttribute('required', 'required');
    }
    
    if (type !== '') {
        feeDisplay.style.display = 'block';
        calculateFees();
    }
}

// ---------- CALCULATE FEES ----------
async function calculateFees() {
    const type = document.getElementById('applicationType').value;
    const vehicleId = document.getElementById('vehicleId').value;
    const radioId = document.getElementById('radioLicenseId').value;
    
    console.log('💰 Calculating fees for:', { type, vehicleId, radioId });
    
    if (type === '') return;
    if ((type === 'vehicle' || type === 'both') && !vehicleId) return;
    if ((type === 'radio' || type === 'both') && !radioId) return;
    
    try {
        const data = {
            vehicle_id: vehicleId || null,
            radio_license_id: radioId || null
        };
        
        console.log('📤 Sending fee request:', data);
        
        const result = await API.calculateFees(data);
        
        console.log('📥 Fee result:', result);
        
        document.getElementById('feeAmount').textContent = formatCurrency(result.fee_amount);
        document.getElementById('penaltyAmount').textContent = formatCurrency(result.penalty_fee);
        document.getElementById('totalAmount').textContent = formatCurrency(result.total_amount);
        
    } catch (error) {
        console.error('❌ Error calculating fees:', error);
        showToast('Error calculating fees', 'error');
    }
}

// ---------- HANDLE SUBMIT ----------
async function handleSubmit(e) {
    e.preventDefault();
    console.log('📝 Form submitted');
    
    const type = document.getElementById('applicationType').value;
    const vehicleId = document.getElementById('vehicleId').value;
    const radioId = document.getElementById('radioLicenseId').value;
    
    const errorDiv = document.getElementById('errorMessage');
    const successDiv = document.getElementById('successMessage');
    const submitBtn = document.getElementById('submitBtn');
    
    errorDiv.style.display = 'none';
    successDiv.style.display = 'none';
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Submitting...';
    submitBtn.style.opacity = '0.6';
    
    try {
        const data = {
            application_type: type,
            vehicle_id: vehicleId || null,
            radio_license_id: radioId || null
        };
        
        console.log('📤 Submitting renewal:', data);
        
        const result = await API.applyRenewal(data);
        
        console.log('✅ Renewal submitted:', result);
        
        // Show success
        successDiv.innerHTML = `
            <div style="display:flex;align-items:center;gap:10px;">
                <i class="fas fa-check-circle" style="font-size:1.2rem;"></i>
                <div>
                    <div style="font-weight:600;">Application Submitted!</div>
                    <div style="font-size:0.8rem;opacity:0.7;">Your application is being processed. You will receive a confirmation shortly.</div>
                </div>
            </div>
        `;
        successDiv.style.display = 'block';
        showToast('✅ Renewal application submitted!', 'success');
        
        // Reset form
        document.getElementById('renewalForm').reset();
        document.getElementById('feeDisplay').style.display = 'none';
        document.getElementById('vehicleSection').style.display = 'none';
        document.getElementById('radioSection').style.display = 'none';
        document.getElementById('vehicleId').removeAttribute('required');
        document.getElementById('radioLicenseId').removeAttribute('required');
        
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Submit Renewal Application';
        submitBtn.style.opacity = '1';
        
        // Show success message for 5 seconds then redirect
        setTimeout(() => {
            window.location.href = '/dashboard.html';
        }, 3000);
        
    } catch (error) {
        console.error('❌ Submission error:', error);
        errorDiv.innerHTML = `
            <div style="display:flex;align-items:center;gap:10px;">
                <i class="fas fa-exclamation-circle" style="font-size:1.2rem;"></i>
                <div>${error.message || 'Submission failed. Please try again.'}</div>
            </div>
        `;
        errorDiv.style.display = 'block';
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Submit Renewal Application';
        submitBtn.style.opacity = '1';
    }
}