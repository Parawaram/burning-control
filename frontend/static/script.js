const picker = document.getElementById('picker');
document.getElementById('set').onclick = () => {
  const hex = picker.value;
  const rgb = [
    parseInt(hex.substr(1,2),16),
    parseInt(hex.substr(3,2),16),
    parseInt(hex.substr(5,2),16)
  ];
  fetch('/api/color', {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({r:rgb[0], g:rgb[1], b:rgb[2]})
  });
};
document.getElementById('off').onclick = () => {
  fetch('/api/off',{method:'POST'});
};
