#!/bin/bash

nohup python /main.py &
mosquitto -c /etc/mosquitto/mosquitto.conf
