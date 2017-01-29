#!/usr/bin/env bash

set -e

# git clone https://github.com/laura-dietz/wikistein.git
# cd wikistein
# python setup.py install
# bash run.sh

#dataset="spritzer"
#subset="spritzer"


dataset="release"
subset="release-v1.4/fold0.train"

version="1.4"
qrels="${subset}.cbor.hierarchical.qrels"

if [[ ! -f ${dataset}-v${version}.zip ]]; then
    wget http://trec-car.cs.unh.edu/datareleases/${dataset}-v${version}.zip
    unzip ${dataset}-v${version}.zip -d data
fi




echo "preparing data"
wikistein-create data/${subset}.cbor data/${subset}.cbor.paragraphs data/${subset}.train data/${subset}.test



echo "TREC CAR data is ready, run duet model NOW!"

echo "(Faking rankings for now)"
wikistein-mock-rank  data/${subset}.train data/${subset}.test data/${subset}.run

echo "Evaluating"
wikistein-eval data/${qrels} data/${subset}.run

