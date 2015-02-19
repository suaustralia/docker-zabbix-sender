# encoding: utf-8

import json
import logging
import signal
import sys
import time
import threading

from docker import Client
from docker.utils import kwargs_from_env

from .RWLock import RWLock

__all__ = [
    'ContainerStatsEmitter',
    'ContainerStats'
]

def docker_client():
    return Client(**kwargs_from_env())

class ContainerStats:
    def __init__(self, container):
        self.container = container
        self._lock = RWLock()
        self._response = None
        self.cpu_percent = 0.0
        self.memory = 0.0
        self.memory_limit = 0.0
        self.memory_percentage = 0.0
        self.network_rx = 0.0
        self.network_tx = 0.0

    def collect(self, client):
        assert isinstance(client, Client)
        self.name = client.inspect_container(self.container)['Name'][1:]
        previous_cpu = 0.0
        previous_system = 0.0
        start = True
        url = client._url("/containers/{0}/stats".format(self.container))
        self._response = client._get(url, stream=True)
        stream = client._stream_helper(self._response, decode=True)
        try:
            for stats in stream:
                mem_percent = float(stats['memory_stats']['usage']) / stats['memory_stats']['limit'] * 100.0
                cpu_percent = 0.0
                if not start:
                    cpu_percent = self._calculate_cpu_percent(previous_cpu, previous_system, stats)
                start = False
                self._lock.acquire_write()
                self.cpu_percent = cpu_percent
                self.memory = float(stats['memory_stats']['usage'])
                self.memory_limit = float(stats['memory_stats']['limit'])
                self.memory_percentage = mem_percent
                self.network_rx = float(stats['network']['rx_bytes'])
                self.network_tx = float(stats['network']['tx_bytes'])
                self._lock.release()
                previous_cpu = stats['cpu_stats']['cpu_usage']['total_usage']
                previous_system = stats['cpu_stats']['system_cpu_usage']
        except AttributeError:
            # raise in urllib3 when the stream is closed while waiting for stuff to read
            pass
        except ReadTimeoutError:
            pass # not sure I should stop this
        finally:
            self.close()

    def emit(self, consumer_func):
        self._lock.acquire_read()
        try:
            consumer_func(self)
        finally:
            self._lock.release()


    def close(self):
        if self._response:
            print "closing stream"
            self._response.raw.close()
            self._response = None

    def _calculate_cpu_percent(self, previous_cpu, previous_system, stats):
        cpu_percent = 0.0
        # calculate the change for the cpu usage of the container in between readings
        cpu_delta = float(stats['cpu_stats']['cpu_usage']['total_usage']) - previous_cpu
        # calculate the change for the entire system between readings
        system_delta = float(stats['cpu_stats']['system_cpu_usage']) - previous_system
        if system_delta > 0.0 and cpu_delta > 0.0:
            cpu_percent = (cpu_delta / system_delta) * float(len(stats['cpu_stats']['cpu_usage']['percpu_usage'])) * 100.0
        return cpu_percent


class ContainerStatsEmitter(threading.Thread):
    def __init__(self, client, endpoint_func, delay):
        threading.Thread.__init__(self)
        self._client = client
        self._endpoint_func = endpoint_func
        self._delay = delay
        self._stop = False
        self._logger = logging.getLogger("stats-emitter")

    def run(self):
        container_stats = dict()
        all_threads = []
        while self._should_run():
            # update list of container stats
            running_containers = set(map(lambda c: c['Id'], self._client.containers()))
            monitored_containers = set(container_stats.keys())
            started_containers = running_containers - monitored_containers
            stopped_containers = monitored_containers - running_containers
            for container in stopped_containers:
                self._logger.info("container has stopped: %s", container)
                container_stats.pop(container).close()
            for container in started_containers:
                self._logger.info("container has started: %s", container)
                stats = ContainerStats(container)
                container_stats[container] = stats
                t = threading.Thread(target=stats.collect, args=(self._client,))
                all_threads.append(t)
                t.start()
            time.sleep(self._delay)
            # collect results
            payload = []
            def append(stats):
                payload.append({
                    'name': stats.name,
                    'id': stats.container,
                    'cpu_percent': stats.cpu_percent,
                    'memory': stats.memory,
                    'memory_limit': stats.memory_limit,
                    'memory_percentage': stats.memory_percentage,
                    'network_rx': stats.network_rx,
                    'network_tx': stats.network_tx,
                })
            for stats in container_stats.values():
                stats.emit(append)
            # emit to endpoint_func
            self._endpoint_func(payload)
        self._logger.info("Waiting for all collectors threads to terminate.")
        for container in container_stats.values():
            container.close()
        for thread in all_threads:
            thread.join()
        self._logger.info("Collectors terminated successfully. See you bye!")

    
    def _should_run(self):
        return not self._stop

    def stop(self):
        self._logger.info("Begin script termination.")
        self._stop = True
        
def log_all(payload):
    import pprint
    pprint.pprint(payload)

if __name__ == '__main__':
    FORMAT = '%(asctime)-15s %(levelname)-8s %(name)s %(message)s'
    logging.basicConfig(format=FORMAT, level=logging.INFO)
    emitter = ContainerStatsEmitter(docker_client(), log_all, 3)
    def stop_emitter(signum, frame):
        emitter.stop()
    signal.signal(signal.SIGTERM, stop_emitter)
    signal.signal(signal.SIGINT, stop_emitter)
    emitter.start()
    signal.pause()
