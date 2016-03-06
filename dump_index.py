#! /usr/bin/env python
# -*- coding: utf-8 -*

import gzip
import argparse
import cPickle as pickle
from common import load_index
from common import DOCS_CNT_KEY

def dump_index(index, dst):
  with open(dst, 'w') as f:
    index.pop(DOCS_CNT_KEY)
    for term in sorted(index, key = lambda x: len(index[x]), reverse = True):
      docs = index[term]
      f.write('%s\t%d\t%s\n' % (term.encode('utf8'), len(docs), str(docs)))

def parse_args():
  parser = argparse.ArgumentParser(description = 'Dump index as text file')
  parser.add_argument('-s', '--src', help = 'source file path', required  = True)
  parser.add_argument('-d', '--dst', help = 'destination file path', required = True)
  return parser.parse_args()

def main():
  args = parse_args()
  index = load_index(args.src)
  dump_index(index, args.dst)

if __name__ == "__main__":
  main()
