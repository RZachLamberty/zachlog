#!/usr/bin/env python
from setuptools import setup

setup(
    name='zachlog',
    version='1.0.0',
    description='Ripped off logging library from peak6',
    author='Zach Lamberty',
    author_email='r.zach.lamberty@gmail.com',
    url='https://github.com/RZachLamberty/',
    packages=['zachlog'],
    install_requires=[
        'pyyaml',
    ]
)
