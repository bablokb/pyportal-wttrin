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
import adafruit_adt7410
import adafruit_touchscreen
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label
from adafruit_esp32spi import adafruit_esp32spi, adafruit_esp32spi_wifimanager

from secrets import secrets  # file secrets.py

# --- constants   -----------------------------------------------------

WTTRIN_URL    = "https://wttr.in/München?AT0&lang=de"
WTTRIN_INT    = 120
CLOCK_INT     = 60
BACKLIGHT_INT = 300

WDAY={0:'Mo',
      1:'Di',
      2:'Mi',
      3:'Do',
      4:'Fr',
      5:'Sa',
      6:'So'
  }

FONT  = bitmap_font.load_font("/DejaVuSansMono-Bold-18.bdf")
COLOR = 0xFFFFFF

# --- helper-class for timers   ---------------------------------------

class Timer(object):
  def __init__(self,dur):
    self._dur = dur     # in seconds
  def start(self,expired=False):
    if expired:
      self._start = 0
    else:
      self._start = time.time()
  def rest(self,now=None):
    if now is None:
      now = time.time()
    return max(self._dur-(now-self._start),0)

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
def set_text(group,text,offset=0):
  if len(group) == 3:
    del group[2]
  text_area = label.Label(FONT,text=text,color=COLOR,line_spacing=1)
  (x,y,w,h) = text_area.bounding_box

  # Set the location at top left
  text_area.x = 0
  text_area.y = -y + offset
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

# --- wait for touch-event   ------------------------------------------
def wait_for_touch(ts):
  while True:
    if ts.touch_point:
      print("screen touched")
      return
    else:
      time.sleep(0.1)

# --- update header (datetime+temp)   ---------------------------------

def update_header(header,sensor):
  text = "%s   %04.1f°C" % (get_time(),sensor.temperature)
  if header is None:
    header = label.Label(FONT,text=text,color=COLOR)
    header.y = -header.bounding_box[1]
    return header
  else:
    header.text = text

# --- main-loop   -----------------------------------------------------

i2c_bus = busio.I2C(board.SCL, board.SDA)
adt     = adafruit_adt7410.ADT7410(i2c_bus, address=0x48)
adt.high_resolution = True

display = board.DISPLAY
group   = displayio.Group()
wdata   = "no data available yet"

# set background
print("\nloading background")
group.append(get_background("wolken.bmp"))

# connect to internet
print("connecting to AP ...")
connection = get_wifi(secrets)

# set local time
print("get local time from worldtimeapi.org")
set_time(connection,secrets['timezone'])
now = get_time()
print("local time is: %s" % now)

# add header
header = update_header(None,adt)
group.append(header)

# setup touchscreen
touchscreen = adafruit_touchscreen.Touchscreen(
  board.TOUCH_XL, board.TOUCH_XR,board.TOUCH_YD, board.TOUCH_YU,
  calibration=((5200, 59000),(5800, 57000)),
  size=(board.DISPLAY.width, board.DISPLAY.height))

# setup timers
w_tmr = Timer(WTTRIN_INT)
c_tmr = Timer(CLOCK_INT)
b_tmr = Timer(BACKLIGHT_INT)
w_tmr.start(True)
c_tmr.start(True)
b_tmr.start(False)

while True:
  update = False
  # turn off backlight when timer expires
  if not b_tmr.rest():
    board.DISPLAY.auto_brightness = False
    board.DISPLAY.brightness      = 0.0
    wait_for_touch(touchscreen)
    board.DISPLAY.auto_brightness = True
    b_tmr.start()

  # update time
  rest = c_tmr.rest()
  if not rest:
    print("clock-timer expired")
    update = True
    update_header(header,adt)
    c_tmr.start()

  # update weather-info
  rest = w_tmr.rest()
  if not rest:
    print("weather-timer expired")
    update = True
    try:
      print("connecting to https://wttr.in")
      response = connection.get(WTTRIN_URL)
      wdata    = response.text
    except:
      print("wttr.in error: code: %d, reason: %s" %
            (response.status_code,response.reason))
    finally:
      response.close()
    w_tmr.start()

  # update display
  if update:
    set_text(group,wdata,header.bounding_box[3]+header.height)
    display.show(group)

  # wait
  now = time.time()
  time.sleep(min(c_tmr.rest(now),w_tmr.rest(now)))
