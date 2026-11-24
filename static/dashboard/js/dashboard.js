
document.addEventListener('DOMContentLoaded', async () => {
    const statsContainer = document.getElementById('stats-container');

    try {
        const response = await fetch('/scanner/history/api/');

        if (!response.ok) {
            throw new Error('Failed to fetch scan history');
        }

        const result = await response.json();

        if (result.status !== 'success') {
            throw new Error('Invalid API response');
        }

        const scans = result.scans;

        const legitimateScans = scans.filter(
            scan => scan.prediction.toLowerCase() === 'legitimate'
        );

        const phishingScans = scans.filter(
            scan => scan.prediction.toLowerCase() === 'phishing'
        );

        const totalScans = result.total_count;
        const phishingRatio = totalScans
            ? ((phishingScans.length / totalScans) * 100).toFixed(1)
            : '0.0';

        const dashboardData = {
            total_scans: totalScans,
            safe_urls: legitimateScans.length,
            phishing_urls: phishingScans.length,
            phishing_ratio: phishingRatio,
            recent_scans: scans.slice(0, 10),
            scan_overview: buildDailyOverview(scans)
        };

        renderStats(dashboardData);
        renderDistribution(dashboardData);
        renderRecentScans(dashboardData.recent_scans);

        if (typeof renderScanOverviewChart === 'function') {
            renderScanOverviewChart(dashboardData.scan_overview);
        }

    } catch (error) {
        console.error('Dashboard error:', error);

        if (statsContainer) {
            statsContainer.innerHTML =
                '<p>Unable to load dashboard data. Please refresh.</p>';
        }
    }
});


function renderStats(data) {
    const container = document.getElementById('stats-container');

    const cards = [
        {
            title: 'Total Scans',
            value: data.total_scans,
            type: 'total'
        },
        {
            title: 'Legitimate URLs',
            value: data.safe_urls,
            type: 'safe'
        },
        {
            title: 'Phishing URLs',
            value: data.phishing_urls,
            type: 'phishing'
        },
        {
            title: 'Phishing Ratio',
            value: `${data.phishing_ratio}%`,
            type: 'rate'
        }
    ];

    container.innerHTML = cards.map(card => `
        <div class="stat-card stat-${card.type}">
            <div class="stat-content">
                <h3>${card.value}</h3>
                <p>${card.title}</p>
            </div>
        </div>
    `).join('');
}


function renderDistribution(data) {
    const container = document.getElementById('distribution-container');

    const total = data.safe_urls + data.phishing_urls;

    const safePct = total
        ? ((data.safe_urls / total) * 100).toFixed(1)
        : '0.0';

    const phishPct = total
        ? ((data.phishing_urls / total) * 100).toFixed(1)
        : '0.0';

    const items = [
        {
            label: 'Legitimate URLs',
            pct: safePct,
            count: data.safe_urls,
            type: 'safe'
        },
        {
            label: 'Phishing URLs',
            pct: phishPct,
            count: data.phishing_urls,
            type: 'phishing'
        }
    ];

    container.innerHTML = items.map(item => `
        <div class="dist-item">
            <div class="dist-header">
                <div class="dist-label">${item.label}</div>
                <div class="dist-value">${item.pct}% (${item.count})</div>
            </div>
            <div class="dist-bar-wrap">
                <div class="dist-bar ${item.type}"
                     style="width: ${item.pct}%"></div>
            </div>
        </div>
    `).join('');
}


function renderRecentScans(scans) {
    const container = document.getElementById('recent-scans-body');

    if (!scans.length) {
        container.innerHTML = `
            <tr>
                <td colspan="5">No scans found.</td>
            </tr>
        `;
        return;
    }

    container.innerHTML = scans.map(scan => {
        const isPhishing =
            scan.prediction.toLowerCase() === 'phishing';

        const status = isPhishing ? 'phishing' : 'safe';

        return `
            <tr>
                <td class="td-url">${escapeHTML(scan.url)}</td>
                <td>
                    <span class="badge ${status}">
                        ${isPhishing ? 'Phishing' : 'Legitimate'}
                    </span>
                </td>
                <td class="td-confidence">
                    ${Number(scan.phishing_probability).toFixed(2)}
                </td>
                <td class="td-date">${escapeHTML(scan.scanned_at)}</td>
                <td><button class="action-btn">...</button></td>
            </tr>
        `;
    }).join('');
}


function buildDailyOverview(scans) {
    const labels = [];
    const safe = [];
    const phishing = [];

    for (let i = 6; i >= 0; i--) {
        const date = new Date();
        date.setHours(0, 0, 0, 0);
        date.setDate(date.getDate() - i);

        labels.push(date.toLocaleDateString('en-US', {
            weekday: 'short'
        }));

        const dayScans = scans.filter(scan => {
            const scannedDate = new Date(scan.scanned_at);

            return scannedDate.getFullYear() === date.getFullYear()
                && scannedDate.getMonth() === date.getMonth()
                && scannedDate.getDate() === date.getDate();
        });

        safe.push(dayScans.filter(
            scan => scan.prediction.toLowerCase() === 'legitimate'
        ).length);

        phishing.push(dayScans.filter(
            scan => scan.prediction.toLowerCase() === 'phishing'
        ).length);
    }

    return { labels, safe, phishing };
}


function escapeHTML(value) {
    return String(value).replace(/[&<>"']/g, char => ({
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;'
    })[char]);
}


/* Mobile Sidebar Toggle */
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
        overlay.addEventListener('click', toggleMenu);
    }
});
