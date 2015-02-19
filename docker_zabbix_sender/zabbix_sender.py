# encoding: utf-8

import logging
import os
import subprocess
import tempfile

from docker import Client

from .endpoint import EndPoint

LOGGER = logging.getLogger(__name__)

def zabbix_sender(input_file, config_file=None, zabbix_server=None, port=None, with_timestamps=False):
    """Simple wrapper around `zabbix_sender` utility.

    TODO: definitely implement the --real-time option. this module would pipe metrics to one single zabbix_sender
    process instead of spawning one process each time.
    """
    cmdline = ['zabbix_sender', '--input-file', input_file]
    if config_file:
        cmdline.extend(['--config', config_file])
    if zabbix_server:
        cmdline.extend(['--zabbix-server', zabbix_server])
    if port:
        cmdline.extend(['--port', port])
    if with_timestamps:
        cmdline.append('--with-timestamps')
    LOGGER.info("spawning process: " + " ".join(cmdline))
    subprocess.check_call(cmdline)

class ZabbixSenderEndPoint(EndPoint):
    def __init__(self, **kwargs):
        """
        :param kwargs: optional arguments given to the `zabbix_sender` function.
        """
        EndPoint.__init__(self)
        self._kwargs = kwargs
        self.pid = os.getpid()
        fd, self.output_file = tempfile.mkstemp()
        os.close(fd)

    def emit(self, events):
        if not any(events):
            return
        fmt = "{hostname} {key} {value}\n"
        if events[0].has_key('timestamp'):
            fmt = "{hostname} {key} {timestamp} {value}\n"
        with open(self.output_file, 'w') as ostr:
            for event in events:
                ostr.write(fmt.format(**event))
        zabbix_sender(self.output_file, **self._kwargs)
