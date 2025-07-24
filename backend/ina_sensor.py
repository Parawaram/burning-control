"""INA219 sensor helpers supporting multiple addresses."""

import logging

try:  # pragma: no cover - hardware optional
    import board
    import busio
    from adafruit_ina219 import INA219
except Exception as e:  # pragma: no cover - no hardware in tests
    board = busio = INA219 = None
    logging.error("INA219 libs not available: %s", e)


log = logging.getLogger(__name__)


class INASensor:
    """Wrapper for a single INA219 sensor."""

    def __init__(self, addr: int):
        self.addr = addr
        self._sensor = None

    def _init_sensor(self):
        if board is None or busio is None or INA219 is None:
            return
        try:
            i2c = busio.I2C(board.SCL, board.SDA)
            self._sensor = INA219(i2c, addr=self.addr)
            log.info("INA219 0x%02X initialized", self.addr)
        except Exception as e:  # pragma: no cover - hardware error
            log.warning("INA219 0x%02X init failed: %s", self.addr, e)
            self._sensor = None

    def read(self):
        if self._sensor is None:
            self._init_sensor()
        if self._sensor is None:
            return None
        try:
            return {
                "bus_voltage": round(self._sensor.bus_voltage, 3),
                "shunt_voltage": round(self._sensor.shunt_voltage / 1000, 3),
                "current": round(self._sensor.current, 1),
                "power": round(self._sensor.power, 1),
            }
        except Exception as e:  # pragma: no cover - hardware error
            log.warning("INA219 0x%02X read failed: %s", self.addr, e)
            self._sensor = None
            return None


_sensors = {}
DEFAULT_ADDRESSES = [0x40, 0x41, 0x42, 0x43, 0x44, 0x45]


def _get_sensor(addr: int) -> INASensor:
    if addr not in _sensors:
        _sensors[addr] = INASensor(addr)
    return _sensors[addr]


def read_data(addr: int = 0x40):
    """Return readings for sensor at given address or ``None``."""
    return _get_sensor(addr).read()


def read_all(addrs=None):
    """Return readings for a list of sensors with status flags."""
    if addrs is None:
        addrs = DEFAULT_ADDRESSES
    result = {}
    for addr in addrs:
        data = read_data(addr)
        key = f"0x{addr:02X}"
        if data is None:
            result[key] = {"status": "off"}
        else:
            result[key] = {"status": "on", **data}
    return result
