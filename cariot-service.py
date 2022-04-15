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

import threading
import time
import json

config_file = open('./cariot-config.json')
cariot_config = json.load(config_file)

# We should
event_loop_group = io.EventLoopGroup(1)
host_resolver = io.DefaultHostResolver(event_loop_group)
client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)

aws_iot_connection = mqtt_connection_builder.mtls_from_path(
    endpoint = cariot_config['thing']['endpoint'],
    client_id = cariot_config['thing']['clientId'],
    client_bootstrap = client_bootstrap,
    cert_filepath = cariot_config['thing']['certfile'],
    pri_key_filepath = cariot_config['thing']['keyfile'],
    ca_filepath = cariot_config['thing']['rootCaFile'],
    clean_session = False
)

aws_iot_connect_future = aws_iot_connection.connect()
aws_iot_connect_future.result()
print("Connected")

aws_iot_disconnect_future = aws_iot_connection.disconnect()
aws_iot_disconnect_future.result()
print("Disconnected!")