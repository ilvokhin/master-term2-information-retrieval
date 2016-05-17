#! /usr/bin/env python
# -*- coding: utf-8 -*

import sys
import argparse

import trie
import kneser_ney
from trie import Trie
from viterbi import Viterbi
from viterbi import FixChain
from viterbi import Generator
from trie import FuzzySearcher
from kneser_ney import KneserNey


def spellcheck(generator, query, iteration):
    lm = generator.viterbi.lang_model
    fix = query
    smoothed_lang_weight = lm.calc_log_prob_phrase(fix, False)
    for i in xrange(iteration):
        cands = generator.make_candidates(fix)
        cands = sorted(cands, key=lambda x: x.calc_weight(), reverse=True)
        cur_fix = ' '.join(cands[0].phrase[1::])
        if(cur_fix != query and
           cands[0].smoothed_lang_weight > smoothed_lang_weight):
            fix = cur_fix
            # recalc lang weight without error
            smoothed_lang_weight = lm.calc_log_prob_phrase(fix, False)
    return fix


def parse_args():
    parser = argparse.ArgumentParser(description='Simple slow spellchecher')
    parser.add_argument('-t', '--trie', required=True)
    parser.add_argument('-l', '--lang-model', required=True)
    parser.add_argument('-i', '--iteration', required=True, type=int)
    return parser.parse_args()


def main():
    args = parse_args()

    fuzzy_searcher = trie.load_trie(args.trie)
    lang_model = kneser_ney.load_kneser_ney(args.lang_model)

    generator = Generator(fuzzy_searcher, Viterbi(lang_model))

    for line in sys.stdin:
        query = line.strip().decode('utf8')
        fix = spellcheck(generator, query, args.iteration)
        if fix == query:
            fix = ''
        print '\t'.join([query, fix]).encode('utf8')

if __name__ == "__main__":
    main()
