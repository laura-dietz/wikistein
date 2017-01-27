from typing import List

from trec_car.read_data import *
import itertools
import sys
from typing import *
import random
import string

printable = set(string.printable)

if len(sys.argv)<3:
    print("usage ",sys.argv[0]," cbor train_out test_out")
    exit()

query_cbor=sys.argv[1]
train_out=sys.argv[2]
test_out=sys.argv[3]
max_entries=int(sys.argv[4])


print("loading queries from ", query_cbor)


def flatten_paras_with_section_path(page:Page):
    def flatten_children(prefix: List[str], prefixName:List[str], skel:PageSkeleton):
        if isinstance(skel, Para):
            if len(skel.paragraph.get_text())>10:
                yield (prefix, prefixName, skel.paragraph)
        elif isinstance(skel, Section):
            new_prefix = prefix + [skel.headingId]
            new_prefix_name = prefixName + [skel.heading]
            for child in skel.children:
                yield from flatten_children(new_prefix, new_prefix_name, child)
        else:
            raise BaseException("Unknown page skeleton ",skel)

    for skel in page.skeleton:
        yield from flatten_children([page.page_id], [page.page_name], skel)


def queryTokenize(text:str):
    return ''.join([ c  if str(c).isalnum() else ' ' for c in text if c.isprintable()])


with open(train_out, 'w') as train_writer:
    with open(test_out, 'w') as test_writer:


        with open(query_cbor, 'rb') as f:
            for page in itertools.islice(iter_annotations(f), 0, max_entries):
                paras = list([(tuple(sectionpath), sectionNames, para) for (sectionpath, sectionNames, para) in flatten_paras_with_section_path(page)])

                if len(paras)>1:
                    sectionpaths = {sectionpath: sectionnames for (sectionpath, sectionnames, p) in paras}
                    # train data

                    for (trueSectionPath, sectionPathName, paragraph) in paras:
                        sectionName = ' '.join(sectionpaths[trueSectionPath])
                        negatives = [p.get_text() for (sectionpath_, sectionnames_, p) in paras if sectionpath_ != trueSectionPath ]
                        if len(negatives) >= 4:
                            random.shuffle(negatives)

                            train_writer.write("\t".join([ queryTokenize(sectionName)
                                            , paragraph.get_text()
                                            ]+negatives[0:4]) + "\n")


                    # test data
                    random.shuffle(paras)

                    for sectionPath in sectionpaths:
                        sectionName = ' '.join(sectionpaths[sectionPath])
                        sectionId =  '/'.join(sectionPath)
                        for (trueSectionPath, tsn, paragraph) in paras:
                            test_writer.write("\t".join([sectionId
                                            , queryTokenize(sectionName)
                                            , paragraph.para_id
                                            , paragraph.get_text()
                                            , str(1) if trueSectionPath == sectionPath else str(0)
                                            ])+"\n")



