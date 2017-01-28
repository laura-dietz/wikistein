#!/usr/bin/env bash -e



wget http://trec-car.cs.unh.edu/datareleases/spritzer-v1.4.zip
unzip spritzer-v1.4.zip -d data
git clone https://github.com/laura-dietz/wikistein.git

python wikistein/setup.py install
