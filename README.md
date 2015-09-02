# Domain Discovery Tool

This repository contains the Domain Discovery Tool (DDT) project. The DDT tool helps select good seed pages that can subsequently be used to bootstrap focused crawlers. It also allows information extraction and selection of relevant and non-relevant pages crawled by the focused crawlers to help build good page classifiers for them.

## Installing in your machine

Building and deploying the Domain Discovery Tool can either be done using its Makefile to create a local development environment, or automatically by conda or Docker for deployment.  The conda build environment is currently only supported on 64-bit OS X and Linux.

### Local development

First install conda, either through the Anaconda or miniconda installers provided by Continuum.  You will also need Git and a Java Development Kit.  These are system tools that are generally not provided by conda.

Clone the DDT repository and enter it:

```
https://github.com/ViDA-NYU/domain_discovery_tool
cd domain_discovery_tool
```

Use the `make` command to build DDT and download/install its dependencies.

```
make
```

### Docker development

First, make sure you have Docker installed and running. Then, you can create an DDT image using the Dockerfile. Run the following command in the root folder of this project:

    docker build -t domain_discovery_tool .

Run the app using the Docker image that you just built:

    docker run -i -p 8084:8084 -p 9200:9200 -t domain_discovery_tool /domain_discovery_tool/run_demo.sh

To see the app running, go to:

    http://localhost:8084/seedcrawler

Alternativaly, you can also specify an external ElasticSearch server address using an enviroment variable:

    docker run -p 8084:8084 -e "ELASTICSEARCH_SERVER=http://127.0.0.1:9200" -i -t domain_discovery_tool sh -c 'fab runvis'
