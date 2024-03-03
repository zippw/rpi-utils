from gpiozero import CPUTemperature
import serial
import serial.tools.list_ports

# port = "/dev/ttyUSB0"

try:
    ports = serial.tools.list_ports.comports()
    port = next((p.device for p in ports), None)
    if port is None:
        raise ValueError("No COM port found.")

    ser = serial.Serial(port, baudrate=9600)

    while True:
        line = ser.readline().decode().strip()

        if line and line == "Hello":
            ser.write(b"0,192.168.31.201\x0D")
            cpu = CPUTemperature()
            ser.write(bytes("1,{}\x0D".format(cpu.temperature), encoding='utf-8'))

except ValueError as ve:
    print("Error:", str(ve))

except serial.SerialException as se:
    print("Serial port error:", str(se))

except Exception as e:
    print("An error occurred:", str(e))

# except KeyboardInterrupt:
#     pass

finally:
    if ser.is_open:
        ser.close()
        print("Serial connection closed.")