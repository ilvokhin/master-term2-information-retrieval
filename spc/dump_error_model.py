#! /usr/bin/env python
# -*- coding: utf-8 -*

import argparse

import error_model
from error_model import ErrorModel


def parse_args():
    parser = argparse.ArgumentParser(description='Dump error model')
    parser.add_argument('-s', '--src', required=True)
    return parser.parse_args()


def main():
    args = parse_args()
    em = error_model.load_error_model(args.src)

    for key in sorted(em.stat, key=lambda x: em.stat[x], reverse=True):
        print '\t'.join(key + (str(em.stat[key]),)).encode('utf8')

    for key in em.fix_cnt:
        print '\t'.join([key, str(em.fix_cnt[key])])

    print em.error_cnt

if __name__ == "__main__":
    main()
