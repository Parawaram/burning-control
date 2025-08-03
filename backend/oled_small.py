# backend/oled_small.py — минимальный вывод пяти параметров на маленький OLED

import logging
import threading
import time
import queue
import signal

# --- попытка подключить аппаратные библиотеки ---
try:
    import board, busio  # type: ignore
    from PIL import Image, ImageDraw, ImageFont
    import adafruit_ssd1306  # type: ignore
except Exception as e:  # pragma: no cover – запускаем и без железа
    board = busio = None
    Image = ImageDraw = ImageFont = adafruit_ssd1306 = None
    logging.error("OLED libs unavailable: %s", e)

# ---------------------------------------------------------------------------
# Глобальный кеш, обновляемый из очереди
_teency_data: dict = {}

# ---------------------------------------------------------------------------
class _NullDraw:
    """Fallback drawing object used when no OLED is attached."""

    def rectangle(self, *a, **k):
        pass

    def text(self, *a, **k):
        pass


class OLED:
    WIDTH = 64
    HEIGHT = 48

    def __init__(self, addr: int = 0x3C):
        self.addr = addr
        self.display = None
        self.image = None
        self.draw = _NullDraw()
        self.font = None
        self._last_try = 0.0  # last time we attempted to (re)connect
        self._setup()

    def _setup(self):
        if board is None:
            self.draw = _NullDraw()
            self.image = None
            self.font = None
            return
        try:
            i2c = busio.I2C(board.SCL, board.SDA)
            self.display = adafruit_ssd1306.SSD1306_I2C(self.WIDTH, self.HEIGHT, i2c, addr=self.addr)
            self.image   = Image.new("1", (self.WIDTH, self.HEIGHT))
            self.draw    = ImageDraw.Draw(self.image)
            self.font    = ImageFont.load_default()
            logging.info("OLED ready at 0x%X", self.addr)
            self._last_try = time.time()
        except Exception as e:  # pragma: no cover
            logging.warning("OLED init failed: %s", e)
            self.display = None
            self.draw = _NullDraw()
            self.image = None
            self.font = None
            self._last_try = time.time()

    def _update(self):
        if not self.display:
            if time.time() - self._last_try > 5:
                self._last_try = time.time()
                self._setup()
            return
        try:
            self.display.image(self.image)
            self.display.show()
        except OSError as e:  # pragma: no cover
            logging.warning("OLED I/O error: %s", e)
            logging.info("OLED disconnected")
            self.display = None
            self._last_try = 0.0

    def poweroff(self):
        """Clear the screen and try to power down the display."""
        if not self.display:
            return
        try:
            self.display.fill(0)
            self.display.show()
            if hasattr(self.display, "poweroff"):
                self.display.poweroff()
        except Exception as e:  # pragma: no cover
            logging.warning("OLED poweroff failed: %s", e)

    def loop(self):
        last = 0.0
        while True:
            now = time.time()
            if now - last >= 0.5:
                self.render()
                last = now
            time.sleep(0.05)

    def render(self):
        # получаем актуальные данные (или нули)
        d = _teency_data or {}
        cpu   = d.get("cpu_usage", 0)
        v5    = d.get("voltageSensorV5PiBrain", {})
        v3    = d.get("voltageSensorV3",       {})

        self.draw.rectangle((0, 0, self.WIDTH, self.HEIGHT), fill=0)  # clear
        self.draw.text((0,  0), f"CPU:{cpu:>3}%",               font=self.font, fill=255)
        self.draw.text((0, 10), f"V5 :{v5.get('voltage',0):4.2f}V", font=self.font, fill=255)
        self.draw.text((0, 20), f"I5 :{v5.get('current',0):4.2f}A", font=self.font, fill=255)
        self.draw.text((0, 30), f"V3 :{v3.get('voltage',0):4.2f}V", font=self.font, fill=255)
        self.draw.text((0, 40), f"I3 :{v3.get('current',0):4.2f}A", font=self.font, fill=255)
        self._update()

# ---------------------------------------------------------------------------
# Entry‑points

def _listener(q):
    global _teency_data
    while True:
        try:
            pkt = q.get(timeout=1)
            if pkt.get("type") == "telemetry":
                _teency_data = pkt
        except queue.Empty:
            continue


def run(q):
    """Вызывается orchestrator'ом main.py"""
    logging.basicConfig(level=logging.INFO)
    oled = OLED()
    threading.Thread(target=_listener, args=(q,), daemon=True).start()

    def _cleanup(signum, frame):  # pragma: no cover - hardware cleanup
        oled.poweroff()
        raise SystemExit

    signal.signal(signal.SIGTERM, _cleanup)
    signal.signal(signal.SIGINT, _cleanup)

    try:
        oled.loop()
    finally:
        oled.poweroff()


def main():
    """Standalone запуск на ПК/PI без очереди."""
    from multiprocessing import Queue
    run(Queue())


if __name__ == "__main__":
    main()
