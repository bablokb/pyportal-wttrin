#!/usr/bin/python3
# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# Pygame-fbgui code: display weather-information from https://wttr.in
#
# This is an alternative implementation for a Pi with a small display using
# the library pygame-fbgui (see https://github.com/bablokb/pygame-fbgui)
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pygame-wttrin
#
# -------------------------------------------------------------------------

import fbgui
import os, sys, time, datetime, threading, locale, traceback
import requests

class Display(fbgui.App):
  WTTRIN_URL  = "https://wttr.in/Muenchen?AT0&lang=de"

  # --- constructor   --------------------------------------------------
  
  def __init__(self,settings=fbgui.Settings()):
    super(Display,self).__init__(settings=settings)
    self._imgpath = settings.imgpath
    self._create_widgets()
    self._main.pack()
    self.set_widget(self._main)

  # --- create widget-tree   --------------------------------------------

  def _create_widgets(self):
    self._main = fbgui.Panel("main",
                             settings=fbgui.Settings({
                             }),toplevel=True)
    fbgui.Image("background",img=self._imgpath,parent=self._main)
    self._vbox = fbgui.VBox("vbox",
                            settings=fbgui.Settings({
                             'align': (fbgui.TOP,fbgui.LEFT),
                             'width': 1.0,
                             'height': 1.0,
                             'padding': 10
                            }),parent=self._main)
    self._header = fbgui.Panel("header",
                            settings=fbgui.Settings({
                             'width': 1.0,
                             'padding': 10
                            }),parent=self._vbox)
    self._dtlabel = fbgui.Label("datetime","Do 21.11.2019 16:41",
                                settings=fbgui.Settings({
                                  'align': fbgui.LEFT}),
                                parent=self._header)
    self._templabel = fbgui.Label("temp","22.5°C",
                                settings=fbgui.Settings({
                                  'align': fbgui.RIGHT}),
                                parent=self._header)
    self._wdata   = fbgui.Text("wdata","""Wetterbericht für: München

               leichter Nebel
  _ - _ - _ -  3..4 °C        
   _ - _ - _   ← 6 km/h       
  _ - _ - _ -  4 km           
               0.1 mm""",
                                parent=self._vbox)

  # --- update time-string   -------------------------------------------

  def _update_time(self):
    delay = 60
    while True:
      now = datetime.datetime.now()
      try:
        self._dtlabel.set_text(now.strftime("%a %x %H:%M"))
      except:
        break
      time.sleep(delay)

  # --- update weather-data   ------------------------------------------

  def _update_wdata(self):
    delay = 120

    while True:
      try:
        response = requests.get(Display.WTTRIN_URL)
        if response.status_code == requests.codes.OK:
          response_data = response.text
          self._wdata.set_text(response_data)
        else:
          print("http-code: %d, reason: %s" %
                (response.status_code,response.reason))
      except Exception as ex:
        print("ERROR: %r" % ex)
      time.sleep(delay)

  def on_start(self):
    threading.Thread(target=self._update_time).start()
    threading.Thread(target=self._update_wdata).start()

if __name__ == '__main__':
  locale.setlocale(locale.LC_ALL, '')
  config               = fbgui.Settings()
  config.msg_level     = "DEBUG"
  config.font_size     = 40
  config.width         = 320
  config.height        = 240
  config.bg_color      = fbgui.Color.TRANSPARENT
  config.fg_color      = fbgui.Color.WHITE
  config.font_size     = 16
  config.font_name     = "DejaVuSansMono-Bold.ttf"
  config.title         = "wttr.in"
  config.imgpath       = os.path.join(
    os.path.dirname(sys.argv[0]),"../files/wolken.bmp")

  app   = Display(config)
  app.run()
