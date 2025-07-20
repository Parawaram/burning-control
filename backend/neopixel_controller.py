# backend/neopixel_controller.py
import board
import neopixel
from threading import Lock

LED_COUNT = 12
LED_PIN = board.D18
BRIGHTNESS = 0.3          # глобальная яркость (0…1)

_pixels = neopixel.NeoPixel(
    LED_PIN,
    LED_COUNT,
    brightness=BRIGHTNESS,
    auto_write=False
)
_lock = Lock()

def fill(color):
    """Залить кольцо заданным цветом (tuple R,G,B)."""
    with _lock:
        _pixels.fill(color)
        _pixels.show()

def off():
    """Выключить все пиксели."""
    fill((0, 0, 0))
