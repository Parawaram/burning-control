import subprocess
import sys
from pathlib import Path


def main():
    root = Path(__file__).resolve().parent
    python = sys.executable
    p = subprocess.Popen([python, str(root / 'main.py')])
    try:
        p.wait()
    except KeyboardInterrupt:
        pass
    finally:
        if p.poll() is None:
            p.terminate()
            try:
                p.wait(timeout=5)
            except subprocess.TimeoutExpired:
                p.kill()


if __name__ == '__main__':
    main()
