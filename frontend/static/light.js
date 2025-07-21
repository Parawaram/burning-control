const picker = document.getElementById('picker');
const brightnessSlider = document.getElementById('brightness');

function setColor() {
  const hex = picker.value;
  const rgb = [
    parseInt(hex.substr(1,2),16),
    parseInt(hex.substr(3,2),16),
    parseInt(hex.substr(5,2),16)
  ];
  fetch('/api/color', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({r: rgb[0], g: rgb[1], b: rgb[2]})
  });
}

function turnOff() {
  fetch('/api/off', {method:'POST'});
}

document.getElementById('set')?.addEventListener('click', setColor);
document.getElementById('off')?.addEventListener('click', turnOff);

brightnessSlider?.addEventListener('input', () => {
  const val = parseFloat(brightnessSlider.value);
  fetch('/api/brightness', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({value: val})
  });
});

function sendAnimation(name) {
  fetch('/api/animation', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({name})
  });
}
