#! /usr/bin/env python
# -*- coding: utf-8 -*

import nltk
import argparse
from make_index import PUNCT
from common import make_term
from make_index import parse_file
import matplotlib.pyplot as plt
from collections import Counter

def make_zipf(src):
  cnt = Counter()
  docs = parse_file(src).find_all('dd')
  for doc in docs:
    tokens = nltk.word_tokenize(doc.text)
    terms = filter(lambda t: not t in PUNCT, map(make_term, tokens))
    for term in terms:
      cnt[term] += 1
  return cnt

def make_plot(vals, filename, start, end, x_name, y_name):
  fig = plt.figure(1)
  pos = range(len(vals))
  # fair plot looks like shit, so cut it a little
  plot_pos = pos[start:end]
  plot_vals = vals[start:end]
  plt.plot(plot_pos, plot_vals, 'o', plot_pos, plot_vals)
  # add some labels
  plt.title(filename)
  plt.xlabel(x_name)
  plt.ylabel(y_name)
  plt.grid(True)

  plt.savefig(filename)

def parse_args():
  parser = argparse.ArgumentParser(description = 'Make term freq plot')
  parser.add_argument('-s', '--src', help = 'source file path', required  = True)
  parser.add_argument('-d', '--dst', help = 'destination file path', required  = True)
  return parser.parse_args()

def main():
  args = parse_args()
  stat = make_zipf(args.src)

  vals = sorted(stat.values(), reverse = True)
  make_plot(vals, args.dst, 3, 150, 'position', 'frequency')

if __name__ == "__main__":
  main()
