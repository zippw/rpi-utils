import time

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

RST = None  # on the PiOLED this pin isnt used
# Note the following are only used with SPI:
DC = 23
SPI_PORT = 0
SPI_DEVICE = 0

# 128x32 display with hardware I2C:
disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST)

# Initialize library.
disp.begin()

# Clear display.
disp.clear()
disp.display()

w = disp.width
h = disp.height
image = Image.new("1", (w, h)) # 1 - 1 bit color image
draw = ImageDraw.Draw(image)
draw.rectangle((0, 0, w, h), outline=0, fill=0) # blank rect
font = ImageFont.load_default()
font = ImageFont.truetype('Vermin_Vibes_1989.ttf', 8) # http://www.dafont.com/bitmap.php

while True:
    draw.rectangle((0, 0, w, h), outline=0, fill=0) # blank rect
    draw.text((0, 0), "IP: ", fill=255)
    rotated_image = image.rotate(180)
    
    disp.image(rotated_image)
    disp.display()
    time.sleep(0.1)
