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

class obd_reader:
    def __init__(self):
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
        obdConnection = obd.OBD()
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
                self.lock.acquire()
                self.obd_data['coolant'] = response.value.magnitude
                self.lock.release()
            
            if obdVoltageAvailable:
                cmd = obd.commands.ELM_VOLTAGE
                response = obdConnection.query(cmd)
                self.lock.acquire()
                self.obd_data['voltage'] = response.value.magnitude
                self.lock.release()
            
            if obdOilAvailable:
                cmd = obd.commands.OIL_TEMP
                response = obdConnection.query(cmd)
                self.lock.acquire()
                self.obd_data['oil'] = response.value
                self.lock.release()
            
            if obdLoadAvailable:
                cmd = obd.commands.ENGINE_LOAD
                response = obdConnection.query(cmd)
                self.lock.acquire()
                self.obd_data['load'] = response.value.magnitude
                self.lock.release()
            
            if obdIntakeAvailable:
                cmd = obd.commands.INTAKE_TEMP
                response = obdConnection.query(cmd)
                self.lock.acquire()
                self.obd_data['intake'] = response.value.magnitude
                self.lock.release()
                
            if obdRpmAvailable:
                response = obdConnection.query(obd.commands.RPM)
                self.lock.acquire()
                self.obd_data['rpm'] = response.value.magnitude
                self.lock.release()
                
            if obdThrottleAvailable:
                response = obdConnection.query(obd.commands.THROTTLE_POS)
                self.lock.acquire()
                self.obd_data['throttle'] = response.value.magnitude
                self.lock.release()
                
            if obdFuelRateAvailable:
                response = obdConnection.query(obd.commands.FUEL_RATE)
                self.lock.acquire()
                self.obd_data['fuelrate'] = response.value.magnitude
                self.lock.release()
                
            if obdEcuVoltageAvailable:
                response = obdConnection.query(obd.commands.CONTROL_MODULE_VOLTAGE)
                self.lock.acquire()
                self.obd_data['ecuVoltage'] = response.value.magnitude
                self.lock.release()
            
            obdAvailable = True
            time.sleep(0.5)

    def get_data(self):
        return self.obd_data