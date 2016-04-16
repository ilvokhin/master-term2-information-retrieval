#! /usr/bin/env python
# -*- coding: utf-8 -*

import string
import mrjob.job
import mrjob.protocol

def make_term(token):
  return token.strip(string.punctuation).lower()

class MRIndexer(mrjob.job.MRJob):
  INPUT_PROTOCOL = mrjob.protocol.RawValueProtocol
  OUTPUT_PROTOCOL = mrjob.protocol.RawValueProtocol

  def mapper(self, _, line):
    try:
      doc_id, doc = line.decode('utf8').strip().split('\t', 1)
      for token in doc.split():
        self.increment_counter('Stat', 'tokens', 1)
        term = make_term(token)
        if term:
          self.increment_counter('Stat', 'terms', 1)
          yield term.encode('utf8'), doc_id
    except ValueError:
      self.increment_counter('Stat', 'empty value', 1)

  def reducer(self, key, values):
    vals = sorted(list(set(values)))
    yield None, '\t'.join([key] + vals).encode('utf8')

def main():
  MRIndexer.run()

if __name__ == "__main__":
  main()
