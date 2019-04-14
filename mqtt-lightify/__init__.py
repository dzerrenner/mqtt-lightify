import paho.mqtt.client as mqtt
import json
import logging
from datetime import datetime
import lightify

MSG_CONNECTION_STATUS_OUT_OF_BOUNDS = "connect status has to be either 0, 1 or 2."
MSG_DEVICE_NOT_FOUND = "device %s not in device list."
MSG_COLOR_FORMAT_WRONG = "color format should be html-rgb #RRGGBB"

class LightifyEncoder(json.JSONEncoder):
    """Enables objects from the lightify library to be encoded as JSON."""
    def default(self, obj):
        if isinstance(obj, lightify.Light):
            response = {}
            for key in (
                "name", "addr", "idx", "reachable", "last_seen", 
                "on", "lum", "temp", "min_temp", "max_temp",
                "red", "green", "blue", "groups", 
                "type_id", "devicename",
                "version", "deleted",
            ):
                response[key] = getattr(obj, key, None)()  
            response.update({
                "deviceType": obj.devicetype().name,
                "deviceTypeValue": obj.devicetype().value,
                "deviceSubType": obj.devicesubtype().name,
                "deviceSubTypeValue": obj.devicesubtype().value,  
                "supported_features": list(obj.supported_features()),
            }) 
            return response
        elif isinstance(obj, lightify.Group):
            response = {}
            for key in (
                "name", "idx", "lights", "reachable", "light_names", 
                "on", "lum", "temp", "min_temp", "max_temp",
                "red", "green", "blue", "deleted",
            ):
                response[key] = getattr(obj, key, None)()  
            response.update({
                "supported_features": list(obj.supported_features()),

            })
            return response

        elif isinstance(obj, lightify.Scene):
            response = {}
            for key in (
                "name", "idx", "group", "deleted",
            ):
                response[key] = getattr(obj, key, None)()  
            return response

        return json.JSONEncoder.default(self, obj)

