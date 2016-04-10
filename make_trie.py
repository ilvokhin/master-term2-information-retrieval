#! /usr/bin/env python
# -*- coding: utf-8 -*

import argparse
from common import time_exec
from common import load_index
from make_index import save_index

class Trie(object):
  def __init__(self):
    self.nodes = [{}]

  def add(self, key):
    cur = 0
    for char in key:
      node = self.nodes[cur]
      if not char in node:
        # add new one
        next_pos = len(self.nodes)
        node[char] = next_pos
        self.nodes.append({})
      cur = node[char]

  def find_all_suffixes(self, pos, prefix):
    to = self.nodes[pos]
    if not to:
      # strip $-sign
      return [prefix[:-1:]]
    out = []
    for ch in to:
      cur_suffs = self.find_all_suffixes(to[ch], prefix + ch)
      out.extend(cur_suffs)
    return out

  def find(self, key):
    cur = 0
    for char in key:
      node = self.nodes[cur]
      if not char in node:
        return []
      cur = node[char]
    return self.find_all_suffixes(cur, key)

def parse_args():
  parser = argparse.ArgumentParser(description = \
    'Make trie and reverse trie from index')
  parser.add_argument('-i', '--index', help = 'index file', required  = True)
  parser.add_argument('-d', '--dst', help = 'destination file path', required = True)
  return parser.parse_args()

def main():
  args = parse_args()
  index = time_exec(load_index)(args.index)

  trie = Trie()
  reverse_trie = Trie()
  for key in index:
    trie.add(key + '$')
    reverse_trie.add(key[::-1] + '$')

  save_index((trie, reverse_trie), args.dst)

if __name__ == "__main__":
  main()
