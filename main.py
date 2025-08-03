import importlib, logging, time
from multiprocessing import Process, Queue
from logging.handlers import RotatingFileHandler

workers = {
    # single UART reader
    "reader":      "backend.teensy_reader",
    # existing consumers
    "oled_small":  "backend.oled_small",
    "logger":      "backend.logger",
    # flask web api
    "flask":       "backend.app",
}

def main():
    handler = RotatingFileHandler("system.log", maxBytes=1_000_000, backupCount=5)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s: %(message)s",
        handlers=[handler],
    )
    q = Queue(maxsize=200)
    procs = []
    for name, mp in workers.items():
        mod = importlib.import_module(mp)
        p   = Process(target=mod.run, args=(q,), name=name, daemon=True)
        p.start();  procs.append(p)

    try:                       # supervisor loop
        while True:
            time.sleep(0.3)
            for p in procs[:]:
                if not p.is_alive():
                    logging.error("%s died (%s)", p.name, p.exitcode)
                    raise RuntimeError
    except (KeyboardInterrupt, RuntimeError):
        logging.info("shutting down …")
        for p in procs: p.terminate()
        for p in procs: p.join()

if __name__ == "__main__":
    main()
