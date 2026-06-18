// ============================================================
// ZINARA Integration - Integration Page (integration.js)
// ============================================================

document.addEventListener('DOMContentLoaded', function() {
    if (!APP.token) {
        window.location.href = '/login.html';
        return;
    }
    refreshStatus();
    addLog('🔌 Integration page loaded', 'info');
});

// ---------- REFRESH SYSTEM STATUS ----------
async function refreshStatus() {
    try {
        const result = await API.getSystemStatus();
        const container = document.getElementById('systemStatus');
        
        container.innerHTML = `
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem;">
                <div>
                    <div style="font-size: 0.8rem; color: #94a3b8;">Status</div>
                    <div style="font-weight: 700; color: #10b981; display: flex; align-items: center; gap: 6px;">
                        <span class="status-completed" style="width: 8px; height: 8px; display: inline-block; padding: 0;"></span>
                        ${result.system_status}
                    </div>
                </div>
                <div>
                    <div style="font-size: 0.8rem; color: #94a3b8;">Queue Size</div>
                    <div style="font-weight: 700;">${result.queue_size} applications</div>
                </div>
                <div>
                    <div style="font-size: 0.8rem; color: #94a3b8;">Avg Processing Time</div>
                    <div style="font-weight: 700;">${result.average_processing_time}</div>
                </div>
                <div>
                    <div style="font-size: 0.8rem; color: #94a3b8;">Applications Today</div>
                    <div style="font-weight: 700;">${result.total_applications_today}</div>
                </div>
                <div>
                    <div style="font-size: 0.8rem; color: #94a3b8;">System Uptime</div>
                    <div style="font-weight: 700;">${result.system_uptime}</div>
                </div>
                <div>
                    <div style="font-size: 0.8rem; color: #94a3b8;">Last Maintenance</div>
                    <div style="font-weight: 700; font-size: 0.8rem;">${formatDate(result.last_maintenance)}</div>
                </div>
            </div>
        `;
        
        addLog('✅ System status refreshed', 'success');
    } catch (error) {
        console.error('Error fetching system status:', error);
        document.getElementById('systemStatus').innerHTML = `
            <p style="color: #ef4444;">❌ Failed to fetch system status</p>
        `;
    }
}

// ---------- VERIFY VEHICLE ----------
async function verifyVehicle() {
    const reg = document.getElementById('verifyVehicleInput').value.trim();
    if (!reg) {
        showToast('Please enter a registration number', 'warning');
        return;
    }
    
    const resultDiv = document.getElementById('vehicleVerificationResult');
    resultDiv.innerHTML = '<p style="color: #94a3b8;">Checking with ZINARA...</p>';
    
    try {
        const result = await API.verifyVehicle(reg);
        resultDiv.innerHTML = `
            <div style="padding: 1rem; border-radius: 8px; margin-top: 0.5rem; background: ${result.success ? '#d1fae5' : '#fee2e2'};">
                ${result.success ? `
                    <div style="display: flex; align-items: center; gap: 8px; color: #065f46;">
                        <i class="fas fa-check-circle"></i>
                        <strong>Verified</strong>
                    </div>
                    <div style="font-size: 0.9rem; margin-top: 4px;">
                        ${result.make} ${result.model} (${result.year}) - ${result.status}
                    </div>
                ` : `
                    <div style="display: flex; align-items: center; gap: 8px; color: #991b1b;">
                        <i class="fas fa-times-circle"></i>
                        <strong>${result.message}</strong>
                    </div>
                `}
            </div>
        `;
        addLog(`🔍 Vehicle verification: ${reg} - ${result.success ? 'Found ✅' : 'Not found ❌'}`, result.success ? 'success' : 'error');
    } catch (error) {
        resultDiv.innerHTML = `<p style="color: #ef4444;">❌ ${error.message}</p>`;
    }
}

// ---------- VERIFY RADIO ----------
async function verifyRadio() {
    const serial = document.getElementById('verifyRadioInput').value.trim();
    if (!serial) {
        showToast('Please enter a radio serial number', 'warning');
        return;
    }
    
    const resultDiv = document.getElementById('radioVerificationResult');
    resultDiv.innerHTML = '<p style="color: #94a3b8;">Checking with ZBC...</p>';
    
    try {
        const result = await API.verifyRadio(serial);
        resultDiv.innerHTML = `
            <div style="padding: 1rem; border-radius: 8px; margin-top: 0.5rem; background: ${result.success ? '#d1fae5' : '#fee2e2'};">
                ${result.success ? `
                    <div style="display: flex; align-items: center; gap: 8px; color: #065f46;">
                        <i class="fas fa-check-circle"></i>
                        <strong>Valid License</strong>
                    </div>
                    <div style="font-size: 0.9rem; margin-top: 4px;">
                        Expires: ${formatDate(result.expiry_date)}
                    </div>
                ` : `
                    <div style="display: flex; align-items: center; gap: 8px; color: #991b1b;">
                        <i class="fas fa-times-circle"></i>
                        <strong>${result.message}</strong>
                    </div>
                `}
            </div>
        `;
        addLog(`📻 Radio verification: ${serial} - ${result.success ? 'Valid ✅' : 'Invalid ❌'}`, result.success ? 'success' : 'error');
    } catch (error) {
        resultDiv.innerHTML = `<p style="color: #ef4444;">❌ ${error.message}</p>`;
    }
}

