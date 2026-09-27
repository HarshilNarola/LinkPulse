document.addEventListener('DOMContentLoaded', function () {
  requireAuth();
  loadAdminData();
});

async function loadAdminData() {
  try {
    const stats = await apiRequest('/api/admin/statistics', { token: getToken() });
    document.getElementById('totalUsers').textContent = stats.total_users || 0;
    document.getElementById('activeUsers').textContent = stats.active_users || 0;
    document.getElementById('totalUrls').textContent = stats.total_urls || 0;
    document.getElementById('totalClicks').textContent = stats.total_clicks || 0;

    const users = await apiRequest('/api/admin/users', { token: getToken() });
    renderUsersTable(users);

    const urls = await apiRequest('/api/admin/urls', { token: getToken() });
    renderAdminUrlsTable(urls);
  } catch (error) {
    console.error(error);
    alert(error.message || 'You do not have permission to view this page.');
  }
}

function renderUsersTable(users) {
  const container = document.getElementById('usersTable');
  if (!container) return;

  if (!users.length) {
    container.innerHTML = '<p>No users found.</p>';
    return;
  }

  container.innerHTML = `
    <table>
      <thead>
        <tr><th>Name</th><th>Email</th><th>Role</th><th>Status</th><th>Action</th></tr>
      </thead>
      <tbody>
        ${users.map((user) => `
          <tr>
            <td>${user.name}</td>
            <td>${user.email}</td>
            <td>${user.role}</td>
            <td>${user.is_active ? 'Active' : 'Inactive'}</td>
            <td>
              <button class="btn btn-secondary small" data-user-toggle="${user.id}" data-active="${user.is_active}">
                ${user.is_active ? 'Deactivate' : 'Activate'}
              </button>
            </td>
          </tr>
        `).join('')}
      </tbody>
    </table>
  `;

  container.querySelectorAll('[data-user-toggle]').forEach((button) => {
    button.addEventListener('click', async () => {
      const id = button.getAttribute('data-user-toggle');
      const nextState = button.getAttribute('data-active') === 'true' ? false : true;
      await apiRequest(`/api/admin/users/${id}/status`, {
        method: 'PATCH',
        body: { is_active: nextState },
        token: getToken(),
      });
      loadAdminData();
    });
  });
}

function renderAdminUrlsTable(urls) {
  const container = document.getElementById('adminUrlsTable');
  if (!container) return;

  if (!urls.length) {
    container.innerHTML = '<p>No URLs found.</p>';
    return;
  }

  container.innerHTML = `
    <table>
      <thead>
        <tr><th>User</th><th>Original URL</th><th>Short Code</th><th>Status</th></tr>
      </thead>
      <tbody>
        ${urls.map((url) => `
          <tr>
            <td>${url.user_id}</td>
            <td>${url.original_url}</td>
            <td>${url.short_code}</td>
            <td>${url.is_active ? 'Active' : 'Inactive'}</td>
          </tr>
        `).join('')}
      </tbody>
    </table>
  `;
}
