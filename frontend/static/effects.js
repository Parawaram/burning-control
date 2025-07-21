const brightnessSlider = document.getElementById('brightness');
brightnessSlider.addEventListener('input', () => {
  const val = parseFloat(brightnessSlider.value);
  fetch('/api/brightness', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ value: val })
  });
});

function sendAnimation(name) {
  fetch('/api/animation', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ name })
  });
}

function turnOff() {
  fetch('/api/off', { method: 'POST' });
}
