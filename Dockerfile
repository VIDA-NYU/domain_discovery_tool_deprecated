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
 openjdk-7-jdk\
 wget curl vim

# Install miniconda
RUN echo 'export PATH=/opt/conda/bin:$PATH' > /etc/profile.d/conda.sh && \
    wget --quiet http://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh && \
    /bin/bash /Miniconda2-latest-Linux-x86_64.sh -b -p /opt/conda && \
    rm Miniconda2-latest-Linux-x86_64.sh && \
    /opt/conda/bin/conda install --yes conda==3.14.1
ENV PATH /opt/conda/bin:$PATH

# Expose Domain Discovery Tool port
EXPOSE 8084

# Expose ElasticSearch ports
EXPOSE 9200
EXPOSE 9300

# Expose Supervisord port
EXPOSE 9001

WORKDIR /ddt

# Add build file
ADD ./Makefile /ddt/Makefile

# Install conda dependencies and download nltk data
ADD ./environment.yml /ddt/environment.yml
RUN make conda_env
RUN make get_nltk_data

# Compile Java app
ADD ./seeds_generator /ddt/seeds_generator
RUN make downloader_app

# Add remaining python source files
ADD . /ddt

# Setup remaning configs
RUN make cherrypy_config link_word2vec_data

# Patch address to listen to external connections
RUN sed -i "s#port = 127.0.0.1:9001#port = 0.0.0.0:9001#g" supervisord.conf

CMD bash -c 'source activate ddt; /ddt/bin/ddt-dev'
