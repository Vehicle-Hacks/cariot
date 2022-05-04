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

import threading
import time
import json

import serial
from pynmeagps import NMEAReader
import pynmeagps.exceptions as nme

import cariot.aws

class gps_reader:
    def __init__(self):
        self.gps_running = False
        self.gps_available = False
        self.gps_config = ""
        self.lat = 0
        self.lon = 0
        self.alt = 0
        self.quality = 0
        self.lock = threading.Lock()

    def start(self,config):
        self.gps_running = True
        self.gps_config = config['gps']
        self.gps_thread = threading.Thread(target=self.gps_loop)
        self.gps_thread.start()

    def stop(self):
        self.gps_running = False
        self.gps_thread.join(5)

    def gps_loop(self):
        try:
            gpsStream = serial.Serial(self.gps_config['interface'], self.gps_config['baudrate'], timeout=3)
        except ( 
            serial.serialutil.SerialException 
        ) as err:
            print(f"Error connecting to GPS {err}")
            return

        nms = NMEAReader(gpsStream)
        print('GPS started')

        while self.gps_running:
            try:
                (raw_data, parsed_data) = nms.read()
                if parsed_data:
                    if parsed_data.msgID == "GGA":
                        self.lock.acquire()
                        self.lat = parsed_data.lat
                        self.lon = parsed_data.lon
                        self.alt = parsed_data.alt
                        self.quality = parsed_data.quality
                        self.gps_available = True
                        self.lock.release()
            except (
                nme.NMEAStreamError,
                nme.NMEAMessageError,
                nme.NMEATypeError,
                nme.NMEAParseError,
            ) as err:
                print(f"Something went wrong {err}")
                continue

config_file = open('./cariot-config.json')
cariot_config = json.load(config_file)

aws = cariot.aws.aws_iot()
aws.start(cariot_config)

gps = gps_reader()
gps.start(cariot_config)

print("running")
time.sleep(10)
print("Stopping thread")

aws.stop()
gps.stop()