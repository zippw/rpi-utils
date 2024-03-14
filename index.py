from rpi_ws281x import Color, PixelStrip, ws
import RPi.GPIO as GPIO
import sacn
import numpy
import time
import sys

LED_COUNT = [18, 30, 7]
LED_PIN = [12, 21, 10]

BUTTON_PIN = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

lights_check = True

while True:
    input_state = GPIO.input(BUTTON_PIN)
    if input_state == False:
        lights_check = not lights_check
        print('Button Pressed', lights_check)
        time.sleep(0.2)

strips = [
    PixelStrip(LED_COUNT[0], LED_PIN[0]),
    PixelStrip(LED_COUNT[1], LED_PIN[1]),
    PixelStrip(LED_COUNT[2], LED_PIN[2]),
]

for i in range(len(strips)):
    strips[i].begin()

def process_packet(packet):
    for i in range(sum(LED_COUNT)):
        try:
            r = packet.dmxData[i * 3]
            g = packet.dmxData[i * 3 + 1]
            b = packet.dmxData[i * 3 + 2]

            for strip_index in range(len(strips)):
                if i < LED_COUNT[strip_index]:
                    strips[strip_index].setPixelColor(i, Color(r, g, b))
                    break
                else:
                    i -= LED_COUNT[strip_index]

        except IndexError:
            pass

    for i in range(len(strips)):
        strips[i].show()

if __name__ == '__main__':
    try:
        receiver = sacn.sACNreceiver()
        receiver.start()

        @receiver.listen_on("universe", universe=1)
        def callback(packet):
            process_packet(packet)
        receiver.join_multicast(1)
        input("Press ^C to exit\n")
    except KeyboardInterrupt:
        receiver.leave_multicast(1)
        receiver.stop()
        print("Receiver stopped.")