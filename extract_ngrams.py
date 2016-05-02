#! /usr/bin/env python
# -*- coding: utf-8 -*

import sys
import string
import argparse
from collections import Counter

PUNCT = set(list(string.punctuation))


def make_term_simple(token):
    return token.lower().strip(string.punctuation)


def is_good_term(term):
    return not (term.isspace() or all([ch in PUNCT for ch in term]))


def extraxt_ngrams(line, n):
    terms = map(make_term_simple, line.split(' '))
    terms = filter(is_good_term, terms)
    ngrams = []
    for i in xrange(len(terms) - n + 1):
        ngrams.append(terms[i:i+n])
    return ngrams


def parse_args():
    parser = argparse.ArgumentParser(description='Extract ngrams')
    parser.add_argument('-n', '--ngrams', required=True, type=int)
    return parser.parse_args()


def main():
    args = parse_args()
    cnt = Counter()
    for line in sys.stdin:
        ngrams = extraxt_ngrams(line.strip().decode('utf8'), args.ngrams)
        for ngram in ngrams:
            key = ' '.join(ngram)
            cnt[key] += 1

    for key in sorted(cnt, key=lambda x: cnt[x], reverse=True):
        print '\t'.join([key, str(cnt[key])]).encode('utf8')

if __name__ == "__main__":
    main()
