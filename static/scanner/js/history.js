
document.addEventListener("DOMContentLoaded", () => {
    // HTML elements
    const apiUrl = document.currentScript?.dataset.apiUrl ||
        "/scanner/history/api/";

    const searchInput = document.getElementById("searchInput");
    const resultFilter = document.getElementById("resultFilter");
    const dateFilter = document.getElementById("dateFilter");
    const clearBtn = document.getElementById("clearFiltersBtn");

    const tableBody = document.getElementById("historyTableBody");
    const loadingState = document.getElementById("loadingState");
    const paginationControls = document.getElementById("paginationControls");
    const pageInfo = document.getElementById("pageInfo");

    const statTotal = document.getElementById("stat-total");
    const statLegit = document.getElementById("stat-legit");
    const statPhish = document.getElementById("stat-phish");
    const statRate = document.getElementById("stat-rate");

    const ITEMS_PER_PAGE = 10;

    let allScans = [];
    let currentPage = 1;
    let debounceTimer;

    // Fetch records from Django API
    async function loadHistory() {
        loadingState.style.display = "flex";

        try {
            const response = await fetch(apiUrl, {
                method: "GET",
                headers: {
                    "Accept": "application/json"
                },
                credentials: "same-origin"
            });

            if (!response.ok) {
                throw new Error(`HTTP Error: ${response.status}`);
            }

            const data = await response.json();

            if (data.status !== "success") {
                throw new Error("Invalid API response");
            }

            allScans = data.scans || [];

            updateStats();
            applyFilters();

        } catch (error) {
            console.error("History loading error:", error);

            tableBody.innerHTML = `
                <tr>
                    <td colspan="6" style="text-align:center; padding:40px;">
                        Failed to load history. Please try again.
                    </td>
                </tr>
            `;
        } finally {
            loadingState.style.display = "none";
        }
    }

    // Update summary cards
    function updateStats() {
        const total = allScans.length;

        const legitimate = allScans.filter(
            scan => scan.prediction === "Legitimate"
        ).length;

        const phishing = allScans.filter(
            scan => scan.prediction === "Phishing"
        ).length;

        const phishingRate = total > 0
            ? ((phishing / total) * 100).toFixed(1)
            : 0;

        statTotal.textContent = total;
        statLegit.textContent = legitimate;
        statPhish.textContent = phishing;
        statRate.textContent = phishingRate + "%";
    }

    // Search and filter records
    function applyFilters() {
        const search = searchInput.value.trim().toLowerCase();
        const result = resultFilter.value;
        const date = dateFilter.value;

        let filteredScans = allScans.filter(scan => {

            const matchesSearch = scan.url
                .toLowerCase()
                .includes(search);

            const matchesResult = !result ||
                scan.prediction === result;

            let matchesDate = true;

            if (date) {
                const scanDate = new Date(scan.scanned_at);
                const now = new Date();

                const startOfToday = new Date(
                    now.getFullYear(),
                    now.getMonth(),
                    now.getDate()
                );

                if (date === "today") {
                    matchesDate = scanDate >= startOfToday &&
                        scanDate <= now;
                }

                if (date === "last_7_days") {
                    const last7Days = new Date(startOfToday);
                    last7Days.setDate(
                        last7Days.getDate() - 6
                    );

                    matchesDate = scanDate >= last7Days &&
                        scanDate <= now;
                }

                if (date === "last_30_days") {
                    const last30Days = new Date(startOfToday);
                    last30Days.setDate(
                        last30Days.getDate() - 29
                    );

                    matchesDate = scanDate >= last30Days &&
                        scanDate <= now;
                }
            }

            return matchesSearch &&
                matchesResult &&
                matchesDate;
        });

        currentPage = 1;
        renderTable(filteredScans);
    }

    // Render table and pagination
    function renderTable(scans) {
        const totalCount = scans.length;
        const totalPages = Math.ceil(
            totalCount / ITEMS_PER_PAGE
        );

        if (totalCount === 0) {
            tableBody.innerHTML = `
                <tr class="empty-row">
                    <td colspan="6">
                        <div class="empty-state">
                            <p>No scan history found.</p>
                        </div>
                    </td>
                </tr>
            `;

            pageInfo.textContent = "Showing 0 scans";
            paginationControls.innerHTML = "";
            return;
        }

        const startIndex = (currentPage - 1) * ITEMS_PER_PAGE;

        const pageScans = scans.slice(
            startIndex,
            startIndex + ITEMS_PER_PAGE
        );

        tableBody.innerHTML = "";

        pageScans.forEach((scan, index) => {
            const row = document.createElement("tr");

            const serial = startIndex + index + 1;

            const badgeClass =
                scan.prediction === "Phishing"
                    ? "phishing"
                    : "legitimate";

            // Create URL cell safely
            const urlCell = document.createElement("td");
            urlCell.className = "url-cell";

            const urlLink = document.createElement("a");
            urlLink.className = "url-link";
            urlLink.textContent = scan.url;
            urlLink.target = "_blank";
            urlLink.rel = "noopener noreferrer";

            try {
                const parsedUrl = new URL(scan.url);

                if (
                    parsedUrl.protocol === "http:" ||
                    parsedUrl.protocol === "https:"
                ) {
                    urlLink.href = parsedUrl.href;
                } else {
                    urlLink.removeAttribute("target");
                }
            } catch {
                urlLink.removeAttribute("target");
            }

            urlCell.appendChild(urlLink);

            // Create result badge
            const resultCell = document.createElement("td");
            const badge = document.createElement("span");

            badge.className = `badge ${badgeClass}`;
            badge.textContent = scan.prediction;

            resultCell.appendChild(badge);

            // Create score cell
            const scoreCell = document.createElement("td");
            scoreCell.className = "score-cell";

            const score = Number(scan.phishing_probability);

            scoreCell.textContent = Number.isFinite(score)
                ? score.toFixed(2)
                : "N/A";

            // Create date cell
            const dateCell = document.createElement("td");
            dateCell.className = "date-cell";
            dateCell.textContent = scan.scanned_at;

            // Create serial cell
            const serialCell = document.createElement("td");
            serialCell.className = "serial-num";
            serialCell.textContent = serial;

            // Create action cell
            const actionCell = document.createElement("td");
            actionCell.className = "action-cell";

            const actionButton = document.createElement("button");
            actionButton.className = "action-btn";
            actionButton.type = "button";
            actionButton.textContent = "...";
            actionButton.disabled = true;

            actionCell.appendChild(actionButton);

            row.append(
                serialCell,
                urlCell,
                resultCell,
                scoreCell,
                dateCell,
                actionCell
            );

            tableBody.appendChild(row);
        });

        updatePagination(totalPages, totalCount);
    }

    // Update pagination
    function updatePagination(totalPages, totalCount) {
        const start = (currentPage - 1) * ITEMS_PER_PAGE + 1;
        const end = Math.min(
            currentPage * ITEMS_PER_PAGE,
            totalCount
        );

        pageInfo.textContent =
            `Showing ${start}–${end} of ${totalCount} scans`;

        paginationControls.innerHTML = "";

        function createPageButton(label, page, disabled = false, active = false) {
            const button = document.createElement(
                disabled || active ? "span" : "a"
            );

            button.className = "page-btn";
            button.textContent = label;

            if (disabled) {
                button.classList.add("disabled");
            }

            if (active) {
                button.classList.add("active");
            }

            if (!disabled && !active) {
                button.href = "#";
                button.addEventListener("click", event => {
                    event.preventDefault();
                    currentPage = page;
                    applyFilters();
                });
            }

            return button;
        }

        paginationControls.appendChild(
            createPageButton(
                "‹",
                currentPage - 1,
                currentPage === 1
            )
        );

        for (let page = 1; page <= totalPages; page++) {
            if (
                page === 1 ||
                page === totalPages ||
                Math.abs(page - currentPage) <= 1
            ) {
                paginationControls.appendChild(
                    createPageButton(
                        String(page),
                        page,
                        false,
                        page === currentPage
                    )
                );
            }
        }

        paginationControls.appendChild(
            createPageButton(
                "›",
                currentPage + 1,
                currentPage === totalPages
            )
        );
    }

    // Search with debounce
    searchInput.addEventListener("input", () => {
        clearTimeout(debounceTimer);

        debounceTimer = setTimeout(() => {
            applyFilters();
        }, 300);
    });

    // Result filter
    resultFilter.addEventListener("change", applyFilters);

    // Date filter
    dateFilter.addEventListener("change", applyFilters);

    // Clear filters
    clearBtn.addEventListener("click", () => {
        searchInput.value = "";
        resultFilter.value = "";
        dateFilter.value = "";

        applyFilters();
    });

    // Initial load
    loadHistory();
});
