document.addEventListener('DOMContentLoaded', function () {
  requireAuth();
  loadUrlAnalytics();
});

async function loadUrlAnalytics() {
  try {
    const params = new URLSearchParams(window.location.search);
    const urlId = params.get('id');
    if (!urlId) {
      document.querySelector('.analytics-stats').classList.add('hidden');
      document.querySelector('.analytics-charts').classList.add('hidden');
      document.getElementById('analyticsEmptyState').classList.remove('hidden');
      return;
    }

    const analytics = await apiRequest(`/api/analytics/${urlId}`, { token: getToken() });

    document.getElementById('totalClicks').textContent = analytics.total_clicks || 0;
    document.getElementById('clicksToday').textContent = analytics.clicks_today || 0;
    document.getElementById('clicksWeek').textContent = analytics.clicks_this_week || 0;
    document.getElementById('clicksMonth').textContent = analytics.clicks_this_month || 0;

    renderLineChart(analytics.clicks_by_date || {});
    renderPieChart('deviceChart', analytics.device_breakdown || {}, 'Devices');
    renderBarChart('browserChart', analytics.browser_breakdown || {}, 'Browsers');
  } catch (error) {
    console.error(error);
    alert(error.message || 'Unable to load analytics');
  }
}

function renderLineChart(data) {
  const labels = Object.keys(data);
  const values = Object.values(data);

  if (!labels.length) {
    renderEmptyChart('lineChart', 'No click activity yet.');
    return;
  }

  new Chart(document.getElementById('lineChart'), {
    type: 'line',
    data: {
      labels,
      datasets: [{
        label: 'Clicks',
        data: values,
        borderColor: '#2563eb',
        backgroundColor: 'rgba(37, 99, 235, 0.2)',
        fill: true,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            precision: 0,
          },
        },
      },
    },
  });
}

function renderPieChart(canvasId, data, label) {
  if (!Object.keys(data).length) {
    renderEmptyChart(canvasId, `No ${label.toLowerCase()} data yet.`);
    return;
  }

  new Chart(document.getElementById(canvasId), {
    type: 'doughnut',
    data: {
      labels: Object.keys(data),
      datasets: [{
        label,
        data: Object.values(data),
        backgroundColor: ['#3b82f6', '#10b981', '#f59e0b', '#ef4444'],
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            precision: 0,
          },
        },
      },
    },
  });
}

function renderBarChart(canvasId, data, label) {
  if (!Object.keys(data).length) {
    renderEmptyChart(canvasId, `No ${label.toLowerCase()} data yet.`);
    return;
  }

  new Chart(document.getElementById(canvasId), {
    type: 'bar',
    data: {
      labels: Object.keys(data),
      datasets: [{
        label,
        data: Object.values(data),
        backgroundColor: '#84cc16',
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
    },
  });
}

function renderEmptyChart(canvasId, message) {
  const canvas = document.getElementById(canvasId);
  canvas.classList.add('hidden');

  const emptyState = document.createElement('p');
  emptyState.className = 'chart-empty';
  emptyState.textContent = message;
  canvas.parentElement.appendChild(emptyState);
}
