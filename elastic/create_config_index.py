from os import environ
import json

from config import es_elastic as default_es

def create_config_index(es_index='config', es=None):
    if es is None:
        es = default_es

    json_config_data=open(environ['DDT_HOME']+'/elastic/config.json').read()

    config_mappings = json.loads(json_config_data)

    mappings = {"mappings": 
                {
                    "domains": config_mappings["domains"] 
                }
            }
    
    fields = es_index.lower().split(' ')

    es_index = '_'.join([item for item in fields if item not in ''])

    res = es.indices.create(index=es_index, body=mappings, ignore=400)
    
    return res
