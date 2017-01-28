from typing import List

from trec_car.read_data import *
import itertools
import sys
import random
import string

printable = set(string.printable)

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


def write_output(query_reader, train_writer, test_writer, max_entries = None):
    for page in itertools.islice(iter_annotations(query_reader), 0, max_entries):
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
    train_writer.close()
    test_writer.close()

description = """
Glue code for TREC CAR and the Duet Model
"""

def main():
    import argparse
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('query_cbor', type=argparse.FileType('rb'), help='Input cbor file')
    parser.add_argument('train', type=argparse.FileType('w'), help='Output path for training data')
    parser.add_argument('test', type=argparse.FileType('w'), help='Output path for test data')
    parser.add_argument('--maxentries', type=int, help='max number of articles to include')
    args = parser.parse_args()

    print("loading queries from ", args.query_cbor.name)
    write_output(args.query_cbor, args.train, args.test, args.maxentries)

if __name__ == '__main__':
    main()