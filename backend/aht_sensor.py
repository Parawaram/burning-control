"""Simple helpers for AHT20 temperature/humidity sensors."""

import logging

try:  # pragma: no cover - hardware optional
    import board
    import busio
    import adafruit_ahtx0
except Exception as e:  # pragma: no cover - no hardware in tests
    board = busio = adafruit_ahtx0 = None
    logging.error("AHT20 libs not available: %s", e)


log = logging.getLogger(__name__)


class AHTSensor:
    """Wrapper for a single AHT20 sensor."""

    def __init__(self, address: int = 0x38):
        self.address = address
        self._sensor = None

    def _init_sensor(self):
        if board is None or busio is None or adafruit_ahtx0 is None:
            return
        try:
            i2c = busio.I2C(board.SCL, board.SDA)
            self._sensor = adafruit_ahtx0.AHTx0(i2c, address=self.address)
            log.info("AHT20 0x%02X initialized", self.address)
        except Exception as e:  # pragma: no cover - hardware error
            log.info("AHT20 0x%02X init failed: %s", self.address, e)
            self._sensor = None

    def read(self):
        if self._sensor is None:
            self._init_sensor()
        if self._sensor is None:
            return None
        try:
            return {
                "temperature": round(self._sensor.temperature, 1),
                "humidity": round(self._sensor.relative_humidity, 1),
            }
        except Exception as e:  # pragma: no cover - hardware error
            log.info("AHT20 0x%02X read failed: %s", self.address, e)
            self._sensor = None
            return None


_sensors = {}
# Only one AHT20 sensor is used by default and it is fixed at address 0x38.
# A second sensor on 0x39 was previously supported but caused issues when only
# a single device is present and its address cannot be changed.
DEFAULT_ADDRESSES = {1: 0x38}


def _get_sensor(index: int) -> AHTSensor:
    addr = DEFAULT_ADDRESSES.get(index, 0x38)
    if index not in _sensors:
        _sensors[index] = AHTSensor(addr)
    return _sensors[index]


def read_data(index: int = 1):
    """Return readings for sensor with given index or ``None``."""
    return _get_sensor(index).read()


def read_all(indices=None):
    """Return readings for a list of sensors with status flags."""
    if indices is None:
        indices = sorted(DEFAULT_ADDRESSES)
    result = {}
    for idx in indices:
        data = read_data(idx)
        key = str(idx)
        if data is None:
            result[key] = {"status": "off"}
        else:
            result[key] = {"status": "on", **data}
    return result

