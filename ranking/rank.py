import sys

import tfidf
import BayesianSets
import numpy as np

class rank:
    def results(self,table,query_urls, other_urls):

        [urls, _, data] = table.getTfidfArray()

        indices = [urls.index(url) for url in query_urls]
        subquery_data = data[indices, :]
        
        indices = [urls.index(url) for url in other_urls]
        other_data = data[indices, :]

        bs = BayesianSets.BayesianSets()
        
        score = bs.score(subquery_data, other_data)

        indices = np.argsort(np.multiply(score,-1))
        ranked_urls = [other_urls[index] for index in indices]
        ranked_scores = [score[index] for index in indices]
        return [ranked_urls,ranked_scores]

def main(argv):
    if len(argv) != 2:
        print "Invalid arguments"
        print "python rank.py inputfile 0,1,2"
        return
    
    # File containing information of documents
    input_file = argv[0]
    # Most relevant documents
    query_index = [int(i) for i in argv[1].split(',')]
    ranker = rank()
    [ranked_urls,scores] = ranker.results(input_file,query_index)

    for i in range(0,len(ranked_urls)):
        print ranked_urls[i]," ", str(scores[i])
    
if __name__=="__main__":
    main(sys.argv[1:])
