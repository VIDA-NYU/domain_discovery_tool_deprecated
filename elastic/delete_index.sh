#!/bin/sh
if [ $# -eq 0 ]
then 
    INDEX=memex
else
    INDEX=$1
fi

if [ $# -gt 1 ]
then
    ELASTIC=$2
else
    ELASTIC=http://localhost:9200
fi
echo $INDEX

curl -XDELETE "$ELASTIC/$INDEX/"; echo
