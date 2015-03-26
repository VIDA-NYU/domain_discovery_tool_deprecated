#This class provide APIs for interfaces applications
#to communicate with seed crawler
#
#03/11/2015

from sets import Set

from subprocess import call
from subprocess import Popen
from subprocess import PIPE
from os import chdir, listdir, environ
from os.path import isfile, join, exists
import shutil
import sys

import parallel_download
import rank
import tfidf
import extract_terms

class SeedCrawlerModel:
    #Note: we should estimate the latency of each operation so that the application could adapt smoothly

    def __init__(self):
        #Intermediate data will being handled here: urls, extracted text, terms, clusters, etc.

        #list of urls and their labels, ranking scores
        #e.g: urls = [["nature.com", 1, 0.9], ["sport.com", 0, 0.01]
        #list of terms and their labels, ranking scores
        #e.g: terms = [["science", 1, 0.9], ["sport", 0, 0.02]]
        self.positive_urls = Set()
        self.negative_urls = Set()
        self.tfidf = tfidf.tfidf()
        self.memex_home = environ['MEMEX_HOME']


    def submit_query_terms(self, term_list):
    #Perform queries to Search Engine APIs
    #This function only operates when there is no information associated with the terms,
    #usually before running extract_terms()
    #
    #Args:
    #   term_list: list of search terms that are submited by user
    #Returns:
    #   urls: list of urls that are returned by Search Engine
        chdir(self.memex_home + '/seed_crawler/seeds_generator')
        
        with open('conf/queries.txt','w') as f:
            for term in term_list:
                f.write(term)
            
        p=Popen("java -cp .:class:libs/commons-codec-1.9.jar BingSearch -t 100",shell=True,stdout=PIPE)
        output, errors = p.communicate()
        print output
        print errors
        call(["rm", "-rf", "html"])
        call(["mkdir", "-p", "html"])
        #download.download("results.txt","html")
        parallel_download.startProcesses("results.txt","html")
        
        if exists(self.memex_home + "/seed_crawler/ranking/exclude.txt"):
            call(["rm", self.memex_home + "/seed_crawler/ranking/exclude.txt"])

        urls = []
        with open("results.txt",'r') as f:
            urls = [self.validate_url(line.strip()) for line in f.readlines()]

        chdir(self.memex_home + '/seed_crawler/lda_pipeline')
        call(["mkdir", "-p", "data"])
        p=Popen("java -cp .:class/:lib/boilerpipe-1.2.0.jar:lib/nekohtml-1.9.13.jar:lib/xerces-2.9.1.jar Extract ../seeds_generator/html/  | python concat_nltk.py data/lda_input.csv",shell=True,stdout=PIPE)
        output, errors = p.communicate()
        print output
        print errors

        return urls #Results from Search Engine
        
    
    def submit_selected_urls(self, positive, negative):
    #Perform ranking and diversifing on all urls with regard to the positive urls
    #
    #Args:
    #   labeled_urls: a list of pair <url, label>. Label 1 means positive and 0 means negative.
    #Returns:
    #   urls: list of urls with ranking scores

        # Test new positive and negative examples with exisitng classifier
        # If accuracy above threshold classify pages
        # Ranking 
        # Diversification

        for url in positive:
            self.positive_urls.add(url)
            if url in self.negative_urls:
                self.negative_urls.discard(url)

        for url in negative:
            self.negative_urls.add(url)
            if url in self.positive_urls:
                self.positive_urls.discard(url)

        documents = {}
        other = []
        input_file = self.memex_home + '/seed_crawler/lda_pipeline/data/lda_input.csv'

        with open(input_file,'r') as f:
            for line in f.readlines():
                url, content = line.strip().split(";")
                if url not in self.negative_urls:
                    documents[url] = content
                    if url not in self.positive_urls:
                        other.append(url)
                
        self.copy_files(positive, negative)

        self.tfidf.process(documents)

        chdir(self.memex_home + '/seed_crawler/ranking')
        ranker = rank.rank()
        
        [ranked_urls,scores] = ranker.results(self.tfidf,self.positive_urls, other)
        return [ranked_urls, scores] # classified, ranked, diversified 

    def extract_terms(self, count):
    #Extract salient terms from positive urls
    #
    #Returns:        
    #   terms: list of extracted salient terms and their ranking scores
        chdir(self.memex_home + '/seed_crawler/ranking')
        if exists("selected_terms.txt"):
            call(["rm", "selected_terms.txt"])
        if exists("exclude.txt"):
            call(["rm", "exclude.txt"])

        extract = extract_terms.extract_terms(self.tfidf)
        return extract.getTopTerms(count)

    def submit_selected_terms(self, positive, negative):
    #Rerank the terms based on the labeled terms
    #
    #Args:
    #   labeled_terms: list of pair of term and label: <term, label>. Label 1 means postive, 0 means negative.
    #Returns:
    #   terms: list of newly ranked terms and their ranking scores
        terms = []
        chdir(self.memex_home+'/seed_crawler/ranking')
        
        past_yes_terms = []
        if exists("selected_terms.txt"):
            with open('selected_terms.txt','r') as f:
                past_yes_terms = [line.strip() for line in f.readlines()]

        with open('selected_terms.txt','w+') as f:
            for word in past_yes_terms:
                f.write(word+'\n')
            for choice in positive :
                if choice not in past_yes_terms:
                    f.write(choice+'\n')

        past_no_terms = []
        if exists("exclude.txt"):
            with open('exclude.txt','r') as f:
                past_no_terms = [line.strip() for line in f.readlines()]

        with open('exclude.txt','w+') as f:
            for word in past_no_terms:
                f.write(word+'\n')
            for choice in negative :
                if choice not in past_no_terms:
                    f.write(choice+'\n')

        extract = extract_terms.extract_terms(self.tfidf)
        [ranked_terms, scores] = extract.results(past_yes_terms + positive)

        ranked_terms = [ term for term in ranked_terms if (term not in past_no_terms) and (term not in negative)]
                
        return ranked_terms # ranked

    def test(self):
        chdir(self.memex_home+'/seed_crawler/seeds_generator')
        parallel_download.startProcesses("results.txt","html")

    def copy_files(self, positive, negative):
        urlspath = self.memex_home + '/seed_crawler/seeds_generator/html/'
        classifier_data_positive_path = self.memex_home+'/pageclassifier/conf/sample_training_data/positive'
        classifier_data_negative_path = self.memex_home+'/pageclassifier/conf/sample_training_data/negative'
        files = [ f for f in listdir(urlspath) if isfile(join(urlspath,f))]
        [ shutil.copy(urlspath+f, classifier_data_positive_path) for f in files if parallel_download.decode(f) in positive ]
        [ shutil.copy(urlspath+f, classifier_data_negative_path) for f in files if parallel_download.decode(f) in negative ]

    def validate_url(self, url):
        s = url[:4]
        if s == "http":
            return url
        else:
            url = "http://" + url
        return url


if __name__=="__main__":
    scm = SeedCrawlerModel()
    scm.submit_query_terms(["elsa"])
    #scm.test()
    #Create a test that mimick user process here to test
    #1. User starts with some terms
    #2. (Repeat) User labels the urls and submits the labeled urls
    #3. User requests for extracting terms from labeled urls
    #4. (Repeat) User labels the terms and submits the labeled terms for reranking
