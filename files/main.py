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
import rtc
import neopixel
import displayio
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label
from adafruit_esp32spi import adafruit_esp32spi, adafruit_esp32spi_wifimanager

from secrets import secrets  # file secrets.py

# --- constants   -----------------------------------------------------

WDAY={0:'Mon',
      1:'Die',
      2:'Mit',
      3:'Don',
      4:'Fre',
      5:'Sam',
      6:'Son'
  }

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

# ---------------------------------------------------------------------
def set_time(con,tz):
  response = con.get("http://worldtimeapi.org/api/timezone/"+tz)
  tinfo    = response.json()
  print(tinfo['datetime'])
  rtc.RTC().datetime = time.localtime(tinfo['unixtime']+tinfo['raw_offset'])
  response.close()

# ---------------------------------------------------------------------
def get_time():
  now = rtc.RTC().datetime
  return ("%s, %02d.%02d.%02d %02d:%02d" %
          (WDAY[now.tm_wday],now.tm_mday,now.tm_mon,now.tm_year,
           now.tm_hour,now.tm_min))

# --- main-loop   -----------------------------------------------------

display = board.DISPLAY
group   = displayio.Group()
FONT    = bitmap_font.load_font("/DroidSansMono-16.bdf")
COLOR   = 0xFFFFFF

# set background
print("\nloading background")
group.append(get_background("wolken.bmp"))

# connect to internet
print("connecting to AP ...")
connection = get_wifi(secrets)

# set local time
print("get local time from worldtimeapi.org")
set_time(connection,secrets['timezone'])
print("local time is: %s" % get_time())

weather_data = "no data available yet"

while True:
  try:
    print("connecting to https://wttr.in")
    response     = connection.get("https://wttr.in/München?AT0")
    weather_data = response.text
  except:
    print("wttr.in error: code: %d, reason: %s" %
          (response.status_code,response.reason))
  finally:
    response.close()

  set_text(group,weather_data,FONT,COLOR)
  display.show(group)

  # wait
  time.sleep(120)
