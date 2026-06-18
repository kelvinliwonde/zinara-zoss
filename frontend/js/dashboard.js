// ============================================================
// ZINARA ZOSS - Dashboard (dashboard.js)
// 2026 World-Class Dashboard
// ============================================================

let spendingChart = null;

document.addEventListener('DOMContentLoaded', async function() {
    if (!APP.token) {
        window.location.href = '/login.html';
        return;
    }
    
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
    
    await loadDashboardData();
    initChart();
});

async function loadDashboardData() {
    try {
        const profile = await API.getProfile();
        if (profile.user) {
            APP.user = profile.user;
            document.getElementById('userName').textContent = profile.user.full_name;
            document.getElementById('userEmail').textContent = profile.user.email;
        }
        
        const vehicles = await API.getVehicles();
        const vehicleCount = vehicles.vehicles ? vehicles.vehicles.length : 0;
        document.getElementById('miniVehicles').textContent = vehicleCount;
        document.getElementById('statVehicles').textContent = vehicleCount;
        document.getElementById('vehicleCountLabel').textContent = vehicleCount + ' registered';
        
        const radios = await API.getRadioLicenses();
        const radioCount = radios.radio_licenses ? radios.radio_licenses.length : 0;
        document.getElementById('miniRadio').textContent = radioCount;
        document.getElementById('statActive').textContent = radioCount + vehicleCount;
        
        const apps = await API.getApplications();
        const appCount = apps.applications ? apps.applications.length : 0;
        document.getElementById('miniApps').textContent = appCount;
        
        let totalSpent = 0;
        let pendingCount = 0;
        const pendingApps = [];
        const monthlyData = [0, 0, 0, 0, 0, 0];
        
        if (apps.applications) {
            apps.applications.forEach(app => {
                if (app.status === 'completed' || app.status === 'paid') {
                    totalSpent += app.total_amount || 0;
                }
                if (app.status === 'pending') {
                    pendingCount++;
                    pendingApps.push(app);
                }
                const date = new Date(app.application_date);
                const month = date.getMonth();
                if (month >= 0 && month < 6) {
                    monthlyData[month] += app.total_amount || 0;
                }
            });
        }
        
        document.getElementById('miniSpent').textContent = totalSpent > 0 ? '$' + totalSpent.toFixed(0) : '$0';
        document.getElementById('statSpent').textContent = totalSpent.toFixed(2);
        document.getElementById('statPending').textContent = pendingCount;
        
        renderPendingApplications(pendingApps);
        renderVehicles(vehicles.vehicles);
        updateChart(monthlyData);
        
    } catch (error) {
        console.error('Error loading dashboard:', error);
        showToast('Error loading dashboard data', 'error');
    }
}

function renderPendingApplications(pendingApps) {
    const container = document.getElementById('pendingApplications');
    if (!container) return;
    
    if (!pendingApps || pendingApps.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-check-circle" style="color:var(--green);font-size:1.5rem;"></i>
                <p style="color:var(--text-secondary);font-size:0.8rem;">All caught up! No pending actions.</p>
            </div>
        `;
        return;
    }
    
    let html = '<div class="table-wrap"><table class="table-custom">';
    html += `<thead><tr>
        <th>Type</th>
        <th>Amount</th>
        <th>Action</th>
    </tr></thead><tbody>`;
    
    pendingApps.slice(0, 3).forEach(app => {
        html += `<tr>
            <td><span class="type-badge" style="text-transform:capitalize;">${app.application_type}</span></td>
            <td>$${Number(app.total_amount).toFixed(2)}</td>
            <td>
                <button onclick="showToast('Payment feature coming soon','info')" 
                        style="background:var(--gold);border:none;border-radius:6px;padding:3px 12px;font-size:0.65rem;font-weight:600;color:#05050f;cursor:pointer;">
                    Pay Now
                </button>
            </td>
        </tr>`;
    });
    
    html += '</tbody></table></div>';
    container.innerHTML = html;
}

function renderVehicles(vehicles) {
    const container = document.getElementById('vehiclesList');
    if (!container) return;
    
    if (!vehicles || vehicles.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-car"></i>
                <p>No vehicles registered yet</p>
                <a href="renew.html" style="color:var(--gold);font-size:0.75rem;text-decoration:none;margin-top:4px;display:inline-block;">Add your first vehicle →</a>
            </div>
        `;
        return;
    }
    
    const colorMap = {
        'Car': '#dbeafe',
        'Kombi': '#fef3c7',
        'Bus': '#fce4ec',
        'Truck': '#e0e7ff',
        'Motorcycle': '#d1fae5'
    };
    
    let html = '<div class="vehicle-grid">';
    vehicles.slice(0, 4).forEach(v => {
        const bgColor = colorMap[v.vehicle_type] || '#f1f5f9';
        html += `
            <div class="vehicle-card">
                <div class="icon-wrap" style="background:${bgColor};color:#3b82f6;">
                    <i class="fas fa-car"></i>
                </div>
                <div class="info">
                    <div class="reg">${v.registration_number}</div>
                    <div class="details">${v.make} ${v.model} · ${v.year}</div>
                </div>
            </div>
        `;
    });
    html += '</div>';
    container.innerHTML = html;
}

function initChart() {
    const ctx = document.getElementById('spendingChart').getContext('2d');
    spendingChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            datasets: [{
                label: 'Spending',
                data: [0, 0, 0, 0, 0, 0],
                borderColor: '#fbbf24',
                backgroundColor: 'rgba(251, 191, 36, 0.05)',
                fill: true,
                tension: 0.4,
                pointBackgroundColor: '#fbbf24',
                pointBorderColor: '#05050f',
                pointBorderWidth: 2,
                pointRadius: 3,
                pointHoverRadius: 5,
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'rgba(10,10,26,0.95)',
                    borderColor: 'rgba(255,255,255,0.06)',
                    borderWidth: 1,
                    titleColor: '#fff',
                    bodyColor: 'rgba(255,255,255,0.6)',
                    cornerRadius: 8,
                    padding: 10,
                    callbacks: {
                        label: function(context) {
                            return '$' + context.parsed.y.toFixed(2);
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: 'rgba(255,255,255,0.03)' },
                    ticks: { 
                        color: 'rgba(255,255,255,0.3)',
                        font: { size: 9 },
                        callback: function(value) { return '$' + value; }
                    }
                },
                x: {
                    grid: { display: false },
                    ticks: { 
                        color: 'rgba(255,255,255,0.3)',
                        font: { size: 9 }
                    }
                }
            }
        }
    });
}

function updateChart(monthlyData) {
    if (!spendingChart) return;
    spendingChart.data.datasets[0].data = monthlyData;
    spendingChart.update();
}