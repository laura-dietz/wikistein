#!/usr/bin/env bash



wget http://trec-car.cs.unh.edu/datareleases/spritzer-v1.4.zip
unzip spritzer-v1.4.zip -d data
git clone https://github.com/TREMA-UNH/trec-car-tools.git
git clone https://github.com/laura-dietz/wikistein.git

python trec-car-tools/setup.py install
python wikistein/setup.py install
