#!/usr/bin/env bash

set -e

# git clone https://github.com/laura-dietz/wikistein.git
# cd wikistein
# python setup.py install
# bash run.sh

echo "requires python 3.5"


#dataset="spritzer"
#subset="spritzer"

#dataset="release"
#subset="release-v1.4/fold0.train"

dataset="test200"
subset="test200set/all.test200"

version="1.4"
qrels="${subset}.cbor.hierarchical.qrels"


version="1.4"
qrels="${subset}.cbor.hierarchical.qrels"

if [[ ! -f ${dataset}-v${version}.zip ]]; then
    wget http://trec-car.cs.unh.edu/datareleases/${dataset}-v${version}.zip
    unzip ${dataset}-v${version}.zip -d data
fi




echo "preparing data"
wikistein-create data/${subset}.cbor data/${subset}.cbor.paragraphs --train=data/${subset}.train --test=data/${subset}.test --relevance



echo "TREC CAR data is ready, run duet model NOW!"

echo "(Faking rankings for now)"
wikistein-mock-rank  data/${subset}.train data/${subset}.test data/${subset}.run

echo "Evaluating"
wikistein-eval data/${qrels} data/${subset}.run

