from rpi_ws281x import Color, PixelStrip
import RPi.GPIO as GPIO
import sacn
import time

# Constants
UNIVERSE = 1
LIGHTS_SWITCH_BUTTON_PIN = 17
LIGHTS_SWITCH_FADE_TIME = 0.3
LED_COUNT = [18, 30, 7]
LED_PIN = [10, 21, 18]
DEFAULT_LIGHT = [2]
STEP = 10
COLORS = [
    [255, 0, 4],
    [255, 0, 230],
    [0, 0, 255],
    [0, 179, 255],
    [0, 255, 81],
    [234, 255, 0],
    [255, 179, 0],
    [255, 0, 4],
]
# COLORS = [
#     [255, 113, 206],
#     [185, 103, 255],
#     [1, 205, 254],
#     [5, 255, 161],
#     [255, 251, 250],
#     [255, 113, 206],
# ]

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(LIGHTS_SWITCH_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Setup PixelStrips
strips = [PixelStrip(LED_COUNT[i], LED_PIN[i]) for i in range(len(LED_COUNT))]
for strip in strips:
    strip.begin()


# Gradient generator
def generate_gradient(colors, step):
    gradient = []
    for i in range(len(colors)):
        gradient.append(colors[i])
        next_color = colors[(i + 1) % len(colors)]
        for j in range(1, step):
            gradient.append(
                [
                    round(colors[i][k] + ((next_color[k] - colors[i][k]) / step * j))
                    for k in range(3)
                ]
            )
    return gradient


gradient = generate_gradient(COLORS, STEP)


def update_lights(gradient, index):
    for i in range(len(DEFAULT_LIGHT)):
        for j in range(LED_COUNT[DEFAULT_LIGHT[i]]):
            r, g, b = gradient[(index + j) % len(gradient)]
            strips[DEFAULT_LIGHT[i]].setPixelColor(j, Color(r, g, b))
        strips[DEFAULT_LIGHT[i]].show()
    return (index + 1) % len(gradient)


def process_packet(packet):
    total_leds = sum(LED_COUNT)

    for i in range(total_leds):
        try:
            r, g, b = packet.dmxData[i * 3 : i * 3 + 3]

            for strip_index, strip in enumerate(strips):
                if i < LED_COUNT[strip_index]:
                    strip.setPixelColor(i, Color(r, g, b))
                    break
                i -= LED_COUNT[strip_index]

        except IndexError:
            break

    for strip in strips:
        strip.show()


def ease_in_out_quint(x):
    return 16 * x**5 if x < 0.5 else 1 - ((-2 * x + 2) ** 5) / 2


def fade_lights(on):
    for i in range(21):
        ease_value = ease_in_out_quint(i / 20)
        brightness = 255 * ease_value if on else 255 - (255 * ease_value)
        for strip in strips:
            if strips.index(strip) not in DEFAULT_LIGHT:
                strip.setBrightness(round(brightness))
                strip.show()
        time.sleep(LIGHTS_SWITCH_FADE_TIME / 20)


# Main loop
if __name__ == "__main__":
    try:
        receiver = sacn.sACNreceiver()
        receiver.start()

        @receiver.listen_on("universe", universe=UNIVERSE)
        def callback(packet):
            if lights_check:
                process_packet(packet)

        @receiver.listen_on("availability")
        def availability_callback(universe, changed):
            global lights_check
            if universe == UNIVERSE:
                if changed == "available":
                    lights_check = True
                else:
                    lights_check = False
                    print(f"Universe {universe} is now {changed}")
                time.sleep(1)
                fade_lights(lights_check)

        lights_check = True
        gradient_index = 0

        while True:
            if GPIO.input(LIGHTS_SWITCH_BUTTON_PIN) == False:
                lights_check = not lights_check
                fade_lights(lights_check)
                print("Button Pressed", lights_check)

            if not lights_check:
                gradient_index = update_lights(gradient, gradient_index)
                time.sleep(0.05)

    except KeyboardInterrupt:
        receiver.leave_multicast(1)
        receiver.stop()
        print("Receiver stopped.")
