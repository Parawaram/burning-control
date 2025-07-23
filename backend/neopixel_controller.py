import board
import neopixel
import time
import logging
from threading import Lock, Thread, current_thread

log = logging.getLogger(__name__)

LED_COUNT = 7
LED_PIN = board.D18
BRIGHTNESS = 0.3

def _init_pixels():
    global _pixels
    try:
        _pixels = neopixel.NeoPixel(
            LED_PIN,
            LED_COUNT,
            brightness=BRIGHTNESS,
            auto_write=False,
        )
        log.info("LEDs initialized")
    except Exception as e:  # pragma: no cover - hardware error
        log.warning("LED init failed: %s", e)
        _pixels = None

def _ensure_pixels():
    if _pixels is None:
        _init_pixels()

_pixels = None
_init_pixels()
_lock = Lock()
_current_thread = None


def fill(color):
    """Fill the strip with a color, handling write errors."""
    _ensure_pixels()
    with _lock:
        try:
            _pixels.fill(color)
            _pixels.show()
        except Exception as e:  # pragma: no cover - hardware error
            log.warning("LED update failed: %s", e)

def off():
    fill((0, 0, 0))

def set_brightness(value):
    global _pixels
    _ensure_pixels()
    with _lock:
        _pixels.brightness = max(0.0, min(0.5, value))  # Clamp to 0.5
        try:
            _pixels.show()
        except Exception as e:  # pragma: no cover - hardware error
            log.warning("LED brightness update failed: %s", e)

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
            _ensure_pixels()
            for j in range(256):
                with _lock:
                    for i in range(LED_COUNT):
                        pixel_index = (i * 256 // LED_COUNT) + j
                        _pixels[i] = wheel(pixel_index & 255)
                    try:
                        _pixels.show()
                    except Exception as e:  # pragma: no cover - hardware error
                        log.warning("LED update failed: %s", e)
                        return
                time.sleep(0.02)

    def pulse():
        t = current_thread()
        while getattr(t, "do_run", True):
            _ensure_pixels()
            for b in range(0, 256, 5):
                fill((b, 0, 0))
                time.sleep(0.02)
            for b in range(255, -1, -5):
                fill((b, 0, 0))
                time.sleep(0.02)

    def chase():
        t = current_thread()
        while getattr(t, "do_run", True):
            _ensure_pixels()
            for i in range(LED_COUNT):
                fill((0, 0, 0))
                with _lock:
                    _pixels[i] = (0, 255, 0)
                    try:
                        _pixels.show()
                    except Exception as e:  # pragma: no cover - hardware error
                        log.warning("LED update failed: %s", e)
                        return
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
