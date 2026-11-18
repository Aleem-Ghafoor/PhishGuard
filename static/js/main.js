/* ============================================================
   PhishGuard — Homepage Interactions
   Vanilla JavaScript only — no dependencies
   ============================================================ */

(function () {
    'use strict';

    /* ------------------------------------------------------------
       1. Mobile navigation (hamburger toggle)
       ------------------------------------------------------------ */
    const navToggle = document.getElementById('navToggle');
    const navMenu   = document.getElementById('navMenu');

    function closeNav() {
        if (!navMenu || !navToggle) return;
        navMenu.classList.remove('is-open');
        navToggle.classList.remove('is-open');
        navToggle.setAttribute('aria-expanded', 'false');
    }

    function openNav() {
        if (!navMenu || !navToggle) return;
        navMenu.classList.add('is-open');
        navToggle.classList.add('is-open');
        navToggle.setAttribute('aria-expanded', 'true');
    }

    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function () {
            const isOpen = navMenu.classList.contains('is-open');
            if (isOpen) closeNav();
            else openNav();
        });

        // Close menu when a link is clicked
        navMenu.querySelectorAll('a').forEach(function (link) {
            link.addEventListener('click', closeNav);
        });

        // Close on Escape
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') closeNav();
        });

        // Close if viewport grows past mobile breakpoint
        window.addEventListener('resize', function () {
            if (window.innerWidth > 768) closeNav();
        });
    }

    /* ------------------------------------------------------------
       2. Smooth scrolling for in-page anchor links
          (CSS scroll-behavior already helps, but we handle
          offset-aware scrolling and CTA target here)
       ------------------------------------------------------------ */
    const NAV_OFFSET = 72; // matches --nav-height

    function scrollToTarget(targetEl, extraOffset) {
        if (!targetEl) return;
        const offset = (extraOffset !== undefined ? extraOffset : NAV_OFFSET);
        const rect   = targetEl.getBoundingClientRect();
        const top    = rect.top + window.pageYOffset - offset;
        window.scrollTo({ top: top, behavior: 'smooth' });

        // Move focus for accessibility
        if (typeof targetEl.focus === 'function') {
            targetEl.focus({ preventScroll: true });
        }
    }

    document.querySelectorAll('a[href^="#"]').forEach(function (link) {
        link.addEventListener('click', function (e) {
            const href = link.getAttribute('href');

            // Special: CTA "Start Scanning Now" scrolls to the URL input
            if (link.dataset.scrollTo) {
                const inputTarget = document.getElementById(link.dataset.scrollTo);
                if (inputTarget) {
                    e.preventDefault();
                    scrollToTarget(inputTarget, NAV_OFFSET + 40);
                    return;
                }
            }

            if (!href || href === '#') return;

            const target = document.querySelector(href);
            if (!target) return;

            e.preventDefault();
            scrollToTarget(target, NAV_OFFSET);
        });
    });

    /* ------------------------------------------------------------
       3. Active nav-link highlighting on scroll
       ------------------------------------------------------------ */
    const sectionIds = ['home', 'about', 'features', 'faq', 'contact'];
    const navLinks   = document.querySelectorAll('.navbar__link');

    function setActiveLink(id) {
        navLinks.forEach(function (link) {
            const href = link.getAttribute('href');
            link.classList.toggle('is-active', href === '#' + id);
        });
    }

    const sectionEls = sectionIds
        .map(function (id) { return document.getElementById(id); })
        .filter(Boolean);

    if ('IntersectionObserver' in window && sectionEls.length) {
        const navObserver = new IntersectionObserver(
            function (entries) {
                entries.forEach(function (entry) {
                    if (entry.isIntersecting) {
                        setActiveLink(entry.target.id);
                    }
                });
            },
            {
                rootMargin: '-45% 0px -45% 0px',
                threshold: 0
            }
        );
        sectionEls.forEach(function (el) { navObserver.observe(el); });
    }

    /* ------------------------------------------------------------
       4. URL scanner form — validation + placeholder message
          (Backend integration comes later; no fake predictions.)
       ------------------------------------------------------------ */
    const scannerForm    = document.getElementById('urlScanner');
    const urlInput       = document.getElementById('urlInput');
    const scannerMessage = document.getElementById('scannerMessage');

    // Basic URL validator — requires http(s):// and a dot in the hostname
    function isValidUrl(value) {
        if (!value) return false;
        try {
            const parsed = new URL(value);
            if (!/^https?:$/.test(parsed.protocol)) return false;
            return parsed.hostname.includes('.');
        } catch (_err) {
            return false;
        }
    }

    function showMessage(text, type) {
        if (!scannerMessage) return;
        scannerMessage.textContent = text;
        scannerMessage.classList.remove('is-error', 'is-info', 'is-success');
        if (type) scannerMessage.classList.add('is-' + type);
    }

    if (scannerForm && urlInput) {
        scannerForm.addEventListener('submit', function (e) {
            e.preventDefault();

            const value = urlInput.value.trim();

            // Empty input
            if (!value) {
                showMessage('Please enter a URL to scan.', 'error');
                urlInput.focus();
                return;
            }

            // Invalid format
            if (!isValidUrl(value)) {
                showMessage(
                    'That doesn\u2019t look like a valid URL. Try something like https://example.com',
                    'error'
                );
                urlInput.focus();
                return;
            }

            // Valid format — backend not yet connected
            showMessage(
                'URL format looks good! Scanning is not connected yet — this will link to the backend soon.',
                'info'
            );

            // Optional: brief button feedback
            const submitBtn = scannerForm.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.dataset.originalLabel = submitBtn.innerHTML;
                submitBtn.innerHTML = 'Checking…';
                setTimeout(function () {
                    submitBtn.disabled = false;
                    if (submitBtn.dataset.originalLabel) {
                        submitBtn.innerHTML = submitBtn.dataset.originalLabel;
                    }
                }, 900);
            }
        });

        // Clear error state when typing again
        urlInput.addEventListener('input', function () {
            if (scannerMessage && scannerMessage.classList.contains('is-error')) {
                showMessage('', '');
            }
        });
    }

    /* ------------------------------------------------------------
       5. FAQ accordion
       ------------------------------------------------------------ */
    const faqItems = document.querySelectorAll('.faq-item');

    faqItems.forEach(function (item) {
        const btn    = item.querySelector('.faq-item__question');
        const answer = item.querySelector('.faq-item__answer');
        if (!btn || !answer) return;

        btn.addEventListener('click', function () {
            const isOpen = item.classList.contains('is-open');

            // Close all others (single-open behaviour)
            faqItems.forEach(function (other) {
                if (other !== item) {
                    other.classList.remove('is-open');
                    const otherBtn = other.querySelector('.faq-item__question');
                    if (otherBtn) otherBtn.setAttribute('aria-expanded', 'false');
                }
            });

            // Toggle current
            item.classList.toggle('is-open', !isOpen);
            btn.setAttribute('aria-expanded', String(!isOpen));
        });
    });

    /* ------------------------------------------------------------
       6. Scroll-in reveal animations
       ------------------------------------------------------------ */
    const revealTargets = document.querySelectorAll(
        '.section-head, .feature-card, .how__step, .stats__grid, .cta__inner, .faq-item'
    );

    revealTargets.forEach(function (el) { el.classList.add('reveal'); });

    if ('IntersectionObserver' in window && revealTargets.length) {
        const revealObserver = new IntersectionObserver(
            function (entries, observer) {
                entries.forEach(function (entry) {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('is-visible');
                        observer.unobserve(entry.target);
                    }
                });
            },
            { rootMargin: '0px 0px -10% 0px', threshold: 0.12 }
        );

        revealTargets.forEach(function (el) { revealObserver.observe(el); });
    } else {
        // Fallback: show everything
        revealTargets.forEach(function (el) { el.classList.add('is-visible'); });
    }

})();