document.addEventListener('DOMContentLoaded', () => {
  const editBtn = document.getElementById('editBtn');
  const saveBtn = document.getElementById('saveBtn');
  const cancelBtn = document.getElementById('cancelBtn');
  const formInputs = document.querySelectorAll('#profileForm input[type="text"], #profileForm input[type="email"]');

  // Original values backup (agar cancel karna ho)
  let originalValues = {};
  formInputs.forEach(input => {
    originalValues[input.name] = input.value;
  });

  // Edit Profile Click
  if (editBtn) {
    editBtn.addEventListener('click', () => {
      formInputs.forEach(input => input.disabled = false);
      editBtn.style.display = 'none';
      saveBtn.style.display = 'inline-block';
      cancelBtn.style.display = 'inline-block';
    });
  }

  // Cancel Click
  if (cancelBtn) {
    cancelBtn.addEventListener('click', () => {
      formInputs.forEach(input => {
        input.disabled = true;
        input.value = originalValues[input.name]; // Restore original
      });
      editBtn.style.display = 'inline-block';
      saveBtn.style.display = 'none';
      cancelBtn.style.display = 'none';
    });
  }

  // Smooth scroll to password section
  window.scrollToPassword = function() {
    const passSection = document.getElementById('change-password');
    if (passSection) {
      passSection.scrollIntoView({ behavior: 'smooth' });
    }
  };
});