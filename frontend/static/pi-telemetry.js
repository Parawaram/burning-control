const MAX_POINTS = 60;

function makeChart(ctx, label, color) {
  return new Chart(ctx, {
    type: 'line',
    data: { labels: [], datasets: [{ label, data: [], borderColor: color, tension: 0.1 }] },
    options: { animation: false, responsive: true, scales: { y: { beginAtZero: true } } }
  });
}

const cpuTempChart = makeChart(document.getElementById('cpuTempChart'), 'CPU Temp \u00B0C', 'rgb(255,99,132)');
const cpuFreqChart = makeChart(document.getElementById('cpuFreqChart'), 'CPU Freq MHz', 'rgb(54,162,235)');
const memChart = makeChart(document.getElementById('memChart'), 'Memory MB', 'rgb(75,192,192)');
const diskChart = makeChart(document.getElementById('diskChart'), 'Disk GB', 'rgb(153,102,255)');

function pushData(chart, value) {
  const labels = chart.data.labels;
  const data = chart.data.datasets[0].data;
  labels.push('');
  data.push(value);
  if (labels.length > MAX_POINTS) { labels.shift(); data.shift(); }
  chart.update();
}

async function fetchTelemetry() {
  const resp = await fetch('/api/telemetry');
  const data = await resp.json();
  if (data.cpu_temp !== null) pushData(cpuTempChart, data.cpu_temp);
  if (data.cpu_freq !== null) pushData(cpuFreqChart, data.cpu_freq);
  if (data.mem_used !== null) pushData(memChart, data.mem_used);
  if (data.disk_used !== null) pushData(diskChart, data.disk_used);
}

fetchTelemetry();
setInterval(fetchTelemetry, 1000);
