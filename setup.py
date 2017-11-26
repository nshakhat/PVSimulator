#!/usr/bin/env python

from distutils.core import setup

setup(
    name='PVSimulator',
    version='0.1',
    description='PVSimulator for 1 day',
    author='Nadya Shakhat',
    author_email='nadmi4@gmail.com',
    packages=['simulator'],
    extras_require={},
    install_requires=['pvlib', 'pika', 'pandas', 'scipy'],
    entry_points={
        'console_scripts': [
            'simulate=simulator.simulate:init',
        ],
    },
)
