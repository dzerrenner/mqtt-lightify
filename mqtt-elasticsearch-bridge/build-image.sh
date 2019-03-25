#! /bin/sh
docker build -t python-mqtt-elasticsearch-bridge:$(date +%Y%m%d-%H%M%S) -t python-mqtt-elasticsearch-bridge:latest .