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
        # Read a line of data from the serial port
        line = ser.readline().decode().strip()

        if line:
            print("Received:", line)
            # ser.write(b"0,192.168.31.201")
            # cpu = CPUTemperature()
            # ser.write(b"1,{cpu.temperature}")

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