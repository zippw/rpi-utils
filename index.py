import time
import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306
from PIL import Image, ImageDraw, ImageFont
import random
from rpi_ws281x import Color, PixelStrip
import RPi.GPIO as GPIO
import sacn


class OLEDController:
    def __init__(self, rst=None, dc=23, spi_port=0, spi_device=0):
        self.disp = Adafruit_SSD1306.SSD1306_128_64(rst=rst)

        self.disp.begin()

        self.disp.clear()
        self.disp.display()

        self.width = self.disp.width
        self.height = self.disp.height
        self.image = Image.new("1", (self.width, self.height))  # 1 - 1 bit color image
        self.draw = ImageDraw.Draw(self.image)
        self.font = ImageFont.load_default()

    def clear_display(self):
        self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)
        self.disp.image(self.image.rotate(180))
        self.disp.display()

    def update_display(self):
        self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)
        self.draw.text(
            (0, 0), "IP: {}".format(random.random()), font=self.font, fill=255
        )
        self.disp.image(self.image.rotate(180))
        self.disp.display()


class LightController:
    UNIVERSE = 1
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


if __name__ == "__main__":
    oled_controller = OLEDController()
    light_controller = LightController()

    try:
        oled_controller.update_display()
        while True:
            if not light_controller.lights_check:
                light_controller.gradient_index = light_controller.update_lights(
                    light_controller.gradient, light_controller.gradient_index
                )
            # time.sleep(0.1)

    except KeyboardInterrupt:
        oled_controller.clear_display()
        light_controller.receiver.leave_multicast(1)
        light_controller.receiver.stop()
        print("Program stopped.")
