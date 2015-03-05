FROM python:2.7-onbuild
MAINTAINER Tristan CAREL <tristan.carel@gmail.com>

# ONBUILD directives took care of uploading
# the code and install dependencies

# Install zabbix_sender utility
RUN apt-get update && apt-get install -y zabbix-agent && apt-get clean

# Install module
RUN pip install .

# Install entry-point script
ADD docker-entry-point.sh /usr/local/bin/docker-entry-point.sh

# REQUIRED INPUTS

# Hostname or IP address of Zabbix server
ENV ZABBIX_SERVER zabbix-server

# Container needs to access the socket on host
VOLUME /var/run/docker.sock

ENTRYPOINT [ "docker-entry-point.sh" ]
