FROM python:3.6-alpine as base

FROM base as builder
RUN mkdir /install
WORKDIR /install
COPY requirements.txt /requirements.txt
RUN pip install --install-option="--prefix=/install" -r /requirements.txt

FROM base
COPY --from=builder /install /usr/local
COPY mqtt-lightify /app
WORKDIR /app

ENV BROKER_ADDRESS 192.168.178.30
ENV BRIDGE_ADDRESS 192.168.178.63

CMD ["python", "-m", "mqtt-lightify"]