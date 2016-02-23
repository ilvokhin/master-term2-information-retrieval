#! /usr/bin/env python
# -*- coding: utf-8 -*

import sys
import bs4
import nltk
import gzip
import timeit
import argparse
import string
import cPickle as pickle
from collections import Counter
from collections import defaultdict

PUNCT = set(list(string.punctuation) + ['--', '...', '``', '\'\''])

def time_exec(func):
  def wrapper(*args, **kwargs):
    s = timeit.default_timer()
    out = func(*args, **kwargs)
    f = timeit.default_timer()
    print '%s takes %f sec' % (func.__name__, f - s)
    return out
  return wrapper

def parse_file(filename):
  with open(filename) as f:
    # there are not closed <dd> tag, so we should use parser, which
    # can handle it.
    return bs4.BeautifulSoup(f, 'html5lib', from_encoding='utf8')

def lemmatize(token):
  # can't find russian lemmatizer quickly, so nothing to do here yet
  return token

def normalize(token):
  return token.lower()

def make_term(token):
  return lemmatize(normalize(token))

def print_stat(stat):
  print 'Index stat:'
  for cnt in stat:
    print '%s: %d' % (cnt, stat[cnt])

def collect_stat_per_doc(stat, tokens, terms):
  stat['tokens'] += len(tokens)
  stat['terms'] += len(terms)

def collect_stat_final(stat, docs, index):
  stat['docs'] = len(docs)
  stat['uniq_terms'] = len(index)

@time_exec
def make_index(src):
  stat = Counter()
  docs = parse_file(src).find_all('dd')
  index = defaultdict(list)

  for doc_id, doc in enumerate(docs):
    tokens = nltk.word_tokenize(doc.text)
    terms = filter(lambda t: not t in PUNCT, map(make_term, tokens))
    for term in set(terms):
      index[term].append(doc_id)
    collect_stat_per_doc(stat, tokens, terms)

  collect_stat_final(stat, docs, index)
  print_stat(stat)
  return index

@time_exec
def save_index(index, dst):
  with gzip.open(dst, 'wb') as f:
    pickle.dump(index, f)

def parse_args():
  parser = argparse.ArgumentParser(description = 'Make index from raw shtml file')
  parser.add_argument('-s', '--src', help = 'source file path', required  = True)
  parser.add_argument('-d', '--dst', help = 'destination file path', required = True)
  return parser.parse_args()

def main():
  args = parse_args()
  index = make_index(args.src)
  save_index(index, args.dst)

if __name__ == "__main__":
  main()
