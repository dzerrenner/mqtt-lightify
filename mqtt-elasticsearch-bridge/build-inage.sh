#! /bin/sh
docker build -t python-test:$(date +%Y%m%d-%H%M%S) -t python-test:latest .