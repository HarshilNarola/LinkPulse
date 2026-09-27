document.addEventListener('DOMContentLoaded', function () {
  requireAuth();

  const token = getToken();
  const user = getCurrentUser();
  const welcomeText = document.getElementById('welcomeText');
  if (welcomeText && user) {
    welcomeText.textContent = `Welcome, ${user.name || user.sub || 'User'}`;
  }

  loadUserUrls();
  attachCreateFormHandler();

  const adminLink = document.getElementById('adminLink');
  if (adminLink && user && user.role === 'ADMIN') {
    adminLink.hidden = false;
  }
});

async function loadUserUrls() {
  try {
    const urls = await apiRequest('/api/urls', { token: getToken() });
    const container = document.getElementById('urlTableContainer');
    const totalUrls = document.getElementById('totalUrls');
    const totalClicks = document.getElementById('totalClicks');

    if (!container) return;

    if (totalUrls) totalUrls.textContent = urls.length;
    if (totalClicks) {
      totalClicks.textContent = urls.reduce((sum, url) => sum + (url.click_count || 0), 0);
    }

    if (!urls.length) {
      container.innerHTML = '<p>No URLs yet.</p>';
      return;
    }

    const rows = urls.map((url) => {
      const shortUrl = `${API_BASE_URL}/${url.short_code}`;
      return `
        <tr>
          <td>${url.original_url}</td>
          <td><a href="${shortUrl}" target="_blank">${shortUrl}</a></td>
          <td>${new Date(url.created_at).toLocaleDateString()}</td>
          <td>${url.is_active ? 'Active' : 'Disabled'}</td>
          <td>${url.click_count}</td>
          <td>
            <a href="analytics.html?id=${url.id}" class="btn btn-secondary small">Analytics</a>
            <button class="btn btn-secondary small" data-action="copy" data-url="${shortUrl}">Copy</button>
            <button class="btn btn-secondary small" data-action="toggle" data-id="${url.id}" data-status="${url.is_active}">${url.is_active ? 'Disable' : 'Enable'}</button>
            <button class="btn btn-secondary small" data-action="delete" data-id="${url.id}">Delete</button>
          </td>
        </tr>
      `;
    }).join('');

    container.innerHTML = `
      <table>
        <thead>
          <tr>
            <th>Original URL</th>
            <th>Short URL</th>
            <th>Created</th>
            <th>Status</th>
            <th>Clicks</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          ${rows}
        </tbody>
      </table>
    `;

    container.querySelectorAll('[data-action="toggle"]').forEach((button) => {
      button.addEventListener('click', async () => {
        const id = button.dataset.id;
        const status = button.dataset.status === 'true';
        await apiRequest(`/api/urls/${id}/status`, {
          method: 'PATCH',
          body: { is_active: !status },
          token: getToken(),
        });
        loadUserUrls();
      });
    });

    container.querySelectorAll('[data-action="copy"]').forEach((button) => {
      button.addEventListener('click', async () => {
        try {
          const copied = await copyTextToClipboard(button.dataset.url);
          button.textContent = copied ? 'Copied!' : 'Select and copy';
          showCopyToast(copied ? 'Link copied!' : 'Copy the URL from the dialog.');
          setTimeout(() => {
            button.textContent = 'Copy';
          }, 1500);
        } catch (error) {
          showCopyToast(error.message);
        }
      });
    });

    container.querySelectorAll('[data-action="delete"]').forEach((button) => {
      button.addEventListener('click', async () => {
        const id = button.dataset.id;
        await apiRequest(`/api/urls/${id}`, {
          method: 'DELETE',
          token: getToken(),
        });
        loadUserUrls();
      });
    });
  } catch (error) {
    console.error(error);
    const container = document.getElementById('urlTableContainer');
    if (container) container.innerHTML = `<p>${error.message}</p>`;
  }
}

function attachCreateFormHandler() {
  const form = document.getElementById('createUrlForm');
  if (!form) return;

  form.addEventListener('submit', async function (event) {
    event.preventDefault();
    const originalUrl = document.getElementById('originalUrl').value;
    const expiresAt = document.getElementById('expiresAt').value;
    const resultBox = document.getElementById('resultMessage');
    const shortUrlBox = document.getElementById('shortUrlBox');

    try {
      const payload = {
        original_url: originalUrl,
        expires_at: expiresAt ? new Date(expiresAt).toISOString() : null,
      };

      const created = await apiRequest('/api/urls', {
        method: 'POST',
        body: payload,
        token: getToken(),
      });

      const shortUrl = `${API_BASE_URL}/${created.short_code}`;
      shortUrlBox.classList.remove('hidden');
      shortUrlBox.innerHTML = `<strong>Short URL:</strong> <a href="${shortUrl}" target="_blank" rel="noopener">${shortUrl}</a> <button type="button" class="btn btn-secondary small" id="copyShortUrlBtn">Copy</button>`;
      document.getElementById('copyShortUrlBtn').addEventListener('click', async () => {
        try {
          const copied = await copyTextToClipboard(shortUrl);
          resultBox.textContent = copied
            ? 'Short URL copied to clipboard.'
            : 'Copy the URL from the dialog.';
          showCopyToast(copied ? 'Link copied!' : 'Copy the URL from the dialog.');
        } catch (error) {
          resultBox.textContent = error.message;
          showCopyToast(error.message);
        }
      });
      resultBox.textContent = 'URL created successfully.';
      form.reset();
      loadUserUrls();
    } catch (error) {
      resultBox.textContent = error.message;
    }
  });
}
