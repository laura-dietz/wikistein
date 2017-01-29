from itertools import groupby
from typing import Dict, List

import itertools

QrelCollection = Dict[str, Dict[str, bool]]

class Qrel():
    def __init__(self, sectionid, paraid, rel_level:bool):
        self.sectionid = sectionid
        self.paraid = paraid
        self.rel_level = rel_level

def parse_qrels(line):
    splits = line.split(" ")
    return Qrel(splits[0], splits[2], int(splits[3])>0)

def load_qrels (qrels_reader) -> QrelCollection :
    qrelsdata = [parse_qrels(line) for line in qrels_reader]
    qrelsGrouped = groupby(qrelsdata, lambda elem: elem.sectionid)
    return {sectionid:
                {elem.paraid: elem.rel_level for elem in list}
            for sectionid, list in qrelsGrouped}


# =============
#     line = "\t".join([elem.sectionId, "Q0", elem.paraId, str(rank), str(1.0/rank), "mock"])
# runwriter.write(line + "\n")

class RankElem():
    def __init__(self, sectionId, paraId, rank:int, score:float, exp_name):
        self.sectionId = sectionId
        self.paraId = paraId
        self.rank = rank
        self.score = score
        self.exp_name = exp_name

class WithTruth():
    def __init__(self, elem:RankElem, is_truth:bool):
        self.elem = elem
        self.is_truth = is_truth


rankingWithZero = False

def parse_rankelem(line:str) -> RankElem:
    global rankingWithZero
    splits = line.split(" ")
    parsedrank = int(splits[3])

    if not rankingWithZero and (parsedrank == 0):
        rankingWithZero = True
        print("Warning: found rank 0, switching to zero-based rankings" )

    rank = parsedrank if not rankingWithZero else parsedrank +1

    return RankElem(splits[0], splits[2], rank, float(splits[4]), "")

def addTruth(qrels:QrelCollection, elem:RankElem)-> WithTruth :
    is_truth = qrels.get(elem.sectionId, False).get(elem.paraId, False)
    return WithTruth(elem, is_truth)

def load_rankings(qrelcollection, runreader) -> Dict[str, List[WithTruth]] :
    rankdata = [addTruth(qrelcollection, parse_rankelem(line)) for line in runreader]
    rankGrouped = groupby(rankdata, lambda elem: elem.elem.sectionId)
    return rankGrouped


#  ============================

class Eval():
    def __init__(self, mrr:float, p5:float, aveprec:float):
        self.mrr = mrr
        self.p5 = p5
        self.aveprec = aveprec

    def __str__(self, *args, **kwargs):
        return  "Eval(mrr="+str(self.mrr)+", p@5="+str(self.p5)+", map="+str(self.aveprec)+")"


def average_eval(evals: List[Eval], numQueries:int)->Eval:
    norm = 1.0/numQueries
    return Eval(mrr = norm*sum([e.mrr for e in evals])
            ,   p5 = norm*sum([e.p5 for e in evals])
            ,   aveprec = norm*sum([e.aveprec for e in evals])
            )


def compute_evaluation(qrelcollection:QrelCollection, rankings:Dict[str, List[WithTruth]]):
    def mrr(ranking:List[WithTruth])->float:
        for elem in ranking:
            if elem.is_truth:
                # print('mrr found rank', elem.elem.rank)
                return (1.0/ elem.elem.rank)
        return 0.0

    def p5(ranking:List[WithTruth])->float:
        hits = 0
        for elem in itertools.islice(ranking, 0, 5):
            if elem.is_truth:
                # print('p5 found rank', elem.elem.rank)
                hits += 1
        return 1.0*hits/5

    def aveprec(ranking:List[WithTruth], num_truths)->float:
        hits = 0
        sumscore = 0.0
        for elem in ranking:
            if elem.is_truth:
                hits +=1
                sumscore += 1.0 * hits/ elem.elem.rank
                # print( 'map fond at rank ',elem.elem.rank, ":  ", (1.0 * hits/ elem.elem.rank), "--> ",sumscore, "  -->  ", (sumscore/num_truths))
        return sumscore / num_truths


    def numTruths(sectionId):
        elemdict =  qrelcollection.get(sectionId, {})
        return sum([1 if elem else 0 for elem in elemdict.values()])


    def eval(sectionId, ranking:List[WithTruth])->Eval:
        ranking = list(ranking) # turn iterator into a list
        num_truth = numTruths(sectionId)

        return Eval(aveprec = aveprec(ranking, num_truths=num_truth),
                    mrr = mrr(ranking),
                    p5 = p5(ranking))


    eval = {key: eval(key, ranking)   for key, ranking in rankings} # attention: this ranking is actually an iterator!!!

    numQueries = len(qrelcollection)
    avgeval = average_eval(list(eval.values()), numQueries)

    return (avgeval, eval)

def perform_evaluation(qrels, run):
    qrelsCollection = load_qrels(qrels)
    rankingdata =load_rankings (qrelsCollection, run)
    return compute_evaluation(qrelsCollection, rankingdata)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Mock  dont use for anything but testing")
    parser.add_argument('qrels', type=argparse.FileType('r'), help='Input path for qrels (ground truth)')
    parser.add_argument('run', type=argparse.FileType('r'), help='Input path for run files')
    args = parser.parse_args()
    (avgeval, fulleval) = perform_evaluation(args.qrels, args.run)
    print (avgeval)
    print("\n")

    # for sectionId, eval in fulleval.items():
    #     print(sectionId,eval)


if __name__ == '__main__':
    main()