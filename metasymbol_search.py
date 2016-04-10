#! /usr/bin/env python
# -*- coding: utf-8 -*

import sys
import argparse
from common import time_exec
from common import load_index
from boolean_search import make_or
from boolean_search import make_and
from make_trie import Trie

def make_query(query, index, tries):
  if not '*' in query:
    return [query], index[query]
  if query.count('*') > 1:
    raise Exception('only one asterics is allowed')
  trie, reverse_trie = tries
  pos = query.index('*')
  if pos == 0:
    terms = [elem[::-1] for elem in reverse_trie.find(query[1::][::-1])]
  elif pos == len(query) - 1:
    terms = trie.find(query[:-1:])
  else:
    head, tail = query.split('*')
    terms_forward = trie.find(head)
    terms_backward = [elem[::-1] for elem in reverse_trie.find(tail[::-1])]
    terms = make_and(terms_forward, terms_backward, None)
  docs = index[terms[0]]
  for term in terms[1::]:
    docs = make_or(docs, index[term], index)
  return terms, docs

def parse_args():
  parser = argparse.ArgumentParser(description = 'Metasymbol search')
  parser.add_argument('-i', '--index', help = 'index file', required  = True)
  parser.add_argument('-t', '--trie', help = 'trie file', required  = True)
  return parser.parse_args()

def main():
  args = parse_args()
  index = time_exec(load_index)(args.index)
  tries = time_exec(load_index)(args.trie)

  for line in sys.stdin:
    query = line.strip('\n')
    terms, docs = make_query(query.decode('utf8'), index, tries)
    print 'query "%s": found %d docs, %s' % (query, len(docs), docs)
    print 'found %d terms: [%s]' % \
      (len(terms), ', '.join(map(lambda x: x.encode('utf8'), terms)))

if __name__ == "__main__":
  main()
