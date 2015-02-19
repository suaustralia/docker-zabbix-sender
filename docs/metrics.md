# Docker metrics

This page explains how to augment the list of metrics pushed by `docker-zabbix-sender` by default.

To get the list of `docker-zabbix-sender` already pushed, please see the [Daemon](daemon.md#Provided metrics out of the box) documentation.

# Write your own Python module!

You can write and install a Python module that declares a set of metrics to be used by `docker-zabbix-sender`. They must be declared under the `docker_zabbix_sender.metrics` entrypoint group.

An event emitter must be a callable object that takes 3 arguments in parameters and returns a list of dict, one for each event.

for instance:
```python
def dumb_emitter(host_fqdn, docker_client, statistics):
    """
    :param host_fqdn: FQDN of the host where the docker-zabbix-daemon is running, for instance docker.acme.com
    :type host_fqdn: string

    :param docker_client: instance of docker.Client see http://docker-py.readthedocs.org/en/latest/api/
    :type docker_client: docker.Client

    :param statistics: List of dicts providing collected container statistics. see Docker stats API call on https://docs.docker.com/reference/api/docker_remote_api_v1.17/#get-container-stats-based-on-resource-usage

    :return: list of dicts providing additional events to push to Zabbix.
    Each dict is composed of 4 keys:
        - hostname
        - key
        - value
        - timestamp
    """
    return [
        {
            'hostname': 'docker-leet_torwald.docker.acme.com',
            'timestamp': 1424363786,
            'key': 'docker.container.pgfault',
            'value': 42000,
        },
        {
            'hostname': 'docker-leet_torwald.docker.acme.com',
            'timestamp': 1424363786,
            'key': 'docker.container.pgmajfault',
            'value': 0,
        }
    ]
```

You can exploit `containers_stats` to build your metrics. If it does not fit your needs, then you can connect to Docker remote API with the `docker_client`parameter.
