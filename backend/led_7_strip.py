import time
import math
import psutil
from dataclasses import dataclass
from threading import Thread, current_thread

try:
    from rpi_ws281x import PixelStrip, Color, ws
    import RPi.GPIO as GPIO
    import board
    import busio
    from adafruit_ssd1306 import SSD1306_I2C
    from PIL import Image, ImageDraw, ImageFont
except Exception:  # pragma: no cover - hardware optional
    PixelStrip = None
    Color = lambda r, g, b: 0
    GPIO = None
    board = busio = None
    SSD1306_I2C = None
    Image = ImageDraw = ImageFont = None

CONFIG = {
    'LED_COUNT': 60,
    'LED_PIN': 18,
    'I2C_ADDR': 0x3C,
    'BTN_NEXT': 17,
    'BTN_BACK': 27,
    'FPS': 60,
    'SHUTDOWN_HOLD': 2.0,
    'DEBOUNCE_MS': 50,
}

# --- Globals for thread management similar to neopixel_controller ---------
_thread = None
_strip = None
_ui = None
_animators = []
_off = None
_index = 0
_requested = None


def clamp(v, lo=0, hi=255):
    return max(lo, min(hi, int(v)))


class Animator:
    name = "NONE"

    def __init__(self, strip):
        self.strip = strip
        self.count = strip.numPixels() if strip else 0

    def step(self, dt):
        pass

    def _fill(self, color):
        if not self.strip:
            return
        for i in range(self.count):
            self.strip.setPixelColor(i, color)

    def cleanup(self):
        self._fill(Color(0, 0, 0))
        if self.strip:
            self.strip.show()


class SolidCyan(Animator):
    name = "CYAN"

    def step(self, dt):
        self._fill(Color(0, 255, 255))


class BreathCyan(Animator):
    name = "BREATH CYAN"
    PERIOD = 2.0

    def __init__(self, strip):
        super().__init__(strip)
        self.t = 0.0

    def step(self, dt):
        self.t += dt
        phase = (math.sin(2 * math.pi * self.t / self.PERIOD) + 1) / 2
        g = clamp(255 * (1 - phase))
        color = Color(0, g, 255)
        self._fill(color)


class Wave(Animator):
    name = "WAVE"
    WIDTH = 10
    SPEED = 30  # px/s

    def __init__(self, strip):
        super().__init__(strip)
        self.pos = 0.0

    def step(self, dt):
        self.pos = (self.pos + self.SPEED * dt) % (self.count + self.WIDTH)
        for i in range(self.count):
            d = i - int(self.pos)
            if 0 <= d < self.WIDTH:
                frac = d / (self.WIDTH - 1)
                g = clamp(255 * (1 - frac))
                color = Color(0, g, 255)
            else:
                color = Color(0, 0, 0)
            if self.strip:
                self.strip.setPixelColor(i, color)


class PulseBeat(Animator):
    name = "BEAT BLUE"
    PERIOD = 0.8
    FADE = 0.6  # s

    def __init__(self, strip):
        super().__init__(strip)
        self.elapsed = 0.0
        self.level = 0.0

    def step(self, dt):
        self.elapsed += dt
        if self.elapsed >= self.PERIOD:
            self.elapsed -= self.PERIOD
            self.level = 1.0
        self.level = max(0.0, self.level - dt / self.FADE)
        b = clamp(255 * self.level)
        color = Color(0, 0, b)
        self._fill(color)


