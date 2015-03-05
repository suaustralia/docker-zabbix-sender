#!/bin/bash

# Set ZABBIX_HOST environment variable 
# to container hostname if not already set.
export ZABBIX_HOST=${ZABBIX_HOST:-$HOSTNAME}

# if `docker run` first argument start with `-`, then
# the user is passing arguments to docker-zabbix-sender
if [[ $# -lt 1 ]] || [[ "$1" == "-"* ]]; then
  exec docker-zabbix-sender "$@"
fi

# As argument is not related to docker-zabbix-sender,
# then assume that user wants to run his own process,
# for example a `bash` shell to explore this image
exec "$@"
