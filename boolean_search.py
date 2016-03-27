#! /usr/bin/env python
# -*- coding: utf-8 -*

import re
import sys
import ast
import argparse
from common import make_term
from common import time_exec
from common import load_index
from common import count_calls
from common import DOCS_CNT_KEY
from common import NGRAMS_DELIM
from common import count_calls_other

def make_and(docs_x, docs_y, index):
  return sorted(set(docs_x).intersection(docs_y))

@count_calls
def less(x, y):
  return x < y

@count_calls
def equal(x, y):
  return x == y

def le(x, y):
  return less(x, y) or equal(x, y)

@count_calls_other(less)
@count_calls_other(equal)
def make_and_simple(docs_x, docs_y, index):
  x = 0
  y = 0
  out = []
  while less(x, len(docs_x)) and less(y, len(docs_y)):
    if equal(docs_x[x], docs_y[y]):
      out.append(docs_x[x])
      x += 1
      y += 1
    elif less(docs_x[x], docs_y[y]):
      x += 1
    else:
      y += 1
  return out

def make_period(docs):
  return int(len(docs)**0.5)

def has_skip(docs, pos):
  period = make_period(docs)
  if pos % period == 0:
    return True
  return False

def skip(docs, pos):
  period = make_period(docs)
  return min(len(docs) - 1, pos + period)

@count_calls_other(less)
@count_calls_other(equal)
def make_and_skips(docs_x, docs_y, index):
  x = 0
  y = 0
  out = []
  while less(x, len(docs_x)) and less(y, len(docs_y)):
    if equal(docs_x[x], docs_y[y]):
      out.append(docs_x[x])
      x += 1
      y += 1
    elif less(docs_x[x], docs_y[y]):
      if has_skip(docs_x, x) and le(docs_x[skip(docs_x, x)], docs_y[y]):
        while has_skip(docs_x, x) and le(docs_x[skip(docs_x, x)], docs_y[y]):
          x = skip(docs_x, x)
      else:
        x += 1
    else:
      if has_skip(docs_y, y) and le(docs_y[skip(docs_y, y)], docs_x[x]):
        while has_skip(docs_y, y) and le(docs_y[skip(docs_y, y)], docs_x[x]):
          y = skip(docs_y, y)
      else:
        y += 1
  return out

def make_or(docs_x, docs_y, index):
  return sorted(set(docs_x + docs_y))

def make_not(docs, index):
  if not hasattr(make_not, 'all_docs'):
    make_not.all_docs = range(index[DOCS_CNT_KEY])
  return sorted(set(make_not.all_docs).difference(docs))

def make_and_func(and_algo):
  if and_algo == 'default':
    return make_and
  elif and_algo == 'simple':
    return make_and_simple
  elif and_algo == 'skips':
    return make_and_skips
  else:
    raise Exception('unknown and algorithm')

class EvalQuery(ast.NodeTransformer):
  def __init__(self, index, and_algo):
    self.index = index
    self.and_algo = and_algo

  def visit_BoolOp(self, node):
    self.generic_visit(node)
    
    vals = [val for val in node.values if isinstance(val, ast.Str)]
    vals.sort(key = lambda x: x.weight)

    op = make_or if isinstance(node.op, ast.Or) else make_and_func(self.and_algo)
    docs = vals[0].docs

    for child in vals[1::]:
      docs = op(docs, child.docs, self.index)

    new_node = ast.Str(s = 'tmp', ctx = ast.Load())
    new_node.docs = docs
    new_node.weight = len(new_node.docs)
    return new_node

  def visit_UnaryOp(self, node):
    self.generic_visit(node)
 
    new_node = ast.Str(s = 'tmp', ctx = ast.Load())
    new_node.docs = make_not(node.operand.docs, self.index)
    new_node.weight = len(new_node.docs)
    return new_node

  def visit_Str(self, node):
    term = make_term(node.s.decode('utf8'), False)
    if len(term.split(NGRAMS_DELIM)) == 1:
      # if term is't bigram, we should stem it
      term = make_term(term, True)
    node.docs = self.index[term]
    node.weight = len(node.docs)
    return node

def eval_query_tree(tree, index, and_algo):
  ops = EvalQuery(index, and_algo)
  ops.visit(tree)

  for node in ast.walk(tree):
    if isinstance(node, ast.Str):
      return node.docs

def quote_terms(query):
  # python doesn't work with unicode variables names,
  # so some hack here: wrap search terms in quotes
  return re.sub('((?![and|or|not])\w+)', r"'\1'", query, flags = re.UNICODE)

def parse_cite(query):
  m = re.search('"(.*?)"', query)
  if not m:
    return query
  cite_groups = m.groups()
  replace = []
  for cite in cite_groups:
    operands = []
    tokens = cite.split()
    for pos in xrange(len(tokens) - 1):
      token_a, token_b = tokens[pos], tokens[pos + 1]
      operands.append(token_a + NGRAMS_DELIM + token_b)
    repl = ' and '.join(operands)
    query = query.replace('"' + cite  + '"', repl)
  return query

@time_exec
def make_query(query, index, and_algo):
  tree = ast.parse(quote_terms(parse_cite(query.decode('utf8'))))
  docs = eval_query_tree(tree, index, and_algo)
  return docs

def parse_args():
  parser = argparse.ArgumentParser(description = 'Boolean search')
  parser.add_argument('-i', '--index', help = 'index file path', required  = True)
  parser.add_argument('-a', '--and-algo', help = 'algorithm for and op intersection', \
    choices = ['default', 'simple', 'skips'], default = 'default')
  return parser.parse_args()

def main():
  args = parse_args()
  index = time_exec(load_index)(args.index)

  for line in sys.stdin:
    query = line.strip('\n')
    docs = make_query(query, index, args.and_algo)
    print 'query "%s": found %d docs, %s' % (query, len(docs), docs)

if __name__ == "__main__":
  main()
