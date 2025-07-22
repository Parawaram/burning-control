const MAX_POINTS = 60;

function makeChart(ctx, label, color, max=null) {
  const options = {
    animation: false,
    responsive: true,
    scales: { y: { beginAtZero: true } }
  };
  if (max !== null) {
    options.scales.y.max = max;
  }
  return new Chart(ctx, {
    type: 'line',
    data: { labels: [], datasets: [{ label, data: [], borderColor: color, tension: 0.1 }] },
    options
  });
}

const cpuTempChart = makeChart(document.getElementById('cpuTempChart'), 'CPU Temp \u00B0C', 'rgb(255,99,132)');
const cpuFreqChart = makeChart(document.getElementById('cpuFreqChart'), 'CPU Freq MHz', 'rgb(54,162,235)');
const cpuUsageChart = makeChart(document.getElementById('cpuUsageChart'), 'CPU Usage %', 'rgb(255,205,86)', 100);
const memChart = makeChart(document.getElementById('memChart'), 'Memory MB', 'rgb(75,192,192)');
const diskChart = makeChart(document.getElementById('diskChart'), 'Disk GB', 'rgb(153,102,255)');
const cpuTempValue = document.getElementById('cpuTempValue');
const cpuFreqValue = document.getElementById('cpuFreqValue');
const cpuUsageValue = document.getElementById('cpuUsageValue');
const memValue = document.getElementById('memValue');
const diskValue = document.getElementById('diskValue');

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
  if (data.cpu_temp !== null) {
    pushData(cpuTempChart, data.cpu_temp);
    cpuTempValue.textContent = data.cpu_temp;
  }
  if (data.cpu_freq !== null) {
    pushData(cpuFreqChart, data.cpu_freq);
    cpuFreqValue.textContent = data.cpu_freq;
  }
  if (data.cpu_usage !== null) {
    pushData(cpuUsageChart, data.cpu_usage);
    cpuUsageValue.textContent = data.cpu_usage;
  }
  if (data.mem_used !== null) {
    pushData(memChart, data.mem_used);
    memValue.textContent = `${data.mem_used}/${data.mem_total}`;
  }
  if (data.disk_used !== null) {
    pushData(diskChart, data.disk_used);
    diskValue.textContent = `${data.disk_used}/${data.disk_total}`;
  }
}

fetchTelemetry();
setInterval(fetchTelemetry, 1000);
