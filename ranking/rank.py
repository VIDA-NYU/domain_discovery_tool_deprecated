import sys

import tfidf
import BayesianSets
import numpy as np

class rank:
    def results(self,input_file,positive,negative):
        documents = {}
        other = []

        with open(input_file,'r') as f:
            for line in f.readlines():
                url, content = line.strip().split(";")
                if url not in negative:
                    documents[url] = content
                    if url not in positive:
                        other.append(url)
        
        table = tfidf.tfidf()
    
        # Compute tfidf of terms in the documents
        table.process(documents)

        subquery_data = table.getTfidfArray(positive)
        other_data = table.getTfidfArray(other)

        bs = BayesianSets.BayesianSets()
        
        score = bs.score(subquery_data, other_data)

        indices = np.argsort(np.multiply(score,-1))
        ranked_urls = [other[index] for index in indices]
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
