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

import obd
import threading
import time

from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label

class obd_reader(GridLayout):
    def __init__(self,**kwargs):
        super(obd_reader,self).__init__(**kwargs)
        self.cols = 4
        self.rows = 3

        self.gui_status = Label(text='OBD Offline')
        self.gui_status.color = (1,0,0)
        self.add_widget(self.gui_status)
        self.gui_protocol = Label(text='None')
        self.add_widget(self.gui_protocol)
        self.gui_voltage = Label(text='- V')
        self.add_widget(self.gui_voltage)
        self.gui_spacer1 = Label(text='reserved')
        self.add_widget(self.gui_spacer1)
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
        self.gui_fuelrate = Label(text='Fuel Rate:')
        self.add_widget(self.gui_fuelrate)

        self.obd_running = True
        self.obd_available = False
        self.obd_data = {
            "voltage": 0,
            "coolant": 0,
            "oil": 0,
            "load": 0,
            "intake": 0,
            "throttle": 0,
            "rpm": 0,
            "fuelrate": 0,
            "ecuVoltage": 0
        }
        self.lock = threading.Lock()

    def start(self,config):
        self.obd_running = True
        self.obd_config = config['obd']
        self.obd_thread = threading.Thread(target=self.obd_loop)
        self.obd_thread.start()

    def stop(self):
        self.obd_running = False
        self.obd_thread.join(5)        

    def obd_loop(self):
        connecting = True
        while connecting:
            obdConnection = obd.OBD()
            obdStatus = obdConnection.status()

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
                connecting = False

        print("OBD connected")
        obdCoolantAvailable = obdConnection.supports(obd.commands.COOLANT_TEMP)
        obdVoltageAvailable = obdConnection.supports(obd.commands.ELM_VOLTAGE)
        obdOilAvailable = obdConnection.supports(obd.commands.OIL_TEMP)
        obdLoadAvailable = obdConnection.supports(obd.commands.ENGINE_LOAD)
        obdIntakeAvailable = obdConnection.supports(obd.commands.INTAKE_TEMP)
        obdRpmAvailable = obdConnection.supports(obd.commands.RPM)
        obdThrottleAvailable = obdConnection.supports(obd.commands.THROTTLE_POS)
        obdFuelRateAvailable = obdConnection.supports(obd.commands.FUEL_RATE)
        obdEcuVoltageAvailable = obdConnection.supports(obd.commands.CONTROL_MODULE_VOLTAGE)

        while self.obd_running:
            if obdCoolantAvailable:
                cmd = obd.commands.COOLANT_TEMP
                response = obdConnection.query(cmd)
                if not response.is_null():
                    self.gui_coolant.text = 'Water: ' + str(response.value.magnitude) + ' °C'

                    self.lock.acquire()
                    self.obd_data['coolant'] = response.value.magnitude
                    self.lock.release()
            
            if obdVoltageAvailable:
                cmd = obd.commands.ELM_VOLTAGE
                response = obdConnection.query(cmd)
                if not response.is_null():
                    self.gui_voltage.text = str(response.value.magnitude) + 'V'

                    self.lock.acquire()
                    self.obd_data['voltage'] = response.value.magnitude
                    self.lock.release()
            
            if obdOilAvailable:
                cmd = obd.commands.OIL_TEMP
                response = obdConnection.query(cmd)
                if not response.is_null():
                    self.gui_oil.text = 'Oil: ' + str(response.value) + ' °C'

                    self.lock.acquire()
                    self.obd_data['oil'] = response.value
                    self.lock.release()
            
            if obdLoadAvailable:
                cmd = obd.commands.ENGINE_LOAD
                response = obdConnection.query(cmd)
                if not response.is_null():
                    self.gui_load.text = 'Load: ' + str(response.value.magnitude) + '%'

                    self.lock.acquire()
                    self.obd_data['load'] = response.value.magnitude
                    self.lock.release()
            
            if obdIntakeAvailable:
                cmd = obd.commands.INTAKE_TEMP
                response = obdConnection.query(cmd)
                if not response.is_null():
                    self.gui_intake.text = 'Intake: ' + str(response.value.magnitude) + ' °C'

                    self.lock.acquire()
                    self.obd_data['intake'] = response.value.magnitude
                    self.lock.release()
                
            if obdRpmAvailable:
                response = obdConnection.query(obd.commands.RPM)
                if not response.is_null():
                    self.gui_rpm.text = str(response.value.magnitude) + ' rpm'
                
                    self.lock.acquire()
                    self.obd_data['rpm'] = response.value.magnitude
                    self.lock.release()
                
            if obdThrottleAvailable:
                response = obdConnection.query(obd.commands.THROTTLE_POS)
                if not response.is_null():
                    self.gui_throttle.text = 'Throttle: ' + str(response.value.magnitude) + ' %'

                    self.lock.acquire()
                    self.obd_data['throttle'] = response.value.magnitude
                    self.lock.release()
                
            if obdFuelRateAvailable:
                response = obdConnection.query(obd.commands.FUEL_RATE)
                if not response.is_null():
                    self.gui_fuelrate.text = 'Fuel Rate: ' + str(response.value.magnitude)

                    self.lock.acquire()
                    self.obd_data['fuelrate'] = response.value.magnitude
                    self.lock.release()
                
            if obdEcuVoltageAvailable:
                response = obdConnection.query(obd.commands.CONTROL_MODULE_VOLTAGE)
                
                if not response.is_null():
                    self.lock.acquire()
                    self.obd_data['ecuVoltage'] = response.value.magnitude
                    self.lock.release()
            
            obdAvailable = True
            time.sleep(0.5)

    def get_data(self):
        return self.obd_data