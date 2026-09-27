(function () {
  const THEME_KEY = 'linkpulse_theme';

  function getStoredTheme() {
    const savedTheme = localStorage.getItem(THEME_KEY);
    if (savedTheme === 'dark' || savedTheme === 'light') {
      return savedTheme;
    }
    return 'light';
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    if (document.body) {
      document.body.setAttribute('data-theme', theme);
    }

    const themeButton = document.getElementById('themeToggleBtn');
    if (themeButton) {
      themeButton.textContent = theme === 'dark' ? 'Light mode' : 'Dark mode';
    }
  }

  function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
    const nextTheme = currentTheme === 'dark' ? 'light' : 'dark';
    localStorage.setItem(THEME_KEY, nextTheme);
    applyTheme(nextTheme);
  }

  function ensureToggleButton() {
    let button = document.getElementById('themeToggleBtn');
    if (button) {
      return button;
    }

    button = document.createElement('button');
    button.id = 'themeToggleBtn';
    button.type = 'button';
    button.textContent = 'Dark mode';
    document.body.appendChild(button);
    return button;
  }

  document.addEventListener('DOMContentLoaded', function () {
    applyTheme(getStoredTheme());
    ensureToggleButton();
    const themeButton = document.getElementById('themeToggleBtn');
    if (themeButton) {
      themeButton.addEventListener('click', toggleTheme);
    }
  });

  window.addEventListener('storage', function (event) {
    if (event.key === THEME_KEY && (event.newValue === 'dark' || event.newValue === 'light')) {
      applyTheme(event.newValue);
    }
  });

  window.linkpulseTheme = { applyTheme, toggleTheme };
})();