// ---------- SUBMIT TO ZINARA ----------
async function submitToZinara() {
    const appId = document.getElementById('submitAppId').value;
    if (!appId) {
        showToast('Please enter an application ID', 'warning');
        return;
    }
    
    const resultDiv = document.getElementById('submitResult');
    resultDiv.innerHTML = '<p style="color: #94a3b8;">Submitting to ZINARA...</p>';
    
    try {
        const result = await API.submitToZinara(appId);
        resultDiv.innerHTML = `
            <div style="padding: 1rem; border-radius: 8px; margin-top: 0.5rem; background: #d1fae5; color: #065f46;">
                <div><i class="fas fa-check-circle"></i> <strong>Submitted Successfully</strong></div>
                <div style="font-size: 0.9rem; margin-top: 4px;">
                    Reference: ${result.reference_number}
                </div>
                <div style="font-size: 0.9rem;">
                    Status: ${result.status}
                </div>
                <div style="font-size: 0.9rem; color: #64748b;">
                    ${result.message}
                </div>
            </div>
        `;
        addLog(`📤 Application #${appId} submitted to ZINARA. Ref: ${result.reference_number}`, 'success');
    } catch (error) {
        resultDiv.innerHTML = `<p style="color: #ef4444;">❌ ${error.message}</p>`;
    }
}

// ---------- PROCESS PAYMENT ----------
async function processPayment() {
    const appId = document.getElementById('paymentAppId').value;
    const method = document.getElementById('paymentMethod').value;
    
    if (!appId) {
        showToast('Please enter an application ID', 'warning');
        return;
    }
    
    const resultDiv = document.getElementById('paymentResult');
    resultDiv.innerHTML = '<p style="color: #94a3b8;">Processing payment...</p>';
    
    try {
        const result = await API.processZinaraPayment(appId, method);
        resultDiv.innerHTML = `
            <div style="padding: 1rem; border-radius: 8px; margin-top: 0.5rem; background: ${result.payment.success ? '#d1fae5' : '#fee2e2'};">
                ${result.payment.success ? `
                    <div style="display: flex; align-items: center; gap: 8px; color: #065f46;">
                        <i class="fas fa-check-circle"></i>
                        <strong>Payment Successful!</strong>
                    </div>
                    <div style="font-size: 0.9rem; margin-top: 4px;">
                        Payment Ref: ${result.payment.payment_reference}
                    </div>
                    <div style="font-size: 0.9rem;">
                        Transaction ID: ${result.payment.transaction_id}
                    </div>
                    ${result.license ? `
                        <div style="margin-top: 8px; padding: 8px; background: #f8fafc; border-radius: 6px;">
                            <div style="font-weight: 600; color: #1a1a2e;">Digital License Generated</div>
                            <div style="font-size: 0.85rem; color: #64748b;">
                                License Number: ${result.license.license_number}
                            </div>
                            <div style="font-size: 0.85rem; color: #64748b;">
                                Valid Until: ${formatDate(result.license.expiry_date)}
                            </div>
                        </div>
                    ` : ''}
                ` : `
                    <div style="display: flex; align-items: center; gap: 8px; color: #991b1b;">
                        <i class="fas fa-times-circle"></i>
                        <strong>Payment Failed</strong>
                    </div>
                    <div style="font-size: 0.9rem; margin-top: 4px;">
                        ${result.payment.message}
                    </div>
                `}
            </div>
        `;
        addLog(`💳 Payment processed for app #${appId} - ${result.payment.success ? 'Success ✅' : 'Failed ❌'}`, result.payment.success ? 'success' : 'error');
    } catch (error) {
        resultDiv.innerHTML = `<p style="color: #ef4444;">❌ ${error.message}</p>`;
    }
}

// ---------- INTEGRATION LOG ----------
function addLog(message, type = 'info') {
    const logDiv = document.getElementById('integrationLog');
    const colors = {
        info: '#3b82f6',
        success: '#10b981',
        error: '#ef4444',
        warning: '#f59e0b'
    };
    
    const timestamp = new Date().toLocaleTimeString();
    const entry = document.createElement('div');
    entry.style.cssText = `
        padding: 4px 0;
        border-bottom: 1px solid #e2e8f0;
        color: ${colors[type] || '#64748b'};
    `;
    entry.innerHTML = `<span style="color: #94a3b8;">[${timestamp}]</span> ${message}`;
    
    // Remove "Waiting..." message if present
    if (logDiv.querySelector('p[style*="color: #94a3b8"]')) {
        logDiv.innerHTML = '';
    }
    
    logDiv.prepend(entry);
    
    // Keep only last 50 entries
    while (logDiv.children.length > 50) {
        logDiv.removeChild(logDiv.lastChild);
    }
}

function clearLog() {
    const logDiv = document.getElementById('integrationLog');
    logDiv.innerHTML = '<p style="color: #94a3b8; text-align: center;">Log cleared</p>';
}

// ---------- EXPOSE FUNCTIONS ----------
window.refreshStatus = refreshStatus;
window.verifyVehicle = verifyVehicle;
window.verifyRadio = verifyRadio;
window.submitToZinara = submitToZinara;
window.processPayment = processPayment;
window.clearLog = clearLog;
window.addLog = addLog;