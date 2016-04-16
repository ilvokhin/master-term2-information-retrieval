#! /usr/bin/env python
# -*- coding: utf-8 -*

import argparse
from make_index import parse_file

def enumerate_docs(src):
  raw_docs = parse_file(src).find_all('dd')
  out = []
  for doc_id, doc in enumerate(raw_docs):
    out.append((doc_id, doc.text.replace('\n', ' ').encode('utf8')))
  return out

def save_nums(nums, dst):
  with open(dst, 'w') as f:
    for elem in nums:
      f.write('%d\t%s\n' % elem)

def parse_args():
  parser = argparse.ArgumentParser(description = 'Enumerate docs')
  parser.add_argument('-s', '--src', help = 'source file path', required  = True)
  parser.add_argument('-d', '--dst', help = 'destination file path', required = True)
  return parser.parse_args()

def main():
  args = parse_args()
  nums = enumerate_docs(args.src)
  save_nums(nums, args.dst)

if __name__ == "__main__":
  main()
