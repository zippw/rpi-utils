from rpi_ws281x import Color, PixelStrip
import RPi.GPIO as GPIO
import sacn
import time


class LightController:
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

    def __init__(self):
        self.lights_check = False
        self.gradient_index = 0

        # GPIO setup
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.LIGHTS_SWITCH_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # Setup PixelStrips
        self.strips = [
            PixelStrip(self.LED_COUNT[i], self.LED_PIN[i])
            for i in range(len(self.LED_COUNT))
        ]
        for strip in self.strips:
            strip.begin()

        # Generate gradient
        self.gradient = self.generate_gradient(self.COLORS, self.STEP)

        # Setup sACN receiver
        self.receiver = sacn.sACNreceiver()
        self.receiver.start()

        @self.receiver.listen_on("universe", universe=self.UNIVERSE)
        def callback(packet):
            if self.lights_check:
                self.process_packet(packet)

        @self.receiver.listen_on("availability")
        def availability_callback(universe, changed):
            if universe == self.UNIVERSE:
                if changed == "available":
                    self.lights_check = True
                else:
                    self.lights_check = False
                self.fade_lights(self.lights_check)

    def generate_gradient(self, colors, step):
        gradient = []
        for i in range(len(colors)):
            gradient.append(colors[i])
            next_color = colors[(i + 1) % len(colors)]
            for j in range(1, step):
                gradient.append(
                    [
                        round(
                            colors[i][k] + ((next_color[k] - colors[i][k]) / step * j)
                        )
                        for k in range(3)
                    ]
                )
        return gradient

    def update_lights(self, gradient, index):
        for i in range(len(self.DEFAULT_LIGHT)):
            for j in range(self.LED_COUNT[self.DEFAULT_LIGHT[i]]):
                r, g, b = gradient[(index + j) % len(gradient)]
                self.strips[self.DEFAULT_LIGHT[i]].setPixelColor(j, Color(r, g, b))
            self.strips[self.DEFAULT_LIGHT[i]].show()
        return (index + 1) % len(gradient)

    def process_packet(self, packet):
        total_leds = sum(self.LED_COUNT)

        for i in range(total_leds):
            try:
                r, g, b = packet.dmxData[i * 3 : i * 3 + 3]

                for strip_index, strip in enumerate(self.strips):
                    if i < self.LED_COUNT[strip_index]:
                        strip.setPixelColor(i, Color(r, g, b))
                        break
                    i -= self.LED_COUNT[strip_index]

            except IndexError:
                break

        for strip in self.strips:
            strip.show()

    def ease_in_out_quint(self, x):
        return 16 * x**5 if x < 0.5 else 1 - ((-2 * x + 2) ** 5) / 2

    def fade_lights(self, on):
        for i in range(21):
            ease_value = self.ease_in_out_quint(i / 20)
            brightness = 255 * ease_value if on else 255 - (255 * ease_value)
            for strip in self.strips:
                if self.strips.index(strip) not in self.DEFAULT_LIGHT:
                    strip.setBrightness(round(brightness))
                    strip.show()
            time.sleep(self.LIGHTS_SWITCH_FADE_TIME / 20)

    def run(self):
        try:
            while True:
                if GPIO.input(self.LIGHTS_SWITCH_BUTTON_PIN) == False:
                    self.lights_check = not self.lights_check
                    self.fade_lights(self.lights_check)

                if not self.lights_check:
                    self.gradient_index = self.update_lights(
                        self.gradient, self.gradient_index
                    )
                    time.sleep(0.05)

        except KeyboardInterrupt:
            self.receiver.leave_multicast(1)
            self.receiver.stop()
            print("Receiver stopped.")

    def get_lights_check(self):
        return self.lights_check

    def set_lights_check(self, value):
        self.lights_check = value
        self.fade_lights(value)
