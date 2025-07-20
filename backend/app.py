# backend/app.py
from flask import Flask, render_template, request, jsonify
from neopixel_controller import fill, off

app = Flask(__name__, template_folder='../frontend/templates',
                      static_folder='../frontend/static')

@app.route('/')
def index():
    return render_template('index.html')

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

if __name__ == '__main__':
    # host='0.0.0.0' — доступ извне; port = 5000 по умолчанию
    app.run(host='0.0.0.0', port=5000, debug=False)
