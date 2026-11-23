/**
 * PhishGuard — Registration Page JS
 * - Password visibility toggles
 * - Client-side password match feedback
 * - Basic interactive validation
 * - Prevents accidental multiple submissions
 *
 * NOTE: This is UX enhancement ONLY.
 * Django server-side validation remains the source of truth.
 */
(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('registerForm');
    if (!form) return;

    const submitBtn = document.getElementById('submitBtn');
    const password1 = document.getElementById('id_password1');
    const password2 = document.getElementById('id_password2');
    const matchHint = document.getElementById('passwordMatchHint');
    const emailInput = document.getElementById('id_email');

    /* ============================================
       1. Password Visibility Toggles
       ============================================ */
    document.querySelectorAll('.toggle-password').forEach(function (btn) {
      btn.addEventListener('click', function () {
        const targetId = btn.getAttribute('data-target');
        const input = document.getElementById(targetId);
        if (!input) return;

        const isPassword = input.type === 'password';
        input.type = isPassword ? 'text' : 'password';

        const eyeOpen = btn.querySelector('.eye-open');
        const eyeClosed = btn.querySelector('.eye-closed');
        if (eyeOpen && eyeClosed) {
          eyeOpen.style.display = isPassword ? 'none' : 'block';
          eyeClosed.style.display = isPassword ? 'block' : 'none';
        }

        btn.setAttribute(
          'aria-label',
          isPassword ? 'Hide password' : 'Show password'
        );
      });
    });

    /* ============================================
       2. Password Confirmation Feedback
       ============================================ */
    function checkPasswordMatch() {
      if (!password1 || !password2 || !matchHint) return;
      const p1 = password1.value;
      const p2 = password2.value;

      matchHint.classList.remove('match', 'mismatch');
      password2.classList.remove('valid', 'invalid');

      if (p2.length === 0) {
        matchHint.textContent = '';
        return;
      }

      if (p1 === p2) {
        matchHint.textContent = '✓ Passwords match';
        matchHint.classList.add('match');
        password2.classList.add('valid');
      } else {
        matchHint.textContent = '✗ Passwords do not match';
        matchHint.classList.add('mismatch');
        password2.classList.add('invalid');
      }
    }

    if (password1 && password2) {
      password1.addEventListener('input', checkPasswordMatch);
      password2.addEventListener('input', checkPasswordMatch);
    }

    /* ============================================
       3. Basic Interactive Validation
       ============================================ */
    function markInvalid(input) {
      if (!input) return;
      input.classList.add('invalid');
    }

    function clearInvalid(input) {
      if (!input) return;
      input.classList.remove('invalid');
    }

    // Email format check (basic client-side UX)
    if (emailInput) {
      emailInput.addEventListener('blur', function () {
        const val = emailInput.value.trim();
        if (val === '') {
          clearInvalid(emailInput);
          return;
        }
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (re.test(val)) {
          clearInvalid(emailInput);
        } else {
          markInvalid(emailInput);
        }
      });
      emailInput.addEventListener('input', function () {
        clearInvalid(emailInput);
      });
    }

    // Clear invalid state on typing in any input
    form.querySelectorAll('input').forEach(function (input) {
      input.addEventListener('input', function () {
        if (input !== emailInput && input !== password2) {
          clearInvalid(input);
        }
      });
    });

    /* ============================================
       4. Prevent Multiple Submissions
       ============================================ */
    let isSubmitting = false;

    form.addEventListener('submit', function (e) {
      if (isSubmitting) {
        e.preventDefault();
        return;
      }

      // Basic client-side checks (server-side still validates)
      let hasClientError = false;

      // Passwords must match (client UX only)
      if (password1 && password2) {
        if (password1.value !== password2.value) {
          markInvalid(password2);
          if (matchHint) {
            matchHint.textContent = '✗ Passwords do not match';
            matchHint.classList.add('mismatch');
          }
          hasClientError = true;
        }
      }

      if (hasClientError) {
        e.preventDefault();
        return;
      }

      // Allow submit, but lock the button
      isSubmitting = true;
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.classList.add('loading');
      }
    });

    /* ============================================
       5. Re-enable button on page restore (bfcache)
       ============================================ */
    window.addEventListener('pageshow', function (event) {
      if (event.persisted) {
        isSubmitting = false;
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.classList.remove('loading');
        }
      }
    });
  });
})();