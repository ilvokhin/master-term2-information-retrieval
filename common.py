#! /usr/bin/env python
# -*- coding: utf-8 -*

import sys
import gzip
import timeit
import cPickle as pickle
from nltk.stem.snowball import RussianStemmer

DOCS_CNT_KEY = '__docs_cnt'
NGRAMS_DELIM = '_'

def time_exec(func):
  def wrapper(*args, **kwargs):
    s = timeit.default_timer()
    out = func(*args, **kwargs)
    f = timeit.default_timer()
    print '%s takes %f sec' % (func.__name__, f - s)
    sys.stdout.flush()
    return out
  return wrapper

def count_calls(func):
  def wrapper(*args, **kwargs):
    wrapper.call_counter += 1
    return func(*args, **kwargs)
  wrapper.call_counter = 0
  wrapper.__name__ = func.__name__
  return wrapper

def count_calls_other(other):
  def decorator(func):
    def wrapper(*args, **kwargs):
      other.call_counter = 0
      try:
        return func(*args, **kwargs)
      finally:
        print '%s was called %d times' % (other.__name__, other.call_counter)
    wrapper.__name__ = func.__name__
    return wrapper
  return decorator

def stem(token):
  if not hasattr(stem, 'stemmer'):
    stem.stemmer = RussianStemmer()
  return stem.stemmer.stem(token)

def normalize(token):
  return token.lower()

def make_term(token, need_stemming = True):
  if need_stemming:
    return stem(normalize(token))
  else:
    return normalize(token)

def make_term_no_stem(token):
  return make_term(token, False)

def load_index(filename):
  with gzip.open(filename, 'rb') as f:
    return pickle.load(f)
