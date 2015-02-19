# encoding: utf-8

"""Provides collection of events emitters"""

import time

def containers_count(host_fqdn, docker_client, containers_metrics):
    """Emit events providing:
      - number of containers
      - number of running containers
      - number of crashed containers
    """
    running = 0
    crashed = 0
    now = int(time.time())
    containers = docker_client.containers(all=True)
    for container in containers:
        status = container['Status']
        if status.startswith('Up'):
            running += 1
        elif not status.startswith('Exited (0)'):
            crashed += 1
    data = {
        'all': len(containers),
        'running': running,
        'crashed': crashed,
    }
    return [
        {
            'hostname': host_fqdn,
            'timestamp': now,
            'key': 'docker.container.count.' + key,
            'value': value
        }
        for key, value in data.items()
    ]
