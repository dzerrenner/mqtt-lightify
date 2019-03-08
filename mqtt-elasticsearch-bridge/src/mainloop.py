# import paho.mqtt.client as mqtt
# from pprint import pprint
# import json




# The callback for when the client receives a CONNACK response from the server.
# def on_connect(client, userdata, flags, rc):
#     print("Connection returned " + str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
#     client.subscribe("hm/#")

# The callback for when a PUBLISH message is received from the server.
# def on_message(client, userdata, msg):
#     print(msg.topic)  # +" "+str(msg.payload))
#     json_message = json.loads(msg.payload)
#     pprint(json_message)
#     mongo_collection.insert_one(json_message)


# mqtt_client = mqtt.Client("mqtt-mongo-status")
# mqtt_client.on_connect = on_connect
# mqtt_client.on_message = on_message

# mqtt_client.connect("192.168.178.30")


# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
# mqtt_client.loop_forever()

import time
from datetime import datetime
while True:
    print(f"[{datetime.now()}] Hello world")
    time.sleep(5)