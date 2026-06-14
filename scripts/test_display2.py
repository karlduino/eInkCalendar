# SPDX-FileCopyrightText: 2019 Melissa LeBlanc-Williams for Adafruit Industries
# SPDX-License-Identifier: MIT

"""
ePaper Display Shapes and Text demo using the Pillow Library.
7.5" Tri-Color 800x480 display
https://www.adafruit.com/product/6415
"""

import board
import busio
import digitalio
from PIL import Image, ImageDraw, ImageFont
import datetime
from datetime import date, timedelta

from adafruit_epd.uc8179 import Adafruit_UC8179

# First define some color constants
WHITE = (0xFF, 0xFF, 0xFF)
BLACK = (0x00, 0x00, 0x00)
RED = (0xFF, 0x00, 0x00)

# Next define some constants to allow easy resizing of shapes and colors
BORDER = 20
FONTSIZE = 24
BACKGROUND_COLOR = BLACK
FOREGROUND_COLOR = WHITE
TEXT_COLOR = BLACK

# create the spi device and pins we will need
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
ecs = digitalio.DigitalInOut(board.CE0)
dc = digitalio.DigitalInOut(board.D22)
srcs = None
rst = digitalio.DigitalInOut(board.D27)
busy = digitalio.DigitalInOut(board.D17)

display = Adafruit_UC8179(800, 480,         # 7.5" tricolor 800x480 display
    spi,
    cs_pin=ecs,
    dc_pin=dc,
    sramcs_pin=srcs,
    rst_pin=rst,
    busy_pin=busy,
    tri_color = True
)

display.rotation = 0

width = display.width
height = display.height
image = Image.new("RGB", (width, height))

# clear the buffer
display.fill(WHITE)

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)
# empty it
draw.rectangle((0, 0, width, height), fill=WHITE)

# Draw an outline box
draw.rectangle((1, 1, width - 2, height - 2), outline=BLACK, fill=WHITE)

# Load default font.
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 56)
font28 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)

padding = 10
top = padding
x = (100+25)*4
bottom = height - padding

draw.text((x, top), "Hello", font=font, fill=BLACK)
draw.text((x, top + 50), "World!", font=font, fill=BLACK)

today = date.today()
weekday = today.strftime("%A")
month = today.strftime("%B")
day = today.strftime("%-d")

x = padding
y = padding
draw.text((x,y), day, font=font, fill=RED)
x += 80
y -= 2
draw.text((x,y), month, font=font28, fill=BLACK)
y += 28+4
draw.text((x,y), weekday, font=font28, fill=BLACK)

# Display image.
display.image(image)

display.display()


