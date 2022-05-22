"""
Created on Wed Mai 4 17:14:09 2022

gps.py
Copyright (C) 2022 Ralph Grewe
  
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

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout

import json

import cariot.aws
import cariot.aws_gui
import cariot.gps
import cariot.gps_gui
import cariot.obd
import cariot.obd_gui

class CariotMain(BoxLayout):
    def __init__(self, **kwargs):
        super(CariotMain, self).__init__(**kwargs)
        self.orientation = 'vertical'

        config_file = open('./cariot-config.json')
        cariot_config = json.load(config_file)

        self.gps = cariot.gps.gps_reader()
        self.gps_gui = cariot.gps_gui.gps_gui(self.gps, size_hint=(1,.2))
        self.gps.start(cariot_config)

        self.obd = cariot.obd.obd_reader()
        self.obd_gui = cariot.obd_gui.obd_gui(self.obd, size_hint=(1,.6))
        self.obd.start(cariot_config)

        self.aws = cariot.aws.aws_iot()
        self.aws_gui = cariot.aws_gui.aws_gui(self.aws, size_hint=(1,.2))
        self.aws.start(cariot_config, self.gps, self.obd)
        
        self.add_widget(self.aws_gui)
        self.add_widget(self.gps_gui)
        self.add_widget(self.obd_gui)

    def stop(self):
        self.gps.stop()
        self.obd.stop()
        self.aws.stop()
