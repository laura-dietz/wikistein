#!/usr/bin/env python3
from setuptools import setup

setup(
    name='wikistein',
    version='1.0',
    packages=['wikistein'],
    entry_points={
        'console_scripts': [
            'wikistein-create = wikistein.create_train_data:main',
            'wikistein-mock-rank = wikistein.mock_rankings:main',
            'wikistein-eval = wikistein.simple_eval:main',
        ]
    },
    url='http://trec-car.cs.unh.edu/',
    license='BSD 3-Clause',
    author='laura-dietz',
    author_email='Laura.Dietz@unh.edu',
    description='Interface between the duet model and trec-car-tools',
    #install_requires=['trec_car>=1.4'],
    dependency_links=['git+https://github.com/TREMA-UNH/trec-car-tools.git']
)
