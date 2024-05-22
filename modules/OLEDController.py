import time
import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306
from PIL import Image, ImageDraw, ImageFont
import random


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

    def run(self):
        try:
            while True:
                self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)
                self.draw.text((0, 0), "IP: {}".format(random.random()), font=self.font, fill=255)
                self.disp.image(self.image.rotate(180))
                self.disp.display()
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.clear_display()
            print("Display loop stopped.")
