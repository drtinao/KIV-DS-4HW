#
# Use base image, install python and copy 
#

FROM ghcr.io/maxotta/kiv-ds-docker:latest
COPY commands.sh /
COPY main.py /
RUN chmod u+x ./commands.sh
RUN chmod u+x ./main.py

RUN yum -q -y install epel-release
RUN yum -q -y install python-pip
RUN pip install lorem
RUN pip install paho-mqtt
RUN pip install kazoo
