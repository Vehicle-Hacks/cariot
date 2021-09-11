#   simple_car_connect
#   Copyright (C) 2021 Ralph Grewe
  
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.

#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.

#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.

# Based on the pubsub.py example from AWS IoT Device SDK v2 for Python
# https://github.com/aws/aws-iot-device-sdk-python-v2
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0.

import argparse
from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder
import sys
import threading
import time
from uuid import uuid4
import json
import random

import obd

from threading import Thread
from pynmeagps import NMEAReader
import pynmeagps.exceptions as nme
from serial import Serial

# This sample uses the Message Broker for AWS IoT to send and receive messages
# through an MQTT connection. On startup, the device connects to the server,
# subscribes to a topic, and begins publishing messages to that topic.
# The device should receive those same messages back from the message broker,
# since it is subscribed to that same topic.

parser = argparse.ArgumentParser(description="Send and receive messages through and MQTT connection.")
parser.add_argument('--endpoint', required=True, help="Your AWS IoT custom endpoint, not including a port. " +
                                                      "Ex: \"abcd123456wxyz-ats.iot.us-east-1.amazonaws.com\"")
parser.add_argument('--port', type=int, help="Specify port. AWS IoT supports 443 and 8883.")
parser.add_argument('--cert', help="File path to your client certificate, in PEM format.")
parser.add_argument('--key', help="File path to your private key, in PEM format.")
parser.add_argument('--root-ca', help="File path to root certificate authority, in PEM format. " +
                                      "Necessary if MQTT server uses a certificate that's not already in " +
                                      "your trust store.")
parser.add_argument('--client-id', default="test-" + str(uuid4()), help="Client ID for MQTT connection.")
parser.add_argument('--topic', default="test/topic", help="Topic to subscribe to, and publish messages to.")
parser.add_argument('--message', default="Hello World!", help="Message to publish. " +
                                                              "Specify empty string to publish nothing.")
parser.add_argument('--count', default=10, type=int, help="Number of messages to publish/receive before exiting. " +
                                                          "Specify 0 to run forever.")
parser.add_argument('--signing-region', default='us-east-1', help="If you specify --use-web-socket, this " +
    "is the region that will be used for computing the Sigv4 signature")
parser.add_argument('--proxy-host', help="Hostname of proxy to connect to.")
parser.add_argument('--proxy-port', type=int, default=8080, help="Port of proxy to connect to.")
parser.add_argument('--verbosity', choices=[x.name for x in io.LogLevel], default=io.LogLevel.NoLogs.name,
    help='Logging level')

# Using globals to simplify sample code
args = parser.parse_args()
print("2")
io.init_logging(getattr(io.LogLevel, args.verbosity), 'stderr')

received_count = 0
received_all_event = threading.Event()

# GPS Globals
gpsInterface = '/dev/ttyACM0'
gpsSpeed = 115200
gpsRunning = True
gpsAvailable = False
lat = 0;
lon = 0;
alt = 0;
quality = 0;

# GPS Thread
def gps_thread():
    global lat, lon, alt, quality, gpsRunning, gpsAvailable
    gpsStream = Serial(gpsInterface, gpsSpeed, timeout=3)
    nms = NMEAReader(gpsStream)
    print('GPS started')
    while gpsRunning:
        try:
            (raw_data, parsed_data) = nms.read()
            if parsed_data:
                if parsed_data.msgID == "GGA":
                    lat = parsed_data.lat
                    lon = parsed_data.lon
                    alt = parsed_data.alt
                    quality = parsed_data.quality
                    gpsAvailable = True
        except (
            nme.NMEAStreamError,
            nme.NMEAMessageError,
            nme.NMEATypeError,
            nme.NMEAParseError,
        ) as err:
            print(f"Something went wrong {err}")
            continue

# OBD Globals
obdRunning = True
obdAvailable = False
obdVoltage = 0
obdCoolant = 0
obdOil = 0
obdLoad = 0
obdThrottle = 0
obdIntake = 0
obdRpm = 0
obdFuelRate = 0
obdEcuVoltage = 0