class Ui:
    def __init__(self, cfg):
        self.cfg = cfg
        self._setup_gpio()
        self._setup_oled()
        self.state = {"next": None, "back": None}

    # --- GPIO -------------------------------------------------------------
    def _setup_gpio(self):
        if GPIO is None:
            self.gpio = False
            return
        GPIO.setmode(GPIO.BCM)
        for pin in (self.cfg['BTN_NEXT'], self.cfg['BTN_BACK']):
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self.gpio = True

    def poll(self):
        if not self.gpio:
            return []
        now = time.time()
        events = []
        for name, pin in (("next", self.cfg['BTN_NEXT']), ("back", self.cfg['BTN_BACK'])):
            pressed = not GPIO.input(pin)
            if pressed:
                if self.state[name] is None:
                    self.state[name] = now
            else:
                if self.state[name] is not None:
                    dur = now - self.state[name]
                    self.state[name] = None
                    if dur >= self.cfg['SHUTDOWN_HOLD']:
                        events.append((name, 'long'))
                    elif dur > self.cfg['DEBOUNCE_MS'] / 1000:
                        events.append((name, 'short'))
        return events

    # --- OLED -------------------------------------------------------------
    def _setup_oled(self):
        if board is None:
            self.display = None
            return
        i2c = busio.I2C(board.SCL, board.SDA)
        self.display = SSD1306_I2C(64, 48, i2c, addr=self.cfg['I2C_ADDR'])
        self.image = Image.new("1", (self.display.width, self.display.height))
        self.draw = ImageDraw.Draw(self.image)
        self.font = ImageFont.load_default()

    def show_mode(self, name):
        if not self.display:
            return
        self.draw.rectangle((0, 0, self.display.width, self.display.height), outline=0, fill=0)
        self.draw.text((0, 0), "Black Playa Mk-I", font=self.font, fill=255)
        self.draw.text((0, 12), name, font=self.font, fill=255)
        try:
            self.display.image(self.image)
            self.display.show()
        except Exception:
            pass

    def cleanup(self):
        if self.display:
            self.draw.rectangle((0, 0, self.display.width, self.display.height), outline=0, fill=0)
            try:
                self.display.image(self.image)
                self.display.show()
            except Exception:
                pass
        if self.gpio:
            GPIO.cleanup()


def build_strip(cfg):
    if PixelStrip is None:
        return None
    strip = PixelStrip(cfg['LED_COUNT'], cfg['LED_PIN'], freq_hz=800000, dma=10, invert=False,
                       brightness=255, channel=0, strip_type=ws.WS2813_STRIP_GRB)
    strip.begin()
    return strip


def init(cfg=CONFIG):
    """Initialize hardware and animations."""
    global _strip, _ui, _animators, _off, _index
    if _strip:
        return
    _strip = build_strip(cfg)
    _ui = Ui(cfg)
    _animators = [
        SolidCyan(_strip),
        BreathCyan(_strip),
        Wave(_strip),
        PulseBeat(_strip),
    ]
    _off = Animator(_strip)
    _index = 0


def _loop(frame):
    global _index, _requested
    current = _animators[_index]
    _ui.show_mode(current.name)
    last = time.time()
    while getattr(current_thread(), "running", True):
        now = time.time()
        dt = now - last
        last = now
        for name, kind in _ui.poll():
            if kind == "long":
                current = _off
            elif name == "next":
                _index = (_index + 1) % len(_animators)
                current = _animators[_index]
            elif name == "back":
                _index = (_index - 1) % len(_animators)
                current = _animators[_index]
            _ui.show_mode(current.name if current is not _off else "OFF")
        if _requested is not None:
            for i, a in enumerate(_animators):
                if a.name == _requested:
                    _index = i
                    current = a
                    _ui.show_mode(a.name)
                    break
            _requested = None
        current.step(dt)
        if _strip:
            _strip.show()
        cpu = psutil.cpu_percent(interval=None)
        sleep = frame - (time.time() - now)
        if cpu > 30:
            sleep += 0.02
        if sleep > 0:
            time.sleep(sleep)
    # cleanup
    if _strip:
        for i in range(_strip.numPixels()):
            _strip.setPixelColor(i, Color(0, 0, 0))
        _strip.show()
    _ui.cleanup()


def start():
    """Start background animation loop."""
    global _thread
    if _thread and _thread.is_alive():
        return
    init()
    frame = 1.0 / CONFIG["FPS"]
    t = Thread(target=_loop, args=(frame,), daemon=True)
    t.running = True
    _thread = t
    t.start()


def stop():
    """Stop the animation loop."""
    global _thread
    if not _thread:
        return
    _thread.running = False
    _thread.join()
    _thread = None


def set_animation(name: str):
    """Request a specific animation by name."""
    global _requested
    _requested = name


