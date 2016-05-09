#! /usr/bin/env bash

# build ngrams from raw data
# raw data should be in tsv format: orig if no fix occured, orig\tfix otherwise

cat data/queries.txt | head -n 1000000 | tr '\t' '\n' | python extract_ngrams.py -n 1 -s > data/unigrams.txt &
cat data/queries.txt | head -n 1000000 | tr '\t' '\n' | python extract_ngrams.py -n 2 -s > data/bigrams.txt &
wait

