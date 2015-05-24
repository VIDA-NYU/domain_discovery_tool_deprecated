#!/usr/bin/python
from pyelasticsearch import ElasticSearch
import sys
import urllib2
import base64
from os import environ
from pprint import pprint
from datetime import datetime
        
def search(field, queryStr, es_index='memex', es_doc_type='page', es=None):
    if es is None:
        es = ElasticSearch("http://localhost:9200")

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

def term_search(field, queryStr, es_index='memex', es_doc_type='page', es=None):
    if es is None:
        es = ElasticSearch("http://localhost:9200")

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
        res = es.search(query, index=es_index, doc_type=es_doc_type, size=500)

        hits = res['hits']
        urls = []
        for hit in hits['hits']:
            urls.append(hit['_id'])
        return urls

def get_image(url, es_index='memex', es_doc_type='page', es=None):
    if es is None:
        es = ElasticSearch("http://localhost:9200")

    if url:
        query = {
            "query": {
                "term": {
                    "url": url
                }
            },
            "fields": ["thumbnail", "thumbnail_name"]
        }
        res = es.search(query, index=es_index, doc_type=es_doc_type, size=500)

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

def get_context(terms, es_index='memex', es_doc_type='page', es=None):
    if es is None:
        es = ElasticSearch("http://localhost:9200")

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
        res = es.search(query, index=es_index, doc_type=es_doc_type, size=500)
        hits = res['hits']
        print 'Document found: %d' % hits['total']
        highlights = []
        for hit in hits['hits']:
            highlights.append(hit['highlight']['text'])
        return highlights

def range(field, from_val, to_val, ret_fields=[], epoch=None, es_index='memex', es_doc_type='page', es=None):
    if es is None:
        es = ElasticSearch("http://localhost:9200")

    if not (epoch is None):
        if epoch:
            from_val = datetime.utcfromtimestamp(long(from_val)).strftime('%Y-%m-%dT%H:%M:%S')
            to_val = datetime.utcfromtimestamp(long(to_val)).strftime('%Y-%m-%dT%H:%M:%S')
            
    query = { 
        "query" : { 
            "range" : { 
                field : {
                    "from": from_val,
                    "to": to_val
                }
            },
        },
        "fields": ret_fields
    }

    res = es.search(query, index=es_index, doc_type=es_doc_type, size=500)
    hits = res['hits']['hits']

    results=[]
    for hit in hits:
        results.append(hit['fields'])

    return results

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
    elif 'range' in sys.argv[1]:
        epoch = True
        if len(sys.argv) == 7:
            if 'False' in sys.argv[6]:
                epoch = False
        print range(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5].split(','), epoch, es_index='memex')

