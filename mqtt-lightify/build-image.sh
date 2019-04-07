#! /bin/sh
docker build -t python-mqtt-lightify-bridge:$(date +%Y%m%d-%H%M%S) -t python-mqtt-lightify-bridge:latest .
