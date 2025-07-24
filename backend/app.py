from flask import Flask, render_template, request, jsonify, redirect, url_for
from neopixel_controller import fill, off, set_brightness, run_animation
from telemetry_service import get_telemetry
from ina_sensor import read_data as read_ina, read_all as read_all_ina
from temperature_sensor import read_temperature
from aht_sensor import read_data as read_aht, read_all as read_all_aht
import random
import time

app = Flask(
    __name__,
    template_folder='../frontend/templates',
    static_folder='../frontend/static'
)

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


@app.get('/api/ina219')
def api_ina219():
    addr_param = request.args.get('addr')
    if request.args.get('all') is not None:
        return jsonify(read_all_ina())
    if addr_param is not None:
        try:
            addr = int(addr_param, 0)
        except ValueError:
            return jsonify({})
        data = read_ina(addr)
    else:
        data = read_ina()
    if data is None:
        return jsonify({"status": "off"})
    return jsonify({"status": "on", **data})


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


@app.get('/api/sensors')
def api_sensors():
    return jsonify({
        'ina219': read_ina() or {},
        'temperature': read_temperature(),
        'aht20': read_all_aht(),
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
