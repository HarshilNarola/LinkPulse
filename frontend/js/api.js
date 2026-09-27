// Set this to the public backend URL after deployment, for example:
// window.LINKPULSE_PUBLIC_API_URL = 'https://links.example.com';
const configuredApiUrl = window.LINKPULSE_PUBLIC_API_URL || '';
const localFrontendPort = window.location.port === '5500';
const apiHost = window.location.hostname;
const localApiUrl = `${window.location.protocol}//${apiHost}:8000`;
const API_BASE_URL = configuredApiUrl || (localFrontendPort ? localApiUrl : window.location.origin);

async function copyTextToClipboard(text) {
  if (navigator.clipboard) {
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch (error) {
      // Continue with the legacy method for HTTP/LAN pages.
    }
  }

  const textArea = document.createElement('textarea');
  textArea.value = text;
  textArea.style.position = 'fixed';
  textArea.style.top = '0';
  textArea.style.left = '0';
  textArea.style.opacity = '0';
  document.body.appendChild(textArea);
  textArea.focus();
  textArea.select();
  textArea.setSelectionRange(0, text.length);
  let copied = false;
  try {
    copied = document.execCommand('copy');
  } catch (error) {
    copied = false;
  }
  textArea.remove();

  if (!copied) {
    window.prompt('Copy this shortened URL:', text);
    return false;
  }

  return true;
}

function showCopyToast(message = 'Link copied!') {
  const toast = document.createElement('div');
  toast.className = 'copy-toast';
  toast.textContent = message;
  document.body.appendChild(toast);
  requestAnimationFrame(() => toast.classList.add('visible'));
  setTimeout(() => {
    toast.classList.remove('visible');
    setTimeout(() => toast.remove(), 220);
  }, 1800);
}

async function apiRequest(path, { method = 'GET', body = null, token = null, requiresAuth = true } = {}) {
  const headers = {
    'Content-Type': 'application/json',
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const config = {
    method,
    headers,
  };

  if (body !== null) {
    config.body = JSON.stringify(body);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, config);

  if (response.status === 204) {
    return null;
  }

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    const message = data.detail || 'Request failed';
    throw new Error(message);
  }

  return data;
}
