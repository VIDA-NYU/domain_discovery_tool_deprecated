# Domain Discovery Tool

This repository contains the Domain Discovery Tool (DDT) project. The DDT tool helps select good seed pages that can subsequently be used to bootstrap focused crawlers. It also allows information extraction and selection of relevant and non-relevant pages crawled by the focused crawlers to help build good page classifiers for them.

## Installing in your machine

To install DDT, you will need to have Python and Java installed. You will also need pip, fabric, virtualenv, ElasticSearch and [ACHE Crawler](https://github.com/ViDA-NYU/ache). 
For a detailed description, you can follow the step-by-step commands in the  [Dockerfile](https://github.com/ViDA-NYU/domain_discovery_tool/blob/master/Dockerfile).

An easier and self contained way to run DDT is to build and run a docker image, as described bellow.

## Running using Docker

First, make sure you have Docker installed and running. Then, you can create an DDT image using the Dockerfile. Run the following command in the root folder of this project:

    docker build -t domain_discovery_tool .

Run the app using the Docker image that you just built:

    docker run -i -p 8084:8084 -p 9200:9200 -t domain_discovery_tool /domain_discovery_tool/run_demo.sh

To see the app running, go to:

    http://localhost:8084/seedcrawler

Alternativaly, you can also specify an external ElasticSearch server address using an enviromente variable:

    docker run -p 8084:8084 -e "ELASTICSEARCH_SERVER=http://127.0.0.1:9200" -i -t domain_discovery_tool sh -c 'fab runvis'
