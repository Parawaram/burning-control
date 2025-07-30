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
  if (data.ts !== undefined) {
    document.getElementById('ts').textContent = data.ts;
  }
  if (data.voltageSensorV3 !== undefined) {
    document.getElementById('voltage').textContent = data.voltageSensorV3.voltage;
    document.getElementById('current').textContent = data.voltageSensorV3.current;
    document.getElementById('power').textContent = data.voltageSensorV3.power;
  }
  if (data.relay1 !== undefined && data.relay2 !== undefined) {
    document.getElementById('relays').textContent =
      `${data.relay1}, ${data.relay2}`;
  }
  if (data.button !== undefined) {
    document.getElementById('button').textContent = data.button;
  }
}

fetchTeency();
startTimer();
