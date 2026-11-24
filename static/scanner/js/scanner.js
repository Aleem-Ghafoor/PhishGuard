
document.addEventListener('DOMContentLoaded', () => {

    // Form Elements
    const scanForm = document.getElementById('scanForm');
    const urlInput = document.getElementById('urlInput');
    const scanBtn = document.querySelector('.btn-scan');

    // Result Elements
    const resultCard = document.getElementById('resultCard');
    const resultTitle = document.getElementById('resultTitle');
    const resultMessage = document.getElementById('resultMessage');
    const resultScore = document.getElementById('resultScore');
    const resultIcon = document.getElementById('resultIcon');

    // Demo Buttons
    const demoPhishBtn = document.getElementById('demoPhishBtn');
    const demoSafeBtn = document.getElementById('demoSafeBtn');

    // SVG Icons
    const iconPhish = `
        <svg viewBox="0 0 24 24" fill="none"
             stroke="currentColor" stroke-width="2">
            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
            <line x1="12" y1="9" x2="12" y2="13"/>
            <line x1="12" y1="17" x2="12.01" y2="17"/>
        </svg>`;

    const iconSafe = `
        <svg viewBox="0 0 24 24" fill="none"
             stroke="currentColor" stroke-width="2">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
            <polyline points="9 12 11 14 15 10"/>
        </svg>`;

    // Hide Previous Result
    function hideResult() {
        if (resultCard) {
            resultCard.style.display = 'none';
        }

        demoPhishBtn?.classList.remove('active');
        demoSafeBtn?.classList.remove('active');
    }

    // Display Result
    function displayResult(prediction, score, isDemo = false) {

        if (!resultCard) return;

        resultCard.style.display = 'flex';

        const isPhishing = prediction.toLowerCase() === 'phishing';

        resultCard.classList.toggle('legitimate', !isPhishing);

        resultTitle.textContent = isDemo
            ? `Sample result: ${prediction}`
            : `Scan result: ${prediction}`;

        resultMessage.textContent = isDemo
            ? 'This is a simulated demonstration result, not an actual ML prediction.'
            : isPhishing
                ? 'Warning! The ML model classified this URL as potentially phishing.'
                : 'The ML model classified this URL as legitimate. Always practice safe browsing.';

        resultScore.textContent = score;

        resultIcon.innerHTML = isPhishing ? iconPhish : iconSafe;
    }

    // Demo: Phishing
    demoPhishBtn?.addEventListener('click', () => {

        hideResult();

        displayResult('Phishing', '0.92', true);

        demoPhishBtn.classList.add('active');
    });

    // Demo: Legitimate
    demoSafeBtn?.addEventListener('click', () => {

        hideResult();

        displayResult('Legitimate', '0.05', true);

        demoSafeBtn.classList.add('active');
    });

    // Actual ML Scan using Fetch API
    scanForm?.addEventListener('submit', async (event) => {

        event.preventDefault();

        const url = urlInput.value.trim();

        if (!url) {
            hideResult();
            resultCard.style.display = 'flex';
            resultTitle.textContent = 'Invalid URL';
            resultMessage.textContent = 'Please enter a URL.';
            return;
        }

        hideResult();

        // Loading State
        const originalText = scanBtn.textContent;

        scanBtn.disabled = true;
        scanBtn.textContent = 'Scanning...';

        try {

            const csrfToken = scanForm.querySelector(
                '[name=csrfmiddlewaretoken]'
            ).value;

            const formData = new FormData(scanForm);

            const response = await fetch(
                scanForm.dataset.apiUrl,
                {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken
                    },
                    body: formData
                }
            );

            const data = await response.json();

            if (!response.ok || !data.success) {
                throw new Error(data.message || 'Scanning failed.');
            }

            const result = data.result;

            // Actual ML Result
            displayResult(
                result.prediction,
                result.phishing_probability
            );

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
