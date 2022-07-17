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

class obd_reader():
    def __init__(self):
        self.obd_running = True
        self.obd_available = False
        self.obd_data = {
            # Set everything to -1 so in the backend it's clear that we received "empty" data
            "voltage": -1,
            "coolant": -1,
            "oil": -1,
            "load": -1,
            "intake": -1,
            "throttle": -1,
            "rpm": -1,
            "fuelrate": -1,
            "ecuVoltage": -1,
            "obdAlive": -1,
            "obdStatus": -1
        }
        self.lock = threading.Lock()
        self.obd_thread = ''
        self.obd_status =  obd.OBDStatus.NOT_CONNECTED
        self.gui_update_fcn = ''

    def start(self,config):
        self.obd_running = True
        self.obd_config = config['obd']
        self.obd_thread = threading.Thread(target=self.obd_loop)
        self.obd_thread.start()

    def stop(self):
        self.obd_running = False
        if self.obd_thread:
            self.obd_thread.join(5)        

    def obd_loop(self):
        connecting = True
        aliveCounter = 0

        while connecting:
            obdConnection = obd.OBD()
            self.obdStatus = obdConnection.status()

            if self.obdStatus == obd.OBDStatus.NOT_CONNECTED:
                print('OBD: no connection')
                self.obd_data['obdStatus'] = 0
                time.sleep(1)
            if self.obdStatus == obd.OBDStatus.ELM_CONNECTED:
                print('OBD: ELM connected')
                self.obd_data['obdStatus'] = 1
                time.sleep(1)
            if self.obdStatus == obd.OBDStatus.OBD_CONNECTED:
                print('OBD: port detected')
                self.obd_data['obdStatus'] = 2
                time.sleep(1)
            if self.obdStatus == obd.OBDStatus.CAR_CONNECTED:
                print('OBD: connected')
                self.obd_data['obdStatus'] = 3
                connecting = False
            if not self.obd_running:
                connecting = False
            if self.gui_update_fcn:
                self.gui_update_fcn()

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
            try:
                if obdCoolantAvailable:
                    cmd = obd.commands.COOLANT_TEMP
                    response = obdConnection.query(cmd)
                    self.lock.acquire()
                    if not response.is_null():
                        self.obd_data['coolant'] = response.value.magnitude
                    else:
                        self.obd_data['coolant'] = -2
                    self.lock.release()
                
                if obdVoltageAvailable:
                    cmd = obd.commands.ELM_VOLTAGE
                    response = obdConnection.query(cmd)
                    self.lock.acquire()
                    if not response.is_null():
                        self.obd_data['voltage'] = response.value.magnitude
                    else:
                        self.obd_data['voltage'] = -2
                    self.lock.release()


                if obdOilAvailable:
                    cmd = obd.commands.OIL_TEMP
                    response = obdConnection.query(cmd)
                    self.lock.acquire()
                    if not response.is_null():
                        self.obd_data['oil'] = response.value
                    else:
                        self.obd_data['oil'] = -2
                    self.lock.release()

                if obdLoadAvailable:
                    cmd = obd.commands.ENGINE_LOAD
                    response = obdConnection.query(cmd)
                    self.lock.acquire()
                    if not response.is_null():
                        self.obd_data['load'] = response.value.magnitude
                    else:
                        self.obd_data['load'] = -2
                    self.lock.release()
                
                if obdIntakeAvailable:
                    cmd = obd.commands.INTAKE_TEMP
                    response = obdConnection.query(cmd)
                    self.lock.acquire()
                    if not response.is_null():
                        self.obd_data['intake'] = response.value.magnitude
                    else:
                        self.obd_data['intake'] = -2
                    self.lock.release()
                    
                if obdRpmAvailable:
                    cmd = obd.commands.RPM
                    response = obdConnection.query(cmd)
                    self.lock.acquire()
                    if not response.is_null():
                        self.obd_data['rpm'] = response.value.magnitude
                    else:
                        self.obd_data['rpm'] = -2
                    self.lock.release()
                    
                if obdThrottleAvailable:
                    cmd = obd.commands.THROTTLE_POS
                    response = obdConnection.query(cmd)
                    self.lock.acquire()
                    if not response.is_null():
                        self.obd_data['throttle'] = response.value.magnitude
                    else:
                        self.obd_data['throttle'] = -2
                    self.lock.release()
                    
                if obdFuelRateAvailable:
                    cmd = obd.commands.FUEL_RATE
                    response = obdConnection.query(cmd)
                    self.lock.acquire()
                    if not response.is_null():
                        self.obd_data['fuelrate'] = response.value.magnitude
                    else:
                        self.obd_data['fuelrate'] = -2
                    self.lock.release()
                    
                if obdEcuVoltageAvailable:
                    cmd = obd.commands.CONTROL_MODULE_VOLTAGE
                    response = obdConnection.query(cmd)
                    self.lock.acquire()
                    if not response.is_null():
                        self.obd_data['ecuVoltage'] = response.value.magnitude
                    else:
                        self.obd_data['ecuVoltage'] = -2
                    self.lock.release()
            except:
                self.obd_data['obdStatus'] = -3

                
            obdAvailable = True
            aliveCounter += 1
            self.lock.acquire()
            self.obd_data['obdAlive'] = aliveCounter
            self.lock.release()
            if self.gui_update_fcn:
                self.gui_update_fcn()

    def get_data(self):
        return self.obd_data