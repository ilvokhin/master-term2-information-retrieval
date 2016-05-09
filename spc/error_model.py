#! /usr/bin/env python
# -*- coding: utf-8 -*

import sys
import argparse
from math import log
import cPickle as pickle
from collections import Counter

from extract_ngrams import normalize_query as normalize


class ErrorModel(object):
    def __init__(self, error_stat):
        self.stat = error_stat
        self.fix_cnt = Counter()
        self.error_cnt = 0.

        for error in self.stat:
            self.fix_cnt[error[0]] += self.stat[error]
            self.error_cnt += self.stat[error]

    def calc_log_prob_phrase(self, how, from_ch, to_ch):
        cur_fix = (how, from_ch, to_ch)
        # math breaks here: can't quickly come up with something
        # simple and correct
        prob = (self.fix_cnt[how] + self.stat[cur_fix]) / self.error_cnt
        assert(prob < 1.0)
        return prob

    def calc(self, how, from_ch, to_ch):
        return calc_log_prob_phrase(self, how, from_ch, to_ch)


def calc_lev_dist(src, dst):
    n = len(src)
    m = len(dst)
    dp = {}
    for i in xrange(n + 1):
        dp[i, 0] = i
    for j in xrange(m + 1):
        dp[0, j] = j
    for i in xrange(1, n + 1):
        for j in xrange(1, m + 1):
            dp[i, j] = min(dp[i - 1, j] + 1,
                           dp[i, j - 1] + 1,
                           dp[i - 1, j - 1]
                           + (src[i - 1] != dst[j - 1]))
    return dp


def calc_simple_errors(src, dst):
    dp = calc_lev_dist(src, dst)
    errors = []
    i = len(src)
    j = len(dst)
    while i >= 0 and j >= 0:
        if i > 0 and dp[i - 1, j] + 1 == dp[i, j]:
            errors.append(('D', src[i - 1], ''))
            i -= 1
        elif j > 0 and dp[i, j - 1] + 1 == dp[i, j]:
            errors.append(('I', '', dst[j - 1]))
            j -= 1
        elif i > 0 and j > 0:
            if dp[i - 1, j - 1] + 1 == dp[i, j]:
                errors.append(('R', src[i - 1], dst[j - 1]))
            i -= 1
            j -= 1
        else:
            if i == j == 0:
                break
    return errors[::-1]


def save_error_model(em, filename):
    with open(filename, 'wb') as f:
        pickle.dump(em, f)


def load_error_model(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f)


def parse_args():
    parser = argparse.ArgumentParser(description='Make error model')
    parser.add_argument('-d', '--dst', required=True)
    return parser.parse_args()


def main():
    args = parse_args()
    cnt = Counter()
    for line in sys.stdin:
        orig, fix = map(normalize, line.strip().decode('utf8').split('\t', 1))
        errors = calc_simple_errors(orig, fix)
        for error in errors:
            cnt[error] += 1

    em = ErrorModel(cnt)
    save_error_model(em, args.dst)

if __name__ == "__main__":
    main()
