#!/bin/sh

if [ $# -eq 0 ]
then
    ELASTIC=$2
else
    ELASTIC=http://localhost:9200
fi

./create_index.sh config $ELASTIC
./put_mapping.sh config domains config.json $ELASTIC
python load_config.py 


