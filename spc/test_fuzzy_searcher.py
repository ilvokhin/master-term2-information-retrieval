#! /usr/bin/env python
# -*- coding: utf-8 -*

import sys
import argparse

import trie
from trie import Trie
from trie import FuzzySearcher


def parse_args():
    parser = argparse.ArgumentParser(description='Test fuzzy searcher')
    parser.add_argument('-s', '--src', required=True)
    return parser.parse_args()


def main():
    args = parse_args()
    fuzzy_searcher = trie.load_trie(args.src)

    for line in sys.stdin:
        key = line.decode('utf8').strip()
        candidates = fuzzy_searcher.find(key)
        for candidate in sorted(candidates, key=lambda x: x[1], reverse=True):
            word, weight, err = candidate
            print '\t'.join([word, str(weight), str(err)]).encode('utf8')

if __name__ == "__main__":
    main()
