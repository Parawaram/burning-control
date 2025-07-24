let interval = 1000;
let timerId = null;

function startTimer() {
  if (timerId) clearInterval(timerId);
  timerId = setInterval(fetchCooling, interval);
}

document.getElementById('updateInterval')?.addEventListener('change', (e) => {
  interval = parseInt(e.target.value);
  startTimer();
});

async function fetchCooling() {
  const resp = await fetch('/api/sensors');
  const data = await resp.json();
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

fetchCooling();
startTimer();

