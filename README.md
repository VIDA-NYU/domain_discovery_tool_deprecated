# Domain Discovery Tool

This repository contains the Domain Discovery Tool (DDT) project. The DDT tool helps select good seed pages that can subsequently be used to bootstrap focused crawlers. It also allows information extraction and selection of relevant and non-relevant pages crawled by the focused crawlers to help build good page classifiers for them.

## Installing in your machine

To install it, you need:

1) Install git

    sudo apt-get install git

2) Install Java, like the OpenJDK such as java-7-openjdk

    sudo apt-get install openjdk-7-jdk

3) Install Maven

    sudo apt-get install maven2

4) Make sure python 2.7 is installed

5) Install virtualenv

    sudo pip2 install virtualenv

6) Install fabric

    pip2 install fabric

7) Install scipy

    sudo apt-get install python-scipy

8) Install elasticsearch

    wget https://download.elastic.co/elasticsearch/elasticsearch/elasticsearch-1.5.2.deb
    sudo dpkg -i elasticsearch-1.5.2.deb
    rm elasticsearch-1.5.2.deb

9) Start elasticsearch, for now:

    sudo /etc/init.d/elasticsearch start

10) On this directory (domain_discovery_tool), type:

    sudo fab setup

It will take some time to proceed, download everything you need, check that things are properly installed, and stop.

11) Run the program:

    fab runvis

12) Open a web browser and connect to the vis server at the following url:

    http://localhost:8084/seedcrawler


## Running using Docker

Create an image using the Dockerfile. Run the following command in the root folder of this project:

    docker build -t domain_discovery_tool .

Run the app using the Docker image that you just built:

	sudo docker run -i -p 8084:8084 -t domain_discovery_tool /bin/sh -c 'service elasticsearch start; cd domain_discovery_tool/elastic && sleep 10 && bash create_config_index.sh && cd .. && fab runvis'

To see the app running, go to:

    http://localhost:8084/seedcrawler
