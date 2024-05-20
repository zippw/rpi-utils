from rpi_ws281x import Color, PixelStrip, ws
import RPi.GPIO as GPIO
import sacn
import numpy
import time
import sys

# setup lights switch
LIGHTS_SWITCH_BUTTON_PIN = 17
LIGHTS_SWITCH_FADE_TIME = 0.3

GPIO.setmode(GPIO.BCM)
GPIO.setup(LIGHTS_SWITCH_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# setup lights
LED_COUNT = [18, 30, 7]
LED_PIN = [10, 21, 18]
DEFAULT_LIGHT = [2]  # indexes, ex. 2 -> LED_COUNT[2]

strips = [
    PixelStrip(LED_COUNT[0], LED_PIN[0]),
    PixelStrip(LED_COUNT[1], LED_PIN[1]),
    PixelStrip(LED_COUNT[2], LED_PIN[2]),
]

for i in range(len(strips)):
    strips[i].begin()

# Gradient generator
step = 10


def stepped(c1, c2, i):
    return round(c1 + ((c2 - c1) / step * i))


colors = [
    [255, 113, 206],
    [185, 103, 255],
    [1, 205, 254],
    [5, 255, 161],
    [255, 251, 250],
    [255, 113, 206],
]
gradient = []
for i in range(len(colors)):
    gradient.append(colors[i])
    n = (i + 1) % len(colors)
    for j in range(1, step):
        gradient.append(
            [
                stepped(colors[i][0], colors[n][0], j),
                stepped(colors[i][1], colors[n][1], j),
                stepped(colors[i][2], colors[n][2], j),
            ]
        )

lenta = gradient[slice(0, 7)]


def gen_gradient(gradient, c):
    # str = "\x1B[0;0H\x1B[0J"
    for i in range(len(lenta)):
        r, g, b = gradient[(c + i) % len(gradient)]
        # str += "\x1B[48;2;{};{};{}m  \x1B[0m".format(int(r), int(g), int(b))
        for s in range(len(DEFAULT_LIGHT)):
            strips[s].setPixelColor(i, Color(r, g, b))
    # print(str)
    c = (c + 1) % len(gradient)
    for s in range(len(DEFAULT_LIGHT)):
        strips[s].show()
    return c


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


def ease_in_out_quint(x):
    return 16 * x**5 if x < 0.5 else 1 - ((-2 * x + 2) ** 5) / 2


if __name__ == "__main__":
    try:
        # setup local server
        receiver = sacn.sACNreceiver()
        receiver.start()

        @receiver.listen_on("universe", universe=1)
        def callback(packet):
            if lights_check == True:
                process_packet(packet)
        @receiver.listen_on("availability")
        def callback(universe, changed):
            print(universe, changed)

        receiver.join_multicast(1)

        # lights switch
        lights_check = True
        c = 0  # default light counter
        while True:
            input_state = GPIO.input(LIGHTS_SWITCH_BUTTON_PIN)
            if input_state == False:
                lights_check = not lights_check

                for i in range(21):
                    x = i / 20
                    ease_value = ease_in_out_quint(x)
                    brightness = (
                        255 * ease_value if lights_check else 255 - (255 * ease_value)
                    )

                    for i in range(len(strips)):
                        if i not in DEFAULT_LIGHT:
                            strips[i].setBrightness(round(brightness))
                            strips[i].show()

                    time.sleep(LIGHTS_SWITCH_FADE_TIME / 20)

                print("Button Pressed", lights_check)
            if lights_check == False:
                c = gen_gradient(gradient, c)
                time.sleep(0.05)
    except KeyboardInterrupt:
        receiver.leave_multicast(1)
        receiver.stop()
        print("Receiver stopped.")
