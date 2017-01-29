from itertools import groupby
from random import shuffle
from typing import List, Dict

import itertools

columndelim=' ' # for trec_eval set to space; for TSV set to tab

class Elem():
    def __init__(self, sectionId, query, paraId, paraText, rel):
        self.sectionId = sectionId
        self.query = query
        self.paraId = paraId
        self.paraText = paraText
        self.rel = rel


def parse_test(line:str) -> Elem:
    splits = line.split(sep='\t')
    sectionId = splits[0]
    query = splits[1]
    paraId = splits[2]
    paraText = splits[3]
    rel = int(splits[4])
    return Elem(sectionId, query, paraId, paraText, rel)

def load_input(testFile, runwriter, maxentries=None):# -> Dict[str, List[Elem]]:
    testdata = (parse_test(line) for line in itertools.islice(testFile, 0, maxentries))
    # return groupby(testdata, key=lambda elem: elem.sectionId)
#
# def write_mock_rankings(testdata:Dict[str,List[Elem]], runwriter):
#     testdata = itertools.groupby(testdata, key=lambda elem: elem.sectionId)
    for key, elems_ in itertools.groupby(testdata, key=lambda elem: elem.sectionId): #testdata:
        print("mock ranking:", key)
        elems = list(elems_)
        shuffle(elems)
        for elem, rank in zip(elems, range(1,len(elems))):
            line = columndelim.join([elem.sectionId, "Q0", elem.paraId, str(rank), str(1.0/rank), "mock"])
            runwriter.write(line + "\n")
    runwriter.close()

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Mock  dont use")
    parser.add_argument('train', type=argparse.FileType('r'), help='Input path for training data')
    parser.add_argument('test', type=argparse.FileType('r'), help='Input path for test data')
    parser.add_argument('run', type=argparse.FileType('w'), help='Output path for run file (rankings)')
    parser.add_argument('--maxentries', type=int, help='max number of articles to include')
    args = parser.parse_args()

    # testdata =\
    load_input (args.test, args.run, args.maxentries)
    # write_mock_rankings(testdata, args.run)


if __name__ == '__main__':
    main()