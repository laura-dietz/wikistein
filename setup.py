#!/usr/bin/env python3
from setuptools import setup

setup(
    name='wikistein',
    version='1.0',
    packages=['wikistein'],
    entry_points={
        'console_scripts': [
            'wikistein-create = wikistein.create_train_data:main',
        ]
    },
    url='http://trec-car.cs.unh.edu/',
    license='BSD 3-Clause',
    author='laura-dietz',
    author_email='Laura.Dietz@unh.edu',
    description='Interface between the duet model and trec-car-tools',
    install_requires=['trec_car>=1.4'],
)
