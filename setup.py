#!/usr/bin/env python
import os
import sys
from setuptools import setup

ROOT_DIR = os.path.dirname(__file__)
SOURCE_DIR = os.path.join(ROOT_DIR)

requirements = [
    'docker-py >= 1.0.0',
]

exec(open('docker_zabbix_sender/version.py').read())

setup(
    name="docker-zabbix-sender",
    version=version,
    description="Push Docker containers information to Zabbix",
    packages=['docker_zabbix_sender'],
    install_requires=requirements,
    zip_safe=False,
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
)