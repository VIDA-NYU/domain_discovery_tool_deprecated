# Domain Discovery Tool

This repository contains the Domain Discovery Tool (DDT) project. DDT is an interactive system that helps users explore and better understand a domain (or topic) as it is represented on the Web. It achieves this by integrating human insights with machine computation (data mining and machine learning) through visualization. DDT allows a domain expert to visualize and analyze pages returned by a search engine or a crawler, and easily provide feedback about relevance. This feedback, in turn, can be used to address two challenges:

* Guide users in the process of domain understanding and help them construct effective queries to be issued to a search engine; and
* Configure focused crawlers that efficiently search the Web for additional pages on the topic. DDT allows users to quickly select crawling seeds as well as positive and negatives required to create a page classifier for the focus topic.

## Installing on your machine

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

After a successful installation, you can activate the DDT development environment:

```
source activate ddt
```

And (from the top-level `domain_discovery_tool` directory),  start
supervisord to run the web application and its associated services:

```
supervisord
```

Now you should be able to head to http://localhost:8084/ to interact
with the tool.

### Docker development

First, make sure you have Docker installed and running. Then, you can create an DDT image using the Dockerfile. Run the following command in the root folder of this project:

    docker build -t domain_discovery_tool .

Run the app using the Docker image that you just built. This starts the elasticsearch and the DDT server:

    docker run -i -p 8084:8084 -p 9200:9200 -t domain_discovery_tool /ddt/run_demo.sh

To see the app running, go to:

    http://localhost:8084/seedcrawler

Alternativaly, you can also specify an external ElasticSearch server address using an enviroment variable:

    docker run -p 8084:8084 -e "ELASTICSEARCH_SERVER=http://127.0.0.1:9200" -i -t domain_discovery_tool

## Further Documentation

[Detailed Description of the tool](https://s3.amazonaws.com/vida-nyu/DDT/domain_discovery_tool.pdf)

[Demo Scripts and Videos](https://s3.amazonaws.com/vida-nyu/DDT/DomainDiscoveryToolDemoScripts.pdf)
Note: To follow the demo videos download and use the following demo build version of DDT:

docker pull vidanyu/ddt:2.7.0-demo
docker run -i -p 8084:8084 -p 9200:9200 -p 9001:9001  -t vidanyu/ddt:2.7.0-demo

## Contact

Yamuna Krishnamurthy [yamuna@nyu.edu]

Aecio Santos [aecio.santos@nyu.edu]





