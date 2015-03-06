# Docker Zabbix Sender Documentation
Leverage Docker `stats` live streams to push containers statistics to Zabbix.

Docker Zabbix Sender is available as a Docker container itself. It is also delivered as a Python module to install it manually on a server.

## Requirements
Docker Zabbix Sender requires Docker 1.5 or higher. It leverages the new `stats` API call available in Docker Remote API version 17 to get live streams of containers statistics.

# How to use the Docker container?

```shell
docker run                                          \
    -e ZABBIX_SERVER=<YOUR_ZABBIX_SERVER>           \
    -e ZABBIX_HOST=<HOST_FQDN>                      \
    -v /var/run/docker.sock:/var/run/docker.sock    \
    dockermeetupsinbordeaux/docker-zabbix-sender
```

# How to use the distributed Python module?

The latest stable installation is always available on PyPi.

```shell
pip install zabbix-containers-sender
```

# Getting started

You may follow the [Getting started tutorial](getting_started.md) to know more about it.

# How to contribute?

The source code is hosted on [GitHub](https://github.com/dockermeetupsinbordeaux/docker-zabbix-sender). Please feel free to submit pull request.

# How to report an issue?

Please use the project bug tracker available on [GitHub](https://www.zabbix.com/documentation/2.4/manual/config/items/itemtypes/trapper)

# License
zabbix-container-sender is licensed under the Apache License, Version 2.0. See [LICENSE](https://raw.githubusercontent.com/dockermeetupsinbordeaux/docker-zabbix-sender/master/LICENSE) for full license text.
