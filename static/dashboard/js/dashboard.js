/* static/dashboard/js/dashboard.js */
document.addEventListener('DOMContentLoaded', () => {
  renderDashboard(DASHBOARD_DATA);
});

function renderDashboard(data) {
  renderStats(data);
  renderDistribution(data);
  renderRecentScans(data.recent_scans);
}

function renderStats(data) {
  const container = document.getElementById('stats-container');
  const cards = [
    { title: 'Total Scans', value: data.total_scans, type: 'total', icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>`, trend: data.trends.total_scans },
    { title: 'Safe URLs', value: data.safe_urls, type: 'safe', icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/></svg>`, trend: data.trends.safe_urls },
    { title: 'Phishing URLs', value: data.phishing_urls, type: 'phishing', icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>`, trend: data.trends.phishing_urls },
    { title: 'Detection Rate', value: data.detection_rate, type: 'rate', icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="20" x2="12" y2="10"/><line x1="18" y1="20" x2="18" y2="4"/><line x1="6" y1="20" x2="6" y2="16"/></svg>`, trend: data.trends.detection_rate }
  ];

  container.innerHTML = cards.map(card => `
    <div class="stat-card stat-${card.type}">
      <div class="stat-icon-wrap">${card.icon}</div>
      <div class="stat-content">
        <h3>${card.value}</h3>
        <p>${card.title}</p>
        <div class="stat-trend trend-${card.trend.direction}">
          ${card.trend.direction === 'up' ? '&nearr;' : '&searr;'} ${card.trend.value} ${card.trend.text}
        </div>
      </div>
    </div>
  `).join('');
}

function renderDistribution(data) {
  const container = document.getElementById('distribution-container');
  const total = data.safe_urls + data.phishing_urls + data.suspicious_urls;
  const safePct = ((data.safe_urls / total) * 100).toFixed(1);
  const phishPct = ((data.phishing_urls / total) * 100).toFixed(1);
  const suspPct = ((data.suspicious_urls / total) * 100).toFixed(1);

  const items = [
    { label: 'Safe URLs', pct: safePct, count: data.safe_urls, type: 'safe', icon: `<svg viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/></svg>` },
    { label: 'Phishing URLs', pct: phishPct, count: data.phishing_urls, type: 'phishing', icon: `<svg viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>` },
    { label: 'Suspicious URLs', pct: suspPct, count: data.suspicious_urls, type: 'suspicious', icon: `<svg viewBox="0 0 24 24" fill="none" stroke="#8b5cf6" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>` }
  ];

  container.innerHTML = items.map(item => `
    <div class="dist-item">
      <div class="dist-header">
        <div class="dist-label">${item.icon} ${item.label}</div>
        <div class="dist-value">${item.pct}% (${item.count})</div>
      </div>
      <div class="dist-bar-wrap">
        <div class="dist-bar ${item.type}" style="width: ${item.pct}%"></div>
      </div>
    </div>
  `).join('');
}

function renderRecentScans(scans) {
  const container = document.getElementById('recent-scans-body');
  container.innerHTML = scans.map(scan => {
    let badgeClass = scan.status.toLowerCase();
    let icon = '';
    if (scan.status === 'safe') icon = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/></svg>`;
    else if (scan.status === 'phishing') icon = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>`;

    return `
      <tr>
        <td class="td-url">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>
          ${scan.url}
        </td>
        <td><span class="badge ${badgeClass}">${icon} ${scan.status.charAt(0).toUpperCase() + scan.status.slice(1)}</span></td>
        <td class="td-confidence">${scan.confidence}</td>
        <td class="td-date">${scan.scanned_at}</td>
        <td><button class="action-btn">...</button></td>
      </tr>
    `;
  }).join('');
}

/* =========================================
   Mobile Sidebar Toggle Logic
   ========================================= */
document.addEventListener('DOMContentLoaded', () => {
  const mobileMenuBtn = document.getElementById('mobileMenuBtn');
  const sidebar = document.getElementById('mainSidebar');
  const overlay = document.getElementById('sidebarOverlay');

  if (mobileMenuBtn && sidebar && overlay) {
    function toggleMenu() {
      sidebar.classList.toggle('active');
      overlay.classList.toggle('active');
    }

    mobileMenuBtn.addEventListener('click', toggleMenu);
    
    // Overlay par click karne se sidebar band ho jaye
    overlay.addEventListener('click', toggleMenu);
  }
});