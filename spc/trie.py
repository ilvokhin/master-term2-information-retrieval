#! /usr/bin/env python
# -*- coding: utf-8 -*

import sys
import argparse


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


def main():
    pass

if __name__ == "__main__":
    main()
