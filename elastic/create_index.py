from os import environ
import json

from config import es_elastic as default_es

def create_index(es_index='memex', es=None):
    if es is None:
        es = default_es

    json_page_data=open(environ['DDT_HOME']+'/elastic/mapping.json').read()
    json_terms_data=open(environ['DDT_HOME']+'/elastic/mapping_terms.json').read()

    page_mappings = json.loads(json_page_data)
    terms_mappings = json.loads(json_terms_data)

    mappings = {"mappings": 
                {
                    "page": page_mappings["page"], 
                    "terms":terms_mappings["terms"]
                }
            }
    
    fields = es_index.lower().split(' ')
    es_index = '_'.join([item for item in fields if item not in ''])

    res = es.indices.create(index=es_index, body=mappings, ignore=400)
    
    return res
