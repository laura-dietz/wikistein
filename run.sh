#!/usr/bin/env bash -e

#wget http://trec-car.cs.unh.edu/datareleases/spritzer-v1.4.zip
#unzip spritzer-v1.4.zip -d data
git clone https://github.com/laura-dietz/wikistein.git

cd wikistein
python setup.py install

wikistein-create ../data/spritzer.cbor  bla bla2
