#! /usr/bin/env python
# -*- coding: utf-8 -*

import sys
import argparse
from common import time_exec
from common import load_index
from common import make_term_no_stem

def doc_id(posting):
  return posting[0]

def term_entries(posting):
  return posting[1]

def make_and_dist(docs_x, docs_y, dist):
  x = 0
  y = 0
  docs = []
  while x < len(docs_x) and y < len(docs_y):
    if doc_id(docs_x[x]) == doc_id(docs_y[y]):
      matches = []
      entries_x = term_entries(docs_x[x])
      entries_y = term_entries(docs_y[y])
      xx = 0
      yy = 0
      while xx < len(entries_x) and yy < len(entries_y):
        if entries_x[xx] + dist == entries_y[yy]:
          # we always want have entry position of first word
          matches.append(entries_x[xx])
          xx += 1
          yy += 1
        elif entries_x[xx] + dist < entries_y[yy]:
          xx += 1
        else:
          yy += 1
      if matches:
        docs.append((doc_id(docs_x[x]), matches))
      x += 1
      y += 1
    elif doc_id(docs_x[x]) < doc_id(docs_y[y]):
      x += 1
    else:
      y += 1
  return docs

def make_query(query, index):
  terms = [make_term_no_stem(token) for token in query.split()]
  docs = index[terms[0]]
  for pos in xrange(1, len(terms)):
    docs = make_and_dist(docs, index[terms[pos]], pos)
  return docs

def parse_query(s):
  return s.strip('"')

def parse_args():
  parser = argparse.ArgumentParser(description = 'Cite coordinate search')
  parser.add_argument('-i', '--index', help = 'index file path', required  = True)
  return parser.parse_args()

def main():
  args = parse_args()
  index = time_exec(load_index)(args.index)

  for line in sys.stdin:
    query = parse_query(line.decode('utf8').strip())
    docs = make_query(query, index)
    print 'query "%s": found %d docs, %s' % (query, len(docs), docs)

if __name__ == "__main__":
  main()
