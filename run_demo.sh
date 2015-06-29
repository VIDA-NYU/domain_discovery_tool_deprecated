#!/bin/sh
if [ -z "$ELASTICSEARCH_SERVER" ]; then
	#start elasticsearch and wait elasticsearch bind to port
	service elasticsearch start
	ELASTICSEARCH_SERVER=http://localhost:9200
	echo "Waiting ElasticSearch start..."
	while netstat -lnt | awk '$4 ~ /:9200$/ {exit 1}'; do sleep 1; done
else
	sleep 5
fi

echo "Using ElasticSearch at $ELASTICSEARCH_SERVER"

# setup demo indexes
echo "Setting up demo data..."
cd /domain_discovery_tool/elastic
./create_config_index.sh $ELASTICSEARCH_SERVER

./create_index.sh ebola $ELASTICSEARCH_SERVER
./put_mapping.sh ebola page mapping.json $ELASTICSEARCH_SERVER
./put_mapping.sh ebola terms mapping_terms.json $ELASTICSEARCH_SERVER

./create_index.sh gun_control $ELASTICSEARCH_SERVER
./put_mapping.sh gun_control page mapping.json $ELASTICSEARCH_SERVER
./put_mapping.sh gun_control terms mapping_terms.json $ELASTICSEARCH_SERVER

# run server
echo "Running server..."
cd /domain_discovery_tool
fab runvis
#fab runvis >> ./ddt.log 2>&1 &
