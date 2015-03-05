# encoding: utf-8

import argparse
import logging
import os
import subprocess
import signal
import sys
import tempfile

from docker import Client
from docker.utils import kwargs_from_env

from .endpoint import EndPoint
from .collector import ContainerStatsEmitter

LOGGER = logging.getLogger(__name__)

class ZabbixSenderProcess(subprocess.Popen):
    """A 'zabbix_sender' process with stdin piped.
    """
    def __init__(self, **kwargs):
        subprocess.Popen.__init__(self, ZabbixSenderProcess.cmdline(**kwargs), stdin=subprocess.PIPE)

    @classmethod
    def cmdline(cls,
            input_file,
            config_file=None,
            zabbix_server=None,
            host=None,
            port=None,
            with_timestamps=False,
            real_time=False,
            verbose=0):
        """
        :return collection containing the 'zabbix_sender' command line to execute.
        """
        cmdline = ['zabbix_sender', '--input-file', input_file]
        if config_file:
            cmdline.extend(['--config', config_file])
        if zabbix_server:
            cmdline.extend(['--zabbix-server', zabbix_server])
        if host:
            cmdline.extend(['--host', host])
        if port:
            cmdline.extend(['--port', port])
        if with_timestamps:
            cmdline.append('--with-timestamps')
        if real_time:
            cmdline.append('--real-time')
        print verbose
        if verbose != 0:
            cmdline.append('-' + 'v' * verbose)
        return cmdline

def get_zabbix_hostname_from_config(config_file):
    """Look for the hostname in Zabbix agent configuration file and returns it.

    Best match is value of 'Hostname' key, 'HostnameItem' otherwise.

    :param config_file: zabbix agent config file. 
    Should be "/etc/zabbix/zabbix_agent.conf" unless you have an exotic installation

    Throws Exception if both key are not defined.
    """
    import ConfigParser
    class FakeSecHead(object):
        def __init__(self, fp):
            self.fp = fp
            self.sechead = '[asection]\n'

        def readline(self):
            if self.sechead:
                try:
                    return self.sechead
                finally:
                    self.sechead = None
            else:
                return self.fp.readline()
    with open(config_file) as istr:
        cp = ConfigParser.ConfigParser()
        cp.readfp(FakeSecHead(istr))
        try:
            return cp.get('asection', 'Hostname')
        except:
            pass
        try:
            return cp.get('asection', 'HostnameItem')
        except:
            raise Exception("Couldn't find either 'Hostname' and 'HostnameItem' in configuration file: %s" % config_file)


class ZabbixSenderEndPoint(EndPoint):
    def __init__(self, **kwargs):
        """
        :param kwargs: optional arguments given to the `zabbix_sender` function.
        """
        docker_daemon = kwargs.get('host')
        if docker_daemon is None:
            zabbix_agent_config = kwargs.get('config_file')
            if zabbix_agent_config is None:
                raise Exception("Invalid parameters: needs 'host' or 'config_file'")
            else:
                docker_daemon = get_zabbix_hostname_from_config(zabbix_agent_config)
        EndPoint.__init__(self, docker_daemon)
        self.zabbix_sender_p = ZabbixSenderProcess(
            input_file='-',
            with_timestamps=True,
            **kwargs
        )

    def emit(self, events):
        if not any(events):
            return
        fmt = "{hostname} {key} {value}\n"
        if events[0].has_key('timestamp'):
            fmt = "{hostname} {key} {timestamp} {value}\n"
        for event in events:
            self.zabbix_sender_p.stdin.write(fmt.format(**event))

    def close(self):
        self.zabbix_sender_p.communicate()

def run(args=None):
    """Main entry point. Runs until SIGTERM or SIGINT is emitted.

    :param args: Optional arguments, use `sys.argv[1:]` otherwise
    """
    if args is None:
        args = sys.argv[1:]
        FORMAT = '%(asctime)-15s %(levelname)-8s %(name)s %(message)s'
        logging.basicConfig(format=FORMAT, level=logging.INFO)

    from .version import version
    parser = argparse.ArgumentParser(
        description="""Provides Zabbix Docker containers statistics running on a Docker daemon."""
    )
    parser.add_argument('-V', '--version',
        action='version',
        version='%(prog)s ' + version
    )
    parser.add_argument('-v', '--verbose',
        action='count',
        help='Verbose mode, -vv for more details'
    )
    parser.add_argument("--tlsverify",
        action='store',
        choices=["true", "false"],
        default='true',
        help="Use TLS and verify the remote Docker daemon. Default is %(default)s"
    )
    parser.add_argument('-c', '--config',
        metavar="<file>",
        help="Absolute path to the zabbix agent configuration file"
    )
    parser.add_argument('-z', '--zabbix-server',
        metavar='<server>',
        help='Hostname or IP address of Zabbix server'
    )
    parser.add_argument('-p', '--port',
        metavar='<server port>',
        help='Specify port number of server trapper running on the server. Default is 10051'
    )
    parser.add_argument('-i', '--interval',
        metavar='<sec>',
        default=30,
        type=int,
        help='Specify Zabbix update interval (in sec). Default is %(default)s'
    )
    parser.add_argument('-r', '--real-time',
        action='store_true',
        help="zabbix_sender push metrics to Zabbix one by one as soon as they are sent."
    )
    parser.add_argument('-s', '--host',
        metavar='<hostname>',
        help='Specify host name. Host IP address and DNS name will not work'
    )
    args = parser.parse_args(args)
    kwargs  = kwargs_from_env()
    if not args.tlsverify.lower() in ("yes", "true", "t", "1"):
        kwargs['tls'].assert_hostname = False
    kwargs['version'] = '1.17'
    docker_client = Client(**kwargs)
    docker_client.info()
    if args.zabbix_server is None:
        args.zabbix_server = os.environ['ZABBIX_SERVER']
    if args.host is None:
        args.host = os.environ['ZABBIX_HOST']

    emitter = ContainerStatsEmitter(
        docker_client,
        ZabbixSenderEndPoint(
            config_file=args.config,
            zabbix_server=args.zabbix_server,
            host=args.host,
            port=args.port,
            real_time=args.real_time,
            verbose=args.verbose if args.verbose is not None else 0
        ),
        args.interval)
    def _stop_emitter(signum, frame):
        """Handle for signal catching used to stop the `ContainerStatsEmitter` thread
        """
        emitter.shutdown()
    signal.signal(signal.SIGTERM, _stop_emitter)
    signal.signal(signal.SIGINT, _stop_emitter)
    emitter.start()
    signal.pause()

if __name__ == '__main__':
    run()
