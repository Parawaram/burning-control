from flask import Flask, render_template, request, jsonify, redirect, url_for
from neopixel_controller import fill, off, set_brightness, run_animation

app = Flask(
    __name__,
    template_folder='../frontend/templates',
    static_folder='../frontend/static'
)


def get_fake_status():
    return {
        'temperature': 36.6,
        'suit_temperature': 31.4,
        'voltage': 12.3,
        'cooling_status': 'OFF',
        'fans': 'IDLE',
    }

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

@app.route('/monitor')
def monitor():
    return render_template('v2/monitor.html')

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
