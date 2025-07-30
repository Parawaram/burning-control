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
  try {
    const resp = await fetch('/api/teency');
    const data = await resp.json();
    document.getElementById('teencyJson').textContent =
      JSON.stringify(data, null, 2);
    const status = data.status || 'error';
    document.getElementById('status').textContent = status;
    const errorBox = document.getElementById('teencyError');
    if (status !== 'ok') errorBox.classList.remove('d-none');
    else errorBox.classList.add('d-none');
  } catch (e) {
    document.getElementById('status').textContent = 'error';
    document.getElementById('teencyError').classList.remove('d-none');
  }
}

fetchTeency();
startTimer();
