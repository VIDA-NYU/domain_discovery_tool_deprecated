#!/bin/bash
echo "Activating DDT enviroment..."
source activate ddt

echo "Using ElasticSearch at $ELASTICSEARCH_SERVER"

echo "Starting services..."
supervisord -c /ddt/supervisord.conf
