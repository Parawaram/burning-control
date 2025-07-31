import json, logging, time, queue
try:
    import serial
except ImportError:
    serial = None

PORTS   = ["/dev/ttyACM0", "/dev/ttyUSB0"]
BAUD    = 115200
LOG     = logging.getLogger("reader")

def _open():
    for p in PORTS:
        try: return serial.Serial(p, BAUD, timeout=1)
        except Exception: LOG.info("no %s", p)
    return None

def run(q):
    ser = None
    while True:
        if serial is None: time.sleep(1); continue
        if ser is None: ser = _open(); time.sleep(1); continue

        try:
            line = ser.readline().decode("utf-8","ignore").strip()
            if not line: continue
            pkt  = {"type":"telemetry", **json.loads(line)}
            try: q.put_nowait(pkt)
            except queue.Full: LOG.warning("drop pkt")
        except Exception as e:
            LOG.warning("reset serial %s", e)
            try: ser.close()
            except Exception: pass
            ser = None

