#
# Use base image, install Eclipse Mosquitto for mqtt and Python for easy zookeeper registration.
#

FROM ghcr.io/maxotta/kiv-ds-docker:latest
COPY commands.sh /
COPY main.py /
RUN chmod u+x ./commands.sh
RUN chmod u+x ./main.py

#RUN yum -q -y install python3

# install Eclipse Mosquitto - START
RUN yum -q -y install epel-release
RUN yum -q -y install mosquitto
# install Eclipse Mosquitto - END

RUN yum -q -y install python-pip
RUN pip install kazoo

# specify port on which broker will listen
RUN echo "listener 1880" >> /etc/mosquitto/mosquitto.conf
# allow anonymous connections
RUN echo "allow_anonymous true" >> /etc/mosquitto/mosquitto.conf

# set up bridge between brokers - START
ARG BRIDGENAME
ARG BRIDGEADDRESS
ARG TOPICOUT
ARG TOPICIN

RUN echo "$BRIDGENAME" >> /etc/mosquitto/mosquitto.conf
RUN echo "$BRIDGEADDRESS" >> /etc/mosquitto/mosquitto.conf
RUN echo "$TOPICOUT" >> /etc/mosquitto/mosquitto.conf
RUN echo "$TOPICIN" >> /etc/mosquitto/mosquitto.conf
# set up bridge between brokers - END

HEALTHCHECK --interval=5s CMD pgrep mosquitto || exit 1

