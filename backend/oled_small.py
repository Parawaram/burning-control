import time
import logging
import queue

try:
    import board
    import busio
    from PIL import Image, ImageDraw, ImageFont
    import adafruit_ssd1306
except Exception as e:  # pragma: no cover - hardware optional
    board = busio = None
    Image = ImageDraw = ImageFont = adafruit_ssd1306 = None
    logging.error("Required hardware libraries not available: %s", e)

from .telemetry_service import get_telemetry
from .teency_service import (
    DEFAULT_DATA,
    get_data as get_teency_data,
)
try:
    import requests  # type: ignore
except Exception:
    requests = None


def fetch_teency() -> dict:
    """Get telemetry from the Flask API if available."""
    if requests is None:
        return get_teency_data()
    try:
        resp = requests.get("http://localhost:5000/api/teency", timeout=0.5)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return DEFAULT_DATA.copy()

log = logging.getLogger(__name__)


class Page:
    def __init__(self, name, renderer):
        self.name = name
        self.render = renderer


class OLEDApp:
    WIDTH = 64
    HEIGHT = 48

    def __init__(self, addr=0x3C):
        self.addr = addr
        self._setup_display()
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
        teency = fetch_teency()
        vs_pibrain = teency.get('voltageSensorV5PiBrain', {})
        volt_5 = vs_pibrain.get('voltage', 0.0)
        amp_5 = vs_pibrain.get('current', 0.0)
        vs_3 = teency.get('voltageSensorV3', {})
        volt_3 = vs_3.get('voltage', 0.0)

        status = "OK"
        if cpu and cpu > 90:
            status = "ERR"
        self._clear()
        self.draw.text((0, 0), f"CPU:{cpu or 0:>4}%", font=self.font, fill=255)
        self.draw.text((0, 10), f"V:{volt_5:4.1f}V", font=self.font, fill=255)
        self.draw.text((0, 20), f"B:{amp_5:4.1f}A", font=self.font, fill=255)
        self.draw.text((0, 30), f"V3:{volt_3:4.1f}V", font=self.font, fill=255)
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
    # standalone preview mode
    app = OLEDApp()
    app.run()


def run(q):
    """Run OLED display worker using packets from a queue."""
    logging.basicConfig(level=logging.INFO)
    app = OLEDApp()
    last_pkt = {}

    def render_from_pkt():
        data = get_telemetry()
        cpu = data.get('cpu_usage')
        teency = last_pkt or fetch_teency()
        vs_pibrain = teency.get('voltageSensorV5PiBrain', {})
        volt_5 = vs_pibrain.get('voltage', 0.0)
        amp_5 = vs_pibrain.get('current', 0.0)
        vs_3 = teency.get('voltageSensorV3', {})
        volt_3 = vs_3.get('voltage', 0.0)

        status = "OK"
        if cpu and cpu > 90:
            status = "ERR"
        app._clear()
        app.draw.text((0, 0), f"CPU:{cpu or 0:>4}%", font=app.font, fill=255)
        app.draw.text((0, 10), f"V:{volt_5:4.1f}V", font=app.font, fill=255)
        app.draw.text((0, 20), f"B:{amp_5:4.1f}A", font=app.font, fill=255)
        app.draw.text((0, 30), f"V3:{volt_3:4.1f}V", font=app.font, fill=255)
        app.draw.text((50, 0), status, font=app.font, fill=255)
        app._update()

    if not app.pages:
        app.add_page(Page("home", render_from_pkt))
    app.show_logo()
    try:
        while True:
            try:
                pkt = q.get(timeout=0.2)
                if isinstance(pkt, dict):
                    if pkt.get("type") == "telemetry":
                        last_pkt = pkt
                    elif pkt.get("type") == "cmd" and pkt.get("cmd") == "page":
                        idx = pkt.get("idx")
                        if isinstance(idx, int) and app.pages:
                            app.page_index = idx % len(app.pages)
            except queue.Empty:
                pass
            now = time.time()
            if now - app.last_update >= 0.5:
                app.pages[app.page_index].render()
                app.last_update = now
            time.sleep(0.05)
    except KeyboardInterrupt:
        pass
    finally:
        app.shutdown()


if __name__ == "__main__":
    main()
