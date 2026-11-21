/**
 * PhishGuard Login JS
 * Only contains Show/Hide Password functionality.
 */
document.addEventListener('DOMContentLoaded', function () {
  const toggleBtn = document.getElementById('togglePassword');
  const passwordInput = document.getElementById('id_password'); 
  // Note: Django default id for password field is 'id_password'

  if (toggleBtn && passwordInput) {
    toggleBtn.addEventListener('click', function (e) {
      e.preventDefault();
      
      // Toggle type
      const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
      passwordInput.setAttribute('type', type);
      
      // Toggle icon
      const eyeOpen = toggleBtn.querySelector('.eye-open');
      const eyeClosed = toggleBtn.querySelector('.eye-closed');
      
      if (type === 'text') {
        eyeOpen.style.display = 'none';
        eyeClosed.style.display = 'block';
        toggleBtn.setAttribute('aria-label', 'Hide password');
      } else {
        eyeOpen.style.display = 'block';
        eyeClosed.style.display = 'none';
        toggleBtn.setAttribute('aria-label', 'Show password');
      }
    });
  }
});