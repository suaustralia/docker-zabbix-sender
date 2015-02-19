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
    def __init__(self):
        self.fqdn = socket.getfqdn()
        self._logger = logging.getLogger("end-point")
        self.metrics_plugins = self._load_metrics_plugins()

    IGNORED_METRIC_KEYS = {'name', 'timestamp'}
    METRICS_GROUP = 'docker_zabbix_sender.metrics'

    def container_hostname(self, container_metrics):
        """Get "real" hostname of a container.

        Default implement returns: 'docker-{container_name}.{current_host_fqdn}'

        :param: metrics of a container given to the endpoint (dict)


        """
        return "docker-{0}.{1}".format(container_metrics['name'], self.fqdn)

    def __call__(self, client, containers_metrics):
        """Method used by collector to emit new metrics to this end-point.
        Metrics are translated, enriched, and passed to the `emit` member method

        :param client: Docker client

        :params metrics: list of dict with containers information, one dict per container.
        """
        events = self._metrics_to_events(containers_metrics)
        self._enrich_with_plugins(client, containers_metrics, events)
        self.emit(events)

    def emit(self, events):
        """
        :param events: list of dict with the following keys: hostname, timestamp, key, value
        """
        raise NotImplementedError()

    def _metrics_to_events(self, containers_metrics):
        """Transform list of dict containing containers metrics to a list of dict with the following keys:
            'host', 'key', 'value'
        Each dict also contains the 'timestamp' key if the metrics provide it.

        :param containers_metrics: new metrics given to the endpoint
        :return list of events
        """
        events = []
        for metrics in containers_metrics:
            hostname = self.container_hostname(metrics)
            timestamp = metrics['timestamp']
            for key, value in metrics.items():
                if key in EndPoint.IGNORED_METRIC_KEYS:
                    continue
                events.append({
                    'hostname': hostname,
                    'timestamp': timestamp,
                    'key': key,
                    'value': value,
                })
        return events

    def _enrich_with_plugins(self, client, containers_metrics, events):
        """Ask registered metrics plugins to produce additional events according to new containers metrics"""
        for name, collector in self.metrics_plugins.items():
            try:
                events.extend(collector(self.fqdn, client, containers_metrics))
            except Exception, e:
                self._logger.exception("Could not collect metrics from plugin %s", name)

    def _load_metrics_plugins(self):
        """Loads objects registered with the '[docker-zabbix-sender.metrics]' entry point.
        :return dict of name -> value
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
