#!/usr/bin/python3
# Author: Suzanna Sia
# Credits: Ayush Dalmia
# Modifications for MALLET: Alexandra DeLucia

import numpy as np
import math
import os
import sys
import argparse
import pdb
import logging
from dataloader import DataLoader

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--nfiles', type=int, default=0, help="Number of documents")
    parser.add_argument('--topic-word-file', type=str, required=True,
                        help="Word topic file. Format should be one line per topic, with the top topic words comma delimited")
    parser.add_argument('--word-doc-file', type=str, required=True)
    parser.add_argument('--ntopics', type=int, help="Number of topics", required=True)
    parser.add_argument('--format', default=None, help="Format of input files. Stay 'None' for default format or 'mallet'"
                                                       "for a MALLET input parser. 'mallet' assumes the input is the default"
                                                       "MALLET output from topic_keys and model_state.gz")
    parser.add_argument('--output-file', type=str, required=True, help="TSV file to save topic coherence scores")
    parser.add_argument('--topic_wordf', type=str)
    parser.add_argument('--word_docf', type=str)
    return parser.parse_args()


def main():
    args = parse_args()

    dl = DataLoader(format=args.format)
    topic_words = dl.load_topic_words(args.topic_word_file)
    logging.info(f"Loaded topic words from {args.topic_word_file}")
    word_doc_counts = dl.load_word_docids(args.word_doc_file)
    logging.info(f"Loaded word document counts from {args.word_doc_file}")

    if args.nfiles == 0:
        total_docs = set()
        for word in word_doc_counts.keys():
            total_docs = total_docs.union(word_doc_counts[word])

        logging.warning(f"nfiles not provided - calculating from dataset: {len(total_docs)}")
        args.nfiles = len(total_docs)

    logging.info("Calculating average NPMI...")
    average_npmi_topics(topic_words, args.ntopics, word_doc_counts, args.nfiles, args.output_file)


def average_npmi_topics(topic_words, ntopics, word_doc_counts, nfiles, output_file):
    eps = 10**(-12)
    
    all_topics = []
    for k in range(ntopics):
        word_pair_counts = 0
        topic_score = []

        ntopw = len(topic_words[k])

        if ntopw<2:
            sys.exit("number of words in cluster less than 2.. fix your cluster..")

        for i in range(ntopw-1):
            for j in range(i+1, ntopw):
                w1 = topic_words[k][i]
                w2 = topic_words[k][j]

                w1w2_dc = len(word_doc_counts.get(w1, set()) & word_doc_counts.get(w2, set()))
                w1_dc = len(word_doc_counts.get(w1, set()))
                w2_dc = len(word_doc_counts.get(w2, set()))

                # what we had previously:
                #pmi_w1w2 = np.log(((w1w2_dc * nfiles) + eps) / ((w1_dc * w2_dc) + eps))

                # Correct eps:

                pmi_w1w2 = np.log((w1w2_dc * nfiles) / ((w1_dc * w2_dc) + eps) + eps)
                npmi_w1w2 = pmi_w1w2 / (- np.log( (w1w2_dc)/nfiles + eps))

                # Which is equivalent to this:
                #if w1w2_dc ==0: 
                #    npmi_w1w2 = -1
                #else:
                #    pmi_w1w2 = np.log( (w1w2_dc * nfiles)/ (w1_dc*w2_dc))
                #    npmi_w1w2 = pmi_w1w2 / (-np.log (w1w2_dc/nfiles))


                if npmi_w1w2>1 or npmi_w1w2<-1:
                    print(f"warning: NPMI score not bounded for:{w1}, {w2}, \
                            score:{np.around(npmi_w1w2,5)} ... rounding off")

                    if npmi_w1w2 > 1:
                        npmi_w1w2 = 1
                    elif npmi_w1w2 <-1:
                        npmi_w1w2 = -1

                topic_score.append(npmi_w1w2)

        all_topics.append(np.mean(topic_score))

    with open(output_file, "w+") as f:
        for k in range(ntopics):
            temp = f"{k}\t{np.around(all_topics[k], 5)}\t{','.join(topic_words[k])}"
            logging.info(temp)
            f.write(f"{temp}\n")

    avg_score = np.around(np.mean(all_topics), 5)
    logging.info(f"\nAverage NPMI for {ntopics} topics: {avg_score}")

    return avg_score


if __name__ == "__main__":
    main()


