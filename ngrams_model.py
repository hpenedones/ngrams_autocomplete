#-------------------------------------------------------------------------------
# Name:        Character-based n-grams model for Bing Queries
# Purpose:      
#
# Author:      Hugo Penedones (hugopen)
#
# Created:     08/08/2013
# Copyright:   (c) Microsoft 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import pickle
import math
import queue
import itertools
import hashlib
from optparse import OptionParser

class NGramsModel():
    def __init__(self, long_mem_size, order, start_char, end_char):
        self.order = order
        self.start_char = start_char
        self.end_char = end_char
        self.ngrams = {}
        self.totals = {}
        self.inserted = 0
        self.long_mem_size = long_mem_size

    def encode_long_term(self, text, nchars):
        return hashlib.sha1(text.encode()).hexdigest()[:nchars]

    def sub_string_iterator(self, query):
        query = self.start_char*(self.order) + query + self.end_char
        for i in range(self.order, len(query)):
            context_str = self.context(query, i, self.long_mem_size, self.order)
            next_char = query[i]
            yield (context_str, next_char)

    def context(self, query, cursor_pos, longterm_size, ngrams_size):
        beggining = query[:cursor_pos-ngrams_size]
        long_term_mem = self.encode_long_term(beggining, longterm_size)
        last_chars = query[cursor_pos-ngrams_size:cursor_pos]
        context_str = long_term_mem + last_chars
        return context_str


    def insert_string(self, query, frequency, verbose=False):
        for prev_chars, next_char in self.sub_string_iterator(query):
            if prev_chars not in self.ngrams:
                self.ngrams[prev_chars] = {}
                self.totals[prev_chars] = 0
            if next_char not in self.ngrams[prev_chars]:
                self.ngrams[prev_chars][next_char] = 0
            self.ngrams[prev_chars][next_char] += frequency
            self.totals[prev_chars] += frequency
        self.inserted += 1
        if verbose:
            if self.inserted % 10000 == 0:
                print("Inserted", self.inserted)

    def likelihood(self, query):
        prob = 1.0
        for prev_chars, next_char in self.sub_string_iterator(query):
            if not prev_chars in self.ngrams:
                prob *= 1.0/64 # uniform distribution for the alphabet size
                continue
            count_to_next = 1
            if next_char in self.ngrams[prev_chars]:
                count_to_next = self.ngrams[prev_chars][next_char]
            prob *= 1.0*count_to_next/self.totals[prev_chars]
        return prob

    def log_likelihood(self, query):
        return math.log(self.likelihood(query)+1e-50)


    def suggestions_iterator(self, prefix):
        prefix = self.start_char*(self.order) + prefix
        pqueue = queue.PriorityQueue()
        pqueue.put((0,prefix))
        while not pqueue.empty():
            neg_log_prob, prefix = pqueue.get()
            if len(prefix)>0 and prefix[len(prefix)-1] == self.end_char:
                yield prefix[self.order:-1]
            else:
                context_str = self.context(prefix, len(prefix), self.long_mem_size, self.order)
                if context_str in self.ngrams:
                    for next_char, counts in list(self.ngrams[context_str].items()):
                        new_neg_log_prob = neg_log_prob -math.log(1.0*counts/self.totals[context_str])
                        next_context_str = self.context(prefix+next_char, len(prefix)+1, self.long_mem_size, self.order)
                        if next_context_str in self.ngrams or next_char == self.end_char:
                            pqueue.put((new_neg_log_prob, prefix+next_char))


    def suggest(self, prefix, nsuggestions):
        counter = 0
        for sugg in self.suggestions_iterator(prefix):
            if counter > nsuggestions:
                break
            counter += 1
            yield sugg

def main():

    usage = "usage: %prog [options] input_queries_file"
    parser = OptionParser(usage=usage)
    parser.add_option("-n", "--ngrams_order", help="Number of preceding characters to look into", dest="ngrams_order", type='int',  default=3)
    parser.add_option("-l", "--long_term_order", help="Number of character to represent long term memory", dest="lterm_order", type='int',  default=2)
    parser.add_option("-c", "--column_number_query", help="Zero-based column number in the TSV file, where the query is located", dest="query_col", type='int',  default=0)
    parser.add_option("-f", "--column_number_frequency", help="Zero-based column number in the TSV file, where the frequency is located", dest="freq_col", type='int',  default=1)
    parser.add_option("-v", "--verbose", help="Verbose mode, prints more info", dest="verbose", action="store_true", default=False)

    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.error("incorrect number of arguments")

    input_filepath = args[0]
    model_filepath = 'ngrams%d_%d.model' % (options.lterm_order, options.ngrams_order)

    start_char = "["
    end_char = "]"

    ngrams_model = NGramsModel(options.lterm_order, options.ngrams_order, start_char, end_char)

    if options.verbose:
        print("Starting model training")
    with open(input_filepath, 'r') as fin:
        line = fin.readline()
        while line != "":
            tokens = line.split('\t')
            query = tokens[options.query_col]
            frequency = tokens[options.freq_col]
            ngrams_model.insert_string(query, int(frequency), options.verbose)
            line = fin.readline()

    if options.verbose:
        print("Starting serialization")
    pickle.dump(ngrams_model, open(model_filepath, "wb"))

    if options.verbose:
        print("Empty prefix top completions")
        for sugg in  ngrams_model.suggest("", 10):
            print(sugg)

    pass

if __name__ == '__main__':
    main()
