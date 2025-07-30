const sensors = {
  voltageSensorV3: 'vs_v3_',
  voltageSensorV5: 'vs_v5_',
  voltageSensorV5PiBrain: 'vs_v5pi_',
  voltageSensorV24: 'vs_v24_',
};

let interval = 500;
let timerId = null;

function startTimer() {
  if (timerId) clearInterval(timerId);
  timerId = setInterval(fetchVoltages, interval);
}

document.getElementById('updateInterval')?.addEventListener('change', (e) => {
  interval = parseInt(e.target.value);
  startTimer();
});

async function fetchVoltages() {
  const resp = await fetch('/api/teency');
  const data = await resp.json();

  for (const [key, prefix] of Object.entries(sensors)) {
    const s = data[key] || {};
    document.getElementById(prefix + 'voltage').textContent =
      s.voltage !== undefined ? s.voltage : '--';
    document.getElementById(prefix + 'current').textContent =
      s.current !== undefined ? s.current : '--';
    document.getElementById(prefix + 'power').textContent =
      s.power !== undefined ? s.power : '--';
    document.getElementById(prefix + 'status').textContent =
      s.isAvailable !== undefined ? (s.isAvailable ? 'on' : 'off') : 'off';
  }
}

fetchVoltages();
startTimer();
