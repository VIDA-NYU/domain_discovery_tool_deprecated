#!/usr/bin/python
from pyelasticsearch import ElasticSearch
import sys
from os import environ

def get_documents(urls):
    host =  environ['ELASTICSEARCH_SERVER'] if environ.get('ELASTICSEARCH_SERVER') else 'http://localhost:9200'
    es = ElasticSearch(host)
        
    if len(urls) > 0:
        results = {}

        for url in urls:
            query = {
                "query": {
                    "term": {
                        "url": url
                    }
                },
                "fields": ["text"]
            }
        
            res = es.search(query, 
                            index=environ['ELASTICSEARCH_INDEX'] if environ.get('ELASTICSEARCH_INDEX') else 'memex', 
                            doc_type=environ['ELASTICSEARCH_DOC_TYPE'] if environ.get('ELASTICSEARCH_DOC_TYPE') else 'page')
            hits = res['hits']
            try:
                results[url] = hits['hits'][0]['fields']['text'][0]
            except KeyError, e:
                print url, e, " not found in database"
            except IndexError, e:
                print url, e, " not found in database"

        return results



# Returns most recent documents in the format:
# [
#   ["url", "x", "y", "tag", "retrieved"],
#   ["url", "x", "y", "tag", "retrieved"],
#   ...
# ]
def get_most_recent_documents( \
    opt_maxNumberOfPages = 1000, opt_filter = None, es_index = 'memex', es_doc_type = 'page', es = None):
    if es is None:
        host = environ['ELASTICSEARCH_SERVER'] \
        if environ.get('ELASTICSEARCH_SERVER') else 'http://localhost:9200'
        es = ElasticSearch(host)
        
    # TODO(Yamuna): apply filter if it is None. Otherwise, match_all.
    query = { \
      "query": {
        "match_all": {}
      },
      "fields": ["url", "x", "y", "tag", "retrieved"],
      "size": opt_maxNumberOfPages,
      "sort": [
        {
          "retrieved": {
            "order": "desc"
          }
        }
      ]
    }

    res = es.search( \
    query, index = es_index, doc_type = es_doc_type, size = opt_maxNumberOfPages)

    hits = res['hits']

    docs = ["", 0, 0, [], 0] * len(hits['hits'])
    for i, hit in enumerate(hits['hits']):
      doc = docs[i]
      fields = hit['fields']
      if 'url' in fields:
        doc[0] = fields['url']
      if 'x' in fields:
        doc[1] = fields['x']
      if 'y' in fields:
        doc[2] = fields['y']
      if 'tag' in fields:
        doc[3] = fields['tag'].split(';')
      if 'retrieved' in fields:
        doc[4] = fields['retrieved']

    return docs



if __name__ == "__main__":
    urls = []
    with open(environ['MEMEX_HOME']+'/seed_crawler/seeds_generator/results.txt', 'r') as f:
        urls = f.readlines()
    urls = [url.strip() for url in urls]

    docs = get_documents(urls)

