# Main entry point for executing with python -m mqtt-lightify

import logging
from . import MqttLightify

try:
    import coloredlogs
    coloredlogs.install(
        level="DEBUG",
        milliseconds=True,
        fmt="%(asctime)s %(levelname)-8s %(name)-16s %(message)s",
        field_styles={
            'asctime': {'color': 'blue'},
            'msecs': {'color': 'blue'},
            'name': {'color': 'magenta'},
            'levelname': {'color': 'white', 'faint': True}
        }
    )
except ModuleNotFoundError:
    logging.basicConfig(format='%(asctime)-15s %(levelname)-8s %(name)-16s %(message)s', level=logging.DEBUG)

import argparse
parser = argparse.ArgumentParser("mqtt-lightify")
parser.add_argument("--broker", default=None, help="mqtt broker address")
parser.add_argument("--bridge", default=None, help="lightify bridge address")
parser.add_argument("--user", default=None, help="mqtt user name")
parser.add_argument("--password", default=None, help="mqtt user password")

args = parser.parse_args()

import os
import base64
if not args.broker:    
    BROKER_ADDRESS = os.environ.get("BROKER_ADDRESS", "127.0.0.1")
else:
    BROKER_ADDRESS = args.broker
if not args.bridge:
    BRIDGE_ADDRESS = os.environ.get("BRIDGE_ADDRESS", "127.0.0.1")
else:
    BRIDGE_ADDRESS = args.bridge
if not args.user:
    BROKER_USER = os.environ.get("BROKER_USER")
else:
    BROKER_USER = args.user
if not args.password:
    BROKER_PASSWD = base64.b64decode(os.environ.get("BROKER_PASSWD"))
else:
    BROKER_PASSWD = args.password

bridge = MqttLightify(broker_address=BROKER_ADDRESS, bridge_address=BRIDGE_ADDRESS, username=BROKER_USER, passwd=BROKER_PASSWD)
bridge.start(loop_forever=True)