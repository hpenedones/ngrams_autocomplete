import sys
import pickle
import gzip
from ngrams_model import NGramsModel
from optparse import OptionParser
from bottle import route, run, template, response

@route('/ngrams//')
def index():
    return get_ngram_suggestions("")

@route('/ngrams/:prefix/')
def index(prefix):
    return get_ngram_suggestions(prefix)

def get_ngram_suggestions(prefix):
    response.headers['Access-Control-Allow-Origin'] = '*'
    prefix_log_likelihood = ngrams_model.log_likelihood(prefix)
    suggestions = ngrams_model.suggest(prefix, 8)
    output = "<br>Prefix Log likelihood = " + str(prefix_log_likelihood) + "</br>"
    for suggestion in suggestions:
            output += "<br>%s</br>" % suggestion

    return output

@route('/:filename')
def index(filename):
    try:
        with open(filename) as f:
            return f.readlines()
    except IOError:
        return ""
    return ""


usage = "usage: %prog [options] ngrams_model_filepath"
parser = OptionParser(usage=usage)
parser.add_option("-v", "--verbose", help="Verbose mode, prints more info", dest="verbose", action="store_true", default=False)

(options, args) = parser.parse_args()

if len(args) != 1:
    parser.error("incorrect number of arguments")

model_filepath = args[0]

if (options.verbose):
    print("loading ngrams model", model_filepath)
ngrams_model = pickle.load(gzip.open(model_filepath, "rb"))
if (options.verbose):
    print("loaded")


run(host='localhost', port=8080)

