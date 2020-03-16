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
parser.add_argument("--b64password", default=None, help="b64 encoded mqtt user password")
parser.add_argument("--transition_lum", default=None, help="transition time in 1/10s for luminance changes")
parser.add_argument("--transition_temp", default=None, help="transition time in 1/10s for color temperature changes")
parser.add_argument("--transition_rgb", default=None, help="transition time in 1/10s for RGB color changes")

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
if not args.password and not args.b64password:
    BROKER_PASSWD = os.environ.get("BROKER_PASSWD")
    if BROKER_PASSWD:
        BROKER_PASSWD = base64.b64decode(BROKER_PASSWD)
elif args.password:
    BROKER_PASSWD = args.password
elif args.b64password:
    BROKER_PASSWD = base64.b64decode(args.b64password)

bridge = MqttLightify(broker_address=BROKER_ADDRESS, bridge_address=BRIDGE_ADDRESS, username=BROKER_USER, passwd=BROKER_PASSWD,
                      trans_lum=args.transition_lum, trans_temp=args.transition_temp, trans_rgb=args.transition_rgb)
bridge.start(loop_forever=True)