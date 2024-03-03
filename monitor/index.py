from gpiozero import CPUTemperature
import serial
import serial.tools.list_ports

# port = "/dev/ttyUSB0"

ports = serial.tools.list_ports.comports()

for port in ports:
    ser = serial.Serial(port, baudrate=9600)
    ser.write(b"0,192.168.31.201")
    cpu = CPUTemperature()
    ser.write(b"1,{cpu.temperature}")
    ser.close()