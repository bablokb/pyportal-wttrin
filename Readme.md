Geek-Weather with PyPortal and wettr.in
=======================================

Overview
--------

This PyPortal-application displays weather-data collected from
[https://wttr.in](https://wttr.in). After a preconfigured interval,
the backlight is turned off to prevent burn-in. Touching the screen
turns the backlight back on again.

Besides the weather-data from the internet, the portal displays the local
time and the temperature from the builtin-sensor.

The application contains a number of building-blocks that are useful for
all kinds of applications, so it also serves as a blueprint.


Features
--------

  - fill background with an image
  - connect to AP
  - query data and parse results
  - set local time from worldtimeapi.org
  - display text
  - read on-board temperature sensor
  - process touch-events
  - turn backlight on and off


Installation
------------

Just copy everything below the `files`-directory to your PyPortal. Create
a file called `secrets.py` in the root-directory. Note that there is
a template (`secrets-template.py`) which you can rename and edit.

In `main.py` you have to change the location in the variable `WTTRIN_URL`
to your location.


Libraries and Fonts
-------------------

Some files are not provided for legal or technical reasons (CircuitPython
libraries must match the version of your installed interpreter).

The directory-tree contains (empty) files with the names
`ADD_xxx`. Replace these files with the corresponding file or directory.

Specifically, the application needs the following libraries:

  - adafruit_adt7410
  - adafruit_bitmap_font
  - adafruit_bus_device
  - adafruit_display_text
  - adafruit_esp32spi
  - adafruit_register
  - adafruit_requests
  - adafruit_touchscreen
  - neopixel

The application uses the *DejaVuSansMono-Bold-18* font. You have to create
the font yourself. Adafruit provides a simple guide https://learn.adafruit.com/custom-fonts-for-pyportal-circuitpython-display. The whole process takes about
five minutes.


Where to go
-----------

Of course a project like this is never finished. Here are some ideas you
might want to implement:

  - cycle through multiple locations at every touch
  - replace the builin temperature-sensor with an external sensor
    attached to the I2C-connector (e.g. a BME280 or LM75)
  - change the background image according to the weather condition
  - use the json-output of wttr.in and show current weather and forecast
  - query the data directly from OpenWeatherMap
