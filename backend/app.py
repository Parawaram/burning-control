from flask import Flask, render_template, request, jsonify, redirect, url_for
from .neopixel_controller import fill, off, set_brightness, run_animation
from .telemetry_service import get_telemetry
from .temperature_sensor import read_temperature
from .dht_sensor import read_data as read_dht
import random
import time
import json
import logging
import queue
import threading

_teency = {}

def _listener(q):
    global _teency
    while True:
        try:
            pkt = q.get(timeout=1)
            if pkt.get("type")=="telemetry":
                _teency = pkt
        except queue.Empty:
            continue

def get_teency_data():        # used by /api/teency etc.
    if _teency:
        return {**_teency, "status": _teency.get("status", "ok")}
    return {"status": "wait"}

app = Flask(
    __name__,
    template_folder='../frontend/templates',
    static_folder='../frontend/static'
)

# start background reader for Teency telemetry

# Track last generated status to update once per second
_last_status = {
    'temperature': 36.6,
    'suit_temperature': 31.4,
    'voltage': 12.3,
    'cooling_status': 'OFF',
    'fans': 'IDLE',
}
_last_update = 0.0


def get_fake_status():
    """Return fake status values with slight random variation.

    The values are regenerated at most once per second to simulate
    periodic sensor updates.
    """
    global _last_status, _last_update
    now = time.time()
    if now - _last_update >= 1:
        _last_status = {
            'temperature': round(36.6 + random.uniform(-0.5, 0.5), 1),
            'suit_temperature': round(31.4 + random.uniform(-0.5, 0.5), 1),
            'voltage': round(12.3 + random.uniform(-0.2, 0.2), 2),
            'cooling_status': random.choice(['OFF', 'ON']),
            'fans': random.choice(['IDLE', 'ACTIVE']),
        }
        _last_update = now
    return _last_status




@app.route('/')
def home():
    return render_template('v2/home.html')

@app.route('/light')
def light():
    return render_template('v2/light.html')

@app.route('/effects')
def effects():
    return redirect(url_for('light'))

@app.route('/cooling')
def cooling():
    return render_template('v2/cooling.html')

@app.route('/ventilation')
def ventilation():
    return render_template('v2/ventilation.html')

@app.route('/sensors')
def sensors():
    return render_template('v2/sensors.html')


@app.route('/teency')
def teency_page():
    """Display telemetry from the Teency controller."""
    return render_template('v2/teency.html')


@app.route('/pi-telemetry')
def pi_telemetry():
    return render_template('v2/pi-telemetry.html')

@app.route('/voltage')
def voltage_control_page():
    return render_template('v2/voltage.html')

@app.post('/api/color')
def api_color():
    data = request.get_json()
    r, g, b = data.get('r',0), data.get('g',0), data.get('b',0)
    fill((r, g, b))
    return jsonify(status='ok', color=[r, g, b])

@app.post('/api/off')
def api_off():
    off()
    return jsonify(status='off')

@app.post('/api/brightness')
def api_brightness():
    data = request.get_json()
    value = data.get('value', 0.3)
    set_brightness(value)
    return jsonify(status='ok', brightness=value)

@app.post('/api/animation')
def api_animation():
    data = request.get_json()
    name = data.get('name')
    run_animation(name)
    return jsonify(status='ok', animation=name)


@app.get('/api/status')
def api_status():
    return jsonify(get_fake_status())


@app.get('/api/telemetry')
def api_telemetry():
    return jsonify(get_telemetry())


@app.get('/api/temperature')
def api_temperature():
    temp = read_temperature()
    return jsonify({'temperature': temp} if temp is not None else {})


def _teency_aht(idx: int):
    data = get_teency_data()
    key = f"temperatureSensor{idx}"
    val = data.get(key)
    if not isinstance(val, dict) or not val.get("isAvailable"):
        return {'status': 'off'}
    return {
        'status': 'on',
        'temperature': val.get('temperature'),
        'humidity': val.get('humidity'),
    }


@app.get('/api/aht20')
def api_aht20():
    index_param = request.args.get('idx')
    if request.args.get('all') is not None:
        return jsonify({"1": _teency_aht(1)})
    if index_param is not None:
        try:
            idx = int(index_param)
        except ValueError:
            return jsonify({})
    else:
        idx = 1
    return jsonify(_teency_aht(idx))


@app.get('/api/dht11')
def api_dht11():
    """Return readings from the DHT11 sensor."""
    data = read_dht()
    if data is None:
        return jsonify({'status': 'off'})
    return jsonify({'status': 'on', **data})


@app.get('/api/teency')
def api_teency():
    """Return latest telemetry from the Teency board."""
    return jsonify(get_teency_data())


@app.get('/api/sensors')
def api_sensors():
    dht = read_dht()
    return jsonify({
        'teency': get_teency_data(),
        'temperature': read_temperature(),
        'aht20': {'1': _teency_aht(1)},
        'dht11': {'status': 'on', **dht} if dht else {'status': 'off'},
    })

def run(q):
    threading.Thread(target=_listener, args=(q,), daemon=True).start()
    app.run(host="0.0.0.0", port=8000, debug=False)


if __name__ == '__main__':
    from multiprocessing import Queue
    run(Queue())
