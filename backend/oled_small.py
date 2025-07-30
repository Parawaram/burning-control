import time
import random
import logging

try:
    import board
    import busio
    import digitalio
    from PIL import Image, ImageDraw, ImageFont
    import adafruit_ssd1306
except Exception as e:  # pragma: no cover - hardware optional
    board = busio = digitalio = None
    Image = ImageDraw = ImageFont = adafruit_ssd1306 = None
    logging.error("Required hardware libraries not available: %s", e)

from telemetry_service import get_telemetry
from teency_service import get_data as get_teency_data


log = logging.getLogger(__name__)


class Page:
    def __init__(self, name, renderer):
        self.name = name
        self.render = renderer


class OLEDApp:
    WIDTH = 64
    HEIGHT = 48

    def __init__(self, addr=0x3C, left_pin=5, right_pin=6):
        self.addr = addr
        self.left_pin = left_pin
        self.right_pin = right_pin
        self._setup_display()
        self._setup_buttons()
        self.pages = []
        self.page_index = 0
        self.last_update = 0

    def _setup_display(self):
        """Initialize the OLED display if hardware is available."""
        if board is None:
            self.display = None
            return
        try:
            i2c = busio.I2C(board.SCL, board.SDA)
            self.display = adafruit_ssd1306.SSD1306_I2C(
                self.WIDTH, self.HEIGHT, i2c, addr=self.addr
            )
            self.image = Image.new("1", (self.display.width, self.display.height))
            self.draw = ImageDraw.Draw(self.image)
            self.font = ImageFont.load_default()
            log.info("OLED display initialized")
        except Exception as e:  # pragma: no cover - hardware error
            log.warning("OLED init failed: %s", e)
            self.display = None

    def _ensure_display(self):
        """Try to reinitialize the display if it became unavailable."""
        if self.display is None:
            self._setup_display()

    def _setup_buttons(self):
        if digitalio is None:
            self.button_left = None
            self.button_right = None
            return
        self.button_left = digitalio.DigitalInOut(getattr(board, f"D{self.left_pin}"))
        self.button_left.direction = digitalio.Direction.INPUT
        self.button_left.pull = digitalio.Pull.UP
        self.button_right = digitalio.DigitalInOut(getattr(board, f"D{self.right_pin}"))
        self.button_right.direction = digitalio.Direction.INPUT
        self.button_right.pull = digitalio.Pull.UP

    # --- Display helpers -------------------------------------------------
    def _clear(self):
        if not self.display:
            return
        self.draw.rectangle((0, 0, self.WIDTH, self.HEIGHT), outline=0, fill=0)

    def _update(self):
        self._ensure_display()
        if not self.display:
            return
        try:
            self.display.image(self.image)
            self.display.show()
        except OSError as e:  # pragma: no cover - hardware error
            log.warning("OLED update failed: %s", e)
            self.display = None

    # --- Pages -----------------------------------------------------------
    def add_page(self, page: Page):
        self.pages.append(page)

    def next_page(self):
        if self.pages:
            self.page_index = (self.page_index + 1) % len(self.pages)

    def prev_page(self):
        if self.pages:
            self.page_index = (self.page_index - 1) % len(self.pages)

    # --- Rendering -------------------------------------------------------
    def show_logo(self, duration=3.0):
        if not self.display:
            time.sleep(duration)
            return
        steps = 20
        start = time.time()
        for i in range(steps + 1):
            self._clear()
            self.draw.text((5, 5), "BurningMan", font=self.font, fill=255)
            self.draw.text((5, 15), "MK-1", font=self.font, fill=255)
            bar_width = int((self.WIDTH - 10) * i / steps)
            self.draw.rectangle((5, 35, 5 + bar_width, 40), outline=255, fill=255)
            self._update()
            time.sleep(duration / steps)
        # wait remainder if any
        remaining = duration - (time.time() - start)
        if remaining > 0:
            time.sleep(remaining)

    def render_home(self):
        data = get_telemetry()
        cpu = data.get('cpu_usage')
        teency = get_teency_data()
        vs = teency.get('voltageSensorV5PiBrain', {})
        volt = vs.get('voltage', 0.0)
        batt = random.randint(40, 100)
        temp = random.uniform(25.0, 35.0)
        status = "OK"
        if batt < 20:
            status = "!"  # warning
        if cpu and cpu > 90:
            status = "ERR"
        self._clear()
        self.draw.text((0, 0), f"CPU:{cpu or 0:>4}%", font=self.font, fill=255)
        self.draw.text((0, 10), f"V:{volt:4.1f}V", font=self.font, fill=255)
        self.draw.text((0, 20), f"B:{batt:3}%", font=self.font, fill=255)
        self.draw.text((0, 30), f"T:{temp:4.1f}C", font=self.font, fill=255)
        self.draw.text((50, 0), status, font=self.font, fill=255)
        self._update()

    def run(self):
        self.show_logo()
        # default pages
        if not self.pages:
            self.add_page(Page("home", self.render_home))
        try:
            while True:
                now = time.time()
                if self.button_left and not self.button_left.value:
                    self.prev_page()
                if self.button_right and not self.button_right.value:
                    self.next_page()
                if now - self.last_update >= 0.5:
                    current = self.pages[self.page_index]
                    current.render()
                    self.last_update = now
                time.sleep(0.05)
        except KeyboardInterrupt:
            pass
        finally:
            self.shutdown()

    def shutdown(self):
        if not self.display:
            return
        try:
            self.display.fill(0)
            self.display.show()
        except Exception:
            pass


def main():
    logging.basicConfig(level=logging.INFO)
    app = OLEDApp()
    app.run()


if __name__ == "__main__":
    main()
