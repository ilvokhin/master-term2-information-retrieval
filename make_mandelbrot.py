#! /usr/bin/env python
# -*- coding: utf-8 -*

import matplotlib.pyplot as plt
from make_zipf import make_zipf
from numpy import arange
import argparse


def mandelbrot(p, rank, rho, b):
    return p * (rank + rho)**-b


def calc_error(pos, vals, P, rho, B):
    err = [abs(x - y)**2 for x, y in zip(vals, [mandelbrot(P, p, rho, B)
                                                for p in pos])]
    return sum(err) / len(err)


def stupid_params_search(pos, vals):
    best_p = -1
    best_rho = -1
    best_b = -1
    min_err = 10**9

    for p in xrange(1000, 30000, 500):
        for rho in xrange(0, 1000, 5):
            for b in arange(0.25, 2, 0.25):
                cur_err = calc_error(pos, vals, p, rho, b)
                if cur_err < min_err:
                    best_p = p
                    best_rho = rho
                    best_b = b
                    min_err = cur_err
    return (best_p, best_rho, best_b, min_err)


def make_plot(vals, filename, start, end, x_name, y_name):
    fig = plt.figure(1)
    pos = range(len(vals))
    plot_pos = pos[start:end]
    plot_vals = vals[start:end]
    plt.plot(plot_pos, plot_vals, 'o', plot_pos, plot_vals)
    p, rho, b, err = stupid_params_search(plot_pos, plot_vals)
    print 'best params: p = %d, rho = %d, b = %f (with error = %f)' \
        % (p, rho, b, err)
    plt.plot(plot_pos, [mandelbrot(p, elem, rho, b) for elem in plot_pos], 'o')
    # add some labels
    plt.title(filename)
    plt.xlabel(x_name)
    plt.ylabel(y_name)
    plt.grid(True)

    plt.savefig(filename)


def parse_args():
    parser = argparse.ArgumentParser(
        description='Make Mandelbrot term freq plot')
    parser.add_argument('-s', '--src', help='source file path', required=True)
    parser.add_argument(
        '-d', '--dst', help='destination file path', required=True)
    return parser.parse_args()


def main():
    args = parse_args()
    stat = make_zipf(args.src)

    vals = sorted(stat.values(), reverse=True)
    make_plot(vals, args.dst, 3, 150, 'position', 'frequency')

if __name__ == "__main__":
    main()
