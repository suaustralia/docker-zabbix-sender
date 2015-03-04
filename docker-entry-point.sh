#!/bin/bash

# Set ZABBIX_HOST if not already done
export ZABBIX_HOST=${ZABBIX_HOST:-$HOSTNAME}

# if `docker run` first argument start with `-` the user is passing jenkins swarm launcher arguments
if [[ $# -lt 1 ]] || [[ "$1" == "-"* ]]; then

  exec docker-zabbix-sender "$@"
fi

# As argument is not jenkins, assume user want to run his own process, for sample a `bash` shell to explore this image
exec "$@"