# OBD Thread
def obd_thread():
    global obdRunning, obdAvailable, obdVoltage, obdCoolant, obdOil, obdLoad, obdIntake, obdRpm, obdThrottle, obdFuelRate, obdEcuVoltage
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
    while obdRunning:
        if obdCoolantAvailable:
            cmd = obd.commands.COOLANT_TEMP
            response = obdConnection.query(cmd)
            obdCoolant = response.value.magnitude
        
        if obdVoltageAvailable:
            cmd = obd.commands.ELM_VOLTAGE
            response = obdConnection.query(cmd)
            obdVoltage = response.value.magnitude
        
        if obdOilAvailable:
            cmd = obd.commands.OIL_TEMP
            response = obdConnection.query(cmd)
            obdOil = response.value
        
        if obdLoadAvailable:
            cmd = obd.commands.ENGINE_LOAD
            response = obdConnection.query(cmd)
            obdLoad = response.value.magnitude
        
        if obdIntakeAvailable:
            cmd = obd.commands.INTAKE_TEMP
            response = obdConnection.query(cmd)
            obdIntake = response.value.magnitude
            
        if obdRpmAvailable:
            response = obdConnection.query(obd.commands.RPM)
            obdRpm = response.value.magnitude
            
        if obdThrottleAvailable:
            response = obdConnection.query(obd.commands.THROTTLE_POS)
            obdThrottle = response.value.magnitude
            
        if obdFuelRateAvailable:
            response = obdConnection.query(obd.commands.FUEL_RATE)
            obdFuelRate = response.value.magnitude
            
        if obdEcuVoltageAvailable:
            response = obdConnection.query(obd.commands.CONTROL_MODULE_VOLTAGE)
            obdEcuVoltage = response.value.magnitude
        
        obdAvailable = True
        time.sleep(0.5)

# Callback when connection is accidentally lost.
def on_connection_interrupted(connection, error, **kwargs):
    print("Connection interrupted. error: {}".format(error))


# Callback when an interrupted connection is re-established.
def on_connection_resumed(connection, return_code, session_present, **kwargs):
    print("Connection resumed. return_code: {} session_present: {}".format(return_code, session_present))

    if return_code == mqtt.ConnectReturnCode.ACCEPTED and not session_present:
        print("Session did not persist. Resubscribing to existing topics...")
        resubscribe_future, _ = connection.resubscribe_existing_topics()

        # Cannot synchronously wait for resubscribe result because we're on the connection's event-loop thread,
        # evaluate result with a callback instead.
        resubscribe_future.add_done_callback(on_resubscribe_complete)


def on_resubscribe_complete(resubscribe_future):
        resubscribe_results = resubscribe_future.result()
        print("Resubscribe results: {}".format(resubscribe_results))

        for topic, qos in resubscribe_results['topics']:
            if qos is None:
                sys.exit("Server rejected resubscribe to topic: {}".format(topic))


# Callback when the subscribed topic receives a message
def on_message_received(topic, payload, dup, qos, retain, **kwargs):
    print("Received message from topic '{}': {}".format(topic, payload))
    global received_count
    received_count += 1
    if received_count == args.count:
        received_all_event.set()

