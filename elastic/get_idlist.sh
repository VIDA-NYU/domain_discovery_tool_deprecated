#!/bin/sh

curl -s -XGET 'http://localhost:9200/memex/page/_search?scroll=5m&search_type=scan' -d '
{ 
    "query" : { 
        "match_all" : {} 
    },
    "fields": [],
    "size": 100
}
'

