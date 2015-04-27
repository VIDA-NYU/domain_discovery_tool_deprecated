#!/bin/sh
if [ $# -eq 0 ]
then
    ELASTIC=http://localhost:9200
else
    ELASTIC=$1
fi

curl -XPUT "$ELASTIC/memex/page/_mapping?pretty=1" -d '@mapping.json'
