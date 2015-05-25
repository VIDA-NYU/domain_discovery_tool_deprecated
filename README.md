This repository contains the Domain Discovery Tool (DDT) project. The DDT tool helps select good seed pages that can subsequently be used to bootstrap focused crawlers. It also allows information extraction and selection of relevant and non-relevant pages crawled by the focused crawlers to help build good page classifiers for them.

To install it, you need:

1) install git
    sudo apt-get install git

2) Install Java, like the OpenJDK such as java-7-openjdk
    sudo apt-get install openjdk-7-jdk

3) Make sure python 2.7 is installed

4) virtualenv
    sudo pip2 install virtualenv

4) install fabrick
    pip2 install fabric

5) install scipy
    sudo apt-get install python-scipy

6) install elasticsearch
    wget https://download.elastic.co/elasticsearch/elasticsearch/elasticsearch-1.5.2.deb
    sudo dpkg -i elasticsearch-1.5.2.deb
    rm elasticsearch-1.5.2.deb

7) Start elasticsearch, for now:
    sudo /etc/init.d/elasticsearch start

8) On this directory (domain_discovery_tool), type:
    sudo fab setup

    It will take some time to proceed, download everything you need, check 
    that things are properly installed, and stop.

9) Run the program:
    fab runvis

10) Open a web browser and connect to the vis server at the following url:
    http://localhost:8084/seedcrawler

