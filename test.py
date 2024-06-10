import psutil
import subprocess
import re


def get_temperatures():
    try:
        temp_pattern = re.compile(r"temp\d+:\s+\+([\d\.]+)°C")
        temperatures = temp_pattern.findall(
            subprocess.check_output(["sensors"], encoding="utf-8")
        )
        return temperatures[0]
    except subprocess.CalledProcessError as e:
        print(f"Failed to get temperature: {e}")
        return "0"


cpu_usage = f"{psutil.cpu_percent(interval=1)}%"
memory_usage = f"{psutil.virtual_memory().percent}%"
temperature = f"{get_temperatures()}°C"

print(cpu_usage, memory_usage, temperature)
