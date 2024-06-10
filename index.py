import time
import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306
from PIL import Image, ImageDraw, ImageFont
from rpi_ws281x import Color, PixelStrip
import RPi.GPIO as GPIO
import sacn
import subprocess
import psutil
import re
import threading

ASSETS_PATH = "/home/zw/rpi-utils/assets/"


class OLEDController:
    def __init__(self):
        self.disp = Adafruit_SSD1306.SSD1306_128_64(rst=None)

        self.disp.begin()

        self.disp.clear()
        self.disp.display()

        self.width = self.disp.width
        self.height = self.disp.height
        self.image = Image.new("1", (self.width, self.height))  # 1 - 1 bit color image
        self.draw = ImageDraw.Draw(self.image)
        self.icons = {
            "cpu": Image.open(ASSETS_PATH + "cpu.png").resize((14, 14)).convert("1")
        }
        self.bg = Image.open(ASSETS_PATH + "frame0.png").convert("1")
        self.font = ImageFont.truetype(ASSETS_PATH + "Consolas.ttf", 14)  # 14 = 16 chars widths
        self.time_font = ImageFont.truetype(ASSETS_PATH + "Consolas.ttf", 9)  # 14 = 16 chars widths
        # self.font = ImageFont.load_default(14)

    def clear_display(self):
        self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)
        self.disp.image(self.image.rotate(180))
        self.disp.display()

    def update_display(self, stats):
        self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)
        self.image.paste(self.bg, (0, 0))
        # self.image.paste(self.icons['cpu'], (4, 18))

        # self.draw.text((4, 4), "▮▮▮▮▮▯▯▯▯▯", font=self.font, fill=255)
        self.draw.text((4, 18), stats["temperature"], font=self.font, fill=255)
        self.draw.text((4, 32), stats["cpu_usage"], font=self.font, fill=255)
        temp_progress = 0 if stats["memory_usage"] == "N/A" else round(60 * (float(stats["memory_usage"].strip('%')) / 100))
        self.draw.rectangle((65, 3, 65 + temp_progress, 3 + 4), fill=255)
        self.disp.image(self.image.rotate(180))
        self.disp.display()
        self.image.save("a.png")


class Monitoring:
    def __init__(self):
        self.stats = {
            "time": "N/A",
            "temperature": "N/A",
            "cpu_usage": "N/A",
            "memory_usage": "N/A",
        }

    def updater(self, func, key, interval):
        while True:
            self.stats[key] = func()
            time.sleep(interval)

    def get_time(self):
        return time.strftime("%H:%M:%S")

    def get_temperature(self):
        try:
            output = subprocess.check_output(["sensors"], encoding="utf-8")
            temp_pattern = re.compile(r"temp\d+:\s+\+([\d\.]+)°C")
            temperatures = temp_pattern.findall(output)
            return f"{temperatures[0]}°C" if temperatures else "N/A"
        except subprocess.CalledProcessError as e:
            print(f"Failed to get temperature: {e}")
            return "N/A"

    def get_cpu_usage(self):
        return f"{psutil.cpu_percent(interval=1)}%"

    def get_memory_usage(self):
        return f"{psutil.virtual_memory().percent}%"

    def main(self):
        threads = [
            threading.Thread(target=self.updater, args=(self.get_time, "time", 1)),
            threading.Thread(
                target=self.updater, args=(self.get_temperature, "temperature", 5)
            ),
            threading.Thread(
                target=self.updater, args=(self.get_cpu_usage, "cpu_usage", 1)
            ),
            threading.Thread(
                target=self.updater, args=(self.get_memory_usage, "memory_usage", 1)
            ),
        ]

        for thread in threads:
            thread.daemon = True
            thread.start()

        while True:
            oled_controller.update_display(self.stats)
            time.sleep(1)


class LightController:
    UNIVERSE = 1
    LIGHTS_SWITCH_FADE_TIME = 0.3
    LED_COUNT = [18, 30, 7]
    LED_PIN = [10, 21, 18]
    # DEFAULT_LIGHT = [2]
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
                # if self.strips.index(strip) not in self.DEFAULT_LIGHT:
                strip.setBrightness(round(brightness))
                strip.show()
            time.sleep(self.LIGHTS_SWITCH_FADE_TIME / 20)


if __name__ == "__main__":
    oled_controller = OLEDController()
    light_controller = LightController()
    monitoring = Monitoring()

    try:
        monitoring.main()

    except KeyboardInterrupt:
        oled_controller.clear_display()
        light_controller.receiver.leave_multicast(1)
        light_controller.receiver.stop()
        print("Program stopped.")
