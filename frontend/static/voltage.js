async function fetchIna() {
  const resp = await fetch('/api/ina219');
  const data = await resp.json();
  const val = data.bus_voltage !== undefined ? data.bus_voltage : '--';
  document.getElementById('inaV5Value').textContent = val;
}

fetchIna();
setInterval(fetchIna, 250);
