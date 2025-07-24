async function fetchSensors() {
  const resp = await fetch('/api/sensors');
  const data = await resp.json();
  if (data.temperature !== undefined && data.temperature !== null) {
    document.getElementById('temperature').textContent = data.temperature;
  }
  if (data.ina219) {
    const v = data.ina219;
    if (v.bus_voltage !== undefined)
      document.getElementById('bus_voltage').textContent = v.bus_voltage;
    if (v.shunt_voltage !== undefined)
      document.getElementById('shunt_voltage').textContent = v.shunt_voltage;
    if (v.current !== undefined)
      document.getElementById('current').textContent = v.current;
    if (v.power !== undefined)
      document.getElementById('power').textContent = v.power;
  }
}

fetchSensors();
setInterval(fetchSensors, 250);
