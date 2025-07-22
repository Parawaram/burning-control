import subprocess
import shutil


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


def read_cpu_freq():
    """Return CPU frequency in MHz if available."""
    path = '/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq'
    try:
        with open(path) as f:
            return int(int(f.read().strip()) / 1000)
    except FileNotFoundError:
        return None


def read_memory():
    """Return used and total memory in MB."""
    try:
        info = {}
        with open('/proc/meminfo') as f:
            for line in f:
                key, value = line.split(':', 1)
                info[key] = int(value.strip().split()[0])
        total = info.get('MemTotal', 0) // 1024
        available = info.get('MemAvailable', info.get('MemFree', 0)) // 1024
        used = total - available
        return used, total
    except Exception:
        return None, None


def read_disk():
    """Return used and total disk space in GB."""
    usage = shutil.disk_usage('/')
    used = usage.used // (1024 ** 3)
    total = usage.total // (1024 ** 3)
    return used, total


def get_telemetry():
    """Gather Raspberry Pi telemetry data."""
    mem_used, mem_total = read_memory()
    disk_used, disk_total = read_disk()
    return {
        'cpu_temp': read_cpu_temp(),
        'cpu_freq': read_cpu_freq(),
        'mem_used': mem_used,
        'mem_total': mem_total,
        'disk_used': disk_used,
        'disk_total': disk_total,
    }
