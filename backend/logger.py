import json
import logging
import queue
from logging.handlers import RotatingFileHandler


def run(q):
    """Log telemetry packets from the central queue."""
    logging.basicConfig(level=logging.INFO)
    log = logging.getLogger(__name__)
    handler = RotatingFileHandler("telemetry.log", maxBytes=1_000_000, backupCount=5)
    log.addHandler(handler)
    log.setLevel(logging.INFO)
    while True:
        try:
            pkt = q.get(timeout=0.2)
            if isinstance(pkt, dict) and pkt.get("type") == "telemetry":
                log.info(json.dumps(pkt))
        except queue.Empty:
            continue
        except KeyboardInterrupt:
            break
