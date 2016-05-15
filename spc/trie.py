#! /usr/bin/env python
# -*- coding: utf-8 -*

import sys
import argparse
from math import log
import cPickle as pickle
from heapq import heappop, heappush

import error_model as em
from error_model import ErrorModel
from kneser_ney import load_ngrams


class Trie(object):
    def __init__(self):
        self.nodes = [{}]
        self.vals = {}

    def add(self, key, val):
        cur_node_pos = 0
        for ch in key:
            cur_node = self.nodes[cur_node_pos]
            if ch not in cur_node:
                to = len(self.nodes)
                self.nodes.append({})
                cur_node[ch] = to
            cur_node_pos = cur_node[ch]
        self.vals[cur_node_pos] = val


class FuzzyPath(object):
    def __init__(self, weight, node_id, pos, dist, prefix):
        self.weight = weight
        self.node_id = node_id
        self.pos = pos
        self.dist = dist
        self.prefix = prefix

    def __lt__(self, other):
        if self.weight == other.weight:
            return self.node_id < other.node_id
        return self.weight < other.weight


class FuzzySearcher(object):
    def __init__(self, trie, error_model, max_dists):
        self.trie = trie
        self.error_model = error_model
        self.max_dists = max_dists

    def max_dist(self, key):
        for dist in reversed(self.max_dists):
            if len(key) > dist[0]:
                return dist[1]

    def find(self, key, max_candidates=30):
        max_dist = self.max_dist(key)
        pq = [FuzzyPath(0.0, 0, -1, max_dist, '')]
        candidates = set([])

        while pq:
            cur_path = heappop(pq)
            cur_node = self.trie.nodes[cur_path.node_id]
            next_pos = cur_path.pos + 1
            next_ch = key[next_pos] if len(key) > next_pos else None
            if next_ch is not None and next_ch in cur_node:
                no_edit = FuzzyPath(cur_path.weight, cur_node[next_ch],
                                    next_pos, cur_path.dist,
                                    cur_path.prefix + next_ch)
                heappush(pq, no_edit)

            if cur_path.dist:
                for to in cur_node:
                    if to != next_ch:
                        # insert
                        insert_err = -self.error_model.calc('I', '', to)
                        insert = FuzzyPath(cur_path.weight + insert_err,
                                           cur_node[to], cur_path.pos,
                                           cur_path.dist - 1,
                                           cur_path.prefix + to)
                        heappush(pq, insert)
                        # replace
                        replace_err = -self.error_model.calc('R', next_ch, to)
                        replace = FuzzyPath(cur_path.weight + replace_err,
                                            cur_node[to], cur_path.pos + 1,
                                            cur_path.dist - 1,
                                            cur_path.prefix + to)
                        heappush(pq, replace)
                # delete
                delete_err = -self.error_model.calc('D', next_ch, '')
                delete = FuzzyPath(cur_path.weight + delete_err,
                                   cur_path.node_id, cur_path.pos + 1,
                                   cur_path.dist - 1,
                                   cur_path.prefix)
                heappush(pq, delete)

            if next_ch is None and cur_path.node_id in self.trie.vals:
                candidates.add((cur_path.prefix,
                                self.trie.vals[cur_path.node_id]))
                if len(candidates) > max_candidates:
                    break

        return candidates


def make_fuzzy_trie(unigrams, error_model):
    trie = Trie()
    for uni in unigrams:
        trie.add(uni, unigrams[uni])

    max_dist = [(0, 1), (4, 2), (6, 3)]
    fuzzy_trie = FuzzySearcher(trie, error_model, max_dist)
    return fuzzy_trie


def save_trie(trie, filename):
    with open(filename, 'wb') as f:
        pickle.dump(trie, f)


def load_trie(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f)


def parse_args():
    parser = argparse.ArgumentParser(description='Make fuzzy trie')
    parser.add_argument('-u', '--unigrams', required=True)
    parser.add_argument('-e', '--error-model', required=True)
    parser.add_argument('-d', '--dst', required=True)
    return parser.parse_args()


def main():
    args = parse_args()
    unigrams = load_ngrams(args.unigrams)

    for uni in unigrams:
        unigrams[uni] = log(unigrams[uni], 2.)

    error_model = em.load_error_model(args.error_model)

    fuzzy_trie = make_fuzzy_trie(unigrams, error_model)
    save_trie(fuzzy_trie, args.dst)

if __name__ == "__main__":
    main()
