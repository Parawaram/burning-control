import json
import logging
import threading
import time
from typing import Any, Dict

try:
    import serial  # type: ignore
except Exception as e:  # pragma: no cover - optional in tests
    serial = None
    logging.error("pyserial not available: %s", e)

log = logging.getLogger(__name__)

# Default data used when the Teensy board is not available or fails to
# provide telemetry. All sensors are marked as unavailable and values are
# reset to ``0`` and ``status`` set to ``error`` so that the UI can show
# an "off" state.
DEFAULT_VOLTAGE = {"current": 0.0, "voltage": 0.0, "power": 0.0, "isAvailable": False}
DEFAULT_TEMP = {"temperature": 0.0, "humidity": 0.0, "isAvailable": False}
DEFAULT_DATA: Dict[str, Any] = {
    "ts": 0,
    "voltageSensorV3": DEFAULT_VOLTAGE.copy(),
    "voltageSensorV5": DEFAULT_VOLTAGE.copy(),
    "voltageSensorV5PiBrain": DEFAULT_VOLTAGE.copy(),
    "voltageSensorV24": DEFAULT_VOLTAGE.copy(),
    "temperatureSensor1": DEFAULT_TEMP.copy(),
    "temperatureSensor2": DEFAULT_TEMP.copy(),
    "relay1": False,
    "relay2": False,
    "button": False,
    "status": "error",
}

_data: Dict[str, Any] = DEFAULT_DATA.copy()
_serial = None
_thread_started = False

PORT_CANDIDATES = ["/dev/ttyACM0", "/dev/ttyUSB0"]
BAUDRATE = 115200


def _open_serial():
    global _serial
    for port in PORT_CANDIDATES:
        try:
            _serial = serial.Serial(port, BAUDRATE, timeout=1)  # type: ignore
            log.info("Teency connected on %s", port)
            return
        except Exception as e:  # pragma: no cover - hardware optional
            log.info("Teency open %s failed: %s", port, e)
    _serial = None


def _reader():  # pragma: no cover - hardware optional
    global _data, _serial
    while True:
        if serial is None:
            _data = DEFAULT_DATA.copy()
            time.sleep(1)
            continue
        if _serial is None:
            _open_serial()
            _data = DEFAULT_DATA.copy()
            time.sleep(1)
            continue
        try:
            line = _serial.readline().decode("utf-8", errors="ignore").strip()
            if not line:
                continue

            _data = json.loads(line)
            _data.setdefault("status", "ok")
        except Exception as e:
            log.warning("Teency read failed: %s", e)
            _data = DEFAULT_DATA.copy()
            try:
                _serial.close()
            except Exception:
                pass
            _serial = None
            time.sleep(1)


def start():
    global _thread_started
    if _thread_started:
        return
    _thread_started = True
    t = threading.Thread(target=_reader, daemon=True)
    t.start()


def get_data() -> Dict[str, Any]:
    return _data or DEFAULT_DATA.copy()

