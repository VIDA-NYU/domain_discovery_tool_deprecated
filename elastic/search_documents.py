#!/usr/bin/python
from pyelasticsearch import ElasticSearch
import sys
import urllib2
import base64
from os import environ
        
def search(field, queryStr):
    es_server = 'http://localhost:9200/'
    es_index = 'memex'
    es_doc_type = 'page'
    if environ.get('ELASTICSEARCH_SERVER'):
        es_server = environ['ELASTICSEARCH_SERVER']
    if environ.get('ELASTICSEARCH_INDEX'):
        es_index = environ['ELASTICSEARCH_INDEX']
    if environ.get('ELASTICSEARCH_DOC_TYPE'):
        es_doc_type = environ['ELASTICSEARCH_DOC_TYPE']
        
    es = ElasticSearch(es_server)

    if len(queryStr) > 0:
        query = {
            "query": {
                "query_string": {
                    "fields" : [field],
                    "query": ' and  '.join(queryStr[0:]),
                }
            },
            "fields": [field]
        }
        print query
        res = es.search(query, index=es_index, doc_type=es_doc_type, size=500)
        hits = res['hits']
        urls = []
        for hit in hits['hits']:
            urls.append(hit['_id'])
        return urls

def term_search(field, queryStr):
    es_server = 'http://localhost:9200/'
    if environ.get('ELASTICSEARCH_SERVER'):
        es_server = environ['ELASTICSEARCH_SERVER']
    es = ElasticSearch(es_server)

    if len(queryStr) > 0:
        query = {
            "query" : {
                "match": {
                    field: {
                        "query": ' '.join(queryStr),
                        "minimum_should_match":"100%"
                    }
                }
            },
            "fields": ["url"]
        }
        print query
        res = es.search(query, 
                        index=environ['ELASTICSEARCH_INDEX'] if environ.get('ELASTICSEARCH_INDEX') else 'memex', 
                        doc_type=environ['ELASTICSEARCH_DOC_TYPE'] if environ.get('ELASTICSEARCH_DOC_TYPE') else 'page',
                        size=500)

        hits = res['hits']
        urls = []
        for hit in hits['hits']:
            urls.append(hit['_id'])
        return urls

def get_image(url):
    es_server = 'http://localhost:9200/'
    if environ.get('ELASTICSEARCH_SERVER'):
        es_server = environ['ELASTICSEARCH_SERVER']
    es = ElasticSearch(es_server)

    if url:
        query = {
            "query": {
                "term": {
                    "url": url
                }
            },
            "fields": ["thumbnail", "thumbnail_name"]
        }
        res = es.search(query, 
                        index=environ['ELASTICSEARCH_INDEX'] if environ.get('ELASTICSEARCH_INDEX') else 'memex', 
                        doc_type=environ['ELASTICSEARCH_DOC_TYPE'] if environ.get('ELASTICSEARCH_DOC_TYPE') else 'page')

        hits = res['hits']['hits']
        if (len(hits) > 0):
            try:
                img = base64.b64decode(hits[0]['fields']['thumbnail'][0])
                img_name = hits[0]['fields']['thumbnail_name'][0]
                return [img_name, img]
            except KeyError:
                print "No thumbnail found"
        else:
            print "No thumbnail found"
    return [None, None]

def get_context(terms):
    es_server = 'http://localhost:9200/'
    if environ.get('ELASTICSEARCH_SERVER'):
        es_server = environ['ELASTICSEARCH_SERVER']
    es = ElasticSearch(es_server)

    if len(terms) > 0:

        query = {
            "query": { 
                "match": {
                    "text": {
                        "query": ' and  '.join(terms[0:]),
                        "operator" : "and"
                    }
                }
             },
            "highlight" : {
                "fields" : {
                    "text": {
                        "fragment_size" : 100, "number_of_fragments" : 1
                    }
                }
            }
        }
        print query
        res = es.search(query, 
                        index=environ['ELASTICSEARCH_INDEX'] if environ.get('ELASTICSEARCH_INDEX') else 'memex', 
                        doc_type=environ['ELASTICSEARCH_DOC_TYPE'] if environ.get('ELASTICSEARCH_DOC_TYPE') else 'page')

        hits = res['hits']
        print 'Document found: %d' % hits['total']
        highlights = []
        for hit in hits['hits']:
            highlights.append(hit['highlight']['text'])
        return highlights

if __name__ == "__main__":
    print sys.argv[1:]
    if 'string' in sys.argv[1]:
        print search(sys.argv[2], sys.argv[3:])
    elif 'term' in sys.argv[1]:
        for url in term_search(sys.argv[2], sys.argv[3:]):
            print url
    elif 'context' in sys.argv[1]:
        print get_context(sys.argv[2:])
    elif 'image' in sys.argv[1]:
        get_image(sys.argv[2])
