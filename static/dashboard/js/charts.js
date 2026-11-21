/* static/dashboard/js/charts.js */
document.addEventListener('DOMContentLoaded', () => {
  if (typeof DASHBOARD_DATA === 'undefined') return;
  const ctx = document.getElementById('urlScanChart');
  if (!ctx) return;
  const data = DASHBOARD_DATA.scan_overview;
  new Chart(ctx, {
    type: 'bubble',
    data: {
      datasets: [
        { label: 'Safe', data: data.labels.map((day, i) => ({ x: i, y: data.datasets.safe[i], r: 12 })), backgroundColor: '#10b981' },
        { label: 'Phishing', data: data.labels.map((day, i) => ({ x: i, y: data.datasets.phishing[i], r: 10 })), backgroundColor: '#8b5cf6' },
        { label: 'Suspicious', data: data.labels.map((day, i) => ({ x: i, y: data.datasets.suspicious[i], r: 6 })), backgroundColor: '#f8fafc' }
      ]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      scales: {
        x: { type: 'category', labels: data.labels, grid: { display: false }, ticks: { color: '#94a3b8' } },
        y: { display: false, beginAtZero: true }
      },
      plugins: {
        legend: { position: 'bottom', labels: { color: '#94a3b8', usePointStyle: true, boxWidth: 8 } },
        tooltip: { backgroundColor: '#0a1424', titleColor: '#f8fafc', bodyColor: '#cbd5e1', borderColor: 'rgba(255,255,255,0.1)', borderWidth: 1 }
      }
    }
  });
});