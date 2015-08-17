#
# Domain Discover Tool Dockerfile
#
# https://github.com/ViDA-NYU/domain_discovery_tool
#

# Pull base image.
FROM ubuntu:trusty

# Install some dependencies and useful tools
RUN apt-get update &&\
 apt-get -y install\
 build-essential\
 python-dev python-scipy\
 maven2 openjdk-7-jdk\
 git wget curl vim

# Install pip and python build dependencies
RUN wget https://bootstrap.pypa.io/get-pip.py &&\
 python get-pip.py &&\
 rm get-pip.py &&\
 pip install virtualenv fabric

# Install ElasticSearch and plugin head
RUN wget https://download.elastic.co/elasticsearch/elasticsearch/elasticsearch-1.5.2.deb &&\
  dpkg -i elasticsearch-1.5.2.deb &&\
  rm elasticsearch-1.5.2.deb &&\
  /usr/share/elasticsearch/bin/plugin -install mobz/elasticsearch-head

# Install ACHE and set env variable
RUN wget https://github.com/ViDA-NYU/ache/releases/download/0.3.0/ache-0.3.0.tar &&\
  tar -xvf ache-0.3.0.tar &&\
  rm ache-0.3.0.tar  &&\
  mv ache-0.3.0 ache
ENV ACHE_HOME /ache

# Expose Domain Discovery Tool port
EXPOSE 8084

# Expose ElasticSearch ports
EXPOSE 9200
EXPOSE 9300

WORKDIR /domain_discovery_tool

# Create virtual env and install python dependencies
ADD ./requirements.txt /domain_discovery_tool/requirements.txt
ADD ./fabfile.py /domain_discovery_tool/fabfile.py
RUN fab install_dependencies

# Compile Java dependencies
ADD ./seeds_generator /domain_discovery_tool/seeds_generator
RUN fab compile_seeds_generator

# Add remaining python source files
ADD . /domain_discovery_tool

# Creates config files
RUN fab make_settings

VOLUME ["/var/lib/elasticsearch/data"]
