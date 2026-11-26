document.addEventListener('DOMContentLoaded', () => {
    const scanForm = document.getElementById('scanForm');
    const urlInput = document.getElementById('urlInput');
    const scanBtn = document.getElementById('scanBtn');

    const resultCard = document.getElementById('resultCard');
    const resultTitle = document.getElementById('resultTitle');
    const resultMessage = document.getElementById('resultMessage');
    const resultScore = document.getElementById('resultScore');
    const resultIcon = document.getElementById('resultIcon');

    const iconPhish = `
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
            <line x1="12" y1="9" x2="12" y2="13"/>
            <line x1="12" y1="17" x2="12.01" y2="17"/>
        </svg>`;
    const iconSafe = `
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
            <polyline points="9 12 11 14 15 10"/>
        </svg>`;

    function displayResult(prediction, score) {
        if (!resultCard) return;
        const isPhishing = prediction.toLowerCase() === 'phishing';
        resultCard.style.display = 'flex';
        resultCard.classList.toggle('legitimate', !isPhishing);
        resultTitle.textContent = `Scan result: ${prediction}`;
        resultMessage.textContent = isPhishing
            ? 'The PhishGuard model classified this URL as potentially phishing. Avoid entering sensitive information and verify the destination independently.'
            : 'The PhishGuard model classified this URL as legitimate. This is not a guarantee of safety; continue to practice safe browsing.';
        const numericScore = Number(score);
        resultScore.textContent = Number.isFinite(numericScore) ? numericScore.toFixed(4) : 'N/A';
        resultIcon.innerHTML = isPhishing ? iconPhish : iconSafe;
    }

    scanForm?.addEventListener('submit', async (event) => {
        event.preventDefault();
        const url = urlInput.value.trim();
        if (!url) {
            resultCard.style.display = 'flex';
            resultTitle.textContent = 'Invalid URL';
            resultMessage.textContent = 'Please enter a URL.';
            resultScore.textContent = '--';
            return;
        }

        resultCard.style.display = 'none';
        const originalText = scanBtn.textContent;
        scanBtn.disabled = true;
        scanBtn.textContent = 'Scanning...';

        try {
            const csrfInput = scanForm.querySelector('[name=csrfmiddlewaretoken]');
            if (!csrfInput) throw new Error('Security token missing. Refresh the page and try again.');

            const response = await fetch(scanForm.dataset.apiUrl, {
                method: 'POST',
                headers: {'X-CSRFToken': csrfInput.value},
                body: new FormData(scanForm),
                credentials: 'same-origin'
            });
            const data = await response.json();
            if (!response.ok || !data.success) {
                throw new Error(data.message || 'Scanning failed. Please try again.');
            }
            displayResult(data.result.prediction, data.result.phishing_probability);
        } catch (error) {
            resultCard.style.display = 'flex';
            resultCard.classList.remove('legitimate');
            resultTitle.textContent = 'Scan Error';
            resultMessage.textContent = error.message;
            resultScore.textContent = '--';
            resultIcon.innerHTML = iconPhish;
        } finally {
            scanBtn.disabled = false;
            scanBtn.textContent = originalText;
        }
    });
});
