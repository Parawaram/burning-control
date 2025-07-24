import logging

try:
    import board
    import busio
    from adafruit_ina219 import INA219
except Exception as e:  # pragma: no cover - hardware optional
    board = busio = INA219 = None
    logging.error("INA219 libs not available: %s", e)


log = logging.getLogger(__name__)
_sensor = None

def _init_sensor():
    global _sensor
    if board is None or busio is None or INA219 is None:
        return
    try:
        i2c = busio.I2C(board.D17, board.D27)
        _sensor = INA219(i2c)
        log.info("INA219 initialized")
    except Exception as e:  # pragma: no cover - hardware error
        log.warning("INA219 init failed: %s", e)
        _sensor = None


def read_data():
    """Return INA219 sensor readings if available."""
    global _sensor
    if _sensor is None:
        _init_sensor()
    if _sensor is None:
        return None
    try:
        return {
            "bus_voltage": round(_sensor.bus_voltage, 3),
            "shunt_voltage": round(_sensor.shunt_voltage / 1000, 3),
            "current": round(_sensor.current, 1),
            "power": round(_sensor.power, 1),
        }
    except Exception as e:  # pragma: no cover - hardware error
        log.warning("INA219 read failed: %s", e)
        _sensor = None
        return None
