# Getting started

This page describes the step-by-step procedure to install and use Docker Zabbix Sender.

Some commands below supposes your are running on Linux.

## Prerequisites

You may have:
* a Zabbix server installed somewhere, let's say: zabbix.acme.com
* a machine to install Docker (with root privileges), let's say: docker-daemon.acme.com

## Installation

**You can skip this section if you use Docker Zabbix Sender as a Docker container**

1. Install Docker 1.5 or higher.
1. Install Zabbix agent. There is an official `zabbix-agent` package on most distribution. Makes sure the `zabbix-sender` executable is in your `PATH` environment variable.
1. Edit the `/etc/zabbix_agentd.conf` and edit the following variable:
    * Server=zabbix.acme.com
    * Hostname=docker.acme.com
1. Install latest version of `docker-zabbix-sender`.
    
    ```shell
    pip install docker-zabbix-sender
    ```

## Start a bunch of containers

Now it is time to start a few containers to monitor. 

First log as `root` and make sure the Docker service is running:

```shell
service docker start
```

Now starts 3 minimalistic busybox containers in background :

```shell
docker run -d -ti --name container1 busybox
docker run -d -ti --name container2 busybox
docker run -d -ti --name container3 busybox
```

## Configuration on Zabbix server

Zabbix needs a little bit of configuration before being fed with Docker containers statistics.

There are a couple of [Zabbix templates](https://github.com/dockermeetupsinbordeaux/docker-zabbix-sender/tree/master/resources/zabbix_templates) available on the GitHub repository:
* *Docker daemon*: provides [trapper events](https://www.zabbix.com/documentation/2.4/manual/config/items/itemtypes/trapper) monitoring the containers (number of running containers, crashed containers, ...)
* *Docker container*: provides trapper events, meant to monitor one container (CPU, memory, and network).

1. Import the 2 templates on your Zabbix server
2. Add 3 hosts, one for each started containers:
    * container1.docker.docker-daemon.acme.com
    * container2.docker.docker-daemon.acme.com
    * container3.docker.docker-daemon.acme.com
    
    Note the **docker** prefix between the container name and the hostname. 
    
    Note: you will have to specify an agent for those hosts. Zabbix won't talk directly to those machines, so you can put anything you want (the docker-daemon.acme.com IP address for instance)
3. Add the `Docker container` template to those 3 hosts.
4. Add the `docker-daemon.acme.com` host if not already registered
5. Register the `Docker daemon` template to `docker-daemon.acme.com`

## First start

### Running as Docker Container

```shell
docker run                                          \
    -e ZABBIX_SERVER=zabbix.acme.com>               \
    -e ZABBIX_HOST=docker-daemon.acme.com           \
    -v /var/run/docker.sock:/var/run/docker.sock    \
    dockermeetupsinbordeaux/docker-zabbix-sender
```

### Installed on a bare-metal server

Run the `docker-zabbix-sender` command as `root` (required to deal with Docker API):

```shell
docker-zabbix-sender -c /etc/zabbix/zabbix_agentd.conf --interval 5 --real-time
```

The executable will collect information about your containers and send them to Zabbix every 5 seconds.

After a couple of seconds, you should see some metrics in Zabbix, in the **Monitoring > Latest data** page.

There are a couple of basic graphs defined in the Zabbix templates. you should take a look at it.

## Is it really working?

You can play with the CPU activity of one of the container and see if this is propagated to Zabbix.

```shell
# docker exec -ti container1 sh
/ # while true; do usleep 200; done
```

Keep it running and observe the peak on Zabbix.

## Further readings

You may start with the [Daemon page](daemon.md) to get more insight about it, especially about the various options you can pass.
