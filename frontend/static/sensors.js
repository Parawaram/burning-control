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

  if (data.ina219) {
    const v = data.ina219;
    document.getElementById('bus_voltage').textContent =
      v.bus_voltage !== undefined ? v.bus_voltage : '--';
    document.getElementById('shunt_voltage').textContent =
      v.shunt_voltage !== undefined ? v.shunt_voltage : '--';
    document.getElementById('current').textContent =
      v.current !== undefined ? v.current : '--';
    document.getElementById('power').textContent =
      v.power !== undefined ? v.power : '--';
    document.getElementById('ina_status').textContent = v.status || 'off';
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
}

fetchSensors();
startTimer();

