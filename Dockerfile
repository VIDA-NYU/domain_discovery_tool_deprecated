#
# Domain Discover Tool Dockerfile
#
# https://github.com/ViDA-NYU/domain_discovery_tool
#

# Pull base image.
FROM ubuntu:trusty

# Install some dependencies and useful tools
RUN apt-get update
RUN apt-get -y install build-essential
RUN apt-get -y install python-dev python-scipy
RUN apt-get -y install maven2 openjdk-7-jdk
RUN apt-get -y install git wget curl vim

RUN wget https://bootstrap.pypa.io/get-pip.py && python get-pip.py && rm get-pip.py

RUN pip install virtualenv
RUN pip install fabric

# Setup domain discovery tool using Github repository (master branch)
RUN git clone https://github.com/ViDA-NYU/domain_discovery_tool.git && \
  cd domain_discovery_tool && fab setup

# Install ElasticSearch
RUN wget https://download.elastic.co/elasticsearch/elasticsearch/elasticsearch-1.5.2.deb && \
  dpkg -i elasticsearch-1.5.2.deb && rm elasticsearch-1.5.2.deb

RUN sudo /usr/share/elasticsearch/bin/plugin -install mobz/elasticsearch-head

RUN pip install pyelasticsearch
RUN pip install requests

# Expose Domain Discovery Tool port
EXPOSE 8084

# Expose ElasticSearch ports
EXPOSE 9200
EXPOSE 9300

