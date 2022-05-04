"""
Created on Wed Mai 4 07:26:09 2022

aws.py
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

from awscrt import io
from awsiot import mqtt_connection_builder
import threading
import time

class aws_iot:
    def __init__(self):
        self.aws_running = False
        self.thing_config = ""
        self.lock = threading.Lock()

    def start(self, config):
        self.aws_running = True
        self.thing_config = config['thing']
        self.aws_thread = threading.Thread(target=self.aws_loop) 
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
