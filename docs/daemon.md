# `docker-zabbix-sender` script documentation

This module provides a daemon executable titled `docker-zabbix-sender`. It regularly pushes to a Zabbix server statistics about Docker containers running on a Docker deamon.

# Architecture

It is suggested to run the `docker-zabbix-sender` on the Docker daemon itself but this is not mandatory.

# Zabbix sender utility

Zabbix provides an executable titled `zabbix-sender` that allows you to **push** data to a Zabbix server. Instead of the traditional shema where Zabbix server polls its agents, this daemon script regularly pushes containers metrics to Zabbix server.

# How is it working?

`docker-zabbix-sender` holds a set of threads, one for each container to track. Each thread is registered to the `stats` stream of one container. Every x seconds (specified with the *--interval* option), the daemon collects the latest metrics of its threads, and push the result to the `zabbix-sender` utility.

# Command line interface

CLI pretty much looks like `zabbix-agent`'s. Please refer to output of `--help` option for further information.

```shell
$ docker-zabbix-sender --help
usage: docker-zabbix-sender [-h] [--tlsverify {true,false}] [-v] [-c <file>]
                            [-z <server>] [-p <server port>] [-i <sec>]

Provides Zabbix Docker containers statistics running on a Docker daemon.

optional arguments:
  -h, --help            show this help message and exit
  --tlsverify {true,false}
                        Use TLS and verify the remote daemon. Default is true
  -v, --version         show program\'s version number and exit
  -c <file>, --config <file>
                        Absolute path to the zabbix agent configuration file
  -z <server>, --zabbix-server <server>
                        Hostname or IP address of Zabbix server
  -p <server port>, --port <server port>
                        Specify port number of server trapper running on the
                        server. Default is 10051
  -i <sec>, --interval <sec>
                        Specify Zabbix update interval (in sec). Default is 30
```

# Provided metrics out of the box

The following Zabbix template provides events for every metric specified below.

## Container specific

For each container, the daemon will provide the following information:

* User mode CPU percentage
    - zabbix key: *docker.container.cpu.user_percent*
    - unit: percentage
    - type: Numeric (float)
* Kernel mode CPU percentage
    - zabbix key: *docker.container.cpu.kernel_percent*
    - unit: percentage
    - type: Numeric (float)
* Memory allocated:
    - zabbix key: *docker.container.memory.used*
    - unit: bytes
    - type: Numeric (float)
* Memory limit:
    - zabbix key: *docker.container.memory.limit*
    - unit: bytes
    - type: Numeric (float)
* Memory usage percentage
    - zabbix_key: *docker.container.memory.percent*
    - unit: percentage
    - type: Numeric (float)
* Network packet received, in bytes
    - zabbix key: *docker.container.network_rx*
    - unit: bytes
    - type: Numeric (float)
* Network packet transmitted:
    - zabbix key: *docker.container.network_tx*
    - unit: bytes
    - type: Numeric (float)

## Docker daemon specific

Additionally, the daemon provides 3 counters metrics providing containers counting information. Note that the hostname used for those events is the fqdn of **the host running the daemon script** (not the docker daemon if running elsewhere):

* All containers available in the Docker daemon:
    - zabbix key: *docker.container.count.all*
    - type: Numeric (unsigned)
* Running containers:
    - zabbix key: *docker.container.count.running*
    - type: Numeric (unsigned)
* Containers that didn't exit 0:
    - zabbix key: *docker.container.count.crashed*
    - type: Numeric (unsigned)

# Zabbix event hostname

Every pushed event hold the concerned hostname. Hostname for Docker container is computed (by default) as follow:

```
{container_name}.docker.{host_fqdn}
```

Where `host_fqdn` is the FQDN of the machine where is running the daemon script.

# Zabbix host registration

You need to create in Zabbix (virtual) hosts for each container to be monitored.

For example, if Docker daemon is running on **docker.acme.com**, the `docker-zabbix-sender` daemon running on **dockermon.acme.com**, and you want to monitor activity of container named `ÜberFoo`, then you have to create a Zabbix with the following settings:

* Host name: docker-ÜberFoo.dockermon.acme.com
* Agent interfaces: NONE!

# Docker daemon connection

`docker-zabbix-daemon` expected the Docker daemon to run on `localhost`. To connect to a remote Docker daemon, you have to specify a set of environment variables interpreted by the [Docker Python client](https://github.com/docker/docker-py) we use. See [Boot2Docker documentation](boot2docker.md) to get the list of environment variables to specify.
