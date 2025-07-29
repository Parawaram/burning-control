"""DHT11 temperature and humidity sensor helper."""

import logging

try:  # pragma: no cover - hardware optional
    import board
    import adafruit_dht
except Exception as e:  # pragma: no cover - no hardware in tests
    board = adafruit_dht = None
    logging.error("DHT11 libs not available: %s", e)

log = logging.getLogger(__name__)


class DHT11Sensor:
    """Wrapper for a single DHT11 sensor."""

    def __init__(self, pin=board.D4):
        self.pin = pin
        self._sensor = None

    def _init_sensor(self):
        if board is None or adafruit_dht is None:
            return
        try:
            self._sensor = adafruit_dht.DHT11(self.pin)
            log.info("DHT11 on %s initialized", self.pin)
        except Exception as e:  # pragma: no cover - hardware error
            log.info("DHT11 init failed: %s", e)
            self._sensor = None

    def read(self):
        if self._sensor is None:
            self._init_sensor()
        if self._sensor is None:
            return None
        try:
            temp = self._sensor.temperature
            hum = self._sensor.humidity
            if temp is None or hum is None:
                raise RuntimeError("invalid reading")
            return {
                "temperature": round(float(temp), 1),
                "humidity": round(float(hum), 1),
            }
        except Exception as e:  # pragma: no cover - hardware error
            log.info("DHT11 read failed: %s", e)
            self._sensor = None
            return None


_sensor = DHT11Sensor()


def read_data():
    """Return readings for the DHT11 sensor or ``None``."""
    return _sensor.read()
