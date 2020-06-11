#!/usr/bin/python3
# Author: Suzanna Sia

# Standard imports
import pdb
import gzip
import logging
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")


class DataLoader:
    def __init__(self, format=None):
        """

        :param format: None for default, "mallet" to parse MALLET output
        """
        self.format = format
        return

    def load_topic_words(self, topic_word_file):
        if self.format == "mallet":
            return self._load_topics_mallet(topic_word_file)
        else:
            return self._load_topics_default(topic_word_file)

    @staticmethod
    def _load_topics_mallet(topic_word_file):
        topic_words = []
        with open(topic_word_file) as f:
            for line in f.readlines():
                temp = line.split("\t")[-1].strip()
                topic_words.append(temp.split())

        return topic_words

    @staticmethod
    def _load_topics_default(topic_word_file):
        DELIM = ";"

        with open(topic_wordf, 'r') as f:
            topic_words = f.readlines()

        topic_words = [tw.strip().replace(DELIM, '').split() for tw in topic_words]

        return topic_words

    def load_word_docids(self, word_dcf):
        if self.format == "mallet":
            return self._load_word_docs_mallet(word_dcf)
        else:
            return self._load_word_docs_default(word_dcf)

    @staticmethod
    def _load_word_docs_default(word_dcf):
        DELIM1 = "\t"
        DELIM2 = ";"

        word_dc = {}
        with open(word_dcf, 'r') as f:
            data = f.readlines()

        for line in data:
            word, docids = line.split(DELIM1)
            word_dc[word] = set(docids.strip().split(DELIM2))

        return word_dc

    @staticmethod
    def _load_word_docs_mallet(word_dcf):
        """
        Input is MALLET model state gzipped file
        :param word_dcf:
        :return:
        """
        # MALLET model state format: doc source pos typeindex type topic
        # Skip all lines that start with a #
        word_doc_dict = {}
        with gzip.open(word_dcf, mode="rt") as f:
            for i, line in enumerate(f.readlines()):
                #if i % 100000 == 0:
                    #logging.debug(f"On line {i:,}")
                if line.startswith("#"):
                    continue
                document_id, source, position, type_index, token, topic_assignment = [i.strip() for i in line.split()]

                if token not in word_doc_dict:
                    word_doc_dict[token] = set(document_id)
                else:
                    word_doc_dict[token].add(document_id)

        # logging.debug(word_doc_dict)
        return word_doc_dict
