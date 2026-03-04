#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      hugopen
#
# Created:     09/08/2013
# Copyright:   (c) hugopen 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------


from ngrams_model import NGramsModel
from optparse import OptionParser
import pickle
import gzip


def main():

    usage = "usage: %prog [options] ngrams_model_file input_queries_file outfile_junk_queries"
    parser = OptionParser(usage=usage)
    parser.add_option("-t", "--threshold_log_likelihood", help="Minimum neg log likelihood of the query to consider it valid", dest="threshold", type='float',  default=-50.0)
    parser.add_option("-c", "--column_number_query", help="Zero-based column number in the TSV file, where the query is located", dest="query_col", type='int',  default=0)
    parser.add_option("-l", "--line_limit", help="Stop after reading this many lines from input", dest="line_limit", type='int',  default=-1)
    parser.add_option("-v", "--verbose", help="Verbose mode, prints more info", dest="verbose", action="store_true", default=False)
    parser.add_option("-f", "--column_number_frequency", help="Zero-based column number in the TSV file, where the frequency is located", dest="freq_col", type='int',  default=1)

    (options, args) = parser.parse_args()

    if len(args) != 3:
        parser.error("incorrect number of arguments")

    model_filepath = args[0]
    input_filepath = args[1]
    output_filepath = args[2]

    print("loading ngrams model...", model_filepath)
    ngrams_model = pickle.load(gzip.open(model_filepath, "rb"))
    print("loaded!")

    count = 0
    with open(output_filepath, "w") as fout:
        with open(input_filepath, 'r') as fin:
            line = fin.readline()
            while line != "":
                count += 1
                if options.line_limit>= 0 and  count > options.line_limit:
                    break
                tokens = line.split('\t')
                query = tokens[options.query_col]
                frequency = tokens[options.freq_col]
                neg_log_like = ngrams_model.log_likelihood(query)
                if neg_log_like < options.threshold:
                    outstring = str(count) + "\t" + query + "\t" + str(frequency) + "\t" + str(neg_log_like)
                    fout.write(outstring + "\n")
                    if options.verbose:
                        print(outstring)
                line = fin.readline()

    pass

if __name__ == '__main__':
    main()
