import time, logging, queue, threading

try:
    import board, busio
    from PIL import Image, ImageDraw, ImageFont
    import adafruit_ssd1306          # type: ignore
except Exception as e:               # аппаратные либы могут отсутствовать
    board = busio = None
    Image = ImageDraw = ImageFont = adafruit_ssd1306 = None
    logging.error("HW libs not available: %s", e)

# ----------------------------------------------------------------------
#  Глобальный кеш последней телеметрии из Teensy -----------------------
_teency_data: dict = {}              # обновляется listener'ом

# ----------------------------------------------------------------------
#  Вспомогательные функции ---------------------------------------------
try:
    import requests                  # для «резервного» запроса во Flask
except Exception:
    requests = None

def fetch_teency() -> dict:
    """Возвращает кеш из _teency_data, а если он пуст — пытается /api/teency."""
    if _teency_data:
        return _teency_data
    if requests is None:
        return {}
    try:
        r = requests.get("http://localhost:8000/api/teency", timeout=0.5)
        if r.ok:
            return r.json()
    except Exception:
        pass
    return {}

# ----------------------------------------------------------------------
log = logging.getLogger(__name__)

class Page:
    def __init__(self, name, renderer):
        self.name = name
        self.render = renderer

class OLEDApp:
    WIDTH  = 64
    HEIGHT = 48

    # ----- инициализация экрана ---------------------------------------
    def __init__(self, addr=0x3C):
        self.addr = addr
        self._setup_display()
        self.pages, self.page_index, self.last_update = [], 0, 0

    def _setup_display(self):
        if board is None:            # тест/CI без железа
            self.display = None
            return
        try:
            i2c = busio.I2C(board.SCL, board.SDA)
            self.display = adafruit_ssd1306.SSD1306_I2C(
                self.WIDTH, self.HEIGHT, i2c, addr=self.addr
            )
            self.image = Image.new("1", (self.display.width, self.display.height))
            self.draw  = ImageDraw.Draw(self.image)
            self.font  = ImageFont.load_default()
            log.info("OLED OK at 0x%X", self.addr)
        except Exception as e:
            log.warning("OLED init failed: %s", e)
            self.display = None

    # ----- утилиты рисования -----------------------------------------
    def _clear(self):
        if self.display:
            self.draw.rectangle((0, 0, self.WIDTH, self.HEIGHT), fill=0)

    def _update(self):
        if not self.display:
            return
        try:
            self.display.image(self.image);  self.display.show()
        except OSError as e:
            log.warning("OLED I/O error: %s", e);  self.display = None

    # ----- страницы ---------------------------------------------------
    def add_page(self, pg: Page):  self.pages.append(pg)
    def next_page(self):           self.page_index = (self.page_index+1) % len(self.pages)
    def prev_page(self):           self.page_index = (self.page_index-1) % len(self.pages)

    # -- пример отрисовки одной страницы ------------------------------
    def render_home(self):
        teency = fetch_teency()
        v5  = teency.get("voltageSensorV5PiBrain", {})
        v3  = teency.get("voltageSensorV3",       {})
        cpu = teency.get("cpu", 0)               # пример

        self._clear()
        self.draw.text((0,  0), f"CPU:{cpu:>3}%", font=self.font, fill=255)
        self.draw.text((0, 10), f"5V :{v5.get('voltage',0):4.1f}", font=self.font, fill=255)
        self.draw.text((0, 20), f"3V :{v3.get('voltage',0):4.1f}", font=self.font, fill=255)
        self._update()

    # ----- основной цикл экрана --------------------------------------
    def run(self):
        if not self.pages:
            self.add_page(Page("home", self.render_home))
        try:
            while True:
                now = time.time()
                if now - self.last_update >= 0.5:
                    self.pages[self.page_index].render()
                    self.last_update = now
                time.sleep(0.05)
        except KeyboardInterrupt:
            pass

# ----------------------------------------------------------------------
#  Entry-points --------------------------------------------------------
def main():                          # standalone тест
    logging.basicConfig(level=logging.INFO)
    OLEDApp().run()

def run(q):
    """Ворк-функция, вызываемая из main.py."""
    logging.basicConfig(level=logging.INFO)
    # поток-слушатель очереди
    def listener():
        global _teency_data
        while True:
            try:
                pkt = q.get(timeout=1)
                if pkt.get("type") == "telemetry":
                    _teency_data = pkt          # кешируем последнюю
            except queue.Empty:
                continue

    threading.Thread(target=listener, daemon=True).start()
    OLEDApp().run()                 # блокирующий цикл отрисовки

# ----------------------------------------------------------------------
if __name__ == "__main__":
    main()
