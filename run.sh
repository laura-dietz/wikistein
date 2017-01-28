#!/usr/bin/env bash -e

dataset="spritzer"
subset="spritzer"
version="1.4"

if [[ ! -d data ]]; then
    wget http://trec-car.cs.unh.edu/datareleases/${dataset}-v${version}.zip
    unzip ${dataset}-v${version}.zip -d data
fi

if [[ -d wikistein ]]; then
    cd wikistein; git pull; cd ..
else
    git clone https://github.com/laura-dietz/wikistein.git
fi

cd wikistein
python setup.py install
cd ..

wikistein-create data/${subset}.cbor data/${subset}.train data/${subset}.test

wikistein-mock-rank  data/${subset}.train data/${subset}.test data/${subset}.run


echo "TREC CAR data is ready, run duet model!"

