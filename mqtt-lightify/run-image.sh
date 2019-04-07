#! /bin/sh
docker rm mqtt-lightify
docker run --name mqtt-lightify -d python-mqtt-lightify-bridge:latest
