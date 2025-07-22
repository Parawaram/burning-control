import subprocess
import shutil
from typing import Optional, Tuple


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


_last_cpu_times: Optional[Tuple[int, int]] = None


def read_cpu_usage() -> Optional[float]:
    """Return CPU usage percentage if available."""
    global _last_cpu_times
    try:
        with open('/proc/stat') as f:
            parts = f.readline().strip().split()[1:]
            values = [int(x) for x in parts]
        idle = values[3] + values[4]
        total = sum(values)
        if _last_cpu_times is None:
            _last_cpu_times = (idle, total)
            return None
        last_idle, last_total = _last_cpu_times
        _last_cpu_times = (idle, total)
        diff_idle = idle - last_idle
        diff_total = total - last_total
        if diff_total == 0:
            return None
        usage = 100.0 * (1 - diff_idle / diff_total)
        return round(usage, 1)
    except Exception:
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
        'cpu_usage': read_cpu_usage(),
        'mem_used': mem_used,
        'mem_total': mem_total,
        'disk_used': disk_used,
        'disk_total': disk_total,
    }
