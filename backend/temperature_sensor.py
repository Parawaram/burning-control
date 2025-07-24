import os
import logging

log = logging.getLogger(__name__)

BASE_DIR = '/sys/bus/w1/devices'


def _detect_device():
    try:
        for name in os.listdir(BASE_DIR):
            if name.startswith('28-'):
                return name
    except Exception as e:  # pragma: no cover - hardware optional
        log.warning("Temperature sensor detection failed: %s", e)
    return None


def read_temperature(device_id=None):
    """Return temperature in Celsius from DS18B20 sensor if available."""
    if not os.path.exists(BASE_DIR):
        return None
    dev = device_id or _detect_device()
    if not dev:
        return None
    path = os.path.join(BASE_DIR, dev, 'w1_slave')
    try:
        with open(path) as f:
            data = f.read()
        if 't=' in data:
            temp_str = data.split('t=')[-1].strip()
            return round(int(temp_str) / 1000, 1)
    except Exception as e:  # pragma: no cover - hardware optional
        log.warning("Temperature read failed: %s", e)
    return None
