#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mai 22 20:55:00 2022

cariot_cmdline.py
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

import json
import time

import cariot.aws
import cariot.gps
import cariot.obd

if __name__ == '__main__':
    config_file = open('./cariot-config.json')
    cariot_config = json.load(config_file)

    gps = cariot.gps.gps_reader()
    gps.start(cariot_config)

    obd = cariot.obd.obd_reader()

    aws = cariot.aws.aws_iot()
    aws.start(cariot_config, gps, obd)

    time.sleep(100)

    gps.stop()
    obd.stop()
    aws.stop()