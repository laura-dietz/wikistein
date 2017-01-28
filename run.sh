#!/usr/bin/env bash -e

dataset="spritzer"
subset="spritzer"
version="1.4"
qrels="${subset}.cbor.hierarchical.qrels"

if [[ ! -d data ]]; then
    wget http://trec-car.cs.unh.edu/datareleases/${dataset}-v${version}.zip
    unzip ${dataset}-v${version}.zip -d data
fi

if [[ -d wikistein ]]; then
    cd wikistein; git pull; cd ..
    echo "warning: if git pull obtained a new version of this script, you need to run it again."
else
    git clone https://github.com/laura-dietz/wikistein.git
fi

cd wikistein
python setup.py install
cd ..

echo "preparing data"
wikistein-create data/${subset}.cbor data/${subset}.train data/${subset}.test



echo "TREC CAR data is ready, run duet model NOW!"

echo "(Faking rankings for now)"
wikistein-mock-rank  data/${subset}.train data/${subset}.test data/${subset}.run

echo "Evaluating"
wikistein-eval data/${qrels} data/${subset}.run


echo "warning: if git pull obtained a new version of this script, you need to run it again."