class MqttLightify(object):
    def __init__(self, broker_address="127.0.0.1", bridge_address="127.0.0.1", toplevel_topic="lightify", mqtt_client_name="mqtt-lightify"):
        self.toplevel_topic = toplevel_topic
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info(f"Starting mqtt-lightify-bridge on topic {self.toplevel_topic}")
        self.logger.info(f"MQTT-broker address: {broker_address}, Lightify-bridge address: {bridge_address}")
        self.bridge_address = bridge_address

        self._connect_status = 0
        self.mqtt_client = mqtt.Client(mqtt_client_name)
        self.mqtt_client.enable_logger()
        self.mqtt_client.will_set(f"{self.toplevel_topic}/connected", 0)
        self.mqtt_client.on_connect = self._on_connect
        self.mqtt_client.on_message = self._on_message
        self.mqtt_client.connect(broker_address)
        self.lightify_bridge = None 

        self._is_running = False

    def publish(self, subtopic, payload=None, qos=0, retain=False):
        topic = f"{self.toplevel_topic}/{subtopic}"
        self.logger.debug(f"PUB {topic}: {payload}")
        info = self.mqtt_client.publish(topic, payload=payload, qos=qos, retain=retain)
        self.logger.debug(f"PUB result: {info}")

    @property
    def is_running(self):
        return self._is_running

    @property
    def connect_status(self):
        return self._connect_status

    @connect_status.setter
    def connect_status(self, value):
        if value < 0 or value > 2:
            self.logger.error(MSG_CONNECTION_STATUS_OUT_OF_BOUNDS)
            raise ValueError(MSG_CONNECTION_STATUS_OUT_OF_BOUNDS) 
        self._connect_status = value
        self.publish("connected", payload=self._connect_status)
        
    def _on_connect(self, client, userdata, flags, rc):
        self.mqtt_client.subscribe(f"{self.toplevel_topic}/#")
        self.connect_status = 1
        self.lightify_bridge = lightify.Lightify(self.bridge_address)
        self.lightify_bridge.update_all_light_status()
        self.connect_status = 2
        self.mqtt_client.message_callback_add(f"{self.toplevel_topic}/set/#", self._on_set_message)
        self.mqtt_client.message_callback_add(f"{self.toplevel_topic}/get/#", self._on_get_message)
        self.mqtt_client.message_callback_add(f"{self.toplevel_topic}/command/#", self._on_command_message)

        self.logger.info("available devices:")
        lights = self.lightify_bridge.lights()
        for light in lights.keys():
            self.logger.info(f"{light} -> {lights[light]}")
        
        self.logger.info("available groups:")
        groups = self.lightify_bridge.groups()
        for group in groups.keys():
            self.logger.info(f"{group} -> {groups[group]}")
        
        self.logger.info("available scenes:")
        scenes = self.lightify_bridge.scenes()
        for scene in scenes.keys():
            self.logger.info(f"{scene} -> {scenes[scene]}")

        for light in lights.keys():
            self.publish(f"get/{light}")

    def _on_command_info(self, param):
        self.logger.debug(f"INFO ({param})")
        bridge_method = getattr(self.lightify_bridge, param)
        response = bridge_method()
        self.logger.debug(f"got response from bridge: {response}")
        return json.dumps(response, cls=LightifyEncoder)

    def _on_message(self, client, userdata, msg):
        self.logger.debug(f"RCV from {client}:{msg.topic}")
        self.logger.debug(f"RCV {msg.payload}")

    def _on_command_message(self, client, userdata, msg):
        # handle messages on the /command/# channel
        self.logger.debug(f"RCV COMMAND from {client}:{msg.topic}")
        self.logger.debug(f"RCV {msg.payload}") 
        payload = json.loads(msg.payload.decode("utf-8"))
        self.logger.debug(f"RCV payload {payload}")
        command = payload["command"]
        self.logger.debug(f"RCV command {command}")
        param = payload["param"]
        self.logger.debug(f"RCV param {param}")
        
        method_name = f"_on_command_{command}"   
        response = getattr(self, method_name)(param)
        self.logger.debug(f"got response from command: {response}")
        self.publish(command, payload=response)

    def _on_get_message(self, client, userdate, msg):
        # handle messages on the /get/# channel
        self.logger.debug(f"RCV GET from {client}:{msg.topic}, ignoring datapoint and message payload")
        _, _, device = msg.topic.split("/")

        # re-read values from bridge
        self.lightify_bridge.update_all_light_status()
        
        # device key is an int!
        device = int(device)

        l = self.lightify_bridge.lights()[device]

        # not used at the moment: "rgb", "raw_values", "groups", "supported_features", 
        # also not used but included in payload: "devicesubtype", "devicetype", 
        for key in (
            "name", "reachable", "last_seen", 
            "on", "lum", "temp", "min_temp", "max_temp",
            "red", "green", "blue", 
            "type_id", "devicename",
            "version", "deleted",
        ):
            datapoint = key.upper()
            payload = json.dumps({
                "val": getattr(l, key, None)(),
                "ts": int(datetime.now().timestamp() * 1000),
                # "lc": 1553105197000,
                #       1553282307.637285
                "lightify": {
                    "bridge": self.bridge_address,
                    "device": device,
                    "deviceName": l.devicename(),
                    "deviceType": l.devicetype().name,
                    "deviceTypeValue": l.devicetype().value,
                    "deviceSubType": l.devicesubtype().name,
                    "deviceSubTypeValue": l.devicesubtype().value,
                    "addr": l.addr(), 
                    "idx": l.idx(),
                    "datapoint": datapoint,
                    "datapointType": "bla",
                }
                    # "ts": 1553281031286,
                    # "tsPrevious": 1553280738044,
                    # "lc": 1553105197000,
                    # "change": false,
                    # "cache": false
            })
            self.publish(f"status/{device}/{datapoint}", payload=payload)
            # self.logger.debug(payload)


    def _on_set_message(self, client, userdata, msg):
        # handle messages on the /set/# channel
        self.logger.debug(f"RCV SET from {client}:{msg.topic}")
        self.logger.debug(f"RCV {msg.payload}") 
        _, _, device, datapoint = msg.topic.split("/")

        val = msg.payload.decode("utf-8", errors="ignore")
        
        # device key is an int!
        device = int(device)

        self.logger.debug(f"RCV device: {device}, datapoint: {datapoint}, value: {val}")     
        bridge_device = self.lightify_bridge.lights()[device] 

        if datapoint.upper() == "STATE":
            if "on" not in bridge_device.supported_features():
                self.logger.warning(f"device {device} does not support switching.")
            # val ist expected to contin a thruth-like value
            val = (val == "true") or (val == "1")
            try:
                bridge_device.set_onoff(val)
            except KeyError:
                self.logger.error(MSG_DEVICE_NOT_FOUND % device)
        elif datapoint.upper() == "RGB":
            if "rgb" not in bridge_device.supported_features():
                self.logger.warning(f"device {device} does not support rgb values.")
            # val is expected to be an html-hex-rgb-value (#RRGGBB)
            if val.startswith("#"): 
                val = val[1:]
            if len(val) != 6:
                self.logger.error(MSG_COLOR_FORMAT_WRONG)
            else:
                red = int(val[0:2],16)
                green = int(val[2:4],16)
                blue = int(val[4:6],16)
                bridge_device.set_rgb(red, green, blue, 0)
        elif datapoint.upper() == "LUM":
            if "lum" not in bridge_device.supported_features():
                self.logger.warning(f"device {device} does not support luminance.")
            # val is expected to be a value between 0 and 100
            lum = int(val)
            if lum < 0: 
                lum = 0
            if lum > 100:
                lum = 100
            bridge_device.set_luminance(lum, 0)
        elif datapoint.upper() == "TEMP":
            if "temp" not in bridge_device.supported_features():
                self.logger.warning(f"device {device} does not support light temperature.")
            # val is expected to be a value between min_temp and max_temp for the current device
            min_temp = bridge_device.min_temp()
            max_temp = bridge_device.max_temp()
            self.logger.debug(f"temperature range: {min_temp} - {max_temp}")
            temp = int(val)
            if temp < min_temp:
                self.logger.warning(f"temperature {temp} smaller than min_temp {min_temp}, setting to {min_temp}.")
                temp = min_temp
            if temp > max_temp:
                self.logger.warning(f"temperature {temp} greater than max_temp {max_temp}, setting to {max_temp}.")
                temp = max_temp
            bridge_device.set_temperature(temp, 0)

        # update status
        self.publish(f"get/{device}")

    def start(self, loop_forever=False):
        if loop_forever:
            try:
                self.logger.debug(f"starting event loop (forever).")
                self._is_running = True
                self.mqtt_client.loop_forever()
            except KeyboardInterrupt:
                self._is_running = False
                self.logger.debug(f"received keyboard interrupt, trying to shut down gracefully.")
                self.mqtt_client.disconnect()
        else:
            self.logger.debug(f"starting event loop.")
            self._is_running = True
            self.mqtt_client.loop_start()

    def stop(self):
        self.logger.debug(f"stopping event loop.")
        self._is_running = False
        self.mqtt_client.loop_stop()
