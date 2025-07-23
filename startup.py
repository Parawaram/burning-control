import subprocess
import sys
from pathlib import Path


def main():
    root = Path(__file__).resolve().parent / 'backend'
    python = sys.executable
    processes = [
        subprocess.Popen([python, str(root / 'app.py')]),
        subprocess.Popen([python, str(root / 'oled_small.py')])
    ]
    try:
        for p in processes:
            p.wait()
    except KeyboardInterrupt:
        pass
    finally:
        for p in processes:
            if p.poll() is None:
                p.terminate()
        for p in processes:
            try:
                p.wait(timeout=5)
            except subprocess.TimeoutExpired:
                p.kill()


if __name__ == '__main__':
    main()