if __name__ == '__main__':
    # Spin up resources
    print("Starting up")
    event_loop_group = io.EventLoopGroup(1)
    host_resolver = io.DefaultHostResolver(event_loop_group)
    client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)

    proxy_options = None
    if (args.proxy_host):
        proxy_options = http.HttpProxyOptions(host_name=args.proxy_host, port=args.proxy_port)

    mqtt_connection = mqtt_connection_builder.mtls_from_path(
        endpoint=args.endpoint,
        port=args.port,
        cert_filepath=args.cert,
        pri_key_filepath=args.key,
        client_bootstrap=client_bootstrap,
        ca_filepath=args.root_ca,
        on_connection_interrupted=on_connection_interrupted,
        on_connection_resumed=on_connection_resumed,
        client_id=args.client_id,
        clean_session=False,
        keep_alive_secs=30,
        http_proxy_options=proxy_options)

    print("Connecting to {} with client ID '{}'...".format(
        args.endpoint, args.client_id))

    connect_future = mqtt_connection.connect()

    # Future.result() waits until a result is available
    connect_future.result()
    print("Connected!")

    # Subscribe
    print("Subscribing to topic '{}'...".format(args.topic))
    subscribe_future, packet_id = mqtt_connection.subscribe(
        topic=args.topic,
        qos=mqtt.QoS.AT_LEAST_ONCE,
        callback=on_message_received)

    subscribe_result = subscribe_future.result()
    print("Subscribed with {}".format(str(subscribe_result['qos'])))
 
    print("Initializing GPS")
    gpsThread = Thread(target=gps_thread)
    gpsThread.start();
    
    while gpsAvailable == False:
        print(".")
        time.sleep(1)
    print("GPS ready")

    print("Initializing OBD")
    obdThread = Thread(target=obd_thread)
    obdThread.start()
    while obdAvailable == False:
        print(".")
        time.sleep(1)
    print("OBD ready")
    
    # Publish message to server desired number of times.
    # This step is skipped if message is blank.
    # This step loops forever if count was set to 0.
    if args.message:
        if args.count == 0:
            print ("Sending messages until program killed")
        else:
            print ("Sending {} message(s)".format(args.count))
            
        #Hack: Send init message to force right data types in amazon timestream
        message = {"latitude": 0.1,
                   "longitude": 0.1,
                   "altitude": 0.1,
                   "quality": 0,
                   "counter": -1,
                   "voltage": 0.1,
                   "coolant": 0,
                   "oil": 0.1,
                   "load": 0.1,
                   "intake": 0,
                   "throttle": 0.1,
                   "rpm": 0.1,
                   "fuelrate": 0.1,
                   "ecuVoltage": 0.1,
                   "ID":"JEEP"}
        print("Publishing initial message to topic '{}': {}".format(args.topic, message))
        message_json = json.dumps(message)
        mqtt_connection.publish(
            topic=args.topic,
            payload=message_json,
            qos=mqtt.QoS.AT_LEAST_ONCE)
        time.sleep(1)
            
        publish_count = 1
        while (publish_count <= args.count) or (args.count == 0):
            rndNumber = random.random()
            message = {"latitude": lat,
                       "longitude": lon,
                       "altitude": alt,
                       "quality": quality,
                       "counter": publish_count,
                       "voltage": obdVoltage,
                       "coolant": obdCoolant,
                       "oil": obdOil,
                       "load": obdLoad,
                       "intake": obdIntake,
                       "throttle": obdThrottle,
                       "rpm": obdRpm,
                       "fuelrate": obdFuelRate,
                       "ecuVoltage": obdEcuVoltage,
                       "ID":"JEEP"}
            print("Publishing message to topic '{}': {}".format(args.topic, message))
            message_json = json.dumps(message)
            mqtt_connection.publish(
                topic=args.topic,
                payload=message_json,
                qos=mqtt.QoS.AT_LEAST_ONCE)
            time.sleep(1)
            publish_count += 1

    # Wait for all messages to be received.
    # This waits forever if count was set to 0.
    if args.count != 0 and not received_all_event.is_set():
        print("Waiting for all messages to be received...")

    received_all_event.wait()
    print("{} message(s) received.".format(received_count))

    print("Stopping GPS...")
    gpsRunning = False
    gpsThread.join(5)
    # Disconnect
    print("Stopping OBD")
    obdRunning = False
    obdThread.join(5)
    print("Disconnecting...")
    disconnect_future = mqtt_connection.disconnect()
    disconnect_future.result()
    print("Disconnected!")