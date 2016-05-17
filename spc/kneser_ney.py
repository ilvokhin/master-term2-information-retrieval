#! /usr/bin/env python
# -*- coding: utf-8 -*

import sys
import random
import argparse
import string
from math import log
import cPickle as pickle
from collections import Counter

from extract_ngrams import normalize_query as normalize

SEED = 0
TUNE_STEP = 0.000001
UNKNOWN_WORD = '<unk>'


class KneserNey(object):
    def __init__(self, kn_after_word_cnt, kn_before_word_cnt,
                 kn_bigram_cnt, kn_unigram_cnt):
        self.kn_after_word_cnt = kn_after_word_cnt
        self.kn_before_word_cnt = kn_before_word_cnt
        self.kn_bigram_cnt = kn_bigram_cnt
        self.kn_unigram_cnt = kn_unigram_cnt
        self.kn_before_denum = 1.0 * sum([kn_before_word_cnt[key]
                                          for key in kn_before_word_cnt])
        self.d = 0.5

    def calc_lambda(self, word):
        num = self.d * self.kn_after_word_cnt[word]
        denum = self.kn_unigram_cnt[word]
        return 1.0 * num / denum

    def calc_p_cont(self, word):
        num = self.kn_before_word_cnt[word]
        return num / self.kn_before_denum

    def calc_prob_bigram(self, prev, cur):
        x = prev
        y = cur
        if prev not in self.kn_unigram_cnt:
            x = UNKNOWN_WORD
        if cur not in self.kn_unigram_cnt:
            y = UNKNOWN_WORD

        bigram = ' '.join([x, y])
        bi = max(self.kn_bigram_cnt[bigram] - self.d, 0.)
        bi /= self.kn_unigram_cnt[x]
        lambda_coef = self.calc_lambda(x)
        p_cont = self.calc_p_cont(y)

        return bi + lambda_coef * p_cont

    def calc_log_prob_phrase(self, phrase, use_last_santinel=True):
        words = ['^'] + phrase.split()
        if use_last_santinel:
            words.append('$')
        out = 0.
        for pos in xrange(len(words) - 1):
            cur_prob = self.calc_prob_bigram(words[pos], words[pos + 1])
            out += log(cur_prob, 2.)
        return out

    def calc(self, phrase):
        return self.calc_log_prob_phrase(phrase)

    def calc_bi(self, first, second):
        prob = self.calc_prob_bigram(first, second)
        return log(prob, 2)


def make_kneser_ney(unigrams, bigrams, oov_threshold, oov_percent):
    oov_candidates = [uni for uni in unigrams if unigrams[uni] < oov_threshold]
    random.seed(SEED)
    remove = random.sample(oov_candidates,
                           int(oov_percent * len(oov_candidates)))
    # collect Kneser-Ney stats
    kn_after_word_cnt = Counter()
    kn_before_word_cnt = Counter()
    kn_bigram_cnt = Counter()
    kn_unigram_cnt = Counter()

    for bi in bigrams:
        first, second = bi.split(' ')
        if first in remove:
            first = UNKNOWN_WORD
        if second in remove:
            second = UNKNOWN_WORD
        kn_after_word_cnt[first] += 1
        kn_before_word_cnt[second] += 1
        kn_bigram_cnt[' '.join([first, second])] += bigrams[bi]

    for uni in unigrams:
        if uni in remove:
            kn_unigram_cnt[UNKNOWN_WORD] += unigrams[uni]
        else:
            kn_unigram_cnt[uni] += unigrams[uni]

    return KneserNey(kn_after_word_cnt, kn_before_word_cnt,
                     kn_bigram_cnt, kn_unigram_cnt)


def tune_single_step(kn, queries, param, denum):
    kn.d = param
    out = 0
    for key in queries:
        orig, fix = key.split('\t', 1)
        orig_weight = kn.calc(orig)
        fix_weight = kn.calc(fix)
        out += (fix_weight > orig_weight) * queries[key]
    return 1.0 * out / denum


def stupid_tune_kneser_ney(kn, queries):
    denum = 1.0 * sum([queries[key] for key in queries])
    best_val = -1.
    best_d = -1.
    for factor in xrange(int(log(1. / TUNE_STEP, 10))):
        cur_d = 10**factor * TUNE_STEP
        cur_val = tune_single_step(kn, queries, cur_d, denum)
        print >> sys.stderr, '%f\t%f' % (cur_d, cur_val)
        if cur_val > best_val:
            best_d = cur_d
            best_val = cur_val

    assert(best_val != -1)
    assert(best_d != -1)

    print >> sys.stderr, 'best: %f\t%f' % (best_d, best_val)
    return best_d


def save_kneser_ney(kn, filename):
    with open(filename, 'wb') as f:
        pickle.dump(kn, f)


def load_kneser_ney(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f)


def load_ngrams(filename):
    with open(filename) as f:
        cnt = Counter()
        for line in f:
            k, v = line.decode('utf8').strip().split('\t')
            cnt[k] += int(v)
        return cnt


def load_queries(filename):
    with open(filename) as f:
        cnt = Counter()
        for line in f:
            orig, fix = line.decode('utf8').strip().split('\t')
            key = '\t'.join([normalize(orig), normalize(fix)])
            cnt[key] += 1
        return cnt


def check_percent(value):
    val = float(value)
    if 0. < val < 1.:
        return val
    raise argparse.ArgumentTypeError('%f should be in range (0, 1)')


def parse_args():
    parser = argparse.ArgumentParser(description='Make Kneser-Ney smothing')
    parser.add_argument('-u', '--unigrams', required=True)
    parser.add_argument('-b', '--bigrams', required=True)
    parser.add_argument('-t', '--threshold', required=True, type=int)
    parser.add_argument('-p', '--percent', required=True, type=check_percent)
    parser.add_argument('-q', '--queries', required=True)
    parser.add_argument('-d', '--dst', required=True)
    return parser.parse_args()


def main():
    args = parse_args()
    unigrams = load_ngrams(args.unigrams)
    bigrams = load_ngrams(args.bigrams)

    # calc stat
    kn = make_kneser_ney(unigrams, bigrams, args.threshold, args.percent)

    queries = load_queries(args.queries)
    # tune param
    kn.d = stupid_tune_kneser_ney(kn, queries)
    save_kneser_ney(kn, args.dst)

if __name__ == "__main__":
    main()
