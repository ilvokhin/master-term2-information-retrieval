#! /usr/bin/env python
# -*- coding: utf-8 -*

import argparse

import kneser_ney
from kneser_ney import KneserNey


def parse_args():
    parser = argparse.ArgumentParser(description='Test Kneser-Ney smothing')
    parser.add_argument('-s', '--src', required=True)
    parser.add_argument('-q', '--queries', required=True)
    return parser.parse_args()


def main():
    args = parse_args()
    kn = kneser_ney.load_kneser_ney(args.src)
    queries = kneser_ney.load_queries(args.queries)

    denum = 1.0 * sum([queries[key] for key in queries])
    val = kneser_ney.tune_single_step(kn, queries, kn.d, denum)

    print 'val: %f' % val

if __name__ == "__main__":
    main()
