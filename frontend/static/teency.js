let interval = 500;
let timerId = null;

function startTimer() {
  if (timerId) clearInterval(timerId);
  timerId = setInterval(fetchTeency, interval);
}

document.getElementById('updateInterval')?.addEventListener('change', (e) => {
  interval = parseInt(e.target.value);
  startTimer();
});

async function fetchTeency() {
  const resp = await fetch('/api/teency');
  const data = await resp.json();
  if (data.voltageSensorV3 !== undefined) {
    console.log(data)
    document.getElementById('ts').textContent = data.voltageSensorV3.current;
  }
  if (data.voltageSensorV3 !== undefined) {
    document.getElementById('voltage').textContent = data.voltageSensorV3.voltage;
  }
  if (data.I !== undefined) {
    document.getElementById('current').textContent = data.I;
  }
  if (data.P !== undefined) {
    document.getElementById('power').textContent = data.P;
  }
  if (Array.isArray(data.R)) {
    document.getElementById('relays').textContent = data.R.join(', ');
  }
  if (data.B !== undefined) {
    document.getElementById('button').textContent = data.B;
  }
}

fetchTeency();
startTimer();
