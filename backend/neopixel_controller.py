import board
import neopixel
import time
from threading import Lock, Thread, current_thread

LED_COUNT = 12
LED_PIN = board.D18
BRIGHTNESS = 0.3

_pixels = neopixel.NeoPixel(
    LED_PIN,
    LED_COUNT,
    brightness=BRIGHTNESS,
    auto_write=False
)
_lock = Lock()
_current_thread = None


def fill(color):
    with _lock:
        _pixels.fill(color)
        _pixels.show()

def off():
    fill((0, 0, 0))

def set_brightness(value):
    global _pixels
    with _lock:
        _pixels.brightness = max(0.0, min(0.5, value))  # Clamp to 0.5
        _pixels.show()

def run_animation(name):
    global _current_thread

    def stop_previous():
        if _current_thread and _current_thread.is_alive():
            _current_thread.do_run = False
            _current_thread.join()

    def animation_runner(target):
        t = Thread(target=target, daemon=True)
        t.do_run = True
        t.start()
        return t

    def rainbow():
        t = current_thread()
        while getattr(t, "do_run", True):
            for j in range(256):
                for i in range(LED_COUNT):
                    pixel_index = (i * 256 // LED_COUNT) + j
                    _pixels[i] = wheel(pixel_index & 255)
                _pixels.show()
                time.sleep(0.02)

    def pulse():
        t = current_thread()
        while getattr(t, "do_run", True):
            for b in range(0, 256, 5):
                fill((b, 0, 0))
                time.sleep(0.02)
            for b in range(255, -1, -5):
                fill((b, 0, 0))
                time.sleep(0.02)

    def chase():
        t = current_thread()
        while getattr(t, "do_run", True):
            for i in range(LED_COUNT):
                fill((0, 0, 0))
                _pixels[i] = (0, 255, 0)
                _pixels.show()
                time.sleep(0.1)

    def wheel(pos):
        if pos < 85:
            return (pos * 3, 255 - pos * 3, 0)
        elif pos < 170:
            pos -= 85
            return (255 - pos * 3, 0, pos * 3)
        else:
            pos -= 170
            return (0, pos * 3, 255 - pos * 3)

    stop_previous()
    if name == 'rainbow':
        _current_thread = animation_runner(rainbow)
    elif name == 'pulse':
        _current_thread = animation_runner(pulse)
    elif name == 'chase':
        _current_thread = animation_runner(chase)
    else:
        off()
