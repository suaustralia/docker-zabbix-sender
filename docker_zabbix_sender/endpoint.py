# encoding: utf-8

import inspect
import logging
import pkg_resources
import socket

__all__ = [
    'EndPoint',
    'PPrintEndPoint'
]

class EndPoint(object):
    """Abstract class meant to receive containers metrics
    sent by `collector.ContainerStatsEmitter`

    It loads metrics registered as plugins to enrich metrics provided by collector.

    You need to implement the `emit` member method.
    """
    def __init__(self, host):
        """
        :param host: FQDN of the host running the monitored containers
        """
        self._logger = logging.getLogger("end-point")
        self._host = host
        self.metrics_plugins = self._load_metrics_plugins()

    IGNORED_METRIC_KEYS = {'name', 'timestamp', 'stats'}
    METRICS_GROUP = 'docker_zabbix_sender.metrics'
    EVENT_KEY_PREFIX = 'docker.container.'

    @classmethod
    def container_hostname(cls, host, container_name):
        """Get "real" hostname of a container.

        Default implement returns: 'docker-{container_name}.{current_host_fqdn}'

        :param: metrics of a container given to the endpoint (dict)
        """
        return "{0}.docker.{1}".format(container_name, host)

    def __call__(self, client, containers_metrics):
        """Method used by collector to emit new metrics to this end-point.
        Metrics are translated, enriched, and passed to the `emit` member method

        :param client: Docker client

        :params containers_metrics: list of dict with containers information, one dict per container.
        """
        events, statistics = self._metrics_to_events(containers_metrics)
        self._enrich_with_plugins(client, statistics, events)
        self.emit(events)

    def emit(self, events):
        """
        :param events: list of dict with the following keys: hostname, timestamp, key, value
        """
        raise NotImplementedError()

    def close(self):
        """Release allocated resources. Meant to be overloaded
        """
        pass

    def _metrics_to_events(self, containers_metrics):
        """Transform list of dict containing containers metrics to a list of dict with the following keys:
            'host', 'key', 'value'
        Each dict also contains the 'timestamp' key if the metrics provide it.

        :param containers_metrics: new metrics given to the endpoint
        :return list of events
        """
        events = []
        stats = []
        for metrics in containers_metrics:
            stats.append(metrics['stats'])
            hostname = EndPoint.container_hostname(self._host, metrics['name'])
            timestamp = metrics['timestamp']
            for key, value in metrics.items():
                if key in EndPoint.IGNORED_METRIC_KEYS:
                    continue
                events.append({
                    'hostname': hostname,
                    'timestamp': timestamp,
                    'key': EndPoint.EVENT_KEY_PREFIX + key,
                    'value': value,
                })
        return events, stats

    def _enrich_with_plugins(self, client, statistics, events):
        """Ask registered metrics plugins to produce additional events according to new containers metrics

        :param client: Docker client given to the metrics plugins

        :param statistics: list of tuple providing container statistics, one dict per container.

        :param events: events collection, to be filled by metrics plugins
        """
        for name, collector in self.metrics_plugins.items():
            try:
                events.extend(collector(self._host, client, statistics))
            except Exception, e:
                self._logger.exception("Could not collect metrics from plugin %s", name)

    def _load_metrics_plugins(self):
        """Loads objects registered with the '[docker-zabbix-sender.metrics]' entry point.
        :return dict of plugin_name -> callable_object
        """
        metrics = {}
        for entrypoint in pkg_resources.iter_entry_points(group=EndPoint.METRICS_GROUP):
            try:
                plugin = entrypoint.load()
                metrics[entrypoint.name] = plugin
                assert hasattr(plugin, '__call__')
                self._logger.info("Registered metrics entrypoint '%s'", entrypoint.name)
            except Exception:
                self._logger.exception("Could not load entrypoint %s", entrypoint.name)
        return metrics


class PPrintEndPoint(EndPoint):
    """Dumb EndPoint that prints produced events"""
    def emit(self, events):
        import pprint
        pprint.pprint(events)
