#!/usr/bin/python
from pyelasticsearch import ElasticSearch
from pprint import pprint

def get_documents(urls, fields=["text"], es_index='memex', es_doc_type='page', es=None):
    if es is None:
        es = ElasticSearch('http://localhost:9200/')

    if len(urls) > 0:
        results = {}

        for url in urls:
            query = {
                "query": {
                    "term": {
                        "url": url
                    }
                },
                "fields": fields
            }
        
            res = es.search(query, 
                            index=es_index,
                            doc_type=es_doc_type)

            
            hits = res['hits']['hits'][0]

            if not hits.get('fields') is None:
                hits = hits['fields']
                record = {}
                for field in fields:
                    if(not hits.get(field) is None):
                        record[field] = hits[field][0]
                results[url] = record           
            
    return results

            
# Returns most recent documents in the format:
# [
#   ["url", "x", "y", "tag", "retrieved"],
#   ["url", "x", "y", "tag", "retrieved"],
#   ...
# ]
def get_most_recent_documents(opt_maxNumberOfPages = 1000, fields = [], opt_filter = None, es_index = 'memex', es_doc_type = 'page', es = None):
    if es is None:
        es = ElasticSearch('http://localhost:9200')

    # TODO(Yamuna): apply filter if it is None. Otherwise, match_all.
    query = { 
      "size": opt_maxNumberOfPages,
      "sort": [
        {
          "retrieved": {
            "order": "desc"
          }
        }
      ]
    }

    if opt_filter is None:
        query["query"] = {
            "match_all": {}
        }
    else:
        query["query"] = {
            "query_string": {
                "fields" : ['text'],
                "query": ' and  '.join(opt_filter.split(' ')),
            }
        }

    if len(fields) > 0:
        query["fields"] = fields

    res = es.search(query, index = es_index, doc_type = es_doc_type)

    hits = res['hits']['hits']

    results = []
    for hit in hits:
        results.append(hit['fields'])

    return results

if __name__ == "__main__":
    urls = []
    with open(environ['MEMEX_HOME']+'/seed_crawler/seeds_generator/results.txt', 'r') as f:
        urls = f.readlines()
    urls = [url.strip() for url in urls]

    docs = get_documents(urls)

