from pyelasticsearch import ElasticSearch
from pprint import pprint
from datetime import datetime

def get_available_domains(es=None):
    if es is None:
        es = ElasticSearch("http://localhost:9200")
        
    query = {
        "query": {
            "match_all": {}
        },
    }
    res = es.search(query, 
                    index='config',
                    doc_type='domains',
                    size=100
                )

    hits = res['hits']['hits']

    res = []
    for hit in hits:
        res.append(hit['_source'])

    for i in range(0,len(res)):
        res[i]['timestamp'] = long(convert_to_epoch(datetime.strptime(res[i]['timestamp'], '%Y-%m-%dT%H:%M:%S.%f')))
        print datetime.utcfromtimestamp(res[i]['timestamp'])
    return res

def convert_to_epoch(dt):
    epoch = datetime.utcfromtimestamp(0)
    delta = dt - epoch
    return delta.total_seconds()

if __name__ == "__main__":
    get_available_domains()

    
