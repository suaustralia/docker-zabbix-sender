# Docker Zabbix Sender Documentation
Leverage Docker statistic streams to push containers info to Zabbix

# Installation
The latest stable installation is always available on PyPi.

```shell
pip install zabbix-containers-sender
```

# Requirements
Docker Zabbix Sender requires Docker 1.5 or higher. It leverages the new `stats` API call available in Docker Remove API version 17 to get live streams of containers statistics.

# License
zabbix-container-sender is licensed under the Apache License, Version 2.0. See LICENSE for full license text
