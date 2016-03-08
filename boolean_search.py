#! /usr/bin/env python
# -*- coding: utf-8 -*

import re
import sys
import ast
import argparse
from common import make_term
from common import time_exec
from common import load_index
from common import DOCS_CNT_KEY

def make_and(docs_x, docs_y, index):
  return sorted(set(docs_x).intersection(docs_y))

def make_or(docs_x, docs_y, index):
  return sorted(set(docs_x + docs_y))

def make_not(docs, index):
  if not hasattr(make_not, 'all_docs'):
    make_not.all_docs = range(index[DOCS_CNT_KEY])
  return sorted(set(make_not.all_docs).difference(docs))

class EvalQuery(ast.NodeTransformer):
  def __init__(self, index):
    self.index = index

  def visit_BoolOp(self, node):
    self.generic_visit(node)
    
    vals = [val for val in node.values if isinstance(val, ast.Str)]
    vals.sort(key = lambda x: x.weight)

    op = make_or if isinstance(node.op, ast.Or) else make_and
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
    term = make_term(node.s, False).decode('utf8')
    node.docs = self.index[term]
    node.weight = len(node.docs)
    return node

def eval_query_tree(tree, index):
  ops = EvalQuery(index)
  ops.visit(tree)

  for node in ast.walk(tree):
    if isinstance(node, ast.Str):
      return node.docs

def quote_terms(query):
  # python doesn't work with unicode variables names,
  # so some hack here: wrap search terms in quotes
  return re.sub('((?![and|or|not])\w+)', r"'\1'", query, flags = re.UNICODE)

@time_exec
def make_query(query, index):
  tree = ast.parse(quote_terms(query.decode('utf8')))
  docs = eval_query_tree(tree, index)
  return docs

def parse_args():
  parser = argparse.ArgumentParser(description = 'Boolean search')
  parser.add_argument('-i', '--index', help = 'index file path', required  = True)
  return parser.parse_args()

def main():
  args = parse_args()
  index = time_exec(load_index)(args.index)

  for line in sys.stdin:
    query = line.strip('\n')
    docs = make_query(query, index)
    print 'query "%s": found %d docs, %s' % (query, len(docs), docs)

if __name__ == "__main__":
  main()
