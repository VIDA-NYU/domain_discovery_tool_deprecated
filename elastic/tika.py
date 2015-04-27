#!/usr/bib/python
## If you put the jar in a non-standard location, you need to
## prepare the CLASSPATH **before** importing jnius
import os, re

dir = os.path.dirname(os.path.realpath(__file__))
try:
    os.environ['CLASSPATH'] = os.environ['CLASSPATH'] + os.pathsep + dir+"/lib/tika-app-1.7.jar"
except KeyError, ex: 
    os.environ['CLASSPATH'] = dir+"/lib/tika-app-1.7.jar"

from jnius import autoclass

## Import the Java classes we are going to need
Tika = autoclass('org.apache.tika.Tika')
Metadata = autoclass('org.apache.tika.metadata.Metadata')
FileInputStream = autoclass('java.io.FileInputStream')
#BasicConfigurator = autoclass('org.apache.log4j.BasicConfigurator')
PropertyConfigurator = autoclass('org.apache.log4j.PropertyConfigurator')

#BasicConfigurator.configure()
PropertyConfigurator.configure(dir+'/lib/log4j.txt')

def tika(filename, url=None, contentType=None,maxLength=None,clean=True):
    tika = Tika()
    meta = Metadata()
    if url is None:
        url = "file:"+filename
    meta.add(Metadata.RESOURCE_NAME_KEY, url)
    if contentType:
        meta.add(Metadata.CONTENT_TYPE, contentType)
    if maxLength is None:
        maxLength = -1
    content = FileInputStream(filename)
    text = tika.parseToString(content, meta, maxLength)
    pymeta = {}
    for key in meta.names():
        pymeta[key] = meta.get(key)
    if clean:
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'(\r?\n[ \t]*)+', '\n', text)
    return (text, pymeta)

if __name__ == "__main__":
    import sys
    for filename in sys.argv[1:]:
        print "Processing document %s" % filename
        text, meta = tika(filename)
        print meta
        print text
