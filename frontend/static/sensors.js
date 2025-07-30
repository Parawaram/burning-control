let interval = 1000;
let timerId = null;

function startTimer() {
  if (timerId) clearInterval(timerId);
  timerId = setInterval(fetchSensors, interval);
}

document.getElementById('updateInterval')?.addEventListener('change', (e) => {
  interval = parseInt(e.target.value);
  startTimer();
});

async function fetchSensors() {
  const resp = await fetch('/api/sensors');
  const data = await resp.json();

  if (data.temperature !== undefined && data.temperature !== null) {
    document.getElementById('temperature').textContent = data.temperature;
  }


  if (data.aht20) {
    for (let i = 1; i <= 2; i++) {
      const val = data.aht20[i];
      document.getElementById(`aht${i}_temp`).textContent =
        val && val.temperature !== undefined ? val.temperature : '--';
      document.getElementById(`aht${i}_hum`).textContent =
        val && val.humidity !== undefined ? val.humidity : '--';
      document.getElementById(`aht${i}_status`).textContent =
        val ? val.status : 'off';
    }
  }

  if (data.dht11) {
    const v = data.dht11;
    document.getElementById('dht_temp').textContent =
      v.temperature !== undefined ? v.temperature : '--';
    document.getElementById('dht_hum').textContent =
      v.humidity !== undefined ? v.humidity : '--';
    document.getElementById('dht_status').textContent = v.status || 'off';
  }
}

fetchSensors();
startTimer();

