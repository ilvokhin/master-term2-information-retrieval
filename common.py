#! /usr/bin/env python
# -*- coding: utf-8 -*

import sys
import gzip
import timeit
import cPickle as pickle

DOCS_CNT_KEY = '__docs_cnt'

def time_exec(func):
  def wrapper(*args, **kwargs):
    s = timeit.default_timer()
    out = func(*args, **kwargs)
    f = timeit.default_timer()
    print '%s takes %f sec' % (func.__name__, f - s)
    sys.stdout.flush()
    return out
  return wrapper

def lemmatize(token):
  # can't find russian lemmatizer quickly, so nothing to do here yet
  return token

def normalize(token):
  return token.lower()

def make_term(token, stem = False):
  if stem:
    return lemmatize(normalize(token))
  else:
    return normalize(token)

def load_index(filename):
  with gzip.open(filename, 'rb') as f:
    return pickle.load(f)
