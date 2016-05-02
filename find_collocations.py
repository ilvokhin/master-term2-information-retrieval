#! /usr/bin/env python
# -*- coding: utf-8 -*

import sys
import argparse
from collections import Counter

import scipy.stats
from nltk.corpus import stopwords

RU_STOPWORDS = set(stopwords.words('russian'))


def calc_t_value(sample_mean, theoretical_mean, sample_size):
    # We have Bernoulli distribution here, so sample variance
    # is p(1 - p). This value approximated by just p in slides.
    sample_var = sample_mean * (1. - sample_mean)
    return (sample_mean - theoretical_mean) / (sample_var / sample_size)**0.5


def find_collocations(bigrams, unigrams, alpha):
    bigrams_cnt = 1. * sum([bigrams[key] for key in bigrams])
    good_collocations = []
    critical_t_value = scipy.stats.t.isf(alpha, bigrams_cnt)
    for bigram in bigrams:
        first, second = bigram.split(' ')
        if first in RU_STOPWORDS or second in RU_STOPWORDS:
            continue
        prob_first = unigrams[first] / bigrams_cnt
        prob_second = unigrams[second] / bigrams_cnt
        prob_bigram = bigrams[bigram] / bigrams_cnt
        t = calc_t_value(prob_bigram, prob_first * prob_second, bigrams_cnt)
        if t > critical_t_value:
            good_collocations.append((t, bigram))
    return good_collocations


def load_counters(filename):
    with open(filename) as f:
        cnt = Counter()
        for line in f:
            k, v = line.decode('utf8').split('\t')
            cnt[k] += int(v)
        return cnt


def parse_args():
    parser = argparse.ArgumentParser(description='Find collocations')
    parser.add_argument('-b', '--bigrams', required=True)
    parser.add_argument('-u', '--unigrams', required=True)
    parser.add_argument('-a', '--alpha', required=True, type=float)
    return parser.parse_args()


def main():
    args = parse_args()
    bigrams = load_counters(args.bigrams)
    unigrams = load_counters(args.unigrams)

    collocations = find_collocations(bigrams, unigrams, args.alpha)
    for t, bigram in sorted(collocations, key=lambda x: x[0], reverse=True):
        first, second = bigram.split(' ')
        first_cnt = str(unigrams[first])
        second_cnt = str(unigrams[second])
        bigram_cnt = str(bigrams[bigram])
        print '\t'.join([str(t), first_cnt, second_cnt, bigram_cnt,
                         bigram]).encode('utf8')

if __name__ == "__main__":
    main()
