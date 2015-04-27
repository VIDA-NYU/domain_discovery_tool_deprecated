#!/usr/bib/python
## If you put the jar in a non-standard location, you need to
## prepare the CLASSPATH **before** importing jnius
import os, re

dir = os.path.dirname(os.path.realpath(__file__))
try:
    os.environ['CLASSPATH'] = os.environ['CLASSPATH']+ os.pathsep +dir+"/lib/boilerpipe-1.2.0.jar:"+dir+"/lib/nekohtml-1.9.13.jar:"+dir+"/lib/xerces-2.9.1.jar"
except KeyError, ex:
    os.environ['CLASSPATH'] = dir+"/lib/boilerpipe-1.2.0.jar:"+dir+"/lib/nekohtml-1.9.13.jar:"+dir+"/lib/xerces-2.9.1.jar"

from jnius import autoclass

## Import the Java classes we are going to need
article_extractor = autoclass('de.l3s.boilerpipe.extractors.ArticleExtractor')
default_extractor = autoclass('de.l3s.boilerpipe.extractors.DefaultExtractor')
URL = autoclass('java.net.URL')

def boilerpipe(html=None, url=None):
    if html and (isinstance(html, str) or isinstance(html, unicode)):
        return article_extractor.INSTANCE.getText(html)
    elif url:
        return article_extractor.INSTANCE.getText(URL(url))
    raise ValueError("One of 'html' or 'url' should be specified as argument")

if __name__ == "__main__":
    import sys
    for url in sys.argv[1:]:
        print "Processing document %s" % url
        text = boilerpipe(url=url)
        print text
