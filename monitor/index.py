from gpiozero import CPUTemperature
import psutil
import serial
from datetime import datetime
import serial.tools.list_ports
import time

try:
    ports = serial.tools.list_ports.comports()
    port = next((p.device for p in ports), None)
    if port is None:
        raise ValueError("No COM port found.")

    ser = serial.Serial(port, baudrate=9600)

    prev_cpu_temp = None
    prev_memory_available = None
    prev_time = None

    while True:
        msg = ser.readline().decode().strip()
        print("got 1 msg")

        if msg and msg == "Hello":
            while True:
                cpu = CPUTemperature()
                current_cpu_temp = round(cpu.temperature, 2)
                current_memory_available = round(psutil.virtual_memory().available / (2 ** 30), 2)
                current_time = str(datetime.now().strftime("%H:%M"))
                print("generated data")

                if (current_cpu_temp != prev_cpu_temp) or (current_memory_available != prev_memory_available) or (current_time != prev_time):
                    ser.write(bytes("0,{}\x0D".format(current_cpu_temp), encoding='utf-8'))
                    ser.write(bytes("1,{}\x0D".format(current_memory_available), encoding='utf-8'))
                    ser.write(bytes("2,{}\x0D".format(current_time), encoding='utf-8'))

                time.sleep(1)

                new_msg = ser.readline().decode().strip()
                if new_msg and new_msg == "Hello":
                    print("got new msg")
                    break

except ValueError as ve:
    print("ValueError:", str(ve))

except serial.SerialException as se:
    print("Serial port error:", str(se))

except Exception as e:
    print("An error occurred:", str(e))

except KeyboardInterrupt:
    pass

finally:
    if ser.is_open:
        ser.close()
        print("Serial connection closed.")