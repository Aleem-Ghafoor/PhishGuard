/* static/dashboard/js/dashboard-data.js */
const DASHBOARD_DATA = {
  total_scans: 124,
  safe_urls: 87,
  phishing_urls: 34,
  suspicious_urls: 3,
  detection_rate: "70.2%",
  trends: {
    total_scans: { value: "+18%", direction: "up", text: "from last week" },
    safe_urls: { value: "+20%", direction: "up", text: "from last week" },
    phishing_urls: { value: "-12%", direction: "down", text: "from last week" },
    detection_rate: { value: "+5.4%", direction: "up", text: "from last week" }
  },
  scan_overview: {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    datasets: {
      safe: [45, 60, 35, 50, 55, 40, 30],
      phishing: [15, 25, 10, 20, 30, 15, 10],
      suspicious: [2, 5, 1, 3, 4, 2, 1]
    }
  },
  recent_scans: [
    { url: "https://www.google.com", status: "safe", confidence: "99.1%", scanned_at: "Nov 18, 2026, 06:12 PM" },
    { url: "https://free-gift-shop.xyz", status: "phishing", confidence: "95.6%", scanned_at: "Nov 18, 2026, 05:48 PM" },
    { url: "https://github.com", status: "safe", confidence: "98.9%", scanned_at: "Nov 18, 2026, 04:21 PM" },
    { url: "http://secure-bank-login.co", status: "phishing", confidence: "94.3%", scanned_at: "Nov 18, 2026, 03:57 PM" }
  ]
};