import importlib
import logging
from multiprocessing import Process, Queue
import time

workers = {
    "reader": "backend.app",
    "oled_small": "backend.oled_small",
    "logger": "backend.logger",
}


def main():
    logging.basicConfig(level=logging.INFO)
    q = Queue(maxsize=200)
    processes = []
    for name, mod_path in workers.items():
        try:
            mod = importlib.import_module(mod_path)
        except Exception as e:
            logging.error("Failed to import %s: %s", mod_path, e)
            continue
        p = Process(target=mod.run, args=(q,), name=name)
        p.start()
        processes.append(p)

    try:
        while processes:
            time.sleep(0.2)
            for p in processes[:]:
                if not p.is_alive():
                    if p.exitcode != 0:
                        logging.error("%s exited with code %s", p.name, p.exitcode)
                        raise RuntimeError
                    processes.remove(p)
    except KeyboardInterrupt:
        logging.info("Interrupted, shutting down...")
    except RuntimeError:
        logging.info("Stopping remaining workers...")
    finally:
        for p in processes:
            if p.is_alive():
                p.terminate()
        for p in processes:
            p.join()


if __name__ == "__main__":
    main()
