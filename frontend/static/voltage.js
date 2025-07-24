const addresses = [0x40, 0x41, 0x42, 0x43, 0x44, 0x45];

async function fetchIna() {
  const resp = await fetch('/api/ina219?all=1');
  const all = await resp.json();

  for (const addr of addresses) {
    const hex = '0x' + addr.toString(16).toUpperCase();
    const data = all[hex] || { status: 'off' };
    const prefix = 'ina_' + hex.slice(2) + '_';

    document.getElementById(prefix + 'bus').textContent =
      data.bus_voltage !== undefined ? data.bus_voltage : '--';
    document.getElementById(prefix + 'shunt').textContent =
      data.shunt_voltage !== undefined ? data.shunt_voltage : '--';
    document.getElementById(prefix + 'current').textContent =
      data.current !== undefined ? data.current : '--';
    document.getElementById(prefix + 'power').textContent =
      data.power !== undefined ? data.power : '--';
    document.getElementById(prefix + 'status').textContent = data.status || 'off';
  }
}

fetchIna();
setInterval(fetchIna, 250);
