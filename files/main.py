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
def get_label(text,font,color):
  text_area = label.Label(font, text=text, color=color)
  (x,y,w,h) = text_area.bounding_box

  # Set the location at top left
  text_area.x = 0
  text_area.y = -y

  return text_area

# --- main-loop   -----------------------------------------------------

display = board.DISPLAY
group   = displayio.Group()
FONT    = bitmap_font.load_font("/DroidSansMono-16.bdf")
COLOR   = 0xFFFFFF

# set background
group.append(get_background("wolken.bmp"))

connection = get_wifi(secrets)
try:
  response = connection.get("https://wttr.in/München?AT0")
  text = response.text
except:
  text = "keine Daten erhalten"
group.append(get_label(text,FONT,COLOR))

# Show it
display.show(group)

while True:
  time.sleep(60)
