from typing import List, Set

from trec_car.read_data import *
import itertools
import random
import string





printable = set(string.printable)

def flatten_paras_with_section_path(page:Page):
    def flatten_children(prefix: List[str], prefixName:List[str], skel:PageSkeleton):
        if isinstance(skel, Para):
            if len(cleanParagraphText(skel.paragraph.get_text()))>10:
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

def keyfun(sectionpath, paraid)->str :
   key= paraid+str(tuple(sectionpath))
   return key

PUNKT = {'.',';','?','!','(',')','-','+','$','%','&','*','@','<','>','=','_','"'}
def cleanParagraphText(text:str):
    global PUNKT
    return ''.join([c
             if str(c).isalpha() or str(c).isdigit() or c in PUNKT
             else ' '
             for c in text
             if c.isprintable and c not in {'\n','\t','\''}])
    # return text.replace("[^A-Za-z01-9\.,;?\(\)-\/]"," ").replace("\n","").replace("[\s]+"," ")


def write_output(query_reader,  paragraph_reader, train_writer, test_writer, max_entries = None, rel = False, segmentpath = False):

    class RandomParas():
        def __init__(self, paragraph_reader):
            self.random_paragraphs = list(itertools.islice(iter_paragraphs(paragraph_reader),0,1000))
            self.r_idx = 0

        def nextIndex(self):
            if (self.r_idx+1) >= len(self.random_paragraphs):
                self.r_idx = 0

            next = self.random_paragraphs[self.r_idx]
            self.r_idx +=1
            return next

        def get_k(self, k:int, forbidden_para_ids:Set[str])-> Set[Paragraph]:
            result = set()
            while len(result) < k:
                next = self.nextIndex()
                while next.para_id in forbidden_para_ids:
                    next = self.nextIndex()
                result.add(next)
            return result
    random_paras = RandomParas(paragraph_reader)

    def sectionPathToQuery(sectionnames:List[str])-> str:
        tokenizedPaths = [queryTokenize(path) for path in sectionnames]
        if segmentpath:
            return ' // '.join(tokenizedPaths)
        else:
            return ' '.join(tokenizedPaths)




    for page in itertools.islice(iter_annotations(query_reader), 0, max_entries):
        parasDict = {keyfun(sectionpath, para.para_id): (tuple(sectionpath), sectionNames, para) for (sectionpath, sectionNames, para) in flatten_paras_with_section_path(page)}

        paras = list(parasDict.values())   # discard duplicate paragraph ids
        paras_in_this_page = set({p.para_id for (sectionpath, sectionnames, p) in paras})

        if len(paras)>1:
            sectionpaths = {sectionpath: sectionnames for (sectionpath, sectionnames, p) in paras}

            if train_writer is not None:
                # train data
                for (trueSectionPath, sectionPathName, paragraph) in paras:
                    sectionNameTokenized = sectionPathToQuery(sectionpaths[trueSectionPath])
                    negatives = [cleanParagraphText(p.get_text()) for (sectionpath_, sectionnames_, p) in paras if sectionpath_ != trueSectionPath ]
                    randomparas = [cleanParagraphText(p.get_text()) for p in random_paras.get_k(4, paras_in_this_page) ]
                    if len(negatives) >= 4:
                        random.shuffle(negatives)
                        train_writer.write("\t".join([ sectionNameTokenized
                                        , cleanParagraphText(paragraph.get_text())
                                        ]+negatives[0:4]+randomparas) + "\n")

            # test data
            random.shuffle(paras)

            relinfo=""
            if test_writer is not None:
                randomparas = list(random_paras.get_k(4, paras_in_this_page))  # paragraphs from other pages
                for sectionPath in sectionpaths:
                    # sectionName = ' '.join(sectionpaths[sectionPath])
                    sectionId =  '/'.join(sectionPath)
                    # queryTokenized = queryTokenize(sectionName)
                    queryTokenized = sectionPathToQuery(sectionpaths[sectionPath])


                    for (trueSectionPath, tsn, paragraph) in paras:
                        if rel:
                            relinfo = str(1) if trueSectionPath == sectionPath else str(0)
                        test_writer.write("\t".join([sectionId
                                        , queryTokenized
                                        , paragraph.para_id
                                        , cleanParagraphText(paragraph.get_text())
                                        , relinfo
                                        ])+"\n")

                    for paragraph in randomparas:
                        if rel:
                            relinfo=str(0)
                        test_writer.write("\t".join([sectionId
                                        , queryTokenized
                                        , paragraph.para_id
                                        , cleanParagraphText(paragraph.get_text())
                                        , relinfo
                                        ])+"\n")
    if train_writer is not None: train_writer.close()
    if test_writer is not None: test_writer.close()

description = """
Glue code for TREC CAR and the Duet Model
"""

def main():
    import argparse
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('query_cbor', type=argparse.FileType('rb'), help='Input articles cbor file')
    parser.add_argument('paragraph_cbor', type=argparse.FileType('rb'), help='Input paragraphs cbor file data')
    parser.add_argument('--train', type=argparse.FileType('w'), help='Output path for training data')
    parser.add_argument('--test', type=argparse.FileType('w'), help='Output path for test data')
    parser.add_argument('--maxentries', type=int, help='max number of articles to include')
    parser.add_argument('--relevance', help='if given, relevance info in written to test', action='store_true', default=False)
    parser.add_argument('--segmentpath', help='if given, segment section path', action='store_true', default=False)
    args = parser.parse_args()



    random.seed(0)
    print("loading queries from ", args.query_cbor.name)
    write_output(args.query_cbor, args.paragraph_cbor, args.train, args.test, args.maxentries, args.relevance, args.segmentpath)

if __name__ == '__main__':
    main()