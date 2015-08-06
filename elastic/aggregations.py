#!/usr/bin/python
from os import environ
from config import es as default_es

def get_significant_terms(ids, termCount = 50, mapping=None, es_index='memex', es_doc_type='page', es=None):
    if es is None:
        es = default_es

    with open(environ['DDT_HOME']+'/elastic/stopwords.txt', 'r') as f:
        stopwords = [word.strip() for word in f.readlines()]

    query = {
        "query":{
            "ids": {
                "values": ids
            }
        },
        "aggregations" : {
            "significantTerms" : {
                "significant_terms" : { 
                    "field" : mapping["text"],
                    "size" : termCount,
                    "exclude": stopwords
                }
            },
        },
        "size": 0
    }

    res = es.search(body=query, index=es_index, doc_type=es_doc_type, timeout=30)

    return [item['key'] for item in res['aggregations']['significantTerms']['buckets'] if len(item['key']) > 2]
