# ElasticSearch utility for MEMEX (Experimental)

Jean-Daniel Fekete, March 10th, 2015

Using ElasticSearch requires its installation first. Go to:
https://www.elastic.co/, the "downloads", get the version that fits your system (mine is Ubuntu so I take the .deb file). Install it and start the server.
It should work on port 9200 on localhost. The installed version should be higher than 1.4 to provide some of the features we need.

To debug and see what ElasticSearch is doing, I advise to install the "Head" plugin:
   ```
   sudo elasticsearch/bin/plugin -install mobz/elasticsearch-head
   ```

You should figure-out where elasticsearch has been installed on your system. On Ubuntu, it is `/usr/share/`.

Then, you can take a look at the contents of Elasticsearch on your machine by opening the url: http://localhost:9200/_plugin/head/

Also, install the requirements for python. I have tested everything using python 2.7.9, not python3.

You can create a virtualenv if you prefer before calling pip install -r requirements.txt

## Creating the ElasticSearch Index

A Database is called an Index in ElasticSearch. To create it, use the script `create_index.sh'
  ```
  ./create_index.sh
  ```

Then, a Schema should be defined. A ElasticSearch Schema is called a "Mapping" and the one I created for Memex is in `mapping.json`. You can install it with the script:
      ```
      ./put_mapping.sh
      ```

Then, you can populate the database with html documents

## Adding new HTML Document

Run the script with urls as parameters:
    ```
    python add_documents.py <url1> <url2> ...
    ```

You can repeat is as much as you want. ElasticSearch will load everything and index it.



## Search Documents

A simple search program can be used as:
  ```
  python search_documents.py 'human traffic'
  ```

It will return the urls of the matching documents.

## Getting the term vectors

To perform its search, ElasticSearch maintains term vectors and computes TF/IDF on them. The information can be retrieved with the sample script:
   ```
   python get_term_vectors.py
   ```

## Caveats

For now, I store the HTML document inside elasticsearch. The mapping and creation make sure the tags are ignored, but attributes are not. It might be better to cleanup the HTML text before storing it.

New fields can be created at will, Elasticsearch will try to guess their schema. Sometimes, it guesses well, sometimes not. It is usually better to update the schema and reload it, but some changes are not possible without reloading the whole system.

