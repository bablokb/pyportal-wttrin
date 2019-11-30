Geek-Weather with pygame-fbgui and wettr.in
===========================================

Overview
--------

This is an alternative implementation for a Pi with a small framebuffer-display.
It uses the library [pygame-fbgui](https://github.com/bablokb/pygame-fbgui).

It lacks some features from the PyPortal-based implementation, but these
could easily be added (e.g. reading a temperature-sensor).

Current shortcomings:

  - no support for local temperature-sensor (value shown in first line is
    a constant)
  - closing the window does not stop the background threads
    (this is a todo and easily fixed)

