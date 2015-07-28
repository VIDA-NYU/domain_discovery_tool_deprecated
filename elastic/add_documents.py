#!/usr/bin/python

import sys

from config import es as default_es

from elasticsearch import helpers

def add_document(entries, es_index='memex', es_doc_type='page', es=None):
    if es is None:
        es = default_es

    helpers.bulk(es, [{"_index": es_index,
                       "_type": es_doc_type,
                       "_source": doc } for doc in entries], refresh=True)

def update_document(update_entries, es_index='memex', es_doc_type='page', es=None):
    if es is None:
        es = default_es
    
    helpers.bulk(es, [{"_op_type": "update",
                       "_index": es_index,
                       "_type": es_doc_type,
                       "doc": value,
                       "_id": key} for key, value in update_entries.items()], refresh=True)

def refresh(es_index='memex', es_doc_type='page', es=None):
    if es is None:
        es = default_es

    es.refresh(es_index)

if __name__ == "__main__":
    if len(sys.argv)>1:
        inputfile = sys.argv[1]
        urls = []
        with open(inputfile, 'r') as f:
            for line in f:
                urls.append(line.strip())
    else:
        urls = [
            'http://en.wikipedia.org/wiki/Dark_internet',
            'http://www.dailymail.co.uk/.../article-3017888/...details-sold-dark-web.html',
            'http://en.wikipedia.org/wiki/Deep_Web',
            'http://www.rogerdavies.com/2011/06/dark-internet',
            'http://www.straightdope.com/.../read/3092/how-can-i-access-the-deep-dark-web'
        ]
    entries = []
    for url in urls:
        print 'Retrieving url %s' % url
        e = compute_index_entry(url=url)
        
        if e: entries.append(e)
    
    if len(entries):
        add_document(entries)
    
    url = 'http://en.wikipedia.org/wiki/Dark_internet',
    entry = {
        'url': url,
        'relevance' : 1
    }
    update_document([entry])
