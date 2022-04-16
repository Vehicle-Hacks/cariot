#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep  5 07:17:09 2021

simple_car_connect
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

from awscrt import io
from awsiot import mqtt_connection_builder

from threading import Thread
import time
import json

import serial
from pynmeagps import NMEAReader
import pynmeagps.exceptions as nme

class gps_reader:
    def __init__(self):
        self.gps_running = False
        self.gps_available = False
        self.gps_config = ""
        self.lat = 0
        self.lon = 0
        self.alt = 0
        self.quality = 0

    def start(self,config):
        self.gps_running = True
        self.gps_config = config['gps']
        self.gps_thread = Thread(target=self.gps_loop)
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
                        self.lat = parsed_data.lat
                        self.lon = parsed_data.lon
                        self.alt = parsed_data.alt
                        self.quality = parsed_data.quality
                        self.gps_available = True
            except (
                nme.NMEAStreamError,
                nme.NMEAMessageError,
                nme.NMEATypeError,
                nme.NMEAParseError,
            ) as err:
                print(f"Something went wrong {err}")
                continue
    


class aws_iot:
    def __init__(self):
        self.aws_running = False
        self.thing_config = ""

    def start(self, config):
        self.aws_running = True
        self.thing_config = config['thing']
        self.aws_thread = Thread(target=self.aws_loop) 
        self.aws_thread.start()

    def stop(self):
        self.aws_running = False
        self.aws_thread.join(5)        

    def aws_loop(self):
        event_loop_group = io.EventLoopGroup(1)
        host_resolver = io.DefaultHostResolver(event_loop_group)
        client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)

        aws_iot_connection = mqtt_connection_builder.mtls_from_path(
            endpoint = self.thing_config['endpoint'],
            client_id = self.thing_config['clientId'],
            client_bootstrap = client_bootstrap,
            cert_filepath = self.thing_config['certfile'],
            pri_key_filepath = self.thing_config['keyfile'],
            ca_filepath = self.thing_config['rootCaFile'],
            clean_session = False
        )

        aws_iot_connect_future = aws_iot_connection.connect()
        aws_iot_connect_future.result()
        print("Connected")

        while (self.aws_running == True):
            print("A")
            time.sleep(1)

        aws_iot_disconnect_future = aws_iot_connection.disconnect()
        aws_iot_disconnect_future.result()
        print("Disconnected!")                    


config_file = open('./cariot-config.json')
cariot_config = json.load(config_file)

aws = aws_iot()
aws.start(cariot_config)

gps = gps_reader()
gps.start(cariot_config)

print("running")
time.sleep(10)
print("Stopping thread")

aws.stop()
gps.stop()