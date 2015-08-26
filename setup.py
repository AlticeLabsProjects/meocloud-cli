#! /usr/bin/env python
import os
import sys

from setuptools import Command
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


setup(
    name='meocloud-cli',
    version='0.1.18',
    description='Command line interface for meocloud',
    author='Hugo Castilho',
    author_email='hugo.p.castilho@telecom.pt',
    url='https://gitlab.intra.sapo.pt/security/fraudsible',
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
    packages=find_packages(),
    package_data={
        '': ['*.md', '*.sh'],
    },
    zip_safe=False,
    install_requires=[
        'PyYAML',
        'gevent',
        'greenlet',
        'six',
        'thrift',
    ],
    entry_points={
        'console_scripts': [
            'meocloud-cli = meocloud.client.linux.cli.cli:main',
            'meocloud-cli-daemon = meocloud.client.linux.daemon.daemon:main',
        ]
    },
    scripts=['meocloud/client/linux/daemon/restart_meocloud.sh'],
)
