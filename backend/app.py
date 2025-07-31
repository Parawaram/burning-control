from flask import Flask, render_template, request, jsonify, redirect, url_for
from neopixel_controller import fill, off, set_brightness, run_animation
from telemetry_service import get_telemetry
from temperature_sensor import read_temperature
from aht_sensor import read_data as read_aht, read_all as read_all_aht
from dht_sensor import read_data as read_dht
from teency_service import start as start_teency, get_data as get_teency_data
import random
import time
import json
import logging
import queue
try:
    import serial  # type: ignore
except Exception as e:  # pragma: no cover - optional
    serial = None
    logging.error("pyserial not available: %s", e)

app = Flask(
    __name__,
    template_folder='../frontend/templates',
    static_folder='../frontend/static'
)

# start background reader for Teency telemetry
start_teency()

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


@app.get('/api/aht20')
def api_aht20():
    index_param = request.args.get('idx')
    if request.args.get('all') is not None:
        return jsonify(read_all_aht())
    if index_param is not None:
        try:
            idx = int(index_param)
        except ValueError:
            return jsonify({})
        data = read_aht(idx)
    else:
        data = read_aht()
    if data is None:
        return jsonify({'status': 'off'})
    return jsonify({'status': 'on', **data})


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
        'aht20': read_all_aht(),
        'dht11': {'status': 'on', **dht} if dht else {'status': 'off'},
    })

def run(q):
    """Read JSON telemetry from serial and put packets onto the queue."""
    logging.basicConfig(level=logging.INFO)
    log = logging.getLogger(__name__)
    if serial is None:
        log.error("Serial library unavailable")
        return
    try:
        ser = serial.Serial('/dev/ttyACM0', 115200, timeout=0.1)
    except Exception as e:  # pragma: no cover - hardware optional
        log.error("Serial open failed: %s", e)
        return
    while True:
        try:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if not line:
                continue
            try:
                pkt = {"type": "telemetry", **json.loads(line)}
            except Exception as e:
                log.warning("Bad packet: %s", e)
                continue
            try:
                q.put_nowait(pkt)
            except queue.Full:
                log.warning("queue full, dropping packet")
        except KeyboardInterrupt:
            break
        except Exception as e:  # pragma: no cover - hardware optional
            log.warning("serial read failed: %s", e)


if __name__ == '__main__':
    from multiprocessing import Queue
    run(Queue())
