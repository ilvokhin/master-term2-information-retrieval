#! /usr/bin/env python
# -*- coding: utf-8 -*

import sys
import bs4
import nltk
import gzip
import argparse
import string
import cPickle as pickle
from common import make_term
from common import time_exec
from common import DOCS_CNT_KEY
from common import NGRAMS_DELIM
from collections import defaultdict
from common import make_term_no_stem
from common import make_defaultdict

PUNCT = set(list(string.punctuation) + ['--', '...', '``', '\'\''])


def parse_file(filename):
    with open(filename) as f:
        # there are not closed <dd> tag, so we should use parser, which
        # can handle it.
        return bs4.BeautifulSoup(f, 'html5lib', from_encoding='utf8')


def print_stat(stat):
    print 'Index stat:'
    for cnt in stat:
        print cnt, ':', stat[cnt]


def collect_stat_per_doc(stat, tokens):
    stat['avg_tokens_len'] += sum([len(tok) for tok in tokens])
    stat['tokens'] += len(tokens)


def collect_bigram_stat_per_doc(stat, tokens):
    stat['bigrams'] += ((len(tokens) - 1) * len(tokens)) / 2.


def collect_stat_final(stat, docs, index):
    stat['docs'] = len(docs)
    stat['terms'] = len(index)
    stat['avg_tokens_len'] /= 1. * stat['tokens']
    stat['avg_terms_len'] = 1. * sum([len(term)
                                      for term in index]) / len(index)


@time_exec
def make_index(src, bigrams=False):
    stat = defaultdict(float)
    index = defaultdict(list)
    docs = parse_file(src).find_all('dd')

    for doc_id, doc in enumerate(docs):
        tokens = nltk.word_tokenize(doc.text)
        terms = filter(lambda t: not t in PUNCT, map(make_term, tokens))
        for term in set(terms):
            index[term].append(doc_id)

        if bigrams:
            terms_no_stem = filter(lambda t: not t in PUNCT,
                                   map(make_term_no_stem, tokens))
            for pos in xrange(len(terms_no_stem) - 1):
                term_a, term_b = terms_no_stem[pos], terms_no_stem[pos + 1]
                term = term_a + NGRAMS_DELIM + term_b
                index[term].append(doc_id)
            collect_bigram_stat_per_doc(stat, terms_no_stem)

        collect_stat_per_doc(stat, tokens)
    # save max doc id for quick not in boolean search
    index[DOCS_CNT_KEY] = len(docs)
    collect_stat_final(stat, docs, index)
    print_stat(stat)
    return index


@time_exec
def make_coordinate_index(src):
    stat = defaultdict(float)
    tmp_index = defaultdict(make_defaultdict)
    docs = parse_file(src).find_all('dd')

    for doc_id, doc in enumerate(docs):
        tokens = nltk.word_tokenize(doc.text)
        terms = filter(lambda t: not t in PUNCT,
                       map(make_term_no_stem, tokens))
        for term_pos, term in enumerate(terms):
            tmp_index[term][doc_id].append(term_pos)
        collect_stat_per_doc(stat, tokens)

    index = defaultdict(list)

    for term in tmp_index:
        term_docs = tmp_index[term]
        postings = []
        for doc_id in sorted(term_docs.keys()):
            postings.append((doc_id, term_docs[doc_id]))
        index[term] = postings

    collect_stat_final(stat, docs, index)
    print_stat(stat)
    return index


@time_exec
def save_index(index, dst):
    with gzip.open(dst, 'wb') as f:
        pickle.dump(index, f)


def parse_args():
    parser = argparse.ArgumentParser(
        description='Make index from raw shtml file')
    parser.add_argument('-s', '--src', help='source file path', required=True)
    parser.add_argument(
        '-d', '--dst', help='destination file path', required=True)
    parser.add_argument('-i', '--index', help='index type',
                        choices=['default', 'bigrams', 'coordinates'], default='default')
    return parser.parse_args()


def main():
    args = parse_args()
    if args.index in ['default', 'bigrams']:
        index = make_index(args.src, args.index == 'bigrams')
    elif args.index == 'coordinates':
        index = make_coordinate_index(args.src)

    save_index(index, args.dst)

if __name__ == "__main__":
    main()
