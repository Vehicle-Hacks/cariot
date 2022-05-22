"""
Created on Sun Mai 22 20:56:00 2022

obd_gui.py
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

from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label

class obd_gui(GridLayout):
    def __init__(self,**kwargs):
        super(obd_gui,self).__init__(**kwargs)
        self.cols = 4
        self.rows = 3

        self.gui_status = Label(text='OBD Offline')
        self.gui_status.color = (1,0,0)
        self.add_widget(self.gui_status)
        self.gui_protocol = Label(text='None')
        self.add_widget(self.gui_protocol)
        self.gui_voltage = Label(text='- V')
        self.add_widget(self.gui_voltage)
        self.gui_alive = Label(text='-')
        self.add_widget(self.gui_alive)
        self.gui_coolant = Label(text='Water: - °C')
        self.add_widget(self.gui_coolant)
        self.gui_oil = Label(text='Oil: - °C')
        self.add_widget(self.gui_oil)
        self.gui_intake = Label(text='Intake: - °C')
        self.add_widget(self.gui_intake)
        self.gui_spacer2 = Label(text='Reserved')
        self.add_widget(self.gui_spacer2)
        self.gui_rpm = Label(text='- rpm')
        self.add_widget(self.gui_rpm)
        self.gui_throttle = Label(text='Throttle: - %')
        self.add_widget(self.gui_throttle)
        self.gui_load = Label(text='Load - %')
        self.add_widget(self.gui_load)
        self.gui_fuelrate = Label(text='Fuel:')
        self.add_widget(self.gui_fuelrate)

    def status(self):
        if obdStatus == obd.OBDStatus.NOT_CONNECTED:
            self.gui_status.text = 'Connection Error'
            self.gui_status.color = (1,0,0)
        if obdStatus == obd.OBDStatus.ELM_CONNECTED:
            self.gui_status.text = 'ELM327 detected'
            self.gui_status.color = (0.5,0.5,0)
        if obdStatus == obd.OBDStatus.OBD_CONNECTED:
            self.gui_status.text = 'OBD port detected'
            self.gui_status.color = (1,1,0)
        if obdStatus == obd.OBDStatus.CAR_CONNECTED:
            self.gui_status.text = 'OBD connected'
            self.gui_status.color = (0,1,0)

    def update(self):
        self.gui_coolant.text = 'Water: ' + str(response.value.magnitude) + ' °C'
        self.gui_voltage.text = str(response.value.magnitude) + 'V'
        self.gui_oil.text = 'Oil: ' + str(response.value) + ' °C'
        self.gui_load.text = 'Load: ' + str(response.value.magnitude) + '%'
        self.gui_intake.text = 'Intake: ' + str(response.value.magnitude) + ' °C'
        self.gui_rpm.text = str(response.value.magnitude) + ' rpm'
        self.gui_throttle.text = 'Throttle: ' + str(response.value.magnitude) + ' %'
        self.gui_fuelrate.text = 'Fuel Rate: ' + str(response.value.magnitude)