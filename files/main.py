# -------------------------------------------------------------------------
# PyPortal code: display weather-information from https://wttr.in
#
# See the Readme.md for necessary libraries.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pygame-wttrin
#
# -------------------------------------------------------------------------

import board
import busio
from digitalio import DigitalInOut
import time
import neopixel
import displayio
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label
from adafruit_esp32spi import adafruit_esp32spi, adafruit_esp32spi_wifimanager

from secrets import secrets  # file secrets.py

# ---------------------------------------------------------------------
def get_wifi(secrets):
  esp32_ready = DigitalInOut(board.ESP_BUSY)
  esp32_gpio0 = DigitalInOut(board.ESP_GPIO0)
  esp32_reset = DigitalInOut(board.ESP_RESET)
  esp32_cs    = DigitalInOut(board.ESP_CS)
  spi         = busio.SPI(board.SCK, board.MOSI, board.MISO)
  esp         = adafruit_esp32spi.ESP_SPIcontrol(
                  spi, esp32_cs, esp32_ready,esp32_reset, esp32_gpio0)
  status_rgb  = neopixel.NeoPixel(board.NEOPIXEL,1,brightness=0.2)
  return adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager(
                  esp,secrets,status_rgb)

# ---------------------------------------------------------------------
def get_background(filename):
  bg_file = open(filename, "rb")
  background = displayio.OnDiskBitmap(bg_file)
  return displayio.TileGrid(background,
                            pixel_shader=displayio.ColorConverter())

# ---------------------------------------------------------------------
def set_text(group,text,font,color):
  if len(group) == 2:
    del group[1]
  text_area = label.Label(font, text=text, color=color)
  (x,y,w,h) = text_area.bounding_box

  # Set the location at top left
  text_area.x = 0
  text_area.y = -y
  group.append(text_area)

# --- main-loop   -----------------------------------------------------

display = board.DISPLAY
group   = displayio.Group()
FONT    = bitmap_font.load_font("/DroidSansMono-16.bdf")
COLOR   = 0xFFFFFF

# set background
group.append(get_background("wolken.bmp"))

textbox = set_text(group,"connecting to AP ...",FONT,COLOR)

# Show it
display.show(group)

# connect to internet
connection = get_wifi(secrets)

weather_data = "no data available yet"

while True:
  try:
    set_text(group,"connecting to https://wttr.in",FONT,COLOR)
    display.show(group)
    response     = connection.get("https://wttr.in/München?AT0")
    weather_data = response.text
  except:
    pass           # keep old data

  set_text(group,weather_data,FONT,COLOR)
  display.show(group)

  # wait
  time.sleep(120)
