#!/bin/sh
python3 pubsub.py --endpoint XXX-ats.iot.eu-central-1.amazonaws.com --root-ca AmazonRootCA1.pem --cert YYY-certificate.pem.crt --key YYY-private.pem.key --topic cars/01 --count=0