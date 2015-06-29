#!/usr/bin/python
from os import environ
from config import es as default_es

def get_significant_terms(terms, field='text', fields=['text'], termCount = 50, es_index='memex', es_doc_type='page', es=None):
    if es is None:
        es = default_es

    with open(environ['DDT_HOME']+'/elastic/stopwords.txt', 'r') as f:
        stopwords = [word.strip() for word in f.readlines()]

    query = {
        "query" : {
            "query_string": {
                "fields" : fields,
                "query": ' and  '.join(terms[0:])
            }
        },
        "aggregations" : {
            "significantTerms" : {
                "significant_terms" : { 
                    "field" : field ,
                    "size" : termCount,
                    "exclude": stopwords
                }
            },
        },
        "size": 0
    }
    res = es.search(query, index=es_index, doc_type=es_doc_type)
    
    return [item['key'] for item in res['aggregations']['significantTerms']['buckets']]
