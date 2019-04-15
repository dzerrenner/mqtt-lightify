# MQTT-Lightify

## Installation

Clone the git repository, optionally run tests with `setup.py test`, and run `setup.py install`.

## Invocation

To run the bridge with default settings (both mqtt-broker and lightify access bridge on `localhost`), just run

    python -m mqtt-lightify

Since the bridge is usually not located on localhost and the broker could run on any host in your network, there are two command line parameters to set them:

    python -m mqtt-lightify --broker=127.0.0.1 --bridge=192.168.x.x

If you need to use a non standard port for your broker, use the following syntax: `--broker=127.0.0.1:1883`. The port for the Lightify bridge is fixed to 4000.

For simplified use in isolated environments, you can also provide these using the environment variables `BROKER_ADDRESS` and `BRIDGE_ADDRESS` respectively.

## Docker

This package can easily deployed as a docker container, a Dockerfile is provided. It uses `python:3.6-alpine` as base image which usually results in a container smaller than 100MB. It has no published ports and no external volumes, so configuration is quite minimal.

The provided shell-script `build-image.sh` creates an image named `python-mqtt-lightify-bridge:%Y%m%d-%H%M%S` and tags it with `python-mqtt-lightify-bridge:latest`. You can run the image with

    docker rm mqtt-lightify
    docker run --name mqtt-lightify -d python-mqtt-lightify-bridge:latest

or just use the provided `run-image.sh`.

## Usage

[![mqtt-smarthome](https://img.shields.io/badge/mqtt-smarthome-blue.svg)](https://github.com/mqtt-smarthome/mqtt-smarthome)
This project tries to follow the MQTT-Smarthome proposal. This means, that the bridge subscribes to specific topics on the broker and responds with messages at a certain format. More details are described at the [MQTT-Smarthome repository](https://github.com/mqtt-smarthome/mqtt-smarthome/blob/master/Architecture.md).

### Status reports

    /lightify/status/<device-id>/<datapoint>

If the bridge is asked for a device status, it reports all available datapoints at this topic. There will be one message for each available datapoint at its specific topic published.

The message format is as follows:

    {
        "val": <value>,
        "ts": <message creation timestamp>,
        "lightify": {
            "bridge": "<bridge ip>",
            "device": <device id>,
            "deviceName": "<device name>",
            "deviceType": "<device type>",
            "deviceTypeValue": <numerical representation of the device type>,
            "deviceSubType": "<device subtype>",
            "deviceSubTypeValue": <numerical representation of the device subtype>,
            "addr": <device address>,
            "idx": <device index>,
            "datapoint": "<datapoint name>",
            "datapointType": "<datapoint type>"
        }
    }

| value | data type | description |
| ----------------------------- | --- | -- |
| `val`                         | any | datapoint value |
| `ts`                          | int | timestamp (in milliseconds) when the message was created |
| `lightify.bridge`             | str | IP-address of the hardware brige | 
| `lightify.device`             | int | device ID, should be unique for each device |
| `lightify.deviceName`         | str | the name reported by te device |
| `lightify.deviceType`         | str | one of [`lightify.DeviceType`](https://github.com/tfriedel/python-lightify/blob/3a398381314efabffa69321f61d6ee7d44c721bd/lightify/__init__.py#L97) (currently `LIGHT`, `PLUG`, `SENSOR` or `SWITCH`) |
| `lightify.deviceTypeValue`    | int | the internal numerical representation of the device type |
| `lightify.deviceSubType`      | str | one of [`lighitfy.DeviceSubType`](https://github.com/tfriedel/python-lightify/blob/3a398381314efabffa69321f61d6ee7d44c721bd/lightify/__init__.py#L84) (currently `LIGHT_FIXED_WHITE`, `LIGHT_TUNABLE_WHITE`, `LIGHT_RGB`, `LIGHT_RGBW`, `PLUG`, `SWITCH`, `CONTACT_SENSOR` or `MOTION_SENSOR`) |
| `lightify.deviceSubTypeValue` | int | the internal numerical representation of the device subtype |
| `lightify.addr`               | int | device address, ths seems to be the same as `lightify.device` |
| `lightify.idx`                | int | index number of unknown function | 
| `lightify.datapoint`          | str | datapoint name, this should be reported the same as the datapoint in the message topic |
| `lightify.datapointType`      | str | data type of the datapoint. This is not implemented yet, contains `bla` |

### Set value

    /lightify/set/<device-id>/<datapoint>

Sets the value of a datapoint on the given device. The datapoints differ from the dtapoints reported back in status messages. The following datapoints are currently supported:

- `STATE`: If the message payload is `"true"`, `"1"` or `1`, turns the device on. All other values turn the device off.
- `RGB`: Sets the RGB value. The value has to be provided in HTML-hex-format, either with or without leading `#`. Example: a payload of `#ff0000` turns the light red, `00ff00` green etc. The characters are case insensitive. Note that this does not turn on the device and setting the value on an switched off device does not necessarily mean that the color has changed if the device is turned on afterwards.
- `LUM`: Sets the luminance of the device. Accepts an integer or a string which os astable to an integer between 0 and 100. The value is interpreted as percentage.
- `TEMP`: Sets the color temperature on devices supporting color temperature. The value has to be between `MIN_TEMP`and `MAX_TEMP` which both can be obtained by reading the status of that device.

Setting the device values is vastly simplified and cut down to the possibilities that are available to the single device I own, which is a RGBW bulb. Improvements (and pull requests) are very welcome!

### Get status

    /lightify/get/<device-id>

Since the bridge is passive and does not poll information from the devices (at the moment), you'll have to poll the status information yourself, either before each operation or periodically. This can be done by publishing a message to the above topic. This causes the bridge to publish the status report on the selected device at the topic `/lightify/status/<device-id>/<datapoint>` for each known datapoint on that device. The message payload sent with the message is ignored.

### Device discovery

    /lightify/command

To discover attached devices, a client can send a message to the above topic. There is currently one supported command, `INFO`. This can be invoked by sending a message payload to the command channel like this:

    {
        "command": "INFO",
        "param": <lightify method name>
    }

Note: this is absolute work in progress and not finally implemented yet! The safe way to see the device ids of the connected devices is to look at the logs at startup.

## Using the bridge in your own programs

If the bridge is started via th above command line invocation, it instantiates the main class as follows:

    bridge = MqttLightify(broker_address=BROKER_ADDRESS, bridge_address=BRIDGE_ADDRESS)
    bridge.start(loop_forever=True)

If the `loop_forever` is provided, this basically calls the same method on the mqtt client and waits for keyboard interrupt. If its not provided, the method calls `loop_start` on the mqtt client and returns. This can be used to integrate the bridge in your own programs. The event loop runs until the `stop` method is called or the program ends.