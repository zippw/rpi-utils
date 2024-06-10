import time
import threading
import psutil
import subprocess
import re


def get_time():
    return time.strftime("%H:%M:%S")


def get_temperature():
    try:
        output = subprocess.check_output(["sensors"], encoding="utf-8")
        temp_pattern = re.compile(r"temp\d+:\s+\+([\d\.]+)°C")
        temperatures = temp_pattern.findall(output)
        return f"{temperatures[0]}°C" if temperatures else "N/A"
    except subprocess.CalledProcessError as e:
        print(f"Failed to get temperature: {e}")
        return "N/A"


def get_cpu_usage():
    return f"{psutil.cpu_percent(interval=1)}%"


def get_memory_usage():
    return f"{psutil.virtual_memory().percent}%"


results = {
    "time": "N/A",
    "temperature": "N/A",
    "cpu_usage": "N/A",
    "memory_usage": "N/A",
}


def update_display():
    print(
        f"{results['time']}\n{results['temperature']}\n{results['cpu_usage']}\n{results['memory_usage']}"
    )


def updater(func, key, interval):
    while True:
        results[key] = func()
        time.sleep(interval)


def main():
    threads = [
        threading.Thread(target=updater, args=(get_time, "time", 1)),
        threading.Thread(target=updater, args=(get_temperature, "temperature", 5)),
        threading.Thread(target=updater, args=(get_cpu_usage, "cpu_usage", 1)),
        threading.Thread(target=updater, args=(get_memory_usage, "memory_usage", 1)),
    ]

    for thread in threads:
        thread.daemon = True
        thread.start()

    try:
        while True:
            update_display()
            time.sleep(1)  # Обновление дисплея каждые 1 секунду
    except KeyboardInterrupt:
        print("Программа остановлена пользователем.")


if __name__ == "__main__":
    main()
