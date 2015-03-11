#This class provide APIs for interfaces applications
#to communicate with seed crawler
#
#03/11/2015

class SeedCrawlerModel:
    #Note: we should estimate the latency of each operation so that the application could adapt smoothly

    def __init__(self):
        #Intermediated data will being handled here: urls, extracted text, terms, clusters, etc.

        #list of urls and their labels, ranking scores
        #e.g: urls = [["nature.com", 1, 0.9], ["sport.com", 0, 0.01]
        self.urls = []

        #list of terms and their labels, ranking scores
        #e.g: terms = [["science", 1, 0.9], ["sport", 0, 0.02]]
        self.terms = []

    def submit_query_terms(self, term_list):
    #Perform queries to Search Engine APIs
    #This function only operates when there is no information associated with the terms,
    #usually before running extract_terms()
    #
    #Args:
    #   term_list: list of search terms that are submited by user
    #Returns:
    #   urls: list of urls that are returned by Search Engine
    
        urls = []
        return urls #Results from Search Engine
        
    
    def submit_selected_urls(self, labeled_urls):
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
        urls = []
        return urls # classified, ranked, diversified 

    def extract_terms(self):
    #Extract salient terms from positive urls
    #
    #Returns:        
    #   terms: list of extracted salient terms and their ranking scores

        terms = [] #if there is no positive url
        return terms

    def submit_selected_terms(self, labeled_terms):
    #Rerank the terms based on the labeled terms
    #
    #Args:
    #   labeled_terms: list of pair of term and label: <term, label>. Label 1 means postive, 0 means negative.
    #Returns:
    #   terms: list of newly ranked terms and their ranking scores

        terms = []
        return terms # ranked

if __name__=="__main__":
    scm = new SeedCrawlerModel()
    #Create a test that mimick user process here to test
    #1. User starts with some terms
    #2. (Repeat) User labels the urls and submits the labeled urls
    #3. User requests for extracting terms from labeled urls
    #4. (Repeat) User labels the terms and submits the labeled terms for reranking
