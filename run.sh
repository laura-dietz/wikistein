#!/usr/bin/env bash -e

#wget http://trec-car.cs.unh.edu/datareleases/spritzer-v1.4.zip
#unzip spritzer-v1.4.zip -d data

if [[ -d wikistein ]]; then
    cd wikistein; git pull; cd ..
else
    git clone https://github.com/laura-dietz/wikistein.git
fi

cd wikistein
python setup.py install
cd ..

wikistein-create data/spritzer.cbor  bla bla2
