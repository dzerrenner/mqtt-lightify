import paho.mqtt.client as mqtt
from elasticsearch import Elasticsearch
from pprint import pprint
import json
from datetime import datetime

TOPIC_MAPPING = {
    "hm/status/HmIP-eTRV-2 000A18A9A3C01B:1/ACTUAL_TEMPERATURE": "Wohnzimmer Couch",
    "hm/status/HMIP-eTRV 000393C99BB735:1/ACTUAL_TEMPERATURE": "Wohnzimmer Schreibtisch",
    "hm/status/HMIP-eTRV 000393C99BB99E:1/ACTUAL_TEMPERATURE": "Küche",
    "hm/status/HMIP-eTRV 000393C99BB9C0:1/ACTUAL_TEMPERATURE": "Esszimmer",

    "hm/status/HMIP-PS 000218A995F0CB:3/STATE": "Stehlampe Fenster",
}

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    # print("Connection returned " + str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("hm/status/#")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    now = datetime.utcnow()
    index_suffix = now.strftime("%Y-%m-%d")
    json_message = json.loads(msg.payload)
    if msg.topic == "hm/status/HMIP-PS 000218A995F0CB:3/STATE":
        print(f"[{now}] {json_message['hm']['change']} ({type(json_message['hm']['change'])})")
    if msg.topic in TOPIC_MAPPING and json_message['hm']['change']:
        print(f"[{now}] {msg.topic} -> {json_message['val']}")
        es.index(index=f"hm-{index_suffix}", doc_type="string", body={"room": TOPIC_MAPPING[msg.topic], "topic" : msg.topic, "data" : msg.payload, "timestamp": now})

es = Elasticsearch(hosts=["192.168.178.30:9200", ])

mqtt_client = mqtt.Client("mqtt-mongo-status")
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

mqtt_client.connect("192.168.178.30")


# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
mqtt_client.loop_forever()

# import time
# from datetime import datetime
# while True:
#     print(f"[{datetime.now()}] Hello world")
#     time.sleep(5)