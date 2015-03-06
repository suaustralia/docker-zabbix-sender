#!/usr/bin/env python
import os
import sys
from setuptools import setup
from textwrap import dedent

NAME = "docker-zabbix-sender"
GITHUB_ORG_URL = "https://github.com/dockermeetupsinbordeaux"
ROOT_DIR = os.path.dirname(__file__)
SOURCE_DIR = os.path.join(ROOT_DIR)

exec(open('docker_zabbix_sender/version.py').read())

setup(
    name=NAME,
    version=version,
    author="Tristan Carel",
    author_email="tristan.carel@gmail.com",
    url= GITHUB_ORG_URL + '/' + NAME,
    download_url="{0}/{1}/tarball/v{2}".format(GITHUB_ORG_URL, NAME, version),
    description="Push Docker containers statistics to Zabbix efficiently",
    long_description=dedent("""
        Rationale
        ---------
        Docker Zabbix Sender delivers a daemon script that push to Zabbix statistics about Docker containers.

        It leverages 2 interesting components:

        - Zabbix maintains a tool titled ``zabbix-sender``.
          It is meant to push `Zabbix trapper items`_ efficiently.

        - Docker 1.5.0 comes with Docker Remote API version 17, providing a new `stats endpoint`_.
          It allows the client to subscribe to a live feed delivering a container statistics.

        The daemon script stands in the middle of those 2 components.
        It collects Docker containers statistics and transforms them in Zabbix trapper events.

        Published metrics
        -----------------
        The daemon script already emits a collection of metrics: CPU, memory, and network usage.
        The module's API provide mechanism to easily extend the list of published events.

        Documentation
        -------------
        The stable documentation is available on ReadTheDocs_

        .. _Zabbix trapper items: https://www.zabbix.com/documentation/2.4/manual/config/items/itemtypes/trapper
        .. _stats endpoint: https://docs.docker.com/reference/api/docker_remote_api_v1.17/#get-container-stats-based-on-resource-usage
        .. _ReadTheDocs: http://docker-zabbix-sender.readthedocs.org/en/stable/
    """),
    keywords="docker zabbix monitoring",
    packages=['docker_zabbix_sender'],
    install_requires=[
        'docker-py >= 1.0.0',
    ],
    zip_safe=False,
    license="Apache license version 2.0",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Utilities',
        'License :: OSI Approved :: Apache Software License',
    ],
    entry_points = """
        [console_scripts]
        docker-zabbix-sender = docker_zabbix_sender.zabbix_sender:run
        [docker_zabbix_sender.metrics]
        container-count = docker_zabbix_sender.stats:container_count
        cpu-count = docker_zabbix_sender.stats:cpu_count
        container-ip = docker_zabbix_sender.stats:container_ip
    """
)
