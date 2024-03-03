from gpiozero import CPUTemperature
import serial
import serial.tools.list_ports

port = "COM1"
baudrate = 9600
ser = serial.Serial(port, baudrate=baudrate)

ports = serial.tools.list_ports.comports()

for port in ports:
    print(port.device)

ser.write(b"0,192.168.31.201")

cpu = CPUTemperature()
ser.write(b"1,{cpu.temperature}")

ser.close()