# cariot
Connect your Car to IoT

# Using the script to upload OBD/NMEA-Data to AWS IoT Core / Amazon Timestream
The script in this repository can be used to upload OBD data using an ELM327-compatible OBD interface and GPS data using NMEA to AWS IoT Core. Using the script and configuring AWS to store the data in Amazon Timestream is described [here](https://vehicle-hacks.com/2021/10/22/connect-your-car-to-iot-using-raspberry-pi-and-aws/).

# Configuring the script as a service on a Raspberry PI using read only file system
Having the script started automatically on a raspberry pi which also can be switched off without powering down is advantageous e.g. when you just want to use it headless powered by a cigarette lighter in the vehicle. How to configure the Raspberry PI that way is described [here](https://vehicle-hacks.com/2021/12/01/running-the-aws-iot-script-as-service-quick-and-dirty/)
