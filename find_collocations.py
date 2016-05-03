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


def find_collocations_student(bigrams, unigrams, alpha, prune):
    bigrams_cnt = 1. * sum([bigrams[key] for key in bigrams])
    good_collocations = []
    critical_t_value = scipy.stats.t.isf(alpha, bigrams_cnt)
    for bigram in bigrams:
        first, second = bigram.split(' ')
        if (first in RU_STOPWORDS or second in RU_STOPWORDS or
            bigrams[bigram] < prune):
            continue
        prob_first = unigrams[first] / bigrams_cnt
        prob_second = unigrams[second] / bigrams_cnt
        prob_bigram = bigrams[bigram] / bigrams_cnt
        t = calc_t_value(prob_bigram, prob_first * prob_second, bigrams_cnt)
        if t > critical_t_value:
            good_collocations.append((t, bigram))
    return good_collocations


def calc_chi2_value(first_freq, second_freq, bigram_freq, bigrams_cnt):
    table = [[0., 0.], [0., 0.]]
    # w_1 = first and w_2 == second
    table[0][0] = bigram_freq
    # w_1 != first and w_2 == second
    table[0][1] = second_freq - bigram_freq
    # w_1 == first and w_2 != second
    table[1][0] = first_freq - bigram_freq
    # w_1 != first and w_2 != second
    table[1][1] = bigrams_cnt - table[1][0] - table[0][1]
    num = 1. * bigrams_cnt * (table[0][0] * table[1][1]
                              - table[0][1] * table[1][0])**2
    denum = ((table[0][0] + table[0][1])
             * (table[0][0] + table[1][0])
             * (table[0][1] + table[1][1])
             * (table[1][0] + table[1][1]))
    return num / denum


def find_collocations_pearson(bigrams, unigrams, alpha, prune):
    bigrams_cnt = 1. * sum([bigrams[key] for key in bigrams])
    good_collocations = []
    critical_chi2_value = scipy.stats.chi2.isf(alpha, 1.)
    for bigram in bigrams:
        first, second = bigram.split(' ')
        if (first in RU_STOPWORDS or second in RU_STOPWORDS
            or bigrams[bigram] < prune):
            continue
        chi2 = calc_chi2_value(unigrams[first], unigrams[second],
                               bigrams[bigram], bigrams_cnt)
        if chi2 > critical_chi2_value:
            good_collocations.append((chi2, bigram))
    return good_collocations


def load_counters(filename):
    with open(filename) as f:
        cnt = Counter()
        for line in f:
            k, v = line.decode('utf8').split('\t')
            cnt[k] += int(v)
        return cnt


def make_find_func(func_name):
    if func_name == 'student':
        return find_collocations_student
    elif func_name == 'pearson':
        return find_collocations_pearson
    raise Exception('wrong func name: %d' % func_name)


def parse_args():
    parser = argparse.ArgumentParser(description='Find collocations')
    parser.add_argument('-b', '--bigrams', required=True)
    parser.add_argument('-u', '--unigrams', required=True)
    parser.add_argument('-a', '--alpha', required=True, type=float)
    parser.add_argument('-p', '--prune', type=int, default=10)
    parser.add_argument('-f', '--func', choices=['student', 'pearson'],
                        default='student')
    return parser.parse_args()


def main():
    args = parse_args()
    bigrams = load_counters(args.bigrams)
    unigrams = load_counters(args.unigrams)

    collocations = make_find_func(args.func)(bigrams, unigrams, args.alpha,
                                             args.prune)
    for t, bigram in sorted(collocations, key=lambda x: x[0], reverse=True):
        first, second = bigram.split(' ')
        first_cnt = str(unigrams[first])
        second_cnt = str(unigrams[second])
        bigram_cnt = str(bigrams[bigram])
        print '\t'.join([str(t), first_cnt, second_cnt, bigram_cnt,
                         bigram]).encode('utf8')

if __name__ == "__main__":
    main()
