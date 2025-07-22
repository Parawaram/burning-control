async function fetchTelemetry() {
  const resp = await fetch('/api/telemetry');
  const data = await resp.json();
  document.getElementById('cpu_temp').textContent = data.cpu_temp ?? 'N/A';
  document.getElementById('cpu_freq').textContent = data.cpu_freq ?? 'N/A';
  document.getElementById('mem_used').textContent = data.mem_used ?? 'N/A';
  document.getElementById('mem_total').textContent = data.mem_total ?? 'N/A';
  document.getElementById('disk_used').textContent = data.disk_used ?? 'N/A';
  document.getElementById('disk_total').textContent = data.disk_total ?? 'N/A';
}
fetchTelemetry();
setInterval(fetchTelemetry, 1000);
