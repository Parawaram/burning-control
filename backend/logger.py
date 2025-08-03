import json, logging, queue
from logging.handlers import RotatingFileHandler

def run(q):
    log = logging.getLogger("logger")
    fh  = RotatingFileHandler("telemetry.log", maxBytes=1_000_000, backupCount=5)
    fh.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
    log.addHandler(fh); log.setLevel(logging.INFO)
    while True:
        try:
            pkt = q.get(timeout=1)
            if pkt.get("type") == "telemetry":
                log.info(json.dumps(pkt))
        except queue.Empty:
            continue

