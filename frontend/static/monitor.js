async function fetchStatus() {
  const resp = await fetch('/api/status');
  const data = await resp.json();
  document.getElementById('temperature').textContent = data.temperature;
  document.getElementById('suit_temperature').textContent = data.suit_temperature;
  document.getElementById('voltage').textContent = data.voltage;
  document.getElementById('cooling_status').textContent = data.cooling_status;
  document.getElementById('fans').textContent = data.fans;
}
fetchStatus();
// Update the status every second
setInterval(fetchStatus, 1000);
