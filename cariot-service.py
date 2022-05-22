#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep  5 07:17:09 2021

cariot-service.py
Copyright (C) 2021 Ralph Grewe
  
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import kivy


import threading
import time

import cariot.gui

from kivy.app import App
from kivy.config import Config

class CariotApp(App):
    def build(self):
        self.gui = cariot.gui.CariotMain()
        return self.gui

    def on_stop(self):
        self.gui.stop()


if __name__ == '__main__':
    print("Starting App")
    Config.set('graphics','width',480)
    Config.set('graphics','height',320)
    CariotApp().run()
    print("Stopping App")