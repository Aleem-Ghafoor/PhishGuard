
let urlScanChartInstance = null;

function renderScanOverviewChart(data) {
    const canvas = document.getElementById('urlScanChart');

    if (!canvas) return;

    // Destroy previous chart before creating a new one
    if (urlScanChartInstance) {
        urlScanChartInstance.destroy();
    }

    urlScanChartInstance = new Chart(canvas, {
        type: 'line',

        data: {
            labels: data.labels,

            datasets: [
                {
                    label: 'Legitimate',
                    data: data.safe,
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Phishing',
                    data: data.phishing,
                    borderColor: '#ef4444',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    tension: 0.4,
                    fill: true
                }
            ]
        },

        options: {
            responsive: true,
            maintainAspectRatio: false,

            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        usePointStyle: true,
                        color: '#94a3b8'
                    }
                }
            },

            scales: {
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: '#94a3b8'
                    }
                },

                y: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0,
                        color: '#94a3b8'
                    }
                }
            }
        }
    });
}
