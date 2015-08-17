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

# run server
echo "Running server..."
cd /domain_discovery_tool
fab runvis
#fab runvis >> ./ddt.log 2>&1 &
