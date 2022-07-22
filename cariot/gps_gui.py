"""
Created on Sun Mai 22 20:33:00 2022

gps_gui.py
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

import cariot.gps

from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label

class gps_gui(GridLayout):
    def __init__(self, gps_reader,  **kwargs):
        super(gps_gui, self).__init__(**kwargs)
        self.cols = 3
        self.gui_status = Label(text='GPS Offline')
        self.gui_status.color = (1,0,0)
        self.add_widget(self.gui_status)
        self.gui_lat = Label(text='Lat: no data')
        self.add_widget(self.gui_lat)
        self.gui_lon = Label(text='Lon: no data')
        self.add_widget(self.gui_lon)

        self.gps = gps_reader
        self.gps.gui_update_fcn = self.update

    def update(self):
        if self.gps.gps_connected:
            self.gui_status.text = 'GPS connected'
            self.gui_status.color = (0,1,0)

        self.gui_lat.text = "Lat:" + str(self.gps.gps_data['latitude'])
        self.gui_lon.text = "Lon:" + str(self.gps.gps_data['longitude'])
