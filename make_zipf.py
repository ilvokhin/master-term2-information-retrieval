#! /usr/bin/env python
# -*- coding: utf-8 -*

import nltk
import argparse
import matplotlib.pyplot as plt
from numpy import arange
from common import make_term
from make_index import PUNCT
from make_index import parse_file
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

def calc_error(pos, vals, const, rho):
  err = [abs(x - y)**2 for x, y in zip(vals, [const / p**rho for p in pos])]
  return sum(err) / len(err)

def stupid_params_search(pos, vals):
  # some magic numbers here
  min_avg_err = 10**9
  best_const = -1
  best_rho = -1
  for const in xrange(1000, 30000, 500):
    for rho in arange(0.25, 2, 0.25):
      cur_err = calc_error(pos, vals, const, rho)
      if min_avg_err > cur_err:
        min_avg_err = cur_err
        best_const = const
        best_rho = rho
  return (best_const, best_rho)

def make_plot(vals, filename, start, end, x_name, y_name):
  fig = plt.figure(1)
  pos = range(len(vals))
  # fair plot looks like shit, so cut it a little
  plot_pos = pos[start:end]
  plot_vals = vals[start:end]
  plt.plot(plot_pos, plot_vals, 'o', plot_pos, plot_vals)
  # find params for analytic form, which looks like
  # f(rank) = const / rank**rho, check wiki for more details:
  # https://en.wikipedia.org/wiki/Zipf's_law
  const, rho = stupid_params_search(plot_pos, plot_vals)
  print 'best params: const = %f, rho = %f' % (const, rho)
  plt.plot(plot_pos, [const / elem**rho for elem in plot_pos], 'o')
  # add some labels
  plt.title(filename)
  plt.xlabel(x_name)
  plt.ylabel(y_name)
  plt.grid(True)

  plt.savefig(filename)

def parse_args():
  parser = argparse.ArgumentParser(description = 'Make Zipf term freq plot')
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
