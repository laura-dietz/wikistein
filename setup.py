#!/usr/bin/env python3
from setuptools import setup

setup(
    name='wikistein',
    version='1.0',
    packages=['wikistein'],
    url='trec-car.cs.unh.edu',
    license='BSD 3-Clause',
    author='laura-dietz',
    author_email='Laura.Dietz@unh.edu',
    description='Interface between wikistein and trec-car-tools',
    install_requires=['cbor>=0.1.4', 'trec_car'],
)
