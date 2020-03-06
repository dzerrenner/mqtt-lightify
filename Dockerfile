FROM python:3.6-alpine as base

FROM base as builder
RUN mkdir /install
WORKDIR /install
COPY requirements.txt /requirements.txt
RUN pip install --install-option="--prefix=/install" -r /requirements.txt

FROM base
COPY --from=builder /install /usr/local
COPY mqtt-lightify /app/mqtt-lightify
WORKDIR /app

ENV BROKER_ADDRESS 192.168.x.x
ENV BRIDGE_ADDRESS 192.168.x.x
ENV BROKER_USER mqtt_user
ENV BROKER_PASSWD b64password

CMD ["python", "-m", "mqtt-lightify"]
