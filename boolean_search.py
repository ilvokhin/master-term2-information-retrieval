#! /usr/bin/env python
# -*- coding: utf-8 -*

import ast

def make_and(docs_x, docs_y, index):
  return sorted(set(docs_x).intersection(docs_y))

def make_or(docs_x, docs_y, index):
  return sorted(set(docs_x + docs_y))

def make_not(docs, index):
  # not very effective code here
  all_docs = sum(index.values(), [])
  return sorted(set(all_docs).difference(docs))

class EvalQuery(ast.NodeTransformer):
  def __init__(self, index):
    self.index = index

  def visit_BoolOp(self, node):
    self.generic_visit(node)
    
    vals = [val for val in node.values if isinstance(val, ast.Name)]
    vals.sort(key = lambda x: x.weight)

    op = make_or if node.op == ast.Or() else make_and
    docs = vals[0].docs

    for child in vals[1::]:
      docs = op(docs, child.docs, self.index)

    new_node = ast.Name(id = 'tmp', ctx = ast.Load())
    new_node.docs = docs
    new_node.weight = len(new_node.docs)
    return new_node

  def visit_UnaryOp(self, node):
    self.generic_visit(node)
 
    new_node = ast.Name(id = 'tmp', ctx = ast.Load())
    new_node.docs = make_not(node.operand.docs, self.index)
    new_node.weight = len(new_node.docs)
    return new_node

  def visit_Name(self, node):
    node.docs = self.index[node.id]
    node.weight = len(node.docs)
    return node

def main():
  tree = ast.parse("(cesar and brutus and not calpurnia)")
  print ast.dump(tree)
  op = EvalQuery({'cesar' : [1, 2, 3], 'brutus' : [2, 4], 'calpurnia' : [1, 2, 4, 5]})
  op.visit(tree)
  print ast.dump(tree)

  for node in ast.walk(tree):
    if isinstance(node, ast.Name):
      print node.docs

if __name__ == "__main__":
  main()
