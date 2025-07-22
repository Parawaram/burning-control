import subprocess


def read_cpu_temp():
    """Return CPU temperature in Celsius if available."""
    try:
        with open('/sys/class/thermal/thermal_zone0/temp') as f:
            return round(int(f.read().strip()) / 1000, 1)
    except FileNotFoundError:
        try:
            result = subprocess.run(['vcgencmd', 'measure_temp'], capture_output=True, text=True)
            if result.returncode == 0:
                out = result.stdout.strip()
                if out.startswith('temp=') and out.endswith("'C"):
                    return float(out.replace('temp=', '').replace("'C", ''))
        except Exception:
            pass
    return None
