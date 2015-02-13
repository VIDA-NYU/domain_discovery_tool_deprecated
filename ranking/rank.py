import sys

import tfidf
import BayesianSets
import numpy as np

def main(argv):
    if len(argv) != 2:
        print "Invalid arguments"
        print "python rank.py inputfile 0,1,2"
        return
    
    # File containing information of documents
    input_file = argv[0]
    # Most relevant documents
    query_index = [int(i) for i in argv[1].split(',')]

    table = tfidf.tfidf()
    
    # Compute tfidf of terms in the documents
    table.process(input_file)

    data = table.getTfidfArray()

    bs = BayesianSets.BayesianSets()
    
    # documents other than the relevant documents
    index = [x for x in range(0,len(data)) if x not in query_index]

    score = bs.score(data[query_index,:], data[index,:])

    rank_index = np.argsort(np.multiply(score,-1))

    offset_rank_index = [index[x] for x in rank_index]

    # Get the urls corresponding to the scored documents
    ranked_urls = table.getURLs(offset_rank_index)

    for i in range(0,len(score)):
        print ranked_urls[i], " ", score[rank_index[i]]

if __name__=="__main__":
    main(sys.argv[1:])
