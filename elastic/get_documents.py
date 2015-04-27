#!/usr/bin/python
from pyelasticsearch import ElasticSearch
import sys
from os import environ

def get_documents(urls):
    es_server = 'http://localhost:9200/'
    if environ.get('ELASTICSEARCH_SERVER'):
        es_server = environ['ELASTICSEARCH_SERVER']
    es = ElasticSearch(es_server)
        
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
        
            res = es.search(query, index='memex', doc_type='page')
            hits = res['hits']
            try:
                results[url] = hits['hits'][0]['fields']['text'][0]
            except KeyError, e:
                print url, e, " not found in database"
            except IndexError, e:
                print url, e, " not found in database"

        return results

if __name__ == "__main__":
    urls = []
    with open(environ['MEMEX_HOME']+'/seed_crawler/seeds_generator/results.txt', 'r') as f:
        urls = f.readlines()
    urls = [url.strip() for url in urls]

    docs = get_documents(urls)

