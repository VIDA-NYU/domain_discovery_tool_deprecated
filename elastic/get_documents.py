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

if __name__ == "__main__":
    urls = []
    with open(environ['MEMEX_HOME']+'/seed_crawler/seeds_generator/results.txt', 'r') as f:
        urls = f.readlines()
    urls = [url.strip() for url in urls]

    docs = get_documents(urls)

