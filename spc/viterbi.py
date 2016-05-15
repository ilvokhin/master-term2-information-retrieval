#! /usr/bin/env python
# -*- coding: utf-8 -*

import sys
import argparse
from copy import deepcopy
from heapq import heappop, heappush

import trie
import kneser_ney
from trie import Trie
from trie import FuzzySearcher
from kneser_ney import KneserNey

from extract_ngrams import normalize


class FixChain(object):
    def __init__(self, phrase=[], raw_lw=0.0, smoothed_lw=0.0, ew=0.0):
        self.phrase = phrase
        self.raw_lang_weight = raw_lw
        self.smoothed_lang_weight = smoothed_lw
        self.error_weight = ew

    def calc_weight(self):  
        return self.smoothed_lang_weight + self.error_weight

    def __lt__(self, other):
        return self.calc_weight() < other.calc_weight()


class Viterbi(object):
    def __init__(self, lang_model):
        self.lang_model = lang_model

    def calc(self, phrase, heap_size=10):
        prev = [FixChain(['^'])]
        pq = []
        for candidates in phrase:
            for candidate in candidates:
                word, lang, err = candidate
                for prev_chain in prev:
                    cur_chain = deepcopy(prev_chain)
                    cur_chain.phrase.append(word)
                    cur_chain.raw_lang_weight += lang
                    bi_w = self.lang_model.calc_bi(prev_chain.phrase[-1], word)
                    cur_chain.smoothed_lang_weight += bi_w
                    cur_chain.error_weight += err
                    heappush(pq, cur_chain)
                    if len(pq) > heap_size:
                        heappop(pq)
            prev = list(pq)
            pq = []
        return prev


class Generator(object):
    def __init__(self, fuzzy_searcher, viterbi):
        self.fuzzy_searcher = fuzzy_searcher
        self.viterbi = viterbi

    def make_candidates(self, query, max_candidates=30):
        terms = normalize(query)
        candidates = []
        for term in terms:
            term_cands = self.fuzzy_searcher.find(term, -1)
            orig_weight = self.fuzzy_searcher.trie.find(term, 0.0)
            term_cands.append((term, orig_weight, 0.0))
            candidates.append(term_cands)

        phrase_candidates = self.viterbi.calc(candidates, max_candidates)
        return phrase_candidates


def parse_args():
    parser = argparse.ArgumentParser(description='Test Viterbi generator')
    parser.add_argument('-t', '--trie', required=True)
    parser.add_argument('-l', '--lang-model', required=True)
    return parser.parse_args()


def main():
    args = parse_args()

    fuzzy_searcher = trie.load_trie(args.trie)
    lang_model = kneser_ney.load_kneser_ney(args.lang_model)

    generator = Generator(fuzzy_searcher, Viterbi(lang_model))

    for line in sys.stdin:
        query = line.decode('utf8').strip()
        cands = generator.make_candidates(query)
        for candidate in sorted(cands, key=lambda x: x.calc_weight(),
                                reverse=True):
            fix = ' '.join(candidate.phrase[1::]).encode('utf8')
            attributes = [candidate.calc_weight(), candidate.raw_lang_weight,
                          candidate.error_weight,
                          candidate.smoothed_lang_weight]
            print '\t'.join([fix] + map(str, attributes))


if __name__ == "__main__":
    main()
