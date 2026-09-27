function saveToken(token) {
  localStorage.setItem('linkpulse_access_token', token);
}

function getToken() {
  return localStorage.getItem('linkpulse_access_token');
}

function isLoggedIn() {
  return Boolean(getToken());
}

function logout() {
  localStorage.removeItem('linkpulse_access_token');
  window.location.href = 'login.html';
}

function getCurrentUser() {
  const token = getToken();
  if (!token) {
    return null;
  }

  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    return payload;
  } catch (error) {
    return null;
  }
}

async function register(name, email, password) {
  const messageBox = document.getElementById('message');
  try {
    await apiRequest('/api/auth/register', {
      method: 'POST',
      body: { name, email, password },
      requiresAuth: false,
    });
    if (messageBox) {
      messageBox.textContent = 'Registration successful.';
      messageBox.style.color = '#15803d';
    }
    return { success: true };
  } catch (error) {
    if (messageBox) {
      messageBox.textContent = error.message;
      messageBox.style.color = '#b91c1c';
    }
    return { success: false, error: error.message };
  }
}

async function login(email, password) {
  const messageBox = document.getElementById('message');
  try {
    const data = await apiRequest('/api/auth/login', {
      method: 'POST',
      body: { email, password },
      requiresAuth: false,
    });
    saveToken(data.access_token);
    if (messageBox) {
      messageBox.textContent = 'Login successful.';
      messageBox.style.color = '#15803d';
    }
    return { success: true };
  } catch (error) {
    if (messageBox) {
      messageBox.textContent = error.message;
      messageBox.style.color = '#b91c1c';
    }
    return { success: false, error: error.message };
  }
}

function requireAuth() {
  if (!isLoggedIn()) {
    window.location.href = 'login.html';
  }
}

document.addEventListener('DOMContentLoaded', function () {
  const logoutBtn = document.getElementById('logoutBtn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', logout);
  }
});
