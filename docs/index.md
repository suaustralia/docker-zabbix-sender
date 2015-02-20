# Docker Zabbix Sender Documentation
Leverage Docker `stats` live streams to push containers statistics to Zabbix.

Docker Zabbix Sender is a Python module that allows you to monitor Docker containers with Zabbix.

# Installation
The latest stable installation is always available on PyPi.

```shell
pip install zabbix-containers-sender
```

# Requirements
Docker Zabbix Sender requires Docker 1.5 or higher. It leverages the new `stats` API call available in Docker Remote API version 17 to get live streams of containers statistics.

It also needs a Zabbix agent installed and properly configured (but not necessarily running).

# Getting started

You may follow the [Getting started tutorial](getting_started.md) to know more about it.

# How to contribute?

The source code is hosted on [GitHub](https://github.com/dockermeetupsinbordeaux/docker-zabbix-sender). Please feel free to submit pull request.

# How to report an issue?

Please use the project bug tracker available on [GitHub](https://www.zabbix.com/documentation/2.4/manual/config/items/itemtypes/trapper)

# License
zabbix-container-sender is licensed under the Apache License, Version 2.0. See [LICENSE](https://raw.githubusercontent.com/dockermeetupsinbordeaux/docker-zabbix-sender/master/LICENSE) for full license text.
